#!/usr/bin/env python3
"""求人「詳細ページ」のURLを見つける層。

JobPosting の構造化データは求人一覧ではなく求人詳細に置かれるのが一般的で、
採用トップを1階層辿るだけでは届かない（2026-08-20の79社実測で取得率1.3%）。
ここでは詳細URLに到達する2経路を用意する。

  経路A: sitemap.xml（robots.txt の Sitemap: 行 → 既定パスの順に探索）
  経路B: リンクを2階層辿る（採用トップ → 求人一覧 → 求人詳細）

どちらも「詳細らしさ」でURLを順位付けし、取得予算の範囲で上位から使う。
HTTP取得は呼び出し側（crawl）から fetch を注入する（robots遵守・間隔制御・
キャッシュを一箇所に集約するため）。
"""
import re
from urllib.parse import urljoin, urlparse

# 求人関連のURLらしさ（パス・クエリに対して判定）
JOB_HINT = re.compile(
    r'(recruit|career|job|saiyo|entry|position|opening|vacanc|graduate|mid|hiring)'
    r'|(採用|求人|募集|中途|キャリア|新卒)', re.IGNORECASE)

# 詳細ページではない汎用的な末尾セグメント（一覧・トップの類）
_GENERIC_LAST = {
    "", "index", "index.html", "index.php", "list", "search", "top", "home",
    "job", "jobs", "career", "careers", "recruit", "recruitment", "recruiting",
    "position", "positions", "opening", "openings", "entry", "saiyo", "mid",
    "graduate", "newgrads", "newgrad", "experienced", "occupation", "jobtype",
    "採用", "求人", "募集", "中途採用", "新卒採用", "キャリア採用",
}

_LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>", re.IGNORECASE)
_HREF_RE = re.compile(r'href=["\']([^"\'#]+)["\']', re.IGNORECASE)
_SITEMAP_DIRECTIVE_RE = re.compile(r"^\s*sitemap\s*:\s*(\S+)", re.IGNORECASE | re.MULTILINE)

SITEMAP_PATHS = ("/sitemap.xml", "/sitemap_index.xml", "/sitemap-index.xml",
                 "/sitemap/sitemap.xml", "/wp-sitemap.xml")


def _last_segment(path: str) -> str:
    return path.rstrip("/").rsplit("/", 1)[-1].lower()


def looks_like_job_detail(url: str) -> bool:
    """求人「詳細」ページらしいURLか。一覧・トップと区別するための素朴な判定。

    条件: パスのどこかに求人系の語があり、かつ末尾セグメントが
    汎用語ではない（＝個別求人を指す固有のID/スラッグが付いている）。
    """
    p = urlparse(url)
    if not JOB_HINT.search(p.path):
        return False
    last = _last_segment(p.path)
    if last in _GENERIC_LAST:
        # 末尾が汎用でも ?id=123 のように クエリで個別指定する型を拾う
        return bool(re.search(r"(^|&)\w*(id|job|position)\w*=\w+", p.query, re.IGNORECASE))
    # 拡張子付きの一覧ページ（jobs.html等）は除く
    if last.endswith((".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf")):
        return False
    return True


def url_priority(url: str) -> int:
    """小さいほど優先。詳細 > 求人系一覧 > その他。"""
    if looks_like_job_detail(url):
        p = urlparse(url)
        # 数字IDで終わる／id=数字を持つものは個別求人である確度が高い
        has_id = re.search(r"/\d+/?$", p.path) or re.search(r"(^|&)\w*id=\d+", p.query)
        return 0 if has_id else 1
    return 2 if JOB_HINT.search(urlparse(url).path) else 3


def _same_site(host: str, base_host: str) -> bool:
    """完全一致 or 互いのルートのサブドメイン（recruit.example.co.jp 等を許可）。"""
    def root(h: str) -> str:
        h = h.lower()
        return h[4:] if h.startswith("www.") else h
    h, b = root(host), root(base_host)
    return h == b or h.endswith("." + b) or b.endswith("." + h)


def _normalize(base_url: str, href: str) -> str | None:
    if href.startswith(("mailto:", "javascript:", "tel:", "data:")):
        return None
    full = urljoin(base_url, href).split("#")[0]
    p = urlparse(full)
    if p.scheme not in ("http", "https", "file"):
        return None
    return full


def links_on_page(base_url: str, html: str, same_site_only: bool = True) -> list[str]:
    """ページ内リンクを同一サイトに限って正規化・重複排除して返す（順序保持）。"""
    base = urlparse(base_url)
    seen, out = set(), []
    for href in _HREF_RE.findall(html):
        full = _normalize(base_url, href)
        if not full:
            continue
        p = urlparse(full)
        if p.scheme in ("http", "https"):
            if same_site_only and not _same_site(p.netloc, base.netloc):
                continue
        elif base.scheme != "file":
            continue
        if full == base_url or full in seen:
            continue
        seen.add(full)
        out.append(full)
    return out


def rank_job_links(urls: list[str], limit: int) -> list[str]:
    """求人系リンクだけを残し、詳細らしい順に limit 件まで返す。"""
    scored = [(url_priority(u), i, u) for i, u in enumerate(urls)]
    scored = [s for s in scored if s[0] <= 2]  # 求人と無関係なリンクは捨てる
    scored.sort()
    return [u for _, _, u in scored[:limit]]


# --- 経路A: sitemap ---------------------------------------------------------

def sitemap_urls(base_url: str, fetch, robots_text: str = "",
                 max_children: int = 6, max_urls: int = 4000) -> list[str]:
    """sitemap から URL を列挙する。sitemapindex は1段だけ再帰する。

    fetch(url) -> (本文 | None, 状態) を呼び出し側から注入する。
    robots_text は取得済み robots.txt の本文（Sitemap: 行の読み取りに使う）。
    """
    p = urlparse(base_url)
    if p.scheme not in ("http", "https"):
        return []
    origin = f"{p.scheme}://{p.netloc}"

    candidates: list[str] = [m.strip() for m in _SITEMAP_DIRECTIVE_RE.findall(robots_text or "")]
    candidates.extend(origin + path for path in SITEMAP_PATHS)

    urls: list[str] = []
    seen_sitemaps: set[str] = set()
    for sm_url in candidates:
        if sm_url in seen_sitemaps:
            continue
        seen_sitemaps.add(sm_url)
        body, _ = fetch(sm_url)
        if not body or "<loc" not in body.lower():
            continue
        locs = _LOC_RE.findall(body)
        if re.search(r"<sitemapindex", body[:2000], re.IGNORECASE):
            # 子sitemapは求人らしい名前のものを優先して開く
            children = sorted(locs, key=lambda u: (0 if JOB_HINT.search(u) else 1))
            for child in children[:max_children]:
                if child in seen_sitemaps:
                    continue
                seen_sitemaps.add(child)
                child_body, _ = fetch(child)
                if child_body:
                    urls.extend(_LOC_RE.findall(child_body))
                if len(urls) >= max_urls:
                    break
        else:
            urls.extend(locs)
        if urls:
            break  # 最初に中身のあった sitemap 群で打ち切る
    # 同一サイトのみ・重複排除
    seen, out = set(), []
    for u in urls[:max_urls]:
        pu = urlparse(u)
        if pu.scheme not in ("http", "https") or not _same_site(pu.netloc, p.netloc):
            continue
        u = u.split("#")[0]
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
    return out

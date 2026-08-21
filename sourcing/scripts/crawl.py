#!/usr/bin/env python3
"""採用ページを巡回して JobPosting を取得し、DBへ取り込むクローラ本体。

- robots.txt を遵守（ホスト単位でキャッシュ）
- 条件付きGET（ETag/Last-Modified）で未更新ページはスキップ＝差分巡回
- ドメインまたぎで並列取得（同一ドメインへの連続アクセスは間隔を空ける）
- 求人詳細ページへの到達は job_discovery（sitemap経路 / 2階層リンク経路）に委譲
- 取得HTMLから JobPosting を抽出 → 企業ごとに update_db へ

入力シード JSON: [{"company": {...メタ...}, "careers_url": "https://..."}]
usage: python3 crawl.py seed.json --source careers --db ../data/sourcing.db [--workers 8]
"""
import argparse
import json
import threading
import time
import urllib.request
import urllib.robotparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from common import DEFAULT_DB, connect
from extract_jobposting import extract
from http_cache import USER_AGENT, HttpCache
from job_discovery import (ats_links, links_on_page, looks_like_job_detail,
                           rank_job_links, sitemap_urls, url_priority)
from update_db import ingest_batch

# 1社あたりの取得予算。robots/sitemap/一覧/詳細の全取得を含む総ページ数の上限。
MAX_PAGES_PER_COMPANY = 26
MAX_SITEMAP_JOBS = 12    # sitemap から開く求人詳細ページ数
MAX_LIST_PAGES = 6       # 採用トップから辿る求人一覧候補（1階層目）
MAX_DETAIL_PER_LIST = 4  # 求人一覧1ページから辿る詳細候補（2階層目）

_robots_cache: dict[str, urllib.robotparser.RobotFileParser | None] = {}
_robots_body: dict[str, str] = {}
_robots_lock = threading.Lock()
_domain_last: dict[str, float] = {}
_domain_lock = threading.Lock()
MIN_DOMAIN_INTERVAL = 2.0  # 同一ドメインへの最小アクセス間隔（秒）


def allowed_by_robots(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme == "file":
        return True
    host = f"{parsed.scheme}://{parsed.netloc}"
    with _robots_lock:
        rp = _robots_cache.get(host, "unset")
    if rp == "unset":
        # rp.read() はタイムアウト指定不可でハングし得るため、自前で取得してparseする
        rp = urllib.robotparser.RobotFileParser()
        body = ""
        try:
            req = urllib.request.Request(host + "/robots.txt",
                                         headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=10) as resp:
                body = resp.read(262144).decode("utf-8", "replace")
            rp.parse(body.splitlines())
        except Exception:
            rp = None  # robots取得失敗時は保守的にアクセスを許可（一般的挙動）
        with _robots_lock:
            _robots_cache[host] = rp
            _robots_body[host] = body
    if rp is None:
        return True
    return rp.can_fetch(USER_AGENT, url)


def robots_text(url: str) -> str:
    """取得済み robots.txt の本文（Sitemap: 行の読み取りに使う）。未取得なら空。"""
    parsed = urlparse(url)
    with _robots_lock:
        return _robots_body.get(f"{parsed.scheme}://{parsed.netloc}", "")


def _throttle(url: str):
    parsed = urlparse(url)
    if parsed.scheme == "file":
        return
    host = parsed.netloc
    with _domain_lock:
        last = _domain_last.get(host, 0.0)
        wait = MIN_DOMAIN_INTERVAL - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        _domain_last[host] = time.time()


class _Budget:
    """1社あたりの取得ページ数を制限するカウンタ（相手サイトへの負荷の上限）。"""

    def __init__(self, limit: int):
        self.left = limit
        self.pages = 0

    def take(self) -> bool:
        if self.left <= 0:
            return False
        self.left -= 1
        self.pages += 1
        return True


def _make_fetch(cache: HttpCache, budget: _Budget, force: bool):
    """robots遵守・間隔制御・予算消費をまとめた取得関数を作る。"""
    def fetch(url: str) -> tuple[str | None, str]:
        if not allowed_by_robots(url):
            return None, "robots_blocked"
        if not budget.take():
            return None, "budget_exhausted"
        _throttle(url)
        return cache.fetch(url, force=force)
    return fetch


def _dedupe(records: list[dict]) -> list[dict]:
    """同一求人が一覧・詳細の双方に出た場合の重複を落とす。"""
    uniq = {}
    for r in records:
        uniq[r["source_job_id"]] = r
    return list(uniq.values())


def _harvest_sitemap(base_url: str, source_site: str, name: str,
                     fetch, budget: _Budget) -> tuple[list[dict], int]:
    """経路A: sitemap から求人詳細URLを列挙し、上位を開いて抽出する。"""
    urls = sitemap_urls(base_url, fetch, robots_text=robots_text(base_url))
    details = [u for u in urls if looks_like_job_detail(u)]
    if not details:
        return [], 0
    records = []
    for u in sorted(details, key=url_priority)[:MAX_SITEMAP_JOBS]:
        if budget.left <= 0:
            break
        html, state = fetch(u)
        if state == "fetched" and html:
            records.extend(extract(html, source_site, name))
    return _dedupe(records), len(details)


def _harvest_ats(base_url: str, html: str, source_site: str, name: str,
                 fetch, budget: _Budget) -> tuple[list[dict], int]:
    """経路C: 採用ページから外部ATS（HRMOS/HERP等）へのリンクを辿って抽出する。

    日本企業は募集一覧の実体をATSに置き、構造化データもそちら側にあることが多い。
    同一サイト限定の探索では捨ててしまうため、ATSドメインだけ例外的に許可する。
    """
    found_links = ats_links(base_url, html)
    records = []
    for ats_url in found_links:
        if budget.left <= 0:
            break
        a_html, state = fetch(ats_url)
        if state != "fetched" or not a_html:
            continue
        got = extract(a_html, source_site, name)
        if not got:  # ATSの一覧に無ければATS内をもう2階層辿る
            got = _harvest_links(ats_url, a_html, source_site, name, fetch, budget)
        records.extend(got)
        if records:
            break
    return _dedupe(records), len(found_links)


def _harvest_links(base_url: str, html: str, source_site: str, name: str,
                   fetch, budget: _Budget) -> list[dict]:
    """経路B: 採用トップ → 求人一覧 → 求人詳細 と2階層辿って抽出する。"""
    records = []
    for link in rank_job_links(links_on_page(base_url, html), MAX_LIST_PAGES):
        if budget.left <= 0:
            break
        sub_html, state = fetch(link)
        if state != "fetched" or not sub_html:
            continue
        found = extract(sub_html, source_site, name)
        if found:
            records.extend(found)
            continue
        # このページ自体に構造化データが無ければ、求人詳細らしいリンクへもう1階層
        deeper = [u for u in links_on_page(link, sub_html) if looks_like_job_detail(u)]
        for detail_url in sorted(deeper, key=url_priority)[:MAX_DETAIL_PER_LIST]:
            if budget.left <= 0:
                break
            d_html, d_state = fetch(detail_url)
            if d_state == "fetched" and d_html:
                records.extend(extract(d_html, source_site, name))
    return _dedupe(records)


def _harvest_site(url: str, source_site: str, name: str, fetch, budget: _Budget):
    """1つの起点URLから求人を集める。戻り値: (records | None, status, 経路名)。

    records が None は取得失敗。経路は top（起点ページ直下）→ sitemap → link の順に試す。
    """
    html, state = fetch(url)
    if state == "not_modified":
        return [], "not_modified", "-"
    if html is None:
        return None, state, "-"

    records = extract(html, source_site, name)
    if records:
        return records, "fetched", "top"

    ats_records, n_ats = _harvest_ats(url, html, source_site, name, fetch, budget)
    if ats_records:
        return ats_records, "fetched", "ats"

    sm_records, n_details = _harvest_sitemap(url, source_site, name, fetch, budget)
    if sm_records:
        return sm_records, "fetched", f"sitemap/{n_details}"

    link_records = _harvest_links(url, html, source_site, name, fetch, budget)
    if link_records:
        return link_records, "fetched", "link2"

    return [], "fetched", f"none(ATS{n_ats}/sitemap候補{n_details})"


def crawl_one(item: dict, source_site: str, cache: HttpCache) -> dict:
    """1社分を取得・抽出。

    採用URLが外れ（404等）や空振りだった場合は、企業サイトのトップから
    採用リンクを辿り直す（起点リストのURL精度に依存しすぎないための保険）。
    """
    url = item["careers_url"]
    company = item.get("company", {})
    name = company.get("name", "")
    force = bool(item.get("force"))  # 求人0件の企業はキャッシュ無視で再探索
    budget = _Budget(MAX_PAGES_PER_COMPANY)
    fetch = _make_fetch(cache, budget, force)

    records, status, strategy = _harvest_site(url, source_site, name, fetch, budget)
    used_url = url

    website = (company.get("website") or "").strip()
    if not records and status != "not_modified" and website:
        same = urlparse(website).geturl().rstrip("/") == urlparse(url).geturl().rstrip("/")
        if not same:
            alt, alt_status, alt_strategy = _harvest_site(
                website, source_site, name, fetch, budget)
            if alt:
                records, used_url = alt, website
                status, strategy = "fetched:website", alt_strategy
            elif records is None and alt is not None:
                records, status, strategy = alt, "fetched:website", alt_strategy

    if records is None:
        return {"status": status, "company": company, "records": [],
                "pages": budget.pages, "strategy": strategy}
    return {"status": status, "company": {**company, "careers_url": used_url},
            "records": records, "pages": budget.pages, "strategy": strategy}


def crawl_seed(conn, seed: list[dict], source_site: str, today: str, workers: int = 8) -> dict:
    cache = HttpCache()
    # 有効求人が1件も無い企業は、ページ未更新でも再探索する（not_modifiedの罠回避）
    from common import normalize_company_name
    for item in seed:
        name = item.get("company", {}).get("name", "")
        row = conn.execute(
            """SELECT COUNT(jp.id) FROM companies c
               LEFT JOIN job_postings jp ON jp.company_id = c.id AND jp.is_active = 1
               WHERE c.name_normalized = ? GROUP BY c.id""",
            (normalize_company_name(name),),
        ).fetchone()
        if not row or row[0] == 0:
            item["force"] = True
    results = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(crawl_one, it, source_site, cache): it for it in seed}
        for fut in as_completed(futures):
            item = futures[fut]
            try:
                results.append(fut.result())
            except Exception as e:  # 1社の想定外エラーで巡回全体を落とさない
                results.append({"status": f"error:{type(e).__name__}",
                                "company": item.get("company", {}),
                                "records": [], "pages": 0, "strategy": "-"})
    cache.save()

    # 差分取り込み: 取得成功した企業のみ ingest（未更新/失敗は現状維持）
    fetched = [r for r in results if r["status"].startswith("fetched")]
    batch = [{"company": r["company"], "records": r["records"]} for r in fetched]
    ingest_stats = ingest_batch(conn, batch, source_site, today) if batch else {
        "companies": 0, "new": 0, "updated": 0, "closed": 0}

    hit_by = {}
    for r in results:
        if r["records"]:
            key = r.get("strategy", "-").split("/")[0]
            hit_by[key] = hit_by.get(key, 0) + 1

    summary = {
        "total": len(seed),
        "fetched": len(fetched),
        "fetched_via_website": sum(1 for r in results if r["status"] == "fetched:website"),
        "not_modified": sum(1 for r in results if r["status"] == "not_modified"),
        "robots_blocked": sum(1 for r in results if r["status"] == "robots_blocked"),
        "errors": sum(1 for r in results if r["status"].startswith("error")),
        "companies_with_jobs": sum(1 for r in results if r["records"]),
        "hit_by_strategy": hit_by,
        "pages_total": sum(r.get("pages", 0) for r in results),
        "ingest": ingest_stats,
        "details": [
            {"name": r["company"].get("name", "?"), "status": r["status"],
             "jobs": len(r["records"]), "pages": r.get("pages", 0),
             "strategy": r.get("strategy", "-")}
            for r in results
        ],
    }
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("seed_json")
    parser.add_argument("--source", required=True)
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--today", default=str(date.today()))
    args = parser.parse_args()
    seed = json.loads(Path(args.seed_json).read_text(encoding="utf-8"))
    conn = connect(args.db)
    try:
        summary = crawl_seed(conn, seed, args.source, args.today, args.workers)
        print(f"クロール完了 [{args.source}]: {summary}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""採用ページを巡回して JobPosting を取得し、DBへ取り込むクローラ本体。

- robots.txt を遵守（ホスト単位でキャッシュ）
- 条件付きGET（ETag/Last-Modified）で未更新ページはスキップ＝差分巡回
- ドメインまたぎで並列取得（同一ドメインへの連続アクセスは間隔を空ける）
- 取得HTMLから JobPosting を抽出 → 企業ごとに update_db へ

入力シード JSON: [{"company": {...メタ...}, "careers_url": "https://..."}]
usage: python3 crawl.py seed.json --source careers --db ../data/sourcing.db [--workers 8]
"""
import argparse
import json
import re
import threading
import time
import urllib.robotparser
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

from common import DEFAULT_DB, connect
from extract_jobposting import extract
from http_cache import USER_AGENT, HttpCache
from update_db import ingest_batch

# 採用トップ→求人一覧/詳細ページを辿るリンク発見（1階層・同一ホスト限定）
_HREF_RE = re.compile(r'href=["\']([^"\'#]+)["\']', re.IGNORECASE)
_JOB_LINK_HINT = re.compile(
    r'(recruit|career|job|saiyo|entry|position|opening|graduate|mid)'
    r'|(採用|求人|募集|中途|キャリア|新卒)', re.IGNORECASE)
MAX_DISCOVER_PAGES = 5  # 1社あたり追加で辿る最大ページ数

_robots_cache: dict[str, urllib.robotparser.RobotFileParser | None] = {}
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
        rp = urllib.robotparser.RobotFileParser()
        try:
            rp.set_url(host + "/robots.txt")
            rp.read()
        except Exception:
            rp = None  # robots取得失敗時は保守的にアクセスを許可（一般的挙動）
        with _robots_lock:
            _robots_cache[host] = rp
    if rp is None:
        return True
    return rp.can_fetch(USER_AGENT, url)


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


def discover_job_links(base_url: str, html: str, limit: int = MAX_DISCOVER_PAGES) -> list[str]:
    """採用トップのHTMLから、求人一覧/詳細らしき同一ホストのリンクを抽出する。"""
    base = urlparse(base_url)
    seen, links = set(), []
    for href in _HREF_RE.findall(html):
        if href.startswith(("mailto:", "javascript:", "tel:")):
            continue
        full = urljoin(base_url, href)
        p = urlparse(full)
        # 同一ホストのhttp(s)のみ。file://はテスト用にbaseがfileの場合のみ許可
        if p.scheme in ("http", "https"):
            if p.netloc != base.netloc:
                continue
        elif not (p.scheme == "file" and base.scheme == "file"):
            continue
        full = full.split("#")[0]
        if full == base_url or full in seen:
            continue
        if not _JOB_LINK_HINT.search(p.path + ("?" + p.query if p.query else "")):
            continue
        seen.add(full)
        links.append(full)
        if len(links) >= limit:
            break
    return links


def crawl_one(item: dict, source_site: str, cache: HttpCache) -> dict:
    """1社分を取得・抽出。トップにJobPostingが無ければ求人リンクを1階層辿る。"""
    url = item["careers_url"]
    company = item.get("company", {})
    name = company.get("name", "")
    if not allowed_by_robots(url):
        return {"status": "robots_blocked", "company": company, "records": [], "pages": 0}
    _throttle(url)
    html, state = cache.fetch(url)
    if state == "not_modified":
        return {"status": "not_modified", "company": company, "records": [], "pages": 0}
    if state.startswith("error") or html is None:
        return {"status": state, "company": company, "records": [], "pages": 0}

    records = extract(html, source_site, name)
    pages = 1
    if not records:  # トップに構造化データ無し → 求人ページ候補を辿る
        for link in discover_job_links(url, html):
            if not allowed_by_robots(link):
                continue
            _throttle(link)
            sub_html, sub_state = cache.fetch(link)
            pages += 1
            if sub_state == "fetched" and sub_html:
                records.extend(extract(sub_html, source_site, name))
        # 同一求人の重複除去（discovery で同じ求人が複数ページに出る場合）
        uniq = {}
        for r in records:
            uniq[r["source_job_id"]] = r
        records = list(uniq.values())
    return {"status": "fetched", "company": {**company, "careers_url": url},
            "records": records, "pages": pages}


def crawl_seed(conn, seed: list[dict], source_site: str, today: str, workers: int = 8) -> dict:
    cache = HttpCache()
    results = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(crawl_one, it, source_site, cache): it for it in seed}
        for fut in as_completed(futures):
            results.append(fut.result())
    cache.save()

    # 差分取り込み: 取得成功した企業のみ ingest（未更新/失敗は現状維持）
    fetched = [r for r in results if r["status"] == "fetched"]
    batch = [{"company": r["company"], "records": r["records"]} for r in fetched]
    ingest_stats = ingest_batch(conn, batch, source_site, today) if batch else {
        "companies": 0, "new": 0, "updated": 0, "closed": 0}

    summary = {
        "total": len(seed),
        "fetched": len(fetched),
        "not_modified": sum(1 for r in results if r["status"] == "not_modified"),
        "robots_blocked": sum(1 for r in results if r["status"] == "robots_blocked"),
        "errors": sum(1 for r in results if r["status"].startswith("error")),
        "ingest": ingest_stats,
        "details": [
            {"name": r["company"].get("name", "?"), "status": r["status"],
             "jobs": len(r["records"]), "pages": r.get("pages", 0)}
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

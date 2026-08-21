#!/usr/bin/env python3
"""クローラ層のオフライン検証: file:// のフィクスチャ採用ページを巡回してDBへ。

外部ネットワーク・APIキー無しで、crawl → extract → ingest と
シードCSV取り込み・gBizINFOレスポンスのパースを確認する。
"""
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from common import connect  # noqa: E402
from crawl import crawl_seed  # noqa: E402
from gbiz_client import parse_gbiz  # noqa: E402
from http_cache import to_ascii_url  # noqa: E402
from job_discovery import (looks_like_job_detail, rank_job_links,  # noqa: E402
                           sitemap_urls)
from load_seed import load_csv  # noqa: E402

CAREERS_HTML = """<html><head>
<script type="application/ld+json">
{"@type":"JobPosting","title":"プロダクトエンジニア","datePosted":"2026-07-25",
 "hiringOrganization":{"name":"テストスタートアップ株式会社"},
 "jobLocation":{"@type":"Place","address":{"addressRegion":"東京都","addressLocality":"目黒区"}},
 "url":"https://example.test/jobs/1"}
</script>
<script type="application/ld+json">
{"@type":"JobPosting","title":"インサイドセールス","datePosted":"2026-08-02",
 "hiringOrganization":{"name":"テストスタートアップ株式会社"},
 "url":"https://example.test/jobs/2"}
</script></head><body></body></html>"""

FALLBACK_JOB_HTML = """<html><head>
<script type="application/ld+json">
{"@type":"JobPosting","title":"法人営業","datePosted":"2026-08-10",
 "hiringOrganization":{"name":"フォールバック商事株式会社"},
 "url":"https://fallback.test/jobs/1"}
</script></head><body></body></html>"""

GBIZ_PAYLOAD = {
    "hojin-infos": [{
        "corporate_number": "9010001000001",
        "name": "テストスタートアップ株式会社",
        "company_url": "https://example.test",
        "representative_name": "山田太郎",
        "date_of_establishment": "2019-04-01",
        "capital_stock": 90000000,
        "employee_number": 85,
        "postal_code": "1530063",
        "prefecture_name": "東京都",
        "city_name": "目黒区",
        "location": "東京都目黒区XX1-2-3",
        "business_items": ["ソフトウェア業", "情報処理サービス業"],
    }]
}


def run():
    tmp = Path(tempfile.mkdtemp())
    db = tmp / "crawl.db"
    subprocess.run([sys.executable, str(SCRIPTS.parent / "init_db.py"), "--db", str(db)],
                   check=True, capture_output=True)

    # フィクスチャ採用ページを file:// で用意
    page = tmp / "careers.html"
    page.write_text(CAREERS_HTML, encoding="utf-8")
    conn = connect(db)

    # --- シードCSV取り込み ---
    csv_path = tmp / "seed.csv"
    csv_path.write_text(
        "name,careers_url,is_listed,funding_stage,last_funding_date,source_list,prefecture\n"
        f"テストスタートアップ株式会社,file://{page},0,シリーズA,2026-05-01,prtimes,東京都\n",
        encoding="utf-8",
    )
    n = load_csv(conn, csv_path, "2026-08-06")
    assert n == 1, f"シード取り込み {n}"
    print(f"[OK] シードCSV取り込み: {n}社（careers_url付き）")

    # --- クロール（file://フィクスチャ） ---
    seed = [{"company": {"name": "テストスタートアップ株式会社", "funding_stage": "シリーズA",
                         "is_listed": 0, "source_list": "prtimes"},
             "careers_url": f"file://{page}"}]
    summary = crawl_seed(conn, seed, "careers", "2026-08-06", workers=2)
    assert summary["fetched"] == 1, f"取得数 {summary}"
    assert summary["ingest"]["new"] == 2, f"新規求人 {summary['ingest']}"
    print(f"[OK] クロール: {summary['fetched']}社取得 / 新規求人{summary['ingest']['new']}件")

    active = conn.execute("SELECT COUNT(*) FROM job_postings WHERE is_active=1").fetchone()[0]
    assert active == 2, f"有効求人 {active}"
    print(f"[OK] DB反映: 有効求人{active}件")

    # --- gBizINFOレスポンスのパース ---
    meta = parse_gbiz(GBIZ_PAYLOAD)
    assert meta["capital_yen"] == 90000000 and meta["employee_count"] == 85, meta
    assert meta["prefecture"] == "東京都" and "ソフトウェア業" in meta["industry"], meta
    print(f"[OK] gBizINFOパース: 資本金{meta['capital_yen']:,}円 / 従業員{meta['employee_count']}名 / 業種「{meta['industry']}」")

    # --- エンリッチ適用（法人番号・資本金がcompaniesに入る） ---
    from update_db import upsert_company
    upsert_company(conn, "テストスタートアップ株式会社", meta, "2026-08-06")
    conn.commit()
    row = conn.execute(
        "SELECT corporate_number, capital_yen, employee_count FROM companies WHERE name_normalized LIKE '%テストスタートアップ%'"
    ).fetchone()
    assert row and row[0] == "9010001000001", f"エンリッチ反映失敗 {row}"
    print(f"[OK] エンリッチ反映: 法人番号{row[0]} / 資本金{row[1]:,}円 / 従業員{row[2]}名")

    # --- 採用URLが外れたときの企業サイトからの辿り直し ---
    site_dir = tmp / "site"
    site_dir.mkdir()
    (site_dir / "recruit.html").write_text(FALLBACK_JOB_HTML, encoding="utf-8")
    (site_dir / "index.html").write_text(
        '<html><body><a href="recruit.html">採用情報</a></body></html>', encoding="utf-8")
    seed2 = [{"company": {"name": "フォールバック商事株式会社", "is_listed": 0,
                          "website": f"file://{site_dir}/index.html"},
              "careers_url": f"file://{tmp}/not_found_404.html"}]
    summary2 = crawl_seed(conn, seed2, "careers", "2026-08-06", workers=1)
    assert summary2["ingest"]["new"] == 1, f"フォールバック取り込み {summary2}"
    row = conn.execute(
        """SELECT c.careers_url, COUNT(jp.id) FROM companies c
           JOIN job_postings jp ON jp.company_id=c.id AND jp.is_active=1
           WHERE c.name_normalized LIKE '%フォールバック商事%' GROUP BY c.id""").fetchone()
    assert row and row[1] == 1, f"フォールバック反映失敗 {row}"
    print(f"[OK] 採用URL外れ→企業サイトから辿り直し: 求人{row[1]}件を取得")

    # --- 非ASCII URL の送信可能化（日本語パスの採用ページ対策） ---
    assert to_ascii_url("https://example.co.jp/採用/中途") == \
        "https://example.co.jp/%E6%8E%A1%E7%94%A8/%E4%B8%AD%E9%80%94"
    assert to_ascii_url("https://example.co.jp/%E6%8E%A1%E7%94%A8/") == \
        "https://example.co.jp/%E6%8E%A1%E7%94%A8/", "二重符号化してはいけない"
    assert to_ascii_url("https://日本語.jp/jobs").startswith("https://xn--")
    print("[OK] 非ASCII URL: パーセント符号化とIDN変換（二重符号化なし）")

    # --- 2階層リンク探索（採用トップ→求人一覧→求人詳細） ---
    deep = tmp / "deep"
    (deep / "jobs").mkdir(parents=True)
    (deep / "careers.html").write_text(
        '<html><body><a href="/company/">会社情報</a>'
        '<a href="jobs/list.html">募集職種一覧</a></body></html>', encoding="utf-8")
    (deep / "jobs" / "list.html").write_text(  # 一覧には構造化データが無い（実サイトの典型）
        '<html><body><ul><li><a href="engineer.html">バックエンドエンジニア</a></li></ul>'
        '</body></html>', encoding="utf-8")
    (deep / "jobs" / "engineer.html").write_text("""<html><head>
<script type="application/ld+json">
{"@type":"JobPosting","title":"バックエンドエンジニア","datePosted":"2026-08-18",
 "hiringOrganization":{"name":"二階層テスト株式会社"},
 "url":"https://deep.test/jobs/engineer"}
</script></head><body></body></html>""", encoding="utf-8")
    seed3 = [{"company": {"name": "二階層テスト株式会社", "is_listed": 0},
              "careers_url": f"file://{deep}/careers.html"}]
    summary3 = crawl_seed(conn, seed3, "careers", "2026-08-06", workers=1)
    assert summary3["ingest"]["new"] == 1, f"2階層探索の取り込み {summary3}"
    assert summary3["hit_by_strategy"].get("link2") == 1, f"経路判定 {summary3['hit_by_strategy']}"
    print(f"[OK] 2階層リンク探索: 一覧を経由して求人詳細から{summary3['ingest']['new']}件を取得")

    # --- sitemap から求人詳細URLを列挙（sitemapindex の1段再帰つき） ---
    pages = {
        "https://sm.test/robots.txt": "User-agent: *\nSitemap: https://sm.test/sitemap_index.xml\n",
        "https://sm.test/sitemap_index.xml":
            "<sitemapindex><sitemap><loc>https://sm.test/sitemap-news.xml</loc></sitemap>"
            "<sitemap><loc>https://sm.test/sitemap-jobs.xml</loc></sitemap></sitemapindex>",
        "https://sm.test/sitemap-jobs.xml":
            "<urlset><url><loc>https://sm.test/recruit/jobs/101</loc></url>"
            "<url><loc>https://sm.test/recruit/jobs/</loc></url>"
            "<url><loc>https://other.test/recruit/jobs/999</loc></url></urlset>",
        "https://sm.test/sitemap-news.xml":
            "<urlset><url><loc>https://sm.test/news/1</loc></url></urlset>",
    }
    calls = []

    def fake_fetch(url):
        calls.append(url)
        return (pages.get(url), "fetched" if url in pages else "error:http404")

    urls = sitemap_urls("https://sm.test/recruit/", fake_fetch,
                        robots_text=pages["https://sm.test/robots.txt"])
    assert "https://sm.test/recruit/jobs/101" in urls, urls
    assert not any(u.startswith("https://other.test") for u in urls), "外部ドメインは除外"
    assert calls[0] == "https://sm.test/sitemap_index.xml", f"robots記載を最優先 {calls}"
    assert calls[1] == "https://sm.test/sitemap-jobs.xml", f"求人らしい子を優先 {calls}"
    details = [u for u in urls if looks_like_job_detail(u)]
    assert details == ["https://sm.test/recruit/jobs/101"], details
    print(f"[OK] sitemap経路: {len(urls)}URLを列挙し求人詳細{len(details)}件を選別（子sitemapは求人優先）")

    # --- URLの詳細/一覧判定とリンクの順位付け ---
    assert looks_like_job_detail("https://x.jp/careers/backend-engineer")
    assert not looks_like_job_detail("https://x.jp/careers/")
    assert not looks_like_job_detail("https://x.jp/company/about")
    ranked = rank_job_links(["https://x.jp/company/about", "https://x.jp/recruit/",
                             "https://x.jp/recruit/jobs/12"], limit=3)
    assert ranked == ["https://x.jp/recruit/jobs/12", "https://x.jp/recruit/"], ranked
    print("[OK] URL順位付け: 求人詳細を優先し、求人と無関係なリンクは辿らない")

    conn.close()
    print("\n=== クローラ層 全テスト通過 ===")


if __name__ == "__main__":
    run()

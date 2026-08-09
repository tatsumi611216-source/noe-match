#!/usr/bin/env python3
"""パイプライン一気通貫の検証: 抽出 → 取り込み → スコア → ビュー。

フィクスチャ（JobPosting JSON-LDを埋めたHTML）を使い、外部ネットワーク無しで
extract → update_db → score が正しく連動することを確認する。
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

import extract_jobposting  # noqa: E402
from common import connect  # noqa: E402
from update_db import ingest_batch  # noqa: E402
import score  # noqa: E402
from datetime import date  # noqa: E402

STARTUP_HTML = """<html><head>
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"JobPosting","title":"バックエンドエンジニア",
 "datePosted":"2026-07-20","employmentType":"FULL_TIME",
 "hiringOrganization":{"@type":"Organization","name":"グロース・テック株式会社"},
 "jobLocation":{"@type":"Place","address":{"@type":"PostalAddress","addressRegion":"東京都","addressLocality":"渋谷区"}},
 "baseSalary":{"@type":"MonetaryAmount","currency":"JPY","value":{"@type":"QuantitativeValue","minValue":500000,"maxValue":800000,"unitText":"MONTH"}},
 "url":"https://growth-tech.example/jobs/1"}
</script>
<script type="application/ld+json">
{"@graph":[
 {"@type":"WebSite","name":"Growth Tech"},
 {"@type":"JobPosting","title":"フィールドセールス","datePosted":"2026-08-01",
  "hiringOrganization":{"name":"グロース・テック株式会社"},
  "url":"https://growth-tech.example/jobs/2"}
]}
</script></head><body></body></html>"""

LISTED_HTML = """<html><head>
<script type="application/ld+json">
[{"@type":"JobPosting","title":"品質管理エンジニア","datePosted":"2026-02-10",
  "hiringOrganization":{"name":"大手製造㈱"},"url":"https://maker.example/jobs/a"},
 {"@type":"JobPosting","title":"経理スタッフ","datePosted":"2026-03-01",
  "hiringOrganization":{"name":"大手製造㈱"},"url":"https://maker.example/jobs/b"}]
</script></head><body></body></html>"""


def run():
    db = Path(__file__).resolve().parent / "_test.db"
    if db.exists():
        db.unlink()
    subprocess.run([sys.executable, str(SCRIPTS.parent / "init_db.py"), "--db", str(db)],
                   check=True, capture_output=True)
    conn = connect(db)

    # --- 抽出 ---
    su = extract_jobposting.extract(STARTUP_HTML, "startup_site", "グロース・テック株式会社")
    li = extract_jobposting.extract(LISTED_HTML, "corp_site", "大手製造㈱")
    assert len(su) == 2, f"startup抽出数 {len(su)}"
    assert len(li) == 2, f"listed抽出数 {len(li)}"
    assert su[0]["salary_min"] == 500000, "給与パース失敗"
    assert su[0]["location"] == "東京都渋谷区", f"勤務地パース {su[0]['location']}"
    print("[OK] 抽出: startup 2件 / listed 2件、給与・勤務地パース成功")

    # --- 取り込み（差分・名寄せ・メタ反映） ---
    ingest_batch(conn, [{
        "company": {"name": "グロース・テック株式会社", "is_listed": 0,
                    "funding_stage": "シリーズB", "last_funding_date": "2026-06-15",
                    "source_list": "prtimes", "prefecture": "東京都"},
        "records": su,
    }], "startup_site", "2026-08-06")
    ingest_batch(conn, [{
        "company": {"name": "大手製造㈱", "is_listed": 1, "prefecture": "愛知県"},
        "records": li,
    }], "corp_site", "2026-08-06")

    n_co = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    n_job = conn.execute("SELECT COUNT(*) FROM job_postings WHERE is_active=1").fetchone()[0]
    assert n_co == 2 and n_job == 4, f"企業{n_co}社 求人{n_job}件"
    print(f"[OK] 取り込み: {n_co}社 / 有効求人{n_job}件")

    # --- 名寄せ確認: ㈱表記の同一企業を再取り込みしても増えない ---
    ingest_batch(conn, [{"company": {"name": "大手製造株式会社", "is_listed": 1},
                         "records": li}], "corp_site", "2026-08-07")
    assert conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0] == 2, "名寄せ失敗（重複企業）"
    print("[OK] 名寄せ: ㈱/株式会社の表記ゆれを同一企業に集約")

    # --- 差分: 求人が消えたら掲載終了に ---
    ingest_batch(conn, [{"company": {"name": "グロース・テック株式会社"},
                         "records": [su[0]]}], "startup_site", "2026-08-08")
    closed = conn.execute(
        "SELECT COUNT(*) FROM job_postings WHERE source_site='startup_site' AND is_active=0"
    ).fetchone()[0]
    assert closed == 1, f"差分検知失敗 closed={closed}"
    print("[OK] 差分: 消えた求人1件を掲載終了に更新")

    # --- スコア & ビュー ---
    updates = score.compute_scores(conn, date(2026, 8, 8))
    conn.executemany("UPDATE companies SET priority_score=? WHERE id=?", updates)
    conn.commit()

    startup_view = conn.execute("SELECT name, funding_stage FROM v_startup_targets").fetchall()
    sales_view = conn.execute("SELECT name FROM v_sales_targets").fetchall()
    assert any(r[0] == "グロース・テック株式会社" for r in startup_view), "スタートアップがビューに出ない"
    assert all(r[0] != "大手製造㈱" for r in sales_view), "上場企業がv_sales_targets(未上場のみ)に混入"
    print(f"[OK] ビュー: v_startup_targets={startup_view} / 上場企業は未上場ビューから除外")

    # --- 上場子会社・外資系の網羅項目取り込み ---
    sub_records = [{"source_site": "sub_site", "source_job_id": "x1",
                    "company_name": "大手製造テック株式会社", "title": "組込みエンジニア",
                    "employment_type": "FULL_TIME", "location": "神奈川県", "salary_min": None,
                    "salary_max": None, "url": "u", "posted_at": "2026-07-01"}]
    ingest_batch(conn, [{
        "company": {"name": "大手製造テック株式会社", "corporate_number": "1234567890123",
                    "is_subsidiary": 1, "parent_name": "大手製造㈱",
                    "ultimate_parent_name": "大手製造㈱", "capital_yen": 100_000_000,
                    "employee_count": 300, "industry": "電子部品", "prefecture": "神奈川県",
                    "source_list": "edinet"},
        "records": sub_records,
    }], "sub_site", "2026-08-06")

    foreign_records = [{"source_site": "gj", "source_job_id": "f1",
                        "company_name": "グローバルSaaSジャパン株式会社", "title": "エンタープライズ営業",
                        "employment_type": "FULL_TIME", "location": "東京都", "salary_min": None,
                        "salary_max": None, "url": "u", "posted_at": "2026-07-10"}]
    ingest_batch(conn, [{
        "company": {"name": "グローバルSaaSジャパン株式会社", "is_foreign_affiliated": 1,
                    "foreign_parent_country": "米国", "foreign_ownership_pct": 100.0,
                    "employee_count": 120, "funding_stage": "未公開", "prefecture": "東京都",
                    "source_list": "toyokeizai"},
        "records": foreign_records,
    }], "gj", "2026-08-06")

    sub = conn.execute(
        "SELECT name, parent_name, corporate_number, capital_yen FROM v_group_targets"
    ).fetchall()
    assert any(r[0] == "大手製造テック株式会社" and r[1] == "大手製造㈱" for r in sub), \
        f"上場子会社がv_group_targetsに出ない: {sub}"
    fa = conn.execute(
        "SELECT name, foreign_parent_country FROM companies WHERE is_foreign_affiliated=1"
    ).fetchall()
    assert fa and fa[0][1] == "米国", f"外資系フラグ取り込み失敗: {fa}"
    print(f"[OK] 上場子会社: {sub[0][0]}←親{sub[0][1]} (法人番号{sub[0][2]}/資本金{sub[0][3]:,}円)")
    print(f"[OK] 外資系: {fa[0][0]} (親会社国籍{fa[0][1]})")

    conn.close()
    db.unlink()
    print("\n=== 全テスト通過 ===")


if __name__ == "__main__":
    run()

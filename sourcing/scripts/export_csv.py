#!/usr/bin/env python3
"""営業リストをCSVで書き出す（他ツール連携用・F-10）。

Excelでそのまま開けるよう UTF-8 BOM 付きで出力する。

usage:
  python3 export_csv.py                    # 主要ビューをまとめて出力
  python3 export_csv.py --view v_sales_targets
  python3 export_csv.py --view jobs        # 有効求人の明細
"""
import argparse
import csv
from datetime import date
from pathlib import Path

from common import DEFAULT_DB, connect

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_VIEWS = ["v_sales_targets", "v_startup_targets", "v_listed_targets",
                 "v_group_targets", "v_category_summary"]

JOBS_SQL = """
SELECT c.name AS company, c.industry, c.prefecture, c.is_listed, c.priority_score,
       cat.name AS category, jp.title, jp.employment_type, jp.location,
       jp.salary_min, jp.salary_max, jp.posted_at,
       jp.first_seen_at, jp.last_seen_at,
       CAST(julianday('now') - julianday(jp.first_seen_at) AS INTEGER) AS days_listed,
       jp.source_site, jp.url
FROM job_postings jp
JOIN companies c ON c.id = jp.company_id
LEFT JOIN categories cat ON cat.id = jp.category_id
WHERE jp.is_active = 1
ORDER BY c.priority_score DESC, days_listed DESC
"""


def dump(conn, name: str, outdir: Path, today: str) -> Path | None:
    sql = JOBS_SQL if name == "jobs" else f"SELECT * FROM {name}"
    cur = conn.execute(sql)
    rows = cur.fetchall()
    header = [d[0] for d in cur.description]
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"{name}_{today}.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {path.name}: {len(rows)}行")
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--view", action="append",
                        help="出力するビュー名（複数指定可）。'jobs' で求人明細")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--outdir", default=str(BASE_DIR / "outputs"))
    parser.add_argument("--today", default=str(date.today()))
    args = parser.parse_args()

    views = args.view or DEFAULT_VIEWS + ["jobs"]
    conn = connect(args.db)
    try:
        print(f"CSV出力: {len(views)}件")
        for v in views:
            dump(conn, v, Path(args.outdir), args.today)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""日次実行のエントリポイント: シードCSV → クロール → スコア → レポート。

GitHub Actions / cron から1コマンドで呼ぶための束ねスクリプト。
usage: python3 run_daily.py --seeds ../seeds/game_companies.csv [--db ...] [--source careers]
"""
import argparse
import csv
from datetime import date
from pathlib import Path

import score
from common import DEFAULT_DB, connect
from crawl import crawl_seed
from generate_report import build_html
from load_seed import _coerce
from update_db import COMPANY_FIELDS

BASE_DIR = Path(__file__).resolve().parent.parent


def read_seeds(csv_path: Path) -> list[dict]:
    seeds = []
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            url = (row.get("careers_url") or "").strip()
            if not name or not url:
                continue
            meta = {k: _coerce(k, row[k]) for k in row if k in COMPANY_FIELDS}
            meta["name"] = name
            seeds.append({"company": meta, "careers_url": url})
    return seeds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", required=True)
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--source", default="careers")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--out", default=str(BASE_DIR / "outputs" / "report.html"))
    args = parser.parse_args()

    today = date.today().isoformat()
    seeds = read_seeds(Path(args.seeds))
    print(f"シード: {len(seeds)}社")

    # DBが無ければ初期化
    db_path = Path(args.db)
    if not db_path.exists():
        import subprocess, sys
        subprocess.run([sys.executable, str(BASE_DIR / "init_db.py"), "--db", str(db_path)],
                       check=True)

    conn = connect(db_path)
    try:
        summary = crawl_seed(conn, seeds, args.source, today, args.workers)
        print(f"クロール結果: {summary}")

        updates = score.compute_scores(conn, date.today())
        conn.executemany(
            "UPDATE companies SET priority_score=?, updated_at=datetime('now') WHERE id=?",
            updates)
        conn.commit()
        print(f"スコア更新: {len(updates)}社")

        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build_html(conn, today), encoding="utf-8")
        print(f"レポート生成: {out}")

        # Actionsのログで見やすいサマリー
        for name, jobs in conn.execute(
            """SELECT c.name, COUNT(jp.id) FROM companies c
               LEFT JOIN job_postings jp ON jp.company_id=c.id AND jp.is_active=1
               GROUP BY c.id ORDER BY COUNT(jp.id) DESC"""):
            print(f"  {name}: 有効求人{jobs}件")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

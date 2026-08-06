#!/usr/bin/env python3
"""起点リスト（CSV）を companies に登録する。採用ページURLの種を作る工程。

CSVヘッダ例（列は可変・存在するものだけ取り込む）:
  name,corporate_number,careers_url,website,is_listed,listing_market,ticker,
  prefecture,industry,employee_count,capital_yen,funding_stage,last_funding_date,
  is_subsidiary,parent_name,is_foreign_affiliated,foreign_parent_country,source_list

トラック①=JPX上場一覧、②=資金調達リリース/VCポートフォリオ 等をこの形に整えて投入する。
usage: python3 load_seed.py seed.csv --db ../data/sourcing.db
"""
import argparse
import csv
from datetime import date
from pathlib import Path

from common import DEFAULT_DB, connect
from update_db import COMPANY_FIELDS, upsert_company

INT_FIELDS = {"is_listed", "is_subsidiary", "is_foreign_affiliated",
              "employee_count", "capital_yen", "revenue_yen", "last_funding_yen",
              "total_funding_yen"}
FLOAT_FIELDS = {"foreign_ownership_pct"}


def _coerce(key: str, val: str):
    val = (val or "").strip()
    if val == "":
        return None
    if key in INT_FIELDS:
        try:
            return int(float(val))
        except ValueError:
            return None
    if key in FLOAT_FIELDS:
        try:
            return float(val)
        except ValueError:
            return None
    return val


def load_csv(conn, csv_path: Path, today: str) -> int:
    n = 0
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("name") or "").strip()
            if not name:
                continue
            meta = {k: _coerce(k, row[k]) for k in row if k in COMPANY_FIELDS}
            upsert_company(conn, name, meta, today)
            n += 1
    conn.commit()
    return n


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_file")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--today", default=str(date.today()))
    args = parser.parse_args()
    conn = connect(args.db)
    try:
        n = load_csv(conn, Path(args.csv_file), args.today)
        total = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        print(f"シード取り込み: {n}行処理 / 企業マスタ合計 {total}社")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

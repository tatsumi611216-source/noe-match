#!/usr/bin/env python3
"""抽出済み求人レコードをDBに取り込む（企業名寄せ・カテゴリ分類・差分更新）。

1社分の求人レコード群を受け取り:
  1. 企業を name_normalized で名寄せしてupsert（is_listed等のメタも反映）
  2. 各求人を (source_site, source_job_id) でupsert、last_seen更新
  3. 同一社・同一sourceで今回見つからなかった求人を is_active=0（掲載終了）に
入力JSON形式: [{"company": {...メタ...}, "records": [...extract出力...]}, ...]
"""
import argparse
import json
import sqlite3
from datetime import date
from pathlib import Path

from common import DEFAULT_DB, classify, connect, load_categories, normalize_company_name

# meta から取り込みを許可する companies カラム（DATA_DICTIONARY.md と対応）
COMPANY_FIELDS = [
    "corporate_number", "industry", "industry_code", "business_summary",
    "website", "careers_url", "representative_name", "established_date",
    "capital_yen", "revenue_yen", "employee_count",
    "postal_code", "prefecture", "city", "address", "phone",
    "is_listed", "listing_market", "ticker",
    "is_subsidiary", "parent_name", "parent_corporate_number", "ultimate_parent_name",
    "is_foreign_affiliated", "foreign_parent_country", "foreign_ownership_pct",
    "funding_stage", "first_funding_date", "last_funding_date", "last_funding_yen",
    "total_funding_yen", "source_list", "gbiz_synced_at",
]


def upsert_company(conn: sqlite3.Connection, name: str, meta: dict, today: str) -> int:
    """企業を名寄せしてupsert。渡されたメタ項目のみ更新（既存値をnullで潰さない）。"""
    norm = normalize_company_name(name)
    fields = {k: meta.get(k) for k in COMPANY_FIELDS if k in meta}
    row = conn.execute("SELECT id FROM companies WHERE name_normalized = ?", (norm,)).fetchone()
    if row:
        cid = row[0]
        set_sql = ["last_seen_at = ?", "updated_at = datetime('now')"]
        params = [today]
        for k, v in fields.items():
            set_sql.append(f"{k} = COALESCE(?, {k})")  # 新しい非null値が勝つ
            params.append(v)
        params.append(cid)
        conn.execute(f"UPDATE companies SET {', '.join(set_sql)} WHERE id = ?", params)
        return cid
    cols = ["name", "name_normalized", "first_seen_at", "last_seen_at", *fields.keys()]
    vals = [name, norm, today, today, *fields.values()]
    placeholders = ",".join("?" * len(cols))
    cur = conn.execute(
        f"INSERT INTO companies ({','.join(cols)}) VALUES ({placeholders})", vals
    )
    return cur.lastrowid


def ingest_company(conn, cid, records, source_site, categories, today) -> tuple[int, int, int]:
    seen_ids = []
    new_n = 0
    for r in records:
        sjid = r["source_job_id"]
        seen_ids.append(sjid)
        cat_id = classify(r["title"], categories)
        exists = conn.execute(
            "SELECT id FROM job_postings WHERE source_site=? AND source_job_id=?",
            (source_site, sjid),
        ).fetchone()
        if exists:
            conn.execute(
                """UPDATE job_postings SET last_seen_at=?, is_active=1, title=?,
                       category_id=?, location=COALESCE(?,location),
                       salary_min=COALESCE(?,salary_min), salary_max=COALESCE(?,salary_max),
                       url=COALESCE(?,url) WHERE id=?""",
                (today, r["title"], cat_id, r.get("location"), r.get("salary_min"),
                 r.get("salary_max"), r.get("url"), exists[0]),
            )
        else:
            new_n += 1
            conn.execute(
                """INSERT INTO job_postings
                   (company_id, category_id, source_site, source_job_id, title,
                    employment_type, salary_min, salary_max, location, url, posted_at,
                    first_seen_at, last_seen_at, is_active)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,1)""",
                (cid, cat_id, source_site, sjid, r["title"], r.get("employment_type"),
                 r.get("salary_min"), r.get("salary_max"), r.get("location"),
                 r.get("url"), r.get("posted_at"), today, today),
            )
    # 差分: この社・このsourceで今回見なかった求人を掲載終了に
    placeholders = ",".join("?" * len(seen_ids)) or "''"
    closed = conn.execute(
        f"""UPDATE job_postings SET is_active=0
            WHERE company_id=? AND source_site=? AND is_active=1
              AND source_job_id NOT IN ({placeholders})""",
        [cid, source_site, *seen_ids],
    ).rowcount
    return new_n, len(records) - new_n, closed


def ingest_batch(conn, batch: list[dict], source_site: str, today: str) -> dict:
    categories = load_categories(conn)
    tot_new = tot_upd = tot_closed = 0
    for item in batch:
        meta = item.get("company", {})
        name = meta.get("name") or (item["records"][0]["company_name"] if item.get("records") else None)
        if not name:
            continue
        cid = upsert_company(conn, name, meta, today)
        n, u, c = ingest_company(conn, cid, item.get("records", []), source_site, categories, today)
        tot_new += n; tot_upd += u; tot_closed += c
    conn.execute(
        """INSERT INTO crawl_runs (run_date, source_site, pages_fetched, jobs_found,
               jobs_new, jobs_closed, finished_at)
           VALUES (?,?,?,?,?,?,datetime('now'))""",
        (today, source_site, len(batch), tot_new + tot_upd, tot_new, tot_closed),
    )
    conn.commit()
    return {"companies": len(batch), "new": tot_new, "updated": tot_upd, "closed": tot_closed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_json", help="[{company:{}, records:[]}] 形式のJSON")
    parser.add_argument("--source", required=True)
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--today", default=str(date.today()))
    args = parser.parse_args()
    batch = json.loads(Path(args.batch_json).read_text(encoding="utf-8"))
    conn = connect(args.db)
    try:
        result = ingest_batch(conn, batch, args.source, args.today)
        print(f"取り込み完了 [{args.source}]: {result}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

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


def upsert_company(conn: sqlite3.Connection, name: str, meta: dict, today: str) -> int:
    norm = normalize_company_name(name)
    row = conn.execute("SELECT id FROM companies WHERE name_normalized = ?", (norm,)).fetchone()
    if row:
        cid = row[0]
        conn.execute(
            """UPDATE companies SET last_seen_at = ?, updated_at = datetime('now'),
                   is_listed = COALESCE(?, is_listed),
                   funding_stage = COALESCE(?, funding_stage),
                   last_funding_date = COALESCE(?, last_funding_date),
                   last_funding_yen = COALESCE(?, last_funding_yen),
                   source_list = COALESCE(?, source_list),
                   url = COALESCE(url, ?)
               WHERE id = ?""",
            (today, meta.get("is_listed"), meta.get("funding_stage"),
             meta.get("last_funding_date"), meta.get("last_funding_yen"),
             meta.get("source_list"), meta.get("url"), cid),
        )
        return cid
    cur = conn.execute(
        """INSERT INTO companies
           (name, name_normalized, is_listed, funding_stage, last_funding_date,
            last_funding_yen, source_list, url, prefecture, industry, employee_count,
            first_seen_at, last_seen_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (name, norm, meta.get("is_listed", 0), meta.get("funding_stage"),
         meta.get("last_funding_date"), meta.get("last_funding_yen"),
         meta.get("source_list"), meta.get("url"), meta.get("prefecture"),
         meta.get("industry"), meta.get("employee_count"), today, today),
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

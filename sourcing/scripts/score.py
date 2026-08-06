#!/usr/bin/env python3
"""採用HR営業向けの優先度スコアを算出して companies.priority_score を更新する。

「採用に困っている企業ほど高スコア」= 人材紹介・採用代行の即ニーズ、という設計。
usage: python3 score.py [--db ../data/sourcing.db] [--top 20]

スコア構成（REQUIREMENTS.md §2.6 と対応）:
  有効求人件数(対数)      : 募集ポジションが多い = 採れていない
  平均掲載日数(上限180日) : 長く出続けている = 充足できず苦戦
  直近7日の新規求人数      : 今まさに動いている = アプローチ好機
  募集カテゴリ数           : 複数職種で採用 = 事業拡大・継続需要
"""
import argparse
import math
import sqlite3
from datetime import date, datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB = BASE_DIR.parent / "data" / "sourcing.db"

# 各指標の重み（合計スコアの目安レンジ 0〜100）
W_JOBS = 30.0        # 有効求人件数（対数正規化）
W_AGE = 30.0         # 平均掲載日数（180日で頭打ち）
W_NEW = 25.0         # 直近7日の新規
W_CATEGORY = 15.0    # 募集カテゴリ数（4種で頭打ち）

AGE_CAP_DAYS = 180
NEW_WINDOW_DAYS = 7


def _days_since(d: str | None, today: date) -> int:
    if not d:
        return 0
    try:
        return max(0, (today - datetime.fromisoformat(d).date()).days)
    except ValueError:
        return 0


def compute_scores(conn: sqlite3.Connection, today: date) -> list[tuple[float, int]]:
    rows = conn.execute(
        """
        SELECT jp.company_id,
               COUNT(*)                                   AS active_jobs,
               COUNT(DISTINCT jp.category_id)             AS n_categories,
               GROUP_CONCAT(jp.first_seen_at, '|')        AS first_seen_dates
        FROM job_postings jp
        WHERE jp.is_active = 1
        GROUP BY jp.company_id
        """
    ).fetchall()

    updates: list[tuple[float, int]] = []
    for company_id, active_jobs, n_categories, first_seen_dates in rows:
        dates = [d for d in (first_seen_dates or "").split("|") if d]
        ages = [_days_since(d, today) for d in dates]
        avg_age = sum(ages) / len(ages) if ages else 0
        new_recent = sum(1 for a in ages if a <= NEW_WINDOW_DAYS)

        s_jobs = W_JOBS * min(1.0, math.log1p(active_jobs) / math.log1p(20))
        s_age = W_AGE * min(1.0, avg_age / AGE_CAP_DAYS)
        s_new = W_NEW * min(1.0, new_recent / 5.0)
        s_cat = W_CATEGORY * min(1.0, (n_categories or 0) / 4.0)

        score = round(s_jobs + s_age + s_new + s_cat, 1)
        updates.append((score, company_id))
    return updates


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--top", type=int, default=20, help="上位何件を表示するか")
    parser.add_argument("--today", help="基準日 YYYY-MM-DD（省略時は本日）")
    args = parser.parse_args()

    today = datetime.fromisoformat(args.today).date() if args.today else date.today()

    conn = sqlite3.connect(args.db)
    try:
        updates = compute_scores(conn, today)
        conn.executemany(
            "UPDATE companies SET priority_score = ?, updated_at = datetime('now') WHERE id = ?",
            updates,
        )
        conn.commit()
        print(f"スコア更新: {len(updates)}社")

        top = conn.execute(
            """
            SELECT name, prefecture, sales_status, priority_score, active_jobs, categories
            FROM v_sales_targets
            LIMIT ?
            """,
            (args.top,),
        ).fetchall()
        if top:
            print(f"\n=== 営業優先度 上位{len(top)}社 ===")
            for name, pref, status, score, jobs, cats in top:
                print(f"  {score:5.1f} | {name} ({pref or '-'}) "
                      f"求人{jobs}件 [{cats or '-'}] {status}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

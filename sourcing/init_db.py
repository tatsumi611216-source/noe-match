#!/usr/bin/env python3
"""営業ソーシングツールのデータベースを初期化する。

usage: python3 init_db.py [--db data/sourcing.db]

schema.sql を適用し、職種カテゴリの初期マスタを投入する。
既存DBに対しては何度実行しても安全（IF NOT EXISTS / INSERT OR IGNORE）。
"""
import argparse
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "schema.sql"

# 初期カテゴリマスタ: (名称, 分類キーワード, 表示順)
SEED_CATEGORIES = [
    ("IT・エンジニア", "エンジニア,プログラマ,SE,インフラ,開発,IT,システム,Web", 10),
    ("営業", "営業,セールス,ルート,法人営業,個人営業", 20),
    ("事務・管理", "事務,経理,総務,人事,労務,アシスタント,受付", 30),
    ("販売・接客", "販売,接客,店舗,店長,レジ,アパレル", 40),
    ("飲食", "調理,ホール,キッチン,飲食,シェフ,バリスタ", 50),
    ("医療・介護・福祉", "看護,介護,医療,福祉,保育,薬剤,ヘルパー,リハビリ", 60),
    ("製造・技術", "製造,工場,組立,検査,機械,電気,品質管理,生産", 70),
    ("建設・土木", "建設,土木,施工,現場,設備,電気工事,大工", 80),
    ("物流・運輸", "ドライバー,配送,物流,倉庫,運転,フォークリフト,軽貨物", 90),
    ("その他", "", 999),
]


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.executemany(
            "INSERT OR IGNORE INTO categories (name, keywords, sort_order) VALUES (?, ?, ?)",
            SEED_CATEGORIES,
        )
        conn.commit()

        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view') "
            "AND name NOT LIKE 'sqlite_%' ORDER BY type, name"
        )]
        n_cat = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        print(f"DB初期化完了: {db_path}")
        print(f"テーブル/ビュー: {', '.join(tables)}")
        print(f"カテゴリマスタ: {n_cat}件")
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=str(BASE_DIR / "data" / "sourcing.db"))
    args = parser.parse_args()
    init_db(Path(args.db))

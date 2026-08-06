#!/usr/bin/env python3
"""ソーシングツール共通ユーティリティ: DBパス・企業名正規化・カテゴリ分類。"""
import re
import sqlite3
import unicodedata
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB = BASE_DIR / "data" / "sourcing.db"

# 企業名から除去する法人格表記（正規化キー生成用）
_CORP_SUFFIXES = [
    "株式会社", "有限会社", "合同会社", "合資会社", "合名会社",
    "一般社団法人", "一般財団法人", "公益社団法人", "公益財団法人",
    "(株)", "(有)", "(同)",
]


def normalize_company_name(name: str) -> str:
    """名寄せキーを生成する。全半角・法人格・記号・空白の揺れを吸収。

    例: '㈱ＡＢＣ商事' → 'abc商事' / '株式会社ABC 商事' → 'abc商事'
    """
    if not name:
        return ""
    s = unicodedata.normalize("NFKC", name)  # 全角→半角、㈱→(株) 等
    for suf in _CORP_SUFFIXES:
        s = s.replace(suf, "")
    s = re.sub(r"\s+", "", s)                 # 空白除去
    s = re.sub(r"[・･,、.。/／\-−―–]", "", s)  # 区切り記号除去
    return s.strip().lower()


def connect(db_path: str | Path = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def load_categories(conn: sqlite3.Connection) -> list[tuple[int, str, list[str]]]:
    """(category_id, name, keywords[]) を sort_order 順で返す。"""
    rows = conn.execute(
        "SELECT id, name, keywords FROM categories ORDER BY sort_order"
    ).fetchall()
    result = []
    for cid, name, kw in rows:
        keywords = [k.strip().lower() for k in (kw or "").split(",") if k.strip()]
        result.append((cid, name, keywords))
    return result


def classify(title: str, categories: list[tuple[int, str, list[str]]]) -> int | None:
    """求人タイトル/職種名をカテゴリIDに分類する。キーワード部分一致・sort_order優先。

    どれにも一致しなければ「その他」(keywords空) を返す。
    """
    text = unicodedata.normalize("NFKC", title or "").lower()
    fallback = None
    for cid, _name, keywords in categories:
        if not keywords:            # その他（キーワード無し）はフォールバック候補
            fallback = cid
            continue
        if any(kw in text for kw in keywords):
            return cid
    return fallback

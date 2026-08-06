#!/usr/bin/env python3
"""EDINET（金融庁）から有価証券報告書を取得し、関係会社（子会社）構造を抽出する。

用途: 上場企業の親子関係を corporate_relations に蓄積し、上場企業傘下の子会社
（採用余力のある営業ターゲット）を companies に is_subsidiary=1 で登録する。

認証: クエリパラメータ Subscription-Key（環境変数 EDINET_API_KEY）。
実接続部（list_documents / fetch_document_csv）はキー必須。
抽出部（extract_subsidiaries / store_relations）はキー不要で単体テスト可能。

APIキー取得: https://api.edinet-fsa.go.jp/ で無料登録。
※ CSVの要素構造は実データでの微調整が必要（Phase 2で校正）。ヒューリスティック実装。
"""
import argparse
import csv
import io
import json
import urllib.parse
import urllib.request
import zipfile
from datetime import date

from common import DEFAULT_DB, connect
from config import get_edinet_key, load_env
from http_cache import USER_AGENT
from update_db import upsert_company

API_BASE = "https://api.edinet-fsa.go.jp/api/v2"
DOCTYPE_YUHO = "120"   # 有価証券報告書
RELATION_HINTS = ("関係会社", "子会社", "連結子会社")


def list_documents(day: str, key: str) -> list[dict]:
    """指定日の提出書類一覧を返す（type=2: 提出書類とメタデータ）。"""
    q = urllib.parse.urlencode({"date": day, "type": 2, "Subscription-Key": key})
    req = urllib.request.Request(f"{API_BASE}/documents.json?{q}",
                                 headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return [d for d in data.get("results", []) if d.get("docTypeCode") == DOCTYPE_YUHO]


def fetch_document_csv(doc_id: str, key: str) -> list[dict]:
    """書類のCSV（type=5）を取得し、行（要素ID/項目名/値）のリストにして返す。"""
    q = urllib.parse.urlencode({"type": 5, "Subscription-Key": key})
    req = urllib.request.Request(f"{API_BASE}/documents/{doc_id}?{q}",
                                 headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        blob = resp.read()
    rows = []
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for nm in z.namelist():
            if not nm.lower().endswith(".csv"):
                continue
            text = z.read(nm).decode("utf-16", "replace")
            for r in csv.DictReader(io.StringIO(text), delimiter="\t"):
                rows.append(r)
    return rows


def extract_subsidiaries(rows: list[dict], parent_name: str) -> list[dict]:
    """CSV行から関係会社（子会社）名・議決権割合を抽出する（ヒューリスティック）。

    EDINET CSVは列に「項目名」「値」を持つ。関係会社セクション由来の
    名称・所有割合行を拾う。実データで列名/要素IDの校正が必要。
    """
    subs: list[dict] = []
    current = None
    for r in rows:
        label = (r.get("項目名") or r.get("要素ID") or "")
        value = (r.get("値") or "").strip()
        if not value or value in ("－", "-", "―"):
            continue
        is_relation_ctx = any(h in label for h in RELATION_HINTS)
        if is_relation_ctx and "名称" in label:
            current = {"child_name": value, "ownership_pct": None,
                       "relation_type": "子会社" if "子会社" in label else "関連会社"}
            subs.append(current)
        elif current and ("議決権" in label or "所有割合" in label):
            try:
                current["ownership_pct"] = float(value.replace("%", "").replace(",", ""))
            except ValueError:
                pass
            current = None
    # 親会社名で重複除去
    seen, uniq = set(), []
    for s in subs:
        if s["child_name"] and s["child_name"] != parent_name and s["child_name"] not in seen:
            seen.add(s["child_name"])
            uniq.append(s)
    return uniq


def store_relations(conn, parent_name: str, subs: list[dict], today: str,
                    parent_corporate_number: str | None = None) -> int:
    """関係会社を corporate_relations に登録し、子会社を companies に is_subsidiary=1 で作成。"""
    n = 0
    for s in subs:
        conn.execute(
            """INSERT OR IGNORE INTO corporate_relations
               (parent_corporate_number, parent_name, child_name, relation_type,
                ownership_pct, source, disclosed_date)
               VALUES (?,?,?,?,?, 'edinet', ?)""",
            (parent_corporate_number, parent_name, s["child_name"],
             s.get("relation_type", "子会社"), s.get("ownership_pct"), today),
        )
        upsert_company(conn, s["child_name"], {
            "is_subsidiary": 1, "parent_name": parent_name,
            "parent_corporate_number": parent_corporate_number,
            "ultimate_parent_name": parent_name, "source_list": "edinet",
        }, today)
        n += 1
    conn.commit()
    return n


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=str(date.today()), help="提出書類一覧の対象日 YYYY-MM-DD")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    load_env()
    key = get_edinet_key()
    conn = connect(args.db)
    today = date.today().isoformat()
    try:
        docs = list_documents(args.date, key)[: args.limit]
        total = 0
        for d in docs:
            parent = d.get("filerName") or ""
            rows = fetch_document_csv(d["docID"], key)
            subs = extract_subsidiaries(rows, parent)
            total += store_relations(conn, parent, subs, today,
                                     d.get("JCN") or d.get("securitiesCode"))
            print(f"  {parent}: 子会社{len(subs)}件")
        print(f"EDINET取り込み完了: {len(docs)}社の有報から子会社 計{total}件")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

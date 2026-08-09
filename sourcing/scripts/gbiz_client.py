#!/usr/bin/env python3
"""gBizINFO（経産省）から企業マスタをエンリッチする。

企業の資本金・従業員数・業種・設立・所在地・代表者などを法人番号ベースで補完する。
HTTP部はAPIトークン（環境変数 GBIZINFO_API_TOKEN）が必要。
パース部（parse_gbiz）はトークン不要で単体テスト可能に分離してある。

APIキー取得: https://info.gbiz.go.jp/api/  （無料 / 1日1万回）
usage: python3 gbiz_client.py --db ../data/sourcing.db   # 未エンリッチ企業を補完
"""
import argparse
import json
import urllib.parse
import urllib.request
from datetime import date

from common import DEFAULT_DB, connect
from config import get_gbizinfo_token
from http_cache import USER_AGENT
from update_db import upsert_company

API_BASE = "https://info.gbiz.go.jp/hojin/v1/hojin"


def parse_gbiz(payload: dict) -> dict:
    """gBizINFO の法人情報レスポンスを companies メタに正規化する。"""
    items = payload.get("hojin-infos") or []
    if not items:
        return {}
    h = items[0]
    meta = {
        "corporate_number": h.get("corporate_number"),
        "industry": h.get("business_summary") and None or h.get("business_items"),
        "business_summary": h.get("business_summary"),
        "website": h.get("company_url"),
        "representative_name": h.get("representative_name"),
        "established_date": h.get("date_of_establishment"),
        "capital_yen": h.get("capital_stock"),
        "employee_count": h.get("employee_number"),
        "postal_code": h.get("postal_code"),
        "prefecture": h.get("prefecture_name"),
        "city": h.get("city_name"),
        "address": (h.get("location") or None),
        "gbiz_synced_at": date.today().isoformat(),
        "source_list": "gbiz",
    }
    # 営業品目（配列）を業種文字列に
    items_list = h.get("business_items")
    if isinstance(items_list, list) and items_list:
        meta["industry"] = "・".join(str(x) for x in items_list[:3])
    return {k: v for k, v in meta.items() if v not in (None, "")}


def fetch_by_corporate_number(corporate_number: str, token: str) -> dict:
    url = f"{API_BASE}/{urllib.parse.quote(corporate_number)}"
    req = urllib.request.Request(url, headers={"X-hojinInfo-api-token": token,
                                               "User-Agent": USER_AGENT,
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def enrich_db(conn, token: str, limit: int = 500) -> int:
    """法人番号を持ち未同期の企業を gBizINFO で補完する。"""
    rows = conn.execute(
        """SELECT name, corporate_number FROM companies
           WHERE corporate_number IS NOT NULL AND gbiz_synced_at IS NULL LIMIT ?""",
        (limit,),
    ).fetchall()
    today = date.today().isoformat()
    n = 0
    for name, cn in rows:
        try:
            payload = fetch_by_corporate_number(cn, token)
        except Exception as e:
            print(f"  スキップ {name} ({cn}): {e}")
            continue
        meta = parse_gbiz(payload)
        if meta:
            upsert_company(conn, name, meta, today)
            n += 1
    conn.commit()
    return n


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()
    token = get_gbizinfo_token()
    conn = connect(args.db)
    try:
        n = enrich_db(conn, token, args.limit)
        print(f"gBizINFOエンリッチ完了: {n}社を更新")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

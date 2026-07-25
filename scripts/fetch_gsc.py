# -*- coding: utf-8 -*-
"""GSCクエリデータを取得して agent/gsc_data.json に書き出す（Phase 2 データ供給・週次実行）

実行方法:
  ローカル(Windows):  python scripts/fetch_gsc.py
  GitHub Actions:     env GSC_KEY_JSON=<JSON文字列> python scripts/fetch_gsc.py

キーの優先順位:
  1. 環境変数 GSC_KEY_JSON（JSON文字列をそのまま渡す）
  2. ファイル KEY_PATH（ローカル実行用）
"""
import json, datetime, sys, os, tempfile

KEY_PATH = r"C:\Users\tatsu\matching-app\secrets\noe-gsc-key.json"
SITE = "https://www.noe-match.com/"
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(REPO_DIR, "agent", "gsc_data.json")

from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

def _load_credentials():
    """環境変数 → ファイルの順でサービスアカウントキーを読む"""
    scopes = ["https://www.googleapis.com/auth/webmasters.readonly"]
    key_json = os.environ.get("GSC_KEY_JSON")
    if key_json:
        info = json.loads(key_json)
        return service_account.Credentials.from_service_account_info(info, scopes=scopes)
    return service_account.Credentials.from_service_account_file(KEY_PATH, scopes=scopes)

def main():
    creds = _load_credentials()
    s = AuthorizedSession(creds)
    end = datetime.date.today() - datetime.timedelta(days=2)   # GSCは2日遅れ
    start = end - datetime.timedelta(days=28)
    url = f"https://searchconsole.googleapis.com/webmasters/v3/sites/{SITE.replace('://','%3A%2F%2F').replace('/','%2F')}/searchAnalytics/query"

    def query(dimensions):
        r = s.post(url, json={
            "startDate": start.isoformat(), "endDate": end.isoformat(),
            "dimensions": dimensions, "rowLimit": 500})
        r.raise_for_status()
        return r.json().get("rows", [])

    data = {
        "fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "period": {"start": start.isoformat(), "end": end.isoformat()},
        "by_query_page": [
            {"query": r["keys"][0], "page": r["keys"][1],
             "clicks": r["clicks"], "impressions": r["impressions"],
             "ctr": round(r["ctr"], 4), "position": round(r["position"], 1)}
            for r in query(["query", "page"])],
        "by_page": [
            {"page": r["keys"][0], "clicks": r["clicks"],
             "impressions": r["impressions"], "position": round(r["position"], 1)}
            for r in query(["page"])],
    }
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"OK: {len(data['by_query_page'])} query-page rows -> {OUT_PATH}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Search Console の URL Inspection API で、記事が実際にインデックスされているかを調べる。

なぜ必要か（2026-08-01）：
GSCの検索パフォーマンスからは「表示ゼロ」しか分からず、これは
  (a) インデックスされていない
  (b) インデックス済みだがどのクエリでも100位以内に入らない（圏外）
のどちらなのか区別できない。**打ち手が正反対になる**ので、推測で進めてはいけない。

  (a) なら → クロール・内部リンク・sitemapの問題
  (b) なら → 狙ったクエリの競合の問題（記事の中身ではなく看板を直す）

2026-07-30の調査は状況証拠から (b) が主因と結論づけたが、直接の確認はしていない。
このスクリプトがその確認を行う。

出力: agent/index_status.json
  { "<url>": {"verdict":..., "coverageState":..., "lastCrawlTime":..., "robotsTxtState":...} }

注意（重要）:
  URL Inspection API は **プロパティの「オーナー」権限**が必要。
  fetch_gsc.py 用にサービスアカウントを「制限付き」で追加している場合は
  403 が返る。その場合は Search Console の
  「設定 > ユーザーと権限」でサービスアカウントを**オーナー**に昇格させること。
  権限エラーはスクリプトが明示的に報告する。

  クォータは 1日2,000URL / 1分600URL（2026年時点）。142本なら余裕がある。

使い方:
    GSC_KEY_JSON='<サービスアカウントJSON>' python3 scripts/index_check.py
    python3 scripts/index_check.py --limit 20     # 先に少数で権限を確認する
    python3 scripts/index_check.py --report       # 取得済みJSONを集計して表示するだけ
"""
import json
import os
import re
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.noe-match.com/"
OUT = os.path.join(ROOT, "agent", "index_status.json")
KEY_PATH = os.environ.get("GSC_KEY_PATH", os.path.expanduser("~/.gsc/key.json"))
ENDPOINT = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

# APIの負荷を抑える。1分600URLの制限に対して十分に余裕を持たせる。
SLEEP_SEC = 0.35


def credentials():
    try:
        from google.oauth2 import service_account
    except ImportError:
        sys.exit("google-auth が必要です: pip install google-auth")
    raw = os.environ.get("GSC_KEY_JSON")
    if raw:
        return service_account.Credentials.from_service_account_info(
            json.loads(raw), scopes=SCOPES)
    if os.path.exists(KEY_PATH):
        return service_account.Credentials.from_service_account_file(
            KEY_PATH, scopes=SCOPES)
    sys.exit("GSC_KEY_JSON も %s も見つかりません。" % KEY_PATH)


def token():
    from google.auth.transport.requests import Request
    creds = credentials()
    creds.refresh(Request())
    return creds.token


def live_urls():
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        return re.findall(r"<loc>(https?://[^<]+)</loc>", f.read())


def inspect(url, bearer):
    body = json.dumps({"inspectionUrl": url, "siteUrl": SITE}).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body,
        headers={"Authorization": "Bearer " + bearer,
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        if e.code == 403:
            raise PermissionError(
                "403: サービスアカウントに URL Inspection の権限がありません。\n"
                "Search Console の「設定 > ユーザーと権限」で、"
                "サービスアカウントを『制限付き』から『オーナー』へ昇格させてください。\n"
                "詳細: " + detail)
        return {"error": "HTTP %d" % e.code, "detail": detail}
    res = data.get("inspectionResult", {}).get("indexStatusResult", {})
    return {
        "verdict": res.get("verdict"),
        "coverageState": res.get("coverageState"),
        "robotsTxtState": res.get("robotsTxtState"),
        "indexingState": res.get("indexingState"),
        "lastCrawlTime": res.get("lastCrawlTime"),
        "pageFetchState": res.get("pageFetchState"),
        "googleCanonical": res.get("googleCanonical"),
        "userCanonical": res.get("userCanonical"),
    }


def report(status):
    from collections import Counter
    ok = {u: v for u, v in status.items() if not v.get("error")}
    print("検査済み %d URL（うちエラー %d）\n" % (len(status), len(status) - len(ok)))

    print("■ カバレッジの内訳")
    for state, n in Counter(v.get("coverageState") for v in ok.values()).most_common():
        print("   %-46s %d本" % (state, n))

    print("\n■ 判定")
    for v_, n in Counter(v.get("verdict") for v in ok.values()).most_common():
        print("   %-12s %d本" % (v_, n))

    never = [u for u, v in ok.items() if not v.get("lastCrawlTime")]
    print("\n■ 一度もクロールされていないURL: %d本" % len(never))
    for u in never[:20]:
        print("   " + u)

    # ユーザー指定canonicalとGoogleの選んだcanonicalの不一致は
    # 「重複扱いで別URLに寄せられた」ことを意味する
    mism = [(u, v) for u, v in ok.items()
            if v.get("googleCanonical") and v.get("userCanonical")
            and v["googleCanonical"] != v["userCanonical"]]
    print("\n■ Googleが別URLを正規と判断: %d本" % len(mism))
    for u, v in mism[:20]:
        print("   %s\n      → %s" % (u, v["googleCanonical"]))

    print("\n※ coverageState が『検出 - インデックス未登録』『クロール済み - "
          "インデックス未登録』なら (a) インデックスの問題。")
    print("　 『URL は Google に登録されています』なのに表示ゼロなら (b) 圏外＝クエリ選定の問題。")


def main():
    if "--report" in sys.argv:
        if not os.path.exists(OUT):
            sys.exit("%s がありません。先に取得してください。" % OUT)
        with open(OUT, encoding="utf-8") as f:
            report(json.load(f))
        return 0

    urls = live_urls()
    if "--limit" in sys.argv:
        n = int(sys.argv[sys.argv.index("--limit") + 1])
        urls = urls[:n]

    bearer = token()
    status = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            status = json.load(f)

    for i, u in enumerate(urls, 1):
        try:
            status[u] = inspect(u, bearer)
        except PermissionError as e:
            print(e)
            return 2
        if i % 20 == 0:
            print("  %d/%d ..." % (i, len(urls)))
            with open(OUT, "w", encoding="utf-8") as f:
                json.dump(status, f, ensure_ascii=False, indent=1)
        time.sleep(SLEEP_SEC)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=1)
    print("\n%s に保存した（%d URL）\n" % (OUT, len(status)))
    report(status)
    return 0


if __name__ == "__main__":
    sys.exit(main())

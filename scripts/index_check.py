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

--------------------------------------------------------------------------
API仕様（2026-08-01に公式ドキュメントで確認した内容）
--------------------------------------------------------------------------
エンドポイント : POST https://searchconsole.googleapis.com/v1/urlInspection/index:inspect
リクエスト     : {"inspectionUrl": <検査するURL>, "siteUrl": <プロパティ>,
                  "languageCode": "en-US"}
                 siteUrl は URL接頭辞プロパティなら末尾スラッシュ必須
                 （ドメインプロパティなら "sc-domain:example.com"）
レスポンス     : {"inspectionResult": {"indexStatusResult": {...},
                                       "inspectionResultLink": ...,
                                       "mobileUsabilityResult": ..., ...}}
                 indexStatusResult に verdict / coverageState / robotsTxtState /
                 indexingState / lastCrawlTime / pageFetchState / googleCanonical /
                 userCanonical / sitemap[] / referringUrls[] / crawledAs が入る
スコープ       : https://www.googleapis.com/auth/webmasters.readonly で足りる
                 （公式リファレンスは webmasters / webmasters.readonly の両方を許容）。
                 fetch_gsc.py と同じスコープなので鍵を使い回せる
権限           : **プロパティの「オーナー」権限が必須**。GSCの「ユーザーと権限」で
                 サービスアカウントを追加しただけの「フル」「制限付き」では 403 になる。
                 サービスアカウントは検証トークンを持てないので、
                 既存の確認済みオーナーが「オーナーを委任」して昇格させる必要がある
クォータ       : 1プロパティあたり **2,000 URL/日・600 URL/分**。
                 142本なら日次クォータの7%で、分次クォータにも余裕がある

languageCode を "en-US" に固定しているのは、coverageState が
**ロケール依存の翻訳済み文字列**として返るため。日本語で受けると分類が言語に依存して
壊れるので、機械判定は必ず英語文字列に対して行う（表示は日本語に訳して出す）。

--------------------------------------------------------------------------
使い方
--------------------------------------------------------------------------
    GSC_KEY_JSON='<サービスアカウントJSON>' python3 scripts/index_check.py
    python3 scripts/index_check.py --limit 5    # まず少数で権限だけ確かめる
    python3 scripts/index_check.py              # 2回目以降は取得済みURLを自動でスキップ
    python3 scripts/index_check.py --refresh    # 取得済みも含めて全件取り直す
    python3 scripts/index_check.py --report     # 取得済みJSONを集計して表示するだけ（API未使用）

出力: agent/index_status.json
    {"fetched_at":..., "site":..., "results": {"<url>": {...}}}

終了コード: 0=正常 / 1=一部のURLでAPIエラー / 2=権限・設定の問題で中断
"""
import argparse
import datetime
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.environ.get("GSC_SITE", "https://www.noe-match.com/")
OUT = os.path.join(ROOT, "agent", "index_status.json")
GSC_DATA = os.path.join(ROOT, "agent", "gsc_data.json")
KEY_PATH = os.environ.get(
    "GSC_KEY_PATH", r"C:\Users\tatsu\matching-app\secrets\noe-gsc-key.json")
ENDPOINT = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

# クォータは 600 URL/分。0.35秒間隔なら約171 URL/分で3分の1以下に収まる。
# 142本なら約50秒で終わる。日次2,000のうち142（7%）しか使わない。
DEFAULT_SLEEP = 0.35
QUOTA_PER_DAY = 2000
QUOTA_PER_MIN = 600

# 一時的な失敗はリトライする。恒久的な失敗（403等）は即座に中断する。
RETRY_STATUS = (429, 500, 502, 503, 504)
MAX_RETRY = 4

# indexStatusResult のうち保存する項目
KEEP = ("verdict", "coverageState", "robotsTxtState", "indexingState",
        "lastCrawlTime", "pageFetchState", "googleCanonical", "userCanonical",
        "crawledAs", "sitemap", "referringUrls")

# coverageState（英語）→ 内部分類。前方から順に評価する。
# 「(a) インデックスの問題」か「(b) 圏外」かの判定はここに集約する。
BUCKETS = [
    # 「Indexed, though blocked by robots.txt」のように、後段の needle にも
    # 引っかかるがインデックス自体はされている状態を先に確定させる
    ("submitted and indexed",      "INDEXED",        "インデックス済み（sitemap経由）"),
    ("indexed,",                   "INDEXED",        "インデックス済み（要確認の但し書きあり）"),
    ("unknown to google",          "NEVER_SEEN",     "Googleがこのページを認識していない"),
    ("discovered",                 "DISCOVERED",     "検出済み・未クロール"),
    ("crawled",                    "CRAWLED_NOIDX",  "クロール済み・インデックス未登録"),
    ("duplicate",                  "DUPLICATE",      "重複扱い（別URLが正規に選ばれた）"),
    ("alternate page",             "DUPLICATE",      "重複扱い（別URLが正規に選ばれた）"),
    ("redirect",                   "REDIRECT",       "リダイレクトとして扱われている"),
    ("excluded by",                "EXCLUDED",       "noindex/robots等で除外"),
    ("blocked",                    "BLOCKED",        "クロールがブロックされている"),
    ("not found",                  "NOTFOUND",       "404"),
    ("soft 404",                   "NOTFOUND",       "ソフト404"),
    ("server error",               "SERVER_ERROR",   "サーバーエラー"),
    ("indexed",                    "INDEXED",        "インデックス済み"),
]
# INDEXED だけが (b)。それ以外はすべて (a)。
INDEXED_KINDS = {"INDEXED"}


def classify(entry):
    """1URLの結果を (kind, 日本語ラベル) に落とす。判定は英語文字列に対して行う。"""
    if entry.get("error"):
        return "ERROR", "取得失敗"
    state = (entry.get("coverageState") or "").lower()
    for needle, kind, label in BUCKETS:
        if needle in state:
            return kind, label
    # coverageState が想定外でも verdict は使える
    if entry.get("verdict") == "PASS":
        return "INDEXED", "インデックス済み（coverageState未分類）"
    return "OTHER", "未分類: %s" % (entry.get("coverageState") or "(空)")


# ---------------------------------------------------------------- 認証・通信

def session():
    """fetch_gsc.py と同じ AuthorizedSession を使う。

    自前で1回だけトークンを取ると、途中でリトライ待ちが入ったときに
    1時間の有効期限を超えて 401 になる。AuthorizedSession は自動で更新する。
    """
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        sys.exit("google-auth が必要です: pip install google-auth requests")

    raw = os.environ.get("GSC_KEY_JSON")
    if raw:
        creds = service_account.Credentials.from_service_account_info(
            json.loads(raw), scopes=SCOPES)
    elif os.path.exists(KEY_PATH):
        creds = service_account.Credentials.from_service_account_file(
            KEY_PATH, scopes=SCOPES)
    else:
        sys.exit("GSC_KEY_JSON も %s も見つかりません。" % KEY_PATH)
    return AuthorizedSession(creds)


class Fatal(Exception):
    """権限・設定の誤りなど、続けても全URLで同じように失敗するもの。"""


def _explain_fatal(status, payload, text):
    err = (payload.get("error") or {}) if isinstance(payload, dict) else {}
    reason = ""
    for d in err.get("details", []) or []:
        reason = d.get("reason") or reason
    msg = err.get("message", "") or text[:300]

    if status == 403 and "SERVICE_DISABLED" in (reason + msg):
        return ("403 (SERVICE_DISABLED): GCPプロジェクトで Google Search Console API が\n"
                "有効化されていません。Cloud Console の「APIとサービス」で\n"
                "「Google Search Console API」を有効にしてください。\n詳細: " + msg)
    if status == 403:
        return ("403: サービスアカウントに URL Inspection の権限がありません。\n"
                "URL Inspection API は **オーナー権限が必須** で、\n"
                "「フル」「制限付き」では通りません（検索パフォーマンスAPIは通るので\n"
                "fetch_gsc.py が動いていても権限が足りているとは限りません）。\n"
                "GSC →「設定 > ユーザーと権限」→ 該当サービスアカウントの行 →\n"
                "「オーナーを委任」で昇格させてください。\n"
                "同じ403は siteUrl(%s) の指定違い・inspectionUrl がプロパティ外の\n"
                "場合にも返ります。\n詳細: %s" % (SITE, msg))
    if status == 401:
        return "401: 認証に失敗しました。鍵JSONとスコープを確認してください。\n詳細: " + msg
    if status == 404:
        return ("404: siteUrl '%s' がこのアカウントのプロパティとして見つかりません。\n"
                "URL接頭辞プロパティは末尾スラッシュ必須、ドメインプロパティは\n"
                "'sc-domain:noe-match.com' 形式です。\n詳細: %s" % (SITE, msg))
    return None


def inspect(sess, url):
    body = {"inspectionUrl": url, "siteUrl": SITE, "languageCode": "en-US"}
    delay = 2.0
    for attempt in range(MAX_RETRY):
        try:
            r = sess.post(ENDPOINT, json=body, timeout=60)
        except Exception as e:                      # ネットワーク断など
            if attempt == MAX_RETRY - 1:
                return {"error": "network", "detail": str(e)[:300]}
            time.sleep(delay)
            delay *= 2
            continue

        if r.status_code == 200:
            res = (r.json().get("inspectionResult") or {})
            out = {k: (res.get("indexStatusResult") or {}).get(k) for k in KEEP}
            out["inspectionResultLink"] = res.get("inspectionResultLink")
            out["checked_at"] = datetime.datetime.now(
                datetime.timezone.utc).replace(microsecond=0).isoformat()
            return out

        text = r.text
        try:
            payload = r.json()
        except ValueError:
            payload = {}

        fatal = _explain_fatal(r.status_code, payload, text)
        if fatal:
            raise Fatal(fatal)

        if r.status_code in RETRY_STATUS and attempt < MAX_RETRY - 1:
            # 429 は分次クォータ（600/分）超過。待てば回復する。
            time.sleep(delay)
            delay *= 2
            continue
        return {"error": "HTTP %d" % r.status_code, "detail": text[:300]}
    return {"error": "retry_exhausted"}


# ---------------------------------------------------------------- 入出力

def live_urls():
    """sitemap.xml に載っているURL（＝出荷済みのもの）"""
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        found = re.findall(r"<loc>\s*(https?://[^<\s]+)\s*</loc>", f.read())
    seen, urls = set(), []
    for u in found:                                  # 重複はクォータの無駄
        if u not in seen:
            seen.add(u)
            urls.append(u)
    return urls


def load():
    """途中で落ちても続きから流せるよう、既存の結果を読む（旧形式も受ける）"""
    if not os.path.exists(OUT):
        return {}
    with open(OUT, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "results" in data:
        return data["results"]
    return data if isinstance(data, dict) else {}


def save(results):
    tmp = OUT + ".tmp"
    payload = {
        "fetched_at": datetime.datetime.now(
            datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "site": SITE,
        "results": results,
    }
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, OUT)          # 保存中に落ちても既存ファイルを壊さない


# ---------------------------------------------------------------- 集計

def zero_impression_urls():
    """GSCの検索パフォーマンスで表示が1回も立っていないURL（sitemap基準）"""
    if not os.path.exists(GSC_DATA):
        return None
    with open(GSC_DATA, encoding="utf-8") as f:
        gsc = json.load(f)
    shown = {p["page"].rstrip("/") + "/" for p in gsc.get("by_page", [])
             if p.get("impressions", 0) > 0}
    return {u for u in live_urls() if u.rstrip("/") + "/" not in shown}


STALE_DAYS = 3


def gsc_is_stale():
    """表示データがインデックス検査より古いと (a)/(b) の切り分けが壊れる。

    2026-08-09に実際に踏んだ：申請で21本が新たにインデックスされた直後に、
    8日前の表示データと突き合わせて「圏外44本」と出た。その21本は表示データの
    取得時点でインデックスされていないのだから、表示が無いのは当たり前で、
    圏外（クエリ選定の失敗）ではない。打ち手を誤らせるので出さない。
    """
    if not os.path.exists(GSC_DATA):
        return True
    try:
        with open(GSC_DATA, encoding="utf-8") as f:
            fetched = json.load(f).get("fetched_at") or ""
        d = datetime.datetime.fromisoformat(fetched.replace("Z", "+00:00"))
    except Exception:
        return True
    # fetch_gsc.py はタイムゾーンなしで書く。UTCとみなす
    if d.tzinfo is None:
        d = d.replace(tzinfo=datetime.timezone.utc)
    now = datetime.datetime.now(datetime.timezone.utc)
    return (now - d).days > STALE_DAYS


def report(results):
    from collections import Counter

    ok = {u: v for u, v in results.items() if not v.get("error")}
    bad = {u: v for u, v in results.items() if v.get("error")}
    print("検査済み %d URL（うち取得失敗 %d）\n" % (len(results), len(bad)))
    if not ok:
        for u, v in list(bad.items())[:10]:
            print("   %s → %s %s" % (u, v.get("error"), v.get("detail", "")[:80]))
        return

    kinds = {u: classify(v)[0] for u, v in ok.items()}
    labels = dict((k, l) for _, k, l in BUCKETS)

    print("■ カバレッジの内訳")
    for kind, n in Counter(kinds.values()).most_common():
        print("   %-14s %-40s %3d本" % (kind, labels.get(kind, ""), n))

    print("\n■ verdict")
    for v_, n in Counter(v.get("verdict") for v in ok.values()).most_common():
        print("   %-14s %3d本" % (v_, n))

    indexed = {u for u, k in kinds.items() if k in INDEXED_KINDS}
    not_indexed = set(ok) - indexed

    # ---- 本題：表示ゼロの正体が (a) なのか (b) なのか
    zero = zero_impression_urls()
    print("\n" + "=" * 66)
    if zero is None:
        print("agent/gsc_data.json が無いので (a)/(b) の切り分けは省略した。")
    elif gsc_is_stale():
        print("agent/gsc_data.json が古いので (a)/(b) の切り分けは出さない。")
        print("  表示データの取得日より後にインデックスされた記事は、"
              "「まだ表示が立っていない」のではなく")
        print("  **表示データの窓に存在していなかった**だけである。"
              "これを圏外(b)として数えると水増しになる。")
        print("  先に `python3 scripts/fetch_gsc.py` を回してから読み直すこと。")
    else:
        zero_ok = zero & set(ok)
        a = sorted(zero_ok & not_indexed)
        b = sorted(zero_ok & indexed)
        print("表示ゼロ %d本の内訳（検査できたのは %d本）" % (len(zero), len(zero_ok)))
        print("  (a) インデックスされていない        : %3d本  → クロール/sitemap/内部リンクの問題"
              % len(a))
        print("  (b) インデックス済みだが表示ゼロ＝圏外: %3d本  → クエリ選定の問題（看板を直す）"
              % len(b))
        if zero_ok:
            share = 100.0 * len(b) / len(zero_ok)
            print("\n  → (b) が %.1f%%。%s" % (
                share,
                "2026-07-30の結論（クエリ競合が主因）は支持される。"
                if share >= 70 else
                "2026-07-30の結論と矛盾する。流通側の点検を優先すること。"
                if share <= 30 else
                "どちらとも言えない。両方の打ち手を並行させる。"))
        for title, group in (("(a) の内訳", a),):
            if group:
                print("\n  %s（先頭20件）" % title)
                for u in group[:20]:
                    print("     %-58s %s" % (u.replace("https://www.noe-match.com", ""),
                                             labels.get(kinds[u], kinds[u])))
    print("=" * 66)

    # ---- 補助的な事実
    never = [u for u in ok if not ok[u].get("lastCrawlTime")]
    print("\n■ 一度もクロールされていないURL: %d本" % len(never))
    for u in never[:20]:
        print("   " + u)

    no_sitemap = [u for u in ok if not ok[u].get("sitemap")]
    print("\n■ Googleがsitemap経由で認識していないURL: %d本" % len(no_sitemap))
    print("   （sitemap.xml に載せていても Google 側の記録に無ければ、"
          "sitemapが読まれていない可能性がある）")
    for u in no_sitemap[:20]:
        print("   " + u)

    mism = [(u, v) for u, v in ok.items()
            if v.get("googleCanonical") and v.get("userCanonical")
            and v["googleCanonical"].rstrip("/") != v["userCanonical"].rstrip("/")]
    print("\n■ Googleが別URLを正規と判断: %d本" % len(mism))
    for u, v in mism[:20]:
        print("   %s\n      → %s" % (u, v["googleCanonical"]))

    if bad:
        print("\n■ 取得失敗（再実行すれば続きから取り直す）: %d本" % len(bad))
        for u, v in list(bad.items())[:10]:
            print("   %s → %s" % (u, v.get("error")))


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true",
                    help="取得済みの agent/index_status.json を集計するだけ（API未使用）")
    ap.add_argument("--refresh", action="store_true",
                    help="取得済みURLも取り直す（既定は未取得分だけ）")
    ap.add_argument("--limit", type=int, help="先頭N件だけ検査する（権限の事前確認用）")
    ap.add_argument("--sleep", type=float, default=DEFAULT_SLEEP,
                    help="1URLごとの待ち時間（既定 %.2f秒）" % DEFAULT_SLEEP)
    args = ap.parse_args()

    results = load()

    if args.report:
        if not results:
            sys.exit("%s がありません。先に取得してください。" % OUT)
        report(results)
        return 0

    urls = live_urls()
    if args.limit:
        urls = urls[:args.limit]

    todo = urls if args.refresh else [
        u for u in urls if u not in results or results[u].get("error")]
    print("sitemap %d URL / 今回検査 %d URL（取得済みスキップ %d）"
          % (len(urls), len(todo), len(urls) - len(todo)))
    if len(todo) > QUOTA_PER_DAY:
        print("⚠ 1日のクォータ %d URL を超えます。分割して実行してください。" % QUOTA_PER_DAY)
    if todo and 60.0 / max(args.sleep, 1e-6) > QUOTA_PER_MIN:
        print("⚠ --sleep %.2f は分次クォータ %d URL/分 を超えます。" % (args.sleep, QUOTA_PER_MIN))
    if not todo:
        report(results)
        return 0

    sess = session()
    interrupted = False
    try:
        for i, u in enumerate(todo, 1):
            results[u] = inspect(sess, u)
            if i % 20 == 0 or i == len(todo):
                print("  %d/%d ..." % (i, len(todo)))
                save(results)          # 20件ごとに保存＝落ちても続きから流せる
            time.sleep(args.sleep)
    except Fatal as e:
        save(results)
        print("\n" + str(e))
        return 2
    except KeyboardInterrupt:
        interrupted = True
    finally:
        save(results)

    print("\n%s に保存した（%d URL）\n" % (OUT, len(results)))
    report(results)
    if interrupted:
        print("\n中断した。再実行すれば未取得分だけを続きから取得する。")
        return 1
    return 1 if any(v.get("error") for v in results.values()) else 0


if __name__ == "__main__":
    sys.exit(main())

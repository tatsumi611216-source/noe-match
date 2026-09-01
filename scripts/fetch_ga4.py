# -*- coding: utf-8 -*-
"""GA4のセッションを日次で取り込む（2026-09-01 新設）

なぜ必要か:
GSCは自動取得しているのにGA4は手動読み取りしかしておらず、**データ記事とバンクの
価値が継続的に測れていない**。データ記事の主な流入はAI（chatgpt・copilot）とBingで、
GSCには一切出ない。GSCだけを見ると「データ記事は表示4.1/本で最弱」に見えるが、
2026-08-27に手でGA4を見たときはデータ記事1.28セッション/本・通常記事0.24（5.3倍）だった。
**判断の土台が片方しか自動化されていない状態を解消する。**

設計は scripts/gsc_archive.py と揃える:
- 日別に1ファイル（agent/ga4_archive/YYYY-MM-DD.json）。取得済みの日は飛ばす
- 直近N日の欠損を埋め直す差分モード（数日落ちても自力で復旧する）
- 認証は「環境変数 → ファイル」の2経路（CIに載せられる形にしておく）

認証（2026-09-01 に実機で確認・追加の権限付与は不要だった）:
  GA4のプロパティ「Noe結婚設計室 noe-match.com」（properties/549779769）には、既に
  gsc-ga4-analytics@matching-app-analytics.iam.gserviceaccount.com が閲覧者として
  登録されていた。その鍵を secrets/noe-ga4-key.json に置いて使う。
  **GSC用の noe-gsc-reader とは別のサービスアカウント（プロジェクトも別）** なので、
  CIに載せるときは GSC_KEY_JSON ではなく GA4_KEY_JSON に入れる。

使い方:
  python scripts/fetch_ga4.py            未取得日を埋める（既定45日ぶん）
  python scripts/fetch_ga4.py --days 90  さかのぼる日数を変える
  python scripts/fetch_ga4.py --stats    取得済みの集計だけ（API未使用）
  python scripts/fetch_ga4.py --report   ページ種別ごとの実績を出す（API未使用）

限界（正直に書く）:
- GA4は当日ぶんが確定しない。**当日と前日は取りに行かない**（2日前まで）
- 参照元の分類はGA4の既定チャネルグループをそのまま使う。AI検索（chatgpt.com等）は
  多くが Referral に入るため、sessionSource も一緒に保存して後から数え直せるようにする
"""
import argparse
import datetime
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARC = os.path.join(ROOT, "agent", "ga4_archive")
KEY_PATH = r"C:\Users\tatsu\matching-app\secrets\noe-ga4-key.json"
PROPERTY_ID = "properties/549779769"   # Noe結婚設計室 noe-match.com（2026-09-01 実機で確認）
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
DEFAULT_DAYS = 45
SETUP_HINT = (
    "GA4のAPIが使えない。次の2つを1回だけ済ませる必要がある:\n"
    "  1) GCPプロジェクト noe-gsc で Google Analytics Data API と Admin API を有効化\n"
    "  2) GA4のプロパティのアクセス管理で "
    "noe-gsc-reader@noe-gsc.iam.gserviceaccount.com に「閲覧者」を付与")


def credentials():
    from google.oauth2 import service_account
    key_json = os.environ.get("GA4_KEY_JSON")
    if key_json:
        return service_account.Credentials.from_service_account_info(
            json.loads(key_json), scopes=SCOPES)
    return service_account.Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)


def resolve_property(creds):
    """プロパティIDを決める。環境変数 → 定数 → Admin APIで自動検出。"""
    pid = os.environ.get("GA4_PROPERTY_ID") or PROPERTY_ID
    if pid:
        return pid if pid.startswith("properties/") else "properties/%s" % pid
    from google.analytics.admin import AnalyticsAdminServiceClient
    client = AnalyticsAdminServiceClient(credentials=creds)
    found = []
    for s in client.list_account_summaries():
        for p in s.property_summaries:
            found.append((p.display_name, p.property))
    if not found:
        raise SystemExit("GA4のプロパティが1つも見えない。\n" + SETUP_HINT)
    for name, prop in found:
        if "noe-match" in name.lower() or "noe" in name.lower():
            print("プロパティ自動検出: %s (%s)" % (name, prop))
            return prop
    print("プロパティ自動検出: %s (%s)" % found[0])
    return found[0][1]


def fetch_day(creds, prop, day):
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Metric, RunReportRequest)
    client = BetaAnalyticsDataClient(credentials=creds)
    ds = day.isoformat()

    req = RunReportRequest(
        property=prop,
        date_ranges=[DateRange(start_date=ds, end_date=ds)],
        dimensions=[Dimension(name="pagePath"),
                    Dimension(name="sessionDefaultChannelGroup"),
                    Dimension(name="sessionSource")],
        metrics=[Metric(name="sessions"), Metric(name="activeUsers"),
                 Metric(name="screenPageViews")],
        limit=100000)
    rows = []
    for r in client.run_report(req).rows:
        rows.append({
            "path": r.dimension_values[0].value,
            "channel": r.dimension_values[1].value,
            "source": r.dimension_values[2].value,
            "sessions": int(r.metric_values[0].value),
            "users": int(r.metric_values[1].value),
            "views": int(r.metric_values[2].value),
        })

    ev = RunReportRequest(
        property=prop,
        date_ranges=[DateRange(start_date=ds, end_date=ds)],
        dimensions=[Dimension(name="eventName")],
        metrics=[Metric(name="eventCount")],
        limit=1000)
    events = {r.dimension_values[0].value: int(r.metric_values[0].value)
              for r in client.run_report(ev).rows}

    return {
        "date": ds, "property": prop,
        "fetched_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "total": {
            "sessions": sum(x["sessions"] for x in rows),
            "users": sum(x["users"] for x in rows),
            "views": sum(x["views"] for x in rows),
        },
        "by_page": rows,
        "events": events,
    }


# ---------------- 集計（APIを使わない） ----------------
import re  # noqa: E402

BANK = re.compile(r"(daredemo-tsuen|sangokea|kodomo-iryohi|hitorioya|ikukyu|shussan"
                  r"|kekkon-shinseikatsu|byoji|funin-josei|hoikuen-tensu)")


def kind_of(path):
    p = path.strip("/")
    if p.startswith("tools/"):
        return "ツール（バンク由来）" if BANK.search(p) else "ツール（その他）"
    if p.startswith("articles/"):
        s = p[len("articles/"):]
        if BANK.search(s):
            return "データ記事（バンク由来）"
        if s.endswith("-data"):
            return "データ記事（統計）"
        return "通常記事"
    if p in ("", "index.html"):
        return "トップ"
    return "その他"


def files():
    return sorted([os.path.join(ARC, f) for f in os.listdir(ARC)]) if os.path.isdir(ARC) else []


def stats():
    fs = files()
    if not fs:
        print("まだ1日も取得していない。")
        return
    days = [os.path.basename(f)[:-5] for f in fs]
    tot = {"sessions": 0, "users": 0, "views": 0}
    for f in fs:
        t = json.load(io.open(f, encoding="utf-8"))["total"]
        for k in tot:
            tot[k] += t.get(k, 0)
    print("保存日数: %d日（%s 〜 %s）" % (len(fs), days[0], days[-1]))
    print("合計  セッション %d / ユーザー %d / PV %d" % (tot["sessions"], tot["users"], tot["views"]))
    d0 = datetime.date.fromisoformat(days[0]); d1 = datetime.date.fromisoformat(days[-1])
    want = {(d0 + datetime.timedelta(n)).isoformat() for n in range((d1 - d0).days + 1)}
    miss = sorted(want - set(days))
    print("期間内の欠損: %d日 %s" % (len(miss), miss[:10]))


def report(days=28):
    fs = files()[-days:]
    if not fs:
        print("まだ1日も取得していない。")
        return
    import collections
    agg = collections.defaultdict(lambda: [0, 0, set()])
    ch = collections.Counter()
    src = collections.Counter()
    for f in fs:
        d = json.load(io.open(f, encoding="utf-8"))
        for r in d["by_page"]:
            k = kind_of(r["path"])
            a = agg[k]
            a[0] += r["sessions"]; a[1] += r["views"]; a[2].add(r["path"])
            ch[r["channel"]] += r["sessions"]
            src[r["source"]] += r["sessions"]
    print("直近%d日（%s〜%s）" % (len(fs), os.path.basename(fs[0])[:-5], os.path.basename(fs[-1])[:-5]))
    print("\n%-22s %5s %8s %8s %10s" % ("種別", "本数", "セッション", "PV", "1本あたり"))
    for k, (s, v, ps) in sorted(agg.items(), key=lambda kv: -kv[1][0]):
        print("%-24s %4d %8d %8d %10.2f" % (k, len(ps), s, v, s / max(len(ps), 1)))
    print("\nチャネル別セッション:", dict(ch.most_common(8)))
    print("参照元 上位:", dict(src.most_common(10)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=DEFAULT_DAYS)
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    if a.stats:
        return stats()
    if a.report:
        return report()

    os.makedirs(ARC, exist_ok=True)
    end = datetime.date.today() - datetime.timedelta(days=2)   # 当日・前日は確定しない
    start = end - datetime.timedelta(days=a.days - 1)
    have = {os.path.basename(f)[:-5] for f in files()}
    todo = [start + datetime.timedelta(n) for n in range((end - start).days + 1)
            if (start + datetime.timedelta(n)).isoformat() not in have]
    print("対象 %d日 ／ 未取得 %d日（%s 〜 %s）" % (a.days, len(todo), start, end))
    if not todo:
        return stats()

    try:
        creds = credentials()
        prop = resolve_property(creds)
    except SystemExit:
        raise
    except Exception as e:
        print("認証・プロパティ解決に失敗: %s: %s" % (type(e).__name__, str(e)[:200]))
        print(SETUP_HINT)
        return 1

    n = 0
    for day in todo:
        try:
            d = fetch_day(creds, prop, day)
        except Exception as e:
            print("  %s 取得失敗: %s: %s" % (day, type(e).__name__, str(e)[:160]))
            print(SETUP_HINT)
            break
        io.open(os.path.join(ARC, "%s.json" % day.isoformat()), "w", encoding="utf-8").write(
            json.dumps(d, ensure_ascii=False, indent=1))
        t = d["total"]
        print("  %s  セッション %3d  ユーザー %3d  PV %3d  ページ %d"
              % (day, t["sessions"], t["users"], t["views"], len(d["by_page"])))
        n += 1
    print("新規保存: %d日" % n)
    stats()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main() or 0)

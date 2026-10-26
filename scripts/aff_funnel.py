# -*- coding: utf-8 -*-
"""広告の「表示 → クリック」を linkId 別に出す（2026-09-27 新設・aff_clicks.py の拡張）

なぜ必要か:
2026-09-27 のCEO決定で、収益化はアフィリ単独に切り替えた。クリックが月数件しか出ない規模では、
クリックだけを見ても「見られていないのか、見ても押されないのか」が分からない。
そこで広告枠が画面に50%以上入ったときに `affv_<linkId>` を送るようにした
（scripts/aff_only_20260927.py が差し込む AFF-VIEW。feat/product-funnel-20260925 の
prod23_cta_view と同じ作り）。クリックは GA4 内蔵の click（linkId に <a> の id が入る）で取る。

  表示  affv_soudanjo       ← id="aff-soudanjo" の広告枠が画面に入った（1ページ表示につき1回）
  クリック click × linkId=aff-soudanjo

イベント名に linkId を入れているのは、GA4 のカスタムディメンションが未登録で、パラメータで送っても
集計できないため（agent/knowledge.md 2026-09-04）。ページは GA4 の pagePath で分かる。
自社の検品アクセス（?noe_qa=1 を付けて開いたブラウザ）と本番以外のホストからは送っていない。

使い方:
  python scripts/aff_funnel.py                    直近28日（アーカイブのみ・API未使用）
  python scripts/aff_funnel.py --days 56
  python scripts/aff_funnel.py --start 2026-09-28 --end 2026-10-31
  python scripts/aff_funnel.py --live             GA4 API を直接読む（アーカイブ未取得の日も含む）

読み方:
  表示0・クリック0 … 広告枠まで読まれていない（位置か流入の問題）
  表示あり・クリック0 … 見られているが押されない（案件か文言の問題）
  表示の計測は 2026-09-27 の差し込み以降のみ。それより前の期間はクリックだけが出る。
"""
import argparse
import collections
import datetime
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARC = os.path.join(ROOT, "agent", "ga4_archive")
AFF_DOMAINS = ("px.a8.net", "t.afi-b.com")
VIEW_PREFIX = "affv_"


def view_to_link(ev):
    return "aff-" + ev[len(VIEW_PREFIX):].replace("_", "-")


def ledger():
    led = {}
    for line in io.open(os.path.join(ROOT, "agent", "AGENT.md"), encoding="utf-8"):
        m = re.match(r'\|\s*([^|]+?)\s*\|\s*(https://(?:px\.a8\.net|t\.afi-b\.com)\S+)\s*\|', line)
        if m:
            led[m.group(2)] = m.group(1)
    return led


SCLICKS = collections.Counter()   # (path, linkId) → 1セッション1回に絞ったクリック（affc_・2026-10-08〜）
URLS = {}   # (path, linkId) → クリックされた linkUrl（id の無い古いクリックの案件名に使う）


def program_of(path, link_id, led, cache={}):
    """いまのページの HTML から linkId の飛び先を引き、台帳の案件名にする"""
    if (path, link_id) in URLS and link_id == "(idなし)":
        return led.get(URLS[(path, link_id)], "（台帳外）")
    if path not in cache:
        f = os.path.join(ROOT, path.strip("/"), "index.html")
        cache[path] = io.open(f, encoding="utf-8").read() if os.path.isfile(f) else ""
    m = re.search(r'<a\b[^>]*\bid="%s"[^>]*>' % re.escape(link_id), cache[path])
    if not m:
        return "（ページに無い）"
    u = re.search(r'href="([^"]+)"', m.group(0))
    return led.get(u.group(1).replace("&amp;", "&"), "（台帳外）") if u else "?"


def period(a):
    end = a.end or (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
    start = a.start or (datetime.date.fromisoformat(end) - datetime.timedelta(days=a.days - 1)).isoformat()
    return start, end


def from_archive(start, end):
    views, clicks, days, no_views = collections.Counter(), collections.Counter(), 0, 0
    SCLICKS.clear()
    for f in sorted(os.listdir(ARC)):
        ds = f[:-5]
        if not f.endswith(".json") or not (start <= ds <= end):
            continue
        d = json.load(io.open(os.path.join(ARC, f), encoding="utf-8"))
        days += 1
        if "aff_views" not in d:
            no_views += 1
        for r in d.get("aff_views", []):
            views[(r["path"], view_to_link(r["event"]))] += r["count"]
        for r in d.get("aff_session_clicks", []):
            SCLICKS[(r["path"], "aff-" + r["event"][len("affc_"):].replace("_", "-"))] += r["count"]
        for c in d.get("clicks", []):
            if c.get("linkDomain") in AFF_DOMAINS:
                k = (c["path"], c.get("linkId") or "(idなし)")
                clicks[k] += c["count"]
                URLS[k] = c.get("linkUrl", "")
    return views, clicks, {"days": days, "no_views": no_views}


def from_live(start, end):
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from fetch_ga4 import credentials, PROPERTY_ID
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Filter, FilterExpression, Metric, RunReportRequest)
    c = BetaAnalyticsDataClient(credentials=credentials())

    def run(dims, flt):
        req = RunReportRequest(property=PROPERTY_ID,
                               date_ranges=[DateRange(start_date=start, end_date=end)],
                               dimensions=[Dimension(name=x) for x in dims],
                               metrics=[Metric(name="eventCount")],
                               dimension_filter=FilterExpression(filter=flt), limit=10000)
        return [([d.value for d in r.dimension_values], int(r.metric_values[0].value))
                for r in c.run_report(req).rows]
    views, clicks = collections.Counter(), collections.Counter()
    for (path, ev), n in run(["pagePath", "eventName"], Filter(
            field_name="eventName", string_filter=Filter.StringFilter(
                value=VIEW_PREFIX, match_type=Filter.StringFilter.MatchType.BEGINS_WITH))):
        views[(path, view_to_link(ev))] += n
    for (path, lid, dom, url), n in run(["pagePath", "linkId", "linkDomain", "linkUrl"], Filter(
            field_name="eventName", string_filter=Filter.StringFilter(value="click"))):
        if dom in AFF_DOMAINS:
            k = (path, lid if lid and lid != "(not set)" else "(idなし)")
            clicks[k] += n
            URLS[k] = url
    return views, clicks, {"days": None, "no_views": 0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--live", action="store_true")
    a = ap.parse_args()
    start, end = period(a)
    views, clicks, meta = (from_live if a.live else from_archive)(start, end)
    led = ledger()

    print("期間 %s 〜 %s（%s）" % (start, end, "GA4 API" if a.live else "アーカイブ %d日" % meta["days"]))
    if meta["no_views"]:
        print("  ※うち %d日は表示計測（aff_views）が無い日。表示は 2026-09-27 の差し込み以降のみ" % meta["no_views"])

    keys = sorted(set(views) | set(clicks), key=lambda k: (-views[k], -clicks[k], k))
    print("\n■ ページ × linkId（表示 → クリック）")
    keys = sorted(set(keys) | set(SCLICKS), key=lambda k: (-views[k], -clicks[k], k))
    print("  %5s %5s %6s %7s  %-44s %-18s %s" % ("表示", "click", "1S1回", "率", "ページ", "linkId", "案件"))
    for k in keys:
        v, n = views[k], clicks[k]
        r = "%.1f%%" % (100.0 * n / v) if v else "—"
        print("  %5d %5d %6d %7s  %-44s %-18s %s" % (v, n, SCLICKS[k], r, k[0][:44], k[1], program_of(k[0], k[1], led)))
    print("  ※1S1回＝同じセッション・同じ枠のクリックを1回に絞った数（affc_・2026-10-08 の差し込み以降のみ）")

    by_prog_v, by_prog_c = collections.Counter(), collections.Counter()
    for k in keys:
        p = program_of(k[0], k[1], led)
        by_prog_v[p] += views[k]
        by_prog_c[p] += clicks[k]
    print("\n■ 案件別")
    for p in sorted(by_prog_v, key=lambda x: (-by_prog_v[x], -by_prog_c[x])):
        v, n = by_prog_v[p], by_prog_c[p]
        print("  表示 %5d  click %4d  %7s  %s" % (v, n, "%.1f%%" % (100.0 * n / v) if v else "—", p))
    print("\n  合計  表示 %d / クリック %d" % (sum(views.values()), sum(clicks.values())))
    print("  ※案件名はいまのページのHTMLから引いている。期間中に差し替えた広告は現行の案件名で出る")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

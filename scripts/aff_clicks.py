# -*- coding: utf-8 -*-
"""広告クリックの正式な計器（2026-09-04 新設）

なぜ必要か:
9/1にA8のクリック数とGA4の自作 `aff_click` が25倍食い違い、「収益導線は測れない」と
結論していた。9/4に調べ直したところ、**GA4には内蔵の outbound click 計測が最初から
動いており、`pagePath` と `linkUrl` まで取れる**ことが分かった。7/17〜9/3の49日で
px.a8.net への click は6件、同期間のA8は約80件。**GSCクリック3件の月にA8が52件を
計上していた**ことから、水増しはA8側と判断した（クローラのhref追跡・プリフェッチ・
自社検品——GA4の内部トラフィック除外はA8には効かない）。

したがって収益導線の分母は**A8のクリック数ではなくこの数字**を使う。
自作の `aff_click` は内蔵より件数を取りこぼす（6→2）ので参考値に落とす。

使い方:
  python scripts/aff_clicks.py                 直近45日
  python scripts/aff_clicks.py --days 90
  python scripts/aff_clicks.py --start 2026-08-01 --end 2026-08-31
"""
import argparse
import datetime
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_ga4 import credentials, PROPERTY_ID  # noqa: E402

AFF_DOMAINS = ("px.a8.net", "t.afi-b.com")


def _client():
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    return BetaAnalyticsDataClient(credentials=credentials())


def _rows(client, dims, start, end, event_names):
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Filter, FilterExpression, Metric, RunReportRequest)
    req = RunReportRequest(
        property=PROPERTY_ID,
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name=d) for d in dims],
        metrics=[Metric(name="eventCount")],
        dimension_filter=FilterExpression(filter=Filter(
            field_name="eventName",
            in_list_filter=Filter.InListFilter(values=list(event_names)))),
        limit=500)
    res = client.run_report(req)
    return [([d.value for d in r.dimension_values], int(r.metric_values[0].value))
            for r in res.rows]


def _sessions(client, start, end):
    """セッション数はイベント数ではなく sessions 指標で取る（session_start とは25%ずれる）"""
    from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
    req = RunReportRequest(
        property=PROPERTY_ID,
        date_ranges=[DateRange(start_date=start, end_date=end)],
        metrics=[Metric(name="sessions")])
    res = client.run_report(req)
    return int(res.rows[0].metric_values[0].value) if res.rows else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=45)
    ap.add_argument("--start")
    ap.add_argument("--end")
    a = ap.parse_args()
    today = datetime.date.today()
    end = a.end or (today - datetime.timedelta(days=1)).isoformat()
    start = a.start or (datetime.date.fromisoformat(end) -
                        datetime.timedelta(days=a.days - 1)).isoformat()

    c = _client()
    print(f"期間 {start} 〜 {end}")

    total_aff = 0
    print("\n■ 外部リンクのクリック（内蔵計測 click）")
    for (dom,), n in sorted(_rows(c, ["linkDomain"], start, end, ["click"]),
                            key=lambda x: -x[1]):
        mark = " ← 広告" if dom in AFF_DOMAINS else ""
        if dom in AFF_DOMAINS:
            total_aff += n
        print(f"  {n:>4}  {dom or '(不明)'}{mark}")

    print("\n■ 広告クリックが起きたページ")
    for (path, dom, url), n in sorted(
            _rows(c, ["pagePath", "linkDomain", "linkUrl"], start, end, ["click"]),
            key=lambda x: -x[1]):
        if dom not in AFF_DOMAINS:
            continue
        print(f"  {n:>4}  {path}\n        {url[:100]}")

    legacy = sum(n for _, n in _rows(c, ["eventName"], start, end, ["aff_click"]))
    sessions = _sessions(c, start, end)
    print(f"\n■ まとめ")
    print(f"  広告クリック（正式）      : {total_aff}")
    print(f"  自作 aff_click（参考値）  : {legacy}")
    print(f"  セッション                : {sessions}")
    if sessions:
        print(f"  クリック率                : {total_aff / sessions * 100:.2f}%")
    print("\n  ※A8管理画面のクリック数は実需と無相関に膨らむため判断に使わない（agent/knowledge.md 9/4）")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    main()

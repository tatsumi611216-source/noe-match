# -*- coding: utf-8 -*-
"""クラスタ別にGSCとGA4を突き合わせる（2026-09-01 新設）

なぜ:
`cluster_gsc.py` は検索（表示・クリック）しか見ていない。だがGA4を入れて、
**流入の29%がAI（chatgpt・copilot）経由で、これはGSCに1件も出ない**ことが分かった。
検索だけでクラスタを評価すると、AIで読まれているクラスタを過小評価する。
2つの計器を1枚に並べて、クラスタごとに「どの経路で来ているか」を見る。

出力する列:
  GSC   … click / 表示 / 平均順位（表示で加重）
  GA4   … セッション（Direct除き）／うちAI経由／1本あたりセッション
  収益  … そのクラスタのページに置いてあるアフィリリンクの本数

Directを除くのは、自社の検品作業が混じるため（2026-08-31 知見）。

2026-09-04 追記:
- 期間の取り方を日付窓に変えた。**GA4は8/13以前のファイルが空**なので、ファイル数で
  `[-days:]` すると空の日を数えて窓が短くなる（--days 22 が実質18日になっていた）
- 期間を前半・後半に割って**伸びているクラスタと死んでいるクラスタ**を出す
- 広告クリックを**GA4内蔵のclick（linkUrl×pagePath）**からクラスタ別に取る。
  A8のクリック数は実需と無相関なので使わない（2026-09-04 知見）

使い方:
  python scripts/cluster_report.py [--days 28] [--no-api]
"""
import collections
import glob
import importlib.util
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AI_SOURCES = ("chatgpt.com", "copilot.com", "perplexity.ai", "gemini.google.com",
              "claude.ai", "you.com")


def load(name, path=None):
    spec = importlib.util.spec_from_file_location(
        name, path or os.path.join(BASE, "scripts", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def slug_of(url_or_path):
    """cluster_gsc.build_map のキー形式に合わせる。ツールは "tool:" 接頭辞つき。"""
    u = url_or_path.replace("https://www.noe-match.com", "").split("?")[0].split("#")[0].rstrip("/")
    slug = u.rsplit("/", 1)[-1]
    return ("tool:" + slug) if "/tools/" in u else slug


def aff_count(cluster_slugs):
    n = 0
    for s in cluster_slugs:
        name = s[5:] if s.startswith("tool:") else s
        for d in (("tools",) if s.startswith("tool:") else ("articles",)):
            f = os.path.join(BASE, d, name, "index.html")
            if os.path.exists(f):
                n += len(re.findall(r'href="https://(?:px\.a8\.net|t\.afi-b\.com)[^"]+"',
                                    io.open(f, encoding="utf-8").read()))
    return n


def files_in_window(sub, days, nonempty_key=None):
    """日付窓でアーカイブを選ぶ。空ファイル（GA4の8/13以前）は窓から除く。"""
    out = []
    for f in sorted(glob.glob(os.path.join(BASE, "agent", sub, "*.json"))):
        d = json.load(io.open(f, encoding="utf-8"))
        if nonempty_key and not d.get(nonempty_key):
            continue
        out.append((os.path.basename(f)[:10], d))
    return out[-days:]


def outbound_clicks_by_page(start, end):
    """広告クリックをページ別に取る（GA4内蔵click）。失敗したら空を返す。"""
    try:
        sys.path.insert(0, os.path.join(BASE, "scripts"))
        from fetch_ga4 import credentials, PROPERTY_ID
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            DateRange, Dimension, Filter, FilterExpression, Metric, RunReportRequest)
        c = BetaAnalyticsDataClient(credentials=credentials())
        res = c.run_report(RunReportRequest(
            property=PROPERTY_ID,
            date_ranges=[DateRange(start_date=start, end_date=end)],
            dimensions=[Dimension(name="pagePath"), Dimension(name="linkDomain")],
            metrics=[Metric(name="eventCount")],
            dimension_filter=FilterExpression(filter=Filter(
                field_name="eventName", string_filter=Filter.StringFilter(value="click"))),
            limit=300))
        out = collections.Counter()
        for r in res.rows:
            path, dom = [d.value for d in r.dimension_values]
            if dom in ("px.a8.net", "t.afi-b.com"):
                out[slug_of(path)] += int(r.metric_values[0].value)
        return out
    except Exception as e:                       # 鍵が無い環境でも表は出す
        print("  （広告クリックの取得を飛ばした: %s）" % type(e).__name__)
        return collections.Counter()


def main():
    days = 28
    if "--days" in sys.argv:
        days = int(sys.argv[sys.argv.index("--days") + 1])
    cg = load("cluster_gsc")
    cmap, _ = cg.build_map()

    gsc_files = files_in_window("gsc_archive", days, "by_page")
    ga_files = files_in_window("ga4_archive", days, "by_page")

    gsc = collections.defaultdict(lambda: [0, 0, 0.0])
    for _, d in gsc_files:
        for r in d["by_page"]:
            c = cmap.get(slug_of(r["p"]))
            if not c:
                continue
            a = gsc[c[0]]
            a[0] += r.get("clicks", 0)
            a[1] += r.get("imp", 0)
            a[2] += r.get("pos", 0) * r.get("imp", 0)

    half = len(ga_files) // 2
    ga = collections.defaultdict(lambda: [0, 0, set()])
    early = collections.Counter()
    late = collections.Counter()
    for i, (day, d) in enumerate(ga_files):
        for r in d["by_page"]:
            if r["channel"] == "Direct":
                continue
            c = cmap.get(slug_of(r["path"]))
            if not c:
                continue
            a = ga[c[0]]
            a[0] += r["sessions"]
            if r["source"] in AI_SOURCES:
                a[1] += r["sessions"]
            a[2].add(slug_of(r["path"]))
            (early if i < half else late)[c[0]] += r["sessions"]

    clicks = collections.Counter()
    if "--no-api" not in sys.argv and ga_files:
        by_page = outbound_clicks_by_page(ga_files[0][0], ga_files[-1][0])
        for slug, n in by_page.items():
            c = cmap.get(slug)
            clicks[c[0] if c else "（未割付）"] += n

    members = collections.defaultdict(set)
    for s_, c in cmap.items():
        members[c[0]].add(s_)

    keys = sorted(set(list(gsc) + list(ga)), key=lambda k: -ga.get(k, [0])[0])
    print("クラスタ別レポート")
    print(("  GSC %s〜%s（%d日） ／ GA4 %s〜%s（%d日・Direct除き）" + chr(10))
          % (gsc_files[0][0], gsc_files[-1][0], len(gsc_files),
             ga_files[0][0], ga_files[-1][0], len(ga_files)))
    print("%-9s %4s %7s %6s %7s %8s %6s %9s %7s %6s %6s" % (
        "クラスタ", "本数", "GSC表示", "clk", "平均順位", "GA4sess", "うちAI",
        "sess/本", "前→後", "広告", "clk"))
    for k in keys:
        g = gsc.get(k, [0, 0, 0.0])
        a = ga.get(k, [0, 0, set()])
        n = len(members[k])
        e, l = early[k], late[k]
        trend = ("%d→%d" % (e, l)) if (e or l) else "-"
        print("%-11s %3d %7d %6d %7.1f %8d %6d %9.2f %7s %6d %6d" % (
            k, n, g[1], g[0], (g[2] / g[1]) if g[1] else 0,
            a[0], a[1], a[0] / max(n, 1), trend, aff_count(members[k]), clicks.get(k, 0)))
    tg = [sum(x[i] for x in gsc.values()) for i in (0, 1)]
    ta = [sum(x[i] for x in ga.values()) for i in (0, 1)]
    te, tl = sum(early.values()), sum(late.values())
    print(chr(10) + "合計  GSC 表示%d / クリック%d ／ GA4 セッション%d（うちAI %d・%.0f%%）"
          % (tg[1], tg[0], ta[0], ta[1], 100 * ta[1] / max(ta[0], 1)))
    print("      前半%d日 %d → 後半%d日 %d（%+.0f%%） ／ 広告クリック %d"
          % (half, te, len(ga_files) - half, tl,
             100 * (tl - te) / max(te, 1), sum(clicks.values())))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

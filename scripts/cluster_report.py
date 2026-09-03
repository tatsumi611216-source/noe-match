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

使い方: python scripts/cluster_report.py [--days 28]
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


def main():
    days = 28
    if "--days" in sys.argv:
        days = int(sys.argv[sys.argv.index("--days") + 1])
    cg = load("cluster_gsc")
    cmap, _ = cg.build_map()

    gsc = collections.defaultdict(lambda: [0, 0, 0.0])          # click, imp, weighted pos
    for f in sorted(glob.glob(os.path.join(BASE, "agent", "gsc_archive", "*.json")))[-days:]:
        d = json.load(io.open(f, encoding="utf-8"))
        for r in d["by_page"]:
            c = cmap.get(slug_of(r["p"]))
            if not c:
                continue
            a = gsc[c[0]]
            a[0] += r.get("clicks", 0)
            a[1] += r.get("imp", 0)
            a[2] += r.get("pos", 0) * r.get("imp", 0)

    ga = collections.defaultdict(lambda: [0, 0, set()])          # sessions, ai sessions, pages
    for f in sorted(glob.glob(os.path.join(BASE, "agent", "ga4_archive", "*.json")))[-days:]:
        d = json.load(io.open(f, encoding="utf-8"))
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

    members = collections.defaultdict(set)
    for s, c in cmap.items():
        members[c[0]].add(s)

    keys = sorted(set(list(gsc) + list(ga)), key=lambda k: -gsc.get(k, [0, 0, 0])[1])
    print("クラスタ別レポート（直近%d日・GA4はDirect除き）\n" % days)
    print("%-8s %6s %7s %7s %8s %6s %7s %7s %6s" % (
        "クラスタ", "本数", "GSC表示", "GSCclk", "平均順位", "GA4session", "うちAI", "session/本", "広告"))
    for k in keys:
        g = gsc.get(k, [0, 0, 0.0])
        a = ga.get(k, [0, 0, set()])
        n = len(members[k])
        print("%-10s %5d %7d %7d %8.1f %8d %7d %9.2f %6d" % (
            k, n, g[1], g[0], (g[2] / g[1]) if g[1] else 0,
            a[0], a[1], a[0] / max(n, 1), aff_count(members[k])))
    tg = [sum(x[i] for x in gsc.values()) for i in (0, 1)]
    ta = [sum(x[i] for x in ga.values()) for i in (0, 1)]
    print("\n合計  GSC 表示%d / クリック%d ／ GA4 セッション%d（うちAI %d・%.0f%%）"
          % (tg[1], tg[0], ta[0], ta[1], 100 * ta[1] / max(ta[0], 1)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

# -*- coding: utf-8 -*-
"""クラスタ完成度の巡回（2026-08-29 新設）

なぜ必要か:
8/27公開のバンク由来ツール3本に、既存スポーク10本が2日間未結線だった（手作業で発見）。
「新ツール公開時にスポークが未接続」は構造的に再発するので、機械で見張る。

完成度 ＝ タイトルに核となる語を含む記事のうち、ツールへリンクしている割合。
基準は誰でも通園クラスタ（唯一クリックが出ている完成形）。

実行: python scripts/cluster_audit.py   （報告のみ・変更しない）
運用: 毎週金曜の巡回。未接続が出たら wire_bank_clusters.py 方式で結線する。
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLUSTERS = {
 "成婚率":       ("tools/seikonritsu-hikaku",    ["成婚率", "結婚率", "成婚"]),
 "相談所費用":   ("tools/soudanjo-hiyou-sim",    ["結婚相談所"]),
 # 「料金」単独だと病児保育・パーティー等まで拾う（8/29実測で15本が偽陽性）。
 # アプリ文脈を必須にする。
 "アプリ料金":   ("tools/app-kakin-hikaku",      ["アプリ 料金", "アプリの料金", "アプリ課金", "有料プラン", "月額料金"]),
 "病児保育":     ("tools/byoji-hoiku-ryokin",    ["病児"]),
 "不妊助成":     ("tools/funin-josei-jichitai",  ["不妊"]),
 "子ども医療費": ("tools/kodomo-iryohi-jichitai", ["医療費"]),
 "誰でも通園":   ("tools/daredemo-tsuen-jichitai", ["通園"]),
 # 「産後」単独だとガルガル/クライシス系（別クラスタの集客装置）まで拾う。
 "産後ケア":     ("tools/sangokea-ryokin",       ["産後ケア"]),
}


def main():
    pages = {}
    for p in glob.glob(os.path.join(ROOT, "articles", "*", "index.html")):
        h = io.open(p, encoding="utf-8").read()
        m = re.search(r"<title>(.*?)</title>", h, re.S)
        pages[p] = (m.group(1).strip() if m else "", h)
    bad = 0
    print("%-14s %6s %6s %8s  %s" % ("クラスタ", "候補", "接続", "完成度", "未接続の例"))
    for name, (tool, kws) in CLUSTERS.items():
        href = 'href="/%s/"' % tool
        cand = [(p, t) for p, (t, h) in pages.items() if any(k in t for k in kws)]
        linked = [p for p, t in cand if href in pages[p][1]]
        miss = [os.path.basename(os.path.dirname(p)) for p, t in cand if href not in pages[p][1]]
        pct = len(linked) / len(cand) * 100 if cand else 0
        mark = "" if pct >= 70 or not cand else " ←"
        if mark:
            bad += 1
        print("%-14s %6d %6d %7.0f%%%s %s" % (name, len(cand), len(linked), pct, mark,
              ",".join(miss[:4]) + ("…" if len(miss) > 4 else "")))
    print("\n70%%未満のクラスタ: %d" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

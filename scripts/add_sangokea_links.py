# -*- coding: utf-8 -*-
"""産後ケア料金ナビ（新設ツール）への内部リンクを、実際に人が来ているページに置く。

なぜここに置くか: 8/27のGA4実測で、実流入の最大の入口は /tools/garugaru-check/
（14日で40セッション・滞在48秒）で、次いで産後クラスタの記事群だった。
新設ツールは公開直後で被リンクも順位も無いので、既に人が着地している
産後クラスタから送る。

アンカーは検索語入りにする（8/24の知見: ブランド語アンカーは順位に効かない）。
冪等: 既に sangokea-ryokin へのリンクがあるページは触らない。
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HREF = "/tools/sangokea-ryokin/"

BLOCK = """
<!-- SANGOKEA-LINK -->
<div style="border-left:3px solid #7c2e42;background:#faf8f5;padding:16px 18px;margin:28px 0;">
<p style="margin:0 0 6px;font-size:.78rem;letter-spacing:.1em;color:#7c2e42;">関連ツール</p>
<p style="margin:0;font-size:.92rem;line-height:1.9;color:#3a4148;">
産後ケア事業は自治体ごとに自己負担が違い、宿泊型を1泊使ったときの負担は0円の自治体と1万円を超える自治体があります。
<a href="%s" style="color:#7c2e42;font-weight:700;">産後ケアの料金を自治体別に調べる（東京23区＋政令市の実額と回数上限）</a>で、
使いたい回数を入れると自己負担の合計が出ます。
</p>
</div>
""" % HREF

TARGETS = [
    "tools/garugaru-check/index.html",
    "tools/sango-recovery-check/index.html",
    "tools/daredemo-tsuen-jichitai/index.html",
    "articles/daredemo-tsuen-ryokin/index.html",
    "articles/garugaru-ki-guide/index.html",
    "articles/garugaru-otto-taiou/index.html",
    "articles/garugaru-sangoutsu-chigai/index.html",
    "articles/garugaru-gibo-jitsubo/index.html",
    "articles/garugaru-ki-itsumade/index.html",
    "articles/sango-crisis-guide/index.html",
    "articles/sango-satogaeri/index.html",
    "articles/sango-iraira/index.html",
    "articles/sango-kaji-buntan/index.html",
    "articles/futarime-sango/index.html",
]


def main():
    added = skipped = 0
    for rel in TARGETS:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print("NOT FOUND:", rel)
            continue
        h = io.open(p, encoding="utf-8").read()
        if HREF in h:
            print("skip(設置済み):", rel)
            skipped += 1
            continue
        # LINE-CTAの直前（本文の末尾）に置く。無ければ footer の直前
        i = h.find("<!-- LINE-CTA -->")
        if i < 0:
            i = h.find("<footer>")
        if i < 0:
            print("挿入位置なし:", rel)
            continue
        io.open(p, "w", encoding="utf-8").write(h[:i] + BLOCK + h[i:])
        print("added:", rel)
        added += 1
    print("設置 %d本 / スキップ %d本" % (added, skipped))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

# -*- coding: utf-8 -*-
"""育休延長の条件判定ツールへの内部リンクを、話題が地続きのページに置く。

保活（保育園に入れるか）と育休延長は同じ判断の裏表なので、保活系・制度系の
ページから送る。アンカーは検索語入りにする（8/24の知見）。
冪等: 既にリンクがあるページは触らない。
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HREF = "/tools/ikukyu-encho-hantei/"

BLOCK = """
<!-- IKUKYU-LINK -->
<div style="border-left:3px solid #7c2e42;background:#faf8f5;padding:16px 18px;margin:28px 0;">
<p style="margin:0 0 6px;font-size:.78rem;letter-spacing:.1em;color:#7c2e42;">関連ツール</p>
<p style="margin:0;font-size:.92rem;line-height:1.9;color:#3a4148;">
保育所に入れなかったときの育休の延長は、2025年4月から給付金側の要件が厳しくなりました。
<a href="%s" style="color:#7c2e42;font-weight:700;">育休はいつまで延長できるか条件を判定する（必要書類と期限つき）</a>で、
子の生年月日と状況を入れると、休業の延長と給付金の延長を分けて判定できます。
</p>
</div>
""" % HREF

TARGETS = [
    "tools/hoikuen-tensu-nerima/index.html",
    "tools/daredemo-tsuen-jichitai/index.html",
    "tools/sango-recovery-check/index.html",
    "articles/daredemo-tsuen-ryokin/index.html",
    "articles/sango-crisis-guide/index.html",
    "articles/sango-kaji-buntan/index.html",
    "articles/tenshoku-riyu-honne/index.html",
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

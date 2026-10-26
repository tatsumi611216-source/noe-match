# -*- coding: utf-8 -*-
"""育児休業給付金のデータ記事への内部リンクを、話題が地続きのページに置く。

送り先は /articles/ikukyu-kyufukin-data/。順位ゼロの新規ページを単独で置いても
入口にならないので、既に人が着地しているクラスタ（産後・保活・出産費用）から引く。
アンカーは検索語入りにする（8/24の知見。ブランド語先頭は効かない）。

冪等: 既にリンクがあるページは触らない。
既存リンクの文言を書き換えることはしない（ブロック要素を含むリンクを壊した8/27の教訓）。
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HREF = "/articles/ikukyu-kyufukin-data/"

BLOCK = """
<!-- IKUKYU-KYUFU-LINK -->
<div style="border-left:3px solid #7c2e42;background:#faf8f5;padding:16px 18px;margin:28px 0;">
<p style="margin:0 0 6px;font-size:.78rem;letter-spacing:.1em;color:#7c2e42;">関連記事</p>
<p style="margin:0;font-size:.92rem;line-height:1.9;color:#3a4148;">
育休中の収入は「賃金の67％」と紹介されがちですが、67％なのは休業開始から通算180日までです。
<a href="%s" style="color:#7c2e42;font-weight:700;">育児休業給付金はいくらもらえる？181日目からは50％、上限は332,454円</a>で、
賃金月額別の支給額と令和8年8月改定の上限額を条文の出典つきで整理しています。
</p>
</div>
""" % HREF

TARGETS = [
    "tools/ikukyu-encho-hantei/index.html",
    "tools/hoikuen-tensu-nerima/index.html",
    "tools/daredemo-tsuen-jichitai/index.html",
    "tools/sangokea-ryokin/index.html",
    "articles/shussan-hiyou-data/index.html",
    "articles/shussan-ichijikin-data/index.html",
    "articles/sangokea-josei/index.html",
    "articles/sangokea-nankai/index.html",
    "articles/daredemo-tsuen-ryokin/index.html",
    "articles/sango-crisis-guide/index.html",
    "articles/sango-kaji-buntan/index.html",
    "articles/futarime-sango/index.html",
]

ANCHORS = ["<!-- LINE-CTA -->", "</article>"]


def main():
    added = skipped = missing = 0
    for rel in TARGETS:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print("NOT FOUND:", rel)
            missing += 1
            continue
        html = io.open(p, encoding="utf-8").read()
        if HREF in html:
            print("skip (already linked):", rel)
            skipped += 1
            continue
        for a in ANCHORS:
            if a in html:
                html = html.replace(a, BLOCK + "\n" + a, 1)
                break
        else:
            print("NO ANCHOR:", rel)
            missing += 1
            continue
        io.open(p, "w", encoding="utf-8").write(html)
        print("added:", rel)
        added += 1
    print("追加 %d ／ 既存 %d ／ 未処理 %d" % (added, skipped, missing))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

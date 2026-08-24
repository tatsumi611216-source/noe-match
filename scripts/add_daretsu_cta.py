# -*- coding: utf-8 -*-
"""産後・育休クラスタから「こども誰でも通園制度 自治体別ナビ」への導線を設置する。

方針は add_tool_cta.py と同じ：
- 記事ごとに文面を変える（同じ定型文を貼るとバナーに見える）
- 置く位置は記事末尾の関連リンク直前
- アンカーは検索語を含む文言にする（2026-08-24の実測で、ツール名だけのアンカーは
  クエリ信号を渡していないことが分かったため）
冪等：既にリンクがある記事は触らない。
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = "/tools/daredemo-tsuen-jichitai/"

CTA = {
    "ikukyu-fuufu-doji": (
        "育休中でも、保育所に入っていない子を時間単位で預けられる",
        "2026年度から本格実施のこども誰でも通園制度は、就労要件を問いません。ただし使える時間は自治体で10時間から64時間まで開きます。",
        "こども誰でも通園制度は月何時間使えるか（自治体別）→"),
    "sango-kaji-buntan": (
        "分担の前に、預けられる時間を確保できないか",
        "家事の割り振りだけで足りないときは、預け先を1つ増やすほうが早いことがあります。自治体ごとの上限時間と利用料を早見表にしました。",
        "自治体別の上限時間・利用料を見る →"),
    "satogaeri-shinai": (
        "里帰りしない場合、日中の預け先が効きます",
        "実家に頼らない前提だと、平日の数時間を外に出せるかで負担が変わります。制度の上限は自治体で6倍以上違います。",
        "こども誰でも通園制度は月何時間使えるか（自治体別）→"),
    "sango-crisis-guide": (
        "ひとりの時間を作る手段として、制度を使う",
        "産後の負荷は、休める時間を作れるかで変わります。保育所に入っていない子を時間単位で預けられる制度の、自治体別の条件をまとめました。",
        "自治体別の上限時間・利用料を見る →"),
    "futarime-sango": (
        "上の子を預けられるかで、二人目の産後は変わる",
        "上の子が未就園なら、こども誰でも通園制度の対象になる場合があります。使える時間と料金は自治体で違います。",
        "こども誰でも通園制度は月何時間使えるか（自治体別）→"),
}

BLOCK = ('<div style="background:#f7f5f2;border:1px solid #e6e2dc;padding:20px 22px;'
         'margin:26px 0">'
         '<p style="font-weight:700;margin:0 0 8px">%s</p>'
         '<p style="font-size:.9rem;color:#5a6068;margin:0 0 14px">%s</p>'
         '<a href="' + TOOL + '" style="display:inline-block;background:#7c2e42;'
         'color:#fff;font-weight:700;padding:12px 28px;text-decoration:none">%s</a>'
         '<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">'
         '無料・登録不要。出典は各自治体公式（2026年8月25日確認）。</p>'
         '</div>')


def main():
    for slug, (head, body, anchor) in CTA.items():
        p = os.path.join(ROOT, "articles", slug, "index.html")
        if not os.path.exists(p):
            print("NOT FOUND:", slug)
            continue
        h = io.open(p, encoding="utf-8").read()
        if TOOL in h:
            print("SKIP (already linked):", slug)
            continue
        m = re.search(r'<div class="related">', h)
        if not m:
            print("NO related block:", slug)
            continue
        i = m.start()
        io.open(p, "w", encoding="utf-8").write(h[:i] + (BLOCK % (head, body, anchor)) + h[i:])
        print("added:", slug)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

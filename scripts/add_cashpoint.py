# -*- coding: utf-8 -*-
"""クラスタAの新記事2本に、文脈の合うキャッシュポイントを設置する。

なぜ位置を指定するか（2026-08-15）:

クラスタAは「集客が主・キャッシュが従」（agent/cluster_map.md）。
記事末尾にまとめて広告を積むと主従が逆転して見えるため、
**本文中で、その話題が自然に出てくる箇所の直後にだけ置く**。

- 義母・実母の記事 → 「訪問の設計」の直後（来客対応の食事負担は実在の論点）
- 「ない人」の記事  → 「環境が変わるタイミング」の直後（ライフイベント＝見直し事由）

冪等：既に a8mat がある記事は触らない。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OISIX = "https://px.a8.net/svt/ejp?a8mat=4B8B4Q+5CWKMY+3RK+2TBJQA"
HOKEN = "https://px.a8.net/svt/ejp?a8mat=4B8B4Q+42GRGA+3S2C+614CX"

YMYL_NOTE = ('<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">'
             '当サイトは相談窓口を選択肢として紹介しており、特定の保険商品を推奨するものでは'
             'ありません。契約の判断はご自身で行ってください。</p>')


def block(head, body, url, label, note):
    return ('<div style="background:#f7f5f2;border:1px solid #e6e2dc;padding:20px 22px;'
            'margin:22px 0;text-align:center">'
            '<p style="font-size:.7rem;color:#999;margin:0 0 6px;text-align:left">PR</p>'
            '<p style="font-weight:700;margin:0 0 8px">%s</p>'
            '<p style="font-size:.8rem;color:#5a6068;margin:0 0 14px">%s</p>'
            '<a href="%s" rel="nofollow sponsored noopener" target="_blank" '
            'style="display:inline-block;background:#7c2e42;color:#fff;font-weight:700;'
            'padding:13px 32px;text-decoration:none">%s</a>%s</div>'
            % (head, body, url, label, note))


PLAN = {
    "articles/garugaru-gibo-jitsubo": [
        ('<h2 id="ato">',
         block("来客対応の食事づくりは、減らせる負担のひとつ",
               "訪問の設計で回数と時間を決めても、そのたびの食事準備は残ります。"
               "作る前提を外すだけで、当日の消耗はかなり変わります。",
               OISIX, "Oisixのおためしセットを見る",
               '<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">'
               '食材宅配のおためしセット（内容・価格は時期により変わります。公式サイトでご確認ください）</p>')),
    ],
    "articles/garugaru-otto-taiou": [
        ('<h2 id="jibun">',
         block("担当を持つ前に、家事の総量そのものを減らす",
               "分担を議論するより、やること自体を減らすほうが早い局面があります。"
               "食事まわりは最初に外せる負担です。",
               OISIX, "Oisixのおためしセットを見る",
               '<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">'
               '食材宅配のおためしセット（内容・価格は時期により変わります。公式サイトでご確認ください）</p>')),
    ],
    "articles/garugaru-otto-genkai": [
        ('<h2 id="soudan">',
         block("家計と保障の現在地を知っておく",
               "選択肢を考える段階では、お金の見通しがあるほど落ち着いて判断できます。"
               "固定費と保障の棚卸しから。",
               HOKEN, "保険ランドリーの無料相談を見る", YMYL_NOTE)),
    ],
    "articles/sango-otto-kirai": [
        ('<h2 id="otto">',
         block("「記憶の収支」を戻す前に、負荷を下げる",
               "言葉より先に、しんどさの総量が減っているかどうかが効きます。"
               "食事づくりは最初に外せる負担です。",
               OISIX, "Oisixのおためしセットを見る",
               '<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">'
               '食材宅配のおためしセット（内容・価格は時期により変わります。公式サイトでご確認ください）</p>')),
    ],
    "articles/gijikka-ikitakunai": [
        ('<h2 id="iku">',
         block("来客・訪問のたびの食事準備は、外せる負担",
               "会う回数を減らせない相手もいます。作る前提を外しておくと、"
               "当日にやることが1つ減ります。",
               OISIX, "Oisixのおためしセットを見る",
               '<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">'
               '食材宅配のおためしセット（内容・価格は時期により変わります。公式サイトでご確認ください）</p>')),
    ],
    "articles/garugaru-doukyo": [
        ('<h2 id="genkai">',
         block("住まいを分ける選択肢も、費用から現在地を知っておく",
               "同居を続けるか環境を変えるかは、家計の見通しがあると判断しやすくなります。"
               "固定費と保障の棚卸しから。",
               HOKEN, "保険ランドリーの無料相談を見る", YMYL_NOTE)),
    ],
    "articles/shinseiji-menkai": [
        ('<h2 id="uke">',
         block("もてなさないための備えを、先に用意しておく",
               "来客のたびの買い出しと調理は省略してかまいません。"
               "手元に用意があるだけで、当日の負担が変わります。",
               OISIX, "Oisixのおためしセットを見る",
               '<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">'
               '食材宅配のおためしセット（内容・価格は時期により変わります。公式サイトでご確認ください）</p>')),
    ],
    "articles/sango-satogaeri": [
        ('<h2 id="otto">',
         block("戻る前に、食事の負担を先に外しておく",
               "里帰り明けは支援がゼロに戻る局面です。作る前提を外しておくと、"
               "段差の当日にやることが1つ減ります。",
               OISIX, "Oisixのおためしセットを見る",
               '<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">'
               '食材宅配のおためしセット（内容・価格は時期により変わります。公式サイトでご確認ください）</p>')),
    ],
    "articles/garugaru-nai-hito": [
        ('<h2 id="otto">',
         block("環境が変わる前が、家計と保険を見直す「動きどき」",
               "里帰り明け・復職・二人目——条件が変わる手前は、"
               "固定費と保障の現在地を確認しておきやすいタイミングです。無料相談で棚卸しから。",
               HOKEN, "保険ランドリーの無料相談を見る", YMYL_NOTE)),
    ],
}


def main():
    for page, items in PLAN.items():
        p = os.path.join(ROOT, page, "index.html")
        h = open(p, encoding="utf-8").read()
        if "a8mat=" in h:
            print("SKIP (already has ads):", page)
            continue
        for anchor, blk in items:
            i = h.find(anchor)
            if i < 0:
                print("ANCHOR NOT FOUND:", page, anchor)
                continue
            h = h[:i] + blk + h[i:]
        open(p, "w", encoding="utf-8").write(h)
        print("added cashpoint:", page)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

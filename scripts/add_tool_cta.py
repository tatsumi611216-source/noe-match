# -*- coding: utf-8 -*-
"""生活費クラスタ14本に、生活費シミュレーターへの導線を設置する。

なぜ必要か（2026-08-16の実測）:
ツールを公開した時点で、クラスタ14本からの導線は**0/14**だった。
核となるツールに人が流れないと、クラスタとして閉じない（tool-clusterの③）。

設置方針:
- **記事ごとに文面を変える。** 同じ定型文を14本に貼ると、
  内部リンクではなく「広告バナー」に見えてしまう
- 置く位置は記事末尾の関連リンク直前（本文の流れを切らない）
- 文中の自然な位置に置くのが理想だが、既存記事の本文構造は個別に違うため、
  今回は末尾に統一する（本文中への挿入は加筆時にあわせて行う）

冪等：既にツールへのリンクがある記事は触らない。
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOL = "/tools/seikatsuhi-simulator/"

# slug -> (見出し, 本文)  記事の主題に接続する言い方にする
CTA = {
    "dousei-hajimekata": (
        "初期費用のあとに来る「毎月いくらか」も出しておく",
        "同棲は始めるときの費用に目が行きますが、続くのは毎月のほうです。家賃と手取りを入れると、月額の内訳と「どちらがいくら出すか」まで出ます。"),
    "shinkon-seikatsu-guide": (
        "準備費用と、毎月の生活費は別ものです",
        "このページで扱ったのは新生活を始めるまでの費用です。始まったあとの毎月については、月額と分担を試算できます。"),
    "shinkon-koteihi-minaoshi": (
        "固定費を削る前に、全体のどこが重いかを見る",
        "見直しは効果の大きいところから。まず月額の内訳を出すと、通信・保険・住まいのどれに手を付けるべきかが数字で見えます。"),
    "shinkon-net-kaisen-dandori": (
        "回線費用は、生活費全体のどのくらいを占めるか",
        "通信費だけを見ても判断しづらいものです。月額の内訳の中で位置づけると、削る優先順位が決めやすくなります。"),
    "futari-hikari-kaisen": (
        "回線を含めた月額を、一度まとめて出してみる",
        "光回線・スマホ・光熱をまとめた月額と、二人でどう分けるかを試算できます。"),
    "futari-sumaho-minaoshi": (
        "スマホ代を含む固定費の全体像を出す",
        "通信費の見直し効果は、全体の中で見ると判断しやすくなります。月額の内訳と分担を試算できます。"),
    "kazoku-simhikaku": (
        "通信費を含めた生活費の月額を試算する",
        "格安SIMへの切り替えで浮く額が、家計全体でどのくらいの意味を持つか。まず総額を出してみてください。"),
    "kekkon-hoken-minaoshi": (
        "保険料を、生活費全体の中に置いて考える",
        "保険は単体では高い安いが判断しづらい費目です。月額の内訳に入れて、家計に占める割合で見ると決めやすくなります。"),
    "futari-kouza-kanri": (
        "共通口座にいくら入れるかは、総額から逆算する",
        "口座の形を決める前に、毎月いくらかかるかを出しておくと決めやすくなります。折半・収入比・定額＋按分の3案で分担額も出ます。"),
    "kekkon-chokin-mokuhyou": (
        "貯められる額は、生活費を引いた残りで決まる",
        "目標額から逆算する前に、毎月の支出を出しておくと現実的な計画になります。手取りに対する支出の割合も表示します。"),
    "shinkyo-kagu-yosan": (
        "家具の予算は、毎月の生活費と合わせて考える",
        "初期費用に使いすぎると、その後の毎月が苦しくなります。月額を先に把握しておくと配分を決めやすくなります。"),
    "kaden-rental-vs-kounyu": (
        "レンタル料は毎月の固定費になります",
        "レンタルを選ぶ場合、月額が生活費に上乗せされます。全体の中でどのくらいの負担かを試算できます。"),
    "tomobataraki-shokuji-data": (
        "食費は、生活費全体のどのくらいを占めるか",
        "食事スタイルを変えたときの差額が、家計全体でどう効くか。月額の内訳で確認できます。"),
    "kekkon-hiyou-futan": (
        "結婚後の毎月も、同じ考え方で分けられる",
        "この記事で扱った「同じ額か、同じ痛みか」は、生活費の分担でもそのまま使えます。月額と3案の分担額を試算できます。"),
}

BLOCK = ('<div style="background:#f7f5f2;border:1px solid #e6e2dc;padding:20px 22px;'
         'margin:26px 0">'
         '<p style="font-weight:700;margin:0 0 8px">%s</p>'
         '<p style="font-size:.9rem;color:#5a6068;margin:0 0 14px">%s</p>'
         '<a href="' + TOOL + '" style="display:inline-block;background:#7c2e42;'
         'color:#fff;font-weight:700;padding:12px 28px;text-decoration:none">'
         'ふたりの生活費シミュレーターへ →</a>'
         '<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">'
         '無料・登録不要。折半／収入比／定額＋按分の3案で分担額まで出ます。</p>'
         '</div>')


def main():
    for slug, (head, body) in CTA.items():
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
        io.open(p, "w", encoding="utf-8").write(h[:i] + (BLOCK % (head, body)) + h[i:])
        print("added:", slug)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

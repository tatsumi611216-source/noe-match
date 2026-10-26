# -*- coding: utf-8 -*-
"""実流入のある着地ページのうち、LINE導線が無い8本に導線を入れる（2026-09-17 新設）

なぜ必要か:
GA4日別アーカイブ（2026-08-27〜09-14・direct/(not set)除き）で3セッション以上の着地ページを
lin.ee の有無と突き合わせたら、8本に導線が無かった。うち平均初婚年齢のデータ記事は
9セッション（bing 8）で、同じ期間のデータ記事の中でも上位なのに、データ記事で唯一の空白側にいた。
8/26（add_line_cta_clicked.py）・8/29（add_line_cta_ai_landing.py）と同じ型の穴埋め。

形式・挿入位置・配信頻度の表記（月1回）は add_line_cta_ai_landing.py に揃える。
GA4イベントは line_add_click の article パラメータで設置元を区別する。

冪等: すでに lin.ee があるページは触らない。
実行: python scripts/add_line_cta_landing_0917.py
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BLOCK = """
<!-- LINE-CTA -->
<section id="line-cta" style="max-width:680px;margin:48px auto 8px;padding:34px 26px;background:#f7f5f2;border:1px solid #e3ddd3;text-align:center;">
  <p style="margin:0 0 10px;font-size:12px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,serif;">NOE OFFICIAL LINE</p>
  <p style="margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5;">%(head)s</p>
  <p style="margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;">%(body)s</p>
  <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{gtag('event','line_add_click',{article:'%(slug)s'});}catch(e){}"
     style="display:inline-block;background:#7c2e42;color:#ffffff;padding:14px 36px;font-size:15px;font-weight:600;text-decoration:none;">友だち追加して受け取る</a>
  <p style="margin:14px 0 0;font-size:11px;color:#8a8f95;">登録は無料・配信は月１回だけです。いつでも解除できます。</p>
</section>
"""

TARGETS = {
 "hatsushon-nenmei-data": ("初婚年齢の公表値が更新されたら、お知らせします",
  "人口動態統計の確定数・概数は毎年書き換わります。<br>変わった点だけを月１回お送りしています。"),
 "nyuseki-2027-guide": ("入籍日の候補を、決める前にもう一度",
  "2027年の吉日と、入籍の手続きの段取りをまとめています。<br>月１回お送りしています。"),
 "pair-ring-guide": ("指輪の相場データは、更新されたときに",
  "調査ごとに数字の取り方が違うので、出典つきで追っています。<br>変わった点だけを月１回お送りしています。"),
 "dousei-hajimekata": ("同棲から結婚までの段取りを、月１回",
  "初期費用・手続き・話し合っておくことを短くまとめています。<br>迷ったら、追加後そのままトークでどうぞ。"),
 "pairs-marriage-data": ("公表値の注記が変わったら、お知らせします",
  "各社の公表値は静かに書き換わります。<br>変わった点だけを月１回お送りしています。"),
 "compare-popular": ("アプリの料金と公表値は、年度で変わります",
  "Pairs・with・Omiaiの改定を追っています。<br>変わった点だけを月１回お送りしています。"),
 "propose-guide": ("プロポーズから入籍までの段取りを、月１回",
  "手続きの順番と、先に決めておくことを短くまとめています。<br>迷ったら、追加後そのままトークでどうぞ。"),
 "usuge-konkatsu-eikyou": ("婚活の判断材料を、数字で",
  "見た目の悩みを含めて、公表データで考える材料をまとめています。<br>月１回お送りしています。"),
}


def main():
    done, skip = [], []
    for slug, (head, body) in sorted(TARGETS.items()):
        p = os.path.join(ROOT, "articles", slug, "index.html")
        if not os.path.exists(p):
            skip.append((slug, "ファイルなし")); continue
        h = io.open(p, encoding="utf-8").read()
        if "lin.ee" in h:
            skip.append((slug, "既にLINEあり")); continue
        if h.count("<footer") != 1:
            skip.append((slug, "footerが1つではない")); continue
        blk = BLOCK % {"head": head, "body": body, "slug": slug}
        h2 = h.replace("<footer", blk + "<footer", 1)
        if h2 == h:
            skip.append((slug, "挿入失敗")); continue
        io.open(p, "w", encoding="utf-8").write(h2)
        done.append(slug)
    print("挿入: %d件" % len(done))
    for s in done:
        print("  +", s)
    if skip:
        print("スキップ: %d件" % len(skip))
        for s, r in skip:
            print("  -", s, r)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

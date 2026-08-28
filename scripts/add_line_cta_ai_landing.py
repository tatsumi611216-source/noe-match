# -*- coding: utf-8 -*-
"""AI（ChatGPT/Copilot）経由の着地ページにLINE導線を入れる（2026-08-29 新設）

なぜ必要か:
GA4実測（直近30日）で AI経由42セッション > Google 41セッション。
しかもAI経由は滞在が長い（Copilot 128秒/1.80PV・ChatGPT 95秒 vs Google 60秒/1.07PV）。
ところが着地ページ18本のうち10本にLINE導線が無く、AI経由42セッションのうち
14セッション（33%）が行き先の無いまま終わっていた。

配信頻度の表記は「月1回」に統一する。サイト内は月1回26ページ・週1回17ページで
割れており、note記事側も月1回で書いている。実配信はまだ始まっていないため、
少ない側に合わせて過大な約束をしない。

冪等: すでに lin.ee があるページは触らない。
実行: python scripts/add_line_cta_ai_landing.py
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
 "over50-guide": ("50代からの婚活を、数字を見ながら",
  "各社の料金と公表値は年度で書き換わります。<br>変わった点だけを月１回お送りしています。"),
 "age-data": ("年齢層のデータは、更新されたときに",
  "各社の公表値は静かに書き換わります。<br>変わった点だけを月１回お送りしています。"),
 "kaiin-age-cross-data": ("会員数の数字は、作り方が社ごとに違います",
  "どの数字がどう数えられているかを追っています。<br>変わった点だけを月１回お送りします。"),
 "omiai-30s-women-data": ("公表値の注記が変わったら、お知らせします",
  "見出しではなく注記の方を見ています。<br>変わった点だけを月１回お送りしています。"),
 "matching-josei-cost-data": ("「女性無料」の中身は、社ごとに違います",
  "無料の範囲と有料オプションを追っています。<br>料金改定があった点だけを月１回お送りします。"),
 "bridal-inner-guide": ("結婚準備の段取りを、月１回だけ",
  "式までに決めることは多く、順番を間違えると高くつきます。<br>決める順番と期限を短文でお送りします。"),
 "tapple-vs-pairs": ("料金は改定されます。変わった点だけを",
  "Web購入とアプリ内購入の差額は年で数千円動きます。<br>改定があったときだけ月１回お送りします。"),
 "osaka-guide": ("エリアで変わる部分を、月１回",
  "候補数も料金も、地域と時期で変わります。<br>変わった点だけを短文でお送りしています。"),
 "photo-tips": ("写真を直したあと、次にどこを見るか",
  "プロフィールの先には料金と無料範囲の問題があります。<br>変わった点だけを月１回お送りしています。"),
 "konkatsu-party-guide": ("1回の金額ではなく、総額で見るために",
  "パーティー・アプリ・相談所の料金は年度で変わります。<br>変わった点だけを月１回お送りします。"),
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
        if "<footer" not in h:
            skip.append((slug, "footerなし")); continue
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

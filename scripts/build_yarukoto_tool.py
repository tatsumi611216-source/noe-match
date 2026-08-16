# -*- coding: utf-8 -*-
"""入籍日カレンダーを生成する。

語の根拠（2026-08-16 サジェスト実測）:
  離婚後 生活費 = 10件（トップサジェストが「シュミレーション」）
  養育費 計算 = 10件（**ツール／機／表／式** が直接出る）
  財産分与 計算 = 10件（ツール／エクセル／表）
  シングルマザー 手当 = 10件 ／ 離婚 貯金 いくら = 10件
  婚姻費用 計算 = 3件（ツール／シュミレーター）
  ★ 今日測った全クラスタで唯一、「ツール」「計算機」がサジェストに直接出た領域

競合実査（2026-08-16）:
  弁護士事務所・法律メディアが「離婚した方がいい夫婦チェックリスト」を大量に出しているが、
  **いずれも読むだけの箇条書きで、インタラクティブなツールではない**（ベンナビ離婚を実確認）。
  CTAは全て「弁護士を探す」＝**離婚しない方向の選択肢を出す動機が構造的にない**。
  計算ツールを作らないのは、自己解決させると相談に来ないため。ここが空いている。

**判定はしない。** 「離婚すべきか」を出力するのは Noe Decision（FACT→選択肢→判断軸→本人が決める）
に反するうえ、入力欄に収まらない情報のほうが決定的なため、機械の結論は判断を歪める。

数値の根拠:
  養育費・婚姻費用 … 裁判所「標準算定方式・算定表（令和元年版）」の考え方にもとづく概算
    https://www.courts.go.jp/toukei_siryou/siryo/H30shihou_houkoku/index.html
    子の指数 0〜14歳=62／15歳以上=85、基礎収入割合は総収入帯で変動
  生活費 … 総務省「家計調査」の水準
  手当 … 児童手当・児童扶養手当（所得制限あり・年度改定あり）
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "kekkon-shikin-keisanki", "index.html")
OUT_DIR = os.path.join(ROOT, "tools", "kekkon-yarukoto")
SITE = "https://www.noe-match.com"
URL = SITE + "/tools/kekkon-yarukoto/"

TITLE = "結婚のやることリスト｜順番つきチェックリストを条件別に無料作成【2026年版】"
DESC = ("結婚に向けてやることを、いまの状況・式の有無・同居の時期・子どもの予定から絞り込み、"
        "時系列の順番つきで表示する無料チェックリスト。順番を間違えると手戻りが出る項目も明示。"
        "チェックは保存され、URLで相手と共有できます。登録不要。")

FAQ = [
    ("結婚に向けてやることは何から始めればよいですか？",
     "お金の価値観のすり合わせと、かかる総額の把握からです。貯蓄・支出・借入の有無を先に共有しておくと、"
     "式をどうするか、いつ入籍するか、どこに住むかといった後の判断がすべて早くなります。"
     "逆にここが曖昧なまま式場を見に行くと、予算が決まらず決められません。"),
    ("結婚準備の順番で、間違えやすいものはありますか？",
     "4つあります。ネット回線は入居の1〜2か月前に申し込まないと使えない期間ができること、"
     "姓の変更は運転免許を最初に直さないと他の窓口で本人確認書類として使えないこと、"
     "保険は住まいが決まってから見直さないと必要保障額が変わって入り直しになること、"
     "式場は日取りを決めてから探さないと日程から選び直しになることです。"),
    ("結婚式をしない場合、やることはどのくらい減りますか？",
     "式場探し・招待客の選定・衣装・支払い方法の確認などがなくなるため、項目としては大きく減ります。"
     "ただし式をしない場合にこそ必要になることもあります。両家への報告の形、写真を残すかどうか、"
     "報告はがきをどうするかで、後から気になることがあるためです。本ツールは条件に応じてこれらを切り替えます。"),
    ("入籍後の手続きは何から進めればよいですか？",
     "姓を変更する側は、運転免許証を最初に変更してください。他の窓口で本人確認書類として使うためです。"
     "そのあとマイナンバーカード、銀行口座とクレジットカード、勤務先への届出と進みます。"
     "勤務先への届出は健康保険や手当に関わるため、遅れると精算が発生することがあります。"),
    ("チェックした内容は保存されますか？",
     "はい。チェックの状態はご利用の端末に保存されるため、次に開いたときは続きから使えます。"
     "また表示されるURLを相手に送ると、チェック済みの状態がそのまま開きます。"
     "同じリストを二人で見ながら、どちらが何を持つかを決められます。"),
    ("項目に「二人で」「どちらか」と書いてあるのは何ですか？",
     "その作業に二人そろって動く必要があるか、片方だけで足りるかの目安です。"
     "全部を一緒にやろうとすると日程が合わずに止まりますが、実際には片方だけで済む手続きが多くあります。"
     "先に分担を決めておくと、抜けが減ります。"),
    ("同棲してから結婚する場合、何が変わりますか？",
     "住まい関係の項目が減ります。物件探し・引っ越し・家具家電・転入届などはすでに済んでいるためです。"
     "一方でお金の管理方法や保険の見直しは、入籍のタイミングで改めて必要になります。"
     "本ツールで「すでに同居している」を選ぶと、不要な項目が消えます。"),
    ("このリストは何を根拠に作られていますか？",
     "当サイトが各テーマで公開している記事とツールの内容を、時系列に並べ直したものです。"
     "各項目からは該当する解説ページに移動できます。ただし届出の要件・必要書類・受付時間は自治体により異なり、"
     "各種サービスの手続き方法も変更されることがあるため、実際の手続きは公式情報でご確認ください。"),
]


def shell():
    h = open(SRC, encoding="utf-8").read()
    gtag = h[:h.find("<meta charset")]
    style = h[h.find('<link href="https://fonts.googleapis.com'):
              h.find('<script type="application/ld+json">')]
    header = h[h.find("<body>"):h.find('<div class="breadcrumb"')]
    footer = h[h.rfind("<footer"):]
    return gtag, style, header, footer


def main():
    gtag, style, header, footer = shell()
    ld = [
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q,
                         "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        {"@context": "https://schema.org", "@type": "WebApplication",
         "name": "結婚のやることリスト", "url": URL,
         "applicationCategory": "LifestyleApplication", "operatingSystem": "All",
         "inLanguage": "ja", "description": DESC,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": SITE + "/"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
             {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": SITE + "/#tools"},
             {"@type": "ListItem", "position": 3, "name": "結婚のやることリスト"}]},
    ]
    lds = ""
    for d in ld:
        s = json.dumps(d, ensure_ascii=False)
        json.loads(s)
        lds += '<script type="application/ld+json">%s</script>\n' % s

    faq_html = "".join("<h3>Q%d. %s</h3>\n<p>%s</p>\n" % (i + 1, q, a)
                       for i, (q, a) in enumerate(FAQ))
    body = open(os.path.join(os.path.dirname(__file__), "_yarukoto_body.html"),
                encoding="utf-8").read()

    related = """
<div class="related"><h2>関連記事・ツール</h2><ul>
<li><a href="/articles/propose-guide/">結婚の段取り完全ガイド｜プロポーズから入籍・入籍後の手続きまで整理</a></li>
<li><a href="/articles/shinkon-seikatsu-guide/">新婚生活の準備ガイド｜引越し・家具・お金の段取りチェックリスト</a></li>
<li><a href="/tools/kekkon-shikin-keisanki/">結婚資金計算機｜総額とご祝儀差引後の自己負担を試算</a></li>
<li><a href="/tools/seikatsuhi-simulator/">ふたりの生活費シミュレーター｜月額と分担3案</a></li>
<li><a href="/tools/nyuseki-calendar/">入籍日カレンダー｜大安・天赦日から候補日を絞る</a></li>
</ul></div>
"""
    html = """%(gtag)s<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(url)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="website">
<meta property="og:url" content="%(url)s">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
%(style)s
%(ld)s</head>
%(header)s
<div class="breadcrumb"><div class="wrap"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ 結婚のやることリスト</div></div>
<main class="wrap">
%(body)s
<article>
<h2>よくある質問</h2>
%(faq)s
</article>
%(related)s
</main>
%(footer)s
""" % dict(gtag=gtag, title=TITLE, desc=DESC, url=URL, style=style, ld=lds,
           header=header, body=body, faq=faq_html, related=related, footer=footer)

    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, "index.html")
    open(p, "w", encoding="utf-8").write(html)

    import re
    h = open(p, encoding="utf-8").read()
    types = [json.loads(b).get("@type")
             for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S)]
    assert len(types) == len(set(types)), "JSON-LDの@type重複: %s" % types
    for u in re.findall(r'"(?:@id|url)":\s*"(https://www\.noe-match\.com/(?:articles|tools)/[^"]+)"', h):
        assert "kekkon-yarukoto" in u, "他ページのURL混入: %s" % u
    body_txt = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S))
    bad = re.findall(r"[Ѐ-ӿ가-힯]+", body_txt)
    assert not bad, "キリル・ハングル混入: %s" % bad[:3]
    print("written:", p, len(h), types)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    main()

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
OUT_DIR = os.path.join(ROOT, "tools", "koisaihi-simulator")
SITE = "https://www.noe-match.com"
URL = SITE + "/tools/koisaihi-simulator/"

TITLE = "デート代の平均は一回・月いくら？社会人・20代の目安と割り勘まで試算【2026年・無料】"
DESC = ("デート代と交際費を、付き合う前と付き合ってからに分けて試算する無料ツール。年代別の1回あたりの目安から、記念日・旅行・テーマパークを含めた年間総額まで計算します。全額・折半・収入比の3案で分担額も表示。簡易版と詳細版を選べます。登録不要。")

FAQ = [
    ("デート代は月いくらが平均ですか？",
     "年代と会う頻度で変わります。1回あたりの目安は大学生で1,500〜5,000円、20代の社会人で2,500〜9,000円、"
     "30代で3,000〜12,000円ほどです。週1回会うなら、20代の社会人で月2万〜4万円が一つの目安になります。"
     "ただし月々の金額だけを見ると、記念日と旅行を見落とします。"),
    ("「デート代がきつい」と感じるのはなぜですか？",
     "1回の金額ではなく、年間の積み上がりが原因であることが多くなります。"
     "誕生日・クリスマス・交際記念日・バレンタインは月々のデート代とは別に乗り、"
     "旅行やテーマパークは1回で数万円単位になります。"
     "月々だけを見ていると、年間の3〜4割を見落とすことになります。"),
    ("付き合う前と付き合ってからで、かかるお金は違いますか？",
     "性質が違います。付き合う前はサービスの月額と会う人数に比例した費用で、人数を増やすほど総額が上がります。"
     "付き合ってからは会う頻度に比例する費用に、記念日と旅行が乗ります。"
     "婚活期に苦しいのは人数×回数が効いているためで、交際期に苦しいのはイベントの積み上がりが効いているためです。"
     "原因が違うので、打つ手も変わります。"),
    ("デート代は男性が払うべきですか？",
     "決まりはありません。実務としては全額・折半・収入比の3つの考え方があります。"
     "全額は分かりやすい一方で期間が延びるほど負担が積み上がり、折半は対等ですが収入差があると片方の負担感が大きくなり、"
     "収入比は負担感が揃う代わりに金額が違うことへの納得が要ります。"
     "本ツールは3案の金額を並べて出すので、見比べてから決められます。"),
    ("テーマパークの費用はどのくらい見ておけばよいですか？",
     "日帰りでもチケットと飲食で2人1.5万〜2万円、グッズや交通費を含めると3万円台になることがあります。"
     "1泊すると7万円前後、2泊で10万円を超えることもあります。"
     "月々のデート代に混ぜて考えると実額から外れるため、本ツールでは別の費目として数えています。"),
    ("旅行はどのくらいの頻度が一般的ですか？",
     "泊まりの旅行は年1〜2回、日帰りの遠出は年数回というカップルが多いようです。"
     "ただし頻度より1回あたりの金額の影響が大きく、近場の1泊なら4万円ほど、"
     "遠方の連泊や海外になると15万〜30万円規模になります。"),
    ("簡易版と詳細版はどう違いますか？",
     "簡易版は年代・段階・頻度・使い方の4つだけで、月々のデート代を中心に概算します。"
     "詳細版では婚活サービスの月額、会う人数、誕生日やクリスマスなどの記念日、旅行、テーマパーク、"
     "手取り収入まで入力でき、年間の総額と収入比での分担額まで出せます。"),
    ("この試算はどのくらい正確ですか？",
     "一般的なレンジにもとづく概算です。地域・店の選び方・記念日の考え方で実額は大きく変わるため、"
     "金額や相場を断定するものではありません。年間でいくら積み上がるかを把握し、"
     "二人で分け方を話し合うための材料としてお使いください。"),
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
         "name": "デート代・交際費シミュレーター", "url": URL,
         "applicationCategory": "FinanceApplication", "operatingSystem": "All",
         "inLanguage": "ja", "description": DESC,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": SITE + "/"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
             {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": SITE + "/#tools"},
             {"@type": "ListItem", "position": 3, "name": "デート代・交際費シミュレーター"}]},
    ]
    lds = ""
    for d in ld:
        s = json.dumps(d, ensure_ascii=False)
        json.loads(s)
        lds += '<script type="application/ld+json">%s</script>\n' % s

    faq_html = "".join("<h3>Q%d. %s</h3>\n<p>%s</p>\n" % (i + 1, q, a)
                       for i, (q, a) in enumerate(FAQ))
    body = open(os.path.join(os.path.dirname(__file__), "_koisaihi_body.html"),
                encoding="utf-8").read()

    related = """
<div class="related"><h2>関連記事・ツール</h2><ul>
<li><a href="/articles/kinsen-kachikan-check/">結婚前に確認すべき金銭感覚のすり合わせ｜聞きにくいお金の話を切り出す方法</a></li>
<li><a href="/tools/konkatsu-type-shindan/">婚活タイプ診断｜使える時間とお金から向いている手段を選ぶ</a></li>
<li><a href="/tools/seikatsuhi-simulator/">ふたりの生活費シミュレーター｜同居した場合の月額と分担3案</a></li>
<li><a href="/tools/soudanjo-simulator/">結婚相談所 料金シミュレーター</a></li>
<li><a href="/tools/kekkon-yarukoto/">結婚のやることリスト｜順番つきで条件別に作成</a></li>
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
<div class="breadcrumb"><div class="wrap"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ デート代・交際費シミュレーター</div></div>
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
        assert "koisaihi-simulator" in u, "他ページのURL混入: %s" % u
    body_txt = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S))
    bad = re.findall(r"[Ѐ-ӿ가-힯]+", body_txt)
    assert not bad, "キリル・ハングル混入: %s" % bad[:3]
    print("written:", p, len(h), types)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    main()

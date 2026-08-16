# -*- coding: utf-8 -*-
"""離婚後の生活費シミュレーターを生成する。

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
OUT_DIR = os.path.join(ROOT, "tools", "rikongo-seikatsuhi")
SITE = "https://www.noe-match.com"
URL = SITE + "/tools/rikongo-seikatsuhi/"

TITLE = "離婚後の生活費シミュレーター｜収支・養育費・手当を無料で試算【2026年版】"
DESC = ("離婚後に毎月いくら入っていくら出るのかを試算する無料シミュレーター。"
        "裁判所の標準算定方式にもとづく養育費の目安、別居中の婚姻費用、受けられる手当、"
        "必要な初期費用まで表示します。判定はせず、数字だけを出します。登録不要。")

FAQ = [
    ("離婚後の生活費は月いくらかかりますか？",
     "家賃を除くと、大人1人でおおむね月11万円、子ども1人につき4万5千円程度が一つの目安です。"
     "ここに家賃が加わるため、住まいをどうするかで総額が大きく変わります。"
     "本ツールでは家賃を入力していただき、手取り・養育費・手当を合わせた月々の収支を表示します。"),
    ("養育費はいくらもらえますか？",
     "裁判所が公表している標準算定方式・算定表（令和元年版）にもとづき、"
     "双方の年収と子どもの人数・年齢から算出されるのが一般的です。"
     "収入と子どもの数・年齢だけで決まる仕組みなので、私立学校の費用や住宅ローンの負担といった"
     "個別事情は含まれていません。あくまで話し合いの出発点であり、"
     "実際の金額は協議、まとまらない場合は調停・審判で決まります。"),
    ("婚姻費用と養育費は何が違いますか？",
     "婚姻費用は離婚が成立するまでの生活費で、養育費より高くなるのが通常です。"
     "子どもの生活費だけでなく、配偶者本人の生活費も含むためです。"
     "別居期間が長引くほど累積するため、別居を考えている段階ではこの差を把握しておくと見通しが変わります。"),
    ("ひとり親が受けられる手当にはどんなものがありますか？",
     "児童手当（高校生年代まで）と児童扶養手当（ひとり親世帯が対象）が代表的です。"
     "このほか、ひとり親家庭等医療費助成、就学援助、住宅支援などがあります。"
     "児童扶養手当には所得制限があり一部支給になる場合があること、金額が年度ごとに改定されること、"
     "自治体の制度は内容が異なることから、必ずお住まいの自治体の公式情報でご確認ください。"),
    ("離婚するのにいくら貯金が必要ですか？",
     "住まいを移す場合、敷金・礼金・仲介手数料・前家賃で家賃の4〜5か月分が目安になります。"
     "これに加えて生活費の3か月分を予備として確保しておくと、収入が安定するまでの期間を凌げます。"
     "引っ越しの繁忙期（3〜4月）を外すと費用は下がります。"),
    ("このツールは「離婚したほうがいいか」を判定してくれますか？",
     "判定しません。その判断に必要な情報の大半は入力欄に収まらないためです。"
     "子どもとの関係、相手と会話が成り立つか、実家の支援、仕事の見通し、健康状態といった"
     "数字にならないものが決定的に効きます。それらを無視して機械が結論を出せば判断を歪めるだけなので、"
     "本ツールは数字を出すことに限定しています。"),
    ("収入が少なくても離婚できますか？",
     "金額の問題というより、収支の見通しが立つかどうかの問題です。"
     "本ツールで毎月の不足額が分かれば、家賃を下げる・就労時間を増やす・支援制度を使うといった"
     "どれを動かせば成立するかが具体的になります。不足額が分からないまま迷い続けるより、"
     "数字にしてから考えるほうが手を打てます。"),
    ("この試算はどのくらい正確ですか？",
     "公表されている制度と統計にもとづく概算であり、法的な助言ではありません。"
     "養育費・婚姻費用は裁判所の算定表がレンジで示されることに合わせ、本ツールもレンジで表示しています。"
     "個別の事情による判断は弁護士等の専門家にご相談ください。"),
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
         "name": "離婚後の生活費シミュレーター", "url": URL,
         "applicationCategory": "FinanceApplication", "operatingSystem": "All",
         "inLanguage": "ja", "description": DESC,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": SITE + "/"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
             {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": SITE + "/#tools"},
             {"@type": "ListItem", "position": 3, "name": "離婚後の生活費シミュレーター"}]},
    ]
    lds = ""
    for d in ld:
        s = json.dumps(d, ensure_ascii=False)
        json.loads(s)
        lds += '<script type="application/ld+json">%s</script>\n' % s

    faq_html = "".join("<h3>Q%d. %s</h3>\n<p>%s</p>\n" % (i + 1, q, a)
                       for i, (q, a) in enumerate(FAQ))
    body = open(os.path.join(os.path.dirname(__file__), "_rikongo_body.html"),
                encoding="utf-8").read()

    related = """
<div class="related"><h2>関連記事・ツール</h2><ul>
<li><a href="/articles/rikon-junbi-jyunban/">離婚を考えたら最初にすること｜証拠集め・お金の整理・相談先の順番</a></li>
<li><a href="/articles/rikon-okane-genjitsu/">離婚した場合のお金の現実｜財産分与・慰謝料の基礎知識と備え方</a></li>
<li><a href="/articles/koninhiyou-guide/">婚姻費用とは｜別居中の生活費分担の仕組みと相手が支払わない時の対処法</a></li>
<li><a href="/articles/sango-rikon/">産後に離婚を考えたとき｜勢いで決めないための、産後特有の事情の切り分け方</a></li>
<li><a href="/tools/seikatsuhi-simulator/">ふたりの生活費シミュレーター</a></li>
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
<div class="breadcrumb"><div class="wrap"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ 離婚後の生活費シミュレーター</div></div>
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
        assert "rikongo-seikatsuhi" in u, "他ページのURL混入: %s" % u
    body_txt = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S))
    bad = re.findall(r"[Ѐ-ӿ가-힯]+", body_txt)
    assert not bad, "キリル・ハングル混入: %s" % bad[:3]
    print("written:", p, len(h), types)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    main()

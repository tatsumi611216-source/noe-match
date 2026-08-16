# -*- coding: utf-8 -*-
"""生活費シミュレーターを生成する。

既存ツール（結婚資金計算機）のシェル（CSS・ヘッダ・フッタ）を流用し、
中身だけ差し替える。build_page.py と同じ思想。

数値の出典（2026-08-16に一次情報を確認）:
  総務省統計局「家計調査（家計収支編）2025年（令和7年）平均結果の概要」
  二人以上の世帯（平均世帯人員2.87人・世帯主平均年齢60.7歳）1か月平均
    消費支出 314,001円 / 食料 94,895 / 住居 18,678 / 光熱・水道 24,547 /
    家具・家事用品 13,068 / 被服及び履物 10,063 / 保健医療 15,863 /
    交通・通信 45,730 / 教育 11,939 / 教養娯楽 32,125 / その他 47,093

**重要な注意（ツール内にも明記する）**
  1. この統計は平均2.87人・世帯主60.7歳。**2人暮らしの新婚世帯より人数が多い**
     ため、そのまま当てはめると高めに出る
  2. 「住居」18,678円が低いのは**持ち家世帯を含む**ため。家賃の実態ではない
     → 家賃はユーザー入力を必須にし、統計値を使わない
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "kekkon-shikin-keisanki", "index.html")
OUT_DIR = os.path.join(ROOT, "tools", "seikatsuhi-simulator")
SITE = "https://www.noe-match.com"
URL = SITE + "/tools/seikatsuhi-simulator/"

TITLE = "ふたりの生活費シミュレーター｜月額の内訳と「収入比でいくらずつ」を試算【2026年版】"
DESC = ("新婚・二人暮らしの生活費を月額で試算し、折半・収入比・定額＋按分の3案で"
        "「どちらがいくら出すか」まで出す無料シミュレーター。家賃・光熱・通信・食費の"
        "内訳と、削れる固定費の余地も表示します。登録不要。")

FAQ = [
    ("二人暮らしの生活費は月いくらが目安ですか？",
     "家賃を除くと、二人暮らしではおおむね月15万〜20万円のレンジに収まるケースが多くなります。"
     "ただし最大の変数は家賃で、地域と間取りで数万円単位で変わるため、"
     "本ツールでは家賃を入力していただく方式にしています。"
     "総務省「家計調査」2025年平均の二人以上世帯（平均2.87人）では消費支出が月314,001円ですが、"
     "これは人数が多く世帯主の平均年齢も60.7歳のため、新婚2人世帯にそのまま当てはめると高めに出ます。"),
    ("生活費は折半にすべきですか？",
     "決まりはありません。判断の分かれ目は「同じ額を出すのが公平」と考えるか、"
     "「同じくらい負担感があるのが公平」と考えるかです。前者なら折半、後者なら収入比になります。"
     "本ツールでは折半・収入比・定額＋残り按分の3案を同時に表示するので、"
     "金額を見比べてから決められます。"),
    ("収入差がある場合はどう分けますか？",
     "収入比で按分する方法が使われます。たとえば手取りが30万円と20万円なら6:4です。"
     "ただし収入比だけだと「対等に出した」感覚が持てないという声もあるため、"
     "各自が同額を出したうえで超過分だけ収入比にする方法もあります。"
     "本ツールはこの2つを並べて表示します。"),
    ("光熱費の目安はどのくらいですか？",
     "総務省「家計調査」2025年平均では、二人以上の世帯（平均2.87人）の光熱・水道が月24,547円です。"
     "2人暮らしは人数が少ないぶんこれより低くなる傾向があります。"
     "実額が分かる場合は入力欄に入れていただくと精度が上がります。"),
    ("家賃はいくらまでが適正ですか？",
     "手取りに対する割合で見るのが一般的で、一つの目安として手取りの25〜30％以内に収める考え方があります。"
     "本ツールでは入力された家賃が手取り合計の何％にあたるかを表示するので、"
     "この目安と比べて判断できます。"),
    ("固定費はどこから見直すと効果がありますか？",
     "金額が大きく、一度変えれば毎月効き続けるものから着手するのが効率的です。"
     "具体的には通信（回線・スマホ）、保険、住まいの順で、"
     "食費や日用品のような変動費より先に見ることをおすすめします。"),
    ("この試算はどのくらい正確ですか？",
     "公的統計と当サイト掲載のレンジをもとにした概算です。"
     "地域・築年数・世帯の生活スタイルで実額は大きく変わるため、"
     "支出の全体像をつかみ、分担を話し合うための出発点としてお使いください。"),
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

    ld = []
    ld.append({"@context": "https://schema.org", "@type": "FAQPage",
               "mainEntity": [{"@type": "Question", "name": q,
                               "acceptedAnswer": {"@type": "Answer", "text": a}}
                              for q, a in FAQ]})
    ld.append({"@context": "https://schema.org", "@type": "WebApplication",
               "name": "ふたりの生活費シミュレーター", "url": URL,
               "applicationCategory": "FinanceApplication",
               "operatingSystem": "All", "inLanguage": "ja",
               "description": DESC,
               "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
               "publisher": {"@type": "Organization", "name": "Noe結婚設計室",
                             "url": SITE + "/"}})
    ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList",
               "itemListElement": [
                   {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
                   {"@type": "ListItem", "position": 2, "name": "無料ツール",
                    "item": SITE + "/#tools"},
                   {"@type": "ListItem", "position": 3, "name": "ふたりの生活費シミュレーター"}]})

    lds = ""
    for d in ld:
        s = json.dumps(d, ensure_ascii=False)
        json.loads(s)
        lds += '<script type="application/ld+json">%s</script>\n' % s

    faq_html = "".join("<h3>Q%d. %s</h3>\n<p>%s</p>\n" % (n + 1, q, a)
                       for n, (q, a) in enumerate(FAQ))

    body = open(os.path.join(os.path.dirname(__file__),
                             "_seikatsuhi_body.html"), encoding="utf-8").read()

    html = """%(gtag)s<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<link rel="canonical" href="%(url)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="website">
<meta property="og:url" content="%(url)s">
<meta property="og:image" content="%(site)s/images/og/seikatsuhi-og.png">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="%(site)s/images/og/seikatsuhi-og.png">
%(style)s%(lds)s</head>
%(header)s<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ ふたりの生活費シミュレーター</div>
%(body)s
<article>
<h2 id="faq">よくある質問</h2>
%(faq)s</article>
%(footer)s""" % dict(gtag=gtag, title=TITLE, desc=DESC, url=URL, site=SITE, style=style,
                     lds=lds, header=header, body=body, faq=faq_html, footer=footer)

    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, "index.html")
    open(p, "w", encoding="utf-8").write(html)

    out = open(p, encoding="utf-8").read()
    types = []
    for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', out, re.S):
        d = json.loads(s)
        types.append(d.get("@type"))
        u = d.get("url") or ""
        if u and u != URL:
            raise AssertionError("他ページのJSON-LD混入: %s" % u)
    if len(types) != len(set(types)):
        raise AssertionError("JSON-LDの型が重複: %s" % types)
    print("written:", p, len(out), "bytes / LD:", types)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    main()

# -*- coding: utf-8 -*-
"""婚活タイプ診断ツールを生成する。

語の根拠（2026-08-16 サジェスト実測）:
  婚活 診断 = 10件（自分に合った 婚活 診断／登録なし／無料／適性診断）
  マッチングアプリ 診断 = 10件（向いてない診断／適性診断）
  ★ 婚活 手段 = 0件／自分に合う 婚活 = 0件／婚活 費用 比較 = 0件
  → **「手段」を主題語にしてはいけない。「診断」で組む。**

既存 tools/soudanjo-simulator との境界:
  あちらは「相談所に決めた人が費用を試算する」。こちらは「そもそもどの手段か」。
  前段に置き、結果が相談所のときだけ既存ツールへ送る。

台帳の制約（agent/AGENT.md）:
  - 成婚・効果の断定禁止（相談所の成婚保証は景表法上アウト）
  - 属性特化の案件は、その属性を不利・欠点として描かない
  → 「向いていない手段」は**本人ではなく手段側の問題**として書く
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "kekkon-shikin-keisanki", "index.html")
OUT_DIR = os.path.join(ROOT, "tools", "konkatsu-type-shindan")
SITE = "https://www.noe-match.com"
URL = SITE + "/tools/konkatsu-type-shindan/"

TITLE = "婚活タイプ診断｜自分に合った婚活はどれか無料で診断【登録なし・2026年版】"
DESC = ("マッチングアプリ・結婚相談所・婚活パーティー・属性特化の4手段から、"
        "使える時間とお金・働き方・得意な進め方に合うものを診断します。"
        "向いていない手段とその理由、月いくら・週何時間かかるかの目安も表示。無料・登録不要。")

FAQ = [
    ("自分に合った婚活はどうやって選べばよいですか？",
     "手段の優劣ではなく、生活のかたちと噛み合うかで選びます。具体的には「使える時間」「使える金額」"
     "「働き方（夜勤・転勤・残業の有無）」「対面と文章のどちらが得意か」の4点が効きます。"
     "たとえば使える時間が少ないなら探す作業を任せられる相談所の価値が上がり、"
     "予算が限られるならアプリが中心になります。本ツールはこの4点から4手段のスコアを出します。"),
    ("マッチングアプリに向いていないのはどんな場合ですか？",
     "文章でのやりとりを続けるのが負担な場合と、探して選ぶ時間を確保しづらい場合です。"
     "アプリは費用が最も低い一方、探す・選ぶ・やりとりするという作業がすべて自分に残ります。"
     "これは向き不向きの問題ではなく、手段の設計と生活が噛み合っていないだけなので、"
     "手段を変えれば解決します。"),
    ("結婚相談所はどんな人に向いていますか？",
     "使える時間が少ない人、結婚の時期を早めに決めたい人、やりとりの負担を減らしたい人です。"
     "相手の結婚の意思が確認されていること、担当者が日程調整などに入ることが特徴になります。"
     "一方で費用は4手段の中で最も高くなるため、予算が制約になる場合は"
     "オンライン型から見るかアプリとの併用が現実的です。"),
    ("婚活パーティーが噛み合わないのはどんな場合ですか？",
     "交代制勤務や夜勤がある働き方、休日が読めない働き方の場合です。開催日程が固定されるため、"
     "参加できない回が増えます。また初対面の場が続くことが消耗につながる場合も噛み合いにくくなります。"
     "地域によっては開催数が限られ、回数を確保しにくいこともあります。"),
    ("属性特化のサービスとは何ですか？",
     "趣味・ペット・体型・再婚・働き方など、特定の前提を共有した人が集まるサービスです。"
     "最初から条件が共有されているぶん説明の手間が減り、話が早く進みます。"
     "一方で母数は小さくなるため、地域によっては候補が限られます。"
     "共有しておきたい条件が複数ある場合ほど価値が上がります。"),
    ("婚活にはいくらかかりますか？",
     "手段によって幅があります。一般的なレンジとして、アプリは月3,000〜4,000円ほど、"
     "婚活パーティーは1回3,000〜7,000円ほど、結婚相談所は初期費用10万〜30万円に加えて"
     "月会費1万〜2万円ほどです。属性特化サービスは形式により異なります。"
     "実際の費用は各サービスの公式情報でご確認ください。"),
    ("複数の手段を同時に使ってもよいですか？",
     "使えますが、時間とお金の両方に余裕がある場合に限ります。"
     "どちらも厳しい状況で並行すると、やりとりの管理だけで時間が消えてしまい、"
     "結果として1つに絞ったほうが早く進むことが多くなります。"
     "本ツールでは上位2つのスコアが接近している場合、どちらから試しても構わない旨を表示します。"),
    ("この診断の結果はどのくらい当たりますか？",
     "手段選びの目安を示すもので、結果や成婚を保証するものではありません。"
     "入力された条件から、各手段の設計と噛み合う度合いを相対的に比較しています。"
     "条件が変われば結果も変わるため、働き方や使える時間が変わったときに"
     "もう一度試していただくと役に立ちます。"),
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
                         "acceptedAnswer": {"@type": "Answer", "text": a}}
                        for q, a in FAQ]},
        {"@context": "https://schema.org", "@type": "WebApplication",
         "name": "婚活タイプ診断", "url": URL,
         "applicationCategory": "LifestyleApplication",
         "operatingSystem": "All", "inLanguage": "ja", "description": DESC,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": SITE + "/"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
             {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": SITE + "/#tools"},
             {"@type": "ListItem", "position": 3, "name": "婚活タイプ診断"}]},
    ]
    lds = ""
    for d in ld:
        s = json.dumps(d, ensure_ascii=False)
        json.loads(s)
        lds += '<script type="application/ld+json">%s</script>\n' % s

    faq_html = "".join("<h3>Q%d. %s</h3>\n<p>%s</p>\n" % (n + 1, q, a)
                       for n, (q, a) in enumerate(FAQ))
    body = open(os.path.join(os.path.dirname(__file__), "_konkatsu_body.html"),
                encoding="utf-8").read()

    related = """
<div class="related"><h2>関連記事・ツール</h2><ul>
<li><a href="/articles/konkatsu-roadmap/">婚活を何から始めるか｜手順の全体像</a></li>
<li><a href="/articles/agency-vs-app/">マッチングアプリと結婚相談所はどちらを選ぶべきか</a></li>
<li><a href="/articles/soudanjo-hikaku/">結婚相談所の比較｜タイプ別の選び方</a></li>
<li><a href="/articles/app-tsukare-guide/">アプリ疲れの原因と、続け方の立て直し</a></li>
<li><a href="/articles/konkatsu-party-guide/">婚活パーティーの選び方と当日の動き方</a></li>
<li><a href="/tools/soudanjo-simulator/">結婚相談所の費用シミュレーター</a></li>
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
<div class="breadcrumb"><div class="wrap"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ 婚活タイプ診断</div></div>
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

    # 生成後の検証（テンプレ由来のLD混入・外部URL・@type重複を弾く）
    h = open(p, encoding="utf-8").read()
    import re
    types = []
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        d = json.loads(b)
        types.append(d.get("@type"))
    assert len(types) == len(set(types)), "JSON-LDの@typeが重複: %s" % types
    for u in re.findall(r'"(?:@id|url)":\s*"(https://www\.noe-match\.com/(?:articles|tools)/[^"]+)"', h):
        assert "konkatsu-type-shindan" in u, "他ページのURLが混入: %s" % u
    print("written:", p, len(h), types)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    main()

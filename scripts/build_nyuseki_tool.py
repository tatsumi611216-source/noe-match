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
OUT_DIR = os.path.join(ROOT, "tools", "nyuseki-calendar")
SITE = "https://www.noe-match.com"
URL = SITE + "/tools/nyuseki-calendar/"

TITLE = "入籍日カレンダー2026・2027｜天赦日・一粒万倍日から縁起のいい日を無料で絞り込む"
DESC = ("2026年・2027年の入籍日を、天赦日・一粒万倍日・寅の日・巳の日と曜日・祝日・語呂合わせから"
        "絞り込める無料カレンダー。土日がいい、平日がいいといった条件で候補日を出します。登録不要。")

FAQ = [
    ("入籍日はどうやって決めればよいですか？",
     "縁起のいい日から選ぶ前に、二人とも動ける日か、役所が開いている日か、記念日として毎年祝える日かを先に決めると絞りやすくなります。"
     "土日祝も時間外窓口で受理されますが、書類に不備があるとその場で直せないため、書類に不安がある場合は平日が確実です。"),
    ("天赦日とはどんな日ですか？",
     "暦の上で最も縁起がよいとされる日で、年に5〜6日しかありません。季節ごとに決まった干支の日が天赦日にあたるため、"
     "日付は年によって変わります。数が少ないぶん希少とされ、他の吉日と重なる日はさらに強い日とされます。"),
    ("一粒万倍日とは何ですか？",
     "小さなことが大きく実るとされる日で、始めごとに向くとされます。年に60日前後あり、天赦日に比べると数は多くなります。"
     "節月ごとに該当する干支が決まっているため、月によって出現する曜日が変わります。"),
    ("天赦日と一粒万倍日が重なる日はありますか？",
     "あります。ただし年に1〜2日程度しかないため、非常に希少とされます。本ツールではこうした重なりを縁起の強さとして順位づけし、上位に表示します。"),
    ("六曜（大安・友引）は入っていますか？",
     "含めていません。六曜は旧暦にもとづくもので、天赦日や一粒万倍日が使う暦とは別の体系だからです。"
     "会場や親世代が六曜を重視する場合は、本ツールで候補日を絞ったあとに六曜カレンダーで確認してください。"),
    ("人気の入籍日は混みますか？",
     "混みます。天赦日や語呂合わせの日、特に土日と重なる日は窓口が集中しやすく、待ち時間が長くなることがあります。"
     "写真撮影や記念品の対応は自治体により異なるため、希望がある場合は事前に確認しておくと当日慌てません。"),
    ("結婚式の前と後、どちらに入籍すべきですか？",
     "どちらでも構いませんが、姓の変更手続きのタイミングが変わります。式の前に入籍すると式の準備と並行して手続きを進めることになり、"
     "後にすると旧姓のまま式を迎えることになります。招待状や会場への申し込み名義にも関わるため、早めに決めておくと迷いが減ります。"),
    ("吉日を気にしないという選択はありですか？",
     "あります。実際に「気にしない」という検索も一定数あります。二人が納得していれば問題はなく、"
     "むしろ休みを合わせやすい日や記念日にしたい日を優先するほうが、毎年祝いやすい日になります。"),
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
         "name": "入籍日カレンダー", "url": URL,
         "applicationCategory": "LifestyleApplication", "operatingSystem": "All",
         "inLanguage": "ja", "description": DESC,
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": SITE + "/"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList",
         "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
             {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": SITE + "/#tools"},
             {"@type": "ListItem", "position": 3, "name": "入籍日カレンダー"}]},
    ]
    lds = ""
    for d in ld:
        s = json.dumps(d, ensure_ascii=False)
        json.loads(s)
        lds += '<script type="application/ld+json">%s</script>\n' % s

    faq_html = "".join("<h3>Q%d. %s</h3>\n<p>%s</p>\n" % (i + 1, q, a)
                       for i, (q, a) in enumerate(FAQ))
    body = open(os.path.join(os.path.dirname(__file__), "_nyuseki_body.html"),
                encoding="utf-8").read()

    related = """
<div class="related"><h2>関連記事・ツール</h2><ul>
<li><a href="/articles/nyuseki-2027-guide/">2027年の入籍日はいつがいい？｜天赦日6回の「当たり年」吉日と選び方ガイド</a></li>
<li><a href="/articles/propose-guide/">結婚の段取り完全ガイド｜プロポーズから入籍・入籍後の手続きまで整理</a></li>
<li><a href="/articles/kisei-kekkon-aisatsu/">年末年始の帰省と結婚挨拶・手土産ガイド</a></li>
<li><a href="/articles/kekkon-houkoku-nengajou/">結婚報告はがき・年賀状の作り方｜文例・写真選び・出す範囲のマナー</a></li>
<li><a href="/tools/kekkon-shikin-keisanki/">結婚資金計算機｜総額とご祝儀差引後の自己負担を試算</a></li>
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
<div class="breadcrumb"><div class="wrap"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ 入籍日カレンダー</div></div>
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
        assert "nyuseki-calendar" in u, "他ページのURL混入: %s" % u
    body_txt = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", "", h, flags=re.S))
    bad = re.findall(r"[Ѐ-ӿ가-힯]+", body_txt)
    assert not bad, "キリル・ハングル混入: %s" % bad[:3]
    print("written:", p, len(h), types)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    main()

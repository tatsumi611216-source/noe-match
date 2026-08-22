# -*- coding: utf-8 -*-
"""アプリ別「結婚率・公表データ」早見表ツールを生成する（Eクラスタの核・2026-08-22）。

語の根拠（2026-08-22 サジェスト実測）:
  マッチングアプリ 結婚率 = 10件フル（アプリ別／ランキング／高い／2024／知恵袋）
  マッチングアプリ 成婚率 = 6件（ランキング／低い／高い）
  ★ 婚活アプリ 成婚率 比較 = 0件、婚活アプリ 実績 = 1件 → 主題語は「結婚率」で組む
  上位にツール形式は0（success-rate-data 33位の静的記事のみ）

型Aの原則（agent/AGENT.md「型A」）:
  **公表されているかどうかを正直に答える。** 非公表なら非公表と書く。
  推測値・独自試算を結婚率として提示するのは禁止。

数値はすべて 2026-08-22 に各社公式サイト・公式リリースで確認したもの（一部は既存型A記事の確認済み値）。
案件は結果連動：選んだアプリに提携があればそのアプリ、無ければ「成婚退会者数を公表している
ユーブライド」を比較対象として提示（ツールの主題＝公表姿勢の比較なので、結果と無関係な広告ではない）。
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "tools", "kekkon-shikin-keisanki", "index.html")
OUT_DIR = os.path.join(ROOT, "tools", "app-kekkonritsu-data")
SITE = "https://www.noe-match.com"
URL = SITE + "/tools/app-kekkonritsu-data/"
CHECKED = "2026年8月22日"

TITLE = "マッチングアプリの結婚率・公表データ早見表｜アプリ別に「公表している数字・していない数字」を確認【2026年8月】"
DESC = ("Pairs・with・Omiai・タップル・ユーブライド・マリッシュ・ブライダルネットについて、"
        "結婚率・成婚者数・会員数・年齢構成・男女比を「公式に公表しているか」で整理した早見表。"
        "非公表は非公表と表示し、出典と確認日を付けます。公的統計（ネットで知り合った夫婦の平均交際期間2.8年）も併記。無料・登録不要。")

# --- データ（公表／非公表・出典・確認日） ---
YOUBRIDE = "https://t.afi-b.com/visit.php?a=62571t-63703183&p=C982892I"
MARRISH = "https://t.afi-b.com/visit.php?a=p8318c-9288783U&p=C982892I"
BRIDALNET = "https://px.a8.net/svt/ejp?a8mat=4B8B4Q+39VYEY+FOG+6PJZL"

APPS = [
 {"k": "pairs", "n": "Pairs（ペアーズ）", "art": "/articles/pairs-kaiin-data/", "artn": "Pairsの会員数データ｜累計2,700万人超の読み方",
  "rows": [
   ["結婚率・成婚率", "非公表", "公式サイトに記載なし", False],
   ["成婚者数", "非公表（「毎月13,000人に恋人ができた」は自己申告ベースの公式発表）", "公式サイト", False],
   ["会員数", "累計登録者数 2,700万人超", "公式サイト（累計。実稼働会員数は非公表）", True],
   ["年齢構成", "非公表", "公式サイトに年代別比率の記載なし", False],
   ["男女比", "非公表", "公式サイトに記載なし", False],
   ["料金（男性・公式）", "Web購入 1ヶ月4,100円／12ヶ月 月1,675円。女性は基本無料", "pairs.lv/price", True],
  ], "pr": None},
 {"k": "with", "n": "with（ウィズ）", "art": "/articles/with-seriousness-data/", "artn": "withの結婚率は公表されているのか",
  "rows": [
   ["結婚率・成婚率", "非公表", "公式サイト・公式発表に記載なし", False],
   ["成婚者数", "非公表", "同上", False],
   ["会員数", "1,500万人", "公式サイト（2026年1月時点）", True],
   ["年齢構成", "非公表（20代中心と公式に訴求）", "公式サイトに比率の記載なし", False],
   ["男女比", "非公表", "公式サイトに記載なし", False],
   ["料金（男性・公式）", "公式ページは画像表示のため金額は公式サイトで確認。21歳以下限定の1週間プランあり", "with.is/products_list", False],
  ], "pr": None},
 {"k": "omiai", "n": "Omiai（オミアイ）", "art": "/articles/omiai-danjohi-data/", "artn": "Omiaiの男女比は約5対5｜公式が公表した年齢構成",
  "rows": [
   ["結婚率・成婚率", "非公表", "公式サイト・公式リリースに記載なし", False],
   ["成婚者数", "非公表", "同上", False],
   ["会員数", "累計 1,000万人", "株式会社エニトグループ 公式発表（2024年7月時点）", True],
   ["年齢構成", "30代以下が84%（20代・30代の内訳は非公表）", "エニトグループ リリース（2026年2月20日）", True],
   ["男女比", "約5対5", "同上（主要アプリで男女比を数値公表しているのはOmiaiのみ）", True],
   ["料金（公式）", "クレジットカード決済 1ヶ月4,400円／12ヶ月 月2,150円（男女同額）", "fb.omiai-jp.com/price", True],
  ], "pr": None},
 {"k": "tapple", "n": "タップル", "art": "/articles/tapple-seriousness-data/", "artn": "タップルの本気度データ｜公表されている数字",
  "rows": [
   ["結婚率・成婚率", "非公表", "公式サイトに記載なし", False],
   ["成婚者数", "非公表", "同上", False],
   ["会員数", "累計 2,000万人", "公式発表（2024年4月末時点）", True],
   ["年齢構成", "非公表", "公式サイトに比率の記載なし", False],
   ["利用目的の内訳", "非公表", "公式サイトに記載なし", False],
   ["料金（公式）", "公式料金ページは要確認（年代別プランなし）", "tapple.me", False],
  ], "pr": None},
 {"k": "youbride", "n": "ユーブライド", "art": "/articles/youbride-seikon-data/", "artn": "ユーブライドの成婚率は公表されているか｜成婚退会者数の読み方",
  "rows": [
   ["結婚率・成婚率", "非公表（率ではなく件数を公表）", "公式サイト", False],
   ["成婚者数", "累計成婚退会者 19,350名", "公式サイト（2013年7月〜2026年8月）", True],
   ["会員数", "累計 300万人", "公式サイト", True],
   ["年齢構成", "非公表（「30代〜50代の婚活・再婚向け」と公式記載）", "youbride.jp/guide/about", False],
   ["男女比", "非公表", "公式サイトに記載なし", False],
   ["料金（公式・男女同額）", "1ヶ月5,000円／3ヶ月 月3,600円／12ヶ月 月2,400円", "youbride.jp/guide/price", True],
  ], "pr": {"u": YOUBRIDE, "h": "成婚退会者数を公式に公表している婚活サイト", "b": "累計成婚退会者19,350名（2013年7月〜2026年8月・公式発表）。率ではなく件数の公表だが、主要アプリで成婚の実数を継続開示しているのはユーブライドのみ。", "btn": "ユーブライド公式サイトを見る（登録無料）", "c": "#7c2e42", "note": "30〜50代の婚活・再婚層向け。料金・条件は公式サイトでご確認ください"}},
 {"k": "marrish", "n": "マリッシュ", "art": "/articles/marrish-saikon-data/", "artn": "マリッシュの再婚成婚データ｜公表値で確認する",
  "rows": [
   ["結婚率・成婚率", "非公表", "公式サイトに記載なし", False],
   ["成婚者数", "非公表（「平均4ヶ月でカップル成立」は全年代平均の公式表記）", "公式サイト", False],
   ["会員数", "400万人超", "公式サイト", True],
   ["年齢構成", "非公表（「30代〜50代・再婚」向けと公式訴求）", "公式サイトに比率の記載なし", False],
   ["再婚向け機能", "シングルマザー・ファーザーの再婚を応援するリボンマーク", "公式サイト", True],
   ["料金（公式）", "公式料金ページは画像表示のため金額は公式サイトで確認。女性は基本無料", "marrish.com/price", False],
  ], "pr": {"u": MARRISH, "h": "再婚・ひとり親の前提を最初から共有できる婚活アプリ", "b": "成婚率は非公表だが、再婚応援のリボンマークなど再婚層向けの機能を公式に明示している。再婚・バツイチの文脈で選ぶなら比較対象になる。", "btn": "マリッシュ公式サイトを見る（登録無料）", "c": "#7c2e42", "note": "料金・条件は公式サイトでご確認ください"}},
 {"k": "bridalnet", "n": "ブライダルネット", "art": "/articles/agency-vs-app/", "artn": "アプリと相談所の中間形態としてのブライダルネット",
  "rows": [
   ["結婚率・成婚率", "非公表", "公式サイトに記載なし", False],
   ["成婚者数", "「年間27万件以上カップル成立」（2022年実績）", "公式サイト（成婚数ではなくカップル成立数）", True],
   ["会員数", "非公表", "公式サイトに記載なし", False],
   ["年齢構成", "非公表", "公式サイトに記載なし", False],
   ["運営", "IBJ（結婚相談所連盟）", "公式サイト", True],
   ["料金（公式）", "月会員3,980円／年会員 年額24,000円。IBJ onlineコース 入会金11,000円＋月7,700円", "bridalnet.co.jp/price", True],
  ], "pr": {"u": BRIDALNET, "h": "アプリと結婚相談所の中間形態", "b": "IBJが運営する婚活サイト。成婚率は非公表だが、料金は年額まで公式に明示している。アプリでは物足りず相談所は重い、という人の比較対象。", "btn": "ブライダルネットの料金・機能を見る", "c": "#7c2e42", "note": "料金・条件は公式サイトでご確認ください"}},
 {"k": "zexy", "n": "ゼクシィ縁結び（サービス終了）", "art": "/articles/zexy-enmusubi-data/", "artn": "ゼクシィ縁結びはサービス終了｜公表されていた数字の記録",
  "rows": [
   ["状態", "2026年3月末でサービス終了（エージェントは2026年6月末）", "リクルート プレスリリース（2025年11月17日）", True],
   ["結婚率・成婚率", "終了前も非公表", "—", False],
  ], "pr": None},
]

FAQ = [
 ("マッチングアプリの結婚率は公表されていますか？",
  "主要アプリ（Pairs・with・Omiai・タップル・ユーブライド・マリッシュ・ブライダルネット）は、いずれも結婚率・成婚率を公式には公表していません（2026年8月22日に各社公式サイトで確認）。公表されているのは会員数、ユーブライドの累計成婚退会者数（19,350名）、Omiaiの男女比（約5対5）と年齢構成（30代以下84%）など、率ではない数字です。"),
 ("「結婚率◯%」と書いてある比較サイトの数字は何ですか？",
  "多くは出典のない推計か、婚活サービス利用者全体の調査（ブライダル総研など）の数字を特定アプリに当てはめたものです。各社が公表していない以上、アプリ別の結婚率を示す数字には公的な裏付けがありません。出典と確認日が書かれているかを確認してください。"),
 ("アプリで出会った人は何年くらいで結婚していますか？",
  "公的統計（国立社会保障・人口問題研究所 第16回出生動向基本調査・2021年）では、SNS・アプリなど「ネットで」知り合った夫婦の平均交際期間（知り合ってから結婚まで）は2.8年で、従来の恋愛結婚の4.9年より短いと報告されています。アプリ別の期間は各社とも非公表です。"),
 ("結婚の実数を公表しているアプリはありますか？",
  "ユーブライドが「累計成婚退会者19,350名（2013年7月〜2026年8月）」を公式に公表しています。率ではなく件数ですが、主要アプリで成婚の実数を継続して開示しているのはユーブライドのみでした（2026年8月時点・当サイト確認）。"),
 ("この早見表の数字はいつの時点のものですか？",
  "2026年8月22日に各社の公式サイト・公式リリースで確認したものです（一部は各社の公表時点を併記）。料金や公表内容は変更されるため、申込前に必ず公式サイトで再確認してください。"),
 ("非公表のアプリは信用できないということですか？",
  "そうではありません。成婚率は分母・分子の定義で大きく変わるため、公表しない判断にも合理性があります。この早見表は「公表しているか」という事実を並べたもので、優劣を判定するものではありません。"),
]


def shell():
    h = open(SRC, encoding="utf-8").read()
    gtag = h[:h.find("<meta charset")]
    style = h[h.find('<link href="https://fonts.googleapis.com'):h.find('<script type="application/ld+json">')]
    header = h[h.find("<body>"):h.find('<div class="breadcrumb"')]
    footer = h[h.rfind("<footer"):]
    return gtag, style, header, footer


def static_table():
    out = []
    for a in APPS:
        if a["k"] == "zexy":
            continue
        pub = sum(1 for r in a["rows"] if r[3])
        out.append("<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%d/%d</td></tr>" % (
            a["n"], a["rows"][0][1].split("（")[0], a["rows"][1][1].split("（")[0],
            a["rows"][2][1], a["rows"][3][1].split("（")[0], pub, len(a["rows"])))
    return ("<div class=\"table-wrap\"><table><thead><tr><th>アプリ</th><th>結婚率・成婚率</th><th>成婚者数</th><th>会員数（公表値）</th><th>年齢構成</th><th>公表項目数</th></tr></thead><tbody>"
            + "".join(out) + "</tbody></table></div>")


def main():
    gtag, style, header, footer = shell()
    ld = [
        {"@context": "https://schema.org", "@type": "FAQPage",
         "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
        {"@context": "https://schema.org", "@type": "WebApplication",
         "name": "マッチングアプリの結婚率・公表データ早見表", "url": URL,
         "applicationCategory": "LifestyleApplication", "operatingSystem": "All", "inLanguage": "ja",
         "description": DESC, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "publisher": {"@type": "Organization", "name": "Noe結婚設計室", "url": SITE + "/"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "ホーム", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": SITE + "/#tools"},
            {"@type": "ListItem", "position": 3, "name": "マッチングアプリの結婚率・公表データ早見表"}]},
    ]
    lds = ""
    for d in ld:
        s = json.dumps(d, ensure_ascii=False); json.loads(s)
        lds += '<script type="application/ld+json">%s</script>\n' % s
    faq_html = "".join("<h3>Q%d. %s</h3>\n<p>%s</p>\n" % (n + 1, q, a) for n, (q, a) in enumerate(FAQ))
    body = open(os.path.join(os.path.dirname(__file__), "_kekkonritsu_body.html"), encoding="utf-8").read()
    body = body.replace("__DATA_JSON__", json.dumps(APPS, ensure_ascii=False)).replace("__STATIC_TABLE__", static_table()).replace("__CHECKED__", CHECKED)
    related = """
<div class="related"><h2>関連記事・ツール</h2><ul>
<li><a href="/articles/kekkon-madeno-kikan-data/">マッチングアプリから結婚までの期間｜公的統計では2.8年</a></li>
<li><a href="/articles/success-rate-data/">マッチングアプリの結婚率データ｜公表・非公表を分けて読む</a></li>
<li><a href="/articles/appkon-wariai-data/">アプリ婚の割合｜公的統計では13.6%</a></li>
<li><a href="/articles/youbride-seikon-data/">ユーブライドの成婚率は公表されているか</a></li>
<li><a href="/articles/omiai-danjohi-data/">Omiaiの男女比は約5対5｜公式が公表した年齢構成</a></li>
<li><a href="/tools/konkatsu-type-shindan/">婚活タイプ診断｜自分に合った婚活はどれか</a></li>
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
<div class="breadcrumb"><div class="wrap"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ マッチングアプリの結婚率・公表データ早見表</div></div>
<main class="wrap">
%(body)s
<article>
<h2>よくある質問</h2>
%(faq)s
</article>
%(related)s
</main>
%(footer)s
""" % dict(gtag=gtag, title=TITLE, desc=DESC, url=URL, style=style, ld=lds, header=header, body=body, faq=faq_html, related=related, footer=footer)
    os.makedirs(OUT_DIR, exist_ok=True)
    p = os.path.join(OUT_DIR, "index.html")
    open(p, "w", encoding="utf-8").write(html)
    h = open(p, encoding="utf-8").read()
    types = []
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        d = json.loads(b); types.append(d.get("@type"))
        if "kekkon-shikin" in json.dumps(d): raise SystemExit("テンプレ由来のLD混入")
    assert len(types) == len(set(types)), types
    print("built:", p, "| ld:", types, "| bytes:", len(h))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""マッチングアプリの料金の器具とデータ記事を生成する（2026-08-27 新設）

狙う語は「マッチングアプリ 料金」「ペアーズ 料金」「アプリ 課金 高い」。
成婚率・結婚相談所費用と同じ婚活クラスタ。

SERP1ページ目は比較メディアの料金表ばかりで、どれも「Webとアプリ内課金の差」を
主題にしていない。ところが実査すると、決済方法別の金額を公開している5社すべてで
アプリ内課金のほうが高く、12か月では最大5,800円の差があった。
**読者が今日から動かせる数字はここだけ**（乗り換えも解約も要らない。契約する場所を変えるだけ）。

実査で分かった核（2026-08-27・8社）:
- 決済方法別の金額を公開している5社すべてでアプリ内課金が高い
  ブライダルネット5,800円／タップル5,200円／マリッシュ2,600円／ペアーズ2,300円／Omiai2,000円（12か月）
- Omiaiには「決済方法によって料金が異なる理由」という専用ヘルプ記事がある＝会社も公式に説明している
- **withとユーブライドは「決済方法で料金が異なる」と明記しながら差額を公開していない**
  （差が無いのではなく分からない）
- **withの料金表はPNG画像**。通常のページ取得では数値が取れない
- Tinderは固定の月額プラン価格表を自社サイトで公開していない
- 「女性無料」の中身も社で違う（withは女性向けVIPオプションが別課金、タップルはプラン単位）
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_shell import SRC_INTRO_KIGYO, faq_html, source_list, table, write
from _app_ryokin_data import APPS, CHECKED, SOURCES, UNCONFIRMED

TODAY = "2026-08-27"
TOOL_SLUG = "app-kakin-hikaku"
ART_SLUG = "app-ryokin-data"
TOOL_URL = "https://www.noe-match.com/tools/%s/" % TOOL_SLUG

AFF = "https://px.a8.net/svt/ejp?a8mat=4B8B4Q+2VLJWA+1PJA+2BJRBL"
AFF_TEXT = "結婚相談所比較ネットで資料を取り寄せる"
AFF_NOTE = "無料の一括資料請求サービスです。成婚率や結果を保証するものではありません"
AFF_COLOR = "#7c5cbf"

N = len(APPS)
DIFF = [a for a in APPS if a["differs"] == "differs"]
UNKNOWN = [a for a in APPS if a["differs"] == "unknown"]
NOPRICE = [a for a in APPS if a["differs"] == "unconfirmed"]
DIFF_SORTED = sorted(DIFF, key=lambda a: -(a["app"][12] - a["web"][12]))
MAXA = DIFF_SORTED[0]
MAXDIFF = MAXA["app"][12] - MAXA["web"][12]
MINDIFF = DIFF_SORTED[-1]["app"][12] - DIFF_SORTED[-1]["web"][12]

# 決済方法別を公開している社は、全社アプリ内課金のほうが高い。
# ここが崩れたら記事の主張が変わるので、生成前に確かめる。
assert all(a["app"][12] > a["web"][12] for a in DIFF), \
    "アプリ内課金のほうが安い社が出た。記事の主張を作り直すこと"


def y(n):
    return "{:,}".format(n)


# ============================================================ 器具
def build_tool():
    shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
    CSS = shell[shell.find("<style>"):shell.find("</style>") + 8]

    TITLE = ("マッチングアプリはWebとアプリ内課金でいくら違う？%d社の料金を比べる【%s確認】"
             % (N, CHECKED))
    H1 = "同じアプリなのに、契約する場所で年%s円変わる｜%d社の課金先くらべ" % (y(MAXDIFF), N)
    DESC = ("マッチングアプリ%d社の公式料金ページを一次確認しました。決済方法別の金額を公開している"
            "%d社すべてで、iPhone・Androidのアプリ内課金がWeb契約より高くなっています。"
            "12か月プランの差は%s（%s円）から%s（%s円）まで。Omiaiには「決済方法によって料金が異なる理由」"
            "という専用のヘルプ記事があり、会社側も公式に説明しています。アプリと期間を選ぶと差額が出ます。"
            % (N, len(DIFF), MAXA["name"], y(MAXDIFF),
               DIFF_SORTED[-1]["name"], y(MINDIFF)))
    OGD = ("乗り換えも解約も要りません。契約する場所を変えるだけで、12か月で最大%s円変わります。"
           % y(MAXDIFF))

    FAQ = [
     ("マッチングアプリはWebとアプリ内課金でどのくらい違いますか？",
      "決済方法別の金額を公開している%d社すべてで、アプリ内課金のほうが高くなっています。"
      "12か月プランの差は%s（%s円）、%s（%s円）、%s（%s円）、%s（%s円）、%s（%s円）でした。"
      "%s現在の各社公式ページの記載にもとづきます。"
      % (len(DIFF),
         DIFF_SORTED[0]["name"], y(DIFF_SORTED[0]["app"][12] - DIFF_SORTED[0]["web"][12]),
         DIFF_SORTED[1]["name"], y(DIFF_SORTED[1]["app"][12] - DIFF_SORTED[1]["web"][12]),
         DIFF_SORTED[2]["name"], y(DIFF_SORTED[2]["app"][12] - DIFF_SORTED[2]["web"][12]),
         DIFF_SORTED[3]["name"], y(DIFF_SORTED[3]["app"][12] - DIFF_SORTED[3]["web"][12]),
         DIFF_SORTED[4]["name"], y(DIFF_SORTED[4]["app"][12] - DIFF_SORTED[4]["web"][12]),
         CHECKED)),
     ("なぜ課金する場所で料金が違うのですか？",
      "AppleとGoogleがアプリ内で行われる課金に手数料をかけるためです。その分が価格に乗ります。"
      "Omiaiは「決済方法によって料金が異なる理由」という専用のヘルプ記事でこれを説明しており、"
      "会社側が隠しているというより、気づきにくい場所に置かれている情報です。"),
     ("どうすれば安いほうで契約できますか？",
      "スマートフォンのブラウザでその会社の公式サイトを開き、そこで契約します。"
      "アプリはそのまま使えますし、乗り換えも退会も必要ありません。"
      "すでにアプリ内課金で契約している場合は、いったん自動更新を止めてから期限後にWebで"
      "契約し直すことになるため、更新日の前に確認してください。"),
     ("差額を公開していないアプリはありますか？",
      "%d社（%s）は「決済方法によって料金が異なる」と明記しながら、具体的な差額を公開していません。"
      "ユーブライドは「AppleID決済・Google Play決済の場合、Apple社・Google社の規定により料金が"
      "異なります」と書くだけで金額を示していません。<strong>差が無いのではなく、"
      "いくら違うかが分からない状態です。</strong>契約前にブラウザとアプリの両方で金額を"
      "見比べてください。"
      % (len(UNKNOWN), "・".join(a["name"] for a in UNKNOWN))),
     ("女性は本当に無料ですか？",
      "「無料」の範囲が社によって違います。ペアーズとマリッシュはメッセージの送受信まで無料と"
      "読める書き方です。withは基本無料としながら女性向けの「VIPオプション」「ロイヤルVIPオプション」"
      "という別建ての有料課金があります。タップルは「シンプルプラン」の範囲だけが無料で、"
      "「スタンダードプラン」は女性も有料です。ユーブライドとブライダルネットは男女同額で、"
      "そもそも女性無料のモデルではありません。"),
     ("Tinderの料金が載っていないのはなぜですか？",
      "Tinderは他の7社と違い、固定の月額プラン価格表を自社サイトで公開していないためです。"
      "App Storeの課金項目にも、期間と金額が一意に対応する形では出ていませんでした。"
      "推測で数字を出すことはしないため、本ツールでは「未確認」としています。"),
     ("この情報はいつのものですか？",
      "%sに%d社の公式ページを確認した内容です。料金は改定されるため、契約前に必ず各社の"
      "公式ページでご確認ください。本ツールには各社の出典リンクを載せています。" % (CHECKED, N)),
    ]

    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in FAQ]}, ensure_ascii=False)
    app_ld = json.dumps({
        "@context": "https://schema.org", "@type": "WebApplication",
        "name": "マッチングアプリの課金先くらべ", "url": TOOL_URL,
        "applicationCategory": "FinanceApplication", "operatingSystem": "All",
        "inLanguage": "ja", "description": DESC,
        "datePublished": TODAY, "dateModified": TODAY,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
        "publisher": {"@type": "Organization", "name": "Noe結婚設計室",
                      "url": "https://www.noe-match.com/"}}, ensure_ascii=False)
    bc_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                        "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
        {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": "https://www.noe-match.com/#tools"},
        {"@type": "ListItem", "position": 3, "name": "マッチングアプリの課金先くらべ"}]}, ensure_ascii=False)

    opts = "".join('<option value="%s">%s</option>' % (a["key"], a["name"]) for a in APPS)
    rows = "".join(
        '<tr><td><strong>%s</strong></td><td class="num">%s円%s</td><td class="num">%s円%s</td>'
        '<td class="num"><strong>%s円%s</strong></td></tr>'
        % (a["name"], y(a["web"][12]), "〜" if a["approx"] else "",
           y(a["app"][12]), "〜" if a["approx"] else "",
           y(a["app"][12] - a["web"][12]), "〜" if a["approx"] else "")
        for a in DIFF_SORTED)
    josei_rows = "".join(
        '<tr><td><strong>%s</strong></td><td>%s</td></tr>' % (a["name"], a["female"] or "記載なし")
        for a in APPS)
    src_rows = "".join(
        '<tr><td><a href="%s" rel="noopener" target="_blank">%s</a></td><td>%s</td></tr>'
        % (u, l, CHECKED) for u, l in SOURCES)
    faq_html_s = "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a)
                           for i, (q, a) in enumerate(FAQ))
    DATA = json.dumps({a["key"]: a for a in APPS}, ensure_ascii=False, separators=(",", ":"))

    tpl = io.open("scripts/_app_ryokin_body.html", encoding="utf-8").read()
    html = (tpl.replace("__TITLE__", TITLE).replace("__DESC__", DESC).replace("__OGD__", OGD)
            .replace("__URL__", TOOL_URL).replace("__H1__", H1).replace("__CSS__", CSS)
            .replace("__FAQLD__", faq_ld).replace("__APPLD__", app_ld).replace("__BCLD__", bc_ld)
            .replace("__OPTS__", opts).replace("__ROWS__", rows)
            .replace("__JOSEIROWS__", josei_rows).replace("__SRCROWS__", src_rows)
            .replace("__FAQHTML__", faq_html_s).replace("__DATA__", DATA)
            .replace("__SLUG__", TOOL_SLUG).replace("__CHECKED__", CHECKED)
            .replace("__MAXNAME__", MAXA["name"])
            .replace("__MAXWEB__", y(MAXA["web"][12])).replace("__MAXAPP__", y(MAXA["app"][12]))
            .replace("__MAXDIFF__", y(MAXDIFF))
            .replace("__NDIFF__", str(len(DIFF))).replace("__NOTHER__", str(len(UNKNOWN)))
            .replace("__AFFTEXT__", AFF_TEXT).replace("__AFF__", AFF)
            .replace("__N__", str(N)))
    os.makedirs("tools/%s" % TOOL_SLUG, exist_ok=True)
    io.open("tools/%s/index.html" % TOOL_SLUG, "w", encoding="utf-8").write(html)
    print("written: tools/%s/index.html  %d chars" % (TOOL_SLUG, len(html)))


# ============================================================ 記事
FAQ_ART = [
 ("マッチングアプリの料金は課金する場所で変わりますか？",
  "変わります。決済方法別の金額を公開している%d社すべてで、iPhone・Androidのアプリ内課金が"
  "Web契約より高くなっています。12か月プランでは%sが%s円、%sが%s円の差でした。"
  % (len(DIFF), DIFF_SORTED[0]["name"], y(MAXDIFF),
     DIFF_SORTED[1]["name"], y(DIFF_SORTED[1]["app"][12] - DIFF_SORTED[1]["web"][12]))),
 ("なぜアプリ内課金のほうが高いのですか？",
  "AppleとGoogleがアプリ内の課金に手数料をかけるためです。Omiaiは「決済方法によって料金が"
  "異なる理由」という専用のヘルプ記事でこれを説明しています。会社が隠しているというより、"
  "気づきにくい場所に置かれている情報です。"),
 ("安く契約するにはどうすればいいですか？",
  "スマートフォンのブラウザで公式サイトを開き、そこで契約します。アプリはそのまま使えますし、"
  "乗り換えも退会も必要ありません。すでにアプリ内課金で契約している場合は、自動更新を止めてから"
  "期限後にWebで契約し直すことになるため、更新日の前に確認してください。"),
 ("差額を公開していないアプリはどれですか？",
  "%s の%d社です。どちらも「決済方法によって料金が異なる」と明記しながら、"
  "具体的な金額を出していません。差が無いのではなく、いくら違うかが分からない状態です。"
  % ("・".join(a["name"] for a in UNKNOWN), len(UNKNOWN))),
 ("女性は完全に無料ですか？",
  "「無料」の範囲が社で違います。ペアーズとマリッシュはメッセージ送受信まで無料と読める書き方、"
  "withは基本無料としながら女性向けVIPオプションが別建ての有料、タップルは「シンプルプラン」の"
  "範囲だけが無料で「スタンダードプラン」は女性も有料です。ユーブライドとブライダルネットは"
  "男女同額です。"),
 ("比較サイトの料金と違うのはなぜですか？",
  "決済方法のどちらを載せているかで金額が変わります。加えてwithの料金表は公式ページ上で"
  "PNG画像として置かれており、通常のページ取得では数値が取れません。"
  "自動で情報を集めているサイトの数字がずれたり古かったりする一因はここにあります。"),
 ("この金額はそのまま信じてよいですか？",
  "各社の公式ページに出ている男性有料プランの金額です。タップル・with・ユーブライドは"
  "「3,700円〜」のような下限表記なので、実際にはこれより高くなる場合があります。"
  "ペアーズの料金ページには税込・税別の明記がありません。本記事は各社の表示をそのまま使い、"
  "換算も丸めもしていません。"),
]


def build_article():
    p = []
    p.append(
        "<blockquote><strong>アプリを消す必要も、別のアプリに乗り換える必要もありません。"
        "契約する場所を変えるだけで、年に数千円変わります。</strong>"
        "%sに%d社の公式料金ページを確認したところ、決済方法別の金額を公開している%d社の"
        "<strong>すべてで、iPhone・Androidのアプリ内課金がWeb契約より高く</strong>なっていました。"
        "12か月プランの差は%sの%s円が最大です。Omiaiには「決済方法によって料金が異なる理由」という"
        "専用のヘルプ記事があり、会社の側もこの差を公式に説明しています。</blockquote>"
        % (CHECKED, N, len(DIFF), MAXA["name"], y(MAXDIFF)))

    p.append('<h2 id="sa">12か月プランの差額</h2>')
    p.append("<p>男性の有料プランで、Webで契約した場合とアプリ内で課金した場合を並べました。"
             "「〜」は原文が下限額で書かれている社です。</p>")
    p.append(table(["アプリ", "Webで契約", "アプリ内で課金", "差"],
                   [(a["name"],
                     "%s円%s" % (y(a["web"][12]), "〜" if a["approx"] else ""),
                     "%s円%s" % (y(a["app"][12]), "〜" if a["approx"] else ""),
                     "<strong>%s円%s</strong>" % (y(a["app"][12] - a["web"][12]),
                                                  "〜" if a["approx"] else ""))
                    for a in DIFF_SORTED], ["", "", "", ""]))
    p.append("<p>差は最小でも%s円（%s）です。婚活が長引いて2年続ければ、その倍になります。</p>"
             % (y(MINDIFF), DIFF_SORTED[-1]["name"]))

    p.append('<h2 id="kikan">期間ごとの金額</h2>')
    p.append("<p>期間が長いほど月あたりは安くなりますが、差額そのものは大きくなります。</p>")
    for a in DIFF_SORTED:
        terms = sorted(set(list(a["web"].keys()) + list(a["app"].keys())))
        p.append("<h3>%s</h3>" % a["name"])
        p.append(table(["期間", "Webで契約", "アプリ内で課金", "差"],
                       [("%dか月" % t,
                         "%s円%s" % (y(a["web"][t]), "〜" if a["approx"] else "") if t in a["web"] else "―",
                         "%s円%s" % (y(a["app"][t]), "〜" if a["approx"] else "") if t in a["app"] else "―",
                         "%s円%s" % (y(a["app"][t] - a["web"][t]), "〜" if a["approx"] else "")
                         if (t in a["web"] and t in a["app"]) else "―")
                        for t in terms], ["", "", "", ""]))

    p.append('<h2 id="naze">なぜ差がつくのか</h2>')
    p.append("<p>AppleとGoogleは、アプリ内で行われる課金に手数料をかけます。その分が価格に乗るため、"
             "同じサービスでもアプリの中で契約するほうが高くなります。"
             "Omiaiはこれを「決済方法によって料金が異なる理由」という専用のヘルプ記事で説明しており、"
             "<strong>会社側が隠しているというより、気づかない場所に置かれている情報です。</strong></p>")
    p.append("<p>避け方は単純です。<strong>スマートフォンのブラウザでその会社の公式サイトを開き、"
             "そこで契約する</strong>。アプリはそのまま使えますし、退会も乗り換えも要りません。"
             "すでにアプリ内課金で契約している場合は、いったん自動更新を止めてから期限後にWebで"
             "契約し直すことになるため、更新日の前に確認してください。</p>")

    p.append('<h2 id="hikohyo">差額を公開していない%d社</h2>' % len(UNKNOWN))
    p.append("<p>ここが本記事でいちばん注意してほしいところです。%s は"
             "「決済方法によって料金が異なる」と明記しながら、<strong>いくら違うかを公開していません</strong>。</p>"
             % "・".join(a["name"] for a in UNKNOWN))
    p.append(table(["アプリ", "会社の記載（原文）", "公式ページに出ている12か月の金額"],
                   [(a["name"], a["differs_note"] or "記載なし",
                     "%s円%s" % (y(a["single"][12]), "〜" if a["approx"] else "")
                     if a.get("single") and 12 in a["single"] else "―")
                    for a in UNKNOWN], ["", "", ""]))
    p.append("<p>公式ページに出ている金額が、Webとアプリ内課金のどちらのものかも書かれていません。"
             "<strong>差が無いのではなく、分からない状態です。</strong>"
             "この2社を検討している場合は、契約の前にブラウザとアプリの両方で表示される金額を"
             "実際に見比べてください。</p>")

    p.append('<h2 id="josei">「女性無料」の中身も同じではない</h2>')
    p.append("<p>女性無料と書かれていても、範囲は社によって違います。原文のまま並べます。</p>")
    p.append(table(["アプリ", "女性の料金（原文）"],
                   [(a["name"], a["female"] or "記載なし") for a in APPS], ["", ""]))
    p.append("<p>整理すると次の3つに分かれます。メッセージの送受信まで無料の社（ペアーズ・マリッシュ）、"
             "無料の中に別建ての有料オプションがある社（with）、"
             "無料の範囲がプラン単位で区切られている社（タップル）。"
             "ユーブライドとブライダルネットは男女同額で、そもそも女性無料のモデルではありません。</p>")

    p.append('<h2 id="chui">料金を調べるときに気をつけること</h2>')
    p.append("<h3>withの料金表はテキストではなく画像</h3>")
    p.append("<p>withの料金は公式ページ上でPNG画像として置かれており、通常のページ取得では数値が"
             "一切とれません。本記事では公式CDNから画像を取得して読み取りました。"
             "<strong>自動で情報を集めている比較サイトの数字がずれたり古かったりする一因は、"
             "こうした構造にあります。</strong></p>")
    p.append("<h3>「〜」表記は下限額</h3>")
    p.append("<p>タップル・with・ユーブライドの料金は「3,700円〜」のように下限で書かれています。"
             "実際にはこれより高くなる場合があります。本記事もその表記をそのまま使い、丸めていません。</p>")
    p.append("<h3>Tinderは料金表を公開していない</h3>")
    p.append("<p>Tinderは他の7社と違い、固定の月額プラン価格表を自社サイトで公開していません。"
             "App Storeの課金項目にも期間と金額が一意に対応する形では出ていないため、"
             "本記事では金額を出していません。金額を書いている比較サイトがあれば、"
             "その根拠を確かめてください。</p>")
    p.append("<h3>税込か税別かの明記が無い社がある</h3>")
    p.append("<p>ペアーズの料金ページには税込・税別の明記がなく、"
             "「記載されている料金は通常料金です」とあるだけです。"
             "本記事は各社が表示している数値をそのまま使っており、換算していません。</p>")

    p.append('<h2 id="tool">自分のアプリと期間で差額を出す</h2>')
    p.append('<p>アプリと契約期間を選ぶと、Webとアプリ内課金の金額と差額が出ます。'
             '無料の範囲・女性の料金・自動更新の扱いも出典つきで表示します。<br>'
             '<a href="/tools/app-kakin-hikaku/">マッチングアプリの課金先くらべ（無料）</a></p>')

    p.append('<h2 id="miconfirm">今回確認できなかったこと</h2>')
    p.append("<p>調べたが取れなかったものを、理由とともに書いておきます。</p>")
    p.append("<ul>%s</ul>" % "".join(
        "<li><strong>%s</strong>｜%s</li>" % (a, b) for a, b in UNCONFIRMED))

    p.append("""
<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/tools/app-kakin-hikaku/">マッチングアプリの課金先くらべ｜Webとアプリ内課金の差</a></li>
<li><a href="/articles/soudanjo-hiyou-data/">結婚相談所の総額はいくら？10社を同じ条件で積むと7.1倍差がついた</a></li>
<li><a href="/articles/seikonritsu-data/">成婚率はなぜ社によって3倍違うのか｜16社の分母と分子を並べた</a></li>
<li><a href="/articles/agency-vs-app/">結婚相談所とマッチングアプリはどちらを使うべきか</a></li>
</ul>""")
    p.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    p.append(faq_html(FAQ_ART))
    p.append(source_list([(u, l) for u, l in SOURCES], SRC_INTRO_KIGYO))

    write(ART_SLUG,
          "マッチングアプリの料金は課金する場所で変わる｜%d社のWebとアプリ内課金の差【%s確認】"
          % (N, CHECKED),
          "マッチングアプリの料金は課金先で変わる｜Webとアプリ内課金の差を%d社で調べた" % N,
          "マッチングアプリ%d社の公式料金ページを一次確認しました。決済方法別の金額を公開している"
          "%d社すべてで、iPhone・Androidのアプリ内課金がWeb契約より高くなっています。"
          "12か月プランの差は%sの%s円が最大で、最小でも%s円です。"
          "%d社は「決済方法で料金が異なる」と明記しながら差額を公開していません。"
          "乗り換えも解約も不要で、ブラウザで契約するだけで避けられます。確認日は%s。"
          % (N, len(DIFF), MAXA["name"], y(MAXDIFF), y(MINDIFF), len(UNKNOWN), CHECKED),
          "乗り換えも解約も要りません。契約する場所を変えるだけで、12か月で最大%s円変わります。"
          % y(MAXDIFF),
          FAQ_ART, "\n".join(p), TODAY, CHECKED,
          "アプリで決まらないまま課金を続けているなら",
          "アプリの料金は月あたりで見ると小さく見えますが、12か月契約を2年続ければ4〜6万円になります。"
          "同じ金額を別の方法に使う選択肢もあります。結婚相談所は総額が大きいぶん、"
          "会員データと費用を先に並べて見ておくと判断しやすくなります。",
          aff_url=AFF, aff_text=AFF_TEXT, aff_note=AFF_NOTE, aff_color=AFF_COLOR,
          aff_rel="nofollow sponsored noopener")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build_tool()
    build_article()
    print("差を公開 %d社（最大%s円＝%s／最小%s円）／内訳非公開 %d社／価格表なし %d社"
          % (len(DIFF), y(MAXDIFF), MAXA["name"], y(MINDIFF), len(UNKNOWN), len(NOPRICE)))

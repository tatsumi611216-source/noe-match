# -*- coding: utf-8 -*-
"""結婚相談所の費用の器具とデータ記事を生成する（2026-08-27 新設）

狙う語は「結婚相談所 費用」「結婚相談所 料金 比較」。
成婚率バンクと同じ婚活クラスタで、単価が最も高い案件帯
（結婚相談所比較ネット＝資料請求3,800円・確定率81.6%）と重なる。

SERP1ページ目は比較メディアの料金表ばかりだが、**どれも総額を出していない**。
各社が項目別の金額しか公表していないためで、10社中8社は自社でも総額を出していない。
総額を同じ条件で積むのが器具の役割。

実査で分かった核（2026-08-27・10社）:
- 12か月活動して成婚した場合の総額は125,400円〜891,000円で7.1倍差
- **差の大半をつくるのは月会費ではなく成婚料**（0円〜330,000円）
- 成婚料は成婚したときにしか発生しないので、月々の料金表を見ている間は目に入らない
- ツヴァイとオーネットは「同じ相談所の会員同士なら0円／連盟会員となら220,000円」
- **「お見合い料0円と明記」と「お見合い料の項目が料金表に無い」は別物**（5社が後者）

数値は _soudanjo_hiyou_data.py から引く。正本の生成時に、自社で12か月総額を
公表している2社（ツヴァイ310,200円・スマリッジ125,400円）と突き合わせて検算している。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_shell import SRC_INTRO_KIGYO, faq_html, source_list, table, write
from _soudanjo_hiyou_data import CHECKED, COMPANIES, UNCONFIRMED

TODAY = "2026-08-27"
TOOL_SLUG = "soudanjo-hiyou-sim"
ART_SLUG = "soudanjo-hiyou-data"
TOOL_URL = "https://www.noe-match.com/tools/%s/" % TOOL_SLUG

# 結婚相談所比較ネット（A8・じげん）。案件台帳の許可文脈「結婚相談所の比較・検討」。
AFF = "https://px.a8.net/svt/ejp?a8mat=4B8B4Q+2VLJWA+1PJA+2BJRBL"
AFF_TEXT = "結婚相談所比較ネットで資料を取り寄せる"
AFF_NOTE = "無料の一括資料請求サービスです。成婚率や結果を保証するものではありません"
AFF_COLOR = "#7c5cbf"

N = len(COMPANIES)
NO_OMIAI = [c for c in COMPANIES if c["omiai"] is None]
SEIKON0 = [c for c in COMPANIES if c["seikon"] == 0]
KOHYO = [c for c in COMPANIES if c["nenkan_sogaku_kohyo"]]
NNOSOGAKU = N - len(KOHYO)


def total(c, months=12, omiai_n=0, with_seikon=True, renmei=False):
    """公表されている項目だけを積む。お見合い料の項目が無い社は積まない（0円扱いにしない）。"""
    t = c["init"] + c["month"] * months
    if c["omiai"] is not None:
        t += c["omiai"] * omiai_n
    if with_seikon:
        s = c["seikon_renmei"] if renmei else c["seikon"]
        if s is not None:
            t += s
    return t


RANKED = sorted(COMPANIES, key=total)
MINC, MAXC = RANKED[0], RANKED[-1]
MIN, MAX = total(MINC), total(MAXC)
RATIO = MAX / float(MIN)
# 成婚料を含めない場合の総額。差が成婚料由来であることを示すための比較。
RANKED_NS = sorted(COMPANIES, key=lambda c: total(c, with_seikon=False))
MIN_NS = total(RANKED_NS[0], with_seikon=False)
MAX_NS = total(RANKED_NS[-1], with_seikon=False)
RATIO_NS = MAX_NS / float(MIN_NS)

# 正本の検算が通っていることを、生成側でももう一度確かめる。
_zwei = [c for c in COMPANIES if c["key"] == "zwei"][0]
_sma = [c for c in COMPANIES if c["key"] == "smarriage"][0]
assert _zwei["init"] + _zwei["month"] * 12 == 310200, "ツヴァイの12か月総額が公表値と合わない"
assert _sma["init"] + _sma["month"] * 12 == 125400, "スマリッジの年間活動費が公表値と合わない"


def y(n):
    return "{:,}".format(n)


# ============================================================ 器具
def build_tool():
    shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
    CSS = shell[shell.find("<style>"):shell.find("</style>") + 8]

    TITLE = ("結婚相談所の費用は総額いくら？%d社を同じ条件で積むシミュレーション【%s確認】"
             % (N, CHECKED))
    H1 = "結婚相談所の総額はいくら？｜%d社を同じ条件で積んで並べる" % N
    DESC = ("結婚相談所%d社の公式料金ページを一次確認しました。12か月活動して成婚した場合の総額は"
            "%s円（%s）から%s円（%s）まで%.1f倍開きます。差の大半をつくっているのは月会費ではなく"
            "成婚料で、0円の社と330,000円の社があります。%d社は自社で1年間の総額を公表していません。"
            "活動する月数とお見合いの回数を入れると、%d社の総額を同じ条件で積んで安い順に並べます。"
            % (N, y(MIN), MINC["name"], y(MAX), MAXC["name"], RATIO, NNOSOGAKU, N))
    OGD = ("12か月で成婚した場合の総額は%s円〜%s円で%.1f倍差。差をつくっているのは月会費ではなく成婚料です。"
           % (y(MIN), y(MAX), RATIO))

    FAQ = [
     ("結婚相談所の費用は総額でいくらですか？",
      "12か月活動して成婚退会した場合、%d社の公表項目を積むと%s円（%s）から%s円（%s）まで、"
      "%.1f倍開きます。入会金・月会費・成婚料の合計で、オプション費用や更新料は含んでいません。"
      "%s現在の各社公式ページの記載にもとづきます。"
      % (N, y(MIN), MINC["name"], y(MAX), MAXC["name"], RATIO, CHECKED)),
     ("いちばん費用の差をつくっているのはどこですか？",
      "成婚料です。成婚料を含めずに12か月ぶんを積むと総額の開きは%.1f倍（%s円〜%s円）ですが、"
      "成婚料を含めると%.1f倍（%s円〜%s円）に広がります。成婚料は0円の社と330,000円の社があり、"
      "成婚したときにしか発生しないため、月々の料金表を見比べているあいだは目に入りません。"
      % (RATIO_NS, y(MIN_NS), y(MAX_NS), RATIO, y(MIN), y(MAX))),
     ("成婚料が0円の相談所はどこですか？",
      "%s現在で%s（%d社）です。ただし「成婚料0円だから安い」とは単純に言えません。"
      "ツヴァイは同じ相談所の会員同士なら0円ですが、IBJ連盟の会員と成婚した場合は220,000円かかります。"
      "オーネットも同じ構造で、オーネット会員同士なら0円、IBJ会員となら220,000円です。"
      % (CHECKED, "・".join(c["name"] for c in SEIKON0), len(SEIKON0))),
     ("お見合い料は必ずかかりますか？",
      "社によって扱いが違います。「お見合い料は0円」と明記している社がある一方、"
      "料金表にお見合い料という項目自体が無い社が%d社（%s）あります。"
      "<strong>項目が無いことは無料と明記されていることと同じではありません。</strong>"
      "本ツールは項目が無い社を0円として扱わず、お見合い料を合計に含めていません。"
      "無料カウンセリングで必ず確認してください。"
      % (len(NO_OMIAI), "・".join(c["name"] for c in NO_OMIAI))),
     ("この金額をそのまま予算にしてよいですか？",
      "目安としてお使いください。公表されている項目を足しただけの金額で、オプション費用・更新料・"
      "休会費・お見合いの追加料金は含んでいません。コースが複数ある社では1つのコースの金額を"
      "使っています。割引やキャンペーンも反映していません。契約前に必ず公式ページと契約書面で"
      "ご確認ください。"),
     ("会社は総額を公表していないのですか？",
      "%d社のうち総額を自社で公表しているのは%d社だけです（%s）。"
      "残りは入会金・月会費・成婚料が項目別に載っているだけなので、読者が自分で足し算しないと"
      "総額が出ません。本ツールはその足し算を代わりにやっています。"
      % (N, len(KOHYO), "・".join(c["name"] for c in KOHYO))),
     ("この情報はいつのものですか？",
      "%sに%d社の公式料金ページを確認した内容です。料金は改定されるため、契約前に必ず"
      "各社の公式ページでご確認ください。本ツールには各社の出典リンクを載せています。"
      % (CHECKED, N)),
    ]

    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in FAQ]}, ensure_ascii=False)
    app_ld = json.dumps({
        "@context": "https://schema.org", "@type": "WebApplication",
        "name": "結婚相談所の総額シミュレーション", "url": TOOL_URL,
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
        {"@type": "ListItem", "position": 3, "name": "結婚相談所の総額シミュレーション"}]}, ensure_ascii=False)

    rows = "".join(
        '<tr><td><strong>%s</strong></td><td class="num">%s円</td><td class="num">%s円</td>'
        '<td>%s</td><td class="num">%s</td></tr>'
        % (c["name"], y(c["init"]), y(c["month"]),
           ("項目なし" if c["omiai"] is None else ("0円" if c["omiai"] == 0 else y(c["omiai"]) + "円")),
           (y(c["seikon"]) + "円" if c["seikon"] is not None else "項目なし"))
        for c in sorted(COMPANIES, key=lambda c: (c["seikon"] or 0, c["init"])))
    src_rows = "".join(
        '<tr><td>%s</td><td><a href="%s" rel="noopener" target="_blank">%s</a></td><td>%s</td></tr>'
        % (c["name"], c["src"], c["src_label"], CHECKED) for c in COMPANIES)
    faq_html_s = "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a)
                           for i, (q, a) in enumerate(FAQ))
    DATA = json.dumps(COMPANIES, ensure_ascii=False, separators=(",", ":"))

    tpl = io.open("scripts/_soudanjo_body.html", encoding="utf-8").read()
    html = (tpl.replace("__TITLE__", TITLE).replace("__DESC__", DESC).replace("__OGD__", OGD)
            .replace("__URL__", TOOL_URL).replace("__H1__", H1).replace("__CSS__", CSS)
            .replace("__FAQLD__", faq_ld).replace("__APPLD__", app_ld).replace("__BCLD__", bc_ld)
            .replace("__ROWS__", rows).replace("__SRCROWS__", src_rows)
            .replace("__FAQHTML__", faq_html_s).replace("__DATA__", DATA)
            .replace("__SLUG__", TOOL_SLUG).replace("__CHECKED__", CHECKED)
            .replace("__MINNAME__", MINC["name"]).replace("__MAXNAME__", MAXC["name"])
            .replace("__MIN__", y(MIN)).replace("__MAX__", y(MAX))
            .replace("__RATIO__", "%.1f" % RATIO)
            .replace("__NNOSOGAKU__", str(NNOSOGAKU)).replace("__NKOHYO__", str(len(KOHYO)))
            .replace("__NSEIKON0__", str(len(SEIKON0)))
            .replace("__SEIKON0NAMES__", "・".join(c["name"] for c in SEIKON0))
            .replace("__AFFTEXT__", AFF_TEXT).replace("__AFF__", AFF)
            .replace("__N__", str(N)))
    os.makedirs("tools/%s" % TOOL_SLUG, exist_ok=True)
    io.open("tools/%s/index.html" % TOOL_SLUG, "w", encoding="utf-8").write(html)
    print("written: tools/%s/index.html  %d chars" % (TOOL_SLUG, len(html)))


# ============================================================ 記事
FAQ_ART = [
 ("結婚相談所は総額でいくらかかりますか？",
  "12か月活動して成婚退会した場合、%d社の公表項目を積むと%s円（%s）から%s円（%s）まで%.1f倍"
  "開きます。入会金・月会費・成婚料の合計で、オプション費用や更新料は含みません。"
  % (N, y(MIN), MINC["name"], y(MAX), MAXC["name"], RATIO)),
 ("月会費が安ければ総額も安いですか？",
  "そうとは限りません。成婚料を含めずに12か月ぶんを積むと総額の開きは%.1f倍ですが、"
  "成婚料を含めると%.1f倍に広がります。成婚料は0円から330,000円まであり、"
  "成婚したときにしか発生しないため月々の料金表には現れません。"
  % (RATIO_NS, RATIO)),
 ("成婚料が0円ならお得ですか？",
  "条件を確かめてください。ツヴァイは同じ相談所の会員同士なら成婚料0円ですが、"
  "IBJ連盟の会員と成婚した場合は220,000円かかります。オーネットも同じ構造です。"
  "IBJ連盟の会員数は10万人規模なので、実際にはIBJ会員と成婚する可能性が十分にあります。"
  "「成婚料0円」の但し書きを読んでいるかどうかで見込みが変わります。"),
 ("いちばん安いのはどこですか？",
  "12か月・成婚退会の条件では%sの%s円です。次いで%sの%s円でした。"
  "ただし安さは受けられるサポートの量と表裏なので、金額だけで選ぶものではありません。"
  "オンライン完結型は担当者との面談が少なく、自分で動く力が要ります。"
  % (MINC["name"], y(MIN), RANKED[1]["name"], y(total(RANKED[1])))),
 ("お見合い料はかかりますか？",
  "社によって扱いが違います。「お見合い料0円」と明記している社がある一方、"
  "料金表にお見合い料という項目自体が無い社が%d社（%s）あります。項目が無いことは"
  "無料と同じではないため、無料カウンセリングで必ず確認してください。"
  % (len(NO_OMIAI), "・".join(c["name"] for c in NO_OMIAI))),
 ("なぜ比較サイトに総額が載っていないのですか？",
  "%d社のうち総額を自社で公表しているのは%d社だけだからです。"
  "各社は入会金・月会費・お見合い料・成婚料を項目別に出しているので、"
  "そのまま転記すると項目別の表になります。総額を出すには足し算が要ります。"
  % (N, len(KOHYO))),
 ("この金額はそのまま信じてよいですか？",
  "公表されている項目を足しただけの目安です。オプション費用・更新料・休会費・"
  "お見合いの追加料金は含んでいません。コースが複数ある社では1つのコースの金額を使っています。"
  "本記事では計算に使った内訳をすべて出典つきで公開しているので、"
  "自分が検討しているコースの金額に置き換えて確かめてください。"),
]


def build_article():
    p = []
    p.append(
        "<blockquote><strong>「月会費が安いから、ここがいちばん安い」——結婚相談所ではこれが成り立ちません。</strong>"
        "%sに%d社の公式料金ページを確認し、12か月活動して成婚退会した場合の総額を同じ条件で積んだところ、"
        "%s円（%s）から%s円（%s）まで<strong>%.1f倍</strong>開きました。"
        "そしてこの差をつくっているのは月会費ではありません。<strong>成婚料です。</strong>"
        "0円の社と330,000円の社があり、成婚したときにしか発生しないので、"
        "月々の料金表を見比べているあいだは一度も目に入りません。</blockquote>"
        % (CHECKED, N, y(MIN), MINC["name"], y(MAX), MAXC["name"], RATIO))

    p.append('<h2 id="sogaku">12か月・成婚退会での総額</h2>')
    p.append("<p>各社が公表している入会金・初期費用・月会費・成婚料を、同じ条件で積みました。"
             "お見合い料は0回として計算しています（回数を入れた計算は"
             "<a href=\"/tools/soudanjo-hiyou-sim/\">総額シミュレーション</a>でできます）。</p>")
    p.append(table(["相談所", "入会金・初期費用", "月会費×12", "成婚料", "12か月の総額"],
                   [(c["name"], y(c["init"]) + "円", y(c["month"] * 12) + "円",
                     y(c["seikon"]) + "円" if c["seikon"] is not None else "項目なし",
                     "<strong>%s円</strong>" % y(total(c)))
                    for c in RANKED], ["", "", "", "", ""]))
    p.append("<p>使ったコースは社によって違います（複数コースがある社は1つを選んでいます）。"
             "どのコースかは記事末の内訳と、ツールの各社カードに明記しています。</p>")

    p.append('<h2 id="seikonryo">差の正体は成婚料</h2>')
    p.append("<p>同じ%d社を、成婚料を含めずに積み直すと開きが縮みます。</p>" % N)
    p.append(table(["条件", "いちばん安い", "いちばん高い", "開き"],
                   [("成婚料を含めない（12か月）",
                     "%s %s円" % (RANKED_NS[0]["name"], y(MIN_NS)),
                     "%s %s円" % (RANKED_NS[-1]["name"], y(MAX_NS)),
                     "%.1f倍" % RATIO_NS),
                    ("成婚料を含める（12か月・成婚退会）",
                     "%s %s円" % (MINC["name"], y(MIN)),
                     "%s %s円" % (MAXC["name"], y(MAX)),
                     "%.1f倍" % RATIO)], ["", "", "", ""]))
    p.append("<p>成婚料の額を並べると、そのまま総額の順番に近くなります。</p>")
    p.append(table(["成婚料", "相談所"],
                   [("0円", "・".join(c["name"] for c in COMPANIES if c["seikon"] == 0)),
                    ("110,000円", "・".join(c["name"] for c in COMPANIES if c["seikon"] == 110000)),
                    ("220,000円", "・".join(c["name"] for c in COMPANIES if c["seikon"] == 220000)),
                    ("330,000円", "・".join(c["name"] for c in COMPANIES if c["seikon"] == 330000))],
                   ["", ""]))

    p.append('<h2 id="zero">「成婚料0円」には但し書きがある</h2>')
    p.append("<p>成婚料が0円なのは%s（%d社）ですが、うち2社は条件付きです。</p>"
             % ("・".join(c["name"] for c in SEIKON0), len(SEIKON0)))
    p.append(table(["相談所", "成婚料の記載（原文）"],
                   [(c["name"], c["seikon_ryo"]) for c in COMPANIES
                    if c["key"] in ("zwei", "onet", "nacodo", "smarriage")], ["", ""]))
    p.append("<p><strong>ツヴァイとオーネットは、お相手が誰かで成婚料が変わります。</strong>"
             "同じ相談所の会員同士なら0円、IBJ連盟の会員と成婚した場合は220,000円です。"
             "IBJ連盟の登録会員数は10万人規模なので、連盟の会員と成婚する可能性は十分にあります。"
             "「成婚料0円」という見出しだけを見て予算を組むと、220,000円ぶん外します。"
             "ツールの「お相手が連盟（IBJ）会員だった場合で計算する」を切り替えると、"
             "この2社の順位が動くのが確認できます。</p>")

    p.append('<h2 id="omiai">「お見合い料0円」と「お見合い料の項目がない」は別</h2>')
    p.append("<p>ここは比較表がいちばん雑になるところです。%d社のうち、"
             "お見合い料を「0円」と明記しているのは%d社。残り%d社は料金表にお見合い料という"
             "項目自体がありません。</p>"
             % (N, N - len(NO_OMIAI), len(NO_OMIAI)))
    p.append(table(["扱い", "相談所", "原文"],
                   [("0円と明記", c["name"], c["omiai_ryo"])
                    for c in COMPANIES if c["omiai"] == 0]
                   + [("料金表に項目なし", c["name"], c["omiai_ryo"])
                      for c in NO_OMIAI]
                   + [("有料", c["name"], c["omiai_ryo"])
                      for c in COMPANIES if c["omiai"] not in (0, None)],
                   ["", "", ""]))
    p.append("<p>項目が無い社を「無料」として比較表に載せると、その社が実際にはお見合いのたびに"
             "費用を取っていた場合に読者が損をします。本記事も本ツールも、"
             "<strong>項目が無い社は0円として扱わず、お見合い料を合計に含めていません</strong>。"
             "無料カウンセリングで確認すべき項目として残しておいてください。</p>")

    p.append('<h2 id="kohyo">総額を出しているのは%d社だけ</h2>' % len(KOHYO))
    p.append("<p>比較サイトに総額が載っていないのは、書き手の怠慢というより、"
             "元になる数字が公表されていないからです。%d社のうち自社サイトで1年間の総額を"
             "公表しているのは%d社でした。</p>" % (N, len(KOHYO)))
    p.append(table(["相談所", "会社が公表している総額"],
                   [(c["name"], c["nenkan_sogaku_kohyo"]) for c in KOHYO], ["", ""]))
    p.append("<p>この2社の公表値は、本記事の積み方の検算にも使っています。"
             "ツヴァイは118,800円＋15,950円×12＝310,200円、"
             "スマリッジは6,600円＋9,900円×12＝125,400円で、どちらも公表値と一致しました。"
             "<strong>同じ積み方をしている他社の数字も、この2本が通ることで確かめられます。</strong>"
             "計算が合わなければ記事を生成しない仕組みにしています。</p>")

    p.append('<h2 id="chui">料金ページを読むときに気をつけること</h2>')
    p.append("<h3>コースが複数ある社は「どのコースか」で大きく変わる</h3>")
    p.append("<p>ムスベルは3コースで入会金が148,500円から451,000円まで開きます。"
             "フィオーレは3コース×複数プランで6種類、オーネットも3プランあります。"
             "「ムスベルは○○円」という書き方をしている比較記事があれば、"
             "どのコースの数字かを確かめてください。</p>")
    p.append("<h3>税込か税別かが揃っていない</h3>")
    p.append("<p>ほとんどの社が税込表記ですが、スマリッジは料金ページに税込・税別の明示が"
             "ありませんでした。naco-doも初期費用66,000円には税込の明記がある一方、"
             "月会費16,800円には税込表記が見当たりませんでした。"
             "本記事は各社が表示している数値をそのまま使っており、換算していません。</p>")
    p.append("<h3>料金がページを開いただけでは出てこない社がある</h3>")
    p.append("<p>naco-doの料金ページは、金額がJavaScriptで遅延描画される作りです。"
             "サーバーが返す生のHTMLには金額が一切含まれておらず、"
             "実際に画面をスクロールさせて初めて「66,000円」「16,800円」が描画されました。"
             "自動で情報を集めている比較サイトの数字がずれることがあるのは、こうした構造も一因です。</p>")
    p.append("<h3>キャンペーン価格と通常価格が併記されている</h3>")
    p.append("<p>フィオーレは「通常価格33,000円→フォーム予約割引16,500円」という二段表示が"
             "常設されています。エクセレンス青山も誕生月10%OFFなどのキャンペーンがあります。"
             "本記事は通常価格で計算しています。</p>")

    p.append('<h2 id="tool">自分の条件で積み直す</h2>')
    p.append('<p>活動する月数とお見合いの回数、成婚するかどうか、お相手が連盟会員かを入れると、'
             '%d社の総額を同じ条件で積んで安い順に並べます。内訳（入会金・月会費・お見合い料・成婚料）が'
             '色分けされたバーで見えるので、どこにお金がかかっているかが分かります。<br>'
             '<a href="/tools/soudanjo-hiyou-sim/">結婚相談所の総額シミュレーション（無料）</a></p>' % N)

    p.append('<h2 id="miconfirm">今回確認できなかったこと</h2>')
    p.append("<p>調べたが取れなかったものを、理由とともに書いておきます。</p>")
    p.append("<ul>%s</ul>" % "".join(
        "<li><strong>%s</strong>｜%s</li>" % (a, b) for a, b in UNCONFIRMED))

    p.append("""
<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/tools/soudanjo-hiyou-sim/">結婚相談所の総額シミュレーション｜10社を同じ条件で積む</a></li>
<li><a href="/articles/seikonritsu-data/">成婚率はなぜ社によって3倍違うのか｜16社の分母と分子を並べた</a></li>
<li><a href="/tools/seikonritsu-hikaku/">その成婚率、同じ式で計算されていますか</a></li>
<li><a href="/articles/shougai-mikonritsu-data/">生涯未婚率はいま何%？男女別・年代別の推移</a></li>
<li><a href="/articles/soudanjo-hikaku/">結婚相談所の選び方｜タイプ別の違いと向き不向き</a></li>
<li><a href="/articles/agency-vs-app/">結婚相談所とマッチングアプリはどちらを使うべきか</a></li>
</ul>""")
    p.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    p.append(faq_html(FAQ_ART))
    p.append(source_list([(c["src"], "%s｜%s" % (c["name"], c["src_label"]))
                          for c in COMPANIES], SRC_INTRO_KIGYO))

    write(ART_SLUG,
          "結婚相談所の総額はいくら？%d社を同じ条件で積むと%.1f倍差がついた【%s確認】"
          % (N, RATIO, CHECKED),
          "結婚相談所の総額はいくら？%d社を同じ条件で積むと%.1f倍差がついた" % (N, RATIO),
          "結婚相談所%d社の公式料金ページを一次確認し、12か月活動して成婚退会した場合の総額を"
          "同じ条件で積みました。%s円（%s）から%s円（%s）まで%.1f倍開きます。"
          "差をつくっているのは月会費ではなく成婚料で、0円の社と330,000円の社があります。"
          "ただし「成婚料0円」には但し書きがあり、ツヴァイとオーネットは連盟会員と成婚した場合は"
          "220,000円かかります。%d社は自社で総額を公表していません。確認日は%s。"
          % (N, y(MIN), MINC["name"], y(MAX), MAXC["name"], RATIO, NNOSOGAKU, CHECKED),
          "12か月で成婚した場合の総額は%s円〜%s円で%.1f倍差。差の正体は月会費ではなく成婚料です。"
          % (y(MIN), y(MAX), RATIO),
          FAQ_ART, "\n".join(p), TODAY, CHECKED,
          "総額と会員データは、資料を取り寄せると並べて見られる",
          "本記事の金額は公式ページに載っている項目を足したものです。実際に自分がいくら払うかは、"
          "選ぶコース・活動期間・オプションで変わります。複数社の資料をまとめて取り寄せると、"
          "総額の内訳と、自分の年齢・地域にどんな会員がいるかを並べて確認できます。",
          aff_url=AFF, aff_text=AFF_TEXT, aff_note=AFF_NOTE, aff_color=AFF_COLOR,
          aff_rel="nofollow sponsored noopener")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build_tool()
    build_article()
    print("12か月・成婚退会: %s円（%s）〜 %s円（%s）＝%.1f倍 ／ 成婚料なしだと%.1f倍"
          % (y(MIN), MINC["name"], y(MAX), MAXC["name"], RATIO, RATIO_NS))

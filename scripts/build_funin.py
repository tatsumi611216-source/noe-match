# -*- coding: utf-8 -*-
"""不妊治療の区独自助成（東京23区）の器具とデータ記事を生成する（2026-08-27 新設）

狙う語は「不妊治療 助成 東京」「先進医療 助成 区」。
子ども医療費助成（対象年齢が23区同一）や病児保育（23区すべて実施）と違い、
**そもそも実施しているかどうかで割れる**のがこのバンクの核。

実査で分かった核（2026-08-27・23区）:
- 実施17区・未実施6区（新宿・墨田・世田谷・豊島・板橋・江戸川）
- 上限額は5万円が13区、10万円が3区（中央・文京・渋谷）、港区だけ30万円
- **ただし上限額の単純比較は成立しない。対象にしている費用の範囲が違う**
  - 12区は「保険診療と併用した先進医療」のみが対象（＝都の助成の差額補填）
  - 港区・文京区は自由診療まで対象に含めるので上限が大きい
  - 中央区・渋谷区は保険診療の自己負担分そのものも対象
  - **品川区は逆で、「保険適用の自己負担分のみ」が対象、先進医療と自由診療は対象外と明記**
    → 同じ「5万円」でも練馬区とは対象が正反対

助成額の計算式は区ごとに違い（練馬区は「先進医療費の7割−都の上限15万円」と
「区の上限5万円」の低い方）、全区ぶんは取れていない。**器具では助成額を計算しない**。

funin_range は原文から読み取って付けたラベル。表には必ず原文を併記する。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_shell import SRC_INTRO_JICHITAI, faq_html, source_list, table, write
from _byoji_funin_data import CHECKED, WARDS

TODAY = "2026-08-27"
TOOL_SLUG = "funin-josei-jichitai"
ART_SLUG = "funin-josei-data"
TOOL_URL = "https://www.noe-match.com/tools/%s/" % TOOL_SLUG
OISIX = "https://px.a8.net/svt/ejp?a8mat=45C0YR+2VBK6Q+3250+5YZ77"

# 対象になる費用の範囲。各区の funin_taisho_chiryo の原文から読み取ったラベルで、
# 優劣ではなく「何にお金が出るか」の区分。表には必ず原文を併記する。
RANGE = {
    "chiyoda": "先進医療のみ", "chuo": "保険診療の自己負担分＋先進医療",
    "minato": "先進医療＋自由診療", "bunkyo": "先進医療＋自由診療",
    "taito": "先進医療のみ", "koto": "先進医療のみ",
    "shinagawa": "保険診療の自己負担分のみ（先進医療・自由診療は対象外）",
    "meguro": "先進医療のみ", "ota": "先進医療のみ",
    "shibuya": "保険診療の自己負担分＋先進医療", "nakano": "先進医療のみ",
    "suginami": "先進医療のみ", "kita": "先進医療のみ", "arakawa": "先進医療のみ",
    "nerima": "先進医療のみ", "adachi": "先進医療のみ", "katsushika": "先進医療のみ",
}
RANGE_ORDER = ["先進医療のみ", "保険診療の自己負担分＋先進医療",
               "先進医療＋自由診療",
               "保険診療の自己負担分のみ（先進医療・自由診療は対象外）"]

for _w in WARDS:
    _w["funin_range"] = RANGE.get(_w["key"], "実施なし")

YES = [w for w in WARDS if w["funin_jisshi"]]
NO = [w for w in WARDS if not w["funin_jisshi"]]
ONLY_SENSHIN = [w for w in YES if w["funin_range"] == "先進医療のみ"]
MAXW = max(YES, key=lambda w: w["funin_jogen_gaku"])
GAKU = sorted(set(w["funin_jogen_gaku"] for w in YES))
NYES, NNO = len(YES), len(NO)

# 実施している区に、上限額のラベルが未定義のものが無いことを確かめてから作る。
_undef = [w["name"] for w in YES if w["key"] not in RANGE]
assert not _undef, "対象範囲のラベルが未定義: %s" % _undef


def groups():
    out = []
    for g in RANGE_ORDER:
        ws = [w for w in YES if w["funin_range"] == g]
        if not ws:
            continue
        out.append((g, ws))
    return out


def range_html():
    parts = []
    for g, ws in groups():
        parts.append('<h3>%s（%d区）</h3>' % (g, len(ws)))
        parts.append(table(["区", "区の上限額", "対象になる費用（原文）"],
                           [(w["name"], "{:,}円".format(w["funin_jogen_gaku"]),
                             w["funin_taisho_chiryo"]) for w in ws], ["", "", ""]))
    return "\n".join(parts)


# ============================================================ 器具
def build_tool():
    shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
    CSS = shell[shell.find("<style>"):shell.find("</style>") + 8]

    TITLE = ("不妊治療の区独自助成は東京23区のどこにある？実施%d区・上限額と対象になる費用【%s確認】"
             % (NYES, CHECKED))
    H1 = "不妊治療の助成、あなたの区にあるか｜東京23区の実施状況と対象になる費用"
    DESC = ("東京都の助成とは別に区が独自に上乗せしている不妊治療助成について、23区すべての公式ページを"
            "確認しました。実施しているのは%d区、実施していないのは%d区（%s）です。"
            "上限額は5万円から%s円まで開きますが、対象になる費用の範囲が区によって違うため金額だけでは"
            "比べられません。%d区は先進医療だけが対象、品川区は逆に保険適用の自己負担分のみが対象で"
            "先進医療は対象外です。区を選ぶと実施の有無・上限額・対象・申請期限を出典つきで表示します。"
            % (NYES, NNO, "・".join(w["name"] for w in NO),
               "{:,}".format(MAXW["funin_jogen_gaku"]), len(ONLY_SENSHIN)))
    OGD = ("同じ上限5万円でも、対象になる費用が正反対の区があります。実施%d区・未実施%d区の一覧。"
           % (NYES, NNO))

    FAQ = [
     ("不妊治療の助成が受けられない区はありますか？",
      "区独自の上乗せ助成を実施していないのは%d区（%s）です。ただし東京都の助成そのものは"
      "都内在住であれば対象なので、「区にないから何もない」ということではありません。"
      "%s現在の各区公式ページの記載にもとづきます。"
      % (NNO, "・".join(w["name"] for w in NO), CHECKED)),
     ("上限額がいちばん大きい区はどこですか？",
      "%sの%s円です。ただし%sは自由診療まで対象に含めているため上限が大きく、"
      "先進医療だけを対象にしている%d区の5万円とは対象範囲が違います。"
      "<strong>金額だけを並べて比べることはできません。</strong>"
      % (MAXW["name"], "{:,}".format(MAXW["funin_jogen_gaku"]),
         MAXW["name"], len(ONLY_SENSHIN))),
     ("同じ5万円なら、どの区でも同じですか？",
      "違います。%d区の5万円は「保険診療と併用した先進医療」が対象ですが、"
      "品川区は「保険適用の自己負担分のみ」が対象で、先進医療および自由診療は対象外と"
      "明記しています。同じ金額でも対象になる費用が正反対です。"
      % len(ONLY_SENSHIN)),
     ("上限額はそのままもらえますか？",
      "もらえません。計算式は区ごとに違い、多くの区が東京都の助成額を差し引いた残りを"
      "対象にしています。練馬区は「先進医療に係る費用の7割から都の助成上限額15万円を"
      "差し引いた額」と「区の上限5万円」の低いほうを助成する方式で、区の掲載例では"
      "自己負担28万円で助成4万6千円、自己負担20万円だと都の上限に届かないため"
      "区の助成は対象外になります。本ツールは金額を計算していません。"),
     ("東京都と区、どちらに先に申請しますか？",
      "都が先です。多くの区が「東京都特定不妊治療費（先進医療）助成事業の承認決定を受けた方」を"
      "対象としており、都の承認決定日を起点に区の申請期限を定めている区もあります。"
      "都に申請していないと区の助成にたどり着けません。"),
     ("申請の期限はいつまでですか？",
      "区によって起算点が違います。「治療終了年度の末日まで（1〜3月終了分は6月30日まで）」と"
      "する区と、「東京都の承認決定日から1年以内」とする区があります。"
      "他の区の情報をそのまま当てはめると期限を逃すため、必ずお住まいの区の記載をご確認ください。"),
     ("この情報はいつのものですか？",
      "%sに23区すべての公式ページを確認した内容です。令和8年度は制度が動いており、"
      "中央区は令和8年4月1日以降の治療から対象範囲を変更、練馬区は同日以降に開始した治療について"
      "「東京都の助成が拡充されるため検討中」と明記しています。申請前に必ず公式ページをご確認ください。"
      % CHECKED),
    ]

    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in FAQ]}, ensure_ascii=False)
    app_ld = json.dumps({
        "@context": "https://schema.org", "@type": "WebApplication",
        "name": "不妊治療の区独自助成 東京23区", "url": TOOL_URL,
        "applicationCategory": "UtilitiesApplication", "operatingSystem": "All",
        "inLanguage": "ja", "description": DESC,
        "datePublished": TODAY, "dateModified": TODAY,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
        "publisher": {"@type": "Organization", "name": "Noe結婚設計室",
                      "url": "https://www.noe-match.com/"}}, ensure_ascii=False)
    bc_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList",
                        "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
        {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": "https://www.noe-match.com/#tools"},
        {"@type": "ListItem", "position": 3, "name": "不妊治療の区独自助成 東京23区"}]}, ensure_ascii=False)

    opts = "".join('<option value="%s">%s</option>' % (w["key"], w["name"]) for w in WARDS)
    rows = "".join(
        '<tr><td><strong>%s</strong></td><td>%s</td><td style="white-space:nowrap">%s</td><td>%s</td></tr>'
        % (w["name"],
           '<span class="badge b-ok">実施</span>' if w["funin_jisshi"]
           else '<span class="badge b-ng">実施なし</span>',
           "{:,}円".format(w["funin_jogen_gaku"]) if w["funin_jisshi"] else "―",
           w["funin_range"] if w["funin_jisshi"] else "―")
        for w in WARDS)
    src_rows = "".join(
        '<tr><td>%s</td><td><a href="%s" rel="noopener" target="_blank">%s</a></td><td>%s</td></tr>'
        % (w["name"], w["funin_src"], w["funin_src_label"], CHECKED) for w in WARDS)
    faq_html_s = "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a)
                           for i, (q, a) in enumerate(FAQ))
    DATA = json.dumps({w["key"]: w for w in WARDS}, ensure_ascii=False, separators=(",", ":"))

    tpl = io.open("scripts/_funin_body.html", encoding="utf-8").read()
    html = (tpl.replace("__TITLE__", TITLE).replace("__DESC__", DESC).replace("__OGD__", OGD)
            .replace("__URL__", TOOL_URL).replace("__H1__", H1).replace("__CSS__", CSS)
            .replace("__FAQLD__", faq_ld).replace("__APPLD__", app_ld).replace("__BCLD__", bc_ld)
            .replace("__OPTS__", opts).replace("__ROWS__", rows).replace("__SRCROWS__", src_rows)
            .replace("__RANGEHTML__", range_html()).replace("__FAQHTML__", faq_html_s)
            .replace("__DATA__", DATA).replace("__SLUG__", TOOL_SLUG)
            .replace("__CHECKED__", CHECKED)
            .replace("__NYES__", str(NYES)).replace("__NNO__", str(NNO))
            .replace("__ONLY_SENSHIN__", str(len(ONLY_SENSHIN)))
            .replace("__OISIX__", OISIX))
    os.makedirs("tools/%s" % TOOL_SLUG, exist_ok=True)
    io.open("tools/%s/index.html" % TOOL_SLUG, "w", encoding="utf-8").write(html)
    print("written: tools/%s/index.html  %d chars" % (TOOL_SLUG, len(html)))


# ============================================================ 記事
FAQ_ART = [
 ("不妊治療の区独自助成はどの区にありますか？",
  "東京23区のうち%d区が実施し、%d区（%s）は実施していません。"
  "区の上乗せは東京都の助成とは別で、都の助成そのものは都内在住であれば対象です。"
  % (NYES, NNO, "・".join(w["name"] for w in NO))),
 ("同じ上限5万円なら、どの区でも同じ内容ですか？",
  "違います。%d区の5万円は「保険診療と併用した先進医療」が対象ですが、品川区の5万円は"
  "「保険適用の自己負担分のみ」が対象で、先進医療および自由診療は対象外と明記しています。"
  "同じ金額でも対象になる費用が正反対です。金額だけを並べた比較表では、この差は見えません。"
  % len(ONLY_SENSHIN)),
 ("いちばん手厚い区はどこですか？",
  "上限額だけを見れば%sの%s円ですが、これは自由診療まで対象に含めているためで、"
  "先進医療だけを対象にする区の5万円とは比べる対象が違います。文京区は先進医療で1回上限5万円、"
  "自由診療で1回上限10万円と内訳を分けて公表しています。"
  "自分が受ける治療がどの区分に当たるかで、どの区が手厚いかは変わります。"
  % (MAXW["name"], "{:,}".format(MAXW["funin_jogen_gaku"]))),
 ("上限額はそのままもらえますか？",
  "もらえません。練馬区は「先進医療に係る費用の7割から東京都の助成上限額15万円を差し引いた額」と"
  "「区の上限5万円」を比べて低いほうを助成する方式です。区の掲載例では自己負担28万円で助成4万6千円、"
  "自己負担20万円では都の上限に届かないため区の助成は対象外になります。"
  "上限額は「これ以上は出ない額」であって、もらえる額ではありません。"),
 ("都と区、どちらに先に申請しますか？",
  "都が先です。多くの区が「東京都特定不妊治療費（先進医療）助成事業の承認決定を受けた方」を"
  "対象としています。区によっては都の承認決定日を起点に申請期限を定めているため、"
  "都への申請が遅れると区の期限にも影響します。"),
 ("引っ越したらどうなりますか？",
  "申請時にその区に住んでいることを要件にしている区が多く、実施していない区へ転出すると"
  "区の上乗せは受けられません。逆に実施している区へ転入すれば対象になり得ます。"
  "居住要件の書き方も区で違うため、転居前に転居先の記載を確認してください。"),
 ("令和8年度はどうなりますか？",
  "制度が動いています。中央区は令和8年4月1日以降の治療から対象範囲を変えており、"
  "練馬区は同日以降に開始した治療について「東京都の助成が拡充されるため検討中」と"
  "明記しています（%s時点）。治療の開始日で扱いが変わるため、開始前の確認が要ります。" % CHECKED),
]


def build_article():
    p = []
    p.append(
        "<blockquote><strong>「うちの区は上限5万円」と分かっても、それだけでは何も分かりません。</strong>"
        "%sに東京23区すべての公式ページを確認したところ、不妊治療の区独自助成を実施していたのは"
        "%d区、実施していないのが%d区（%s）でした。上限額は5万円から%s円まで開きます。"
        "ただし本当の差は金額ではありません。<strong>%d区は「先進医療だけ」が対象なのに対し、"
        "品川区は「保険適用の自己負担分のみ」が対象で先進医療は対象外</strong>と明記しています。"
        "同じ5万円でも、対象になる費用が正反対です。</blockquote>"
        % (CHECKED, NYES, NNO, "・".join(w["name"] for w in NO),
           "{:,}".format(MAXW["funin_jogen_gaku"]), len(ONLY_SENSHIN)))

    p.append('<h2 id="umu">まず、実施していない区が%d区ある</h2>' % NNO)
    p.append("<p>子ども医療費助成は23区すべてが実施していて対象年齢も同一、病児保育も23区すべてが"
             "実施しています。ところが不妊治療の区独自助成は、<strong>そもそも実施しているかどうかで"
             "割れます</strong>。実施していないのは%sの%d区です。</p>"
             % ("・".join(w["name"] for w in NO), NNO))
    p.append("<p>ただし勘違いしやすいのは、これが「その区に住むと不妊治療の助成が一切ない」という"
             "意味ではないことです。東京都の助成は都内在住であれば対象で、区の制度はその上乗せです。"
             "実施していない区にお住まいでも、都の助成そのものは使えます。</p>")

    p.append('<h2 id="hanni">上限額ではなく、対象になる費用で分かれている</h2>')
    p.append("<p>実施している%d区を、対象にしている費用の範囲でまとめました。"
             "ラベルはこちらで原文から読み取って付けたものなので、判断の根拠になる原文も併記します。</p>" % NYES)
    p.append(range_html())
    p.append("<p>ここが本記事のいちばん重要なところです。"
             "<strong>品川区の5万円と練馬区の5万円は、対象になる費用が逆です。</strong>"
             "練馬区は「1回の特定不妊治療（保険診療）と併せて実施した先進医療の費用」が対象で、"
             "品川区は「保険適用の自己負担分のみ。先進医療および自由診療にかかる検査・治療等の医療費は"
             "助成対象外」と明記しています。金額だけを並べた比較表では、この違いは絶対に見えません。</p>")

    p.append('<h2 id="jougen">上限額は「もらえる額」ではない</h2>')
    p.append("<p>上限額をそのまま受け取れると考えると、見込みを大きく外します。"
             "練馬区は計算式と具体例まで公表しているので、そのまま引用します。</p>")
    p.append(table(["練馬区の助成額の決め方", "内容"],
                   [("計算方法", "「先進医療に係る費用の7割から東京都の助成上限額15万円を差し引いた額」と「区の上限5万円」を比べて、低いほうを助成"),
                    ("例1", "自己負担28万円 → 区の助成は4万6千円"),
                    ("例2", "自己負担20万円 → 都の助成上限に届かないため、区の助成は対象外")],
                   ["", ""]))
    p.append("<p>つまり<strong>自己負担が少ないと、かえって区の助成に届かない</strong>という設計です。"
             "計算式は区ごとに違い、23区すべてぶんは公表されていません。"
             "だからこのサイトの器具でも助成額は計算していません。"
             "自動で当てはめると、当たらない見込み額を出してしまうためです。</p>")

    p.append('<h2 id="ichiran">東京23区の一覧</h2>')
    p.append(table(["区", "実施", "区の上限額", "対象になる費用"],
                   [(w["name"], "実施" if w["funin_jisshi"] else "実施なし",
                     "{:,}円".format(w["funin_jogen_gaku"]) if w["funin_jisshi"] else "―",
                     w["funin_range"] if w["funin_jisshi"] else "―") for w in WARDS],
                   ["", "", "", ""]))
    p.append('<p>お住まいの区の詳しい条件は、'
             '<a href="/tools/funin-josei-jichitai/">不妊治療の助成、あなたの区にあるか（東京23区）</a>で'
             '区を選ぶと、対象になる人・回数の上限・申請期限まで出典つきで出ます。</p>')

    p.append('<h2 id="kigen">申請期限は起算点そのものが違う</h2>')
    p.append("<p>「いつまでに出せばいいか」を他の区の情報で判断すると期限を逃します。"
             "起算点が「治療の終了」の区と「東京都の承認決定」の区があるためです。</p>")
    p.append(table(["区", "申請期限（原文）"],
                   [(w["name"], w["funin_shinsei_kigen"]) for w in YES], ["", ""]))

    p.append('<h2 id="taisho">対象になる人の条件</h2>')
    p.append("<p>年齢は「治療開始日時点で妻が43歳未満」とする区が多数です。"
             "居住要件は「申請時に区内在住」「治療開始日から申請日まで継続して居住」など書き方が分かれます。"
             "所得制限については記載が無い区が多く、記載が無いことは制限が無いことを意味しないため、"
             "そのまま原文を載せます。</p>")
    p.append(table(["区", "対象になる人（原文）"],
                   [(w["name"], w["funin_taisho"]) for w in YES], ["", ""]))

    p.append('<h2 id="r8">令和8年度は制度が動いている</h2>')
    p.append("<p>%s時点で、次の変更が公表されています。治療の開始日がいつかで扱いが変わるため、"
             "開始前に区へ確認するのが安全です。</p>" % CHECKED)
    p.append("<ul>"
             "<li><strong>中央区</strong>｜令和8年4月1日以降に開始した治療から対象範囲を変更。"
             "令和8年3月31日までの治療とは扱いが違います。</li>"
             "<li><strong>練馬区</strong>｜令和8年4月1日以降に開始した治療については、"
             "東京都の助成が拡充されるため区制度は「検討中」と明記。"
             "令和7年4月1日〜令和8年3月31日に開始した治療が受付対象です。</li>"
             "</ul>")

    p.append("""
<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/tools/funin-josei-jichitai/">不妊治療の助成、あなたの区にあるか｜東京23区の実施状況と対象</a></li>
<li><a href="/articles/byoji-hoiku-data/">病児保育は1日いくら？東京23区の料金と、料金以外で詰まるところ</a></li>
<li><a href="/articles/kodomo-iryohi-data/">子ども医療費助成は東京23区でどう違う？差がつくのは入院時の食事代</a></li>
<li><a href="/articles/shussan-hiyou-data/">出産費用の平均はいくら？都道府県別・費目別と「実際に請求される額」との差</a></li>
<li><a href="/articles/sangokea-josei/">産後ケアの助成はいくら？非課税世帯の減免と所得を問わない減額枠</a></li>
</ul>""")
    p.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    p.append(faq_html(FAQ_ART))
    p.append(source_list([(w["funin_src"], "%s｜%s" % (w["name"], w["funin_src_label"]))
                          for w in WARDS], SRC_INTRO_JICHITAI))

    write(ART_SLUG,
          "不妊治療の区独自助成は東京23区でどう違う？実施%d区・同じ5万円でも中身が正反対【%s確認】"
          % (NYES, CHECKED),
          "不妊治療の区独自助成は東京23区でどう違う？同じ5万円でも中身が正反対",
          "東京都の助成とは別に区が上乗せしている不妊治療助成を、23区すべての公式ページで確認しました。"
          "実施%d区・未実施%d区（%s）。上限額は5万円から%s円まで開きますが、"
          "本当の差は金額ではなく対象になる費用の範囲です。%d区は先進医療だけが対象、"
          "品川区は逆に保険適用の自己負担分のみが対象で先進医療は対象外と明記しています。"
          "上限額はもらえる額ではなく、練馬区の例では自己負担20万円だと助成の対象外になります。確認日は%s。"
          % (NYES, NNO, "・".join(w["name"] for w in NO),
             "{:,}".format(MAXW["funin_jogen_gaku"]), len(ONLY_SENSHIN), CHECKED),
          "同じ上限5万円でも、対象になる費用が正反対の区があります。実施%d区・未実施%d区の一覧。"
          % (NYES, NNO),
          FAQ_ART, "\n".join(p), TODAY, CHECKED,
          "通院が続く時期に、家のことを一つ減らす",
          "不妊治療は通院の回数が多く、時間の使い方から先に苦しくなります。"
          "助成の額は制度で決まっていて動かせませんが、買い物と献立を考える時間は今日から減らせます。")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build_tool()
    build_article()
    print("実施%d区 / 未実施%d区（%s）／ 上限額の種類 %s ／ 先進医療のみ %d区"
          % (NYES, NNO, "・".join(w["name"] for w in NO),
             "・".join("{:,}円".format(g) for g in GAKU), len(ONLY_SENSHIN)))

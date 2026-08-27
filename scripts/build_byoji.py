# -*- coding: utf-8 -*-
"""病児保育の器具とデータ記事を生成する（2026-08-27 新設）

狙う語は「病児保育 料金」。子ども医療費助成（対象年齢が23区同一）と違い、
**23区すべてが実施しているのに料金が0円〜3,500円まで開く**のが核。
SERP1ページ目は区の公式ページと施設サイトで、23区を横断して比べる器具はゼロだった。

実査で分かった核（2026-08-27・23区）:
- 23区すべてが病児・病後児保育を実施している（差は有無ではなく料金）
- 1日あたり: 江戸川区0円 〜 新宿区3,500円。15区が2,000円で並ぶ
- 減免の区分は区ごとに違う（生活保護／住民税非課税／所得税非課税 の3区分が多いが揃っていない）
- 利用上限は「1回につき連続7日」が多いが、練馬区は6日。非公表の区もある
- ほぼ全区で事前登録が必要で、登録先が区ではなく各施設という区が多い

減免後の額は区分が揃っていないため**計算しない**。通常料金だけを計算し、
減免は原文を表示する（8/25・8/27の教訓: 分類を勝手に決めない）。
"""
import io
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_shell import SRC_INTRO_JICHITAI, faq_html, source_list, table, write
from _byoji_funin_data import CHECKED, WARDS

TODAY = "2026-08-27"
TOOL_SLUG = "byoji-hoiku-ryokin"
ART_SLUG = "byoji-hoiku-data"
TOOL_URL = "https://www.noe-match.com/tools/%s/" % TOOL_SLUG
OISIX = "https://px.a8.net/svt/ejp?a8mat=45C0YR+2VBK6Q+3250+5YZ77"

N = len(WARDS)
JISSHI = [w for w in WARDS if w["byoji_jisshi"]]
PRICED = sorted([w for w in WARDS if w["byoji_fee"] is not None],
                key=lambda w: w["byoji_fee"])
MINW, MAXW = PRICED[0], PRICED[-1]
_C = Counter(w["byoji_fee"] for w in PRICED)
MODE, MODE_N = _C.most_common(1)[0]
# 年10日使ったときの最安と最高の差。生活実感に落とすための数字。
DIFF10 = (MAXW["byoji_fee"] - MINW["byoji_fee"]) * 10


# ============================================================ 器具
def build_tool():
    shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
    CSS = shell[shell.find("<style>"):shell.find("</style>") + 8]

    TITLE = ("病児保育は1日いくら？東京23区の料金・減免・利用上限・予約方法【%s確認】" % CHECKED)
    H1 = "病児保育は1日いくら？｜東京23区の料金と、同じ日数を使ったときの差"
    DESC = ("東京23区はすべて病児・病後児保育を実施していますが、1日あたりの料金は"
            "%s%s円から%s%s円まで開いています（%d区が%s円）。年10日使うと最大%s円の差になります。"
            "区と使う日数を入れると自己負担の合計と23区での位置づけが出ます。"
            "減免の条件・対象年齢・利用上限・予約方法も出典つきで表示します。"
            % (MINW["name"], "{:,}".format(MINW["byoji_fee"]),
               MAXW["name"], "{:,}".format(MAXW["byoji_fee"]),
               MODE_N, "{:,}".format(MODE), "{:,}".format(DIFF10)))
    OGD = ("23区すべてが実施しているのに、1日あたりは0円の区と3,500円の区があります。"
           "年10日で最大%s円の差です。" % "{:,}".format(DIFF10))

    FAQ = [
     ("病児保育は1日いくらかかりますか？",
      "東京23区では1日あたり%s円（%s）から%s円（%s）まで開いています。"
      "%d区が%s円で、これがいちばん多い金額です。"
      "%s現在の各区公式ページの記載にもとづく金額で、これとは別に給食費・おやつ代などが"
      "かかる区があります。"
      % ("{:,}".format(MINW["byoji_fee"]), MINW["name"],
         "{:,}".format(MAXW["byoji_fee"]), MAXW["name"],
         MODE_N, "{:,}".format(MODE), CHECKED)),
     ("病児保育をやっていない区はありますか？",
      "東京23区はすべて病児・病後児保育を実施しています。差がつくのは有無ではなく料金と"
      "利用条件です。ただし区内の実施施設数は区によって違い、希望日に空きがあるとは限りません。"),
     ("料金が安くなる制度はありますか？",
      "多くの区で減免があります。生活保護世帯・住民税非課税世帯・所得税非課税世帯という"
      "3区分を設けている区が多いものの、区分の切り方は区によって違います。"
      "本ツールでは減免後の額を計算せず、各区の記載をそのまま表示しています。"
      "該当しそうな場合は区または施設にご確認ください。"),
     ("何日まで続けて使えますか？",
      "「1回につき連続7日まで」としている区が多数ですが、練馬区は「原則として一つの病気につき"
      "6日間」です。年間の上限日数まで定めている区もあれば、上限の記載が公式ページに"
      "見当たらない区もあります。本ツールでは各区の記載をそのまま表示しています。"),
     ("当日いきなり預けられますか？",
      "ほとんどの区で事前登録が必要です。子どもが熱を出してから登録しようとしても間に合いません。"
      "登録先が区役所ではなく各施設という区も多く、練馬区は「保育課窓口では受け付けなし」と"
      "明記しています。さらに利用前に医療機関を受診して診療情報提供書を書いてもらう必要がある"
      "区が多いため、当日の朝は受診から始まります。<strong>元気なうちに登録を済ませておくのが"
      "前提の制度です。</strong>"),
     ("この情報はいつのものですか？",
      "%sに23区すべての公式ページを確認した内容です。料金・条件は年度で変わるため、"
      "利用前に必ず各区の公式ページでご確認ください。本ツールには各区の出典リンクを載せています。"
      % CHECKED),
    ]

    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in FAQ]}, ensure_ascii=False)
    app_ld = json.dumps({
        "@context": "https://schema.org", "@type": "WebApplication",
        "name": "病児保育の料金 東京23区", "url": TOOL_URL,
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
        {"@type": "ListItem", "position": 3, "name": "病児保育の料金 東京23区"}]}, ensure_ascii=False)

    opts = "".join('<option value="%s">%s</option>' % (w["key"], w["name"]) for w in WARDS)
    rows = "".join(
        '<tr><td><strong>%s</strong></td><td style="white-space:nowrap">%s円</td><td>%s</td><td>%s</td></tr>'
        % (w["name"], "{:,}".format(w["byoji_fee"]), w["byoji_fee_label"], w["byoji_genmen"])
        for w in PRICED)
    src_rows = "".join(
        '<tr><td>%s</td><td><a href="%s" rel="noopener" target="_blank">%s</a></td><td>%s</td></tr>'
        % (w["name"], w["byoji_src"], w["byoji_src_label"], CHECKED) for w in WARDS)
    faq_html_s = "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a)
                           for i, (q, a) in enumerate(FAQ))
    DATA = json.dumps({w["key"]: w for w in WARDS}, ensure_ascii=False, separators=(",", ":"))

    tpl = io.open("scripts/_byoji_body.html", encoding="utf-8").read()
    html = (tpl.replace("__TITLE__", TITLE).replace("__DESC__", DESC).replace("__OGD__", OGD)
            .replace("__URL__", TOOL_URL).replace("__H1__", H1).replace("__CSS__", CSS)
            .replace("__FAQLD__", faq_ld).replace("__APPLD__", app_ld).replace("__BCLD__", bc_ld)
            .replace("__OPTS__", opts).replace("__ROWS__", rows).replace("__SRCROWS__", src_rows)
            .replace("__FAQHTML__", faq_html_s).replace("__DATA__", DATA)
            .replace("__SLUG__", TOOL_SLUG).replace("__CHECKED__", CHECKED)
            .replace("__MINNAME__", MINW["name"]).replace("__MAXNAME__", MAXW["name"])
            .replace("__MIN__", "{:,}".format(MINW["byoji_fee"]))
            .replace("__MAX__", "{:,}".format(MAXW["byoji_fee"]))
            .replace("__MODEN__", str(MODE_N)).replace("__MODE__", "{:,}".format(MODE))
            .replace("__OISIX__", OISIX))
    os.makedirs("tools/%s" % TOOL_SLUG, exist_ok=True)
    io.open("tools/%s/index.html" % TOOL_SLUG, "w", encoding="utf-8").write(html)
    print("written: tools/%s/index.html  %d chars" % (TOOL_SLUG, len(html)))


# ============================================================ 記事
FAQ_ART = [
 ("病児保育の料金は東京23区でどのくらい違いますか？",
  "1日あたり%s円（%s）から%s円（%s）までで、開きは%s円です。"
  "%d区が%s円で並んでおり、これが最も多い金額です。年に10日使うと、最も安い区と"
  "最も高い区で%s円の差になります。"
  % ("{:,}".format(MINW["byoji_fee"]), MINW["name"],
     "{:,}".format(MAXW["byoji_fee"]), MAXW["name"],
     "{:,}".format(MAXW["byoji_fee"] - MINW["byoji_fee"]),
     MODE_N, "{:,}".format(MODE), "{:,}".format(DIFF10))),
 ("病児保育を実施していない区はありますか？",
  "東京23区はすべて実施しています。子ども医療費助成の対象年齢が23区で同一なのと同じく、"
  "「やっているかどうか」で差はつきません。差がつくのは料金と、減免の区分と、"
  "利用上限と、予約の経路です。"),
 ("病児保育は当日でも予約できますか？",
  "施設によっては当日の予約を受け付けていますが、その前に事前登録が済んでいることが前提です。"
  "登録先が区役所ではなく各施設という区が多く、練馬区は「保育課窓口では受け付けなし」と"
  "明記しています。熱が出てから登録するのでは間に合いません。"),
 ("医師の診断書は必要ですか？",
  "多くの区で、利用前に医療機関を受診して区や施設の様式の診療情報提供書を書いてもらう必要が"
  "あります。練馬区は「練馬区病児・病後児保育診療情報提供書」という区の様式を指定しています。"
  "この書類の発行に費用がかかる場合もあり、当日の朝は受診から始まる前提で時間を見ておく必要が"
  "あります。"),
 ("料金のほかにお金はかかりますか？",
  "区や施設によって、給食費・おやつ代・医薬品代などが別途かかります。練馬区は"
  "「別途、給食費等の負担あり」と明記しています。本記事の金額は保育料そのものなので、"
  "合計は施設にご確認ください。"),
 ("何歳から何歳まで使えますか？",
  "区によって違います。練馬区は「生後6か月〜10歳未満」で、区内在住かつ保育所などに"
  "通所していることが条件です。年齢の下限・上限、在住要件、通所要件はいずれも区ごとに"
  "違うため、本記事では各区の記載をそのまま載せています。"),
]


def build_article():
    p = []
    p.append(
        "<blockquote><strong>「うちの区に病児保育はあるか」を調べても、差は見えません。</strong>"
        "%sに東京23区すべての公式ページを確認したところ、<strong>23区すべてが病児・病後児保育を"
        "実施していました</strong>。差がつくのは料金のほうで、1日あたり%s区の%s円から"
        "%s区の%s円まで開いています。年に10日使えば%s円の差です。"
        "そして実際に詰まるのは、料金でも空きでもなく<strong>事前登録</strong>です。</blockquote>"
        % (CHECKED, MINW["name"][:-1], "{:,}".format(MINW["byoji_fee"]),
           MAXW["name"][:-1], "{:,}".format(MAXW["byoji_fee"]), "{:,}".format(DIFF10)))

    p.append('<h2 id="ryokin">1日あたりの料金は0円から3,500円まで</h2>')
    p.append("<p>安い順に並べています。%d区が%s円で並び、そこから上下に外れる区があります。</p>"
             % (MODE_N, "{:,}".format(MODE)))
    p.append(table(["区", "1日あたり", "料金の記載（原文）"],
                   [(w["name"], "{:,}円".format(w["byoji_fee"]), w["byoji_fee_label"])
                    for w in PRICED], ["", "", ""]))
    p.append("<p>この金額は保育料そのものです。区や施設によっては給食費・おやつ代・医薬品代などが"
             "別途かかります。練馬区は「別途、給食費等の負担あり」と明記しています。"
             "半日料金を設けている区と設けていない区もあるため、半日だけ預けたい場合は"
             "施設に確認してください。</p>")

    p.append('<h2 id="tsumori">年に何日使うかで差は積み上がる</h2>')
    p.append("<p>子どもが病気になる回数は選べません。保育園に通い始めた1年目は特に多く、"
             "月に1回以上熱を出すことも珍しくありません。使う日数ごとに、最も安い区と"
             "最も高い区の差を出すと次のようになります。</p>")
    p.append(table(["年間の利用日数", "%s（%s円/日）" % (MINW["name"], "{:,}".format(MINW["byoji_fee"])),
                    "%s（%s円/日）" % (MAXW["name"], "{:,}".format(MAXW["byoji_fee"])), "差"],
                   [("%d日" % d,
                     "{:,}円".format(MINW["byoji_fee"] * d),
                     "{:,}円".format(MAXW["byoji_fee"] * d),
                     "{:,}円".format((MAXW["byoji_fee"] - MINW["byoji_fee"]) * d))
                    for d in (5, 10, 15, 20, 30)], ["", "", "", ""]))
    p.append('<p>自分の区の金額で試すには、'
             '<a href="/tools/byoji-hoiku-ryokin/">病児保育は1日いくら？東京23区</a>で'
             '区と日数を入れてください。23区の中での位置づけも出ます。</p>')

    p.append('<h2 id="genmen">減免はあるが、区分の切り方が揃っていない</h2>')
    p.append("<p>多くの区に減免があります。生活保護世帯・住民税非課税世帯・所得税非課税世帯という"
             "3区分が多いものの、切り方は区によって違います。ここは横並びで比べられる項目ではないため、"
             "各区の記載をそのまま載せます。</p>")
    p.append(table(["区", "減免（原文）"],
                   [(w["name"], w["byoji_genmen"]) for w in PRICED
                    if w["byoji_genmen"] and w["byoji_genmen"] != "記載なし"], ["", ""]))
    p.append("<p>減免の申請先も区ではなく施設という区があります。練馬区は「各施設または保育課へ"
             "利用料免除・減額申請書と証明書類を提出」としています。"
             "<strong>本記事も本ツールも、減免後の額は計算していません。</strong>"
             "区分の切り方が揃っていない以上、自動で当てはめると間違えるためです。</p>")

    p.append('<h2 id="tsumazuki">料金より先に詰まるのは事前登録</h2>')
    p.append("<p>病児保育で最も多い詰まり方は、料金でも空きでもありません。"
             "<strong>子どもが熱を出した朝に、まだ登録していないことに気づく</strong>ことです。</p>")
    p.append("<h3>登録先が区役所ではなく各施設のことが多い</h3>")
    p.append("<p>練馬区は「各施設での事前登録制（保育課窓口では受け付けなし）」と明記しています。"
             "区のページを見て区役所へ行っても登録できません。しかも施設ごとに登録が必要なので、"
             "近隣の複数施設を使いたい場合はその数だけ登録することになります。</p>")
    p.append("<h3>利用前に受診して診療情報提供書を出す</h3>")
    p.append("<p>区や施設の様式の診療情報提供書を医師に書いてもらう必要がある区が多くあります。"
             "つまり当日の朝は、受診 → 書類受け取り → 施設へ移動、という順番になります。"
             "書類の発行に費用がかかることもあります。仕事の遅刻連絡は、この時間を見込んで"
             "入れておくほうが安全です。</p>")
    p.append("<h3>予約の経路も区で違う</h3>")
    p.append("<p>各区の予約方法をそのまま並べます。区共通のweb予約システムがある区と、"
             "施設ごとに方法が指定される区があります。</p>")
    p.append(table(["区", "予約・事前登録（原文）"],
                   [(w["name"], w["byoji_yoyaku"]) for w in WARDS
                    if w["byoji_yoyaku"] and w["byoji_yoyaku"] != "記載なし"], ["", ""]))

    p.append('<h2 id="jogen">利用できる日数の上限</h2>')
    p.append("<p>「1回につき連続7日まで」としている区が多数ですが、練馬区は「原則として一つの病気に"
             "つき6日間」です。年間の上限まで定めている区もあれば、上限の記載が公式ページに"
             "見当たらない区もあります。記載が無いことは上限が無いことを意味しないため、"
             "そのまま「非公表」と書いています。</p>")
    p.append(table(["区", "利用できる日数の上限（原文）"],
                   [(w["name"], w["byoji_jogen"]) for w in WARDS], ["", ""]))

    p.append('<h2 id="taisho">対象になる年齢と条件</h2>')
    p.append("<p>年齢の下限・上限に加えて、区内在住であること、保育所などに通所していることを"
             "条件にしている区があります。在宅で育児をしている家庭が使えるかどうかは、"
             "この通所要件で分かれます。</p>")
    p.append(table(["区", "対象（原文）"],
                   [(w["name"], w["byoji_taisho"]) for w in WARDS], ["", ""]))

    p.append("""
<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/tools/byoji-hoiku-ryokin/">病児保育は1日いくら？東京23区の料金と利用条件</a></li>
<li><a href="/articles/kodomo-iryohi-data/">子ども医療費助成は東京23区でどう違う？差がつくのは入院時の食事代</a></li>
<li><a href="/articles/daredemo-tsuen-ryokin/">こども誰でも通園制度の料金はいくら？46自治体の実額と減免</a></li>
<li><a href="/articles/sangokea-nankai/">産後ケアは何回使える？43自治体の上限一覧</a></li>
<li><a href="/tools/ikukyu-encho-hantei/">育休はいつまで延長できる？条件と必要書類の判定</a></li>
</ul>""")
    p.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    p.append(faq_html(FAQ_ART))
    p.append(source_list([(w["byoji_src"], "%s｜%s" % (w["name"], w["byoji_src_label"]))
                          for w in WARDS], SRC_INTRO_JICHITAI))

    write(ART_SLUG,
          "病児保育は1日いくら？東京23区の料金・減免・利用上限と、料金より先に詰まるところ【%s確認】" % CHECKED,
          "病児保育は1日いくら？東京23区の料金と、料金以外で詰まるところ",
          "東京23区はすべて病児・病後児保育を実施していますが、1日あたりの料金は%s%s円から"
          "%s%s円まで開いています（%d区が%s円）。年に10日使うと%s円の差です。"
          "料金・減免・対象・利用上限・予約方法を23区ぶん出典つきで並べました。"
          "実際に詰まるのは料金ではなく事前登録で、登録先が区役所ではなく各施設という区が"
          "多くあります。確認日は%s。"
          % (MINW["name"], "{:,}".format(MINW["byoji_fee"]),
             MAXW["name"], "{:,}".format(MAXW["byoji_fee"]),
             MODE_N, "{:,}".format(MODE), "{:,}".format(DIFF10), CHECKED),
          "23区すべてが実施しているのに、1日0円の区と3,500円の区があります。年10日で%s円の差。"
          % "{:,}".format(DIFF10),
          FAQ_ART, "\n".join(p), TODAY, CHECKED,
          "熱を出した日に、買い物まで背負わない",
          "病児保育を使う日は受診・書類・送迎で午前が消えます。そのうえで買い物と献立まで"
          "抱えると回りません。制度の側は動かせませんが、この部分は今日から減らせます。")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build_tool()
    build_article()
    print("実施 %d/%d区 ／ 料金 %s円〜%s円（%d区が%s円）／ 年10日で最大%s円差"
          % (len(JISSHI), N, "{:,}".format(MINW["byoji_fee"]), "{:,}".format(MAXW["byoji_fee"]),
             MODE_N, "{:,}".format(MODE), "{:,}".format(DIFF10)))

# -*- coding: utf-8 -*-
"""子ども医療費助成の器具とデータ記事を生成する（2026-08-27 新設）

狙う語は tool_gate / data_gate でGO判定だった「子ども医療費助成」
（サジェスト10件。サジェストに渋谷区・足立区・江戸川区・北区など区名が並ぶ＝自治体差の需要）。
SERP1ページ目は区の公式ページ・都のガイド・まとめサイトで、器具はゼロだった。

実査で分かった核（2026-08-27・23区）:
- 年齢上限は23区すべて「18歳到達後最初の3月31日まで（高校生相当）」で差がない
- 所得制限は13区が「なし」と明記、10区は区ページに記載なし
- 自己負担は21区が「なし」、2区は記載なし
- **唯一の実質的な差は入院時食事療養費で、対象14区・対象外9区に割れる**
東京都の基準は「通院1回につき最大200円の一部負担あり」「入院時食事療養標準負担額は
助成対象外」なので、食事療養費を対象にしている14区は都基準への上乗せにあたる。

器具の計算部分は「子の生年月日 → 助成が切れる日」。18歳到達後最初の3月31日で、
これは年齢計算の応当日ではなく年度末なので、育休ツールとは別のロジックになる。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_shell import faq_html, source_list, table, write
from _kodomo_iryo_data import CHECKED, TOKYO_KIJUN, WARDS

TODAY = "2026-08-27"
TOOL_SLUG = "kodomo-iryohi-jichitai"
TOOL_URL = "https://www.noe-match.com/tools/%s/" % TOOL_SLUG
OISIX = "https://px.a8.net/svt/ejp?a8mat=45C0YR+2VBK6Q+3250+5YZ77"
N = len(WARDS)

shokuji_taisho = [w for w in WARDS if "対象外" not in w["shokuji_ryoyohi"]]
shokuji_gai = [w for w in WARDS if "対象外" in w["shokuji_ryoyohi"]]
seigen_nashi = [w for w in WARDS if w["shotoku_seigen"] is False]
seigen_none = [w for w in WARDS if w["shotoku_seigen"] is None]


# ============================================================ 器具
def build_tool():
    shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
    CSS = shell[shell.find("<style>"):shell.find("</style>") + 8]

    TITLE = ("子ども医療費助成はいつまで？東京23区の対象年齢・所得制限・"
             "入院時食事代の扱い【%s確認】" % CHECKED)
    H1 = "子ども医療費助成はいつまで使える？｜東京23区の条件と、区で割れる入院時食事代"
    DESC = ("子ども医療費助成（マル乳・マル子・マル青）の対象年齢は東京23区すべて"
            "「18歳到達後最初の3月31日まで」で差がありません。差がつくのは入院時食事療養費の扱いで、"
            "23区のうち%d区が助成対象、%d区が対象外でした。東京都の基準は「通院1回につき最大200円の"
            "一部負担あり」「入院時食事療養標準負担額は自己負担」なので、対象にしている区は"
            "都基準への上乗せです。子の生年月日と区を選ぶと、助成が切れる日とその区の条件が出ます。"
            % (len(shokuji_taisho), len(shokuji_gai)))
    OGD = ("23区とも高校生相当まで無料。ただし入院時食事代は%d区が対象外です。"
           "生年月日を入れると助成が切れる日が出ます。" % len(shokuji_gai))

    FAQ = [
     ("子ども医療費助成は何歳まで使えますか？",
      "東京23区はすべて「18歳到達後最初の3月31日まで」で、高校生相当までです。"
      "%s現在、23区で対象年齢に差はありません。誕生日ではなく年度末までなので、"
      "3月生まれと4月生まれで使える期間が1年近く変わります。" % CHECKED),
     ("所得制限はありますか？",
      "23区のうち%d区が公式ページで「所得制限はありません」と明記しています。"
      "残る%d区は所得制限についての記載が公式ページに見当たりませんでした。"
      "記載が無いことは「制限が無い」ことを意味しないため、本ツールでは"
      "「記載なし」として表示しています。心配な場合は区に直接ご確認ください。"
      % (len(seigen_nashi), len(seigen_none))),
     ("入院したときの食事代も助成されますか？",
      "ここが23区で最も割れる項目です。%d区が助成対象、%d区が対象外でした。"
      "東京都の基準では入院時食事療養標準負担額は自己負担（助成対象外）なので、"
      "対象にしている区は都基準への上乗せにあたります。"
      "また対象であっても、窓口では一旦支払って後から償還払いという運用の区が多くあります。"
      % (len(shokuji_taisho), len(shokuji_gai))),
     ("窓口で払うお金はゼロですか？",
      "東京都の基準は「通院1回につき最大200円の一部負担」ですが、23区の多くは"
      "この一部負担を無くしています。ただし都外の医療機関や医療証を扱わない医療機関では、"
      "いったん自己負担分を支払って後日払い戻しを受ける償還払いになります。"),
     ("引っ越したらどうなりますか？",
      "医療証は区ごとに交付されるため、転出入のたびに手続きが必要です。"
      "対象年齢は23区で同じですが、入院時食事療養費の扱いは区で違うので、"
      "転居先の条件を本ツールで確認してください。"),
     ("この情報はいつのものですか？",
      "%sに23区すべての公式ページを確認した内容です。制度は年度で変わるため、"
      "利用前に必ず各区の公式ページでご確認ください。本ツールには各区の出典リンクを載せています。" % CHECKED),
    ]

    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in FAQ]}, ensure_ascii=False)
    app_ld = json.dumps({
        "@context": "https://schema.org", "@type": "WebApplication",
        "name": "子ども医療費助成 東京23区ナビ", "url": TOOL_URL,
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
        {"@type": "ListItem", "position": 3, "name": "子ども医療費助成 東京23区ナビ"}]}, ensure_ascii=False)

    opts = "".join('<option value="%s">%s</option>' % (w["key"], w["name"]) for w in WARDS)
    rows = "".join(
        '<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td></tr>'
        % (w["name"],
           "なしと明記" if w["shotoku_seigen"] is False else "記載なし",
           "なし" if w["jiko_futan"] is False else "記載なし",
           "対象外" if "対象外" in w["shokuji_ryoyohi"] else "対象")
        for w in WARDS)
    src_rows = "".join(
        '<tr><td>%s</td><td><a href="%s" rel="noopener" target="_blank">%s</a></td><td>%s</td></tr>'
        % (w["name"], w["src"], w["src_label"], CHECKED) for w in WARDS)
    faq_html_s = "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a)
                           for i, (q, a) in enumerate(FAQ))
    DATA = json.dumps({w["key"]: w for w in WARDS}, ensure_ascii=False, separators=(",", ":"))

    tpl = io.open("scripts/_kodomo_iryo_body.html", encoding="utf-8").read()
    html = (tpl.replace("__TITLE__", TITLE).replace("__DESC__", DESC).replace("__OGD__", OGD)
            .replace("__URL__", TOOL_URL).replace("__H1__", H1).replace("__CSS__", CSS)
            .replace("__FAQLD__", faq_ld).replace("__APPLD__", app_ld).replace("__BCLD__", bc_ld)
            .replace("__OPTS__", opts).replace("__ROWS__", rows).replace("__SRCROWS__", src_rows)
            .replace("__FAQHTML__", faq_html_s).replace("__DATA__", DATA)
            .replace("__SLUG__", TOOL_SLUG).replace("__CHECKED__", CHECKED)
            .replace("__NTAISHO__", str(len(shokuji_taisho))).replace("__NGAI__", str(len(shokuji_gai)))
            .replace("__OISIX__", OISIX))
    os.makedirs("tools/%s" % TOOL_SLUG, exist_ok=True)
    io.open("tools/%s/index.html" % TOOL_SLUG, "w", encoding="utf-8").write(html)
    print("written: tools/%s/index.html  %d chars" % (TOOL_SLUG, len(html)))


# ============================================================ 記事
FAQ_ART = [
 ("東京23区の子ども医療費助成に差はありますか？",
  "対象年齢には差がありません。23区すべて「18歳到達後最初の3月31日まで（高校生相当）」です。"
  "差がつくのは入院時食事療養費の扱いで、%d区が助成対象、%d区が対象外でした。"
  "東京都の基準では入院時食事療養標準負担額は自己負担なので、対象にしている区は"
  "都基準への上乗せにあたります。" % (len(shokuji_taisho), len(shokuji_gai))),
 ("「23区は高校生まで無料」というのは正しいですか？",
  "対象年齢と窓口の自己負担については概ね正しい表現です。ただし入院した場合の食事代は"
  "%d区で助成対象外なので、「完全に無料」とは言えません。また対象としている区でも、"
  "窓口では一旦支払って後から償還払いという運用が多く、その場で無料になるわけではありません。"
  % len(shokuji_gai)),
 ("所得制限はどうなっていますか？",
  "23区のうち%d区が公式ページで「所得制限はありません」と明記しています。"
  "残る%d区は所得制限についての記載が見当たりませんでした。"
  "記載が無いことは制限が無いことを意味しないため、本記事では「記載なし」として扱っています。"
  % (len(seigen_nashi), len(seigen_none))),
 ("東京都の基準はどうなっていますか？",
  "都の基準は「通院1回につき最大200円の一部負担あり」「入院時食事療養標準負担額は自己負担」です。"
  "都のページ自身が「区市町村によって助成範囲が異なり、窓口負担のない区市町村もあります」と"
  "明記しています。つまり区ページに「自己負担なし」「食事代も助成」と書かれていれば、"
  "それは区独自の上乗せです。"),
 ("区外や都外の病院にかかったときは？",
  "医療証を扱わない医療機関や都外の医療機関では、窓口でいったん自己負担分を支払い、"
  "後日区に申請して払い戻しを受ける償還払いになります。これは23区で共通の運用です。"),
 ("引っ越すと手続きは必要ですか？",
  "必要です。医療証は区ごとに交付されるため、転出入のたびに手続きが要ります。"
  "対象年齢は23区で同じですが、入院時食事療養費の扱いは区で違うので、"
  "転居先の条件を確認してください。"),
]


def build_article():
    slug = "kodomo-iryohi-data"
    p = []
    p.append(
        "<blockquote><strong>「東京23区は高校生まで医療費無料」で片づけると、入院したときの食事代を見落とします。</strong>"
        "23区すべての公式ページを確認したところ、対象年齢は全区とも「18歳到達後最初の3月31日まで」で差がありませんでした。"
        "一方で入院時食事療養費は<strong>%d区が助成対象、%d区が対象外</strong>に割れています。"
        "東京都の基準ではこの食事代は自己負担なので、対象にしている区は都基準への上乗せです。</blockquote>"
        % (len(shokuji_taisho), len(shokuji_gai)))

    p.append('<h2 id="kijun">まず東京都の基準を押さえる</h2>')
    p.append(table(["項目", "東京都の基準"],
                   [("窓口の自己負担", TOKYO_KIJUN["jiko_futan"]),
                    ("入院時食事療養費", TOKYO_KIJUN["shokuji_ryoyohi"])], ["", ""]))
    p.append("<p>%s <strong>したがって、区のページに「自己負担なし」「食事代も助成」と書かれていれば、"
             "それは区が独自に上乗せしている部分です。</strong></p>" % TOKYO_KIJUN["note"])

    p.append('<h2 id="nenrei">対象年齢は23区で差がない</h2>')
    p.append("<p>23区すべてが「18歳到達後最初の3月31日まで」で、高校生相当までです。"
             "誕生日ではなく年度末までなので、<strong>3月生まれと4月生まれで使える期間が1年近く変わります</strong>。"
             "区を選ぶ材料としては、対象年齢は差になりません。</p>")

    p.append('<h2 id="shokuji">割れているのは入院時食事療養費</h2>')
    p.append("<p>助成対象としている区（%d区）と、対象外としている区（%d区）に分かれます。</p>"
             % (len(shokuji_taisho), len(shokuji_gai)))
    p.append("<h3>助成対象としている区</h3>")
    p.append("<p>%s</p>" % "・".join(w["name"] for w in shokuji_taisho))
    p.append("<h3>対象外としている区</h3>")
    p.append("<p>%s</p>" % "・".join(w["name"] for w in shokuji_gai))
    p.append("<p>ただし対象であっても、窓口で一旦支払って後から償還払いという運用の区が多くあります。"
             "その場で無料になるわけではない点に注意してください。"
             "足立区は令和7年10月1日以降の入院分から助成を開始し、文京区は令和8年4月1日受診分からの"
             "新規開始で、それ以前の診療分は助成できないと明記しています。</p>")

    p.append('<h2 id="shotoku">所得制限は「なし」と書いている区と、書いていない区がある</h2>')
    p.append("<p>%d区が「所得制限はありません」と公式ページに明記しています。"
             "残る%d区は所得制限についての記載が見当たりませんでした。"
             "<strong>記載が無いことは制限が無いことを意味しません。</strong>"
             "本記事では推測せず「記載なし」として扱っています。</p>"
             % (len(seigen_nashi), len(seigen_none)))
    p.append("<p>記載なしの区：%s</p>" % "・".join(w["name"] for w in seigen_none))

    p.append('<h2 id="ichiran">東京23区の一覧</h2>')
    p.append("<p>各区の公式ページを%sに確認した内容です。文言は原文にもとづきます。</p>" % CHECKED)
    p.append(table(["区", "対象年齢", "所得制限", "自己負担", "入院時食事療養費"],
                   [(w["name"], w["age_limit_class"],
                     "なしと明記" if w["shotoku_seigen"] is False else "記載なし",
                     "なし" if w["jiko_futan"] is False else "記載なし",
                     "対象外" if "対象外" in w["shokuji_ryoyohi"] else "対象")
                    for w in WARDS], ["", "", "", "", ""]))

    p.append('<h2 id="chui">調べるときに間違えやすいところ</h2>')
    p.append("<h3>医療証の呼び方が区で違う</h3>")
    p.append("<p>「マル乳・マル子・マル青」という通称を公式に使っている区と、"
             "「乳幼児医療証・子ども医療証・高校生等医療証」という正式名称しか使わない区があります。"
             "豊島区・世田谷区は通称を公式ページで使っていません。検索するときは両方で当たってください。</p>")
    p.append("<h3>都外・区外は償還払い</h3>")
    p.append("<p>医療証を扱わない医療機関や都外の医療機関では、窓口でいったん自己負担分を支払い、"
             "後日区に申請して払い戻しを受けます。これは23区で共通です。</p>")
    p.append("<h3>自己負担の比較は書きぶりに幅がある</h3>")
    p.append("<p>「窓口での支払いは不要」と明示している区もあれば、「自己負担分を助成します」とだけ書いて"
             "金額に触れていない区もあります。後者は実質ゼロ負担と読めますが断定できません。"
             "本記事では区ページの書きぶりをそのまま扱い、明示が無いものは「記載なし」としています。"
             "<strong>この項目だけで区を比べるのは適切ではありません。</strong></p>")
    p.append("<h3>まとめサイトの「無料」は範囲が曖昧</h3>")
    p.append("<p>「18歳まで無料」という表現は対象年齢と窓口負担を指していることが多く、"
             "入院時食事療養費まで含んでいるとは限りません。実際に%d区が対象外です。</p>"
             % len(shokuji_gai))

    p.append('<h2 id="calc">自分の場合を調べる</h2>')
    p.append('<p><a href="/tools/%s/">子ども医療費助成 東京23区ナビ</a>で、'
             'お子さんの生年月日と区を選ぶと、助成が切れる日とその区の条件が出典つきで出ます。</p>'
             % TOOL_SLUG)

    p.append("""
<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/tools/kodomo-iryohi-jichitai/">子ども医療費助成 東京23区ナビ</a></li>
<li><a href="/articles/sangokea-josei/">産後ケアの助成はいくら？非課税世帯の減免と所得を問わない減額枠</a></li>
<li><a href="/articles/shussan-mushouka/">出産費用の無償化はいつから？決まっていることと、まだ決まっていないこと</a></li>
<li><a href="/articles/daredemo-tsuen-ryokin/">こども誰でも通園制度の料金はいくら？46自治体の実額と減免</a></li>
<li><a href="/tools/sangokea-ryokin/">産後ケアの料金はいくら？自治体別の自己負担</a></li>
</ul>""")
    p.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    p.append(faq_html(FAQ_ART))
    p.append(source_list([(w["src"], "%s｜%s" % (w["name"], w["src_label"])) for w in WARDS]))

    write(slug,
          "子ども医療費助成は東京23区でどう違う？入院時食事代が%d区で対象外" % len(shokuji_gai),
          "子ども医療費助成は東京23区でどう違う？｜差がつくのは入院時の食事代",
          "子ども医療費助成の対象年齢は東京23区すべて「18歳到達後最初の3月31日まで」で差がありません。"
          "差がつくのは入院時食事療養費の扱いで、%d区が助成対象、%d区が対象外でした。"
          "東京都の基準ではこの食事代は自己負担なので、対象にしている区は都基準への上乗せです。"
          "23区すべての公式ページを確認し、所得制限の記載の有無まで出典つきで整理しました。確認日は%s。"
          % (len(shokuji_taisho), len(shokuji_gai), CHECKED),
          "23区とも高校生相当まで。差がつくのは入院時食事代で、%d区が対象外です。" % len(shokuji_gai),
          FAQ_ART, "\n".join(p), TODAY, CHECKED,
          "医療費が助成されても、日々の負担は残る",
          "医療費の助成は制度で決まっていて、こちらで動かせる余地はありません。"
          "一方で日々の家事の総量は今日から減らせます。")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build_tool()
    build_article()
    print("食事療養費 対象%d区 / 対象外%d区" % (len(shokuji_taisho), len(shokuji_gai)))

# -*- coding: utf-8 -*-
"""結婚新生活支援バンクから派生記事を出す（2026-09-01）

なぜ:
バンクは61自治体を実査したのに面を1つ（一覧記事＋ツール）しか出していなかった。
GA4を入れて分かったとおり、データ記事は流入の49%がAI（chatgpt・copilot）経由で、
これはGSCに一切出ない。**追加の実査ゼロで面を増やせるのがバンクの本体**なので、
同じ正本 `_kekkon_data.py` から切り口を変えて出す。

出力:
  articles/kekkon-hojokin-tokyo/   東京編（狙う語「結婚 補助金 東京」256／「新婚 補助金 東京」312・実測）
  articles/kekkon-hojokin-reigai/  年齢・所得の例外編

狙う語の検索数（2026-09-01 aramakijake実測・Google推定/月）:
  結婚 補助金 東京 256 ／ 新婚 補助金 東京 312 → 東京編は需要あり
  結婚 補助金 年齢制限・所得制限 → いずれも未収録（計測下限未満）
  → **例外編は検索需要では正当化できない。** それでも出すのは、49歳まで対象の自治体や
    所得750万円まで認める自治体の一覧が他にどこにも無い一次情報で、AIに引かれる型だから。
    検索から取れる想定はしていない（判定はGA4のAI経由セッションで行う）。

数値はすべて _kekkon_data.py から流し込む。手で転記しない。
"""
import importlib.util
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BASE, "scripts", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


K = _load("build_kekkon")          # 共通部品（esc / man / tbl / STYLE / CTA など）を再利用する
M, BY_PREF, OVER39, RICH = K.M, K.BY_PREF, K.OVER39, K.RICH
esc, man, tbl = K.esc, K.man, K.tbl
CHECKED, TODAY = K.CHECKED, K.TODAY


def page(slug, title, desc, ogd, h1, body, faq):
    url = "https://www.noe-match.com/articles/%s/" % slug
    faqld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in faq]}, ensure_ascii=False)
    artld = json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": title,
        "description": desc, "inLanguage": "ja", "datePublished": TODAY, "dateModified": TODAY,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "author": {"@type": "Organization", "name": "Noe編集部",
                   "url": "https://www.noe-match.com/about.html"},
        "publisher": {"@type": "Organization", "name": "Noe結婚設計室",
                      "url": "https://www.noe-match.com/"}}, ensure_ascii=False)
    bcld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
        {"@type": "ListItem", "position": 2, "name": "記事一覧", "item": "https://www.noe-match.com/articles/"},
        {"@type": "ListItem", "position": 3, "name": h1}]}, ensure_ascii=False)
    faq_html = "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a)
                         for i, (q, a) in enumerate(faq))
    head = ("<!DOCTYPE html>\n<html lang=\"ja\">\n<head>\n" + K.GA4 + "\n"
            "<meta charset=\"UTF-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            "<title>" + esc(title) + "</title>\n"
            "<meta name=\"description\" content=\"" + esc(desc) + "\">\n"
            "<link rel=\"canonical\" href=\"" + url + "\">\n"
            "<meta property=\"og:title\" content=\"" + esc(title) + "\">\n"
            "<meta property=\"og:description\" content=\"" + esc(ogd) + "\">\n"
            "<meta property=\"og:type\" content=\"article\">\n"
            "<meta property=\"og:url\" content=\"" + url + "\">\n"
            "<meta property=\"og:site_name\" content=\"Noe結婚設計室\">\n"
            "<meta property=\"og:locale\" content=\"ja_JP\">\n"
            "<meta name=\"twitter:card\" content=\"summary_large_image\">\n"
            "<meta name=\"twitter:title\" content=\"" + esc(title) + "\">\n"
            "<meta name=\"twitter:description\" content=\"" + esc(ogd) + "\">\n"
            "<link href=\"https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900"
            "&family=Noto+Serif+JP:wght@500;600;700;900&display=swap\" rel=\"stylesheet\">\n"
            + K.STYLE + "\n"
            "<style>table.cmp td{vertical-align:top;font-size:.84rem;line-height:1.8}\n"
            ".note{font-size:.8rem;color:#6b7178;line-height:1.9}</style>\n"
            "<script type=\"application/ld+json\">" + faqld + "</script>\n"
            "<script type=\"application/ld+json\">" + artld + "</script>\n"
            "<script type=\"application/ld+json\">" + bcld + "</script>\n"
            "</head>\n<body>\n" + K.HEADER + "\n<div class=\"wrap\">\n"
            "<div class=\"breadcrumb\"><a href=\"/\">ホーム</a> ＞ "
            "<a href=\"/articles/\">記事一覧</a> ＞ " + h1 + "</div>\n<article>\n<h1>" + h1 + "</h1>\n"
            "<p style=\"font-size:.78rem;color:#8a8f95;margin:6px 0 20px\">公開 " + TODAY
            + "／出典は各自治体および各都県の公式ページ。" + CHECKED + "に全件確認</p>\n"
            "<p class=\"pr-notice\">本ページはプロモーションを含みます。記事内に広告主から成果報酬を"
            "受け取るリンクが含まれます。掲載内容は編集部の基準で作成しており、報酬の有無で評価を"
            "変えていません。</p>\n")
    tail = ("\n<h2 id=\"faq\">よくある質問</h2>\n" + faq_html + "\n</article>\n"
            + K.line_cta("article", slug, "制度が変わったらお知らせします",
                         "自治体の結婚・子育て支援の公表値を月1回まとめて配信します。<br>"
                         "調べてほしい自治体があれば、追加後そのままトークでどうぞ。")
            + "\n</div>\n" + K.FOOTER_ART
            + "\n<button id=\"top\" onclick=\"scrollTo({top:0,behavior:'smooth'})\">↑</button>\n"
              "</body>\n</html>")
    return head + body + tail


def sources(entries, intro):
    items = []
    seen = set()
    for m in entries:
        if m["src"] in seen:
            continue
        seen.add(m["src"])
        items.append('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>'
                     % (esc(m["src"]), esc(m["src_label"])))
    return ("<h2 id=\"src\">出典</h2>\n<p>" + intro + "</p>\n"
            "<ul style=\"font-size:.84rem;line-height:2\">\n" + "\n".join(items) + "\n</ul>")


# ============================================================
# 東京編
# ============================================================
def tokyo():
    tk = BY_PREF["東京都"]
    near = sorted([m for m in M if m["pref"] != "東京都"], key=lambda m: -m["max_yen"])[:8]
    rows = [[esc(m["muni"] + "（" + m["pref"].replace("県", "") + "）"), man(m["max_yen"]),
             esc(m["special"] or m["program"])] for m in near]
    body = (
        "<h2 id=\"matome\">結論</h2>\n<ul>\n"
        "<li>東京都の公式ポータル「TOKYOふたりSTORY」の区市町村施策一覧で、結婚に伴う住居費・"
        "引越費用の補助として載っているのは<strong>立川市と青梅市の2市だけ</strong>でした。</li>\n"
        "<li>そのうち<strong>青梅市は制度が変わっています</strong>。住居費の補助は終了し、"
        "「おふたりOmeでとう！お祝い金」2.2万円と、婚姻から5年経過後に住宅を取得している場合の"
        "応援金（10万円＋加算最大50万円）に移りました。旧ページは" + CHECKED + "時点で表示できません。</li>\n"
        "<li>つまり<strong>結婚のタイミングで住居費・引越費用が戻る制度を運用している東京都内の自治体は、"
        "立川市だけ</strong>です。しかも立川市には29歳以下の60万円区分がなく、一律30万円が上限です。</li>\n"
        "<li><strong>東京23区で実施している区は確認できませんでした。</strong></li>\n"
        "<li>隣の3県では60自治体が実施しています。最高は市原市の最大130万円です。</li>\n</ul>\n"
        "<p>自治体ごとの条件は<a href=\"/tools/kekkon-shinseikatsu-jichitai/\">"
        "結婚新生活支援 一都三県ナビ</a>で出典つきに確認できます。</p>\n"

        "<h2 id=\"tachikawa\">立川市の条件</h2>\n"
        + tbl(["項目", "内容"], [
            ["上限額", "1世帯あたり最大30万円（年齢による区分なし）"],
            ["年齢", "婚姻届受理時に夫婦ともに39歳以下"],
            ["所得", "夫婦の合計所得500万円未満（貸与型奨学金の返済額は控除できる）"],
            ["対象経費", "住宅取得費・住宅賃借費・引越費用・リフォーム費用"],
            ["婚姻の期間", "令和8年1月1日〜令和9年3月31日"],
            ["申請期間", "令和8年4月1日〜令和9年3月31日（予算額に達した時点で終了）"],
            ["講座", "ライフデザイン支援講座などを夫婦ともに受講（1回目の申請時のみ）"],
        ])
        + "\n<p class=\"note\">立川市は予算額と残額をページで公表しています。申請前に残額を"
          "確認してください。</p>\n"

        "<h2 id=\"ome\">青梅市は「結婚時」から「5年後」に変わった</h2>\n"
        "<p>青梅市はかつて最大60万円の結婚新生活スタートアップ応援事業費補助金を実施していましたが、"
        "令和7年4月以降は次の2本立てになっています。</p>\n<ul>\n"
        "<li><strong>お祝い金 2.2万円</strong>（婚姻またはパートナーシップ関係になった日から1年以内に申請）</li>\n"
        "<li><strong>応援金 10万円＋加算最大50万円</strong>（婚姻から5年が経過する日までに市内で戸建て"
        "または分譲マンションを取得し、その日まで2人が居住していること）</li>\n</ul>\n"
        "<p>新居の初期費用が戻る制度ではなく、市内に住み続けて家を買った世帯への制度に切り替わっています。"
        "引っ越し直後の負担を軽くする目的で探している場合、青梅市は対象になりません。</p>\n"

        "<h2 id=\"rinken\">隣県との差</h2>\n"
        "<p>都内で新生活を始める世帯にとって、この制度は基本的に「隣県に住むなら見る制度」に"
        "なっています。上限額の高い順に8自治体を並べます。</p>\n"
        + tbl(["自治体", "上限額", "内容"], rows)
        + "\n<p>都心への通勤圏にも実施自治体があります。市川市（家賃・共益費 月2万円まで×12か月・"
          "所得600万円未満）、松戸市・船橋市・鎌ケ谷市（いずれも29歳以下60万円／39歳以下30万円）、"
          "川口市（上限10万円）、春日部市（対象経費の2分の1・上限30万円／29歳以下60万円）などです。"
          "住む場所を決める前に<a href=\"/tools/kekkon-shinseikatsu-jichitai/\">一都三県ナビ</a>で"
          "候補の自治体を引いておくと、金額がそのまま変わります。</p>\n"

        "<h2 id=\"kinrin\">東京に接する自治体の実施状況</h2>\n"
        "<p>通勤先を変えずに使える可能性があるのは、東京都に接するか近い次の自治体です。</p>\n"
        + tbl(["自治体", "上限額", "年齢", "所得", "対象経費"],
              [[esc(m["muni"] + "（" + m["pref"].replace("県", "") + "）"), man(m["max_yen"]),
                ("%d歳以下" % m["age_max"]) if m["age_max"] else "記載を確認できず",
                ("%s未満" % man(m["income_max"])) if m["income_max"] else "本文の注を参照",
                esc("・".join(m["costs"]))]
               for m in [x for x in M if x["slug"] in
                         ("ichikawa", "matsudo", "funabashi", "kamagaya", "shiroi",
                          "kawaguchi", "kasukabe", "ageo", "matsubushi", "sagamihara")]])
        + "\n<p>市川市は一時金ではなく家賃補助型で、家賃・共益費を月2万円まで12か月ぶん（最大24万円）。"
          "所得の上限も600万円未満と国基準より100万円広く取っています。川口市は上限10万円と低い一方、"
          "春日部市は対象経費の2分の1という補助率で、実費を上限まで見る自治体とは考え方が違います。"
          "相模原市は引越業者への支払いだけが対象で、上限15万円です。"
          "同じ制度名でも、一時金型・家賃補助型・補助率型が混ざっている点に注意してください。</p>\n"

        "<h2 id=\"toshien\">東京都自体が持っている新婚世帯向けの支援</h2>\n"
        "<p>住居費が現金で戻る制度ではありませんが、東京都は公式ポータルで次の2つを新婚世帯等への"
        "支援として案内しています。住まいの提供・入居支援という形です。</p>\n<ul>\n"
        "<li><strong>結婚予定者向けの公的住宅の提供</strong>（結婚予定のカップル向けに公的住宅を提供）</li>\n"
        "<li><strong>新婚・夫婦世帯入居さぽーと</strong>（東京都住宅供給公社の一般賃貸住宅で"
        "新婚世帯等への入居支援を実施）</li>\n</ul>\n"
        "<p>23区で新生活を始める場合、住居費が戻る制度は見つからないので、家賃そのものを下げる方向"
        "（公社住宅・区営住宅の募集）と、<a href=\"/articles/shinkon-koteihi-minaoshi/\">固定費の見直し</a>"
        "で吸収する形になります。</p>\n"

        "<h2 id=\"tetsuzuki\">立川市の申請の流れ</h2>\n"
        "<p>立川市は事前相談を求めています。要件を満たしているかを含め、企画政策課の窓口か電話で"
        "先に相談する流れです。</p>\n<ol>\n"
        "<li>企画政策課（市役所2階45番窓口）に事前相談</li>\n"
        "<li>補助金交付申請書を提出</li>\n"
        "<li>審査のうえ「立川市結婚新生活支援事業補助金交付決定通知書」で通知</li>\n</ol>\n"
        "<p>対象になるのは令和8年4月1日〜令和9年3月31日に支払った費用で、賃貸住宅の家賃・敷金・礼金・"
        "共益費・仲介手数料、引越業者等への支払い、住宅のリフォーム費、住宅取得費です。"
        "所得は令和7年分で見ますが、申請日が4月1日〜6月30日の場合は令和6年分になります。"
        "貸与型奨学金を返済している場合は年間返還額を控除できます。"
        "生活保護による住宅扶助など、他の公的制度による家賃補助を受けていないことも条件です。</p>\n"
        "<h2 id=\"naze\">なぜ23区にないのか</h2>\n"
        "<p>この制度は国の地域少子化対策重点推進交付金を使って市区町村が実施するもので、"
        "交付金は少子化対策と定住促進を目的にしています。転入超過が続く23区では、"
        "この交付金を使う動機が弱くなります。実際、千葉県30市町村・埼玉県17市町・神奈川県13市町村が"
        "実施していますが、その多くは都心から離れた地域です。</p>\n"
        "<p class=\"note\">※ここでの母集団は各都県が公表している一覧です。東京都の島しょ部など、"
        "都のポータルに掲載がない自治体が独自に実施している可能性は残ります。確認しだい追記します。</p>\n"

        "<h2 id=\"rel\">結婚の費用を先に見積もる</h2>\n"
        "<p>補助金は後払いで、契約と支払いを先に済ませる必要があります。"
        "<a href=\"/tools/kekkon-shikin-keisanki/\">結婚資金の計算機</a>で合計を出し、"
        "<a href=\"/tools/seikatsuhi-simulator/\">ふたりの生活費シミュレーター</a>で引っ越し後に"
        "毎月いくら残るかを見てから、戻る額を差し引くと順番が合います。"
        "全体の一覧は<a href=\"/articles/kekkon-shinseikatsu-data/\">一都三県61自治体の比較</a>、"
        "年齢と所得の例外は<a href=\"/articles/kekkon-hojokin-reigai/\">39歳・500万円を超えても"
        "対象になる自治体</a>、制度の仕組みは"
        "<a href=\"/articles/shinkon-hojokin/\">新婚生活の補助金はいくらもらえる？</a>に"
        "まとめています。</p>\n"
        + K.CTA_HIKKOSHI + "\n"
        + sources(tk + [m for m in near], "本記事の数値はすべて次の自治体・都県公式ページの記載です（"
                  + CHECKED + "確認）。制度は年度で変わるため、申請前に必ず公式ページでご確認ください。")
        .replace("</ul>",
                 '<li><a href="https://www.futari-story.metro.tokyo.lg.jp/support_policy/" '
                 'rel="noopener" target="_blank">行政による支援施策（区市町村による支援施策）'
                 '｜東京都 TOKYOふたりSTORY</a></li>\n'
                 '<li><a href="' + esc(K.ENDED[0]["src"]) + '" rel="noopener" target="_blank">'
                 + esc(K.ENDED[0]["src_label"]) + '</a></li>\n</ul>'))
    faq = [
        ("東京23区に結婚の補助金はありますか。",
         "住居費・引越費用を補助する結婚新生活支援については、実施している区を確認できませんでした。"
         "東京都の公式ポータルの区市町村施策一覧にも掲載がありません。区が独自に行う結婚関連の支援は、"
         "婚姻届のデザインや相談窓口が中心です。"),
        ("立川市の30万円は誰でも受け取れますか。",
         "いいえ。婚姻届受理時に夫婦ともに39歳以下、夫婦の合計所得が500万円未満、指定の講座を受講、"
         "などの要件をすべて満たす必要があります。交付額は支払った対象経費の実費までで、"
         "一律30万円が配られるわけではありません。予算額に達した時点で受付も終了します。"),
        ("青梅市の60万円はもう使えないのですか。",
         "結婚時に住居費が戻る形の補助は終了しています。現在は婚姻から1年以内に申請するお祝い金2.2万円と、"
         "婚姻から5年以内に市内で住宅を取得した場合の応援金（10万円＋加算最大50万円）です。"),
        ("都内に住みながら使える方法はありますか。",
         "この制度は転居先の自治体が実施していることが条件なので、都内であれば立川市に住む場合に限られます。"
         "隣県では市川市・松戸市・船橋市・川口市・春日部市など、都心への通勤圏にある自治体も実施しています。"),
        ("なぜ自治体によってこんなに差があるのですか。",
         "国が示す基準（39歳以下・世帯所得500万円未満・29歳以下は60万円、39歳以下は30万円）は目安で、"
         "実施するかどうかも上乗せするかどうかも市区町村が決めるためです。年齢を49歳まで広げた自治体や、"
         "所得750万円未満まで認める自治体もあります。"),
    ]
    title = "結婚の補助金、東京で使えるのは立川市だけ｜23区は実施ゼロ【%s確認】" % CHECKED
    desc = ("結婚に伴う住居費・引越費用の補助（結婚新生活支援）を東京都内で実施している自治体を"
            "都の公式ポータルから確認したところ、住居費が戻る制度を運用しているのは立川市だけでした。"
            "23区はゼロ、青梅市は制度を改組して住居費補助を終えています。隣県では市原市が最大130万円、"
            "富津市と南足柄市が70万円。都内と隣県の差を並べます。")
    ogd = "東京23区はゼロ、青梅市は制度改組。結婚時に住居費が戻る東京都内の自治体は立川市だけでした。"
    return page("kekkon-hojokin-tokyo", title, desc, ogd,
                "結婚の補助金、東京で使えるのは立川市だけだった", body, faq)


# ============================================================
# 例外編（年齢・所得）
# ============================================================
def reigai():
    age_rows = [[esc(m["muni"] + "（" + m["pref"].replace("県", "").replace("都", "") + "）"),
                 "%d歳以下" % m["age_max"],
                 "／".join("%s %s" % (esc(t[0]), man(t[1])) for t in m["tiers"]),
                 esc(m["age_note"] or "—")]
                for m in sorted(OVER39, key=lambda x: -x["age_max"])]
    inc_rows = [[esc(m["muni"] + "（" + m["pref"].replace("県", "").replace("都", "") + "）"),
                 "%s未満" % man(m["income_max"]), esc(m["income_note"] or "—")]
                for m in sorted(RICH, key=lambda x: -x["income_max"])]
    body = (
        "<h2 id=\"matome\">結論</h2>\n<ul>\n"
        "<li>国の基準は<strong>夫婦ともに婚姻日の年齢が39歳以下・世帯所得500万円未満</strong>。"
        "これは目安で、上乗せするかどうかは市区町村が決めます。</li>\n"
        "<li>年齢では<strong>" + str(len(OVER39)) + "自治体</strong>が39歳を超えても対象にしています。"
        "最も広いのは49歳以下（横須賀市・富津市・長生村・白子町）。</li>\n"
        "<li>所得では<strong>" + str(len(RICH)) + "自治体</strong>が500万円を超えても対象。"
        "最も広いのは長生村の750万円未満です。</li>\n"
        "<li>さらに<strong>所得の枠から外れた世帯にも出す自治体</strong>があります。"
        "東庄町は所得500万円以上の世帯に15万円、千葉市は500万円以上の枠を別に用意、"
        "四街道市は特定地域なら所得制限そのものがありません。</li>\n"
        "<li><strong>ほぼすべての自治体で、貸与型奨学金の返済額を所得から差し引けます。</strong>"
        "ここを知らずに諦めている世帯が出やすい部分です。</li>\n</ul>\n"

        "<h2 id=\"age\">39歳を超えても対象になる自治体</h2>\n"
        + tbl(["自治体", "年齢の上限", "区分", "備考"], age_rows)
        + "\n<p>横須賀市は29歳以下60万円・39歳以下30万円に加えて、40〜49歳に20万円の区分を作っています。"
          "富津市は年齢区分そのものを置かず、49歳以下なら一律70万円です。秦野市は40歳以下で、"
          "国基準よりちょうど1歳広い設定です。</p>\n"
        "<p class=\"note\">年齢は「婚姻日時点」で判定する自治体がほとんどです。愛川町は"
        "「年齢計算に関する法律により誕生日の前日に加算されるため、39歳以下とは誕生日の前々日まで」と"
        "明記しています。境目にいる場合は自治体に確認してください。</p>\n"

        "<h2 id=\"income\">所得500万円を超えても対象になる自治体</h2>\n"
        + tbl(["自治体", "所得の上限", "国基準との違い"], inc_rows)
        + "\n<p>ここでいう所得は年収ではなく、給与所得控除後の金額です。合計所得500万円は、"
          "給与だけの世帯でおおよそ年収680万円前後にあたると複数の自治体が説明しています。</p>\n"

        "<h2 id=\"waku\">所得の枠から外れても出る自治体</h2>\n"
        + tbl(["自治体", "扱い", "内容"], [
            ["東庄町（千葉）", "500万円以上でも15万円",
             "国の所得要件から外れた世帯にも町が15万円を交付する"],
            ["千葉市（千葉）", "500万円以上の枠が別にある",
             "所得500万円未満の枠と500万円以上の枠があり、申請状況も別々に公表されている"],
            ["四街道市（千葉）", "特定地域は所得制限なし",
             "千代田1〜5丁目に住民登録がある場合、所得要件が適用されない"],
        ])
        + "\n<h2 id=\"hanteibi\">年齢を「いつ」で判定するかが自治体で違う</h2>\n"
          "<p>ほとんどの自治体は婚姻届が受理された日の年齢で判定しますが、"
          "<strong>長瀞町と小鹿野町は交付申請時の年齢</strong>で判定すると定めています。"
          "婚姻から申請までに誕生日をまたぐ場合、この違いで区分が変わります。</p>\n"
          "<p>年齢の上限そのものを広げている自治体でも、上限額の区分（29歳以下かどうか）は"
          "別に判定されます。たとえば横須賀市は49歳以下まで対象ですが、60万円が出るのは"
          "夫婦ともに29歳以下の場合だけです。</p>\n"

          "<h2 id=\"keizoku\">上限に届かなかった分を翌年度に回せる自治体</h2>\n"
          "<p>対象経費が上限額に届かなかった場合に、翌年度へ残額を申請できる自治体があります。"
          "初年度は家賃だけで申請し、翌年度にリフォームぶんを足す、といった使い方ができます。</p>\n"
        + tbl(["自治体", "扱い"],
              [[esc(m["muni"] + "（" + m["pref"].replace("県", "").replace("都", "") + "）"),
                esc(m["special"])]
               for m in [x for x in M if x["slug"] in
                         ("narita", "katori", "shiroi", "yotsukaido", "misato",
                          "hadano", "nakai", "ogano", "miura", "togane")] if m["special"]])
          + "\n<p class=\"note\">中井町は「前年度と当該年度の補助上限額が異なる場合は前年度の上限額が"
            "適用される」と明記しています。熊谷市は逆に、令和9年度へ繰り越して申請できる予定はないと"
            "書いています。扱いは自治体ごとに違うので、初回申請の前に確認してください。</p>\n"

          "<h2 id=\"keisan\">所得の計算例</h2>\n"
          "<p>三浦市は公式ページで、給与収入から所得への換算例を挙げています。"
          "自分たちが基準内かを判断する目安になります。</p>\n"
        + tbl(["世帯の収入", "所得に換算すると", "合計所得500万円未満か"],
              [["夫婦ともに給与収入350万円ずつ", "それぞれ237万円・合計474万円", "満たす"],
               ["どちらか一方だけ給与収入650万円", "476万円", "満たす"],
               ["一方400万円・もう一方300万円", "276万円と202万円・合計478万円", "満たす"]])
          + "\n<p>佐倉市も、給与年収400万円と320万円の世帯で合計所得492万円になる例を示しています。"
            "年収の合計が700万円前後でも、所得では500万円を下回ることがあります。"
            "年収で判断して申請をやめてしまうのが、いちばんもったいない誤解です。</p>\n"
          "<p class=\"note\">佐倉市と八街市は、夫婦以外の同居者がいる場合はその所得も合算すると"
            "明記しています。実家に同居する場合は注意が必要です。</p>\n"
        + "\n<h2 id=\"shogakukin\">奨学金の返済額は所得から引ける</h2>\n"
          "<p>一都三県の多くの自治体が、貸与型奨学金を返済している場合に"
          "<strong>年間返済額を所得から控除できる</strong>と明記しています。合計所得が基準を"
          "少し超えていても、控除後に下回れば対象になります。申請には返済額が分かる書類が必要です。</p>\n"
          "<p>また松田町のように、夫婦の一方が離職して申請日時点で無職の場合は"
          "「所得なしとして算出する」と定めている自治体もあります。</p>\n"

        "<h2 id=\"tool\">自分の条件で確認する</h2>\n"
        "<p><a href=\"/tools/kekkon-shinseikatsu-jichitai/\">結婚新生活支援 一都三県ナビ</a>で"
        "自治体を選び、婚姻日の年齢と夫婦の合計所得を入れると、要件に当てはまるかと上限額が"
        "出典つきで出ます。一覧は<a href=\"/articles/kekkon-shinseikatsu-data/\">61自治体の比較</a>、"
        "東京都内の状況は<a href=\"/articles/kekkon-hojokin-tokyo/\">東京で使えるのは立川市だけ</a>、"
        "制度の仕組みは<a href=\"/articles/shinkon-hojokin/\">新婚生活の補助金はいくらもらえる？</a>に"
        "まとめています。</p>\n"
        + K.CTA_HIKARI + "\n"
        + sources(sorted(OVER39 + RICH + [m for m in M if m["slug"] in
                                          ("tohnosho", "chiba-shi", "yotsukaido", "matsuda")],
                         key=lambda x: x["muni"]),
                  "本記事の数値はすべて次の自治体公式ページの記載です（" + CHECKED
                  + "確認）。制度は年度で変わるため、申請前に必ず公式ページでご確認ください。"))
    faq = [
        ("40代でも結婚の補助金はもらえますか。",
         "自治体によります。一都三県では横須賀市（40〜49歳で20万円）、富津市（49歳以下で一律70万円）、"
         "長生村（40〜49歳で最大10万円）、白子町（49歳以下で15万円）が40代を対象にしています。"
         "秦野市は40歳以下までです。それ以外は国基準どおり39歳以下です。"),
        ("所得が500万円を少し超えています。諦めるしかないですか。",
         "2つ確認してください。1つは貸与型奨学金の返済です。ほぼすべての自治体が年間返済額を"
         "所得から控除できるとしており、控除後に基準を下回れば対象になります。もう1つは自治体の上限で、"
         "長生村は750万円未満、南足柄市は650万円未満、市川市と清川村は600万円未満まで対象です。"),
        ("所得と年収は違うのですか。",
         "違います。ここでいう所得は給与所得控除後の金額で、源泉徴収票の「給与所得控除後の金額」に"
         "あたります。合計所得500万円は、給与だけの世帯でおおよそ年収680万円前後にあたると"
         "複数の自治体が説明しています。"),
        ("年齢は申請日と婚姻日のどちらで判定しますか。",
         "多くの自治体が婚姻日（婚姻届が受理された日）で判定します。ただし長瀞町と小鹿野町は"
         "交付申請時の年齢で判定すると定めています。境目にいる場合は必ず自治体に確認してください。"),
        ("夫婦で年齢が違う場合はどちらで見ますか。",
         "上限額の区分は年齢の高い方で決まる自治体がほとんどです（鴻巣市・川島町・小鹿野町・毛呂山町などが"
         "明記しています）。29歳以下の60万円区分は「夫婦ともに29歳以下」が条件です。"),
    ]
    title = "結婚の補助金は39歳・500万円を超えても対象になる｜例外のある自治体【%s確認】" % CHECKED
    desc = ("結婚新生活支援の国の基準は「夫婦とも39歳以下・世帯所得500万円未満」ですが、一都三県では"
            "上乗せしている自治体があります。年齢は横須賀市・富津市・長生村・白子町が49歳以下、"
            "秦野市が40歳以下。所得は長生村750万円、南足柄市650万円、市川市と清川村が600万円。"
            "東庄町は所得500万円以上でも15万円。61自治体を全数確認して抜き出しました。")
    ogd = "年齢は最大49歳まで、所得は最大750万円まで。国基準を上乗せしている自治体を全数から抜き出しました。"
    return page("kekkon-hojokin-reigai", title, desc, ogd,
                "結婚の補助金、39歳・500万円を超えても対象になる自治体", body, faq)


def main():
    out = [("articles/kekkon-hojokin-tokyo", tokyo()),
           ("articles/kekkon-hojokin-reigai", reigai())]
    ng = []
    for slug, html in out:
        ng += K.lint(slug, html)
    if ng:
        print("LINT NG")
        for x in ng:
            print("  " + x)
        return 1
    for slug, html in out:
        d = os.path.join(BASE, slug)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        print("written: %s/index.html  %d chars" % (slug, len(html)))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

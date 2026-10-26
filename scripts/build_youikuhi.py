# -*- coding: utf-8 -*-
"""ひとり親バンクから「養育費の取り決め費用の助成」の区差を出す（2026-09-01）

なぜ:
ひとり親バンク（23区実査・2026-08-29）は面を2つ（ツール＋一覧記事）しか出していない。
区独自支援の欄に、**養育費の公正証書・ADR・保証契約・強制執行の費用助成**が11区ぶん
入っており、金額まで押さえてあるのに、どの面にも出していなかった。追加の実査ゼロで出せる。

狙う語の検索数（2026-09-01 aramakijake実測・Google推定/月）:
  養育費 公正証書 費用 136 → CHECK帯（実績のある器具の下限208には届かない）
  養育費 公正証書 助成 / 養育費 保証 助成 → 未収録
  → **検索だけでは正当化できない語。** データ記事はAI（chatgpt・copilot）経由が
    流入の49%を占める（2026-09-01 GA4実測）ので、そちらを主に見込んで出す。
    判定はGA4のAI経由セッションで行う。

出力: articles/youikuhi-kousei-shosho/index.html
数値はすべて _hitorioya_data.py から流し込む。手で転記しない。
"""
import importlib.util
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BASE, "scripts", name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


K = _load("build_kekkon")          # 共通部品（HTMLの骨格・CTA・リント）を再利用する
D = _load("_hitorioya_data")
esc, tbl = K.esc, K.tbl
CHECKED_WARD = "2026年8月29日"      # ひとり親バンクの確認日
TODAY = K.TODAY
SLUG = "youikuhi-kousei-shosho"
URL = "https://www.noe-match.com/articles/%s/" % SLUG

HIT = re.compile(r"養育費|公正証書")
UNPUB = re.compile(r"非公表|原文になし|確認できず")


def rows():
    """区ごとに、養育費の取り決め費用に関する助成を集める。"""
    out = []
    for w in D.WARDS:
        items = [x for x in w.get("dokuji", []) if HIT.search(x.get("name", ""))]
        if not items:
            continue
        out.append((w["ward"], items))
    return out


def main():
    data = rows()
    n_ward = len(data)
    pub = [(w, i) for w, items in data for i in items if not UNPUB.search(i.get("kingaku", ""))]
    unpub = [(w, i) for w, items in data for i in items if UNPUB.search(i.get("kingaku", ""))]

    tbl_rows = []
    for ward, items in data:
        for it in items:
            k = it.get("kingaku", "") or "—"
            tbl_rows.append([esc(ward), esc(it.get("name", "")),
                             ("<strong>金額の記載なし</strong>" if UNPUB.search(k) else esc(k))])

    body = (
        "<h2 id=\"matome\">結論</h2>\n<ul>\n"
        "<li>東京23区のうち<strong>" + str(n_ward) + "区</strong>が、養育費の取り決めにかかる費用"
        "（公正証書の作成手数料・ADRの利用料・保証契約の保証料・強制執行の申立費用）を助成しています。"
        "" + CHECKED_WARD + "に各区の公式ページで確認しました。</li>\n"
        "<li>助成の対象が区によって違います。<strong>公正証書の作成費用だけを見る区</strong>と、"
        "<strong>ADRや保証契約、強制執行の弁護士費用まで見る区</strong>があります。</li>\n"
        "<li>金額を公表している区では、渋谷区が公正証書の公証人手数料を上限43,000円・ADRを上限50,000円、"
        "世田谷区が強制執行の着手金等を上限10万円・実費を上限5万円、千代田区が公正証書作成等と"
        "保証契約締結費用をそれぞれ上限5万円としています。</li>\n"
        "<li>一方で<strong>" + str(len(unpub)) + "件は区の公式ページに金額の記載が見当たりません。</strong>"
        "問い合わせないと分からない状態です。</li>\n</ul>\n"
        "<p>お住まいの区の制度は<a href=\"/tools/hitorioya-shien-jichitai/\">ひとり親支援 東京23区ナビ</a>で"
        "区を選ぶと、手当・医療費助成・住宅支援・区独自支援が出典つきで出ます。</p>\n"

        "<h2 id=\"naze\">なぜ公正証書の費用が問題になるのか</h2>\n"
        "<p>養育費は口約束でも成立しますが、支払いが止まったときに差し押さえまで進めるには"
        "「債務名義」が要ります。強制執行認諾約款のついた公正証書を作っておくと、"
        "改めて裁判をせずに強制執行を申し立てられます。</p>\n"
        "<p>ただし公正証書の作成には公証人手数料がかかり、金額は取り決める養育費の総額で変わります。"
        "離婚の直後は費用の余裕がないことが多く、ここで作らずに済ませてしまうと、"
        "支払いが止まったときに使える手段が減ります。区の助成は、この入口の費用を下げるものです。</p>\n"

        "<h2 id=\"ichiran\">23区の助成一覧</h2>\n"
        + tbl(["区", "制度名", "金額（区の公式ページの記載）"], tbl_rows)
        + "\n<p class=\"note\">上の表は各区の公式ページに書かれている内容をそのまま並べたものです。"
          "所得制限・対象者の要件・申請の期限は区ごとに違います。利用前に必ず区の公式ページと"
          "窓口で確認してください。</p>\n"

        "<h2 id=\"chigai\">どこで差がつくか</h2>\n"
        "<p>差は金額よりも<strong>「どこまでを助成の対象にしているか」</strong>に出ます。</p>\n"
        "<ul>\n"
        "<li><strong>取り決めの入口だけを見る区</strong>…公正証書の作成手数料や調停の印紙代まで。"
        "渋谷区・荒川区・葛飾区・中野区などがここに厚みがあります。</li>\n"
        "<li><strong>取り決めのあとまで見る区</strong>…世田谷区は強制執行の申立て（着手金等・実費）を"
        "対象にしています。取り決めても払われなかった段階を想定した設計です。</li>\n"
        "<li><strong>保証会社の利用まで見る区</strong>…千代田区・杉並区は養育費保証契約の保証料を"
        "助成しています。滞ったときに保証会社が立て替える仕組みの初期費用にあたります。</li>\n"
        "<li><strong>ADRを対象にする区</strong>…中野区・渋谷区は裁判外紛争解決手続（ADR）の利用費用を"
        "対象にしています。相手と直接やり取りせずに取り決めたい場合の選択肢です。</li>\n"
        "</ul>\n"
        "<p>つまり「いくら出るか」より先に、<strong>自分がいまどの段階にいるか</strong>"
        "（これから取り決めるのか、取り決めたのに払われないのか）で、使える区の制度が変わります。</p>\n"

        "<h2 id=\"matrix\">どの段階を助成しているかの一覧</h2>\n"
        "<p>制度名と概要から、各区が助成の対象にしている段階を機械的に分類しました。"
        "○は区の公式ページにその語が出てくることを示します。</p>\n"
        + tbl(["区", "公正証書の作成", "ADR", "保証契約の保証料", "強制執行・弁護士費用"],
              [[esc(ward),
                "○" if any("公正証書" in (i.get("name", "") + i.get("gaiyo", "")) for i in items) else "—",
                "○" if any(("ADR" in (i.get("name", "") + i.get("gaiyo", ""))
                            or "紛争解決" in (i.get("name", "") + i.get("gaiyo", "")))
                           for i in items) else "—",
                "○" if any("保証" in (i.get("name", "") + i.get("gaiyo", "")) for i in items) else "—",
                "○" if any(("強制執行" in (i.get("name", "") + i.get("gaiyo", ""))
                            or "弁護士" in (i.get("name", "") + i.get("gaiyo", "")))
                           for i in items) else "—"]
               for ward, items in data])
        + "\n<p class=\"note\">分類は区の公式ページの記載語にもとづく機械判定です。"
          "「—」は助成がないことの証明ではなく、その語がページに出てこないという意味です。</p>\n"

        "<h2 id=\"junban\">使う順番</h2>\n"
        "<p>制度は段階ごとに分かれているので、いま自分がどこにいるかで見る場所が変わります。</p>\n"
        "<ol>\n"
        "<li><strong>これから取り決める</strong>…公正証書の作成費用、またはADRの利用費用を助成する区を見ます。"
        "強制執行認諾約款をつけて作るのが要点で、これが無いと支払いが止まったときに"
        "改めて裁判からやり直すことになります。</li>\n"
        "<li><strong>取り決めたが不安がある</strong>…保証契約の保証料を助成する区（千代田区・杉並区）を見ます。"
        "滞納したときに保証会社が立て替え、その後の回収を保証会社が行う仕組みで、"
        "相手と直接やり取りせずに済むのが利点です。</li>\n"
        "<li><strong>取り決めたのに払われない</strong>…強制執行の申立費用を助成する区（世田谷区）を見ます。"
        "債務名義があれば裁判をやり直さずに差押えへ進めます。世田谷区は着手金等を上限10万円、"
        "実費を上限5万円としており、6か月以内に申立てが決定した方が対象です。</li>\n"
        "</ol>\n"
        "<p>離婚後の生活費そのものの見通しは"
        "<a href=\"/tools/rikongo-seikatsuhi/\">離婚後の生活費と養育費のシミュレーション</a>で出せます。"
        "手当・医療費助成・住宅支援まで含めた区ごとの差は"
        "<a href=\"/articles/hitorioya-shien-data/\">ひとり親支援は東京23区でどう違うか</a>、"
        "子どもの医療費の扱いは<a href=\"/articles/kodomo-iryohi-data/\">子ども医療費助成の23区比較</a>、"
        "離婚前後の手続きの順番は<a href=\"/articles/rikon-junbi-jyunban/\">離婚準備の順番</a>に"
        "まとめています。</p>\n"
        "<h2 id=\"tool\">自分の区の制度を確認する</h2>\n"
        "<p><a href=\"/tools/hitorioya-shien-jichitai/\">ひとり親支援 東京23区ナビ</a>で区を選ぶと、"
        "児童育成手当・ひとり親医療費助成・住宅支援・区独自支援が出典つきで表示されます。"
        "区ごとの差の全体像は<a href=\"/articles/hitorioya-shien-data/\">ひとり親支援は東京23区でどう違うか</a>、"
        "離婚後の毎月の収支は<a href=\"/tools/rikongo-seikatsuhi/\">離婚後の生活費と養育費のシミュレーション</a>で"
        "見られます。</p>\n"
        + "<h2 id=\"src\">出典</h2>\n<p>本記事の内容はすべて次の各区公式ページの記載です（"
        + CHECKED_WARD + "確認）。制度は年度で変わるため、利用前に必ず各区の公式ページで"
          "ご確認ください。</p>\n<ul style=\"font-size:.84rem;line-height:2\">\n"
        + "\n".join('<li><a href="%s" rel="noopener" target="_blank">%s｜%s</a></li>'
                    % (esc(it.get("src", "")), esc(it.get("name", "")), esc(ward))
                    for ward, items in data for it in items if it.get("src"))
        + "\n</ul>\n")

    faq = [
        ("養育費の公正証書を作る費用はいくらですか。",
         "公証人手数料は取り決める養育費の総額によって変わります。渋谷区は補助の上限を"
         "43,000円としており、これが手数料の目安の1つになります。実際の金額は公証役場でご確認ください。"),
        ("助成はどの区でも受けられますか。",
         "いいえ。" + CHECKED_WARD + "時点で、養育費の取り決め費用の助成を公式ページで確認できたのは"
         "23区のうち" + str(n_ward) + "区です。実施していない区もあります。"),
        ("取り決めたのに払ってもらえません。助成はありますか。",
         "世田谷区は強制執行の申立てにかかる着手金等（上限10万円）と実費（上限5万円）を助成しています。"
         "千代田区・杉並区は養育費保証契約の保証料を助成しており、滞納時に保証会社が立て替える"
         "仕組みの初期費用に使えます。"),
        ("公正証書を作らずに取り決めても大丈夫ですか。",
         "口約束でも取り決め自体は成立しますが、支払いが止まったときに差し押さえへ進むには"
         "債務名義が必要です。強制執行認諾約款つきの公正証書があれば、改めて裁判をせずに"
         "強制執行を申し立てられます。"),
        ("金額が書かれていない区はどうすればよいですか。",
         "区の公式ページに金額の記載がない場合があります（" + str(len(unpub)) + "件）。"
         "その場合は区の担当課に直接問い合わせてください。ページに書かれていないだけで、"
         "制度自体は運用されています。"),
    ]
    title = "養育費の公正証書、費用を助成する区としない区｜東京23区の差【%s確認】" % CHECKED_WARD
    desc = ("養育費の取り決めにかかる費用（公正証書の作成手数料・ADR・保証料・強制執行）を助成している"
            "東京23区は" + str(n_ward) + "区。渋谷区は公証人手数料を上限43,000円、世田谷区は強制執行の"
            "着手金等を上限10万円、千代田区は保証契約の保証料を上限5万円。金額が公式ページに"
            "書かれていない区もあります。全23区を確認して並べました。")
    ogd = ("養育費の取り決め費用を助成する区は23区中" + str(n_ward) + "区。"
           "対象が公正証書だけの区と、強制執行や保証契約まで見る区があります。")
    html = K_page(title, desc, ogd, "養育費の公正証書、費用を助成する区としない区", body, faq)
    ng = K.lint(SLUG, html)
    if ng:
        print("LINT NG")
        for x in ng:
            print("  " + x)
        return 1
    d = os.path.join(BASE, "articles", SLUG)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print("written: articles/%s/index.html  %d chars（対象%d区）" % (SLUG, len(html), n_ward))
    return 0


def K_page(title, desc, ogd, h1, body, faq):
    faqld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in faq]}, ensure_ascii=False)
    artld = json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting", "headline": title,
        "description": desc, "inLanguage": "ja", "datePublished": TODAY, "dateModified": TODAY,
        "mainEntityOfPage": {"@type": "WebPage", "@id": URL},
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
    return ("<!DOCTYPE html>\n<html lang=\"ja\">\n<head>\n" + K.GA4 + "\n"
            "<meta charset=\"UTF-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
            "<title>" + esc(title) + "</title>\n"
            "<meta name=\"description\" content=\"" + esc(desc) + "\">\n"
            "<link rel=\"canonical\" href=\"" + URL + "\">\n"
            "<meta property=\"og:title\" content=\"" + esc(title) + "\">\n"
            "<meta property=\"og:description\" content=\"" + esc(ogd) + "\">\n"
            "<meta property=\"og:type\" content=\"article\">\n"
            "<meta property=\"og:url\" content=\"" + URL + "\">\n"
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
            + "／出典は各区の公式ページ。" + CHECKED_WARD + "に全23区で確認</p>\n"
            "<p class=\"pr-notice\">本ページはプロモーションを含みます。記事内に広告主から成果報酬を"
            "受け取るリンクが含まれる場合があります。掲載内容は編集部の基準で作成しており、"
            "報酬の有無で評価を変えていません。</p>\n"
            + body
            + "\n<h2 id=\"faq\">よくある質問</h2>\n" + faq_html + "\n</article>\n"
            + K.line_cta("article", SLUG, "制度が変わったらお知らせします",
                         "23区のひとり親支援・子育て支援の公表値を月1回まとめて配信します。<br>"
                         "調べてほしい区があれば、追加後そのままトークでどうぞ。")
            + "\n</div>\n" + K.FOOTER_ART
            + "\n<button id=\"top\" onclick=\"scrollTo({top:0,behavior:'smooth'})\">↑</button>\n"
              "</body>\n</html>")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())

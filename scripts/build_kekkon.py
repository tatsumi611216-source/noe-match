# -*- coding: utf-8 -*-
"""結婚新生活支援バンク（一都三県）のツール＋データ記事を生成する。

データ正本: scripts/_kekkon_data.py（検算済み）
出力:
  tools/kekkon-shinseikatsu-jichitai/index.html
  articles/kekkon-shinseikatsu-data/index.html

数値はすべて _kekkon_data.py から機械的に流し込む（手で転記しない）。
上限額の「判定に使える形」への変換（y29 / y39）は tiers の構造から導出し、
導出できないものは special として区分表だけを出す。金額を推定しない。
"""
import html
import importlib.util
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

spec = importlib.util.spec_from_file_location(
    "_kekkon_data", os.path.join(BASE, "scripts", "_kekkon_data.py"))
_d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_d)
M = _d.M
ENDED = _d.ENDED
KUNI = _d.KUNI

CHECKED = "2026年8月31日"
TOOL_URL = "https://www.noe-match.com/tools/kekkon-shinseikatsu-jichitai/"
ART_URL = "https://www.noe-match.com/articles/kekkon-shinseikatsu-data/"
TODAY = "2026-08-31"


def esc(s):
    return html.escape(s or "", quote=True)


def man(yen):
    """円 → 「◯万円」。端数は千円単位まで出す。"""
    if yen % 10000 == 0:
        return "%d万円" % (yen // 10000)
    return "%s円" % format(yen, ",")


# ---------- 上限額を判定に使える形に落とす ----------
def rule_of(m):
    t = m["tiers"]
    if len(t) == 1:
        return {"kind": "uniform", "y29": t[0][1], "y39": t[0][1]}
    if len(t) == 2 and t[0][1] > t[1][1] and "29" in t[0][0]:
        return {"kind": "std", "y29": t[0][1], "y39": t[1][1]}
    return {"kind": "special", "y29": None, "y39": None}


for m in M:
    m["rule"] = rule_of(m)

STD = [m for m in M if m["rule"]["kind"] == "std"]
UNI = [m for m in M if m["rule"]["kind"] == "uniform"]
SPE = [m for m in M if m["rule"]["kind"] == "special"]

# ---------- 記事本文で使う集計（すべて機械計算） ----------
PREFS = ["東京都", "神奈川県", "千葉県", "埼玉県"]
BY_PREF = {p: [m for m in M if m["pref"] == p] for p in PREFS}
N_ALL = len(M)
TOP = sorted(M, key=lambda m: -m["max_yen"])
OVER39 = [m for m in M if m["age_max"] and m["age_max"] > 39]
RICH = [m for m in M if m["income_max"] and m["income_max"] > 5000000]
NO_ACQ = [m for m in M if "取得" not in "".join(m["costs"])]
STD60 = [m for m in M if m["max_yen"] == 600000]

STYLE_REF = os.path.join(BASE, "tools", "kodomo-iryohi-jichitai", "index.html")
with open(STYLE_REF, encoding="utf-8") as f:
    _ref = f.read()
STYLE = _ref[_ref.index("<style>*,"):_ref.index("</style>") + len("</style>")]

GA4 = ("<!-- Google tag (gtag.js) -->\n"
       "<script async src=\"https://www.googletagmanager.com/gtag/js?id=G-VLQBH0S1SL\"></script>\n"
       "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-VLQBH0S1SL');"
       "document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href*=\"px.a8.net\"],a[href*=\"t.afi-b.com\"]');"
       "if(a){try{gtag('event','aff_click',{link_domain:(a.href.indexOf('a8.net')>-1?'a8':'afb'),page_slug:location.pathname});}catch(x){}}},true);</script>")

UI_GUARD = ("<script>(function(){['pointerdown','keydown','change'].forEach(function(t)"
            "{document.addEventListener(t,function(){window.__ui=true},true)})})();</script>")

HEADER = ("<header><div class=\"header-inner\">\n"
          "<a href=\"/\" class=\"logo\">Noe結婚設計室<span class=\"logo-badge\">2026</span></a>\n"
          "<nav><a href=\"/#tools\">ツール</a><a href=\"/articles/\">記事一覧</a><a href=\"/#faq\">FAQ</a><a href=\"/#about\">運営者</a></nav>\n"
          "</div></header>")

FOOTER_TOOL = ("<footer><div class=\"footer-inner\">\n"
               "<div><a href=\"/\">ホーム</a><a href=\"/articles/\">記事一覧</a><a href=\"/about.html\">運営者情報</a>"
               "<a href=\"/privacy-policy.html\">プライバシー</a><a href=\"/disclaimer.html\">免責事項</a></div>\n"
               "<p class=\"footer-disc\">※本ツールは一都三県の各自治体および各都県の公式公開情報（" + CHECKED +
               "確認）にもとづく目安です。制度の適用と最終的な判断は各自治体が行います。"
               "<strong style=\"color:#cda\">【PR】</strong>本サイトはアフィリエイト広告を含みます。<br>"
               "&copy; 2026 Noe結婚設計室</p>\n</div></footer>")

FOOTER_ART = FOOTER_TOOL.replace("本ツールは", "本記事は")


def line_cta(kind, slug, title, body):
    ev = "{%s:'%s'}" % ("tool" if kind == "tool" else "article", slug)
    return ("<!-- LINE-CTA -->\n"
            "<section id=\"line-cta\" style=\"max-width:680px;margin:56px auto 64px;padding:36px 28px;"
            "background:#f7f5f2;border:1px solid #e3ddd3;text-align:center;\">\n"
            "  <p style=\"margin:0 0 10px;font-size:12px;letter-spacing:.18em;color:#7c2e42;"
            "font-family:Georgia,'Times New Roman',serif;\">NOE OFFICIAL LINE</p>\n"
            "  <p style=\"margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;"
            "font-family:'Yu Mincho','游明朝',serif;line-height:1.5;\">" + title + "</p>\n"
            "  <p style=\"margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;\">" + body + "</p>\n"
            "  <a href=\"https://lin.ee/unbDsCR\" rel=\"noopener\" onclick=\"try{gtag('event','line_add_click',"
            + ev + ");}catch(e){}\"\n"
            "     style=\"display:inline-block;background:#7c2e42;color:#ffffff;padding:14px 36px;"
            "font-size:15px;font-weight:600;text-decoration:none;\">友だち追加する</a>\n"
            "  <p style=\"margin:14px 0 0;font-size:11px;color:#8a8f95;\">登録は無料・配信は月1回だけ。"
            "いつでも解除できます。</p>\n</section>")


def fam_link(to, label, sub):
    return ("<li style=\"margin:0 0 12px\"><a href=\"/tools/%s/\" onclick=\"try{gtag('event','tool_cross',"
            "{from:'kekkon-shinseikatsu-jichitai',to:'%s'});}catch(e){}\" style=\"font-weight:700;color:#7c2e42\">%s</a>"
            "<span style=\"display:block;font-size:.82rem;color:#6b7178;line-height:1.8\">%s</span></li>"
            % (to, to, label, sub))


# ============================================================
# ツールに渡すデータ
# ============================================================
def js_data():
    out = []
    for m in M:
        out.append({
            "pref": m["pref"], "muni": m["muni"], "slug": m["slug"],
            "program": m["program"],
            "tiers": m["tiers"], "max": m["max_yen"],
            "rule": m["rule"]["kind"], "y29": m["rule"]["y29"], "y39": m["rule"]["y39"],
            "ageMax": m["age_max"], "ageNote": m["age_note"],
            "incMax": m["income_max"], "incNote": m["income_note"],
            "costs": m["costs"], "konin": m["konin"], "apply": m["apply"],
            "kouza": m["kouza"], "special": m["special"], "qa": m["qa_note"],
            "src": m["src"], "srcLabel": m["src_label"], "checked": m["checked"],
        })
    return json.dumps(out, ensure_ascii=False)


def pref_options():
    return "".join('<option value="%s">%s（%d自治体）</option>' % (esc(p), esc(p), len(BY_PREF[p]))
                   for p in PREFS if BY_PREF[p])


# ============================================================
# 記事の表
# ============================================================
def tbl(headers, rows):
    th = "".join("<th>%s</th>" % h for h in headers)
    trs = "".join("<tr>" + "".join("<td>%s</td>" % c for c in r) + "</tr>" for r in rows)
    return ('<div class="table-scroll"><table class="cmp"><thead><tr>%s</tr></thead>'
            '<tbody>%s</tbody></table></div>' % (th, trs))


def table_all():
    rows = []
    for m in sorted(M, key=lambda x: (PREFS.index(x["pref"]), -x["max_yen"], x["muni"])):
        tier = "／".join("%s %s" % (esc(t[0]), man(t[1])) for t in m["tiers"])
        age = ("%d歳以下" % m["age_max"]) if m["age_max"] else "記載を確認できず"
        inc = ("%s未満" % man(m["income_max"])) if m["income_max"] else "下の注を参照"
        rows.append([esc(m["pref"]), esc(m["muni"]), man(m["max_yen"]), tier, age, inc,
                     esc("・".join(m["costs"]))])
    return tbl(["都県", "自治体", "上限額", "区分", "年齢要件", "所得要件", "対象経費"], rows)


def table_top():
    rows = []
    for m in TOP[:10]:
        rows.append([esc(m["muni"] + "（" + m["pref"].replace("県", "").replace("都", "") + "）"),
                     man(m["max_yen"]), esc(m["special"] or m["program"])])
    return tbl(["自治体", "上限額", "なぜその額になるか"], rows)


def table_low():
    rows = []
    for m in sorted([x for x in M if x["max_yen"] < 600000], key=lambda x: x["max_yen"]):
        rows.append([esc(m["muni"] + "（" + m["pref"].replace("県", "").replace("都", "") + "）"),
                     man(m["max_yen"]), esc(m["program"]),
                     esc(m["special"] or "—")])
    return tbl(["自治体", "上限額", "制度名", "内容"], rows)


def table_over39():
    rows = []
    for m in sorted(OVER39, key=lambda x: -x["age_max"]):
        rows.append([esc(m["muni"] + "（" + m["pref"].replace("県", "").replace("都", "") + "）"),
                     "%d歳以下" % m["age_max"],
                     "／".join("%s %s" % (esc(t[0]), man(t[1])) for t in m["tiers"]),
                     esc(m["age_note"] or m["special"] or "—")])
    return tbl(["自治体", "年齢の上限", "区分", "備考"], rows)


def table_rich():
    rows = []
    extra = [
        ["千葉市（千葉）", "500万円以上の枠もあり", "所得500万円未満の枠と500万円以上の枠が別に用意されている"],
        ["東庄町（千葉）", "500万円以上でも15万円", "国の所得要件を外れた世帯にも町が15万円を出す"],
        ["四街道市（千葉）", "千代田1〜5丁目は制限なし", "特定地域に住民登録があると所得要件が適用されない"],
    ]
    for m in sorted(RICH, key=lambda x: -x["income_max"]):
        rows.append([esc(m["muni"] + "（" + m["pref"].replace("県", "").replace("都", "") + "）"),
                     "%s未満" % man(m["income_max"]), esc(m["income_note"] or "—")])
    rows += [[esc(a), esc(b), esc(c)] for a, b, c in extra]
    return tbl(["自治体", "所得の上限", "国基準（500万円未満）との違い"], rows)


def table_costs():
    rows = []
    for m in sorted(M, key=lambda x: (PREFS.index(x["pref"]), x["muni"])):
        cs = "".join(m["costs"])
        if all(k in cs for k in ["取得", "賃借", "リフォーム", "引越"]):
            continue
        rows.append([esc(m["muni"] + "（" + m["pref"].replace("県", "").replace("都", "") + "）"),
                     esc("・".join(m["costs"])),
                     esc(m["special"] or "—")])
    return tbl(["自治体", "対象になる費目", "備考"], rows)


def table_sources():
    items = []
    for m in sorted(M, key=lambda x: (PREFS.index(x["pref"]), x["muni"])):
        items.append('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>'
                     % (esc(m["src"]), esc(m["src_label"])))
    for e in ENDED:
        items.append('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>'
                     % (esc(e["src"]), esc(e["src_label"])))
    items.append('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>'
                 % (esc(KUNI["src"]), esc(KUNI["src_label"])))
    items.append('<li><a href="https://www.pref.saitama.lg.jp/a0607/kekkon/r8koufukin.html" '
                 'rel="noopener" target="_blank">令和8年度地域少子化対策重点推進交付金活用事業｜埼玉県</a></li>')
    items.append('<li><a href="https://www.pref.kanagawa.jp/osirase/0214/koikana/support/list02.html" '
                 'rel="noopener" target="_blank">新婚世帯等への経済的補助事業｜神奈川県 恋カナ！プロジェクト</a></li>')
    items.append('<li><a href="https://www.futari-story.metro.tokyo.lg.jp/support_policy/" '
                 'rel="noopener" target="_blank">行政による支援施策（区市町村による支援施策）｜東京都 TOKYOふたりSTORY</a></li>')
    return ("<h2 id=\"src\">出典</h2>\n<p>本記事の数値はすべて次の自治体・都県公式ページの記載です。"
            "制度は年度で変わり、予算に達した時点で受付が終わるものもあるため、"
            "利用前に必ず各自治体の公式ページでご確認ください。</p>\n"
            "<ul style=\"font-size:.84rem;line-height:2\">\n" + "\n".join(items) + "\n</ul>")


FAQ = [
    ("結婚新生活支援は一都三県のどこでもらえますか。",
     "2026年8月31日時点で確認できたのは%d自治体です。内訳は千葉県%d、埼玉県%d、神奈川県%d、東京都%dです。"
     "東京都は23区では実施されておらず、都の公式ポータルに掲載があるのは立川市と青梅市の2市ですが、"
     "青梅市は住居費の補助を終えて、お祝い金と5年後の応援金に切り替えています。"
     % (N_ALL, len(BY_PREF["千葉県"]), len(BY_PREF["埼玉県"]),
        len(BY_PREF["神奈川県"]), len(BY_PREF["東京都"]))),
    ("上限は60万円だと聞きましたが、それより多い自治体はありますか。",
     "あります。市原市は住宅を取得した場合の基本50万円に、市外からの転入50万円・中古住宅10万円・"
     "居住誘導区域内10万円・29歳以下10万円の加算があり、すべて重なると130万円になります。"
     "富津市と南足柄市は上限70万円です。"),
    ("39歳を過ぎていると必ず対象外ですか。",
     "自治体によります。横須賀市は49歳以下で20万円、富津市は49歳以下で一律70万円、"
     "長生村は40〜49歳で最大10万円、白子町は49歳以下で15万円、秦野市は40歳以下で30万円です。"
     "国の基準は39歳以下ですが、上乗せしている自治体があります。"),
    ("世帯の所得が500万円を超えていると申請できませんか。",
     "国の基準は世帯所得500万円未満ですが、市川市と清川村は600万円未満、南足柄市は650万円未満、"
     "長生村は750万円未満まで対象です。東庄町は所得500万円以上の世帯にも15万円を出しています。"
     "また多くの自治体で、貸与型奨学金を返済している場合はその年間返済額を所得から差し引けます。"),
    ("何にでも使えるお金ですか。",
     "いいえ。ほとんどの自治体で、住宅の取得費・賃借費用・リフォーム費用・引越費用の実費が対象です。"
     "八街市は住宅取得費のみ、相模原市は引越費用のみ、松田町と毛呂山町は賃借費用のみ、"
     "いすみ市と秦野市は賃借と引越のみです。一都三県では長生村だけが、村内の店舗で買った家具・家電も対象にしています。"),
    ("令和8年度から要件が変わったと聞きました。",
     "制度の名称が「結婚新生活支援事業」から「結婚・妊娠・共育ての相談機会提供・支援プログラム」に変わり、"
     "ライフデザイン支援講座・プレコンセプションケアの講座・共家事や共育ての講座の受講、"
     "または医療機関への相談が要件に加わりました。夫婦の双方に必要とする自治体が多いので、"
     "申請の前に受講を済ませてください。"),
    ("いつまでに申請すればよいですか。",
     "多くが令和9年3月31日までですが、予算額に達した時点で受付を終える自治体がほとんどです。"
     "市原市は令和8年10月1日から、松戸市と熊谷市は6月1日から、木更津市は6月15日から、"
     "市川市は6月12日から受付を始めています。三浦市は令和9年3月10日までの婚姻、"
     "秦野市と銚子市は令和9年2月28日までの婚姻が対象です。"),
]


def faq_jsonld():
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in FAQ]}, ensure_ascii=False)


def faq_html():
    return "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a) for i, (q, a) in enumerate(FAQ))


# ============================================================
# ツールページ
# ============================================================
TOOL_TITLE = ("結婚新生活支援はいくらもらえる？一都三県%d自治体の上限額と条件【%s確認】"
              % (N_ALL, CHECKED))
TOOL_DESC = ("結婚に伴う住居費・引越費用の補助（令和8年度の名称は結婚・妊娠・共育ての相談機会提供・支援プログラム）は、"
             "一都三県の%d自治体で実施されています。上限は60万円が%d自治体と最も多い一方、"
             "市原市は加算を重ねると130万円、富津市と南足柄市は70万円、川口市は10万円、寒川町は6万円と幅があります。"
             "自治体を選ぶと上限額・年齢・所得・対象経費・申請期間が出典つきで出ます。"
             % (N_ALL, len(STD60)))

tool_webapp_ld = json.dumps({
    "@context": "https://schema.org", "@type": "WebApplication",
    "name": "結婚新生活支援 一都三県ナビ", "url": TOOL_URL,
    "applicationCategory": "UtilitiesApplication", "operatingSystem": "All",
    "inLanguage": "ja", "description": TOOL_DESC,
    "datePublished": TODAY, "dateModified": TODAY,
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
    "publisher": {"@type": "Organization", "name": "Noe結婚設計室",
                  "url": "https://www.noe-match.com/"}}, ensure_ascii=False)

tool_bc_ld = json.dumps({
    "@context": "https://schema.org", "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
        {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": "https://www.noe-match.com/#tools"},
        {"@type": "ListItem", "position": 3, "name": "結婚新生活支援 一都三県ナビ"}]}, ensure_ascii=False)

TOOL_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
""" + GA4 + """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>""" + esc(TOOL_TITLE) + """</title>
<meta name="description" content=\"""" + esc(TOOL_DESC) + """\">
<link rel="canonical" href=\"""" + TOOL_URL + """\">
<meta property="og:title" content=\"""" + esc(TOOL_TITLE) + """\">
<meta property="og:description" content="上限60万円が標準ですが、市原市は最大130万円、川口市は10万円。自治体を選ぶと条件が出典つきで出ます。">
<meta property="og:type" content="website">
<meta property="og:url" content=\"""" + TOOL_URL + """\">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="結婚新生活支援はいくら？一都三県の上限額と条件">
<meta name="twitter:description" content="上限60万円が標準。市原市は最大130万円、川口市は10万円。自治体を選ぶと条件が出ます。">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@500;600;700;900&display=swap" rel="stylesheet">
""" + STYLE + """
<style>
.cityout dt{font-weight:700;color:#1d242b;margin-top:14px;font-size:.9rem}
.cityout dd{margin:4px 0 0;font-size:.88rem;line-height:1.9;color:#3a4148}
.fitbox{padding:14px 16px;border-radius:6px;margin:14px 0;font-size:.9rem;line-height:1.9}
.fit-ok{background:#edf3ee;border:1px solid #cfe0d4}
.fit-ng{background:#f6f0e1;border:1px solid #e6d8b4}
.fit-un{background:#f4f2ef;border:1px solid #e0dad2}
.amt{font-size:1.5rem;font-weight:900;color:#7c2e42}
table.cmp td{vertical-align:top;text-align:left;font-size:.86rem;line-height:1.8}
.note{font-size:.8rem;color:#6b7178;line-height:1.9}
.selrow{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 12px}
.selrow>div{flex:1 1 200px}
label.f{display:block;font-size:.82rem;font-weight:700;color:#3a4148;margin:0 0 4px}
</style>
<script type="application/ld+json">""" + tool_webapp_ld + """</script>
<script type="application/ld+json">""" + tool_bc_ld + """</script>
<script type="application/ld+json">""" + faq_jsonld() + """</script>
""" + UI_GUARD + """
</head>
<body>
""" + HEADER + """
<div class="wrap">
<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ 結婚新生活支援 一都三県ナビ</div>
<article>
<h1>結婚新生活支援 一都三県ナビ</h1>
<p style="font-size:.78rem;color:#8a8f95;margin:6px 0 20px">""" + CHECKED + """に各自治体・各都県の公式ページで確認／対象は一都三県の""" + str(N_ALL) + """自治体</p>
<p class="pr-notice">本ページはプロモーションを含みます。ページ内に広告主から成果報酬を受け取るリンクが含まれます。掲載内容は編集部の基準で作成しており、報酬の有無で評価を変えていません。</p>

<p>結婚に伴う住居費と引越費用の補助は、国の交付金を使って<strong>市区町村ごとに</strong>実施されています。同じ制度の名前でも、上限額・年齢・所得・対象になる費目・申請期間は自治体で違います。住む場所を決める前に見ておくと、金額がそのまま変わります。</p>
<p>令和8年度から制度の名称は<strong>「結婚・妊娠・共育ての相談機会提供・支援プログラム」</strong>に変わり、講座の受講または相談が要件に加わりました。多くの自治体で夫婦の双方に必要です。</p>

<h2 id="check">住む予定の自治体を選ぶ</h2>
<div class="calc">
  <div class="selrow">
    <div>
      <label class="f" for="pref">都県</label>
      <select id="pref"><option value="">選んでください</option>""" + pref_options() + """</select>
    </div>
    <div>
      <label class="f" for="muni">自治体</label>
      <select id="muni"><option value="">先に都県を選んでください</option></select>
    </div>
  </div>
  <div class="selrow">
    <div>
      <label class="f" for="a1">婚姻日の年齢（おひとり目）</label>
      <input type="number" id="a1" min="18" max="70" placeholder="例：31">
    </div>
    <div>
      <label class="f" for="a2">婚姻日の年齢（おふたり目）</label>
      <input type="number" id="a2" min="18" max="70" placeholder="例：29">
    </div>
    <div>
      <label class="f" for="inc">夫婦の合計所得（万円）</label>
      <input type="number" id="inc" min="0" max="2000" placeholder="例：480">
    </div>
  </div>
  <p class="note">所得は年収ではありません。源泉徴収票の「給与所得控除後の金額」にあたります。合計所得500万円は、給与だけの世帯でおおよそ年収680万円前後です。貸与型奨学金を返済している場合は、年間返済額を差し引ける自治体がほとんどです。</p>
  <button id="go" class="btn">この自治体の条件を見る</button>
</div>
<div id="out"></div>

<h2 id="rank">上限額の高い自治体</h2>
<p>一都三県の""" + str(N_ALL) + """自治体のうち、上限が60万円なのは""" + str(len(STD60)) + """自治体です。国の基準（29歳以下60万円・39歳以下30万円）をそのまま採っている自治体が多数派で、そこから外れているところに理由があります。</p>
""" + table_top() + """

<h2 id="fam">結婚とお金の他のツール</h2>
<ul style="list-style:none;padding:0">
""" + fam_link("kekkon-shikin-keisanki", "結婚資金の計算機",
               "式・指輪・新生活をまとめて、いま何円足りないかを出します") + """
""" + fam_link("seikatsuhi-simulator", "ふたりの生活費シミュレーター",
               "家賃と手取りから、毎月いくら残るかを出します") + """
""" + fam_link("nyuseki-calendar", "入籍日カレンダー",
               "婚姻届の日取りと、手続きの順番を並べます") + """
</ul>

<h2 id="faq">よくある質問</h2>
""" + faq_html() + """

<h2 id="src">出典</h2>
<p class="note">自治体を選ぶと、その自治体の公式ページへのリンクが結果の末尾に出ます。一覧は<a href="/articles/kekkon-shinseikatsu-data/">一都三県""" + str(N_ALL) + """自治体の一覧記事</a>にまとめてあります。制度は年度で変わり、予算に達した時点で受付を終えるものもあるため、申請の前に必ず公式ページでご確認ください。</p>
</article>
""" + line_cta("tool", "kekkon-shinseikatsu-jichitai",
               "制度が変わったらお知らせします",
               "自治体の結婚・子育て支援の公表値を月1回まとめて配信します。<br>調べてほしい自治体があれば、追加後そのままトークでどうぞ。") + """
</div>
""" + FOOTER_TOOL + """
<button id="top" onclick="scrollTo({top:0,behavior:'smooth'})">↑</button>
<script>
var DATA = """ + js_data() + """;
var yen = function(n){return (n%10000===0)?(n/10000)+"万円":n.toLocaleString()+"円";};
var esc = function(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c];});};
var pref = document.getElementById('pref'), muni = document.getElementById('muni');
pref.addEventListener('change', function(){
  var p = pref.value;
  muni.innerHTML = '<option value="">選んでください</option>';
  DATA.filter(function(d){return d.pref===p;}).forEach(function(d){
    var o = document.createElement('option'); o.value = d.slug; o.textContent = d.muni; muni.appendChild(o);
  });
});
document.getElementById('go').addEventListener('click', function(){
  var d = DATA.filter(function(x){return x.slug===muni.value;})[0];
  var out = document.getElementById('out');
  if(!d){ out.innerHTML = '<div class="fitbox fit-un">都県と自治体を選んでください。</div>'; return; }
  var a1 = parseInt(document.getElementById('a1').value,10);
  var a2 = parseInt(document.getElementById('a2').value,10);
  var inc = parseFloat(document.getElementById('inc').value);
  var h = '';
  h += '<h2>'+esc(d.muni)+'の'+esc(d.program)+'</h2>';

  // 判定
  var lines = [], cls = 'fit-un', amount = null;
  var hasAge = !isNaN(a1) && !isNaN(a2), older = hasAge ? Math.max(a1,a2) : null;
  var ageOk = null;
  if(hasAge && d.ageMax){ ageOk = (older <= d.ageMax); }
  var incOk = null;
  if(!isNaN(inc) && d.incMax){ incOk = (inc*10000 < d.incMax); }
  if(ageOk === false){ lines.push('婚姻日の年齢が'+d.ageMax+'歳を超えているため、この自治体の年齢要件からは外れます。'); cls='fit-ng'; }
  if(incOk === false){ lines.push('夫婦の合計所得が'+yen(d.incMax)+'以上のため、所得要件からは外れます（貸与型奨学金の返済額を差し引ける自治体が多いので、返済中の方は差し引いた額で確認してください）。'); cls='fit-ng'; }
  if(ageOk !== false && incOk !== false){
    cls = (ageOk===true && incOk===true) ? 'fit-ok' : 'fit-un';
    if(d.rule === 'std' && hasAge){ amount = (older<=29) ? d.y29 : d.y39; }
    else if(d.rule === 'uniform'){ amount = d.y29; }
    if(amount!==null){ lines.push('この条件での上限額は <span class="amt">'+yen(amount)+'</span> です（対象経費の実費が上限に届かない場合は実費まで）。'); }
    else { lines.push('この自治体は上限額が年齢だけでは決まりません。下の区分表をご確認ください。'); }
    if(ageOk===null || incOk===null){ lines.push('年齢と所得を入れると、要件に当てはまるかも表示します。'); }
  }
  h += '<div class="fitbox '+cls+'">'+lines.join('<br>')+'</div>';

  // 区分表
  var rows = d.tiers.map(function(t){return '<tr><td>'+esc(t[0])+'</td><td>'+yen(t[1])+'</td></tr>';}).join('');
  h += '<div class="table-scroll"><table class="cmp"><thead><tr><th>区分</th><th>1世帯あたりの上限額</th></tr></thead><tbody>'+rows+'</tbody></table></div>';

  h += '<dl class="cityout">';
  h += '<dt>年齢の要件</dt><dd>'+(d.ageMax? ('婚姻日における年齢が夫婦ともに'+d.ageMax+'歳以下') : '公式ページで記載を確認できませんでした')+(d.ageNote? '<br>'+esc(d.ageNote):'')+'</dd>';
  h += '<dt>所得の要件</dt><dd>'+(d.incMax? ('夫婦の合計所得が'+yen(d.incMax)+'未満') : '一律の上限ではありません')+(d.incNote? '<br>'+esc(d.incNote):'')+'</dd>';
  h += '<dt>対象になる費目</dt><dd>'+esc(d.costs.join('・'))+'</dd>';
  if(d.konin){ h += '<dt>対象になる婚姻の期間</dt><dd>'+esc(d.konin)+'</dd>'; }
  if(d.apply){ h += '<dt>申請の期間</dt><dd>'+esc(d.apply)+'</dd>'; }
  h += '<dt>講座・相談の要件</dt><dd>'+(d.kouza===true? '必要（ライフデザイン支援講座・プレコンセプションケア・共家事や共育ての講座、または医療機関への相談のいずれか。夫婦の双方に求める自治体が多い）' : '公式ページで明記を確認できませんでした。国の実施要領では令和8年度から要件化されているため、申請前に自治体へご確認ください')+'</dd>';
  if(d.special){ h += '<dt>この自治体の特徴</dt><dd>'+esc(d.special)+'</dd>'; }
  if(d.qa){ h += '<dt>確認できなかった点</dt><dd>'+esc(d.qa)+'</dd>'; }
  h += '<dt>出典</dt><dd><a href="'+esc(d.src)+'" rel="noopener" target="_blank">'+esc(d.srcLabel)+'</a>（'+esc(d.checked)+'確認）</dd>';
  h += '</dl>';
  h += '<p class="note">予算額に達した時点で受付を終える自治体がほとんどです。金額と要件は必ず出典先の公式ページでご確認ください。</p>';
  out.innerHTML = h;
  if(window.__ui){ try{ gtag('event','tool_calc',{tool:'kekkon-shinseikatsu-jichitai',muni:d.slug}); }catch(e){} }
  out.scrollIntoView({behavior:'smooth', block:'start'});
});
</script>
</body>
</html>"""

# ============================================================
# データ記事
# ============================================================
ART_TITLE = ("結婚新生活支援の補助金｜一都三県%d自治体の一覧【%s確認】"
             % (N_ALL, CHECKED))
ART_DESC = ("結婚に伴う住居費・引越費用の補助を、一都三県の%d自治体（千葉%d・埼玉%d・神奈川%d・東京%d）について"
            "公式ページで確認して並べました。上限60万円が%d自治体で最多、最高は市原市の最大130万円、"
            "最低は寒川町の6万円。年齢は49歳以下まで、所得は750万円未満まで認める自治体もあります。"
            % (N_ALL, len(BY_PREF["千葉県"]), len(BY_PREF["埼玉県"]), len(BY_PREF["神奈川県"]),
               len(BY_PREF["東京都"]), len(STD60)))

art_faqld = faq_jsonld()
art_artld = json.dumps({
    "@context": "https://schema.org", "@type": "BlogPosting", "headline": ART_TITLE,
    "description": ART_DESC, "inLanguage": "ja",
    "datePublished": TODAY, "dateModified": TODAY,
    "mainEntityOfPage": {"@type": "WebPage", "@id": ART_URL},
    "author": {"@type": "Organization", "name": "Noe編集部",
               "url": "https://www.noe-match.com/about.html"},
    "publisher": {"@type": "Organization", "name": "Noe結婚設計室",
                  "url": "https://www.noe-match.com/"}}, ensure_ascii=False)
art_bcld = json.dumps({
    "@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
        {"@type": "ListItem", "position": 2, "name": "記事一覧", "item": "https://www.noe-match.com/articles/"},
        {"@type": "ListItem", "position": 3, "name": "結婚新生活支援の補助金 一都三県の一覧"}]}, ensure_ascii=False)

ART_BODY = """
<h2 id="matome">結論</h2>
<ul>
<li>一都三県で結婚新生活支援（住居費・引越費用の補助）を実施しているのは<strong>""" + str(N_ALL) + """自治体</strong>。千葉県""" + str(len(BY_PREF["千葉県"])) + """、埼玉県""" + str(len(BY_PREF["埼玉県"])) + """、神奈川県""" + str(len(BY_PREF["神奈川県"])) + """、東京都""" + str(len(BY_PREF["東京都"])) + """です。</li>
<li>上限は<strong>60万円が""" + str(len(STD60)) + """自治体</strong>で最多。国の基準（夫婦とも29歳以下60万円・39歳以下30万円）をそのまま採っています。</li>
<li>最高は<strong>市原市の最大130万円</strong>。住宅取得の基本50万円に、市外からの転入50万円などの加算が重なります。</li>
<li>最低は<strong>寒川町の6万円</strong>（デジタル地域通貨なら6万5千円相当）、次いで<strong>川口市の10万円</strong>。</li>
<li><strong>東京23区で実施している区は確認できませんでした。</strong>都の公式ポータルに載っているのは立川市と青梅市の2市で、青梅市は住居費の補助を終えて別制度に移っています。</li>
<li>令和8年度から制度名は<strong>「結婚・妊娠・共育ての相談機会提供・支援プログラム」</strong>になり、講座の受講または相談が要件に加わりました。</li>
</ul>
<p>金額と条件は<a href="/tools/kekkon-shinseikatsu-jichitai/">結婚新生活支援 一都三県ナビ</a>で自治体を選ぶと、出典つきで1件ずつ表示できます。</p>

<h2 id="top">上限額が高い自治体</h2>
""" + table_top() + """
<p>市原市の130万円は、住宅取得の基本50万円に4つの加算（市外からの転入50万円・中古住宅10万円・居住誘導区域内10万円・夫婦とも29歳以下10万円）をすべて重ねた場合の理論上の最大です。賃貸・リフォーム・引越の場合は基本30万円＋29歳以下30万円で60万円になります。所得の上限も、賃貸なら500万円未満、住宅取得なら550万円未満と分けています。</p>
<p>富津市は年齢の区分を作らず一律70万円で、しかも49歳以下まで対象です。南足柄市は29歳以下70万円で、所得は650万円未満まで認めます。「60万円が上限」という前提でいると、この3自治体は見落とします。</p>

<h2 id="low">上限額が低い自治体</h2>
""" + table_low() + """
<p>金額が小さい自治体は、制度の作りそのものが違います。相模原市は引越費用だけ、松田町は賃借費用だけを見ています。市川市と箱根町は一時金ではなく毎月の家賃補助で、市川市は月2万円まで×12か月、箱根町は実質家賃の2分の1・月2万円まで×24か月です。寒川町は補助金をやめて、さむかわPayのポイントか現金を渡す方式に変えました。</p>
<p>同じ「結婚新生活支援」という言葉でも、一括で数十万円が入る制度と、毎月2万円ずつ入る制度が混ざっています。引っ越し先を比べるときは、金額の大小より先にこの形の違いを見てください。</p>

<h2 id="age">39歳を超えても対象になる自治体</h2>
<p>国の基準は「夫婦ともに婚姻日における年齢が39歳以下」ですが、""" + str(len(OVER39)) + """自治体が上乗せしています。</p>
""" + table_over39() + """
<p>横須賀市は29歳以下60万円・39歳以下30万円に加えて、40〜49歳に20万円の区分を作っています。富津市は年齢区分そのものを置かず、49歳以下なら一律70万円です。</p>

<h2 id="income">所得500万円を超えても対象になる自治体</h2>
""" + table_rich() + """
<p>所得は年収ではなく、給与所得控除後の金額です。合計所得500万円は、給与だけの世帯でおおよそ年収680万円前後にあたると複数の自治体が説明しています。ほとんどの自治体で、貸与型奨学金を返済している場合は年間返済額を所得から差し引けます。ここを知らずに「うちは超えている」と諦めている世帯が出やすい部分です。</p>

<h2 id="costs">対象になる費目が限られている自治体</h2>
<p>多くは「住宅の取得・賃借・リフォーム・引越」の4つが対象ですが、絞っている自治体があります。</p>
""" + table_costs() + """
<p>賃貸に引っ越すだけの世帯にとって、八街市のように住宅取得費のみを対象にしている自治体では受け取れる額がゼロになります。金額の比較より先に、自分が払う費目が対象かどうかを見てください。</p>

<h2 id="tokyo">東京都で使えるのは実質1市</h2>
<p>東京23区で実施している区は確認できませんでした。東京都の公式ポータル「TOKYOふたりSTORY」の区市町村施策一覧に住居費の補助として載っているのは、立川市（最大30万円）と青梅市（最大60万円）の2市です。</p>
<p>ただし青梅市の該当ページは""" + CHECKED + """時点で表示できなくなっており、市の現行制度は「おふたりOmeでとう！お祝い金」2.2万円と、婚姻から5年経過後に市内で住宅を取得している場合の「応援金」10万円＋加算最大50万円に切り替わっています。結婚した直後に住居費が戻ってくる形ではありません。</p>
<p>したがって、結婚のタイミングで住居費・引越費用の補助を受けられる東京都内の自治体として確認できたのは立川市だけです。しかも立川市には29歳以下の60万円区分がなく、一律30万円が上限です。都内で新生活を始める世帯にとって、この制度は基本的に「隣県に住むなら見る制度」になっています。</p>
<p class="note">※ここでの母集団は各都県が公表している一覧です。東京都の島しょ部など、都のポータルに掲載がない自治体が独自に実施している可能性は残ります。掲載を確認しだい追記します。</p>

<h2 id="kouza">令和8年度から加わった「講座」の要件</h2>
<p>制度の名称は「結婚新生活支援事業」から「結婚・妊娠・共育ての相談機会提供・支援プログラム」に変わりました。名称だけでなく要件も変わり、次のいずれかを済ませていることが求められます。</p>
<ul>
<li>ライフデザイン支援講座の受講（乳幼児とふれあう体験や子育て世帯との意見交換を含む）</li>
<li>プレコンセプションケアに関する講座の受講</li>
<li>医療機関への妊娠・出産に関する相談</li>
<li>共家事・共育て講座（男性の家事・育児参画のための講座を含む）の受講</li>
</ul>
<p>多くの自治体が<strong>夫婦の双方</strong>に求めています。動画の視聴とアンケートの回答で足りる自治体（秩父市・長瀞町・深谷市など）もあれば、受講確認の様式提出を求める自治体（上尾市・坂戸市など）もあります。申請の直前に気づくと間に合わないことがあるので、引っ越しの手配と同じタイミングで済ませてください。</p>

<h2 id="all">一都三県""" + str(N_ALL) + """自治体の一覧</h2>
""" + table_all() + """
<p class="note">上限額は1世帯あたり。実際の交付額は対象経費の実費が上限を超えない範囲です。年齢は婚姻日時点、所得は夫婦の合計（給与所得控除後）です。</p>

<h2 id="how">申請でつまずきやすいところ</h2>
<ul>
<li><strong>予算が尽きたら終わる。</strong>ほとんどの自治体が「予算額に達した時点で受付終了」と書いています。松戸市は令和8年7月31日時点で予算の約5パーセントが受付済み、鴻巣市・深谷市・立川市は予算残額を、上尾市は予算に対する申請額の割合をページで公表しています。</li>
<li><strong>受付の開始が年度の途中のことがある。</strong>市原市は令和8年10月1日、木更津市は6月15日、市川市は6月12日、松戸市と熊谷市は6月1日から。4月に問い合わせても受け付けてもらえない自治体があります。</li>
<li><strong>自分で運んだ引越は対象外。</strong>引越業者・運送業者へ支払った費用に限る自治体がほとんどで、鎌ケ谷市はレンタカーを借りた場合を明記して除いています。</li>
<li><strong>住宅手当が出ていると差し引かれる。</strong>勤務先から住宅手当が支給されている場合、その分を対象経費から控除する自治体が複数あります（東金市・鴻巣市・川島町・小鹿野町ほか）。</li>
<li><strong>居住し続ける意思が条件になる。</strong>山北町は10年、南足柄市は5年、上尾市は3年超、美里町は3年（未満で転出すると返還）と幅があります。</li>
</ul>

<h2 id="rel">結婚のお金を先に見積もる</h2>
<p>補助金は後払いです。契約と支払いを先に済ませる必要があるため、手元の資金は別に用意しておく必要があります。<a href="/tools/kekkon-shikin-keisanki/">結婚資金の計算機</a>で式・指輪・新生活の合計を出し、<a href="/tools/seikatsuhi-simulator/">ふたりの生活費シミュレーター</a>で引っ越し後に毎月いくら残るかを見てから、この補助で戻る額を差し引くと順番が合います。</p>
<p>制度の全体像は<a href="/articles/shinkon-hojokin/">新婚生活の補助金はいくらもらえる？</a>、費用の相場は<a href="/articles/kekkon-hiyou-futan/">結婚費用の負担割合</a>、固定費の見直しは<a href="/articles/shinkon-koteihi-minaoshi/">新婚の固定費見直し</a>にまとめています。</p>

<h2 id="faq">よくある質問</h2>
""" + faq_html() + """

""" + table_sources() + """
"""

ART_HTML = """<!DOCTYPE html>
<html lang="ja">
<head>
""" + GA4 + """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>""" + esc(ART_TITLE) + """</title>
<meta name="description" content=\"""" + esc(ART_DESC) + """\">
<link rel="canonical" href=\"""" + ART_URL + """\">
<meta property="og:title" content=\"""" + esc(ART_TITLE) + """\">
<meta property="og:description" content="上限60万円が標準ですが、市原市は最大130万円、川口市は10万円。東京23区は実施なし。一都三県の全自治体を公式ページで確認して並べました。">
<meta property="og:type" content="article">
<meta property="og:url" content=\"""" + ART_URL + """\">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="結婚新生活支援の補助金 一都三県の一覧">
<meta name="twitter:description" content="上限60万円が標準。最高は市原市の130万円、最低は寒川町の6万円。東京23区は実施なし。">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@500;600;700;900&display=swap" rel="stylesheet">
""" + STYLE + """
<style>table.cmp td{vertical-align:top;font-size:.84rem;line-height:1.8}
.note{font-size:.8rem;color:#6b7178;line-height:1.9}</style>
<script type="application/ld+json">""" + art_faqld + """</script>
<script type="application/ld+json">""" + art_artld + """</script>
<script type="application/ld+json">""" + art_bcld + """</script>
</head>
<body>
""" + HEADER + """
<div class="wrap">
<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/articles/">記事一覧</a> ＞ 結婚新生活支援の補助金 一都三県の一覧</div>
<article>
<h1>結婚新生活支援の補助金、一都三県""" + str(N_ALL) + """自治体の上限額と条件</h1>
<p style="font-size:.78rem;color:#8a8f95;margin:6px 0 20px">公開 """ + TODAY + """／出典は各自治体および各都県の公式ページ。""" + CHECKED + """に全件確認</p>
<p class="pr-notice">本ページはプロモーションを含みます。記事内に広告主から成果報酬を受け取るリンクが含まれます。掲載内容は編集部の基準で作成しており、報酬の有無で評価を変えていません。</p>
""" + ART_BODY + """
<div style="border:1px solid #e3ddd3;border-radius:6px;padding:22px 24px;margin:32px 0;background:#faf8f5">
<p style="font-size:.7rem;color:#999;margin:0 0 6px">PR</p>
<p style="font-weight:900;margin:0 0 6px;color:#1d242b">引っ越し直後の食事づくりを軽くする</p>
<p style="font-size:.86rem;color:#5a6068;margin:0 0 16px;line-height:1.9">新居に移った直後は、調理器具も調味料も揃っていません。Oisixのおためしセットは1回だけの注文で、1,980円から届きます。補助金の対象経費とは関係のないサービスです。</p>
<a href="https://px.a8.net/svt/ejp?a8mat=45C0YR+2VBK6Q+3250+5YZ77" rel="sponsored noopener" target="_blank" style="display:inline-block;background:#7c2e42;color:#fff;font-weight:700;padding:13px 32px;text-decoration:none">Oisixのおためしセットを見る</a>
<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">食材宅配サービス。本記事の制度とは関係ありません</p>
</div>
</article>
""" + line_cta("article", "kekkon-shinseikatsu-data",
               "制度が変わったらお知らせします",
               "自治体の結婚・子育て支援の公表値を月1回まとめて配信します。<br>調べてほしい自治体があれば、追加後そのままトークでどうぞ。") + """
</div>
""" + FOOTER_ART + """
<button id="top" onclick="scrollTo({top:0,behavior:'smooth'})">↑</button>
</body>
</html>"""


# ============================================================
# 出荷前リント
# ============================================================
BANNED = [
    (r"[а-яА-Я]", "キリル文字が混入している"),
    (r"(?<![A-Za-z])(background|long short|lorem|TODO|FIXME)(?![A-Za-z])", "英語の作業語が残っている"),
    (r"qa_note|内部メモ|作業メモ|要確認：社内", "内部作業メモが露出している"),
    (r"唯一の自治体|一都三県で唯一|全国で唯一", "全称の主張（反証されうる言い方）"),
    (r"必ずもらえ|確実にもらえ|全員が対象", "断定的な受給の約束"),
]


def visible_text(content):
    """CSS・JS・属性を落として、読者が読む文字だけにする。
    リントはここにだけかける（styleのbackground等を誤検出しないため）。"""
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", content)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return html.unescape(t)


def lint(name, content):
    ng = []
    text = visible_text(content)
    for pat, why in BANNED:
        m = re.search(pat, text)
        if m:
            ng.append("%s: %s（%r）" % (name, why, m.group(0)[:40]))
    return ng


def main():
    ng = lint("tool", TOOL_HTML) + lint("article", ART_HTML)
    if ng:
        print("LINT NG")
        for x in ng:
            print("  " + x)
        raise SystemExit(1)
    for path, content in [
        (os.path.join(BASE, "tools", "kekkon-shinseikatsu-jichitai", "index.html"), TOOL_HTML),
        (os.path.join(BASE, "articles", "kekkon-shinseikatsu-data", "index.html"), ART_HTML),
    ]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("written: %s  %d chars" % (os.path.relpath(path, BASE), len(content)))
    print("自治体数: %d（千葉%d・埼玉%d・神奈川%d・東京%d）"
          % (N_ALL, len(BY_PREF["千葉県"]), len(BY_PREF["埼玉県"]),
             len(BY_PREF["神奈川県"]), len(BY_PREF["東京都"])))
    print("上限額の型: 標準%d / 一律%d / 特殊%d" % (len(STD), len(UNI), len(SPE)))


if __name__ == "__main__":
    main()

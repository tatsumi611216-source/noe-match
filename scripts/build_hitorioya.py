# -*- coding: utf-8 -*-
"""ひとり親支援バンク（東京23区）のツール＋データ記事を生成する。

データ正本: scripts/_hitorioya_data.py（検算済み・手で編集しない）
出力:
  tools/hitorioya-shien-jichitai/index.html
  articles/hitorioya-shien-data/index.html

数値はすべて _hitorioya_data.py から機械的に流し込む（転記しない）。
住宅支援の「型」の分類だけは編集判断（TYPE_MAP）で、根拠は各区の
jutaku.kingaku / note の原文（分類基準はコメントに記載）。
"""
import html
import importlib.util
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

spec = importlib.util.spec_from_file_location(
    "_hitorioya_data", os.path.join(BASE, "scripts", "_hitorioya_data.py"))
_d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_d)
WARDS = _d.WARDS

KEYS = {
    "千代田区": "chiyoda", "中央区": "chuo", "港区": "minato", "新宿区": "shinjuku",
    "文京区": "bunkyo", "台東区": "taito", "墨田区": "sumida", "江東区": "koto",
    "品川区": "shinagawa", "目黒区": "meguro", "大田区": "ota", "世田谷区": "setagaya",
    "渋谷区": "shibuya", "中野区": "nakano", "杉並区": "suginami", "豊島区": "toshima",
    "北区": "kita", "荒川区": "arakawa", "板橋区": "itabashi", "練馬区": "nerima",
    "足立区": "adachi", "葛飾区": "katsushika", "江戸川区": "edogawa",
}

# 住宅支援の型（編集分類）。根拠は各区の jutaku 原文:
#   月額型   = 月々の家賃そのものへの補助が確認できた（千代田57,000円×最長5年／
#              世田谷 上限月4万円の家賃低廉化／杉並 25,000円×契約月数（区営住宅
#              優遇抽選の落選世帯対象）／足立 家賃半額・上限5万円×ひとり親最長10年）
#   区立住宅 = 現金補助ではなく区立のひとり親専用住宅（中央・計15戸・応能家賃）
#   一時金型 = 転居費用・初期費用・保証料への一時金（月額の家賃補助は確認できず）
#   立退き型 = 立退きを条件とする補助のみで金額非公表（渋谷・江戸川）
#   なし     = ひとり親向けの家賃助成・住宅費給付の専用制度を区公式サイトで確認できず
# 練馬は data 上 jutaku.exists=False だが、区独自支援欄の「ひとり親家庭転宅支援
# 給付金（上限40万円）」が機能的に一時金型のため、住宅欄でも同給付金を参照する。
TYPE_MAP = {
    "chiyoda": "家賃補助（月額型）", "chuo": "区立住宅（現金補助なし）",
    "minato": "なし（確認できず）", "shinjuku": "なし（確認できず）",
    "bunkyo": "一時金型", "taito": "一時金型", "sumida": "なし（確認できず）",
    "koto": "一時金型", "shinagawa": "一時金型（保証料）", "meguro": "一時金型（保証料）",
    "ota": "一時金型", "setagaya": "家賃補助（月額型）", "shibuya": "立退き時のみ",
    "nakano": "一時金型", "suginami": "家賃補助（条件つき）", "toshima": "なし（確認できず）",
    "kita": "一時金型", "arakawa": "一時金型", "itabashi": "なし（確認できず）",
    "nerima": "一時金型", "adachi": "家賃補助（月額型）", "katsushika": "一時金型（保証料）",
    "edogawa": "立退き時のみ",
}

CHECK_RANGE = "2026年8月29日〜30日"
TOOL_URL = "https://www.noe-match.com/tools/hitorioya-shien-jichitai/"
ART_URL = "https://www.noe-match.com/articles/hitorioya-shien-data/"


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def yen(n):
    return "{:,}円".format(n)


def checked_jp(iso):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", iso)
    return "%d年%d月%d日" % (int(m.group(1)), int(m.group(2)), int(m.group(3)))


def med_ok(w):
    """医療費助成の負担割合が区ページに明記されているか。

    「非公表」「見当たらな（かった）」を含む futan は割合未記載（港・目黒）。
    それ以外で「1割／１割」を含めば基準形（20区）。どちらでもない世田谷は
    割合の明記なし扱い。"""
    futan = w["iryo_josei"]["futan"]
    if ("非公表" in futan) or ("見当たらな" in futan):
        return False
    return ("1割" in futan) or ("１割" in futan)


def med_label(w):
    if med_ok(w):
        return "課税世帯1割・非課税世帯なし"
    return "負担割合の記載なし（区に要確認）"


def jutaku_view(w):
    """住宅支援欄の(制度名, 内容, src)。練馬のみ区独自支援欄の転宅支援給付金を参照。"""
    key = KEYS[w["ward"]]
    ju = w["jutaku"]
    if key == "nerima":
        d = w["dokuji"][0]
        assert "転宅支援" in d["name"]
        return (d["name"] + "（区分上は区独自支援）", d["kingaku"], d.get("src", ""))
    if not ju.get("exists"):
        naiyo = "ひとり親向けの家賃助成・住宅費給付の専用制度は区公式サイトで確認できず（区の説明は区選択で原文を表示）"
        return (ju.get("seido_name") or "—", naiyo, ju.get("src", ""))
    return (ju.get("seido_name", ""), ju.get("kingaku", ""), ju.get("src", ""))


# ---------- 共通CSS（kodomo-iryohi-jichitai と同一の骨格） ----------
with open(os.path.join(BASE, "tools", "kodomo-iryohi-jichitai", "index.html"),
          encoding="utf-8") as f:
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
               "<div><a href=\"/\">ホーム</a><a href=\"/articles/\">記事一覧</a><a href=\"/about.html\">運営者情報</a><a href=\"/privacy-policy.html\">プライバシー</a><a href=\"/disclaimer.html\">免責事項</a></div>\n"
               "<p class=\"footer-disc\">※本ツールは東京23区の公式公開情報（" + CHECK_RANGE + "確認）に基づく目安です。制度の適用と最終的な判断は各区が行います。<strong style=\"color:#cda\">【PR】</strong>本サイトはアフィリエイト広告を含みます。<br>&copy; 2026 Noe結婚設計室</p>\n"
               "</div></footer>")

FOOTER_ART = FOOTER_TOOL.replace("本ツールは", "本記事は")


def line_cta(kind, slug, title, body):
    ev = "{%s:'%s'}" % ("tool" if kind == "tool" else "article", slug)
    return ("<!-- LINE-CTA -->\n"
            "<section id=\"line-cta\" style=\"max-width:680px;margin:56px auto 64px;padding:36px 28px;background:#f7f5f2;border:1px solid #e3ddd3;text-align:center;\">\n"
            "  <p style=\"margin:0 0 10px;font-size:12px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif;\">NOE OFFICIAL LINE</p>\n"
            "  <p style=\"margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5;\">" + title + "</p>\n"
            "  <p style=\"margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;\">" + body + "</p>\n"
            "  <a href=\"https://lin.ee/unbDsCR\" rel=\"noopener\" onclick=\"try{gtag('event','line_add_click'," + ev + ");}catch(e){}\"\n"
            "     style=\"display:inline-block;background:#7c2e42;color:#ffffff;padding:14px 36px;font-size:15px;font-weight:600;text-decoration:none;\">友だち追加する</a>\n"
            "  <p style=\"margin:14px 0 0;font-size:11px;color:#8a8f95;\">登録は無料・配信は月1回だけ。いつでも解除できます。</p>\n"
            "</section>")


def fam_link(frm, to, label, sub):
    return ("<li style=\"margin:0 0 12px\"><a href=\"/tools/%s/\" onclick=\"try{gtag('event','tool_cross',{from:'%s',to:'%s'});}catch(e){}\" style=\"font-weight:700;color:#7c2e42\">%s</a>"
            "<span style=\"display:block;font-size:.82rem;color:#6b7178;margin-top:2px\">%s</span></li>" % (to, frm, to, label, sub))


TOOL_FAMILY = ("<!-- TOOL-FAMILY -->\n"
               "<section style=\"max-width:680px;margin:40px auto 8px;padding:26px 24px;background:#f7f5f2;border:1px solid #e3ddd3\">"
               "<p style=\"margin:0 0 6px;font-size:12px;letter-spacing:.16em;color:#7c2e42;font-family:Georgia,serif\">RELATED TOOLS</p>"
               "<p style=\"margin:0 0 16px;font-weight:700;font-size:1.02rem\">同じ自治体の、ほかの制度も確かめられます</p>"
               "<ul style=\"list-style:none;margin:0;padding:0\">"
               + fam_link("hitorioya-shien-jichitai", "kodomo-iryohi-jichitai",
                          "子ども医療費助成はいつまで使えるか", "東京23区の対象年齢・所得制限・入院時食事代の扱い")
               + fam_link("hitorioya-shien-jichitai", "byoji-hoiku-ryokin",
                          "病児保育は1日いくらか", "東京23区の料金・減免・予約方法を並べて確認")
               + fam_link("hitorioya-shien-jichitai", "daredemo-tsuen-jichitai",
                          "誰でも通園制度、月何時間まで使えるか", "46自治体の上限時間・料金・予約方法")
               + "</ul><p style=\"margin:12px 0 0;font-size:.72rem;color:#8a8f95\">いずれも無料・登録不要。公式ページの一次確認にもとづく数字だけを載せています。</p></section>")


# ---------- 集計（本文の主張はすべてここから） ----------
n_ikusei_13500 = sum(1 for w in WARDS if w["ikusei_teate"]["monthly"] == 13500)
shogai_vals = {}
for w in WARDS:
    shogai_vals.setdefault(w["ikusei_teate"]["shogai_monthly"], []).append(w["ward"])
n_med_1wari = sum(1 for w in WARDS if med_ok(w))
med_nolabel = [w["ward"] for w in WARDS if not med_ok(w)]
types_count = {}
for k in TYPE_MAP.values():
    base = k.split("（")[0]
    types_count[base] = types_count.get(base, 0) + 1
assert n_ikusei_13500 == 23
assert sorted(shogai_vals.keys()) == [15500, 17000]
assert shogai_vals[17000] == ["杉並区"]
assert len(shogai_vals[15500]) == 22
assert n_med_1wari == 20 and med_nolabel == ["港区", "目黒区", "世田谷区"], med_nolabel

# 型の内訳（TYPE_MAP から機械集計）
getsugaku = [w["ward"] for w in WARDS if TYPE_MAP[KEYS[w["ward"]]].startswith("家賃補助")]
kuritsu = [w["ward"] for w in WARDS if TYPE_MAP[KEYS[w["ward"]]].startswith("区立住宅")]
ichijikin = [w["ward"] for w in WARDS if TYPE_MAP[KEYS[w["ward"]]].startswith("一時金型")]
tachinoki = [w["ward"] for w in WARDS if TYPE_MAP[KEYS[w["ward"]]].startswith("立退き時")]
nashi = [w["ward"] for w in WARDS if TYPE_MAP[KEYS[w["ward"]]].startswith("なし")]
assert len(getsugaku) + len(kuritsu) + len(ichijikin) + len(tachinoki) + len(nashi) == 23


# ---------- FAQ（可視本文とJSON-LDを同一文字列で同期） ----------
FAQ = [
    ("児童育成手当は区によって金額が違いますか？",
     "育成手当は東京23区すべて児童1人につき月額13,500円で、差がありません。一方、障害のある児童が対象の障害手当は22区が月額15,500円で、杉並区だけが月額17,000円でした（%s確認）。区の公式ページの記載にもとづく数字です。" % CHECK_RANGE),
    ("児童扶養手当と児童育成手当は同じものですか？",
     "別の制度です。児童扶養手当は国の制度、児童育成手当は東京都の制度で、要件を満たせば両方を受け取れます。本ページで扱っているのは児童育成手当（および各区のひとり親支援）で、金額や所得制限は区の公式ページの記載を転記しています。"),
    ("ひとり親家庭の医療費助成（マル親）の自己負担はいくらですか？",
     "23区のうち20区は「住民税課税世帯は医療費の1割負担（上限あり）・非課税世帯は負担なし」という型を公式ページに明記しています。港区は負担割合の記載が現行ページに見当たらず、目黒区・世田谷区も割合の明記がありませんでした。この3区は区に直接ご確認ください。なお非課税世帯でも入院時の食事代は自己負担となる区が多くあります。"),
    ("住宅支援が手厚いのはどの区ですか？",
     "月々の家賃への補助が確認できたのは4区だけです。千代田区は月額57,000円を最長5年、足立区は家賃半額（上限5万円）を最長10年、世田谷区は上限月4万円の家賃低廉化補助、杉並区は25,000円×契約月数（上限30万円）です。ただしいずれも所得基準・対象住宅・抽選落選などの条件があり、誰でも使えるわけではありません。中央区は現金の補助ではなく区立のひとり親世帯住宅（計15戸）を持ちます。"),
    ("住宅の支援がない区に住んでいる場合、何も受けられませんか？",
     "月額の家賃補助が無い区でも、転居費用や保証料への一時金がある区が多くあります。荒川区は転居支援補助金が上限40万円（多子世帯45万円）、練馬区は転宅支援給付金が上限40万円、中野区は上限30万円です。また都営交通の無料乗車券やJR通勤定期の割引、高等職業訓練促進給付金などは多くの区で共通に使えます。"),
    ("この情報はいつのものですか？",
     "%sに東京23区すべての公式ページを確認した内容です。数値は各区公式ページの記載を確認日時点で転記しています。制度は年度で変わり、募集枠が閉じることもあるため、利用前に必ず各区の公式ページと窓口でご確認ください。" % CHECK_RANGE),
]


def faq_jsonld():
    return json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in FAQ]}, ensure_ascii=False)


def faq_html():
    out = []
    for i, (q, a) in enumerate(FAQ, 1):
        out.append("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i, esc(q), esc(a)))
    return "\n".join(out)


# ---------- 一覧テーブル（全23区・HTML直書き） ----------
def table_teate_med():
    rows = []
    for w in WARDS:
        ik = w["ikusei_teate"]
        jt = TYPE_MAP[KEYS[w["ward"]]]
        rows.append("<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            esc(w["ward"]), yen(ik["monthly"]), yen(ik["shogai_monthly"]),
            esc(med_label(w)), esc(jt)))
    return ("<div class=\"table-scroll\">\n<table class=\"cmp\">\n"
            "<thead><tr><th>区</th><th>児童育成手当（月額）</th><th>障害手当（月額）</th><th>医療費助成の自己負担</th><th>住宅支援の型</th></tr></thead>\n"
            "<tbody>" + "".join(rows) + "</tbody>\n</table>\n</div>")


def table_jutaku():
    rows = []
    for w in WARDS:
        key = KEYS[w["ward"]]
        seido, naiyo, _src = jutaku_view(w)
        rows.append("<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            esc(w["ward"]), esc(TYPE_MAP[key]), esc(seido), esc(naiyo)))
    return ("<div class=\"table-scroll\">\n<table class=\"cmp\">\n"
            "<thead><tr><th>区</th><th>型</th><th>制度名</th><th>内容（区ページの記載）</th></tr></thead>\n"
            "<tbody>" + "".join(rows) + "</tbody>\n</table>\n</div>")


def table_sources():
    rows = []
    for w in WARDS:
        ik, ir = w["ikusei_teate"], w["iryo_josei"]
        _seido, _naiyo, jsrc = jutaku_view(w)
        cells = []
        cells.append("<a href=\"%s\" rel=\"noopener\" target=\"_blank\">児童育成手当</a>" % esc(ik["src"]))
        cells.append("<a href=\"%s\" rel=\"noopener\" target=\"_blank\">医療費助成</a>" % esc(ir["src"]))
        if jsrc:
            cells.append("<a href=\"%s\" rel=\"noopener\" target=\"_blank\">住宅支援</a>" % esc(jsrc))
        rows.append("<tr><td>%s</td><td style=\"text-align:left\">%s</td><td>%s</td></tr>" % (
            esc(w["ward"]), "／".join(cells), esc(checked_jp(w["checked"]))))
    return ("<div class=\"table-scroll\">\n<table class=\"cmp\">\n"
            "<thead><tr><th>区</th><th>出典（各区公式ページ）</th><th>確認日</th></tr></thead>\n"
            "<tbody>" + "".join(rows) + "</tbody>\n</table>\n</div>")


# ---------- ツール用 JS データ ----------
def js_data():
    out = {}
    for w in WARDS:
        key = KEYS[w["ward"]]
        out[key] = {
            "key": key, "name": w["ward"], "checked": checked_jp(w["checked"]),
            "ikusei": w["ikusei_teate"], "iryo": w["iryo_josei"],
            "med_ok": med_ok(w),
            "jutaku": w["jutaku"], "jutaku_type": TYPE_MAP[key],
            "dokuji": w["dokuji"],
        }
    return json.dumps(out, ensure_ascii=False, separators=(",", ":"))


def ward_options():
    return "".join("<option value=\"%s\">%s</option>" % (KEYS[w["ward"]], esc(w["ward"]))
                   for w in WARDS)


# ============================================================
# ツールページ
# ============================================================
TOOL_TITLE = "ひとり親支援は区でどれだけ違う？東京23区の児童育成手当・医療費助成・住宅支援【2026年8月30日確認】"
TOOL_DESC = ("ひとり親家庭への支援は東京23区で差があります。児童育成手当は全区とも児童1人につき月額13,500円で同じ、"
             "障害手当は22区が月額15,500円で杉並区だけ月額17,000円でした。医療費助成（マル親）は「課税世帯1割負担・非課税世帯負担なし」が基準形ですが、"
             "港区は負担割合の記載が現行ページに見当たりません。差が大きいのは住宅支援で、月々の家賃補助がある区は4区だけ。"
             "千代田区は月額57,000円×最長5年、足立区は家賃半額（上限5万円）×最長10年、一方で専用制度を確認できなかった区が5区あります。"
             "区を選ぶと手当・医療費・住宅・区独自支援が出典つきで出ます。")

tool_webapp_ld = json.dumps({
    "@context": "https://schema.org", "@type": "WebApplication",
    "name": "ひとり親支援 東京23区ナビ", "url": TOOL_URL,
    "applicationCategory": "UtilitiesApplication", "operatingSystem": "All",
    "inLanguage": "ja", "description": TOOL_DESC,
    "datePublished": "2026-08-30", "dateModified": "2026-08-30",
    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
    "publisher": {"@type": "Organization", "name": "Noe結婚設計室",
                  "url": "https://www.noe-match.com/"}}, ensure_ascii=False)

tool_bc_ld = json.dumps({
    "@context": "https://schema.org", "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
        {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": "https://www.noe-match.com/#tools"},
        {"@type": "ListItem", "position": 3, "name": "ひとり親支援 東京23区ナビ"}]}, ensure_ascii=False)

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
<meta property="og:description" content="児童育成手当は23区とも月13,500円で同じ。差がつくのは住宅支援で、月々の家賃補助がある区は4区だけです。区を選ぶと出典つきで条件が出ます。">
<meta property="og:type" content="website">
<meta property="og:url" content=\"""" + TOOL_URL + """\">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="ひとり親支援は区でどれだけ違う？東京23区の条件">
<meta name="twitter:description" content="児童育成手当は23区とも月13,500円で同じ。差がつくのは住宅支援で、月々の家賃補助がある区は4区だけです。">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@500;600;700;900&display=swap" rel="stylesheet">
""" + STYLE + """
<style>
.cityout dt{font-weight:700;color:#1d242b;margin-top:14px;font-size:.9rem}
.cityout dd{margin:4px 0 0;font-size:.88rem;line-height:1.9;color:#3a4148}
.fitbox{padding:14px 16px;border-radius:6px;margin:14px 0;font-size:.9rem;line-height:1.9}
.fit-ok{background:#edf3ee;border:1px solid #cfe0d4}
.fit-ng{background:#f6f0e1;border:1px solid #e6d8b4}
.badge{display:inline-block;font-size:.74rem;font-weight:700;padding:2px 9px;border-radius:3px;margin-left:8px;vertical-align:middle}
.b-ok{background:#e3ecec;color:#3d585e}
.b-ng{background:#f0e3e6;color:#7c2e42}
table.cmp td{vertical-align:top;text-align:left}
.dok{background:#f7f5f2;border:1px solid #e6e2dc;border-radius:4px;padding:12px 14px;margin:10px 0}
.dok .nm{font-weight:700;color:#1d242b;font-size:.9rem}
.dok p{margin:4px 0 0;font-size:.85rem;line-height:1.85}
</style>
<script type="application/ld+json">""" + faq_jsonld() + """</script>
<script type="application/ld+json">""" + tool_webapp_ld + """</script>
<script type="application/ld+json">""" + tool_bc_ld + """</script>
</head>
<body>
""" + HEADER + """
<div class="wrap">
<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ ひとり親支援 東京23区ナビ</div>

<div class="tool-hero" style="background-image:url('../../images/lp/hands-touch.jpg')"><div class="tool-hero-inner">
<h1>ひとり親支援は住む区でどれだけ違う？｜東京23区の手当・医療費助成・住宅支援</h1>
<p>児童育成手当は23区すべて月額13,500円で差がありません。差が大きいのは住宅支援で、月々の家賃補助が確認できたのは4区だけ。千代田区は月57,000円×最長5年、足立区は家賃半額（上限5万円）×最長10年です。区を選ぶと、手当・医療費助成・住宅支援・区独自支援が出典つきで出ます。無料・登録不要。</p>
</div></div>

<article>
<blockquote><strong>「ひとり親の手当はどこでも同じ」で片づけると、住宅支援の差を見落とします。</strong>東京都の制度である児童育成手当（月13,500円）と医療費助成（マル親）は23区でほぼ横並びですが、住まいへの支援は、家賃助成が月額で出る区から、専用制度を確認できなかった区まで開きがあります。""" + CHECK_RANGE + """に23区すべての公式ページを確認しました。数値は各区公式ページの記載を確認日時点で転記しています。</blockquote>

<h2>STEP1｜お住まいの区（またはこれから住む区）を選ぶ</h2>
<div class="calc" id="calcForm">
  <div class="fld">
    <label for="city">区を選ぶ</label>
    <select id="city">""" + ward_options() + """</select>
    <div class="hint">東京23区を""" + CHECK_RANGE + """に確認して収録しています。転居を検討している区を選ぶと、転居先の条件が見られます。</div>
  </div>
  <button type="button" class="calc-btn" id="run">この区の支援を見る</button>
</div>

<div class="result" id="result" aria-live="polite">
  <div class="big">
    <div class="lbl">児童育成手当（児童1人につき）</div>
    <div class="num" id="teate">—</div>
  </div>
  <div id="fit" class="fitbox"></div>
  <dl class="cityout" id="detail"></dl>
  <div id="dokuji"></div>
  <p id="srcNote" style="font-size:.78rem;color:#6b7178;margin:18px 0 0;line-height:1.9"></p>
</div>

<h2 id="ichiran">東京23区の一覧</h2>
<p>児童育成手当は全区とも月額13,500円です。障害手当（障害のある児童が対象）は22区が月額15,500円で、<strong>杉並区だけが月額17,000円</strong>でした。医療費助成は「課税世帯1割・非課税世帯負担なし」が基準形ですが、<strong>港区・目黒区・世田谷区は負担割合の明記が確認できませんでした</strong>。</p>
""" + table_teate_med() + """
<p style="font-size:.8rem;color:#6b7178">※非課税世帯でも入院時の食事代等は自己負担となる区が多くあります。上限額・支給月などの原文は、上のフォームで区を選ぶと表示されます。</p>

<h2 id="jutaku">住宅支援の一覧｜ここが一番割れる</h2>
<p>月々の家賃そのものへの補助が確認できたのは<strong>""" + esc("・".join(getsugaku)) + """の4区</strong>だけです。中央区は現金の補助ではなく区立のひとり親世帯住宅（計15戸）を持ちます。""" + esc("・".join(ichijikin)) + """は転居費用・保証料への一時金型、""" + esc("・".join(tachinoki)) + """は立退きを条件とする補助のみ（金額非公表）、""" + esc("・".join(nashi)) + """の5区は専用制度を確認できませんでした。</p>
""" + table_jutaku() + """

<h2 id="chui">調べるときに間違えやすいところ</h2>
<h3>児童扶養手当と児童育成手当は別物</h3>
<p>児童扶養手当は国の制度、児童育成手当は東京都の制度で、要件を満たせば両方受け取れます。本ツールが扱うのは児童育成手当です。名前が似ているため、区のページでも取り違えやすい項目です。</p>
<h3>「家賃補助あり」でも誰でも使えるわけではない</h3>
<p>千代田区の家賃助成は高齢者・障害者世帯などと共通の制度で所得基準があります。世田谷区の家賃低廉化補助は対象住宅が限られ、確認時点で「現在、入居募集中の住宅はございません」との記載がありました。杉並区は区営住宅の優遇抽選に落選した世帯が対象、足立区はセーフティネット住宅の専用住戸で所得基準と戸数の限りがあります。<strong>制度の存在と、いま使えるかは別問題です。</strong></p>
<h3>港区の医療費助成は負担割合の記載がない</h3>
<p>港区の公式ページは「負担すべき額の一部または全部を助成します」とのみ記載しており、課税・非課税世帯別の負担割合（1割など）や上限額は制度ページにもFAQにも見当たりませんでした。推測で埋めず、<strong>区に直接確認してください</strong>。目黒区・世田谷区も割合の明記がありません。</p>
<h3>「住宅支援なし」の区でも一時金や共通支援はある</h3>
<p>月額の家賃補助が無い区でも、転居費用や保証料への一時金、都営交通の無料乗車券、JR通勤定期の割引、高等職業訓練促進給付金などは使えることが多くあります。区独自支援の欄もあわせて確認してください。</p>

<h2 id="faq">よくある質問（FAQ）</h2>
""" + faq_html() + """

<h2 id="src">出典</h2>
<p>すべて各区の公式ページで確認しました。確認日は""" + CHECK_RANGE + """です。数値は各区公式ページの記載を確認日時点で転記しています。制度は年度で変わるため、利用前に必ず公式ページをご確認ください。区独自支援の出典リンクは、区を選ぶと各制度に表示されます。</p>
""" + table_sources() + """

<h2 id="related">関連するツールと記事</h2>
<ul>
<li><a href="/articles/hitorioya-shien-data/">ひとり親支援は東京23区でどう違う？差がつくのは住宅支援と障害手当</a></li>
<li><a href="/tools/rikongo-seikatsuhi/">離婚後の生活費と養育費のシミュレーション</a></li>
<li><a href="/tools/kodomo-iryohi-jichitai/">子ども医療費助成はいつまで？東京23区の条件</a></li>
<li><a href="/articles/kodomo-iryohi-data/">子ども医療費助成は東京23区でどう違う？</a></li>
</ul>
</article>

""" + TOOL_FAMILY + """
""" + line_cta("tool", "hitorioya-shien-jichitai", "自治体の制度は年度で変わります",
               "児童育成手当・ひとり親医療費助成・住宅支援など、自治体ごとに違う制度の変更点を月1回お知らせします。<br>お住まいの自治体について調べてほしいことは、追加後そのままトークでどうぞ。") + """
</div>
""" + FOOTER_TOOL + """
<button id="top" onclick="scrollTo({top:0,behavior:'smooth'})">↑</button>
<script>
(function(){
"use strict";
var D=""" + js_data() + """;
function $(id){return document.getElementById(id);}
function esc(s){return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function yen(n){return n==null?'—':Number(n).toLocaleString('ja-JP')+'円';}
function run(){
  var c=D[$('city').value];
  $('teate').textContent='月額 '+yen(c.ikusei.monthly)+'（障害手当 '+yen(c.ikusei.shogai_monthly)+'）';
  var f=$('fit');
  var t=c.jutaku_type;
  if(t.indexOf('なし')===0){
    f.className='fitbox fit-ng';
    f.innerHTML='<strong>'+esc(c.name)+'の住宅支援：'+esc(t)+'。</strong>ひとり親向けの家賃助成・住宅費給付の専用制度は区公式サイトで確認できませんでした。下の区独自支援と、都営交通無料乗車券などの共通支援を確認してください。';
  }else{
    f.className='fitbox fit-ok';
    f.innerHTML='<strong>'+esc(c.name)+'の住宅支援：'+esc(t)+'。</strong>'+esc(c.name==='練馬区'?'区独自支援としてひとり親家庭転宅支援給付金（上限40万円）があります。':(c.jutaku.seido_name||''))+' 詳細は下の住宅支援の欄と出典をご確認ください。';
  }
  var h='';
  h+='<dt>児童育成手当（所得制限）</dt><dd>'+esc(c.ikusei.shotoku_seigen)+'</dd>';
  if(c.ikusei.note)h+='<dt>児童育成手当の補足</dt><dd>'+esc(c.ikusei.note)+'</dd>';
  h+='<dt>医療費助成の制度名</dt><dd>'+esc(c.iryo.seido_name)+'</dd>';
  h+='<dt>医療費の自己負担'+(c.med_ok?'<span class="badge b-ok">課税1割の型</span>':'<span class="badge b-ng">記載なし・区に要確認</span>')+'</dt><dd>'+esc(c.iryo.futan)+'</dd>';
  h+='<dt>医療費助成の所得制限</dt><dd>'+esc(c.iryo.shotoku_seigen)+'</dd>';
  h+='<dt>医療費助成の対象年齢</dt><dd>'+esc(c.iryo.age_limit)+'</dd>';
  if(c.iryo.note)h+='<dt>医療費助成の補足</dt><dd>'+esc(c.iryo.note)+'</dd>';
  if(c.name==='練馬区'){
    h+='<dt>住宅支援</dt><dd>区分上は区独自支援ですが、ひとり親家庭転宅支援給付金（下の区独自支援欄の1つ目）が転居時の費用を上限40万円まで支援します。月々の家賃補助の専用制度は確認できませんでした。</dd>';
  }else if(c.jutaku.exists){
    h+='<dt>住宅支援（'+esc(c.jutaku.seido_name)+'）</dt><dd>'+esc(c.jutaku.kingaku)+'</dd>';
    if(c.jutaku.joken)h+='<dt>住宅支援の条件</dt><dd>'+esc(c.jutaku.joken)+'</dd>';
    if(c.jutaku.note)h+='<dt>住宅支援の補足</dt><dd>'+esc(c.jutaku.note)+'</dd>';
  }else{
    h+='<dt>住宅支援</dt><dd>'+esc(c.jutaku.note||'ひとり親向けの家賃助成・住宅費給付の専用制度は区公式サイトで確認できませんでした。')+'</dd>';
  }
  $('detail').innerHTML=h;
  var dk='';
  if(c.dokuji&&c.dokuji.length){
    dk+='<dt style="font-weight:700;color:#1d242b;margin-top:18px;font-size:.9rem">区独自の主な支援</dt>';
    for(var i=0;i<c.dokuji.length;i++){
      var d=c.dokuji[i];
      dk+='<div class="dok"><span class="nm">'+esc(d.name)+'</span><p>'+esc(d.gaiyo)+'</p><p><strong>金額：</strong>'+esc(d.kingaku)+'</p>'+(d.src?'<p style="font-size:.76rem"><a href="'+d.src+'" rel="noopener" target="_blank">出典（区公式ページ）</a></p>':'')+'</div>';
    }
  }
  $('dokuji').innerHTML=dk;
  $('srcNote').innerHTML='出典：<a href="'+c.ikusei.src+'" rel="noopener" target="_blank">'+esc(c.ikusei.src_label)+'</a>／<a href="'+c.iryo.src+'" rel="noopener" target="_blank">'+esc(c.iryo.src_label)+'</a>'+((c.jutaku&&c.jutaku.src)?'／<a href="'+c.jutaku.src+'" rel="noopener" target="_blank">'+esc(c.jutaku.src_label||'住宅支援')+'</a>':'')+'（'+esc(c.checked)+'確認）。数値は各区公式ページの記載を確認日時点で転記しています。最新の内容は必ず公式ページでご確認ください。';
  $('result').classList.add('show');
  if(window.__ui)try{gtag('event','tool_result',{tool:'hitorioya-shien-jichitai',city:c.key});}catch(e){}
}
$('run').addEventListener('click',run);
$('city').addEventListener('change',run);
run();
})();
</script>
""" + UI_GUARD + """</body>
</html>
"""

# ============================================================
# データ記事
# ============================================================
ART_TITLE = "ひとり親支援は東京23区でどう違う？差がつくのは住宅支援と障害手当"
ART_DESC = ("ひとり親家庭への支援を東京23区すべての公式ページで確認しました（2026年8月29日〜30日）。"
            "児童育成手当は全区とも児童1人につき月額13,500円で差がなく、障害手当は22区が月額15,500円で杉並区だけ月額17,000円。"
            "医療費助成（マル親）は「課税世帯1割・非課税世帯負担なし」が基準形ですが、港区は負担割合の記載が見当たりません。"
            "最も割れるのは住宅支援で、月々の家賃補助がある区は4区（千代田・世田谷・杉並・足立）だけ。"
            "千代田区は月57,000円×最長5年、足立区は家賃半額（上限5万円）×最長10年、荒川区は転居費用上限40万円、"
            "一方で専用制度を確認できなかった区が5区あります。数値は各区公式ページの記載を確認日時点で転記。")

art_blog_ld = json.dumps({
    "@context": "https://schema.org", "@type": "BlogPosting",
    "headline": ART_TITLE, "description": ART_DESC, "inLanguage": "ja",
    "datePublished": "2026-08-30", "dateModified": "2026-08-30",
    "mainEntityOfPage": {"@type": "WebPage", "@id": ART_URL},
    "author": {"@type": "Organization", "name": "Noe編集部",
               "url": "https://www.noe-match.com/about.html"},
    "publisher": {"@type": "Organization", "name": "Noe結婚設計室",
                  "url": "https://www.noe-match.com/"}}, ensure_ascii=False)

art_bc_ld = json.dumps({
    "@context": "https://schema.org", "@type": "BreadcrumbList",
    "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
        {"@type": "ListItem", "position": 2, "name": "記事一覧", "item": "https://www.noe-match.com/articles/"},
        {"@type": "ListItem", "position": 3, "name": "ひとり親支援は東京23区でどう違う？｜差がつくのは住宅支援と障害手当"}]},
    ensure_ascii=False)

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
<meta property="og:description" content="児童育成手当は23区とも月13,500円で同じ。差がつくのは住宅支援で、月々の家賃補助がある区は4区だけです。">
<meta property="og:type" content="article">
<meta property="og:url" content=\"""" + ART_URL + """\">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content=\"""" + esc(ART_TITLE) + """\">
<meta name="twitter:description" content="児童育成手当は23区とも月13,500円で同じ。差がつくのは住宅支援で、月々の家賃補助がある区は4区だけです。">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@500;600;700;900&display=swap" rel="stylesheet">
""" + STYLE + """
<style>table.cmp td{vertical-align:top;font-size:.86rem;line-height:1.85;text-align:left}
.srcline{font-size:.78rem;color:#6b7178;line-height:1.9;margin:8px 0 0}</style>
<script type="application/ld+json">""" + faq_jsonld() + """</script>
<script type="application/ld+json">""" + art_blog_ld + """</script>
<script type="application/ld+json">""" + art_bc_ld + """</script>
</head>
<body>
""" + HEADER + """
<div class="wrap">
<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/articles/">記事一覧</a> ＞ ひとり親支援は東京23区でどう違う？｜差がつくのは住宅支援と障害手当</div>
<article>
<h1>ひとり親支援は東京23区でどう違う？｜差がつくのは住宅支援と障害手当</h1>
<p style="font-size:.78rem;color:#8a8f95;margin:6px 0 20px">公開 2026-08-30／出典は各区公式ページ。""" + CHECK_RANGE + """に各原典で確認</p>
<blockquote><strong>「ひとり親の手当はどこに住んでも同じ」は半分だけ正しい。</strong>東京23区すべての公式ページを確認したところ、児童育成手当（東京都の制度）は全区とも児童1人につき月額13,500円で差がありませんでした。一方で<strong>住まいへの支援は、家賃助成が月額で出る区（4区）から、専用制度を確認できなかった区（5区）まで開いています</strong>。障害手当も22区が月額15,500円のなかで杉並区だけ月額17,000円でした。本記事は離婚をすすめるものでも思いとどまらせるものでもなく、制度の一次データの整理です。</blockquote>

<h2 id="dodai">まず全区共通の土台｜児童扶養手当と児童育成手当は別物</h2>
<p>ひとり親家庭の現金給付は二階建てです。<strong>児童扶養手当は国の制度</strong>で全国共通、<strong>児童育成手当は東京都の制度</strong>で、要件を満たせば両方を受け取れます。区で調べるときに名前が似ていて取り違えやすいのはこの2つです。</p>
<p>児童育成手当は23区すべてが<strong>児童1人につき月額13,500円</strong>で、ここに区の差はありません。所得制限はどの区にもあります（基準額の書き方は区のページで差があります）。</p>

<h2 id="shogai">障害手当は22区が15,500円、杉並区だけ17,000円</h2>
<p>児童育成手当には、障害のある児童を対象とする障害手当があります。22区は<strong>月額15,500円</strong>でしたが、<strong>杉並区だけは月額17,000円</strong>と記載されていました。杉並区のページには「区は都の制度に上乗せしています」といった説明が見当たらないため取り違えを疑い、複数ページで再確認しましたが、17,000円の記載でした。金額差は月1,500円、年間18,000円です。</p>

<h2 id="iryo">医療費助成（マル親）の基準形と、割合を書いていない3区</h2>
<p>ひとり親家庭等医療費助成（マル親医療証）は、23区のうち20区が<strong>「住民税課税世帯は医療費の1割負担（月額・年額の上限あり）、非課税世帯は負担なし」</strong>という型を公式ページに明記しています。上限は多くの区で「外来 月18,000円（年間144,000円）・入院 月57,600円（多数回該当44,400円）」です。非課税世帯でも入院時の食事代（食事療養標準負担額）は自己負担となる区が多くあります。</p>
<p><strong>港区は、負担割合の記載が現行ページに見当たりませんでした。</strong>「負担すべき額の一部または全部を助成します」とのみ書かれており、制度ページにもFAQにも1割などの割合・上限額の記載がありません。目黒区・世田谷区も「自己負担分の一部（または全部）を助成」という書き方で、割合の明記がありませんでした。この3区については推測で埋めず、<strong>区に直接ご確認ください</strong>。</p>

<h2 id="jutaku">最も割れるのは住宅支援｜月額の家賃補助がある区は4つだけ</h2>
<p>23区の住宅支援を型で分けると、次のようになりました。</p>
<div class="table-scroll"><table class="cmp"><thead><tr><th>型</th><th>区</th><th>内容の例</th></tr></thead><tbody>
<tr><td>家賃補助（月額型）</td><td>""" + esc("・".join(getsugaku)) + """（4区）</td><td>千代田＝一律月額57,000円×最長5年／世田谷＝上限月4万円の家賃低廉化補助／杉並＝25,000円×契約月数（上限30万円・区営住宅優遇抽選の落選世帯対象）／足立＝家賃半額（上限5万円）×ひとり親は最長10年</td></tr>
<tr><td>区立住宅（現金補助なし）</td><td>""" + esc("・".join(kuritsu)) + """（1区）</td><td>区立ひとり親世帯住宅 計15戸（応能家賃）。家賃を現金で補助する制度は確認できず</td></tr>
<tr><td>一時金型（転居費用・保証料）</td><td>""" + esc("・".join(ichijikin)) + """（""" + str(len(ichijikin)) + """区）</td><td>荒川＝転居支援補助金 上限40万円（多子世帯45万円）＋保証料上限5万円／練馬＝転宅支援給付金 上限40万円／中野＝上限30万円／台東＝転居初期費用 最大15万円＋保証料の2分の1／北＝転居費用 上限15万円＋保証料上限2万円 など</td></tr>
<tr><td>立退き時のみ（金額非公表）</td><td>""" + esc("・".join(tachinoki)) + """（2区）</td><td>立退きを条件に住み替え後の家賃・転居費用の一部を補助。金額はページに記載なし</td></tr>
<tr><td>なし（専用制度を確認できず）</td><td>""" + esc("・".join(nashi)) + """（5区）</td><td>ひとり親向けの家賃助成・住宅費給付の専用制度は区公式サイトで確認できず</td></tr>
</tbody></table></div>
<p>単純化した比較はできませんが、規模感だけ示します。千代田区の家賃助成（月57,000円×最長5年）を上限まで受けると<strong>累計342万円</strong>、足立区（上限5万円×最長10年）は<strong>最大600万円</strong>に相当します。専用制度が確認できなかった区との差は、この一項目だけで数百万円規模になり得ます。</p>
<p>ただし<strong>「制度がある」と「いま使えるか」は別問題です</strong>。千代田区は高齢者・障害者世帯などと共通の制度で所得基準（申告者の所得月額20万円以下など）があり、世田谷区は確認時点で「現在、入居募集中の住宅はございません」との記載、杉並区は区営住宅の優遇抽選に落選した世帯が対象、足立区はセーフティネット住宅の専用住戸で所得基準（年間189万6,000円以下）と戸数の限りがあります。</p>

<h2 id="ichiran">東京23区の一覧</h2>
<p>各区の公式ページを""" + CHECK_RANGE + """に確認した内容です。数値は各区公式ページの記載を確認日時点で転記しています。</p>
""" + table_teate_med() + """
<p style="font-size:.8rem;color:#6b7178">※非課税世帯でも入院時の食事代等は自己負担となる区が多くあります。上限額・所得制限・支給月などの原文は<a href="/tools/hitorioya-shien-jichitai/">ひとり親支援 東京23区ナビ</a>で区を選ぶと表示されます。</p>
<h3>住宅支援の詳細（全23区）</h3>
""" + table_jutaku() + """

<h2 id="dokuji">区独自支援で目立ったもの</h2>
<ul>
<li><strong>養育費の確保支援</strong>：公正証書の作成費用や保証契約の初回保証料を助成する区が広がっています（千代田・北＝各上限5万円、渋谷＝公証人手数料上限43,000円、葛飾＝公正証書上限43,000円＋弁護士費用上限33,000円、世田谷＝強制執行申立て費用上限10万円＋実費上限5万円など）。</li>
<li><strong>中野区</strong>：離婚協議中の「実質ひとり親家庭」への子育て支援給付（児童1人につき10万円・一括）という珍しい制度があります。</li>
<li><strong>豊島区</strong>：エアコン購入費用等助成（10万円まで）。</li>
<li><strong>練馬区</strong>：学習クーポン（中1・中2は年間上限10万円、高1・高2は年間上限15万円）。</li>
<li><strong>共通で使えるもの</strong>：都営交通の無料乗車券、JR通勤定期の3割引、高等職業訓練促進給付金（非課税世帯 月額10万円が基準形）などは多くの区で確認できました。</li>
</ul>

<h2 id="chui">調べるときに間違えやすいところ</h2>
<h3>「手当は同じだから区は関係ない」ではない</h3>
<p>現金給付（児童扶養手当・児童育成手当）は横並びでも、住宅支援・独自支援は区で違います。転居や住み替えを考える局面では、住宅支援の型（月額型か一時金型か）を先に確認するのが近道です。</p>
<h3>「支援なし」の区でも一時金・共通支援はある</h3>
<p>本記事で「なし」としたのは、ひとり親向けの家賃助成・住宅費給付の<strong>専用制度</strong>が区公式サイトで確認できなかったという意味です。ホームヘルプサービスや交通の割引など、住宅以外の支援はどの区にもあります。</p>
<h3>募集枠と年度に注意</h3>
<p>住宅系の支援は予算・戸数の枠があり、年度の途中で募集が閉じることがあります。足立区の家賃低廉化補助は対象住戸数に限りがあり、募集時期によって申込可否が変わります。制度は年度で変わるため、必ず最新の公式ページと窓口で確認してください。</p>

<h2 id="calc">自分の場合を調べる</h2>
<p><a href="/tools/hitorioya-shien-jichitai/">ひとり親支援 東京23区ナビ</a>で区を選ぶと、手当・医療費助成・住宅支援・区独自支援が出典つきで出ます。離婚後の毎月の収支を数字で見たい場合は<a href="/tools/rikongo-seikatsuhi/">離婚後の生活費と養育費のシミュレーション</a>が使えます。</p>

<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/tools/hitorioya-shien-jichitai/">ひとり親支援 東京23区ナビ</a></li>
<li><a href="/tools/rikongo-seikatsuhi/">離婚後の生活費と養育費のシミュレーション</a></li>
<li><a href="/tools/kodomo-iryohi-jichitai/">子ども医療費助成はいつまで？東京23区の条件</a></li>
<li><a href="/articles/kodomo-iryohi-data/">子ども医療費助成は東京23区でどう違う？差がつくのは入院時の食事代</a></li>
<li><a href="/articles/rikon-okane-genjitsu/">離婚とお金の現実</a></li>
<li><a href="/articles/rikon-junbi-jyunban/">離婚を考えたら最初にすること｜証拠集め・お金の整理・相談先の順番</a></li>
</ul>

<h2 id="faq">よくある質問（FAQ）</h2>
""" + faq_html() + """

<h2 id="src">出典</h2>
<p>本記事の数値はすべて各区公式ページの記載を確認日時点で転記したものです。制度は年度で変わるため、利用前に必ず各区の公式ページでご確認ください。区独自支援の出典リンクは<a href="/tools/hitorioya-shien-jichitai/">ツール側</a>で区を選ぶと各制度に表示されます。</p>
""" + table_sources() + """
</article>
""" + line_cta("article", "hitorioya-shien-data", "制度の更新をお知らせします",
               "児童育成手当・ひとり親医療費助成・住宅支援など、この記事で扱った制度の変更点を月1回まとめて配信します。<br>お住まいの自治体について調べてほしいことは、追加後そのままトークでどうぞ。") + """
</div>
""" + FOOTER_ART + """
<button id="top" onclick="scrollTo({top:0,behavior:'smooth'})">↑</button>
""" + UI_GUARD + """</body>
</html>
"""


def main():
    for path, content in [
        (os.path.join(BASE, "tools", "hitorioya-shien-jichitai", "index.html"), TOOL_HTML),
        (os.path.join(BASE, "articles", "hitorioya-shien-data", "index.html"), ART_HTML),
    ]:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print("wrote %s (%d bytes)" % (os.path.relpath(path, BASE), len(content.encode("utf-8"))))


if __name__ == "__main__":
    main()

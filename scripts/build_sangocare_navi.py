# -*- coding: utf-8 -*-
"""産後ケア 自治体別 料金ナビ（宿泊型・日帰り型・訪問型の自己負担と上限回数）

狙う語は tool_gate.py の判定でGOだった「産後ケア 料金」
（サジェスト10件・SERP1ページ目に器具ゼロ）。金銭語だが計算専業も
事業者の器具も入っていない空白語で、しかも自治体ごとに実額が違う。
こども誰でも通園制度で実証した「器具 × 一次データ × 自治体差」の型をそのまま使う。

数値はすべて _sangocare_data.py（各自治体公式の一次確認）から引く。
表を手で書かない。記事とツールで数字がズレないようにするため。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _sangocare_data import CHECKED, CITIES

SLUG = "sangokea-ryokin"
URL = "https://www.noe-match.com/tools/%s/" % SLUG
TODAY = "2026-08-27"
OISIX = "https://px.a8.net/svt/ejp?a8mat=45C0YR+2VBK6Q+3250+5YZ77"

real = [c for c in CITIES if c["key"] != "kokuhyo"]
N = len(real)

GROUPS = []
for c in real:
    g = c.get("group", "東京23区")
    if g not in GROUPS:
        GROUPS.append(g)


def stay_1night(c):
    """宿泊型を1泊（1泊2日）使ったときの自己負担。数え方が自治体で違うので揃える。
    range＝施設ごとに実額が違い自治体としての単価が無い（比較に使わない）。"""
    if c["stay_basis"] == "range" or c["stay"] is None:
        return None
    if c["stay_basis"] == "day":
        return c["stay"] * 2          # 1泊2日＝2日ぶん
    return c["stay"]                  # trip＝1泊2日の額そのもの


stays = sorted([(stay_1night(c), c["name"]) for c in real
                if stay_1night(c) is not None])
n_range = sum(1 for c in real if stay_1night(c) is None)
visits = sorted([(c["visit"], c["name"]) for c in real if c["visit"] is not None])
free_visit = [n for v, n in visits if v == 0]

if stays:
    lo_s, lo_n = stays[0]
    hi_s, hi_n = stays[-1]
    LEAD = ("宿泊型を1泊（1泊2日）使ったときの自己負担は、区として単価を公表している"
            "%d自治体のなかで%s（%s）から%s（%s）まで開いています。"
            "残る%d自治体は施設ごとに実額が決まり、区としての単価がありません"
            % (len(stays), ("0円" if lo_s == 0 else "{:,}円".format(lo_s)), lo_n,
               "{:,}円".format(hi_s), hi_n, n_range))
else:
    LEAD = "自治体ごとに自己負担額が大きく違います"

SCOPE = ("東京23区＋政令指定都市"
         if any(g == "政令市" for g in GROUPS) else "東京23区")
TITLE = "産後ケアの料金はいくら？%s%d自治体の自己負担・回数上限【2026年度】" % (SCOPE, N)
H1 = "産後ケアの料金はいくら？｜自治体別の自己負担と回数上限がわかる早見ナビ"
DESC = ("産後ケア事業の利用料は市区町村が決めるため、同じ宿泊型1泊でも自己負担が0円の自治体と"
        "1万円近い自治体があります。%s計%d自治体の公式ページを確認し、宿泊型・日帰り型・"
        "訪問型の自己負担額、1回の出産あたりの上限回数、非課税世帯の減免、申請の期限を"
        "出典つきで収録しました。使いたい回数を入れると自己負担の合計が出ます。"
        "確認日は%s。" % (SCOPE, N, CHECKED))
OGD = ("産後ケアの自己負担は自治体で決まる。宿泊型・日帰り型・訪問型の実額と回数上限を"
       "%s計%d自治体ぶん収録。使う回数を入れると合計が出ます。" % (SCOPE, N))


def _fee_cell(c, k):
    return c["%s_label" % k] or "非公表"


def _limit_cell(c):
    parts = []
    for lab, k in (("宿泊", "limit_stay"), ("日帰り", "limit_day"), ("訪問", "limit_visit")):
        v = c[k]
        if v and v != "記載なし":
            parts.append("%s %s" % (lab, v))
    return "／".join(parts) if parts else "非公表"


def _rows_for(g):
    return "".join(
        '<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
        % (c["name"], _fee_cell(c, "stay"), _fee_cell(c, "day"),
           _fee_cell(c, "visit"), _limit_cell(c))
        for c in real if c.get("group", "東京23区") == g)


if len(GROUPS) > 1:
    ROWS = "".join(
        ('<tr><td colspan="5" style="background:#f2efe9;font-weight:700;'
         'color:#7c2e42;padding:10px 8px">%s（%d自治体）</td></tr>'
         % (g, sum(1 for c in real if c.get("group", "東京23区") == g))) + _rows_for(g)
        for g in GROUPS)
else:
    ROWS = _rows_for(GROUPS[0])

GROUP_LABEL = "・".join("%s%d" % (g, sum(1 for c in real if c.get("group", "東京23区") == g))
                       for g in GROUPS)

SRCROWS = "".join(
    '<tr><td>%s</td><td><a href="%s" rel="noopener" target="_blank">%s</a></td><td>%s</td></tr>'
    % (c["name"], c["src"], c["src_label"], CHECKED) for c in CITIES)

OPTS = "".join('<option value="%s">%s</option>' % (c["key"], c["name"]) for c in CITIES)

genmen_free = [c["name"] for c in real
               if "免除" in c["genmen"] or "無償" in c["genmen"] or "無料" in c["genmen"]]

FAQ = [
 ("産後ケアの料金はいくらですか？",
  "産後ケア事業は母子保健法にもとづく市区町村の事業で、利用者負担額は自治体が決めます。"
  "そのため同じ「宿泊型1泊2日」でも自己負担は自治体で大きく違います。%s。"
  "日帰り型は1回あたり数百円から3,500円程度、訪問型は0円から1,200円程度が"
  "収録した範囲での幅でした。金額は%s時点の各自治体公式ページの値です。"
  % (LEAD, CHECKED)),
 ("宿泊型の金額は1泊あたりですか？",
  "自治体によって数え方が3通りに分かれます。ひとつ目は「1日あたりいくら」という単価型で、"
  "1泊2日なら2日ぶんが課金されます。ふたつ目は「1泊2日でいくら、以降1日増えるごとにいくら」"
  "という区分型です。みっつ目は自治体としての単価を持たず、施設が決めた額から自治体の"
  "負担額を差し引いた残りが自己負担になる差額型で、この場合は同じ区の中でも施設によって"
  "自己負担が数倍変わります。数え方を確かめずに金額だけを並べると比較を誤ります。"
  "本ツールはこの3通りを自治体ごとに持たせて計算しています。"),
 ("住民税非課税世帯は無料になりますか？",
  "多くの自治体が非課税世帯・生活保護世帯の減免を設けていますが、扱いは"
  "「全額免除」「半額」「定額まで減額」と分かれます。%s。"
  "注意したいのは、減免が自動では適用されない自治体があることです。"
  "利用登録とは別に減免の申請が必要な場合があるため、申込先に確認してください。"
  % ("収録した範囲では" + "・".join(genmen_free[:8]) + "などが免除または無償と明記しています"
     if genmen_free else "自治体ごとに扱いが異なります")),
 ("何回まで使えますか？",
  "1回の出産あたりで上限が決まっているのが基本です。類型ごとに上限を設ける自治体と、"
  "3類型を合算して「あわせて7回まで」とする自治体があります。多胎児の場合は上限を"
  "上乗せする自治体もあります。金額が安くても使える回数が少なければ受けられるケアの"
  "総量は小さくなるので、金額と回数はセットで見てください。"),
 ("いつまでに申し込めばいいですか？",
  "利用前の申請が必要な自治体が大半で、妊娠中から申し込める自治体が多くあります。"
  "妊娠8か月以降・妊娠28週以降・妊娠30週以降といった開始時期が設定されていたり、"
  "利用希望日の2週間前までという締切があったりします。産後に思い立ってから申請すると"
  "使いたい時期に間に合わないことがあるため、妊娠中の面談の機会に登録まで済ませておくのが"
  "確実です。"),
 ("産後何か月まで使えますか？",
  "母子保健法は産後1年以内を想定していますが、類型ごとに期間を短く設定している"
  "自治体があります。宿泊型と日帰り型は「産後4か月未満」「産後5か月未満」とし、"
  "訪問型だけ産後1年未満とする例が複数ありました。里帰り出産を予定している場合は、"
  "対象期間と住民票の要件を先に確認してください。"),
 ("自己負担が0円の自治体は、本当に無料ですか？",
  "自己負担0円には2つの型があります。もともと利用者負担を設定していない場合と、"
  "自治体が基本利用料を全額補助している場合です。後者は補助の対象外になる費用"
  "（差額ベッド代など）が別に発生することがあります。また、産後ケアの利用料が"
  "無料でも、施設までの交通費や食事の一部が実費になることがあります。"),
 ("この表に無い自治体はどう調べればいいですか？",
  "産後ケア事業は全国の市区町村が実施しているので、「お住まいの自治体名＋産後ケア」で"
  "公式ページを探すのが確実です。確認する項目は、①実施している類型、②類型ごとの"
  "自己負担額、③1回の出産あたりの上限回数、④非課税世帯の減免と申請の要否、"
  "⑤対象期間と申請の締切の5つです。本ツールの表と同じ並びにしてあります。"),
]

faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
    for q, a in FAQ]}, ensure_ascii=False)
app_ld = json.dumps({
    "@context": "https://schema.org", "@type": "WebApplication",
    "name": "産後ケア 自治体別 料金ナビ", "url": URL,
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
    {"@type": "ListItem", "position": 3, "name": "産後ケア 自治体別 料金ナビ"}]}, ensure_ascii=False)

shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
CSS = shell[shell.find("<style>"):shell.find("</style>") + 8]

faq_html = "\n".join("<h3>Q%d. %s</h3>\n<p>%s</p>" % (i + 1, q, a)
                     for i, (q, a) in enumerate(FAQ))
DATA_JS = json.dumps({c["key"]: c for c in CITIES}, ensure_ascii=False,
                     separators=(",", ":"))

TPL = io.open("scripts/_sangocare_body.html", encoding="utf-8").read()
HTML = (TPL.replace("__TITLE__", TITLE).replace("__DESC__", DESC).replace("__OGD__", OGD)
        .replace("__URL__", URL).replace("__H1__", H1).replace("__CSS__", CSS)
        .replace("__FAQLD__", faq_ld).replace("__APPLD__", app_ld).replace("__BCLD__", bc_ld)
        .replace("__OPTS__", OPTS).replace("__ROWS__", ROWS).replace("__SRCROWS__", SRCROWS)
        .replace("__FAQHTML__", faq_html).replace("__DATA__", DATA_JS)
        .replace("__SLUG__", SLUG).replace("__NCITY__", str(N))
        .replace("__SCOPE__", SCOPE)
        .replace("__CHECKED__", CHECKED).replace("__LEAD__", LEAD)
        .replace("__OISIX__", OISIX))

os.makedirs("tools/%s" % SLUG, exist_ok=True)
io.open("tools/%s/index.html" % SLUG, "w", encoding="utf-8").write(HTML)
print("written: tools/%s/index.html  %d chars  自治体%d件" % (SLUG, len(HTML), N))
print("宿泊型の幅:", stays[0] if stays else "-", "〜", stays[-1] if stays else "-")
print("訪問型0円:", "・".join(free_visit) or "なし")

# -*- coding: utf-8 -*-
"""育休取得率｜器具＋データ記事を同じ正本から生成する（2026-10-20 新設）

狙う語: 「育休 取得率」「育休 取得率 男性」
  tool_gate 2026-10-20: 2語とも GO（サジェスト10件・Google月間推定1,280／208・SERP上位に器具なし）
  data_gate 2026-10-20: GO（一致10）。「育休取得率 計算」は tool_gate NO-GO（計測下限未満）のため計算器は作らない
  keyword_queue.json の batting_order 10（tools/ikukyu-shutokuritsu・cluster 制度）

正本: scripts/data/ikukyu_shutokuritsu.json（scripts/fetch_ikukyu_r07.py が厚労省PDFから検算つきで作る）
数値は正本からだけ取る。差・順位はここで計算し、器具のJSにも同じ値を埋め込む。
型は scripts/build_sengyoshufu.py。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_shell import faq_html, source_list, table, write

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(io.open(os.path.join(HERE, "data", "ikukyu_shutokuritsu.json"), encoding="utf-8"))

TODAY = "2026-10-20"
CHECKED = D["checked"]
OISIX = "https://px.a8.net/svt/ejp?a8mat=4B8B4Q+5CWKMY+3RK+2TBJQA"  # agent/AGENT.md 案件台帳の値
TOOL_SLUG = "ikukyu-shutokuritsu"
ART_SLUG = "ikukyu-shutokuritsu-data"
TOOL_URL = "https://www.noe-match.com/tools/%s/" % TOOL_SLUG
KOUHYOU_URL = "https://jsite.mhlw.go.jp/iwate-roudoukyoku/content/contents/002414494.pdf"
KOUHYOU_LABEL = "岩手労働局『2025年4月から、男性労働者の育児休業取得率等の公表が従業員が300人超1,000人以下の企業にも義務化されます』"

S = {s["year"]: s for s in D["series"]}
YEARS = sorted(S)
LATEST = YEARS[-1]
PREV = YEARS[-2]
FIRST = YEARS[0]
L = S[LATEST]
P = S[PREV]
Y = {r["year"]: r for r in D["yuki"]}
K = D["kikan"]
SANGYO = D["sangyo"]
KIBO = D["kibo"]
NOTE = D["notes"]


def w(y):
    return S[y]["wareki"]


def pct(v):
    """公表値の桁のまま出す（12.65 を 12.7 に丸めない）"""
    return "%s%%" % repr(v)


def pt(v):
    return "%+.1fポイント" % v


# 男性が初めて10%・30%・50%を超えた調査年度
def first_over(th):
    return next(y for y in YEARS if S[y]["male"] >= th)


M10, M30, M50 = first_over(10), first_over(30), first_over(50)
F_PEAK = max(YEARS, key=lambda y: S[y]["female"])
F_ABOVE = [y for y in YEARS if S[y]["female"] > L["female"]]  # 最新より高かった年度
SG_M = sorted(SANGYO, key=lambda r: -r["male"])
SG_F = sorted([r for r in SANGYO if not r["female_small_sample"]], key=lambda r: -r["female"])
KF_LT1M = sum(K["female"][:3])
KM_LT2W = sum(K["male"][:2])
KM_LT1M = sum(K["male"][:3])
KM_LT3M = sum(K["male"][:4])
KF_10M = sum(K["female"][7:12])
KM_1M3M = K["male"][3]

assert LATEST == 2025 and L["male"] == 50.9 and L["female"] == 88.3, "正本の最新年が想定と違う。本文の言い回しを見直すこと"
assert (M10, M30, M50) == (2020, 2023, 2025)
assert F_PEAK == 2008 and F_ABOVE == [2007, 2008]
assert round(L["male"] - P["male"], 1) == 10.4 and round(L["female"] - P["female"], 1) == 1.7  # 概要本文の「10.4ポイント」「1.7ポイント」
assert K["labels"][8] == "12か月〜18か月未満" and K["female"][8] == 31.4

# ------------------------------------------------------------------ 共通部品
SRC = [(s["url"], s["label"]) for s in D["sources"]] + [(KOUHYOU_URL, KOUHYOU_LABEL)]
SRC_INTRO = ("取得率・取得期間・業種別・規模別の数値はすべて厚生労働省『令和7年度雇用均等基本調査』の公表値です。"
             "差・順位・区分の合計は、公表値から当サイトが計算しました。企業の公表制度の説明は労働局の資料によります。")

ALL_ROWS = []
for y in YEARS:
    s = S[y]
    ALL_ROWS.append(("%s%s" % (s["wareki"], "※" if s["excl3"] else ""), pct(s["female"]), pct(s["male"]),
                     ("%.1f" % (s["female"] - s["male"])) + "ポイント"))
YUKI_ROWS = [(w(y) if y in S else "", "%.1f%%" % Y[y]["female"], "%.1f%%" % Y[y]["male"],
              "%.1f%%" % S[y]["female"], pct(S[y]["male"])) for y in sorted(Y)]
SANGYO_ROWS = [(r["name"], ("＊" if r["female_small_sample"] else "") + "%.1f%%" % r["female"], "%.1f%%" % r["male"])
               for r in SG_M]
KIBO_ROWS = [(r["name"], "%.1f%%" % r["female"], "%.1f%%" % r["male"]) for r in KIBO]
KIKAN_ROWS = [(lab, "%.1f%%" % f, "%.1f%%" % m) for lab, f, m in zip(K["labels"], K["female"], K["male"])]

# ------------------------------------------------------------------ データ記事
ART_TITLE = "育休取得率は男性%.1f%%・女性%.1f%%｜推移と業種別" % (L["male"], L["female"])
ART_H1 = "育休の取得率は男性%.1f%%・女性%.1f%%（%s調査）｜1996年度からの推移と業種・規模・取得期間" % (
    L["male"], L["female"], w(LATEST))
assert len(ART_TITLE) <= 32, len(ART_TITLE)

FAQ_ART = [
    ("育休の取得率は最新で何%ですか？",
     "厚生労働省『令和7年度雇用均等基本調査』（令和8年7月31日公表）では、女性%.1f%%、男性%.1f%%です。"
     "前回（%s）の女性%.1f%%・男性%.1f%%から、女性は%.1fポイント、男性は%.1fポイント上がりました。"
     "男性が50%%を超えたのは、この調査で初めてです。"
     % (L["female"], L["male"], w(PREV), P["female"], P["male"], L["female"] - P["female"], L["male"] - P["male"])),
    ("この取得率は、いつ出産した人の数字ですか？",
     "令和7年度調査の取得率は、令和5年10月1日〜令和6年9月30日の1年間に出産した女性（男性は配偶者が出産した男性）のうち、"
     "令和7年10月1日までに育児休業を始めた人（申出をしている人を含む）の割合です。"
     "「令和7年度」は調査の年度で、出産した年ではありません。"),
    ("男性の取得率50.9%は、男性の半分が長く休んでいるという意味ですか？",
     "いいえ。取得率は「育休を始めたかどうか」の割合で、期間は問いません。同じ調査の取得期間の集計（令和6年度に育休を終えて復職した人）では、"
     "男性は「1か月〜3か月未満」が%.1f%%で最も多く、1か月未満が合わせて%.1f%%、2週間未満が%.1f%%でした。"
     "女性は10か月以上が合わせて%.1f%%です。" % (KM_1M3M, KM_LT1M, KM_LT2W, KF_10M)),
    ("会社が公表している男性育休取得率と、この数字は同じですか？",
     "同じではありません。従業員300人超の企業が公表する割合は、公表前の事業年度に「育児休業等をした男性」を「配偶者が出産した男性」で割るもので、"
     "育児目的の休暇を足した割合で公表することもできます。分母と分子で数える年が同じとは限らないため、100%を超えることもあります。"
     "この記事の数字は、国が全国の事業所から抽出して調べた推計値です。"),
    ("業種によって男性の取得率はどれくらい違いますか？",
     "令和7年度調査の産業別では、男性が最も高いのは%s（%.1f%%）、最も低いのは%s（%.1f%%）で、%.1fポイントの差があります。"
     "事業所規模別では、500人以上が%.1f%%、5〜29人が%.1f%%でした。"
     % (SG_M[0]["name"], SG_M[0]["male"], SG_M[-1]["name"], SG_M[-1]["male"], SG_M[0]["male"] - SG_M[-1]["male"],
        KIBO[0]["male"], KIBO[3]["male"])),
    ("契約社員など有期雇用でも育休は取れていますか？",
     "同じ調査で、有期契約労働者の取得率は女性%.1f%%、男性%.1f%%です。全体（女性%.1f%%・男性%.1f%%）と比べると、女性は%.1fポイント低く、"
     "男性は%.1fポイント低い水準です。有期雇用の育休には、子が1歳6か月になるまでに契約が満了することが明らかでないことなどの要件があります。"
     % (Y[LATEST]["female"], Y[LATEST]["male"], L["female"], L["male"], L["female"] - Y[LATEST]["female"], L["male"] - Y[LATEST]["male"])),
    ("この数字は、育休を取るかどうかを決める参考になりますか？",
     "世の中の動きを知る目安にはなりますが、個々の家庭の答えにはなりません。取るかどうか、どれくらいの期間にするかは、勤め先の制度、収入、"
     "保育園の入園時期、体調、夫婦の分担で決まります。給付金の額や延長の条件は、下の関連ツール・記事で確かめてください。"),
]


def build_article():
    toc = [("latest", "%s調査の最新値" % w(LATEST)), ("teigi", "「取得率」の分母と分子"),
           ("suii", "1996年度からの推移"), ("fushime", "男性の取得率が動いた年"),
           ("kikan", "取得率と取得期間は別もの"), ("gyoshu", "業種別の取得率"),
           ("kibo", "事業所規模別の取得率"), ("yuki", "有期契約労働者の取得率"),
           ("papa", "産後パパ育休の割合"), ("kouhyou", "企業の公表値との違い"),
           ("chui", "数字を扱うときの注意"), ("related", "関連する記事とツール"),
           ("faq", "よくある質問（FAQ）"), ("src", "出典")]
    toc_html = ('<nav class="toc" aria-label="目次"><p style="font-weight:700;margin:0 0 8px">目次</p><ol>'
                + "".join('<li><a href="#%s">%s</a></li>' % t for t in toc) + "</ol></nav>")

    body = []
    body.append(
        "<blockquote><strong>育児休業の取得率は、女性%.1f%%、男性%.1f%%です（厚生労働省『令和7年度雇用均等基本調査』）。"
        "男性は前回の%.1f%%から%.1fポイント上がり、調査で初めて50%%を超えました。</strong>"
        "ただし取得率は「育休を始めたかどうか」の割合で、期間は含みません。同じ調査では、育休を終えて復職した男性の%.1f%%が1か月未満でした。"
        "%sに公表された原資料（結果概要と付属統計表）で、%sに数値を確認しています。</blockquote>"
        % (L["female"], L["male"], P["male"], L["male"] - P["male"], KM_LT1M, D["published"], CHECKED))
    body.append(toc_html)
    body.append(
        '<p>調査年度を選んでその年の数字だけを見たい場合や、業種・規模を選んで全体と比べたい場合は、'
        '<a href="/tools/%s/">育休の取得率を年度・業種で調べるツール</a>を使ってください。'
        "このページには、公表されている%d回分の推移と、業種・規模・取得期間・有期雇用の表をまとめています。</p>" % (TOOL_SLUG, len(YEARS)))

    body.append('<h2 id="latest">%s調査の最新値</h2>' % w(LATEST))
    body.append(table(["区分", "%s調査" % w(LATEST), "%s調査（前回）" % w(PREV), "差"],
                      [("女性の取得率", "%.1f%%" % L["female"], "%.1f%%" % P["female"], pt(L["female"] - P["female"])),
                       ("男性の取得率（産後パパ育休を含む）", "%.1f%%" % L["male"], "%.1f%%" % P["male"], pt(L["male"] - P["male"])),
                       ("有期契約労働者の女性", "%.1f%%" % Y[LATEST]["female"], "%.1f%%" % Y[PREV]["female"], pt(Y[LATEST]["female"] - Y[PREV]["female"])),
                       ("有期契約労働者の男性", "%.1f%%" % Y[LATEST]["male"], "%.1f%%" % Y[PREV]["male"], pt(Y[LATEST]["male"] - Y[PREV]["male"])),
                       ("男性育休取得者のうち産後パパ育休を取った人", "%.1f%%" % D["papa_ikukyu_share"]["2025"]["all"],
                        "%.1f%%" % D["papa_ikukyu_share"]["2024"]["all"],
                        pt(D["papa_ikukyu_share"]["2025"]["all"] - D["papa_ikukyu_share"]["2024"]["all"]))],
                      ["", "n", "n", "n"]))
    body.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a>（%s確認）。差は当サイトが計算。</p>'
                % (SRC[1][0], SRC[1][1], CHECKED))
    body.append(
        "<p>男性の取得率は、%s調査の%.2f%%から3年で%.1f%%まで上がりました。上がり方は女性と比べものにならないほど急ですが、"
        "それでも女性との差は%.1fポイントあります。女性の取得率は2000年代後半から80%%台で推移していて、今回の%.1f%%は"
        "%s（%s）に次ぐ高さです。</p>"
        % (w(2022), S[2022]["male"], L["male"], L["female"] - L["male"], L["female"],
           "・".join(w(y).replace("年度", "") for y in F_ABOVE) + "年度調査",
           "・".join("%.1f%%" % S[y]["female"] for y in F_ABOVE)))

    body.append('<h2 id="teigi">「取得率」の分母と分子</h2>')
    body.append(
        "<p>この調査の取得率は、次の式で計算されています。</p>"
        "<p><strong>取得率 ＝ 育休を始めた人 ÷ 出産した人（男性は配偶者が出産した人）</strong></p>"
        "<ul><li><strong>分母</strong>：%s</li><li><strong>分子</strong>：%s</li></ul>"
        "<p>ポイントは3つあります。1つ目は、<strong>調査の年度と出産の時期が1年ずれている</strong>ことです。"
        "「令和7年度の取得率」は、令和5年10月〜令和6年9月に生まれた子についての数字です。"
        "2つ目は、<strong>まだ始めていなくても申出をしていれば分子に入る</strong>ことです。"
        "3つ目は、<strong>1日でも育休を始めれば分子に入る</strong>ことです。期間の長さは取得率には反映されません。</p>"
        "<p>また、男性の取得率は令和5年度（2023年度）調査から産後パパ育休を含みます。"
        "調査は全数ではなく、全国の事業所から抽出して全体を推計する標本調査です。</p>"
        % (D["bunbo"], D["bunshi"]))

    body.append('<h2 id="suii">1996年度からの推移</h2>')
    body.append("<p>結果概要の図に載っている%d回分を、間引かずに並べます。右の列は女性と男性の差です。"
                "2007年度までは毎年ではなく、調査があった年度だけの値です。</p>" % len(YEARS))
    body.append(table(["調査年度", "女性", "男性", "男女差"], ALL_ROWS, ["", "n", "n", "n"]))
    body.append('<p class="srcline">※%s。%s。%s。出典：<a href="%s" rel="noopener" target="_blank">%s</a>（図4）</p>'
                % (NOTE["y2011"], NOTE["papa"], NOTE["kikan"], SRC[1][0], SRC[1][1]))
    body.append(
        "<p>女性は、%s調査の%.1f%%から%s調査の%.1f%%まで上がり、その後は80〜88%%台で上下しています。"
        "男性は%s調査の%.2f%%から、2010年代半ばまで1〜3%%台にとどまり、2017年度以降に上がり始めました。</p>"
        % (w(FIRST), S[FIRST]["female"], w(F_PEAK), S[F_PEAK]["female"], w(FIRST), S[FIRST]["male"]))

    body.append('<h2 id="fushime">男性の取得率が動いた年</h2>')
    body.append(
        "<ul>"
        "<li><strong>%s調査</strong>：%.2f%%。初めて10%%を超えました（前回%.2f%%）。</li>"
        "<li><strong>%s調査</strong>：%.1f%%。初めて30%%を超え、前回の%.2f%%から%.1fポイント上がりました。"
        "この年度から、男性の取得率に産後パパ育休が含まれています。</li>"
        "<li><strong>%s調査</strong>：%.1f%%。前回から%.1fポイント上昇。</li>"
        "<li><strong>%s調査</strong>：%.1f%%。初めて50%%を超えました。</li>"
        "</ul>"
        "<p>%s調査の大きな伸びは、産後パパ育休（出生時育児休業）が始まった時期と重なります。"
        "ただし、調査の数字だけでは制度改正の効果をそれ以外の要因と分けられないため、このページでは「時期が重なる」とだけ書いておきます。</p>"
        % (w(M10), S[M10]["male"], S[YEARS[YEARS.index(M10) - 1]]["male"],
           w(M30), S[M30]["male"], S[2022]["male"], S[M30]["male"] - S[2022]["male"],
           w(2024), S[2024]["male"], S[2024]["male"] - S[2023]["male"],
           w(M50), S[M50]["male"], w(M30)))

    body.append('<h2 id="kikan">取得率と取得期間は別もの</h2>')
    body.append(
        "<p>取得率が上がっても、休む期間が長くなったとは限りません。同じ調査に、育休を終えて復職した人の取得期間の分布があります。"
        "%s</p>" % K["note"].replace("（%）", "です。"))
    body.append(table(["取得期間", "女性", "男性"], KIKAN_ROWS, ["", "n", "n"]))
    body.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a>（表12）。'
                "取得率（令和5年10月〜令和6年9月の出産）とは対象の人が違います。</p>" % (SRC[1][0], SRC[1][1]))
    body.append(
        "<p>男性は「1か月〜3か月未満」が%.1f%%で最も多く、次いで「2週間〜1か月未満」%.1f%%、「5日〜2週間未満」%.1f%%でした。"
        "区分を足すと、<strong>男性の%.1f%%が1か月未満、%.1f%%が3か月未満</strong>で復職しています。"
        "女性は「12か月〜18か月未満」%.1f%%、「10か月〜12か月未満」%.1f%%の順で、10か月以上が合わせて%.1f%%です。"
        "1か月未満の女性は%.1f%%でした。</p>"
        "<p>つまり「男性の半分が育休を取る」時代になっても、多くは数週間〜数か月です。"
        "夫婦で休む時期をどう組むかは、<a href=\"/articles/ikukyu-fuufu-doji/\">育休を夫婦同時に取るとどうなるか</a>にまとめています。</p>"
        % (K["male"][3], K["male"][2], K["male"][1], KM_LT1M, KM_LT3M, K["female"][8], K["female"][7], KF_10M, KF_LT1M))

    body.append('<h2 id="gyoshu">業種別の取得率</h2>')
    body.append("<p>%s調査の産業別の値を、男性の取得率が高い順に並べます。</p>" % w(LATEST))
    body.append(table(["産業", "女性", "男性"], SANGYO_ROWS, ["", "n", "n"]))
    body.append('<p class="srcline">%s。出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>'
                % (NOTE["small"], SRC[2][0], SRC[2][1]))
    body.append(
        "<p>男性は%s（%.1f%%）、%s（%.1f%%）、%s（%.1f%%）が上位で、%s（%.1f%%）、%s（%.1f%%）が下位です。"
        "最も高い業種と低い業種の差は%.1fポイントあります。女性は＊の付いた業種を除くと%s（%.1f%%）が最も高く、"
        "%s（%.1f%%）が最も低くなっています。</p>"
        "<p>業種別の値は、その業種で出産した人・配偶者が出産した人の数が少ないほど年ごとに振れやすくなります。"
        "1回の調査の順位で「この業種は取りやすい」と決めつけず、全体の傾向として見てください。</p>"
        % (SG_M[0]["name"], SG_M[0]["male"], SG_M[1]["name"], SG_M[1]["male"], SG_M[2]["name"], SG_M[2]["male"],
           SG_M[-1]["name"], SG_M[-1]["male"], SG_M[-2]["name"], SG_M[-2]["male"], SG_M[0]["male"] - SG_M[-1]["male"],
           SG_F[0]["name"], SG_F[0]["female"], SG_F[-1]["name"], SG_F[-1]["female"]))

    body.append('<h2 id="kibo">事業所規模別の取得率</h2>')
    body.append(table(["事業所規模", "女性", "男性"], KIBO_ROWS, ["", "n", "n"]))
    body.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a>。規模は企業全体ではなく事業所（支店・工場など）単位です。</p>'
                % (SRC[2][0], SRC[2][1]))
    body.append(
        "<p>男性は規模が大きいほど高く、500人以上の%.1f%%に対し、5〜29人は%.1f%%です（差%.1fポイント）。"
        "女性は30人以上の区分がいずれも9割を超える一方、5〜29人は%.1f%%と1割以上低くなっています。"
        "小さな事業所ほど、休む人の代わりを確保しにくいことが背景として考えられますが、調査はその理由までは集計していません。</p>"
        % (KIBO[0]["male"], KIBO[3]["male"], KIBO[0]["male"] - KIBO[3]["male"], KIBO[3]["female"]))

    body.append('<h2 id="yuki">有期契約労働者の取得率</h2>')
    body.append("<p>契約期間を定めて雇われている人（有期契約労働者）だけの取得率です。表の右2列は、同じ年度の全体の値です。</p>")
    body.append(table(["調査年度", "有期・女性", "有期・男性", "全体・女性", "全体・男性"], YUKI_ROWS, ["", "n", "n", "n", "n"]))
    body.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a>（表5・図4）</p>' % (SRC[1][0], SRC[1][1]))
    body.append(
        "<p>有期の男性は、%s調査の%.1f%%から%s調査の%.1f%%まで上がりました。全体の男性（%.1f%%）との差は%.1fポイントです。"
        "有期の女性は%.1f%%で、全体の女性より%.1fポイント低い水準が続いています。"
        "有期雇用の人が育休を取るには、子が1歳6か月になるまでに契約が満了することが明らかでない、などの要件があります。</p>"
        % (w(2013), Y[2013]["male"], w(LATEST), Y[LATEST]["male"], L["male"], L["male"] - Y[LATEST]["male"],
           Y[LATEST]["female"], L["female"] - Y[LATEST]["female"]))

    body.append('<h2 id="papa">産後パパ育休の割合</h2>')
    body.append(
        "<p>産後パパ育休（出生時育児休業）は、子の出生後8週間以内に最大4週間まで取れる、男性向けの育休です。"
        "%s調査では、育休を始めた男性のうち<strong>%.1f%%が産後パパ育休を取っていました</strong>（前回%.1f%%）。"
        "有期契約労働者の男性では%.1f%%（前回%.1f%%）です。</p>"
        "<p>育休を取った男性の半分以上が、出生直後の短い休みを使っていることになります。"
        "上の取得期間で1か月未満が%.1f%%を占めることとも合っています。</p>"
        % (w(LATEST), D["papa_ikukyu_share"]["2025"]["all"], D["papa_ikukyu_share"]["2024"]["all"],
           D["papa_ikukyu_share"]["2025"]["yuki"], D["papa_ikukyu_share"]["2024"]["yuki"], KM_LT1M))

    body.append('<h2 id="kouhyou">企業の公表値との違い</h2>')
    body.append(
        "<p>「育休 取得率」と一緒に「計算」「計算方法」も検索されています。計算方法が法令で決められている数字に、企業が公表する男性育休取得率があります。"
        "育児・介護休業法により、従業員1,000人超の企業に加えて、2025年4月1日からは300人超1,000人以下の企業にも、"
        "男性の育児休業等の取得状況を年1回公表する義務があります。公表する割合は、次のどちらかです。</p>"
        "<ul><li>育児休業等をした男性 ÷ 配偶者が出産した男性</li>"
        "<li>（育児休業等をした男性 ＋ 育児を目的とした休暇制度を使った男性）÷ 配偶者が出産した男性</li></ul>"
        "<p>どちらも公表前の事業年度について数え、事業年度をまたいだ育休は「開始した日を含む年度」に入れます。"
        "前の年度に生まれた子の育休が今年度に入ることがあるため、<strong>企業の公表値は100%%を超えることがあります</strong>。"
        "この記事の国の調査とは、分母・分子の取り方も対象も違うので、並べて比べないでください。</p>"
        '<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>' % (KOUHYOU_URL, KOUHYOU_LABEL))

    body.append('<h2 id="chui">数字を扱うときの注意</h2>')
    body.append(
        "<h3>「令和7年度」は出産の年ではない</h3><p>取得率の年度は調査の年度です。令和7年度調査は、令和5年10月〜令和6年9月の出産が対象です。"
        "ニュースで「2025年度の男性育休取得率」と書かれていても、2025年度に生まれた子の数字ではありません。</p>"
        "<h3>2011年度は全国値ではない</h3><p>%s。前後の年度とはそのまま比べられません。</p>"
        "<h3>2010年度以前は分母の期間が違う</h3><p>%s。2011年度以降は「調査の前々年10月1日から前年9月30日まで」の1年間です。</p>"
        "<h3>標本調査の推計値</h3><p>全国の事業所から抽出して調べた推計値です。特に業種別は、出産した人の数が少ない業種ほど振れが大きくなります。"
        "＊の付いた値は、分母となるサンプル数が少ない（労働者数9以下など）ため、利用に注意が必要です。</p>"
        "<h3>統計は個々の職場の答えではない</h3><p>業種や規模の平均が高くても、勤め先で取りやすいとは限りません。逆も同じです。"
        "育休の期間や給付金の額は、勤め先の制度と雇用保険の要件で決まります。</p>"
        % (NOTE["y2011"], NOTE["kikan"]))

    body.append('<h2 id="related">関連する記事とツール</h2><ul>'
                '<li><a href="/tools/%s/">育休の取得率を年度・業種で調べるツール</a>｜調査年度・業種・規模を選んで全体と比べる</li>'
                '<li><a href="/articles/ikukyu-kyufukin-data/">育児休業給付金はいくら？</a>｜67%%は180日まで・上限額（令和8年8月改定）</li>'
                '<li><a href="/tools/ikukyu-encho-hantei/">育休はいつまで延長できる？判定ツール</a>｜1歳6か月・2歳までの延長の条件</li>'
                '<li><a href="/articles/ikukyu-fuufu-doji/">育休を夫婦同時に取るとどうなるか</a>｜メリットと落とし穴、期間の決め方</li>'
                '<li><a href="/articles/sango-kaji-buntan/">産後の家事分担はどう決めるか</a></li>'
                '<li><a href="/articles/tomobataraki-wariai-data/">共働き世帯の割合はどれくらい？</a>｜共働きの家庭はどれだけ増えたか</li>'
                "</ul>" % TOOL_SLUG)
    body.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    body.append(faq_html(FAQ_ART))
    body.append(source_list(SRC, SRC_INTRO))

    desc = ("育休の取得率は女性%.1f%%・男性%.1f%%（厚生労働省『令和7年度雇用均等基本調査』）。男性は前回から%.1fポイント上がり初めて50%%超え。"
            "1996年度からの推移、業種別・事業所規模別、有期雇用、取得期間（男性の%.1f%%は1か月未満）、企業の公表値との違いを整理。%s確認。"
            % (L["female"], L["male"], L["male"] - P["male"], KM_LT1M, CHECKED))
    ogd = "育休の取得率は男性%.1f%%・女性%.1f%%。男性は3年で%.2f%%から上がったが、復職した男性の%.1f%%は1か月未満だった。" % (
        L["male"], L["female"], S[2022]["male"], KM_LT1M)

    write(ART_SLUG, ART_TITLE, ART_H1, desc, ogd, FAQ_ART, "\n".join(body), TODAY, CHECKED,
          "数字を見たあとに、手元で変えられること",
          "育休を取っても取らなくても、子どもが生まれたあとの家事の総量は増えます。買い物と献立を考える時間を減らすのは、今日から手をつけられることの一つです。",
          aff_url=OISIX, aff_rel="nofollow sponsored noopener")


# ------------------------------------------------------------------ 器具
TOOL_TITLE = "育休の取得率を年度・業種で調べる｜男女別"
TOOL_H1 = "育休の取得率を調べる｜調査年度・業種・事業所規模を選んで男女別に"
assert len(TOOL_TITLE) <= 32, len(TOOL_TITLE)

FAQ_TOOL = [
    ("このツールで何が分かりますか？",
     "%s〜%sの調査年度を選ぶと、その年度の女性と男性の育休取得率、男女差、最新との差が出ます。もう1つ年度を選ぶと2つの年度の差も出ます。"
     "業種か事業所規模を選ぶと、%s調査のその区分の取得率と、全体との差が出ます。数値は厚生労働省『雇用均等基本調査』の公表値です。"
     % (w(FIRST), w(LATEST), w(LATEST))),
    FAQ_ART[0],
    FAQ_ART[1],
    FAQ_ART[2],
    ("業種別は過去の年度も選べますか？",
     "選べません。業種別・規模別は%s調査の付属統計表の値だけを載せています。過去の年度の業種別は、"
     "当サイトではまだ原資料で確認していないため、掲載していません。" % w(LATEST)),
    FAQ_ART[3],
]

JS_SERIES = [{"y": y, "w": S[y]["wareki"], "f": S[y]["female"], "m": S[y]["male"], "ex": S[y]["excl3"],
              "yf": (Y[y]["female"] if y in Y else None), "ym": (Y[y]["male"] if y in Y else None)} for y in YEARS]
JS_IND = ([{"g": "産業", "n": r["name"], "f": r["female"], "m": r["male"], "s": r["female_small_sample"]} for r in SANGYO]
          + [{"g": "事業所規模", "n": r["name"], "f": r["female"], "m": r["male"], "s": False} for r in KIBO])

TOOL_TPL = u"""<!DOCTYPE html>
<html lang="ja">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-VLQBH0S1SL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-VLQBH0S1SL');document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href*="px.a8.net"],a[href*="t.afi-b.com"]');if(a){try{gtag('event','aff_click',{link_domain:(a.href.indexOf('a8.net')>-1?'a8':'afb'),page_slug:location.pathname});}catch(x){}}},true);</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<link rel="canonical" href="__URL__">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__OGD__">
<meta property="og:type" content="website">
<meta property="og:url" content="__URL__">
<meta property="og:site_name" content="Noe結婚設計室">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="__TITLE__">
<meta name="twitter:description" content="__OGD__">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700;900&family=Noto+Serif+JP:wght@500;600;700;900&display=swap" rel="stylesheet">
__CSS__
<style>
.pick{display:flex;flex-wrap:wrap;gap:14px 22px;align-items:flex-end}
.pick label{display:block;font-weight:700;color:#1d242b;font-size:.92rem;margin:0 0 6px}
.pick select{padding:10px 12px;border:1px solid #d8d2c8;border-radius:4px;font-size:1rem;background:#fff;min-width:150px;max-width:100%}
.dt{width:100%;min-width:0;table-layout:fixed;border-collapse:collapse;margin:14px 0 0;font-size:.9rem;word-break:break-all}
.dt th,.dt td{border-bottom:1px solid #e6e2da;padding:9px 8px;text-align:left}
.dt th{width:54%;color:#5a6068;font-weight:500}
.dt td{font-weight:700;color:#7c2e42}
.bars{margin:18px 0 0}
.bars .row{display:flex;align-items:center;gap:8px;font-size:.72rem;color:#6b7178;line-height:1;margin:2px 0}
.bars .row span.y{width:6.5em;text-align:right;flex:none}
.bars .row span.b{display:block;height:9px;background:#d9cfc4;border-radius:2px}
.bars .row.on span.b{background:#7c2e42}
.bars .row.on{color:#1d242b;font-weight:700}
.bars .row span.v{flex:none}
table.cmp td.n{text-align:right;font-weight:700;color:#7c2e42;white-space:nowrap}
.srcline{font-size:.78rem;color:#6b7178;line-height:1.9;margin:8px 0 0}
</style>
<script type="application/ld+json">__FAQLD__</script>
<script type="application/ld+json">__APPLD__</script>
<script type="application/ld+json">__BCLD__</script>
</head>
<body>
<header><div class="header-inner">
<a href="/" class="logo">Noe結婚設計室<span class="logo-badge">2026</span></a>
<nav><a href="/#tools">ツール</a><a href="/articles/">記事一覧</a><a href="/#faq">FAQ</a><a href="/#about">運営者</a></nav>
</div></header>
<div class="wrap">
<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ 育休の取得率を年度・業種で調べる</div>

<div class="tool-hero" style="background-image:url('../../images/lp/room-light.jpg')"><div class="tool-hero-inner">
<h1>__H1__</h1>
<p>調査年度を選ぶと、その年度の女性と男性の育休取得率、男女差、最新との差が出ます。業種か事業所規模を選ぶと、全体との差も出ます。数値は厚生労働省『雇用均等基本調査』の公表値で、__CHECKED__に原資料で確認しました。</p>
</div></div>

<article>
<p class="pr-notice">本ページはプロモーションを含みます。ページ内に広告主から成果報酬を受け取るリンクが含まれます。掲載している統計の数値と計算は、広告とは関係なく公表値にもとづいています。</p>
<blockquote><strong>__LW__調査の育休取得率は、女性__LF__%・男性__LM__%です。</strong>令和5年10月〜令和6年9月に出産した人（男性は配偶者が出産した人）のうち、令和7年10月1日までに育休を始めた人の割合で、期間の長さは含みません。</blockquote>

<h2 id="shiraberu">年度と業種を選ぶ</h2>
<div class="calc" id="calcForm">
  <div class="pick">
    <div><label for="y1">調べたい調査年度</label><select id="y1"></select></div>
    <div><label for="y2">比べる調査年度（任意）</label><select id="y2"></select></div>
    <div><label for="ind">業種・事業所規模（任意・__LW__調査）</label><select id="ind"></select></div>
  </div>
  <button type="button" class="calc-btn" id="run" style="margin-top:18px">取得率を見る</button>
</div>

<div class="result" id="result" aria-live="polite">
  <div class="big"><div class="lbl" id="rLbl"></div><div class="num" id="rNum"></div></div>
  <table class="dt" id="rTable"></table>
  <div id="rCmp"></div>
  <div id="rInd"></div>
  <p id="rNote" style="font-size:.8rem;color:#6b7178;margin:14px 0 0;line-height:1.9"></p>
  <div class="bars" id="bars" aria-hidden="true"></div>
  <p style="font-size:.78rem;color:#6b7178;margin:14px 0 0;line-height:1.9">棒は男性の取得率（__FW__〜__LW__調査）。出典は厚生労働省『令和7年度雇用均等基本調査』事業所調査の結果概要（図4・表5）と付属統計表（第12表）（__CHECKED__確認）。差は当サイトが計算しています。統計は全体の傾向であり、個々の職場で取りやすいかどうかを示すものではありません。</p>
  <section id="line-cta-result" style="border:1px solid #e3ddd3;background:#f7f5f2;padding:18px 18px 20px;margin:24px 0 0;text-align:center">
    <p style="margin:0 0 6px;font-size:11px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif">NOE OFFICIAL LINE</p>
    <p style="margin:0 0 10px;font-size:16px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5">公表値が更新されたらお知らせします</p>
    <p style="margin:0 0 16px;font-size:13px;color:#5a6068;line-height:1.85">育休・給付金・保育の制度と、このサイトで使っている統計の更新を月1回まとめて配信します。</p>
    <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{gtag('event','line_add_result',{tool:'__SLUG__'});}catch(e){}" style="display:inline-block;background:#7c2e42;color:#ffffff;padding:12px 30px;font-size:14px;font-weight:600;text-decoration:none">友だち追加する</a>
    <p style="margin:10px 0 0;font-size:11px;color:#8a8f95">登録は無料。いつでも解除できます。</p>
  </section>
  <div style="border:1px solid #e3ddd3;border-radius:6px;padding:22px 24px;margin:24px 0 0;background:#faf8f5">
  <p style="font-size:.7rem;color:#999;margin:0 0 6px">PR</p>
  <p style="font-weight:900;margin:0 0 6px;color:#1d242b">数字を見たあとに、手元で変えられること</p>
  <p style="font-size:.86rem;color:#5a6068;margin:0 0 16px;line-height:1.9">育休を取っても取らなくても、子どもが生まれたあとの家事の総量は増えます。買い物と献立を考える時間を減らすのは、今日から手をつけられることの一つです。</p>
  <a href="__OISIX__" id="aff-oisix" rel="nofollow sponsored noopener" target="_blank" style="display:inline-block;background:#7c2e42;color:#fff;font-weight:700;padding:13px 32px;text-decoration:none">Oisixのおためしセットを見る</a>
  <p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">食材宅配サービス。このページの統計とは関係ありません</p>
  </div>
</div>

<h2 id="teigi">この取得率が指しているもの</h2>
<p><strong>取得率 ＝ 育休を始めた人 ÷ 出産した人（男性は配偶者が出産した人）</strong></p>
<ul>
<li><strong>分母</strong>：__BUNBO__</li>
<li><strong>分子</strong>：__BUNSHI__</li>
</ul>
<p>調査の年度と出産の時期は1年ずれています。また、1日でも育休を始めれば分子に入るので、取得率が高いことと、長く休めていることは別の話です。__LW__調査で育休を終えて復職した男性のうち、1か月未満の人は__LT1M__%でした。</p>

<h2 id="ichiran">直近5回の早見表</h2>
__RECENT_TABLE__
<p class="srcline">__N__回分すべての推移、取得期間・有期雇用・産後パパ育休の表、企業の公表値との違いは、<a href="/articles/__ART__/">育休取得率の推移データ</a>にまとめています。</p>

<h2 id="chui">数字を見るときの注意</h2>
<h3>2011年度は全国値ではありません</h3>
<p>__Y2011__。前後の年度とはそのまま比べられません。</p>
<h3>2023年度から男性に産後パパ育休を含みます</h3>
<p>__PAPA__。2022年度以前との差には、制度の追加も含まれます。</p>
<h3>業種別は振れやすい値です</h3>
<p>__SMALL__。業種別の値は、出産した人の数が少ない業種ほど年ごとに振れます。</p>
<h3>企業の公表値とは計算が違います</h3>
<p>従業員300人超の企業が公表する男性育休取得率は、公表前の事業年度に育児休業等をした男性を、配偶者が出産した男性で割るもので、100%を超えることもあります。このツールの国の調査とは分母・分子の取り方が違うため、並べて比べないでください。</p>

<h2 id="faq">よくある質問（FAQ）</h2>
__FAQHTML__

<h2 id="src">出典</h2>
<p>__SRCINTRO__（__CHECKED__確認）</p>
<ul style="font-size:.86rem;line-height:2">
__SRCLIST__
</ul>

<h2 id="related">関連するツールと記事</h2>
<ul>
<li><a href="/articles/__ART__/">育休取得率の推移データ</a>｜推移・業種・規模・取得期間・有期雇用</li>
<li><a href="/articles/ikukyu-kyufukin-data/">育児休業給付金はいくら？</a>｜67%は180日まで・上限額（令和8年8月改定）</li>
<li><a href="/tools/ikukyu-encho-hantei/">育休はいつまで延長できる？判定ツール</a>｜1歳6か月・2歳までの延長の条件</li>
<li><a href="/articles/ikukyu-fuufu-doji/">育休を夫婦同時に取るとどうなるか</a>｜メリットと落とし穴、期間の決め方</li>
<li><a href="/articles/sango-kaji-buntan/">産後の家事分担はどう決めるか</a></li>
</ul>
</article>

<!-- LINE-CTA -->
<section id="line-cta" style="max-width:680px;margin:56px auto 64px;padding:36px 28px;background:#f7f5f2;border:1px solid #e3ddd3;text-align:center;">
  <p style="margin:0 0 10px;font-size:12px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif;">NOE OFFICIAL LINE</p>
  <p style="margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5;">公表値が更新されたらお知らせします</p>
  <p style="margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;">育休・給付金・保育の制度と、このサイトで使っている統計の更新を月1回まとめて配信します。</p>
  <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{gtag('event','line_add_click',{tool:'__SLUG__'});}catch(e){}"
     style="display:inline-block;background:#7c2e42;color:#ffffff;padding:14px 36px;font-size:15px;font-weight:600;text-decoration:none;">友だち追加する</a>
  <p style="margin:14px 0 0;font-size:11px;color:#8a8f95;">登録は無料・配信は月1回だけ。いつでも解除できます。</p>
</section>
</div>
<footer><div class="footer-inner">
<div><a href="/">ホーム</a><a href="/articles/">記事一覧</a><a href="/about.html">運営者情報</a><a href="/privacy-policy.html">プライバシー</a><a href="/disclaimer.html">免責事項</a></div>
<p class="footer-disc">※本ツールの数値は厚生労働省『令和7年度雇用均等基本調査』の公表値（__CHECKED__確認）です。差は当サイトが計算しています。<strong style="color:#cda">【PR】</strong>本サイトはアフィリエイト広告を利用しています。</p>
</div></footer>
<button id="top" onclick="scrollTo({top:0,behavior:'smooth'})">↑</button>
<script>
(function(){
  var DATA=__JSDATA__;
  var IND=__JSIND__;
  var LATEST=__LATEST__;
  var by={};DATA.forEach(function(d){by[d.y]=d;});
  function $(id){return document.getElementById(id);}
  function p(v){var t=String(v);return (t.indexOf('.')<0?t+'.0':t)+'%';}
  function sg(n){var r=Math.round(n*10)/10;return (r>0?'+':'')+r.toFixed(1)+'ポイント';}
  var y1=$('y1'),y2=$('y2'),ind=$('ind');
  var o0=document.createElement('option');o0.value='';o0.textContent='選ばない';y2.appendChild(o0);
  for(var i=DATA.length-1;i>=0;i--){
    var a=document.createElement('option');a.value=DATA[i].y;a.textContent=DATA[i].w+'（'+DATA[i].y+'）';y1.appendChild(a);
    var b=document.createElement('option');b.value=DATA[i].y;b.textContent=DATA[i].w+'（'+DATA[i].y+'）';y2.appendChild(b);
  }
  var o1=document.createElement('option');o1.value='';o1.textContent='選ばない';ind.appendChild(o1);
  var grp={};
  IND.forEach(function(r,k){
    if(!grp[r.g]){grp[r.g]=document.createElement('optgroup');grp[r.g].label=r.g;ind.appendChild(grp[r.g]);}
    var o=document.createElement('option');o.value=k;o.textContent=r.n;grp[r.g].appendChild(o);
  });
  function row(th,td){return '<tr><th>'+th+'</th><td>'+td+'</td></tr>';}
  function draw(sel){
    var max=100,h='';
    DATA.forEach(function(d){
      h+='<div class="row'+(d.y==sel?' on':'')+'"><span class="y">'+d.w.replace('年度','')+'</span><span class="b" style="width:'+(Math.max(d.m,0.4)/max*70).toFixed(1)+'%"></span><span class="v">'+p(d.m)+'</span></div>';
    });
    $('bars').innerHTML=h;
  }
  function run(){
    var d=by[y1.value],Lt=by[LATEST];
    $('rLbl').textContent=d.w+'調査の育休取得率'+(d.ex?'（岩手・宮城・福島を除く）':'');
    $('rNum').textContent='男性 '+p(d.m)+' ／ 女性 '+p(d.f);
    var t=row('女性',p(d.f))+row('男性',p(d.m))+row('男女差（女性 − 男性）',(d.f-d.m).toFixed(1)+'ポイント');
    if(d.yf!==null){t+=row('有期契約労働者の女性',d.yf.toFixed(1)+'%')+row('有期契約労働者の男性',d.ym.toFixed(1)+'%');}
    if(d.y!=LATEST){t+=row('最新（'+Lt.w+'）との差・女性',sg(Lt.f-d.f))+row('最新（'+Lt.w+'）との差・男性',sg(Lt.m-d.m));}
    $('rTable').innerHTML=t;
    var c='';
    if(y2.value&&y2.value!=y1.value){
      var e=by[y2.value];
      c='<h3 style="font-size:.96rem;margin:22px 0 0;color:#1d242b">'+d.w+'と'+e.w+'を比べる</h3><table class="dt">'
        +row(e.w+'の女性・男性',p(e.f)+' ／ '+p(e.m))
        +row('女性の差（'+e.w+' − '+d.w+'）',sg(e.f-d.f))
        +row('男性の差（'+e.w+' − '+d.w+'）',sg(e.m-d.m))+'</table>';
    }
    $('rCmp').innerHTML=c;
    var s='';
    if(ind.value!==''){
      var r=IND[Number(ind.value)];
      s='<h3 style="font-size:.96rem;margin:22px 0 0;color:#1d242b">'+r.n+'（'+r.g+'・'+Lt.w+'調査）</h3><table class="dt">'
        +row('女性',(r.s?'＊':'')+r.f.toFixed(1)+'%')+row('男性',r.m.toFixed(1)+'%')
        +row('全体との差・女性',sg(r.f-Lt.f))+row('全体との差・男性',sg(r.m-Lt.m))+'</table>';
    }
    $('rInd').innerHTML=s;
    var n=[];
    if(d.ex||(y2.value&&by[y2.value].ex)){n.push('2011年度は岩手県・宮城県・福島県を除く全国の結果です。前後の年度とはそのまま比べられません。');}
    if(d.y<=2010||(y2.value&&Number(y2.value)<=2010)){n.push('2010年度までは、分母が調査前年度1年間の出産者です。');}
    if((d.y>=2023)!==(y2.value?Number(y2.value)>=2023:d.y>=2023)){n.push('2023年度以降の男性の取得率には産後パパ育休が含まれます。');}
    if(ind.value!==''&&IND[Number(ind.value)].s){n.push('＊は分母となるサンプル数が少ない（労働者数9以下など）ため、利用に注意が必要な値です。');}
    if(ind.value!==''&&d.y!=LATEST){n.push('業種・規模の値は'+Lt.w+'調査のものです（選んだ年度のものではありません）。');}
    $('rNote').textContent=n.join(' ');
    draw(d.y);
    $('result').classList.add('show');
    if(window.__ui)try{gtag('event','tool_result',{tool:'__SLUG__',year:String(d.y),compare:String(y2.value||''),ind:(ind.value!==''?IND[Number(ind.value)].n:'')});}catch(x){}
    try{$('result').scrollIntoView({behavior:'smooth',block:'start'});}catch(x){}
  }
  $('run').addEventListener('click',run);
})();
</script>
<script>(function(){['pointerdown','keydown','change'].forEach(function(t){document.addEventListener(t,function(){window.__ui=true},true)})})();</script>
</body>
</html>"""


def build_tool():
    desc = ("%s〜%sの調査年度を選ぶと、育休の取得率（女性・男性）と男女差、最新との差が出ます。%s調査は女性%.1f%%・男性%.1f%%。"
            "業種・事業所規模を選ぶと全体との差も分かります。厚生労働省『雇用均等基本調査』の公表値を%sに確認。"
            % (w(FIRST), w(LATEST), w(LATEST), L["female"], L["male"], CHECKED))
    ogd = "育休の取得率は%s調査で男性%.1f%%・女性%.1f%%。調査年度や業種を選んで確かめられます。" % (w(LATEST), L["male"], L["female"])
    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in FAQ_TOOL]}, ensure_ascii=False)
    app_ld = json.dumps({
        "@context": "https://schema.org", "@type": "WebApplication",
        "name": "育休の取得率を年度・業種で調べる", "url": TOOL_URL,
        "applicationCategory": "UtilitiesApplication", "operatingSystem": "All",
        "inLanguage": "ja", "description": desc,
        "datePublished": TODAY, "dateModified": TODAY,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
        "publisher": {"@type": "Organization", "name": "Noe結婚設計室",
                      "url": "https://www.noe-match.com/"}}, ensure_ascii=False)
    bc_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
        {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": "https://www.noe-match.com/#tools"},
        {"@type": "ListItem", "position": 3, "name": "育休の取得率を年度・業種で調べる"}]}, ensure_ascii=False)
    shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
    css = shell[shell.find("<style>"):shell.find("</style>") + 8]
    recent = ALL_ROWS[-5:]
    html = TOOL_TPL
    for k, v in (("__TITLE__", TOOL_TITLE), ("__DESC__", desc), ("__OGD__", ogd), ("__URL__", TOOL_URL),
                 ("__H1__", TOOL_H1), ("__CSS__", css), ("__FAQLD__", faq_ld), ("__APPLD__", app_ld),
                 ("__BCLD__", bc_ld), ("__CHECKED__", CHECKED), ("__SLUG__", TOOL_SLUG), ("__ART__", ART_SLUG),
                 ("__OISIX__", OISIX), ("__LATEST__", str(LATEST)), ("__LW__", w(LATEST)), ("__FW__", w(FIRST)),
                 ("__LF__", "%.1f" % L["female"]), ("__LM__", "%.1f" % L["male"]),
                 ("__LT1M__", "%.1f" % KM_LT1M), ("__N__", str(len(YEARS))),
                 ("__BUNBO__", D["bunbo"]), ("__BUNSHI__", D["bunshi"]),
                 ("__Y2011__", NOTE["y2011"]), ("__PAPA__", NOTE["papa"]), ("__SMALL__", NOTE["small"]),
                 ("__RECENT_TABLE__", table(["調査年度", "女性", "男性", "男女差"], recent, ["", "n", "n", "n"])),
                 ("__FAQHTML__", faq_html(FAQ_TOOL)), ("__SRCINTRO__", SRC_INTRO.rstrip("。") + "。"),
                 ("__SRCLIST__", "\n".join('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>' % s for s in SRC)),
                 ("__JSDATA__", json.dumps(JS_SERIES, ensure_ascii=False, separators=(",", ":"))),
                 ("__JSIND__", json.dumps(JS_IND, ensure_ascii=False, separators=(",", ":")))):
        html = html.replace(k, v)
    assert "__" not in html.replace("__proto__", "").replace("window.__ui", ""), \
        [m for m in __import__("re").findall(r"__[A-Z0-9_]+__", html)]
    os.makedirs("tools/%s" % TOOL_SLUG, exist_ok=True)
    io.open("tools/%s/index.html" % TOOL_SLUG, "w", encoding="utf-8", newline="\n").write(html)
    print("written: tools/%s/index.html  %d chars  title %d字" % (TOOL_SLUG, len(html), len(TOOL_TITLE)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    os.chdir(os.path.dirname(HERE))
    build_article()
    build_tool()
    print("article title %d字: %s" % (len(ART_TITLE), ART_TITLE))

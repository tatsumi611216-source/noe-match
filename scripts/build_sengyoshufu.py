# -*- coding: utf-8 -*-
"""専業主婦の割合｜器具＋データ記事を同じ正本から生成する（2026-09-19 新設）

狙う語: 「専業主婦 割合」
  tool_gate 2026-09-19: GO（サジェスト10件・Google月間推定6,480・SERP上位に器具なし）
  data_gate 2026-09-19: GO（一致10）
  GSC 8/18〜9/14: 「専業 主婦 割合 2019」表示12・「専業主婦 割合」表示4 が
  /articles/tomobataraki-wariai-data/ に着地している（専用の受け皿が無い）。
  「共働き世帯 割合 2022」表示22 など、年を指定した検索が出ているので、器具は「年で引く」にした。

正本: scripts/data/setai_kyoudou_sengyou.json（merge_setai_r08.py が検算つきで作る）
数値は正本からだけ取る。割合・倍率・増減率はここで計算し、器具のJSにも同じ値を埋め込む
（ページとJSで丸めがズレないようにするため）。

出荷基準（agent/AGENT.md「ツール＋データ記事の出荷基準」2026-09-19）への対応:
  title 32字以内（assert）／結果直後に LINE CTA と 広告 id="aff-oisix"／対のデータ記事／
  同クラスタからの内部リンクは scripts/add_sengyoshufu_links.py で張る
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_shell import faq_html, source_list, table, write

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(io.open(os.path.join(HERE, "data", "setai_kyoudou_sengyou.json"), encoding="utf-8"))

TODAY = "2026-09-19"
CHECKED = D["checked"]
OISIX = "https://px.a8.net/svt/ejp?a8mat=4B8B4Q+5CWKMY+3RK+2TBJQA"  # agent/AGENT.md 案件台帳の値
TOOL_SLUG = "sengyoshufu-wariai"
ART_SLUG = "sengyoshufu-wariai-data"
TOOL_URL = "https://www.noe-match.com/tools/%s/" % TOOL_SLUG

S = {s["year"]: s for s in D["series"]}
YEARS = sorted(S)
LATEST = YEARS[-1]
FIRST = YEARS[0]


def share(y):
    """専業主婦世帯 ÷（専業主婦世帯＋共働き世帯）。全国値が無い年は None"""
    s = S[y]
    if s["sengyou"] is None:
        return None
    return 100.0 * s["sengyou"] / (s["sengyou"] + s["kyoudou"])


def share_excl3(y):
    s = S[y]
    return 100.0 * s["sengyou_excl3"] / (s["sengyou_excl3"] + s["kyoudou_excl3"])


def bai(y):
    s = S[y]
    return None if s["sengyou"] is None else float(s["kyoudou"]) / s["sengyou"]


def man(v):
    return "{:,}万世帯".format(v)


def rate(key, a, b):
    return (S[b][key] - S[a][key]) * 100.0 / S[a][key]


L = S[LATEST]
SH_L = share(LATEST)
SH_F = share(FIRST)
# 50%を初めて下回った年・最後に上回った年
BELOW50_FIRST = next(y for y in YEARS if share(y) is not None and share(y) < 50)
ABOVE50_LAST = max(y for y in YEARS if share(y) is not None and share(y) >= 50)
# 白書本文の増減率と一致することを、生成側でも確かめる
for k, (a, b) in (("2010-2015", (2010, 2015)), ("2015-2020", (2015, 2020)), ("2020-2025", (2020, 2025))):
    assert round(rate("sengyou", a, b), 1) == D["whitepaper_rates"]["sengyou"][k]
    assert round(rate("kyoudou", a, b), 1) == D["whitepaper_rates"]["kyoudou"][k]
assert LATEST == 2025 and L["sengyou"] == 358 and L["kyoudou"] == 1254, "正本の最新年が想定と違う。本文の言い回しを見直すこと"
assert L["part"] + L["fulltime"] == L["kyoudou"]

# ------------------------------------------------------------------ 共通部品
SRC = [(s["url"], s["label"]) for s in D["sources"]]
SRC_INTRO = ("このページの数値はすべて次の内閣府の公表値（原資料は総務省『労働力調査』）です。"
             "割合・倍率・増減率は、公表された世帯数から当サイトが計算しました。計算式は本文に書いてあります。")

ALL_ROWS = []
for y in YEARS:
    s = S[y]
    if s["sengyou"] is None:
        ALL_ROWS.append(("%d年" % y, "（全国値なし）", "（全国値なし）", "—", "—"))
    else:
        ALL_ROWS.append(("%d年" % y, man(s["sengyou"]), man(s["kyoudou"]),
                         "%.1f%%" % share(y), "%.2f倍" % bai(y)))

FIVE = [y for y in YEARS if y % 5 == 0]
KEITAI_ROWS = [("%d年" % y, man(S[y]["fulltime"]), man(S[y]["part"])) for y in FIVE]
RATE_ROWS = [("%d年→%d年" % (a, b), "%+.1f%%" % rate("sengyou", a, b), "%+.1f%%" % rate("kyoudou", a, b))
             for a, b in ((2010, 2015), (2015, 2020), (2020, 2025))]

# ------------------------------------------------------------------ データ記事
ART_TITLE = "専業主婦の割合は%.1f%%｜%d年の最新値と40年の推移" % (SH_L, LATEST)
ART_H1 = "専業主婦の割合は何%%？%d年は%.1f%%｜1985年からの推移を1年刻みで" % (LATEST, SH_L)
assert len(ART_TITLE) <= 32, len(ART_TITLE)

FAQ_ART = [
    ("専業主婦の割合は最新で何%ですか？",
     "内閣府『男女共同参画白書 令和8年版』の系列では、%d年の専業主婦世帯は%s、共働き世帯は%sで、"
     "両者の合計に占める専業主婦世帯の割合は%.1f%%です。共働き世帯は専業主婦世帯の%.2f倍にあたります。"
     "この系列は「妻が64歳以下で、夫が非農林業の雇用者」の世帯に限った数字で、全世帯に占める割合ではありません。"
     % (LATEST, man(L["sengyou"]), man(L["kyoudou"]), SH_L, bai(LATEST))),
    ("専業主婦の割合はいつ半分を下回りましたか？",
     "この系列で計算すると、専業主婦世帯の割合が初めて50%%を下回ったのは%d年（%.1f%%）です。"
     "その後%d年に%.1f%%と一度だけ50%%を上回り、翌年以降は50%%を下回り続けています。"
     % (BELOW50_FIRST, share(BELOW50_FIRST), ABOVE50_LAST, share(ABOVE50_LAST))),
    ("30代や40代など、年代別の専業主婦の割合は分かりますか？",
     "この系列では分かりません。白書のこの図表は妻が64歳以下の世帯をまとめた合計で、妻の年代別の内訳はありません。"
     "年代別の数字を載せているページを見るときは、どの統計のどの表から取った数字か、分母が何かを確認してください。"
     "当サイトでは年代別の一次データを確認できていないため、掲載していません。"),
    ("専業主婦世帯はどれくらいの速さで減っていますか？",
     "5年ごとに見ると、2010年から2015年が%.1f%%、2015年から2020年が%.1f%%、2020年から2025年が%.1f%%の減少です。"
     "同じ期間の共働き世帯は%.1f%%、%.1f%%、%.1f%%の増加でした。白書の本文に書かれている増減率と、公表された世帯数から計算した値は一致しています。"
     % (abs(rate("sengyou", 2010, 2015)), abs(rate("sengyou", 2015, 2020)), abs(rate("sengyou", 2020, 2025)),
        rate("kyoudou", 2010, 2015), rate("kyoudou", 2015, 2020), rate("kyoudou", 2020, 2025))),
    ("自営業の家庭や、妻が65歳以上の家庭は含まれますか？",
     "含まれません。専業主婦世帯は「夫が非農林業の雇用者で、妻が非就業者、妻が64歳以下」の世帯、"
     "共働き世帯は「夫婦ともに非農林業の雇用者で、妻が64歳以下」の世帯です。"
     "自営業や農林業の世帯、妻が65歳以上の世帯、夫が雇用者でない世帯は、どちらの数にも入っていません。"),
    ("2011年の数字が無いのはなぜですか？",
     "東日本大震災の影響で、2011年は全国の値が公表されていません。岩手県・宮城県・福島県を除いた値"
     "（専業主婦世帯%s・共働き世帯%s）だけがあります。3県を除いた値で計算すると専業主婦世帯の割合は%.1f%%ですが、"
     "前後の年の全国値とはそのまま比べられません。"
     % (man(S[2011]["sengyou_excl3"]), man(S[2011]["kyoudou_excl3"]), share_excl3(2011))),
    ("この数字は、働くかどうかを決める参考になりますか？",
     "なりません。統計は全体の傾向を示すだけで、個々の家庭にとってどちらが良いかは示しません。"
     "収入、子どもの年齢、預け先、健康、本人の希望は家庭ごとに違います。"
     "このページは「世の中の数字がどうなっているか」を正確に知るためのもので、どちらかの選択を勧めるものではありません。"),
]


def build_article():
    toc = [("latest", "%d年の最新値" % LATEST), ("bunbo", "「割合」の分母は何か"),
           ("suii", "1985年からの推移（1年刻み）"), ("fushime", "節目になった年"),
           ("rate", "5年ごとの増減率"), ("keitai", "共働き側の中身：フルタイムとパート"),
           ("nendai", "年代別の割合はこの統計では分からない"), ("chui", "数字を扱うときの注意"),
           ("related", "関連する記事とツール"), ("faq", "よくある質問（FAQ）"), ("src", "出典")]
    toc_html = ('<nav class="toc" aria-label="目次"><p style="font-weight:700;margin:0 0 8px">目次</p><ol>'
                + "".join('<li><a href="#%s">%s</a></li>' % t for t in toc) + "</ol></nav>")

    body = []
    body.append(
        "<blockquote><strong>%d年の専業主婦世帯は%s、共働き世帯は%sです。"
        "両者の合計に占める専業主婦世帯の割合は%.1f%%で、共働き世帯は専業主婦世帯の%.2f倍でした。</strong>"
        "%d年は%.1f%%だったので、40年で半分以下になっています。"
        "ただしこれは「妻が64歳以下で、夫が会社などに雇われている世帯」だけを数えた系列の数字で、"
        "日本の全世帯に占める割合ではありません。内閣府が%sに公表している値を、%sに原典のCSVで確認しました。</blockquote>"
        % (LATEST, man(L["sengyou"]), man(L["kyoudou"]), SH_L, bai(LATEST), FIRST, SH_F,
           "令和8年7月", CHECKED))
    body.append(toc_html)
    body.append(
        '<p>年を選んでその年の数字だけを見たい場合は、<a href="/tools/%s/">専業主婦の割合を年別に調べるツール</a>を使ってください。'
        "このページには全41年ぶんの表と、数字の読み方をまとめています。</p>" % TOOL_SLUG)

    body.append('<h2 id="latest">%d年の最新値</h2>' % LATEST)
    body.append(table(["区分", "%d年" % LATEST, "%d年（前年）" % (LATEST - 1)],
                      [("専業主婦世帯（夫が雇用者・妻が非就業・妻64歳以下）", man(L["sengyou"]), man(S[LATEST - 1]["sengyou"])),
                       ("共働き世帯（夫婦とも雇用者・妻64歳以下）", man(L["kyoudou"]), man(S[LATEST - 1]["kyoudou"])),
                       ("専業主婦世帯の割合（2つの合計に対して）", "%.1f%%" % SH_L, "%.1f%%" % share(LATEST - 1)),
                       ("共働き世帯 ÷ 専業主婦世帯", "%.2f倍" % bai(LATEST), "%.2f倍" % bai(LATEST - 1))],
                      ["", "n", "n"]))
    body.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a>（%s確認）。割合と倍率は公表された世帯数から当サイトが計算。</p>'
                % (SRC[0][0], SRC[0][1], CHECKED))
    body.append(
        "<p>前年からの1年間で、専業主婦世帯は%d万世帯減り、共働き世帯は%d万世帯増えました。"
        "白書の本文は%d年時点の姿を「共働き世帯数は専業主婦世帯数の3.5倍」と書いており、上の計算（%.2f倍）と一致します。</p>"
        % (S[LATEST - 1]["sengyou"] - L["sengyou"], L["kyoudou"] - S[LATEST - 1]["kyoudou"], LATEST, bai(LATEST)))

    body.append('<h2 id="bunbo">「割合」の分母は何か</h2>')
    body.append(
        "<p>「専業主婦の割合」という言葉は、分母を決めないと数字になりません。このページの%.1f%%は、次の式で計算しています。</p>"
        "<p><strong>専業主婦世帯 ÷（専業主婦世帯 ＋ 共働き世帯）</strong></p>"
        "<p>2つの世帯の定義は、白書では次のとおりです。</p>"
        "<ul><li><strong>専業主婦世帯</strong>：%s</li><li><strong>共働き世帯</strong>：%s</li></ul>"
        "<p>%s つまり、分母は「夫が会社などに雇われていて、妻が64歳以下の夫婦」のうち、妻が雇われて働いているか、働いていないかの2通りだけです。"
        "単身世帯、高齢の夫婦、自営業の家庭は最初から分母に入っていません。</p>"
        "<p>そのため、この%.1f%%を「日本の女性の%.1f%%が専業主婦」「全世帯の%.1f%%が専業主婦世帯」と読み替えることはできません。"
        "全世帯に占める割合は、この系列からは計算できないため、このページには載せていません。%s</p>"
        % (SH_L, D["teigi"]["sengyou"], D["teigi"]["kyoudou"], D["teigi"]["fukumanai"],
           SH_L, SH_L, SH_L, D["teigi"]["teigi_src"]))

    body.append('<h2 id="suii">1985年からの推移（1年刻み）</h2>')
    body.append("<p>公表されている41年ぶんを、間引かずにすべて並べます。右の2列は世帯数から計算した値です。</p>")
    body.append(table(["年", "専業主婦世帯", "共働き世帯", "専業主婦世帯の割合", "共働き÷専業主婦"],
                      ALL_ROWS, ["", "n", "n", "n", "n"]))
    body.append('<p class="srcline">%s</p><p class="srcline">2011年の3県を除く値は、専業主婦世帯%s・共働き世帯%s（割合にすると%.1f%%）。'
                '2010年には全国値のほかに3県を除く値（専業主婦世帯%s・共働き世帯%s）も公表されています。</p>'
                '<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>'
                % (D["y2011"], man(S[2011]["sengyou_excl3"]), man(S[2011]["kyoudou_excl3"]), share_excl3(2011),
                   man(S[2010]["sengyou_excl3"]), man(S[2010]["kyoudou_excl3"]), SRC[0][0], SRC[0][1]))

    body.append('<h2 id="fushime">節目になった年</h2>')
    body.append(
        "<p>表から読み取れる節目を、計算で確かめた順に並べます。</p>"
        "<ul>"
        "<li><strong>%d年</strong>：専業主婦世帯%s・共働き世帯%sで、割合は%.1f%%。この系列の出発点です。</li>"
        "<li><strong>%d年</strong>：割合が%.1f%%となり、初めて50%%を下回りました（専業主婦世帯%s・共働き世帯%s）。</li>"
        "<li><strong>%d年</strong>：%.1f%%と、一度だけ50%%を上回りました。これが50%%を超えた最後の年です。</li>"
        "<li><strong>2019年</strong>：%.1f%%。3割を下回った最初の年です（2018年は%.1f%%）。</li>"
        "<li><strong>%d年</strong>：%.1f%%。専業主婦世帯は%sで、%d年の%.0f%%の水準です。</li>"
        "</ul>"
        "<p>「共働きと専業主婦が逆転したのは1997年」という説明を見かけますが、内閣府が現在公表しているこの系列の実数では、"
        "共働き世帯が専業主婦世帯を初めて上回ったのは%d年です。1997年は専業主婦世帯%s・共働き世帯%sで、すでに共働きのほうが多い状態でした。</p>"
        % (FIRST, man(S[FIRST]["sengyou"]), man(S[FIRST]["kyoudou"]), SH_F,
           BELOW50_FIRST, share(BELOW50_FIRST), man(S[BELOW50_FIRST]["sengyou"]), man(S[BELOW50_FIRST]["kyoudou"]),
           ABOVE50_LAST, share(ABOVE50_LAST),
           share(2019), share(2018),
           LATEST, SH_L, man(L["sengyou"]), FIRST, 100.0 * L["sengyou"] / S[FIRST]["sengyou"],
           BELOW50_FIRST, man(S[1997]["sengyou"]), man(S[1997]["kyoudou"])))
    assert share(2019) < 30 <= share(2018)

    body.append('<h2 id="rate">5年ごとの増減率</h2>')
    body.append("<p>減り方は一定ではなく、直近ほど速くなっています。</p>")
    body.append(table(["期間", "専業主婦世帯", "共働き世帯"], RATE_ROWS, ["", "n", "n"]))
    body.append('<p class="srcline">世帯数から計算した値。白書の本文（<a href="%s" rel="noopener" target="_blank">%s</a>）に書かれている増減率と一致することを確認しています。</p>'
                % (D["whitepaper_rates"]["src"], SRC[2][1]))
    body.append(
        "<p>2020年から2025年の5年間で、専業主婦世帯は%d万世帯から%d万世帯へ%d万世帯減りました。"
        "同じ期間に共働き世帯は%d万世帯増えています。減ったぶんがそのまま共働きに移ったと読みたくなりますが、"
        "この統計は同じ家庭を追いかけた調査ではないため、「専業主婦だった人が働き始めた」のか、"
        "「新しく結婚した夫婦に共働きが多い」のか、「妻が65歳になって集計から外れた」のかは、この数字からは分かりません。</p>"
        % (S[2020]["sengyou"], L["sengyou"], S[2020]["sengyou"] - L["sengyou"], L["kyoudou"] - S[2020]["kyoudou"]))

    body.append('<h2 id="keitai">共働き側の中身：フルタイムとパート</h2>')
    body.append(
        "<p>専業主婦世帯が減ったぶん、増えたのは共働き世帯です。その中身を妻の就業時間で分けると、%d年は妻がフルタイム（週35時間以上）の世帯が%s、"
        "パート（週35時間未満）の世帯が%sでした。%d年はフルタイム%s・パート%sだったので、40年間で増えたのは主にパートの側です。"
        "ただし直近は動きが変わっていて、2020年から%d年にかけてはフルタイムが%d万世帯増え、パートの増加は%d万世帯にとどまっています。</p>"
        % (LATEST, man(L["fulltime"]), man(L["part"]), FIRST, man(S[FIRST]["fulltime"]), man(S[FIRST]["part"]),
           LATEST, L["fulltime"] - S[2020]["fulltime"], L["part"] - S[2020]["part"]))
    body.append(table(["年", "妻フルタイム（週35時間以上）", "妻パート（週35時間未満）"], KEITAI_ROWS, ["", "n", "n"]))
    body.append('<p class="srcline">この区分は就業時間であって、正規・非正規の雇用形態ではありません。1985年は内訳の合計が共働き世帯の総数より%d万世帯少なく、内訳と総数は一致しません。'
                '出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>'
                % (S[1985]["naiyaku_gap"], SRC[1][0], SRC[1][1]))

    body.append('<h2 id="nendai">年代別の割合はこの統計では分からない</h2>')
    body.append(
        "<p>「専業主婦 割合」と一緒に検索されている言葉には「30代」「40代」「50代」「年代別」があります。"
        "しかし、このページで使っている内閣府の系列は、妻が64歳以下の世帯をまとめた合計だけで、妻の年代別の内訳はありません。</p>"
        "<p>年代別の数字を載せているページは、別の統計（労働力調査の詳細な集計表や国勢調査など）から取っているか、"
        "民間のアンケートを使っているはずです。見るときは次の3点を確かめてください。</p>"
        "<ul><li>どの統計・どの調査の、どの表の数字か</li>"
        "<li>分母は何か（その年代の女性全員か、結婚している女性か、夫が雇用者の世帯か）</li>"
        "<li>いつの数字か</li></ul>"
        "<p>当サイトでは、年代別の一次データをまだ確認できていません。確認できていない数字は載せない方針なので、このページには掲載していません。</p>")

    body.append('<h2 id="chui">数字を扱うときの注意</h2>')
    body.append(
        "<h3>調査が途中で切り替わっている</h3><p>%s 表の数字は1本の線に見えますが、2001年以前と2002年以降は同じ物差しではありません。</p>"
        "<h3>「専業主婦世帯」は統計上の呼び名</h3><p>統計上の区分は「男性雇用者と無業の妻から成る世帯」で、白書が図表の名前でこれを専業主婦世帯と呼んでいます。"
        "妻が求職中の場合や、育児や介護、病気などの事情で働いていない場合も、働いていなければここに入ります。本人が自分を専業主婦と考えているかどうかとは関係がありません。</p>"
        "<h3>夫が家事・育児を担う世帯は別の区分</h3><p>この系列は「夫が雇用者で妻が非就業」の世帯を数えています。妻が雇用者で夫が非就業の世帯は、専業主婦世帯にも共働き世帯にも入りません。</p>"
        "<h3>他の統計と掛け合わせない</h3><p>この数字は労働力調査（標本調査）から出ています。婚姻件数や離婚件数は人口動態統計（届出の全数）、未婚割合は国勢調査（5年ごとの全数調査）で、"
        "調査の設計が違います。掛け合わせて別の比率を作ると、意味のない数字になります。</p>"
        "<h3>統計は個々の家庭の答えではない</h3><p>%.1f%%という数字は、どちらの暮らし方が良いかを示すものではありません。収入、子どもの年齢、預け先、健康、本人の希望は家庭ごとに違います。"
        "家計の面から考えたい場合は、下の関連記事のシミュレーションを使ってください。</p>"
        % (D["chousa"], SH_L))

    body.append('<h2 id="related">関連する記事とツール</h2><ul>'
                '<li><a href="/tools/%s/">専業主婦の割合を年別に調べるツール</a>｜年を選ぶと、その年の世帯数・割合・最新年との差が出ます</li>'
                '<li><a href="/articles/tomobataraki-wariai-data/">共働き世帯の割合はどれくらい？</a>｜同じ系列を共働きの側から読む</li>'
                '<li><a href="/articles/sengyoshufu-seikatsuhi/">専業主婦世帯の生活費</a>｜片働きの家計をどう組むか</li>'
                '<li><a href="/articles/tomobataraki-shokuji-data/">共働き夫婦の食事はどうしている？</a>｜自炊・ミールキット・外食の費用と時間</li>'
                '<li><a href="/articles/sango-kaji-buntan/">産後の家事分担はどう決めるか</a></li>'
                '<li><a href="/tools/seikatsuhi-simulator/">ふたりの生活費シミュレーション</a></li>'
                "</ul>" % TOOL_SLUG)
    body.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    body.append(faq_html(FAQ_ART))
    body.append(source_list(SRC, SRC_INTRO))

    desc = ("%d年の専業主婦世帯は%s、共働き世帯は%sで、両者の合計に占める専業主婦世帯の割合は%.1f%%（共働きは%.2f倍）です。"
            "%d年の%.1f%%から40年の推移を1年刻みで全部載せ、割合の分母、50%%を下回った年、5年ごとの増減率、年代別が分からない理由まで整理しました。"
            "内閣府『男女共同参画白書 令和8年版』の公表値を%sに確認。"
            % (LATEST, man(L["sengyou"]), man(L["kyoudou"]), SH_L, bai(LATEST), FIRST, SH_F, CHECKED))
    ogd = "%d年は専業主婦世帯%s・共働き世帯%s。割合は%.1f%%で、%d年の%.1f%%から半分以下になりました。" % (
        LATEST, man(L["sengyou"]), man(L["kyoudou"]), SH_L, FIRST, SH_F)

    write(ART_SLUG, ART_TITLE, ART_H1, desc, ogd, FAQ_ART, "\n".join(body), TODAY, CHECKED,
          "数字を見たあとに、手元で変えられること",
          "統計は全体の傾向を示すだけで、個々の家庭の選択を決めるものではありません。"
          "共働きでも片働きでも、日々の家事の総量を減らすことは今日から手をつけられます。買い物と献立を考える時間を削るのはその一つです。",
          aff_url=OISIX, aff_rel="nofollow sponsored noopener")


# ------------------------------------------------------------------ 器具
TOOL_TITLE = "専業主婦の割合を年別に調べる｜%d〜%d年" % (FIRST, LATEST)
TOOL_H1 = "専業主婦の割合を年で調べる｜%d年〜%d年の世帯数と割合" % (FIRST, LATEST)
assert len(TOOL_TITLE) <= 32, len(TOOL_TITLE)

FAQ_TOOL = [
    ("このツールで何が分かりますか？",
     "%d年から%d年までの好きな年を選ぶと、その年の専業主婦世帯数、共働き世帯数、2つの合計に占める専業主婦世帯の割合、"
     "共働き世帯が専業主婦世帯の何倍か、最新年との差が出ます。もう1つ年を選ぶと、2つの年の差も出ます。"
     "数値は内閣府『男女共同参画白書 令和8年版』の公表値です。" % (FIRST, LATEST)),
    FAQ_ART[0],
    ("割合はどう計算していますか？",
     "専業主婦世帯 ÷（専業主婦世帯 ＋ 共働き世帯）です。どちらも「妻が64歳以下で、夫が非農林業の雇用者」の世帯に限った数なので、"
     "全世帯や全女性に占める割合ではありません。自営業の家庭や、妻が65歳以上の家庭は含まれていません。"),
    FAQ_ART[2],
    FAQ_ART[5],
    ("自分が生まれた年や、親が結婚した年と比べる意味はありますか？",
     "世の中の前提がどれくらい違ったかを知る目安にはなります。たとえば%d年は専業主婦世帯の割合が%.1f%%で、%d年は%.1f%%です。"
     "ただし統計は全体の傾向で、どちらの暮らし方が良いかを示すものではありません。"
     "1985〜2001年と2002年以降では調査の方法が違うため、離れた年どうしの差は目安として見てください。"
     % (FIRST, SH_F, LATEST, SH_L)),
]

JS_DATA = [{"y": y, "s": S[y]["sengyou"], "k": S[y]["kyoudou"], "p": S[y]["part"], "f": S[y]["fulltime"],
            "s3": S[y]["sengyou_excl3"], "k3": S[y]["kyoudou_excl3"],
            "sh": (None if share(y) is None else round(share(y), 1)),
            "bai": (None if bai(y) is None else round(bai(y), 2))} for y in YEARS]

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
.pick select{padding:10px 12px;border:1px solid #d8d2c8;border-radius:4px;font-size:1rem;background:#fff;min-width:150px}
.dt{width:100%;min-width:0;table-layout:fixed;border-collapse:collapse;margin:14px 0 0;font-size:.9rem;word-break:break-all}
.dt th,.dt td{border-bottom:1px solid #e6e2da;padding:9px 8px;text-align:left}
.dt th{width:54%;color:#5a6068;font-weight:500}
.dt td{font-weight:700;color:#7c2e42}
.bars{margin:18px 0 0}
.bars .row{display:flex;align-items:center;gap:8px;font-size:.72rem;color:#6b7178;line-height:1;margin:2px 0}
.bars .row span.y{width:3.2em;text-align:right;flex:none}
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
<div class="breadcrumb"><a href="/">ホーム</a> ＞ <a href="/#tools">無料ツール</a> ＞ 専業主婦の割合を年別に調べる</div>

<div class="tool-hero" style="background-image:url('../../images/lp/room-light.jpg')"><div class="tool-hero-inner">
<h1>__H1__</h1>
<p>年を選ぶと、その年の専業主婦世帯と共働き世帯の数、専業主婦世帯の割合、最新年との差が出ます。数値は内閣府『男女共同参画白書 令和8年版』の公表値で、__CHECKED__に原典のCSVで確認しました。</p>
</div></div>

<article>
<p class="pr-notice">本ページはプロモーションを含みます。ページ内に広告主から成果報酬を受け取るリンクが含まれます。掲載している統計の数値と計算は、広告とは関係なく公表値にもとづいています。</p>
<blockquote><strong>__LATEST__年の専業主婦世帯の割合は__SHL__%です（専業主婦世帯__LS__万世帯・共働き世帯__LK__万世帯）。</strong>この割合は「専業主婦世帯 ÷（専業主婦世帯＋共働き世帯）」で、どちらも妻が64歳以下・夫が雇用者の世帯に限った数です。全世帯に占める割合ではありません。</blockquote>

<h2 id="shiraberu">年を選ぶ</h2>
<div class="calc" id="calcForm">
  <div class="pick">
    <div><label for="y1">調べたい年</label><select id="y1"></select></div>
    <div><label for="y2">比べる年（任意）</label><select id="y2"></select></div>
  </div>
  <button type="button" class="calc-btn" id="run" style="margin-top:18px">この年の数字を見る</button>
</div>

<div class="result" id="result" aria-live="polite">
  <div class="big"><div class="lbl" id="rLbl"></div><div class="num" id="rNum"></div></div>
  <table class="dt" id="rTable"></table>
  <div id="rCmp"></div>
  <p id="rNote" style="font-size:.8rem;color:#6b7178;margin:14px 0 0;line-height:1.9"></p>
  <div class="bars" id="bars" aria-hidden="true"></div>
  <p style="font-size:.78rem;color:#6b7178;margin:14px 0 0;line-height:1.9">棒は専業主婦世帯の割合（__FIRST__年〜__LATEST__年）。出典は内閣府『男女共同参画白書 令和8年版』特-5図・特-6図（__CHECKED__確認）。割合と倍率は公表された世帯数から当サイトが計算しています。統計は全体の傾向であり、個々の家庭にとってどちらが良いかを示すものではありません。</p>
  <section id="line-cta-result" style="border:1px solid #e3ddd3;background:#f7f5f2;padding:18px 18px 20px;margin:24px 0 0;text-align:center">
    <p style="margin:0 0 6px;font-size:11px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif">NOE OFFICIAL LINE</p>
    <p style="margin:0 0 10px;font-size:16px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5">公表値が更新されたらお知らせします</p>
    <p style="margin:0 0 16px;font-size:13px;color:#5a6068;line-height:1.85">白書・国勢調査・人口動態統計など、このサイトで使っている統計の更新を月1回まとめて配信します。</p>
    <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{gtag('event','line_add_result',{tool:'__SLUG__'});}catch(e){}" style="display:inline-block;background:#7c2e42;color:#ffffff;padding:12px 30px;font-size:14px;font-weight:600;text-decoration:none">友だち追加する</a>
    <p style="margin:10px 0 0;font-size:11px;color:#8a8f95">登録は無料。いつでも解除できます。</p>
  </section>
  <div style="border:1px solid #e3ddd3;border-radius:6px;padding:22px 24px;margin:24px 0 0;background:#faf8f5">
  <p style="font-size:.7rem;color:#999;margin:0 0 6px">PR</p>
  <p style="font-weight:900;margin:0 0 6px;color:#1d242b">数字を見たあとに、手元で変えられること</p>
  <p style="font-size:.86rem;color:#5a6068;margin:0 0 16px;line-height:1.9">共働きでも片働きでも、日々の家事の総量を減らすことは今日から手をつけられます。買い物と献立を考える時間を削るのはその一つです。</p>
  <a href="__OISIX__" id="aff-oisix" rel="nofollow sponsored noopener" target="_blank" style="display:inline-block;background:#7c2e42;color:#fff;font-weight:700;padding:13px 32px;text-decoration:none">Oisixのおためしセットを見る</a>
  <p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">食材宅配サービス。このページの統計とは関係ありません</p>
  </div>
</div>

<h2 id="teigi">この割合が指しているもの</h2>
<p>このツールの割合は、次の式で計算しています。</p>
<p><strong>専業主婦世帯 ÷（専業主婦世帯 ＋ 共働き世帯）</strong></p>
<ul>
<li><strong>専業主婦世帯</strong>：__T_SENGYOU__</li>
<li><strong>共働き世帯</strong>：__T_KYOUDOU__</li>
</ul>
<p>__T_FUKUMANAI__ 分母は「夫が会社などに雇われていて、妻が64歳以下の夫婦」だけなので、「日本の女性の何%が専業主婦か」「全世帯の何%が専業主婦世帯か」という問いの答えにはなりません。その数字はこの系列からは計算できないため、載せていません。</p>

<h2 id="ichiran">5年ごとの早見表</h2>
__FIVE_TABLE__
<p class="srcline">全41年ぶんの表と、50%を下回った年・5年ごとの増減率・フルタイムとパートの内訳は、<a href="/articles/__ART__/">専業主婦の割合｜40年の推移データ</a>にまとめています。</p>

<h2 id="chui">数字を見るときの注意</h2>
<h3>2011年は全国値がありません</h3>
<p>__Y2011__ このツールで2011年を選ぶと、3県を除く値を参考として表示します。</p>
<h3>調査が途中で切り替わっています</h3>
<p>__CHOUSA__</p>
<h3>年代別の割合は出せません</h3>
<p>この系列は妻が64歳以下の世帯をまとめた合計で、30代・40代といった妻の年代別の内訳はありません。当サイトでは年代別の一次データを確認できていないため、掲載していません。</p>

<h2 id="faq">よくある質問（FAQ）</h2>
__FAQHTML__

<h2 id="src">出典</h2>
<p>__SRCINTRO__（__CHECKED__確認）</p>
<ul style="font-size:.86rem;line-height:2">
__SRCLIST__
</ul>

<h2 id="related">関連するツールと記事</h2>
<ul>
<li><a href="/articles/__ART__/">専業主婦の割合｜40年の推移データ</a>｜全41年の表・節目の年・増減率</li>
<li><a href="/articles/tomobataraki-wariai-data/">共働き世帯の割合はどれくらい？</a>｜同じ系列を共働きの側から読む</li>
<li><a href="/articles/sengyoshufu-seikatsuhi/">専業主婦世帯の生活費</a>｜片働きの家計をどう組むか</li>
<li><a href="/articles/tomobataraki-shokuji-data/">共働き夫婦の食事はどうしている？</a>｜自炊・ミールキット・外食の費用と時間</li>
<li><a href="/tools/seikatsuhi-simulator/">ふたりの生活費シミュレーション</a>｜家賃・食費・分担を試算</li>
</ul>
</article>

<!-- LINE-CTA -->
<section id="line-cta" style="max-width:680px;margin:56px auto 64px;padding:36px 28px;background:#f7f5f2;border:1px solid #e3ddd3;text-align:center;">
  <p style="margin:0 0 10px;font-size:12px;letter-spacing:.18em;color:#7c2e42;font-family:Georgia,'Times New Roman',serif;">NOE OFFICIAL LINE</p>
  <p style="margin:0 0 14px;font-size:20px;font-weight:600;color:#1d242b;font-family:'Yu Mincho','游明朝',serif;line-height:1.5;">公表値が更新されたらお知らせします</p>
  <p style="margin:0 0 22px;font-size:14px;color:#5a6068;line-height:1.9;">白書・国勢調査・人口動態統計など、このサイトで使っている統計の更新を月1回まとめて配信します。</p>
  <a href="https://lin.ee/unbDsCR" rel="noopener" onclick="try{gtag('event','line_add_click',{tool:'__SLUG__'});}catch(e){}"
     style="display:inline-block;background:#7c2e42;color:#ffffff;padding:14px 36px;font-size:15px;font-weight:600;text-decoration:none;">友だち追加する</a>
  <p style="margin:14px 0 0;font-size:11px;color:#8a8f95;">登録は無料・配信は月1回だけ。いつでも解除できます。</p>
</section>
</div>
<footer><div class="footer-inner">
<div><a href="/">ホーム</a><a href="/articles/">記事一覧</a><a href="/about.html">運営者情報</a><a href="/privacy-policy.html">プライバシー</a><a href="/disclaimer.html">免責事項</a></div>
<p class="footer-disc">※本ツールの数値は内閣府男女共同参画局『男女共同参画白書 令和8年版』の公表値（__CHECKED__確認）です。割合・倍率は公表された世帯数から当サイトが計算しています。<strong style="color:#cda">【PR】</strong>本サイトはアフィリエイト広告を利用しています。</p>
</div></footer>
<button id="top" onclick="scrollTo({top:0,behavior:'smooth'})">↑</button>
<script>
(function(){
  var DATA=__JSDATA__;
  var LATEST=__LATEST__;
  var by={};DATA.forEach(function(d){by[d.y]=d;});
  function $(id){return document.getElementById(id);}
  function fmt(n){return String(n).replace(/\\B(?=(\\d{3})+(?!\\d))/g,',');}
  var y1=$('y1'),y2=$('y2');
  var o0=document.createElement('option');o0.value='';o0.textContent='選ばない';y2.appendChild(o0);
  for(var i=DATA.length-1;i>=0;i--){
    var a=document.createElement('option');a.value=DATA[i].y;a.textContent=DATA[i].y+'年';y1.appendChild(a);
    var b=document.createElement('option');b.value=DATA[i].y;b.textContent=DATA[i].y+'年';y2.appendChild(b);
  }
  function vals(d){
    if(d.s!==null){return {s:d.s,k:d.k,sh:d.sh,bai:d.bai,ex:false};}
    var sh=Math.round(d.s3*1000/(d.s3+d.k3))/10;
    return {s:d.s3,k:d.k3,sh:sh,bai:Math.round(d.k3*100/d.s3)/100,ex:true};
  }
  function row(th,td){return '<tr><th>'+th+'</th><td>'+td+'</td></tr>';}
  function sign(n,unit){var r=Math.round(n*10)/10;var t=(unit==='ポイント')?r.toFixed(1):fmt(Math.abs(r));if(unit!=='ポイント'){t=(r<0?'-':'')+t;}return (r>0?'+':'')+t+unit;}
  function draw(sel){
    var max=60,h='';
    DATA.forEach(function(d){
      if(d.sh===null){h+='<div class="row'+(d.y==sel?' on':'')+'"><span class="y">'+d.y+'</span><span class="v">全国値なし</span></div>';return;}
      h+='<div class="row'+(d.y==sel?' on':'')+'"><span class="y">'+d.y+'</span><span class="b" style="width:'+(d.sh/max*78).toFixed(1)+'%"></span><span class="v">'+d.sh.toFixed(1)+'%</span></div>';
    });
    $('bars').innerHTML=h;
  }
  function run(){
    var d=by[y1.value],v=vals(d),L=vals(by[LATEST]);
    $('rLbl').textContent=d.y+'年の専業主婦世帯の割合'+(v.ex?'（岩手・宮城・福島を除く参考値）':'');
    $('rNum').textContent=v.sh.toFixed(1)+'%';
    var t=row('専業主婦世帯',fmt(v.s)+'万世帯')+row('共働き世帯',fmt(v.k)+'万世帯')+row('共働き世帯 ÷ 専業主婦世帯',v.bai.toFixed(2)+'倍');
    if(d.f!==null){t+=row('共働きのうち妻フルタイム（週35時間以上）',fmt(d.f)+'万世帯')+row('共働きのうち妻パート（週35時間未満）',fmt(d.p)+'万世帯');}
    if(d.y!=LATEST){t+=row('最新（'+LATEST+'年・'+L.sh.toFixed(1)+'%）との差',sign(L.sh-v.sh,'ポイント'))+row('専業主婦世帯の増減（'+LATEST+'年まで）',sign(L.s-v.s,'万世帯'));}
    $('rTable').innerHTML=t;
    var c='';
    if(y2.value&&y2.value!=y1.value){
      var e=by[y2.value],w=vals(e);
      c='<h3 style="font-size:.96rem;margin:22px 0 0;color:#1d242b">'+d.y+'年と'+e.y+'年を比べる</h3><table class="dt">'
        +row(e.y+'年の専業主婦世帯の割合',w.sh.toFixed(1)+'%'+(w.ex?'（3県を除く参考値）':''))
        +row('割合の差（'+e.y+'年 − '+d.y+'年）',sign(w.sh-v.sh,'ポイント'))
        +row('専業主婦世帯の差',sign(w.s-v.s,'万世帯'))
        +row('共働き世帯の差',sign(w.k-v.k,'万世帯'))+'</table>';
    }
    $('rCmp').innerHTML=c;
    var n=[];
    if(v.ex||(y2.value&&by[y2.value]&&by[y2.value].s===null)){n.push('2011年は全国値が公表されていないため、岩手県・宮城県・福島県を除く値を参考として表示しています。前後の年の全国値とはそのまま比べられません。');}
    if(d.y<=2001||(y2.value&&Number(y2.value)<=2001)){n.push('1985〜2001年は『労働力調査特別調査』（各年2月）、2002年以降は『労働力調査（詳細集計）』で、調査の方法が違います。離れた年どうしの差は目安として見てください。');}
    if(d.y==1985){n.push('1985年は、フルタイムとパートの合計が共働き世帯の総数と一致しません（内訳の合計のほうが少ない）。');}
    $('rNote').textContent=n.join(' ');
    draw(d.y);
    $('result').classList.add('show');
    try{gtag('event','tool_result',{tool:'__SLUG__',year:String(d.y),compare:String(y2.value||'')});}catch(x){}
    try{$('result').scrollIntoView({behavior:'smooth',block:'start'});}catch(x){}
  }
  $('run').addEventListener('click',run);
})();
</script>
</body>
</html>"""


def build_tool():
    desc = ("%d年から%d年までの年を選ぶと、その年の専業主婦世帯数・共働き世帯数・専業主婦世帯の割合・最新年との差が出ます。"
            "%d年は専業主婦世帯%s・共働き世帯%sで、割合は%.1f%%。2つの年を比べることもできます。"
            "内閣府『男女共同参画白書 令和8年版』の公表値を%sに確認。割合の分母（妻64歳以下・夫が雇用者の世帯）も明記しています。"
            % (FIRST, LATEST, LATEST, man(L["sengyou"]), man(L["kyoudou"]), SH_L, CHECKED))
    ogd = "%d年は%.1f%%、%d年は%.1f%%。年を選んで、その年の世帯数と割合を確かめられます。" % (FIRST, SH_F, LATEST, SH_L)
    faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in FAQ_TOOL]}, ensure_ascii=False)
    app_ld = json.dumps({
        "@context": "https://schema.org", "@type": "WebApplication",
        "name": "専業主婦の割合を年別に調べる", "url": TOOL_URL,
        "applicationCategory": "UtilitiesApplication", "operatingSystem": "All",
        "inLanguage": "ja", "description": desc,
        "datePublished": TODAY, "dateModified": TODAY,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
        "publisher": {"@type": "Organization", "name": "Noe結婚設計室",
                      "url": "https://www.noe-match.com/"}}, ensure_ascii=False)
    bc_ld = json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "ホーム", "item": "https://www.noe-match.com/"},
        {"@type": "ListItem", "position": 2, "name": "無料ツール", "item": "https://www.noe-match.com/#tools"},
        {"@type": "ListItem", "position": 3, "name": "専業主婦の割合を年別に調べる"}]}, ensure_ascii=False)
    shell = io.open("tools/hoikuen-tensu-nerima/index.html", encoding="utf-8").read()
    css = shell[shell.find("<style>"):shell.find("</style>") + 8]
    five_rows = [r for r in ALL_ROWS if int(r[0][:4]) % 5 == 0]
    html = TOOL_TPL
    for k, v in (("__TITLE__", TOOL_TITLE), ("__DESC__", desc), ("__OGD__", ogd), ("__URL__", TOOL_URL),
                 ("__H1__", TOOL_H1), ("__CSS__", css), ("__FAQLD__", faq_ld), ("__APPLD__", app_ld),
                 ("__BCLD__", bc_ld), ("__CHECKED__", CHECKED), ("__SLUG__", TOOL_SLUG), ("__ART__", ART_SLUG),
                 ("__OISIX__", OISIX), ("__LATEST__", str(LATEST)), ("__FIRST__", str(FIRST)),
                 ("__SHL__", "%.1f" % SH_L), ("__LS__", "{:,}".format(L["sengyou"])),
                 ("__LK__", "{:,}".format(L["kyoudou"])),
                 ("__T_SENGYOU__", D["teigi"]["sengyou"]), ("__T_KYOUDOU__", D["teigi"]["kyoudou"]),
                 ("__T_FUKUMANAI__", D["teigi"]["fukumanai"]), ("__Y2011__", D["y2011"]),
                 ("__CHOUSA__", D["chousa"]),
                 ("__FIVE_TABLE__", table(["年", "専業主婦世帯", "共働き世帯", "専業主婦世帯の割合", "共働き÷専業主婦"],
                                          five_rows, ["", "n", "n", "n", "n"])),
                 ("__FAQHTML__", faq_html(FAQ_TOOL)), ("__SRCINTRO__", SRC_INTRO.rstrip("。") + "。"),
                 ("__SRCLIST__", "\n".join('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>' % s for s in SRC)),
                 ("__JSDATA__", json.dumps(JS_DATA, ensure_ascii=False, separators=(",", ":")))):
        html = html.replace(k, v)
    assert "__" not in html.replace("__proto__", ""), [m for m in __import__("re").findall(r"__[A-Z0-9_]+__", html)]
    os.makedirs("tools/%s" % TOOL_SLUG, exist_ok=True)
    io.open("tools/%s/index.html" % TOOL_SLUG, "w", encoding="utf-8", newline="\n").write(html)
    print("written: tools/%s/index.html  %d chars  title %d字" % (TOOL_SLUG, len(html), len(TOOL_TITLE)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    os.chdir(os.path.dirname(HERE))
    build_article()
    build_tool()
    print("article title %d字: %s" % (len(ART_TITLE), ART_TITLE))

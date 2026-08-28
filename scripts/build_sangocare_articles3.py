# -*- coding: utf-8 -*-
"""産後ケアのデータ記事（第3弾）を _sangocare_data.py から生成する（2026-08-29 新設）

狙う語は data_gate.py でGO判定だった2語:
  「産後ケア 日帰り」（完全一致10件・頭の語10件）
  「産後ケア 訪問型」（完全一致9件・頭の語10件）

既に出している面は宿泊型・回数・助成・申し込みの4本で、
3類型のうち日帰り型と訪問型だけ受け皿が無かった。追加取得はゼロ。
同じ正本（43自治体の一次確認）から引く。表を手で書かない。

数値はすべて CITIES から計算する。手で書いた数字を混ぜないため、
生成前に集計値を assert で確かめてから書き出す。
"""
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_shell import SRC_INTRO_JICHITAI, faq_html, source_list, table, write
from _sangocare_data import CHECKED, CITIES

TODAY = "2026-08-29"
real = [c for c in CITIES if c["key"] != "kokuhyo"]
N = len(real)

# ---- 集計（すべて正本から計算する） ----------------------------------------
day_yes = [c for c in real if c["day_avail"]]
visit_yes = [c for c in real if c["visit_avail"]]
visit_no = [c["name"] for c in real if not c["visit_avail"]]

day_num = [c for c in real if c["day_prices"]]
day_lab = [c["name"] for c in real if not c["day_prices"]]
visit_num = [c for c in real if c["visit_prices"]]
visit_lab = [c["name"] for c in real if not c["visit_prices"]]

day_first = sorted((c["day_prices"][0], c["name"]) for c in day_num)
visit_first = sorted((c["visit_prices"][0], c["name"]) for c in visit_num)
day_med = int(statistics.median([v for v, _ in day_first]))
visit_med = int(statistics.median([v for v, _ in visit_first]))
day_zero = [n for v, n in day_first if v == 0]
visit_zero = [n for v, n in visit_first if v == 0]
day_max = day_first[-1][0]
day_max_names = [n for v, n in day_first if v == day_max]
visit_max = visit_first[-1][0]
visit_max_names = [n for v, n in visit_first if v == visit_max]

# 回数で単価が変わる自治体
day_step = [(c["name"], c["day_prices"]) for c in day_num if len(c["day_prices"]) > 1]
visit_step = [(c["name"], c["visit_prices"]) for c in visit_num if len(c["visit_prices"]) > 1]

# 日帰りと訪問の両方に自治体としての単価がある自治体で、どちらが安いか
both = [(c["name"], c["day_prices"][0], c["visit_prices"][0])
        for c in real if c["day_prices"] and c["visit_prices"]]
v_cheaper = [b for b in both if b[2] < b[1]]
v_same = [b for b in both if b[2] == b[1]]
v_pricier = [b for b in both if b[2] > b[1]]
gap_top = sorted(both, key=lambda x: x[1] - x[2], reverse=True)[:5]


def _gassan(s):
    return any(k in (s or "") for k in ("合わせ", "合算", "合計", "共通"))


day_gassan = [c["name"] for c in real if _gassan(c["limit_day"])]
visit_gassan = [c["name"] for c in real if _gassan(c["limit_visit"])]

# ---- 検算（合わないなら記事を作らせない） ----------------------------------
assert N == 43, N
assert len(day_yes) == N, "日帰り型を実施していない自治体があるなら本文を直すこと"
assert len(day_num) + len(day_lab) == N
assert len(visit_num) + len(visit_lab) == N
assert len(visit_yes) + len(visit_no) == N
assert len(v_cheaper) + len(v_same) + len(v_pricier) == len(both)
assert visit_med < day_med, "訪問型のほうが安いという本文の前提が崩れている"
assert len(day_step) == 3 and len(v_pricier) == 3, "本文が件数を名指ししているので要確認"

PR_HEAD = "産後ケアを使わない日の負担をどう下げるか"
PR_BODY = ("産後ケアの回数には上限があります。使える日は限られるので、"
           "それ以外の日をどう回すかが実際の問題になります。"
           "買い物と献立を考える時間を削るのはその一つです。")


def yen(v):
    return "{:,}".format(v) + "円"


def join(names, limit=6):
    s = "・".join(names[:limit])
    return s + ("ほか" if len(names) > limit else "")


def src_table():
    return source_list([(c["src"], "%s｜%s" % (c["name"], c["src_label"])) for c in real],
                       intro=SRC_INTRO_JICHITAI)


# ---- 日帰り型 ---------------------------------------------------------------
FAQ_HIGAERI = [
 ("産後ケアの日帰り型はいくらかかりますか？",
  "自治体で違います。%s自治体を確認したところ、自治体として1回（1日）あたりの単価を決めているのは"
  "%d自治体で、その中央値は%sでした。幅は0円（%s）から%s（%s）までです。"
  "残る%d自治体は自治体としての単価を持たず、施設が決めた額との差額や「〜円から〜円」という幅でしか"
  "示されていません。" % (N, len(day_num), yen(day_med), join(day_zero),
                          yen(day_max), join(day_max_names), len(day_lab))),
 ("日帰り型と宿泊型はどちらが安いですか？",
  "1回あたりで見れば日帰り型のほうが安いのが普通ですが、比べるときに注意が要ります。"
  "宿泊型は「1泊2日」の数え方が自治体で3通りに分かれており、1日あたり型の自治体では"
  "1泊2日が2日ぶんとして課金されます。日帰り型は1回いくらで数える自治体が大半なので、"
  "同じ「1回」でも中身が違います。回数の上限が類型ごとに分かれているか合算かでも実際の負担は変わります。"),
 ("日帰り型は何回使えますか？",
  "1回の出産あたりで上限が決まっているのが基本です。注意したいのは、日帰り型だけの枠を持つ自治体と、"
  "宿泊型・訪問型と合算して数える自治体があることです。%s自治体を確認したところ、"
  "日帰り型の上限を他の類型と合わせて数えると明記していたのは%d自治体（%s）でした。"
  "合算枠の自治体では、宿泊型を使い切ると日帰り型が使えなくなります。"
  % (N, len(day_gassan), join(day_gassan, 5))),
 ("日帰り型が無料の自治体はありますか？",
  "%s が自治体としての基本利用料を0円としています。"
  "ただし無料とされていても、食事代やオプションのケア代が別にかかることがあります。"
  "自治体が補助しているのは基本の利用料までという設計が多いためです。" % join(day_zero)),
 ("使う回数で料金が変わることはありますか？",
  "あります。%s の%d自治体は、途中から単価が変わります。"
  "単価に回数を掛けるだけでは実際の負担額になりません。"
  "上限まで使う前提で見積もるときは、この段差を入れて計算してください。"
  % (join([n for n, _ in day_step]), len(day_step))),
 ("比較サイトに載っている日帰り型の金額は信用できますか？",
  "自治体として単価を持たない%d自治体（%s）については、比較表に単価が載っていれば"
  "それは特定の施設の額か、幅の片方だけを取り出した数字です。"
  "この%d自治体では、同じ自治体の中でも使う施設によって自己負担が変わります。"
  % (len(day_lab), join(day_lab, 5), len(day_lab))),
]

RELATED_HIGAERI = """
<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/tools/sangokea-ryokin/">産後ケアの料金はいくら？自治体別の自己負担</a></li>
<li><a href="/articles/sangokea-houmon/">産後ケアの訪問型はいくら？自宅に来てもらう場合の自己負担</a></li>
<li><a href="/articles/sangokea-shukuhaku/">産後ケアの宿泊型はいくら？金額より「数え方」で差がつく</a></li>
<li><a href="/articles/sangokea-nankai/">産後ケアは何回使える？43自治体の上限一覧</a></li>
<li><a href="/articles/sangokea-josei/">産後ケアの助成はいくら？非課税世帯の減免と所得を問わない減額枠</a></li>
</ul>"""


def step_label(v):
    if v[0] < v[-1]:
        return "1〜%d回目 %s ／ %d回目以降 %s" % (len(v) - 1, yen(v[0]), len(v), yen(v[-1]))
    return "1回目 %s ／ 2回目以降 %s" % (yen(v[0]), yen(v[-1]))


def article_higaeri():
    p = []
    p.append(
        "<blockquote><strong>産後ケアの日帰り型は%s自治体すべてが実施していますが、"
        "「1回いくら」を自治体として決めているのは%d自治体だけです。</strong>"
        "残る%d自治体は施設が決めた額との差額や幅でしか示されておらず、"
        "<strong>自治体としての単価が存在しません</strong>。"
        "単価を公表している%d自治体でも0円から%sまで開いています（中央値%s）。"
        "比較表に1つの金額が載っていても、その額で使えるとは限りません。</blockquote>"
        % (N, len(day_num), len(day_lab), len(day_num), yen(day_max), yen(day_med)))

    p.append('<h2 id="souba">日帰り型の相場は1回%s、幅は0円から%s</h2>' % (yen(day_med), yen(day_max)))
    p.append("<p>自治体として1回（1日）あたりの単価を決めているのは%d自治体で、中央値は%sでした。"
             "最も安いのは%sの0円、最も高いのは%sの%sです。"
             "年に数回しか使わない制度なので金額の絶対値は小さく見えますが、"
             "上限まで使うと自治体間で数万円の差になります。</p>"
             % (len(day_num), yen(day_med), join(day_zero), join(day_max_names), yen(day_max)))
    p.append("<p>ここで言う金額は減免前（課税世帯）の額です。非課税世帯・生活保護世帯の減免は"
             "別に用意されている自治体が多く、その中身は"
             '<a href="/articles/sangokea-josei/">産後ケアの助成と減免の一覧</a>にまとめています。</p>')

    p.append('<h2 id="tanka-nashi">%d自治体には「自治体としての単価」が無い</h2>' % len(day_lab))
    p.append("<p>%s の%d自治体は、日帰り型の自己負担を1つの数字で示していません。"
             "示し方は2通りあります。</p>" % (join(day_lab, 12), len(day_lab)))
    p.append("<h3>差額型</h3>")
    p.append("<p>施設が決めた利用料から自治体の負担額を差し引いた残りが自己負担になります。"
             "同じ自治体の中でも、どの施設を使うかで自己負担が変わります。</p>")
    p.append("<h3>幅で示す型</h3>")
    p.append("<p>「3,500〜7,000円」のように施設ごとの幅で公表されています。"
             "幅の下限だけを取り出して比較表に載せると、実際の支払額と一致しません。</p>")
    p.append("<p><strong>この%d自治体では、金額を確定させるには施設まで決める必要があります。</strong>"
             "自治体名だけで金額が出ると書いている比較記事は、この構造を落としています。</p>" % len(day_lab))

    p.append('<h2 id="kaisu">回数で単価が変わる自治体がある</h2>')
    p.append("<p>%d自治体は、使った回数の途中から単価が変わります。</p>" % len(day_step))
    p.append(table(["自治体", "日帰り型の単価の変わり方"],
                   [(n, step_label(v)) for n, v in day_step], ["", ""]))
    p.append("<p><strong>単価に回数を掛けるだけでは実際の負担額になりません。</strong>"
             "上限まで使う前提で見積もるときは、この段差を入れて計算してください。</p>")

    p.append('<h2 id="waku">上限が他の類型と合算される自治体が%d</h2>' % len(day_gassan))
    p.append("<p>日帰り型だけの枠を持つ自治体と、宿泊型・訪問型と合算して数える自治体があります。"
             "%s の%d自治体は、日帰り型の上限を他の類型と合わせて数えると明記していました。</p>"
             % (join(day_gassan, 12), len(day_gassan)))
    p.append("<p>合算枠の自治体では、<strong>宿泊型を先に使うと日帰り型の残りが消えます。</strong>"
             "どの類型から使うかを決めてから申し込む必要があります。</p>")

    p.append('<h2 id="ichiran">%s自治体の日帰り型 料金と上限</h2>' % N)
    p.append("<p>金額は減免前（課税世帯）の額です。各自治体が公表している文言をそのまま載せています。</p>")
    p.append(table(["自治体", "日帰り型の負担額（公表文のまま）", "上限"],
                   [(c["name"], c["day_label"], c["limit_day"]) for c in real], ["", "", ""]))

    p.append('<h2 id="calc">自分の使い方で自己負担を計算する</h2>')
    p.append('<p><a href="/tools/sangokea-ryokin/">産後ケアの料金を自治体別に調べるツール</a>で、'
             '自治体と使う回数を入れると自己負担の合計が出ます。'
             '回数で単価が変わる自治体は段差を持たせて計算しているので、'
             '単価を掛け算するより正確です。単価を持たない自治体は、金額を出さずに公表文をそのまま表示します。</p>')

    p.append(RELATED_HIGAERI)
    p.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    p.append(faq_html(FAQ_HIGAERI))
    p.append(src_table())

    write("sangokea-higaeri",
          "産後ケアの日帰り型はいくら？%s自治体の料金と、単価を持たない%d自治体" % (N, len(day_lab)),
          "産後ケアの日帰り型はいくら？｜%s自治体の料金と単価の有無" % N,
          "産後ケアの日帰り型（デイサービス型）の自己負担を%s自治体で一次確認しました。"
          "自治体として1回あたりの単価を決めているのは%d自治体で中央値%s、幅は0円から%sです。"
          "残る%d自治体は施設との差額や幅でしか示されておらず、自治体としての単価がありません。"
          "回数で単価が変わる自治体、上限が他の類型と合算される%d自治体まで整理しました。確認日は%s。"
          % (N, len(day_num), yen(day_med), yen(day_max), len(day_lab), len(day_gassan), CHECKED),
          "産後ケアの日帰り型は%s自治体すべてが実施。ただし単価を持つのは%d自治体だけです。"
          % (N, len(day_num)),
          FAQ_HIGAERI, "\n".join(p), TODAY, CHECKED, PR_HEAD, PR_BODY)


# ---- 訪問型 -----------------------------------------------------------------
FAQ_HOUMON = [
 ("産後ケアの訪問型（アウトリーチ型）はいくらかかりますか？",
  "%s自治体のうち%d自治体が実施しています。自治体として1回あたりの単価を決めているのは%d自治体で、"
  "中央値は%sでした。幅は0円（%s）から%s（%s）までです。"
  "残る%d自治体は施設・事業者ごとの額との差額や幅でしか示されていません。"
  % (N, len(visit_yes), len(visit_num), yen(visit_med), join(visit_zero),
     yen(visit_max), join(visit_max_names), len(visit_lab))),
 ("訪問型と日帰り型はどちらが安いですか？",
  "訪問型のほうが安いのが多数です。両方に自治体としての単価がある%d自治体で比べると、"
  "訪問型のほうが安いのが%d自治体、同額が%d自治体、訪問型のほうが高いのが%d自治体（%s）でした。"
  "中央値でも訪問型%sに対し日帰り型%sです。"
  "ただし訪問型は1回の時間が短く設定されていることが多いので、単価だけでは比べきれません。"
  % (len(both), len(v_cheaper), len(v_same), len(v_pricier),
     "・".join("%s（日帰り%s→訪問%s）" % (n, yen(d), yen(v)) for n, d, v in v_pricier),
     yen(visit_med), yen(day_med))),
 ("訪問型が無い自治体はありますか？",
  "あります。%s自治体のうち%sは、産後ケア事業としての訪問型（アウトリーチ型）を公式ページに"
  "掲載していませんでした。区内に訪問型・来所型のサービスはありますが、"
  "それは子育て応援券のサービスであって産後ケア事業とは別の制度です。"
  "名前が似ているだけの別制度を、産後ケアの訪問型と取り違えないでください。"
  % (N, join(visit_no))),
 ("訪問型の回数は他の類型と別枠ですか？",
  "自治体によります。%d自治体は、訪問型の上限を他の類型と合わせて数えると明記していました"
  "（%s）。合算枠の自治体では、日帰り型や宿泊型を先に使うと訪問型の残りが消えます。"
  "訪問型は単価が安いので、合算枠の自治体では使う順番で総額が変わります。"
  % (len(visit_gassan), join(visit_gassan, 5))),
 ("訪問型が無料の自治体はありますか？",
  "%s が自治体としての基本利用料を0円としています。"
  "ただし無料でも回数の上限はあり、対象期間も決まっています。" % join(visit_zero)),
 ("訪問型は何をしてもらえますか？",
  "自治体によって想定している中身が違います。助産師による乳房ケアに限定している自治体、"
  "育児相談や体調確認まで含める自治体、事業者の訪問看護ステーションが担う自治体があります。"
  "料金表の名称も「訪問型」「アウトリーチ型」「乳房ケア訪問型」「助産師出張相談」と分かれるため、"
  "自治体のページでは名称ではなく事業の説明文を読んでください。"),
]

RELATED_HOUMON = """
<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/tools/sangokea-ryokin/">産後ケアの料金はいくら？自治体別の自己負担</a></li>
<li><a href="/articles/sangokea-higaeri/">産後ケアの日帰り型はいくら？自治体の単価と施設差額</a></li>
<li><a href="/articles/sangokea-shukuhaku/">産後ケアの宿泊型はいくら？金額より「数え方」で差がつく</a></li>
<li><a href="/articles/sangokea-nankai/">産後ケアは何回使える？43自治体の上限一覧</a></li>
<li><a href="/articles/sangokea-moshikomi/">産後ケアの申し込みはいつから？妊娠中に済ませる手続き</a></li>
</ul>"""


def article_houmon():
    p = []
    p.append(
        "<blockquote><strong>産後ケアの訪問型は、3類型のなかで最も安いのに、"
        "回数の枠が他の類型と共通のことがあります。</strong>"
        "両方に自治体としての単価がある%d自治体で比べると、訪問型のほうが安いのが%d自治体、"
        "中央値でも訪問型%sに対し日帰り型%sでした。"
        "ところが%d自治体は訪問型の上限を他の類型と合算して数えるため、"
        "<strong>宿泊型や日帰り型を先に使うと訪問型の残りが消えます。</strong>"
        "%s自治体のうち%sには、産後ケア事業としての訪問型がありません。</blockquote>"
        % (len(both), len(v_cheaper), yen(visit_med), yen(day_med),
           len(visit_gassan), N, join(visit_no)))

    p.append('<h2 id="souba">訪問型の相場は1回%s</h2>' % yen(visit_med))
    p.append("<p>%s自治体のうち%d自治体が訪問型（アウトリーチ型）を実施しています。"
             "自治体として1回あたりの単価を決めているのは%d自治体で、中央値は%sでした。"
             "最も安いのは%sの0円、最も高いのは%sの%sです。"
             "残る%d自治体（%s）は、事業者ごとの額との差額や幅でしか示されていません。</p>"
             % (N, len(visit_yes), len(visit_num), yen(visit_med), join(visit_zero),
                join(visit_max_names), yen(visit_max), len(visit_lab), join(visit_lab, 12)))

    p.append('<h2 id="hikaku">訪問型のほうが安いが、逆転する自治体が%d</h2>' % len(v_pricier))
    p.append("<p>日帰り型と訪問型の両方に自治体としての単価がある%d自治体で比べました。</p>" % len(both))
    p.append(table(["日帰り型との比較", "自治体数"],
                   [("訪問型のほうが安い", "%d自治体" % len(v_cheaper)),
                    ("同額", "%d自治体（%s）" % (len(v_same), join([n for n, _, _ in v_same]))),
                    ("訪問型のほうが高い", "%d自治体（%s）" % (len(v_pricier),
                     "・".join(n for n, _, _ in v_pricier)))], ["", ""]))
    p.append("<p>差が大きいのは次の自治体です。</p>")
    p.append(table(["自治体", "日帰り型", "訪問型", "差"],
                   [(n, yen(d), yen(v), yen(d - v)) for n, d, v in gap_top],
                   ["", "n", "n", "n"]))
    p.append("<p>ただし<strong>単価だけでは比べきれません。</strong>訪問型は1回の時間が短く設定されている"
             "ことが多く、事業の中身も乳房ケアに限定している自治体があります。"
             "同じ「1回」でも受けられるものが違います。</p>")

    p.append('<h2 id="waku">枠が共通だと、使う順番で総額が変わる</h2>')
    p.append("<p>%d自治体は、訪問型の上限を他の類型と合わせて数えると明記していました。</p>"
             % len(visit_gassan))
    p.append(table(["自治体", "訪問型の上限（公表文のまま）"],
                   [(c["name"], c["limit_visit"]) for c in real if _gassan(c["limit_visit"])],
                   ["", ""]))
    p.append("<p>この型の自治体では、単価の高い宿泊型や日帰り型から使うと、"
             "安い訪問型の枠が先に消えます。逆に訪問型から使えば同じ回数でも自己負担は下がりますが、"
             "訪問型で足りるかは産後の状態によります。"
             "<strong>先に決めるべきは金額ではなく、どの類型を何回使うかの割り振りです。</strong></p>")

    p.append('<h2 id="nashi">訪問型が無い自治体もある</h2>')
    p.append("<p>%sは、産後ケア事業としての訪問型（アウトリーチ型）を公式ページに掲載していませんでした。"
             "区内に「訪問型・来所型産後ケアサービス」という名称のサービスはありますが、"
             "これは子育て応援券のサービスで、産後ケア事業とは別の制度です。</p>" % join(visit_no))
    p.append("<p><strong>名称が似ているだけの別制度を産後ケアの訪問型と取り違えると、"
             "使える回数も自己負担も変わります。</strong>"
             "自治体のページでは名称ではなく、根拠となる事業の説明文を確認してください。</p>")

    p.append('<h2 id="ichiran">%s自治体の訪問型 料金と上限</h2>' % N)
    p.append("<p>金額は減免前（課税世帯）の額です。各自治体が公表している文言をそのまま載せています。</p>")
    p.append(table(["自治体", "訪問型の負担額（公表文のまま）", "上限"],
                   [(c["name"], c["visit_label"], c["limit_visit"]) for c in real], ["", "", ""]))

    p.append('<h2 id="calc">自分の使い方で自己負担を計算する</h2>')
    p.append('<p><a href="/tools/sangokea-ryokin/">産後ケアの料金を自治体別に調べるツール</a>で、'
             '自治体と類型ごとの回数を入れると自己負担の合計が出ます。'
             '上限が合算の自治体は公表文をそのまま表示するので、割り振りを決める材料になります。</p>')

    p.append(RELATED_HOUMON)
    p.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    p.append(faq_html(FAQ_HOUMON))
    p.append(src_table())

    write("sangokea-houmon",
          "産後ケアの訪問型はいくら？%s自治体の料金と、枠が共通で先に消える%d自治体"
          % (N, len(visit_gassan)),
          "産後ケアの訪問型はいくら？｜%s自治体の料金と回数の枠" % N,
          "産後ケアの訪問型（アウトリーチ型）の自己負担を%s自治体で一次確認しました。"
          "自治体として単価を決めているのは%d自治体で中央値%s、日帰り型（中央値%s）より安いのが%d自治体です。"
          "ただし%d自治体は上限を他の類型と合算するため、先に宿泊型や日帰り型を使うと枠が消えます。"
          "訪問型そのものが無い自治体もあります。確認日は%s。"
          % (N, len(visit_num), yen(visit_med), yen(day_med), len(v_cheaper),
             len(visit_gassan), CHECKED),
          "産後ケアの訪問型は3類型で最も安い（中央値%s）が、%d自治体は枠が他の類型と共通です。"
          % (yen(visit_med), len(visit_gassan)),
          FAQ_HOUMON, "\n".join(p), TODAY, CHECKED, PR_HEAD, PR_BODY)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("日帰り: 単価あり%d / 単価なし%d / 中央値%s / 上限%s"
          % (len(day_num), len(day_lab), yen(day_med), yen(day_max)))
    print("訪問  : 実施%d / 単価あり%d / 単価なし%d / 中央値%s / 未実施%s"
          % (len(visit_yes), len(visit_num), len(visit_lab), yen(visit_med), join(visit_no)))
    print("両方数値%d: 訪問が安い%d・同額%d・訪問が高い%d"
          % (len(both), len(v_cheaper), len(v_same), len(v_pricier)))
    print("合算枠: 日帰り%d / 訪問%d" % (len(day_gassan), len(visit_gassan)))
    article_higaeri()
    article_houmon()

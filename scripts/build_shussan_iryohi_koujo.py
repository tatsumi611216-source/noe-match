# -*- coding: utf-8 -*-
"""出産費用の医療費控除のデータ記事を生成する（2026-08-31 新設）

狙う語は data_gate.py でGO判定だった「出産費用 医療費控除」（一致10・頭「出産費用」10）。
サイト内に「医療費控除」の記載は0件で、受け皿が無い。

資産#4（scripts/data/shussan_hiyou.json＝厚労省の実額）と、
今回新設した scripts/data/iryohi_koujo.json（国税庁の法令ルール）を掛け合わせる。
表の数値はすべて正本から計算しており、手で書いた数字は無い。

検算（assert）:
  1. 費目別内訳の非除外5項目の合計 ＝ 出産費用
  2. 費目別内訳の全項目の合計 ＝ 妊婦合計負担額
  3. 都道府県は47件で、妊婦合計負担額 ≧ 出産費用（室料差額等を含むので必ず上回る）
数字の取り違えが起きたら記事を作らせない。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_shell import faq_html, source_list, table, write

TODAY = "2026-08-31"
CHECKED = "2026年8月31日"
HERE = os.path.dirname(os.path.abspath(__file__))

D = json.load(io.open(os.path.join(HERE, "data", "shussan_hiyou.json"), encoding="utf-8"))
K = json.load(io.open(os.path.join(HERE, "data", "iryohi_koujo.json"), encoding="utf-8"))

HEIKIN = D["zenkoku_heikin"]["value"]              # 出産費用（室料差額等を除く）
GOUKEI = D["zenkoku_ninpu_goukei_futangaku"]["value"]  # 妊婦合計負担額（実費の総額）
ICHIJI = D["ichijikin"]["value"]                   # 出産育児一時金 原則50万円
KIJUN = 100000                                     # 医療費控除の基準額（総所得200万円以上）

SLUG = "shussan-iryohi-koujo"

PR_HEAD = "確定申告の前に、日々の家計のほうを軽くしておく"
PR_BODY = ("医療費控除で戻る額は制度で決まっていて、こちらで動かせる余地はほとんどありません。"
           "一方で、産後にいちばん効いてくるのは日々の家事の総量です。"
           "買い物と献立を考える時間を先に削っておくと、退院後の立ち上がりが変わります。")


def yen(n):
    return "{:,}円".format(n)


def yen_signed(n):
    """マイナスは▲で出す。控除の話で符号を落とすと意味が反転する。"""
    if n < 0:
        return "▲{:,}円".format(-n)
    return "{:,}円".format(n)


# --------------------------------------------------------------- 検算
items = D["hiwake_hitori_atari"]["items"]
detail = [i for i in items if not i["komoku"].startswith(("妊婦合計負担額", "出産費用"))]
naka = sum(i["value"] for i in detail if not i.get("jogai"))
soto = sum(i["value"] for i in detail if i.get("jogai"))
row_goukei = [i for i in items if i["komoku"].startswith("妊婦合計負担額")][0]["value"]
row_hiyou = [i for i in items if i["komoku"].startswith("出産費用")][0]["value"]
assert naka == row_hiyou, (naka, row_hiyou)
assert naka + soto == row_goukei, (naka + soto, row_goukei)

PREF = D["todofuken"]
assert len(PREF) == 47, len(PREF)
for p in PREF:
    assert p["ninpu_goukei_futangaku_r6"] >= p["value"], p["name"]

# --------------------------------------------------------------- 集計
ZAN_HEIKIN = HEIKIN - ICHIJI          # 出産費用ベースの残り
ZAN_GOUKEI = GOUKEI - ICHIJI          # 妊婦合計負担額ベースの残り

rows = []
for p in PREF:
    rows.append({
        "name": p["name"],
        "hiyou": p["value"],
        "goukei": p["ninpu_goukei_futangaku_r6"],
        "zan": p["ninpu_goukei_futangaku_r6"] - ICHIJI,
        "zan_hiyou": p["value"] - ICHIJI,
    })
rows.sort(key=lambda r: -r["zan"])

koeru = [r for r in rows if r["zan"] > KIJUN]                  # 妊婦合計負担額ベースで10万円超
koeru_hiyou = [r for r in rows if r["zan_hiyou"] > KIJUN]      # 出産費用ベースで10万円超
mainasu = [r for r in rows if r["zan"] <= 0]                   # 一時金で足りる
mainasu_hiyou = [r for r in rows if r["zan_hiyou"] <= 0]

N_KOERU = len(koeru)
N_KOERU_HIYOU = len(koeru_hiyou)
N_MAINASU = len(mainasu)
N_MAINASU_HIYOU = len(mainasu_hiyou)

KOERU_NAMES = "・".join(r["name"] for r in koeru)
MAINASU_NAMES = "・".join(r["name"] for r in mainasu)
TOP, BOTTOM = rows[0], rows[-1]

pref_rows = [(r["name"], yen(r["hiyou"]), yen(r["goukei"]),
              yen_signed(r["zan"]), yen_signed(r["zan_hiyou"]))
             for r in rows]

KEN = K["keisan"]
SHU = K["shussan"]
IPP = K["ippan"]

# --------------------------------------------------------------- 本文
parts = []

parts.append(
    "<blockquote><strong>「出産したら医療費控除で戻ってくる」は、出産費用だけで見ると"
    "ほとんどの都道府県で成立しません。</strong>"
    "医療費控除は、支払った医療費から出産育児一時金などの補てん額を引き、さらに10万円を引いた残りが対象です。"
    "実際に請求される額（妊婦合計負担額）の全国平均は%sで、一時金%sを引くと%s。"
    "10万円の基準に%s足りません。"
    "都道府県別に見ても、一時金を引いて10万円を超えるのは<strong>%d都県だけ</strong>（%s）で、"
    "%d県は一時金のほうが大きく残りが出ません。"
    "出産費用そのものではなく、<strong>妊婦健診の自己負担・通院交通費・家族の医療費を合算して</strong>"
    "初めて届く、というのが実態に近い形です。</blockquote>"
    % (yen(GOUKEI), yen(ICHIJI), yen(ZAN_GOUKEI), yen(KIJUN - ZAN_GOUKEI),
       N_KOERU, KOERU_NAMES, N_MAINASU))

parts.append('<h2 id="shiki">計算式：引くものが2段階ある</h2>')
parts.append("<p>国税庁の定める医療費控除額の計算式は次のとおりです。</p>")
parts.append(table(["項目", "内容"],
                   [("計算式", KEN["shiki"]),
                    ("（1）", KEN["kingaku1"]),
                    ("（2）", KEN["kingaku2"]),
                    ("控除額の上限", KEN["jougen_gensen"])],
                   ["", ""]))
parts.append('<p class="srcline">%s 出典：<a href="%s" rel="noopener" target="_blank">%s</a>（%s確認）</p>'
             % (KEN["as_of"], KEN["src"], KEN["src_label"], CHECKED))
parts.append("<p>出産の場合、（1）に入るのが<strong>出産育児一時金</strong>です。"
             "国税庁は出産費用の具体例のページでも「%s」と明記しています。"
             "つまり50万円を先に引いてから、さらに10万円を引くことになります。</p>"
             % SHU["taishougai"][3])

parts.append('<h2 id="zenkoku">全国平均で計算すると、10万円に届かない</h2>')
parts.append("<p>厚生労働省が公表している出産費用には2つの数字があります。"
             "「出産費用」は室料差額・産科医療補償制度の掛金・その他（文書料やお祝い膳など）を"
             "<strong>除いた</strong>額、「妊婦合計負担額」がそれらを<strong>含む</strong>"
             "＝実際に請求される総額です。両方で計算すると次のようになります。</p>")
parts.append(table(["基準にする額", "全国平均", "一時金50万円を引いた残り", "10万円の基準に対して"],
                   [("出産費用（室料差額等を除く）", yen(HEIKIN), yen_signed(ZAN_HEIKIN),
                     "%s不足" % yen(KIJUN - ZAN_HEIKIN)),
                    ("妊婦合計負担額（実際に請求される額）", yen(GOUKEI), yen_signed(ZAN_GOUKEI),
                     "%s不足" % yen(KIJUN - ZAN_GOUKEI))],
                   ["", "n", "n", ""]))
parts.append('<p class="srcline">出産費用・妊婦合計負担額は%s。出典：'
             '<a href="%s" rel="noopener" target="_blank">%s</a></p>'
             % (D["zenkoku_heikin"]["as_of"], D["zenkoku_heikin"]["src"],
                D["zenkoku_heikin"]["src_label"]))
parts.append("<p>どちらで見ても、出産費用だけでは全国平均で10万円に届きません。"
             "「出産＝医療費控除」と説明している記事は多いのですが、"
             "その根拠として出産費用の平均額だけを挙げているものは、一時金を引いていないか、"
             "引いたあとに10万円を引くことを書いていないかのどちらかです。</p>")

parts.append('<h2 id="pref">都道府県別：一時金を引いた残りはいくらか</h2>')
parts.append("<p>最も残るのは%s（%s）、最も少ないのは%s（%s）です。"
             "妊婦合計負担額ベースで10万円を超えるのは%d都県（%s）、"
             "一時金のほうが大きく残りが出ないのが%d県（%s）でした。"
             "室料差額等を除いた「出産費用」で見ると、10万円を超えるのは%s%d件だけになります。</p>"
             % (TOP["name"], yen_signed(TOP["zan"]), BOTTOM["name"], yen_signed(BOTTOM["zan"]),
                N_KOERU, KOERU_NAMES, N_MAINASU, MAINASU_NAMES,
                "・".join(r["name"] for r in koeru_hiyou), N_KOERU_HIYOU))
parts.append(table(["都道府県", "出産費用", "妊婦合計負担額",
                    "一時金を引いた残り（合計負担額ベース）", "同（出産費用ベース）"],
                   pref_rows, ["", "n", "n", "n", "n"]))
parts.append('<p class="srcline">令和6年度（令和6年4月～令和7年3月請求分）・正常分娩・全施設の平均。'
             '一時金は原則%sで計算。▲は一時金のほうが大きい（残りが出ない）ことを示します。'
             '出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>'
             % (yen(ICHIJI), D["zenkoku_heikin"]["src"], D["zenkoku_heikin"]["src_label"]))

parts.append('<h2 id="hikikirenai">残りがマイナスでも、他の医療費から引く必要はない</h2>')
parts.append("<p>%sのように一時金のほうが大きい場合、"
             "「余った分を家族の他の医療費から引かないといけないのか」が問題になります。"
             "国税庁は次のように定めています。</p>" % rows[-1]["name"])
parts.append("<blockquote>%s</blockquote>" % KEN["hoten_gensoku"])
parts.append("<p>つまり出産育児一時金は出産費用からしか引きません。"
             "同じ年に家族が支払った歯科治療費や入院費が別にあるなら、そちらは満額のまま合算できます。"
             "ここを誤解して「一時金が出たから今年は医療費控除を諦めた」となるのが、"
             "この制度でいちばん損をしやすいところです。</p>")

parts.append('<h2 id="taishou">出産まわりで対象になるもの・ならないもの</h2>')
parts.append("<p>国税庁が出産費用の具体例として挙げているものは次のとおりです（原文）。</p>")
parts.append("<h3>対象になるもの</h3>")
parts.append("<ul>%s</ul>" % "".join("<li>%s</li>" % t for t in SHU["taishou"]))
parts.append("<h3>対象にならないもの</h3>")
parts.append("<ul>%s</ul>" % "".join("<li>%s</li>" % t for t in SHU["taishougai"]))
parts.append('<p class="srcline">%s／根拠法令 %s 出典：'
             '<a href="%s" rel="noopener" target="_blank">%s</a></p>'
             % (SHU["as_of"], SHU["konkyo"], SHU["src"], SHU["src_label"]))
parts.append("<p>見落とされやすいのが1つめの<strong>「妊娠と診断されてからの定期検診や検査などの費用、"
             "また、通院費用」</strong>です。妊婦健診は出産費用とは別枠で、"
             "市町村の公費助成の対象になっています（妊婦1人あたりの公費負担額は全国平均11.4万円・"
             "最低8.6万円～最高14.1万円、令和7年4月時点）。"
             "助成で賄われた分は自己負担ではないので控除の対象になりませんが、"
             "助成券を超えた自己負担分と通院の交通費は対象です。"
             "出産費用だけで10万円に届かない以上、実際に控除を使えるかどうかは"
             "この積み上げで決まります。</p>")

parts.append('<h2 id="chui">計算するときに間違えやすいところ</h2>')
parts.append("<h3>「出産費用の平均」をそのまま使わない</h3>")
parts.append("<p>ニュースやまとめ記事で「平均約50万円」とされているのは室料差額等を除いた"
             "「出産費用」です。実際に請求されるのは「妊婦合計負担額」で、"
             "令和6年度の全国平均で%s多くなります。"
             "どちらの数字を使うかで、一時金を引いた残りは%sから%sまで変わります。</p>"
             % (yen(GOUKEI - HEIKIN), yen_signed(ZAN_HEIKIN), yen_signed(ZAN_GOUKEI)))
parts.append("<h3>室料差額を入れてよいかは、国税庁のページに書かれていない</h3>")
parts.append("<p>%s"
             "個室を選んだ場合の差額をどう扱うかは、税務署または税理士に確認してください。"
             "本記事の表で2つの基準を並べているのはこのためです。</p>" % K["mikakunin"][0])
parts.append("<h3>10万円は固定ではない</h3>")
parts.append("<p>差し引くのは「%s」です。"
             "産休・育休で所得が下がった年は、この5％のほうが適用されて基準が10万円より低くなることがあります。"
             "共働きで夫婦のどちらで申告するかを考えるときは、"
             "税率の高いほうにまとめるのが一般的とされますが、"
             "所得が200万円未満の側で申告したほうが基準が下がって有利になる場合もあります。</p>"
             % KEN["kingaku2"])
parts.append("<h3>帝王切開は別の補てんが入る</h3>")
parts.append("<p>%s"
             "高額療養費で払い戻された分も「保険金などで補てんされる金額」にあたるため、"
             "医療費から差し引く必要があります。</p>" % D["teiousekkai_mutsuu"]["kougakuryouyou"])

parts.append('<h2 id="calc">自分の場合の出産費用を調べる</h2>')
parts.append("<p>控除額の計算に使う実額は、住んでいる地域と施設で変わります。"
             "都道府県別・施設種別・費目別の平均は"
             '<a href="/articles/shussan-hiyou-data/">出産費用の平均</a>にまとめています。'
             "一時金の額と受け取り方（直接支払制度・受取代理・償還払い）は"
             '<a href="/articles/shussan-ichijikin-data/">出産育児一時金</a>を参照してください。'
             "償還払いを選んだ場合は窓口でいったん全額を支払うため、"
             "領収書がそのまま医療費控除の資料になります。</p>")

parts.append("""
<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/articles/shussan-hiyou-data/">出産費用の平均はいくら？都道府県別・費目別の実額</a></li>
<li><a href="/articles/shussan-ichijikin-data/">出産育児一時金は50万円のまま？内訳・改定の履歴・現物給付化の法改正</a></li>
<li><a href="/articles/shussan-mushouka/">出産費用の無償化はいつから？決まったことと決まっていないこと</a></li>
<li><a href="/articles/ikukyu-kyufukin-data/">育児休業給付金はいくら？賃金月額別の実効額と上限</a></li>
<li><a href="/articles/sangokea-josei/">産後ケアの助成はいくら？非課税世帯の減免と所得を問わない減額枠</a></li>
<li><a href="/tools/sangokea-ryokin/">産後ケアの料金はいくら？自治体別の自己負担</a></li>
</ul>""")

FAQ = [
 ("出産費用は医療費控除の対象になりますか？",
  "対象になります。ただし出産育児一時金など補てんされた金額を先に差し引き、"
  "さらに10万円（総所得金額等が200万円未満の人は総所得金額等の5％）を引いた残りが控除額です。"
  "令和6年度の全国平均で計算すると、実際に請求される額（妊婦合計負担額）%sから一時金%sを引いて%sとなり、"
  "10万円の基準に%s足りません。妊婦健診の自己負担・通院交通費・家族の医療費を合算して初めて届く形になります。"
  % (yen(GOUKEI), yen(ICHIJI), yen(ZAN_GOUKEI), yen(KIJUN - ZAN_GOUKEI))),
 ("出産育児一時金は医療費から引かないといけませんか？",
  "引きます。国税庁は「%s」と明記しています。"
  "ただし引くのは出産費用からだけです。「%s」と定められているため、"
  "一時金が出産費用を上回っても、その差額を家族の他の医療費から引く必要はありません。"
  % (SHU["taishougai"][3], KEN["hoten_gensoku"])),
 ("どの都道府県なら医療費控除が使えますか？",
  "妊婦合計負担額の平均から一時金50万円を引いて10万円を超えるのは%d都県（%s）です。"
  "残りが出ないのは%d県（%s）でした。ただしこれは平均値の比較で、"
  "実際には施設や分娩の内容で大きく変わります。また出産費用以外の医療費を合算できるので、"
  "この表で下位でも控除が使えないという意味ではありません。"
  % (N_KOERU, KOERU_NAMES, N_MAINASU, MAINASU_NAMES)),
 ("妊婦健診の費用は医療費控除の対象ですか？",
  "国税庁は対象の具体例として「%s」を挙げています。"
  "ただし妊婦健診は市町村の公費助成の対象で、助成で賄われた分は自己負担ではないため控除の対象になりません。"
  "助成券を超えて自分で支払った分と、通院にかかった交通費が対象です。"
  % SHU["taishou"][0]),
 ("入院中の食事代やタクシー代も対象になりますか？",
  "国税庁は「%s」と「%s」を対象として挙げています。"
  "一方で「%s」と「%s」は対象外です。同じ食事代でも、病院に支払う入院中のものか、"
  "出前や外食かで扱いが分かれます。"
  % (SHU["taishou"][2], SHU["taishou"][1], SHU["taishougai"][0], SHU["taishougai"][1])),
 ("差額ベッド代（室料差額）は含めてよいですか？",
  "国税庁のタックスアンサーNo.1122・No.1124のいずれにも明示がありません。"
  "No.1122は「%s」を対象として挙げつつ、全体に「%s」という条件をかけています。"
  "本記事では断定を避け、室料差額を含む額（妊婦合計負担額）と含まない額（出産費用）の"
  "両方で計算した表を載せています。判断は税務署または税理士にご確認ください。"
  % (IPP["nyuuin"], IPP["suijun"])),
 ("夫婦のどちらで申告するのが得ですか？",
  "医療費控除は生計を一にする家族の分をまとめて1人が申告できます。"
  "一般には税率の高いほうにまとめると還付額が大きくなりますが、"
  "差し引く基準額が「%s」であるため、"
  "産休・育休で所得が下がった側で申告したほうが基準が下がって有利になる場合もあります。"
  "還付額は課税所得によって変わるので、両方で試算して比べてください。"
  % KEN["kingaku2"]),
]

parts.append('<h2 id="faq">よくある質問（FAQ）</h2>')
parts.append(faq_html(FAQ))

SOURCES = [
    (KEN["src"], KEN["src_label"]),
    (SHU["src"], SHU["src_label"]),
    (IPP["src"], IPP["src_label"]),
    (D["zenkoku_heikin"]["src"], D["zenkoku_heikin"]["src_label"]),
    (D["fukumu_fukumanai"]["src"], D["fukumu_fukumanai"]["src_label"]),
]
parts.append(source_list(
    SOURCES,
    "本記事は、医療費控除のルール（国税庁タックスアンサー）と、"
    "出産費用の実額（厚生労働省の公表値）という別々の一次情報を突き合わせたものです。"
    "税額の判断は個別の事情で変わるため、実際の申告にあたっては税務署または税理士にご確認ください。"))

write(SLUG,
      "出産費用の医療費控除はいくら？一時金50万円を引くと10万円を超えるのは%d都県だけ" % N_KOERU,
      "出産費用の医療費控除はいくら？｜一時金を引くと全国平均は%s" % yen(ZAN_GOUKEI),
      "出産費用の医療費控除は、出産育児一時金%sを差し引いてから10万円を引いた残りが対象です。"
      "実際に請求される妊婦合計負担額の全国平均%sで計算すると残りは%sで、基準に%s足りません。"
      "都道府県別47件で一時金を引いた残りを計算すると、10万円を超えるのは%d都県だけでした。"
      "対象になる費用・ならない費用は国税庁の原文で、実額は厚労省の公表値で整理しています。確認日は%s。"
      % (yen(ICHIJI), yen(GOUKEI), yen(ZAN_GOUKEI), yen(KIJUN - ZAN_GOUKEI), N_KOERU, CHECKED),
      "出産費用から一時金50万円を引いた全国平均は%s。10万円の基準に届きません。" % yen(ZAN_GOUKEI),
      FAQ, "\n".join(parts), TODAY, CHECKED, PR_HEAD, PR_BODY)

print("koeru=%d %s" % (N_KOERU, KOERU_NAMES))
print("koeru(hiyou base)=%d" % N_KOERU_HIYOU)
print("mainasu=%d %s" % (N_MAINASU, MAINASU_NAMES))
print("zan zenkoku: hiyou=%d goukei=%d" % (ZAN_HEIKIN, ZAN_GOUKEI))

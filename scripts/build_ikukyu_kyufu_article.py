# -*- coding: utf-8 -*-
"""育児休業給付金のデータ記事を生成する（2026-08-27 新設）

狙う語は data_gate.py でGO判定だった「育児休業給付金 いくら」（サジェスト4件）。
既存ページで本文に「育児休業給付金」を含むのは /tools/ikukyu-encho-hantei/ だけで、
記事側の受け皿が無い。

数値は scripts/data/ikukyu_rules.json（雇用保険法・厚労省資料の実査）から引く。
表は手で書かず、すべて正本から計算する。
"""
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_shell import faq_html, source_list, table, write

TODAY = "2026-08-27"
CHECKED = "2026年8月27日"
D = json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "data", "ikukyu_rules.json"), encoding="utf-8"))

K = D["kyufu_rate"]
LIM = K["limits_r8"]
REL = K["related_benefits"]

PR_HEAD = "育休に入る前に、家事の総量のほうを減らしておく"
PR_BODY = ("給付金の額は法律で決まっていて、こちらで動かせる余地はほとんどありません。"
           "一方で休業中にいちばん効いてくるのは、毎日の買い物と献立を考える時間です。"
           "そこを先に削っておくと、復帰前後の負担がかなり変わります。")


def yen(n):
    return "{:,}円".format(n)


def num(s):
    """『332,454円（改定前 323,811円）』→ (332454, 323811)。
    形式が崩れていたら落とす（黙って別の数字を拾わせない）。"""
    m = re.match(r"^([\d,]+)円（改定前\s*([\d,]+)円）$", s.strip())
    if not m:
        raise ValueError("上限額の書式が想定外: %r" % s)
    return int(m.group(1).replace(",", "")), int(m.group(2).replace(",", ""))


JOGEN_67, JOGEN_67_OLD = num(LIM["ikuji_kyugyo_kyufukin_shikyu_jogen_67"])
JOGEN_50, JOGEN_50_OLD = num(LIM["ikuji_kyugyo_kyufukin_shikyu_jogen_50"])
CHINGIN_JOGEN, CHINGIN_JOGEN_OLD = num(LIM["kyugyo_kaishiji_chingin_getsugaku_jogen"])
CHINGIN_KAGEN, CHINGIN_KAGEN_OLD = num(LIM["kyugyo_kaishiji_chingin_getsugaku_kagen"])

# 正本どうしの整合を確かめる。支給上限額＝賃金月額上限×支給率のはずなので、
# ここがずれたら数値の取り違えなので記事を作らせない。
assert round(CHINGIN_JOGEN * 0.67) == JOGEN_67, (CHINGIN_JOGEN, JOGEN_67)
assert round(CHINGIN_JOGEN * 0.50) == JOGEN_50, (CHINGIN_JOGEN, JOGEN_50)

# 横断表に載せる他給付の上限額も、正本の文字列から取り出す（手で書かない）
SHUSSEIJI_JOGEN = int(re.search(r"支給上限額\s*([\d,]+)円",
                                REL["shussei_ji_ikuji_kyugyo_kyufukin"]).group(1).replace(",", ""))
SHUSSEIGO_JOGEN = int(re.search(r"支給上限額\s*([\d,]+)円",
                                REL["shussei_go_kyugyo_shien_kyufukin"]).group(1).replace(",", ""))
JITAN_GENDO = int(re.search(r"支給限度額\s*([\d,]+)円",
                            REL["ikuji_jitan_shugyo_kyufukin"]).group(1).replace(",", ""))


def shikyu(getsugaku, rate):
    """支給単位期間（30日）あたりの給付額。
    休業開始時賃金が上限超（下限未満）なら、その額ではなく上限（下限）で算定する。"""
    base = min(max(getsugaku, CHINGIN_KAGEN), CHINGIN_JOGEN)
    return int(base / 30.0 * 30 * rate)


def build():
    slug = "ikukyu-kyufukin-data"

    # --- 賃金月額別の実効額（上限があるので率は一定ではない） ---
    samples = [200000, 250000, 300000, 350000, 400000, 450000,
               CHINGIN_JOGEN, 550000, 600000]
    rate_rows = []
    for g in samples:
        a, b = shikyu(g, 0.67), shikyu(g, 0.50)
        mark = "上限に到達" if g >= CHINGIN_JOGEN else "—"
        rate_rows.append((yen(g) + ("（賃金月額の上限）" if g == CHINGIN_JOGEN else ""),
                          yen(a), "%.1f%%" % (a * 100.0 / g),
                          yen(b), "%.1f%%" % (b * 100.0 / g), mark))

    # --- 令和8年8月1日改定 ---
    kaitei_rows = [
        ("育児休業給付金の支給上限額（支給率67％のとき）", yen(JOGEN_67_OLD), yen(JOGEN_67)),
        ("育児休業給付金の支給上限額（支給率50％のとき）", yen(JOGEN_50_OLD), yen(JOGEN_50)),
        ("休業開始時賃金月額の上限額", yen(CHINGIN_JOGEN_OLD), yen(CHINGIN_JOGEN)),
        ("休業開始時賃金月額の下限額", yen(CHINGIN_KAGEN_OLD), yen(CHINGIN_KAGEN)),
    ]

    # --- 給付の種類を横断で並べる ---
    kind_rows = [
        ("育児休業給付金（休業開始から通算180日まで）", "67％", yen(JOGEN_67),
         "雇用保険法第61条の7"),
        ("育児休業給付金（181日目以降・延長期間を含む）", "50％", yen(JOGEN_50),
         "雇用保険法第61条の7第6項"),
        ("出生時育児休業給付金（産後パパ育休）", "67％", yen(SHUSSEIJI_JOGEN),
         "雇用保険法第61条の8"),
        ("出生後休業支援給付金（上限28日）", "13％", yen(SHUSSEIGO_JOGEN),
         "雇用保険法第61条の10"),
        ("育児時短就業給付金（支給限度額）", "—", yen(JITAN_GENDO),
         "雇用保険法第61条の12"),
    ]

    parts = []
    parts.append(
        "<blockquote><strong>「育休は給料の67％」と紹介されることが多いのですが、67％なのは"
        "休業開始から通算180日までです。</strong>181日目からは50％に下がります（雇用保険法第61条の7第6項）。"
        "さらに支給には上限があり、休業開始時の賃金月額が%sを超える人は、実際の支給率が67％より低くなります。"
        "1歳〜1歳6か月、1歳6か月〜2歳の延長期間は、その時点でほぼ必ず180日を超えているため"
        "<strong>延長中は50％</strong>です。延長したから率が変わるのではなく、日数で変わります。</blockquote>"
        % yen(CHINGIN_JOGEN))

    parts.append('<h2 id="keisan">計算式と、67％が適用される範囲</h2>')
    parts.append("<p>%s</p>" % K["rule"])
    parts.append("<p>支給日数は%sです。</p>" % K["shikyu_nissu"])
    parts.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">'
                 'e-Gov法令検索 雇用保険法（昭和四十九年法律第百十六号）</a>（%s確認）</p>'
                 % (K["src"], CHECKED))

    parts.append('<h2 id="jogen">賃金月額別の支給額（支給単位期間30日あたり）</h2>')
    parts.append("<p>休業開始時の賃金月額が上限額%sを超える場合は、実際の賃金ではなく上限額を使って"
                 "計算します（下限額%sを下回る場合は下限額を使います）。そのため賃金が高いほど、"
                 "額面に対する実際の支給率は67％・50％より下がります。下の表は、"
                 "この規定にしたがって支給単位期間（30日）あたりの額を計算したものです。</p>"
                 % (yen(CHINGIN_JOGEN), yen(CHINGIN_KAGEN)))
    parts.append(table(["休業開始時の賃金月額", "180日まで（67％）", "額面に対する実効率",
                        "181日目以降（50％）", "額面に対する実効率", "備考"],
                       rate_rows, ["", "n", "n", "n", "n", ""]))
    parts.append("<p>%s</p>" % LIM["note"])
    parts.append("<p>なお、ここでいう「賃金月額」は休業開始前6か月の賃金をもとに算定される"
                 "休業開始時賃金日額の30日分であり、いわゆる手取りではありません。"
                 "育児休業給付金には所得税がかからず、休業中は社会保険料も免除されるため、"
                 "手取りとの比較では額面の率より目減りが小さくなります。</p>")

    parts.append('<h2 id="kaitei">令和8年8月1日の改定（毎年8月に変わる）</h2>')
    parts.append("<p>上限額と下限額は、毎月勤労統計の平均定期給与額の増減をもとに毎年8月1日に改定されます。"
                 "%s以後の額は次のとおりです。</p>" % LIM["as_of"])
    parts.append(table(["項目", "改定前", "改定後（%s）" % LIM["as_of"]],
                       kaitei_rows, ["", "n", "n"]))
    parts.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">'
                 '厚生労働省 雇用継続給付（育児休業給付）の支給限度額等</a>（%s確認）</p>'
                 % (K["src2"], CHECKED))

    parts.append('<h2 id="shurui">育児にかかわる雇用保険の給付を横断で見る</h2>')
    parts.append("<p>「育休のお金」とひとまとめに語られますが、雇用保険の給付は別々の条文にもとづく"
                 "別々の制度で、支給率も上限額も違います。確認日時点で有効なものを並べます。</p>")
    parts.append(table(["給付の種類", "支給率", "支給上限額", "根拠条文"],
                       kind_rows, ["", "", "n", ""]))
    parts.append("<p>%s</p>" % REL["shussei_go_kyugyo_shien_kyufukin"])
    parts.append("<p>%s</p>" % REL["ikuji_jitan_shugyo_kyufukin"])

    parts.append('<h2 id="chosei">休業中に給与が出ると減る（80％の調整）</h2>')
    parts.append("<p>%s</p>" % K["chingin_chosei"])
    parts.append("<p>つまり会社から休業中に賃金が支払われる場合、給付金と合わせて額面の80％までは"
                 "受け取れますが、そこが天井になります。80％以上の賃金が支払われている期間は、"
                 "育児休業給付金は支給されません。</p>")

    parts.append('<h2 id="encho">延長しても支給率は上がらない</h2>')
    parts.append("<p>1歳6か月まで、あるいは2歳までの延長が認められた場合も、支給率が延長を理由に"
                 "変わる規定はありません。休業日数が通算180日を超えているため50％のままです。"
                 "また延長そのものについては、2025年（令和7年）4月から給付金側の手続きが厳格化され、"
                 "保育所等の利用申込書の写し（全ページ）と延長事由認定申告書の提出が必須になりました。"
                 "<strong>育児休業そのものの延長（育児・介護休業法・申出先は勤務先）と、"
                 "給付金の延長（雇用保険法・申請先はハローワーク）は別の判定です。</strong>"
                 "条件と必要書類は判定ツールで確認できます。</p>")

    parts.append("""
<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/tools/ikukyu-encho-hantei/">育休はいつまで延長できる？条件と必要書類の判定</a></li>
<li><a href="/articles/shussan-ichijikin-data/">出産育児一時金は50万円｜内訳・受け取り方・改定の履歴</a></li>
<li><a href="/articles/shussan-hiyou-data/">出産費用の平均はいくら？都道府県別・費目別の実額</a></li>
<li><a href="/articles/sangokea-josei/">産後ケアの助成はいくら？非課税世帯の減免と所得を問わない減額枠</a></li>
<li><a href="/tools/sangokea-ryokin/">産後ケアの料金はいくら？自治体別の自己負担</a></li>
</ul>""")
    parts.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    parts.append(faq_html(FAQ))

    parts.append(source_list([
        (K["src"], "e-Gov法令検索 雇用保険法（昭和四十九年法律第百十六号）"),
        ("https://laws.e-gov.go.jp/law/350M50002000003",
         "e-Gov法令検索 雇用保険法施行規則（昭和五十年労働省令第三号）"),
        (K["src2"], "厚生労働省 雇用継続給付（育児休業給付）の支給限度額等の改定について"),
        (K["src3"], "厚生労働省 育児休業給付について"),
        ("https://www.mhlw.go.jp/content/001269748.pdf",
         "厚生労働省リーフレット LL060701保01『2025年4月から保育所等に入れなかったことを"
         "理由とする育児休業給付金の支給対象期間延長手続きが変わります』"),
    ]))

    write(slug,
          "育児休業給付金はいくら？67％は180日まで・上限%s（令和8年8月改定）" % yen(JOGEN_67),
          "育児休業給付金はいくら？｜67％は最初の180日だけ、そして上限がある",
          "育児休業給付金は休業開始から通算180日までが賃金の67％、181日目以降は50％です"
          "（雇用保険法第61条の7第6項）。支給には上限があり、休業開始時の賃金月額が%sを超えると"
          "実効率は67％より下がります。令和8年8月1日改定の上限額%s、賃金月額別の支給額、"
          "出生時育児休業給付金・出生後休業支援給付金との違い、休業中に給与が出た場合の80％調整まで"
          "条文の出典つきで整理しました。確認日は%s。"
          % (yen(CHINGIN_JOGEN), yen(JOGEN_67), CHECKED),
          "67％なのは休業開始から通算180日まで。181日目以降と延長期間は50％です。",
          FAQ, "\n".join(parts), TODAY, CHECKED, PR_HEAD, PR_BODY)


FAQ = [
 ("育児休業給付金はいくらもらえますか？",
  "休業開始時賃金日額×支給日数×67％です。ただし67％なのは育児休業を開始した日から起算して"
  "支給に係る休業日数が通算180日に達するまでで、181日目以降は50％になります"
  "（雇用保険法第61条の7第6項）。支給単位期間は原則30日なので、たとえば休業開始時の賃金月額が"
  "300,000円なら、180日までは1か月あたり201,000円、181日目以降は150,000円が目安です。"),
 ("上限はいくらですか？",
  "令和8年8月1日以後、支給率67％のときの支給上限額は%s、50％のときは%sです。"
  "これは休業開始時賃金月額の上限額%sに、それぞれの支給率を掛けた額にあたります。"
  "賃金月額が上限を超える場合は、実際の賃金ではなく上限額を使って計算します。"
  "下限額は%sです。上限額・下限額は毎年8月1日に改定されます。"
  % (yen(JOGEN_67), yen(JOGEN_50), yen(CHINGIN_JOGEN), yen(CHINGIN_KAGEN))),
 ("育休を延長したら支給率は下がりますか？",
  "延長を理由に下がるのではなく、日数で下がります。支給率が変わる基準は「休業開始から通算180日」"
  "だけで、延長を理由に率を変える規定はありません。1歳〜1歳6か月、1歳6か月〜2歳の延長期間は"
  "その時点で通算180日を超えているのが通常なので、結果として50％になります。"),
 ("休業中に会社から給与が出たらどうなりますか？",
  "支給単位期間中に事業主から賃金が支払われた場合、賃金額と給付額の合計が休業開始時賃金日額×"
  "支給日数の80％以上になるときは、80％相当額から賃金額を引いた額が給付額になります。"
  "賃金額だけで80％以上になるときは、その支給単位期間の育児休業給付金は支給されません"
  "（雇用保険法第61条の7第7項）。"),
 ("出生時育児休業給付金や出生後休業支援給付金とは何が違いますか？",
  "どれも雇用保険の給付ですが、根拠条文も支給率も別です。出生時育児休業給付金（産後パパ育休・"
  "法第61条の8）は支給率67％で上限%s。出生後休業支援給付金（法第61条の10・令和7年4月1日施行）は"
  "休業開始時賃金日額×出生後休業日数（上限28日）×13％で、上限は%sです。"
  "出生後休業支援給付金は子の出生後8週間以内等が対象なので、延長期間には関係しません。"
  % (yen(SHUSSEIJI_JOGEN), yen(SHUSSEIGO_JOGEN))),
 ("給付金に税金や社会保険料はかかりますか？",
  "育児休業給付金は非課税で、所得税はかかりません。また育児休業期間中は健康保険・厚生年金保険の"
  "保険料が免除されます。そのため額面上の67％・50％という数字よりも、休業前の手取りに対する"
  "比率は高くなります。ただし免除の要件や期間の詳細は加入する保険者の取扱いによるため、"
  "勤務先または日本年金機構の案内で確認してください。"),
]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build()
    print("67%%上限 %s ／ 50%%上限 %s ／ 賃金月額上限 %s"
          % (yen(JOGEN_67), yen(JOGEN_50), yen(CHINGIN_JOGEN)))

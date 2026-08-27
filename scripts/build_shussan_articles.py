# -*- coding: utf-8 -*-
"""出産費用・出産育児一時金のデータ記事を生成する（2026-08-27 新設）

狙う語は data_gate.py でGO判定だった2語:
  「出産費用 平均」（サジェスト10件）／「出産育児一時金」（10件）
どちらも既存の受け皿が無い。

数値は scripts/data/shussan_hiyou.json（厚労省資料の実査）から引く。
本文は %書式ではなく部品の連結で組む（引数の数がずれる事故を避けるため）。
"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _article_shell import faq_html, source_list, table, write

TODAY = "2026-08-27"
CHECKED = "2026年8月27日"
D = json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "data", "shussan_hiyou.json"), encoding="utf-8"))

HEIKIN = D["zenkoku_heikin"]
GOUKEI = D["zenkoku_ninpu_goukei_futangaku"]
ICHIJI = D["ichijikin"]
SAI = GOUKEI["value"] - HEIKIN["value"]

PR_HEAD = "出産前に、生活のほうの固定費を一度見ておく"
PR_BODY = ("出産費用そのものは制度で決まる部分が大きく、こちらで動かせる余地は多くありません。"
           "一方で、産後にいちばん効いてくるのは日々の家事の総量です。"
           "買い物と献立を考える時間を先に削っておくと、退院後の立ち上がりが変わります。")


def srcs(*keys):
    out, seen = [], set()
    for s in D["sources"]:
        if any(k in s.get("label", "") for k in keys) and s["url"] not in seen:
            seen.add(s["url"])
            out.append((s["url"], s["label"]))
    return out


def yen(n):
    return "{:,}円".format(n)


# =========================================================== 出産費用
def build_hiyou():
    slug = "shussan-hiyou-data"

    pref = sorted(D["todofuken"], key=lambda x: -(x["value"] or 0))
    pref_rows = [(p["name"], yen(p["value"]),
                  yen(p["value_r5"]) if p.get("value_r5") else "—")
                 for p in pref]
    top, bottom = pref[0], pref[-1]

    suii_rows = []
    for r in D["suii"]:
        v = yen(r["value"]) if r.get("value") else ("%.1f万円" % r["value_man"])
        suii_rows.append((r["year"], v,
                          "" if r.get("value") else "グラフ表示値"))

    shi = [s for s in D["shisetsu_betsu"] if s.get("value")]
    shi_rows = [(s["type"], s["as_of"], s.get("bunben", "—"), yen(s["value"]))
                for s in shi]

    hiwake_rows = [(i["komoku"], yen(i["value"]), i.get("teigi", "—"))
                   for i in D["hiwake_hitori_atari"]["items"]]

    parts = []
    parts.append(
        "<blockquote><strong>厚生労働省が公表する「出産費用の平均」と、実際に窓口で請求される額は違います。</strong>"
        "%sの平均出産費用は<strong>%s</strong>ですが、これは室料差額・産科医療補償制度の掛金・その他"
        "（文書料やお祝い膳など）を<strong>除いた</strong>額です。それらを含む妊婦合計負担額の平均は"
        "<strong>%s</strong>で、差は約%s万円あります。「平均約50万円」という数字だけを見て準備すると足りません。</blockquote>"
        % (HEIKIN["as_of"], yen(HEIKIN["value"]), yen(GOUKEI["value"]), round(SAI / 10000)))

    parts.append('<h2 id="latest">全国平均：2つの数字</h2>')
    parts.append(table(["区分", "全国平均", "含むもの"],
                       [("出産費用", yen(HEIKIN["value"]), "入院料・分娩料・新生児管理保育料・検査薬剤料・処置手当料"),
                        ("妊婦合計負担額", yen(GOUKEI["value"]), "上記＋室料差額＋産科医療補償制度掛金＋その他")],
                       ["", "n", ""]))
    parts.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a>（%s確認）</p>'
                 % (HEIKIN["src"], HEIKIN["src_label"], CHECKED))
    parts.append("<p>%s</p>" % D["fukumu_fukumanai"]["note"])

    parts.append('<h2 id="hiwake">費目別の内訳</h2>')
    parts.append("<p>%s</p>" % D["hiwake_hitori_atari"]["note"])
    parts.append(table(["費目", "1件あたり平均", "内容"], hiwake_rows, ["", "n", ""]))
    parts.append('<p class="srcline">%s 出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>'
                 % (D["hiwake_hitori_atari"]["as_of"], D["hiwake_hitori_atari"]["src"],
                    D["hiwake_hitori_atari"]["src_label"]))

    parts.append('<h2 id="pref">都道府県別の平均出産費用</h2>')
    parts.append("<p>最も高いのは%s（%s）、最も低いのは%s（%s）で、差は%sあります。"
                 "同じ正常分娩でも住む場所で1.6倍違うことになります。</p>"
                 % (top["name"], yen(top["value"]), bottom["name"], yen(bottom["value"]),
                    yen(top["value"] - bottom["value"])))
    parts.append(table(["都道府県", "令和6年度", "令和5年度"], pref_rows, ["", "n", "n"]))
    parts.append('<p class="srcline">%s</p>' % D["todofuken_note"])

    parts.append('<h2 id="suii">推移</h2>')
    parts.append("<p>%s</p>" % D["suii_note"])
    parts.append(table(["年度", "平均出産費用", "備考"], suii_rows, ["", "n", ""]))
    parts.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>'
                 % (D["suii_src"], D["suii_src_label"]))

    parts.append('<h2 id="shisetsu">施設の種類別</h2>')
    parts.append(table(["施設種別", "年度", "集計範囲", "平均"], shi_rows, ["", "", "", "n"]))
    parts.append('<p class="srcline">%s</p>' % D["shisetsu_betsu_note"])

    parts.append('<h2 id="chui">数字を読むときの注意</h2>')
    parts.append("<h3>「出産費用」と「妊婦合計負担額」を混ぜない</h3>")
    parts.append("<p>ニュースやまとめ記事で「平均約50万円」とされているのは前者です。"
                 "実際に請求される総額は後者で、平均で約%s万円多くなります。準備する金額を考えるときは後者で見てください。</p>"
                 % round(SAI / 10000))
    parts.append("<h3>施設種別の順位は集計範囲で入れ替わる</h3>")
    parts.append("<p>正常分娩だけで見るか、異常分娩を含む全体で見るかによって、私的病院と診療所の順位が入れ替わります。"
                 "どちらの集計かを確かめずに比較すると、資料どうしで矛盾した記述になります。</p>")
    parts.append("<h3>年度の粒度が3種類ある</h3>")
    parts.append("<p>公表資料には通年・上半期・単月の値が混在しています。本記事では表ごとに集計期間を明記していますが、"
                 "他の資料と突き合わせるときは期間が揃っているかを先に確認してください。</p>")

    parts.append("""
<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/articles/shussan-ichijikin-data/">出産育児一時金は50万円のまま？内訳・改定の履歴・現物給付化の法改正</a></li>
<li><a href="/articles/sangokea-josei/">産後ケアの助成はいくら？非課税世帯の減免と所得を問わない減額枠</a></li>
<li><a href="/articles/sangokea-nankai/">産後ケアは何回使える？43自治体の上限一覧</a></li>
<li><a href="/tools/ikukyu-encho-hantei/">育休はいつまで延長できる？条件と必要書類の判定</a></li>
<li><a href="/tools/sangokea-ryokin/">産後ケアの料金はいくら？自治体別の自己負担</a></li>
</ul>""")
    parts.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    parts.append(faq_html(FAQ_HIYOU))
    parts.append(source_list(srcs("出産費用", "医療保険制度における出産")))

    write(slug,
          "出産費用の平均はいくら？全国%s・妊婦合計負担額%s（令和6年度）と都道府県別"
          % (yen(HEIKIN["value"]), yen(GOUKEI["value"])),
          "出産費用の平均はいくら？｜「出産費用」と「実際に請求される額」は約%s万円違う" % round(SAI / 10000),
          "出産費用の全国平均は%s（%s・正常分娩・全施設）ですが、これは室料差額や産科医療補償制度の"
          "掛金を除いた額です。実際に請求される妊婦合計負担額の平均は%sで、約%s万円多くなります。"
          "都道府県別47件（最高%s%s・最低%s%s）、費目別の内訳、施設種別、12年の推移を出典つきで"
          "整理しました。確認日は%s。"
          % (yen(HEIKIN["value"]), HEIKIN["as_of"], yen(GOUKEI["value"]), round(SAI / 10000),
             top["name"], yen(top["value"]), bottom["name"], yen(bottom["value"]), CHECKED),
          "厚労省の「平均約50万円」は室料差額等を除いた額。実際の請求総額の平均は%sです。"
          % yen(GOUKEI["value"]),
          FAQ_HIYOU, "\n".join(parts), TODAY, CHECKED, PR_HEAD, PR_BODY)


FAQ_HIYOU = [
 ("出産費用の平均はいくらですか？",
  "%sの全国平均は%s（正常分娩・全施設）です。ただしこれは室料差額・産科医療補償制度の掛金・"
  "その他（文書料やお祝い膳など）を除いた額で、厚生労働省が「出産費用」と呼んでいる数字です。"
  "実際に窓口で請求される総額にあたる「妊婦合計負担額」の平均は%sで、約%s万円多くなります。"
  % (HEIKIN["as_of"], yen(HEIKIN["value"]), yen(GOUKEI["value"]), round(SAI / 10000))),
 ("出産費用がいちばん高い都道府県はどこですか？",
  "令和6年度の平均出産費用が最も高いのは東京都で648,309円、最も低いのは熊本県で404,411円です。"
  "差は243,898円で、同じ正常分娩でも約1.6倍の開きがあります。令和5年度も最高が東京都、"
  "最低が熊本県で順位は変わっていません。"),
 ("出産費用は上がっていますか？",
  "上がっています。平成24年度の41.7万円から令和6年度の519,805円まで、12年間で約10.3万円"
  "（約24.7%）増えました。円単位の値が公表されているのは令和4年度以降で、それ以前は"
  "資料のグラフに万円単位で示された値です。"),
 ("公立の病院のほうが安いのですか？",
  "令和5年度・正常分娩の平均では、公的病院473,990円、私的病院524,345円、診療所510,754円で、"
  "公的病院が最も低い結果でした。ただし異常分娩を含む全体で見ると診療所と私的病院の順位が"
  "入れ替わります。比較するときは、どちらの集計範囲かを確かめてください。"),
 ("帝王切開や無痛分娩だといくらかかりますか？",
  "帝王切開は異常分娩として医療保険が適用されており、診療報酬点数（緊急22,200点・選択20,140点、"
  "1点10円）にもとづく自己負担になります。高額療養費制度の対象にもなります。"
  "無痛分娩は確認日時点で保険適用されておらず自費です。無痛分娩費用の全国平均を示す公的統計は"
  "存在せず、施設ごとの公表を確認する必要があります。"),
 ("出産費用は保険適用になるのですか？",
  "出産費用そのものの保険適用ではありませんが、令和8年法律第31号（令和8年5月29日成立・6月5日公布）で"
  "出産育児一時金を廃止して現物給付に切り替えることが決まっています。分娩1件あたりの基本単価を国が"
  "設定し、保険者から施設へ直接支払われる仕組みです。ただし施行日は公布後2年以内に政令で定めるとされ、"
  "単価も現金給付額も確認日時点で未定です。"),
]


# =========================================================== 出産育児一時金
def build_ichijikin():
    slug = "shussan-ichijikin-data"

    kaitei_rows = []
    for k in D["kaitei"]:
        frm = yen(k["from"]) if k.get("from") else "—"
        kaitei_rows.append((k["when"], frm, yen(k["to"]), k["naiyo"]))

    youken = "".join("<li>%s</li>" % y for y in ICHIJI["shikyu_youken"])

    parts = []
    parts.append(
        "<blockquote><strong>出産育児一時金は原則%sです（%s）。</strong>"
        "内訳は本人への支給分%sと、産科医療補償制度の掛金分%sに分かれます。"
        "そしてこの制度は<strong>廃止が既に法律で決まっています</strong>。"
        "令和8年法律第31号が令和8年5月29日に成立・6月5日に公布され、"
        "一時金を現物給付へ切り替えることになりました。ただし施行日も新しい単価も、確認日時点で未定です。</blockquote>"
        % (yen(ICHIJI["value"]), ICHIJI["as_of"], yen(ICHIJI["honnin_shikyubun"]),
           yen(ICHIJI["sanka_iryo_hosho"])))

    parts.append('<h2 id="gaku">金額と内訳</h2>')
    parts.append(table(["区分", "金額"],
                       [("出産育児一時金（原則）", yen(ICHIJI["value"])),
                        ("うち本人支給分", yen(ICHIJI["honnin_shikyubun"])),
                        ("うち産科医療補償制度の掛金分", yen(ICHIJI["sanka_iryo_hosho"])),
                        ("減額される場合", yen(ICHIJI["genkaku_value"]))],
                       ["", "n"]))
    parts.append("<p>%s</p>" % ICHIJI["genkaku_joken"])
    parts.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a>（%s確認）</p>'
                 % (ICHIJI["src"], ICHIJI["src_label"], CHECKED))

    parts.append('<h2 id="youken">受け取れる条件</h2>')
    parts.append("<ul>%s</ul>" % youken)
    parts.append("<p>出産の方法や場所は問われません。早産・死産・流産・人工妊娠中絶であっても、"
                 "妊娠4か月（85日）以上であれば支給の対象になります。</p>")

    parts.append('<h2 id="kaitei">改定の履歴</h2>')
    parts.append("<p>創設は平成6年10月で、30万円から始まりました。直近の改定は令和5年4月の"
                 "42万円から50万円への引き上げで、13年ぶりの大幅な増額でした。</p>")
    parts.append(table(["時期", "改定前", "改定後", "内容"], kaitei_rows, ["", "n", "n", ""]))
    parts.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>'
                 % (D["kaitei_src"], D["kaitei_src_label"]))

    parts.append('<h2 id="shiharai">受け取り方は3つ。ただし自分では選べないことがある</h2>')
    parts.append("<h3>直接支払制度</h3><p>%s</p>" % D["shiharai_seido"]["chokusetsu"])
    parts.append("<h3>受取代理制度</h3><p>%s</p>" % D["shiharai_seido"]["uketori_dairi"])
    parts.append("<p><strong>%s</strong>つまり受取代理を使えるかどうかは、本人ではなく出産する施設で決まります。</p>"
                 % D["shiharai_seido"]["joken"])
    parts.append("<h3>償還払い制度</h3><p>%s</p>" % D["shiharai_seido"]["shoukan"])

    parts.append('<h2 id="hoken">帝王切開・無痛分娩の扱い</h2>')
    parts.append("<p>%s</p>" % D["teiousekkai_mutsuu"]["teiousekkai"])
    parts.append("<p>%s</p>" % D["teiousekkai_mutsuu"]["kougakuryouyou"])
    parts.append("<p>%s</p>" % D["teiousekkai_mutsuu"]["mutsuu"])

    parts.append('<h2 id="yotei">制度は廃止が決まっている（施行日は未定）</h2>')
    parts.append("<p>%s</p>" % D["yotei"])
    parts.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>'
                 % (D["yotei_src"], D["yotei_src_label"]))
    parts.append("<p>いま妊娠中の方がすぐに影響を受けるわけではありません。施行日は公布後2年以内に"
                 "政令で定めるとされており、確認日時点では決まっていないためです。施設は当分の間、"
                 "現行の出産育児一時金を選ぶこともできるとされています。</p>")

    parts.append("""
<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/articles/shussan-hiyou-data/">出産費用の平均はいくら？都道府県別・費目別の実額</a></li>
<li><a href="/articles/sangokea-josei/">産後ケアの助成はいくら？非課税世帯の減免と所得を問わない減額枠</a></li>
<li><a href="/articles/sangokea-nankai/">産後ケアは何回使える？43自治体の上限一覧</a></li>
<li><a href="/tools/ikukyu-encho-hantei/">育休はいつまで延長できる？条件と必要書類の判定</a></li>
<li><a href="/tools/sangokea-ryokin/">産後ケアの料金はいくら？自治体別の自己負担</a></li>
</ul>""")
    parts.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    parts.append(faq_html(FAQ_ICHIJI))
    parts.append(source_list(srcs("出産育児一時金", "医療保険制度における出産", "健康保険法等")))

    write(slug,
          "出産育児一時金は%s｜内訳・受け取り方・改定の履歴と現物給付化の法改正"
          % yen(ICHIJI["value"]),
          "出産育児一時金は%s｜内訳と受け取り方、そして廃止が決まっていること" % yen(ICHIJI["value"]),
          "出産育児一時金は原則%sで、内訳は本人支給分%sと産科医療補償制度の掛金%sです。"
          "受け取り方は直接支払・受取代理・償還払いの3つですが、受取代理は施設側の条件で決まるため"
          "本人が選べるとは限りません。創設から9回の改定の履歴、帝王切開と無痛分娩の扱い、"
          "そして令和8年法律第31号で廃止と現物給付化が決まっている点まで出典つきで整理しました。確認日は%s。"
          % (yen(ICHIJI["value"]), yen(ICHIJI["honnin_shikyubun"]),
             yen(ICHIJI["sanka_iryo_hosho"]), CHECKED),
          "出産育児一時金は原則%s。廃止と現物給付化が法律で決まっており、施行日は未定です。"
          % yen(ICHIJI["value"]),
          FAQ_ICHIJI, "\n".join(parts), TODAY, CHECKED, PR_HEAD, PR_BODY)


FAQ_ICHIJI = [
 ("出産育児一時金はいくらもらえますか？",
  "原則%sです（%s）。内訳は本人への支給分%sと、産科医療補償制度の掛金分%sに分かれます。"
  "産科医療補償制度に未加入の医療機関等での出産、または在胎週数22週に達しない出産の場合は%sになります。"
  % (yen(ICHIJI["value"]), ICHIJI["as_of"], yen(ICHIJI["honnin_shikyubun"]),
     yen(ICHIJI["sanka_iryo_hosho"]), yen(ICHIJI["genkaku_value"]))),
 ("流産や死産でも受け取れますか？",
  "受け取れます。支給の要件は、出産時に公的医療保険に加入していることと、妊娠4か月（85日）以上で"
  "あることの2点で、出産の方法や場所は問われません。早産・死産・流産・人工妊娠中絶も対象です。"),
 ("直接支払制度と受取代理制度はどちらを選べばいいですか？",
  "多くの場合、本人が選べるものではありません。受取代理制度を導入できるのは、年間の平均分娩取扱件数が"
  "100件以下の診療所・助産所などで、かつ厚生労働省に届出をした施設に限られます。"
  "つまり出産する施設がどちらの制度を採っているかで決まります。届出施設の一覧は厚生労働省の"
  "サイトに掲載されています。"),
 ("出産費用が一時金の50万円を超えたらどうなりますか？",
  "直接支払制度を使っている場合、超えた分を退院時に窓口で支払います。逆に出産費用が50万円を下回った"
  "場合は、差額を保険者に申請して受け取れます。なお厚生労働省の資料では、令和5年4月の増額直後に"
  "自己負担の平均が76,819円から22,919円まで下がったあと、令和7年3月には34,961円まで再び上昇しており、"
  "出産費用が一時金の範囲に収まった分娩の割合も58%から52%へ下がっています。"),
 ("出産育児一時金は今後どうなりますか？",
  "廃止が決まっています。令和8年法律第31号（令和8年5月29日成立・6月5日公布）により、"
  "出産育児一時金を廃止して現物給付に切り替えることになりました。分娩1件あたりの基本単価を国が設定し、"
  "保険者から施設へ直接支払われる仕組みで、窓口の自己負担はゼロになる想定です。"
  "ただし施行日は公布後2年以内に政令で定めるとされ、基本単価も併せて支給される現金給付の額も、"
  "確認日時点では決まっていません。"),
 ("帝王切開の場合、一時金とは別に給付はありますか？",
  "帝王切開は異常分娩として医療保険が適用されるため、保険診療となった部分は高額療養費制度の"
  "対象になります。出産育児一時金はそれとは別に支給されます。加入している健康保険によっては"
  "付加給付がある場合もあるため、保険者に確認してください。"),
]




# =========================================================== 出産費用の無償化
def build_mushouka():
    slug = "shussan-mushouka"

    kimatta = [
        ("法律", "健康保険法等の一部を改正する法律（令和8年法律第31号）"),
        ("成立", "令和8年5月29日"),
        ("公布", "令和8年6月5日"),
        ("施行期限", "公布後2年以内に政令で定める日（＝遅くとも令和10年6月4日）"),
    ]
    naiyou = [
        ("出産育児一時金に代わる給付方式",
         "保険診療以外の分娩について「分娩1件あたり基本単価」を国が設定し、保険者から施設へ直接支給する現物給付に切り替える。"
         "全国同水準で、施設の体制や役割を評価した加算がある。これにより出産の標準的な費用に妊婦の自己負担が生じないようにする"),
        ("全妊婦への定額の現金給付",
         "上記とは別に、保険診療の一部負担金など出産時の費用負担を軽減するため、すべての妊婦に定額の現金給付を行う"),
        ("費用の見える化の義務付け",
         "施設が提供するサービスの内容や費用等に関する情報提供を義務付ける"),
    ]
    mikettei = [
        ("施行日", "「公布後2年以内に政令で定める日」とされているだけで、具体的な日は未定"),
        ("分娩1件あたりの基本単価", "告示事項。確認日時点で未告示"),
        ("全妊婦への現金給付の額", "政令事項。確認日時点で未制定"),
    ]

    parts = []
    parts.append(
        "<blockquote><strong>出産費用の無償化は「決まっている」が、「いつからか」は決まっていません。</strong>"
        "健康保険法等の一部を改正する法律（令和8年法律第31号）が令和8年5月29日に成立し、6月5日に公布されました。"
        "出産育児一時金を廃止して現物給付に切り替えることは、法律としては確定しています。"
        "一方で<strong>施行日も、分娩1件あたりの基本単価も、全妊婦への現金給付の額も、いずれも確認日時点で未定</strong>です。"
        "この記事は、決まっていることと決まっていないことを分けて整理します。</blockquote>")

    parts.append('<h2 id="kimatta">決まっていること</h2>')
    parts.append(table(["項目", "内容"], kimatta, ["", ""]))
    parts.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a>（%s確認）</p>'
                 % (D["yotei_src"], D["yotei_src_label"], CHECKED))
    parts.append("<h3>改正の3つの柱</h3>")
    parts.append(table(["柱", "内容"], naiyou, ["", ""]))

    parts.append('<h2 id="mikettei">決まっていないこと</h2>')
    parts.append("<p>「無償化」という言葉だけが先に広がっていますが、実際にいくらが無償になるのかは、"
                 "確認日時点でひとつも数字が出ていません。</p>")
    parts.append(table(["項目", "状況"], mikettei, ["", ""]))
    parts.append("<p>したがって「いつから無償になるか」という問いに対する正確な答えは、"
                 "<strong>「法律は成立しているが、施行日は政令待ちで未定。遅くとも令和10年6月4日までには施行される」</strong>になります。</p>")

    parts.append('<h2 id="ima">いま実際にかかっている費用</h2>')
    parts.append("<p>無償化が置き換えようとしているのは、次の金額です。</p>")
    parts.append(table(["区分", "全国平均", "内容"],
                       [("出産費用", yen(HEIKIN["value"]), "室料差額・産科医療補償制度掛金・その他を除いた額"),
                        ("妊婦合計負担額", yen(GOUKEI["value"]), "実際に請求される総額。上より%s高い" % yen(SAI)),
                        ("出産育児一時金", yen(ICHIJI["value"]), "本人支給分%s＋産科医療補償制度の掛金%s"
                         % (yen(ICHIJI["honnin_shikyubun"]), yen(ICHIJI["sanka_iryo_hosho"])))],
                       ["", "n", ""]))
    parts.append("<p>一時金%sに対して妊婦合計負担額の平均が%sなので、"
                 "平均的には差額が自己負担として残ります。ただし出産費用は都道府県で大きく違い、"
                 "東京都648,309円・熊本県404,411円と243,898円の開きがあります。"
                 "同じ全国一律の一時金でも、住む場所によって残る自己負担がまったく違うのが現状です。</p>"
                 % (yen(ICHIJI["value"]), yen(GOUKEI["value"])))
    parts.append('<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>'
                 % (HEIKIN["src"], HEIKIN["src_label"]))

    parts.append('<h2 id="taishou">無償化の対象になるもの・ならないもの</h2>')
    parts.append("<p>改正の条文は「<strong>保険診療以外の分娩</strong>」について基本単価を設定するとしています。"
                 "つまり既に保険が適用されている分娩は、そもそも今回の仕組みの対象外です。</p>")
    parts.append("<h3>帝王切開は今回の改正の対象ではない</h3>")
    parts.append("<p>%s</p>" % D["teiousekkai_mutsuu"]["teiousekkai"])
    parts.append("<p>保険診療となった部分は高額療養費制度の対象です。今回の改正で新設される"
                 "全妊婦への定額の現金給付は、こうした保険診療の一部負担金の軽減も目的に含まれています。</p>")
    parts.append("<h3>無痛分娩は確認日時点で自費のまま</h3>")
    parts.append("<p>%s</p>" % D["teiousekkai_mutsuu"]["mutsuu"])
    parts.append("<h3>基本単価が何を含むかで結論が変わる</h3>")
    parts.append("<p>厚生労働省が公表する「出産費用」は、次の5つの費目の合計です。"
                 "実際に請求される「妊婦合計負担額」は、これに室料差額・産科医療補償制度の掛金・その他が加わります。</p>")
    parts.append(table(["費目", "1件あたり平均", "内容"],
                       [(i["komoku"], yen(i["value"]), i.get("teigi", "—"))
                        for i in D["hiwake_hitori_atari"]["items"]], ["", "n", ""]))
    parts.append('<p class="srcline">%s 出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>'
                 % (D["hiwake_hitori_atari"]["as_of"], D["hiwake_hitori_atari"]["src"],
                    D["hiwake_hitori_atari"]["src_label"]))
    parts.append("<p><strong>この表のどこまでを基本単価が賄うのかが、確認日時点では分かりません。</strong>"
                 "上5項目（出産費用）までなのか、室料差額やその他まで含むのかで、"
                 "実際に窓口で払う額がゼロになるかどうかが変わります。"
                 "改正には施設の費用の見える化を義務付ける柱も含まれているため、"
                 "単価の告示とあわせて各施設の内訳が確認できるようになる見込みです。</p>")

    parts.append('<h2 id="keii">なぜ無償化が進められているのか</h2>')
    parts.append("<p>この見直しの起点は、「妊娠・出産・産後における妊産婦等の支援策等に関する検討会」の"
                 "議論の整理（令和7年5月14日公表）で示された方針です。そこでは"
                 "「令和8年度を目途に、産科医療機関等の経営実態等にも十分配慮しながら、"
                 "標準的な出産費用の自己負担無償化に向けた具体的な制度設計を進める」とされました。</p>")
    parts.append("<p>出産育児一時金は令和5年4月に42万円から50万円へ引き上げられましたが、"
                 "引き上げによって施設側の価格も動くため、一時金の増額だけでは自己負担が残り続ける構造がありました。"
                 "今回の改正で<strong>金額を上げる方式から、国が単価を決めて直接支払う方式へ切り替える</strong>のは、"
                 "この構造への対応にあたります。</p>")

    parts.append('<h2 id="ikou">移行期に注意すること</h2>')
    parts.append("<h3>施設によっては当分の間、現行の一時金のまま</h3>")
    parts.append("<p>新しい仕組みには準備の整った施設から順次移行するとされており、"
                 "<strong>施設の選択により、当分の間は施設単位で現行の出産育児一時金の適用を受けることも可能</strong>です。"
                 "つまり施行日を過ぎても、出産する施設によって仕組みが違う時期が発生します。</p>")
    parts.append("<h3>妊婦健診にも改正がある</h3>")
    parts.append("<p>あわせて妊婦健診についても、国が「望ましい基準」内の検査の実施に係る「標準額」を定める等の改正が"
                 "母子保健法に規定されました（こども家庭庁所管）。出産時の費用だけでなく、"
                 "妊娠期間中の健診の扱いも変わります。</p>")
    parts.append("<h3>いま妊娠中の方への影響</h3>")
    parts.append("<p>確認日時点では施行日が決まっていないため、現在妊娠中の方はこれまでどおり"
                 "出産育児一時金50万円の仕組みが適用されます。直接支払制度・受取代理制度・償還払いの3つの受け取り方も変わりません。</p>")

    parts.append("""
<h2 id="related">関連する記事とツール</h2>
<ul>
<li><a href="/articles/shussan-hiyou-data/">出産費用の平均はいくら？都道府県別・費目別の実額</a></li>
<li><a href="/articles/shussan-ichijikin-data/">出産育児一時金は50万円｜内訳・受け取り方・改定の履歴</a></li>
<li><a href="/articles/sangokea-josei/">産後ケアの助成はいくら？非課税世帯の減免と所得を問わない減額枠</a></li>
<li><a href="/articles/sangokea-nankai/">産後ケアは何回使える？43自治体の上限一覧</a></li>
<li><a href="/tools/ikukyu-encho-hantei/">育休はいつまで延長できる？条件と必要書類の判定</a></li>
</ul>""")
    parts.append('<h2 id="faq">よくある質問（FAQ）</h2>')
    parts.append(faq_html(FAQ_MUSHOUKA))
    parts.append(source_list(srcs("健康保険法等", "医療保険制度における出産", "出産費用")))

    write(slug,
          "出産費用の無償化はいつから？法律は成立済み・施行日と金額は未定【%s時点】" % CHECKED,
          "出産費用の無償化はいつから？｜決まっていることと、まだ決まっていないこと",
          "出産費用の無償化は、健康保険法等の一部を改正する法律（令和8年法律第31号）が令和8年5月29日に成立・"
          "6月5日に公布され、出産育児一時金を廃止して現物給付に切り替えることが法律として確定しています。"
          "一方で施行日は「公布後2年以内に政令で定める日」とされているだけで未定、分娩1件あたりの基本単価も"
          "全妊婦への現金給付の額も未告示・未制定です。決まっていることと決まっていないことを分けて整理しました。確認日は%s。"
          % CHECKED,
          "無償化は法律としては確定。ただし施行日も金額もまだ決まっていません。",
          FAQ_MUSHOUKA, chr(10).join(parts), TODAY, CHECKED,
          "無償化を待つあいだにできること",
          "施行日が決まっていない以上、いま出産を迎える方は現行の仕組みで準備することになります。"
          "出産費用そのものは動かせませんが、産後の生活の負担は先に減らせます。")


FAQ_MUSHOUKA = [
 ("出産費用の無償化はいつからですか？",
  "確認日時点で施行日は決まっていません。健康保険法等の一部を改正する法律（令和8年法律第31号）は"
  "令和8年5月29日に成立・6月5日に公布されましたが、施行期日は「公布後2年以内に政令で定める日」と"
  "されているだけです。逆に言えば、遅くとも令和10年6月4日までには施行されます。"),
 ("無償化されると自己負担はゼロになりますか？",
  "「出産の標準的な費用に妊婦の自己負担が生じないようにする」というのが改正の趣旨です。"
  "ただし分娩1件あたりの基本単価は告示事項で、確認日時点で金額が示されていません。"
  "また室料差額（差額ベッド代）やお祝い膳などのアメニティ費用まで含めて無償になるかは、"
  "単価の設定次第です。現時点で「完全に無料になる」と断定できる材料はありません。"),
 ("出産育児一時金はなくなるのですか？",
  "法律上は廃止され、保険者から施設へ直接支給する現物給付に置き換わります。"
  "ただし新しい仕組みには準備の整った施設から順次移行するとされており、"
  "施設の選択により当分の間は施設単位で現行の出産育児一時金の適用を受けることも可能です。"
  "施行日を過ぎても、出産する施設によって仕組みが違う時期が発生します。"),
 ("いま妊娠中ですが、待ったほうが得ですか？",
  "確認日時点では施行日も金額も決まっていないため、待つ判断の材料がありません。"
  "現在は出産育児一時金50万円（本人支給分48.8万円＋産科医療補償制度の掛金1.2万円）の仕組みが"
  "そのまま適用されます。直接支払制度・受取代理制度・償還払いの3つの受け取り方も変わりません。"),
 ("現金給付もあると聞きましたが？",
  "あります。現物給付とは別に、保険診療の一部負担金など出産時の費用負担を軽減するため、"
  "すべての妊婦に定額の現金給付を行うことが法律に盛り込まれています。"
  "ただし金額は政令事項で、確認日時点で未制定です。"),
 ("なぜ一時金を上げるのではなく仕組みごと変えるのですか？",
  "出産育児一時金は令和5年4月に42万円から50万円へ引き上げられましたが、"
  "一時金を上げても自己負担が残り続ける構造がありました。今回の改正は、"
  "金額を上げる方式から、国が分娩1件あたりの基本単価を設定して保険者から施設へ直接支払う方式へ"
  "切り替えるものです。あわせて施設が提供するサービスの内容や費用の情報提供（見える化）も義務付けられます。"),
]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build_hiyou()
    build_ichijikin()
    build_mushouka()
    print("出産費用 %s ／ 妊婦合計負担額 %s ／ 差 %s"
          % (yen(HEIKIN["value"]), yen(GOUKEI["value"]), yen(SAI)))

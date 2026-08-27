# -*- coding: utf-8 -*-
"""公的統計のデータ記事を生成する（2026-08-27 新設）

狙う語は data_gate.py でGO判定だった3語:
  「生涯未婚率」（サジェスト10件）／「離婚率」（10件）／「共働き 割合」（10件）
いずれも既存の受け皿が無い。

数値は scripts/data/kon_rikon_tomobataraki.json（一次統計を実査して作成）から引く。
表を手で書かない。記事どうしで数字がズレないようにするため。

この型は「複数の公表値を横断で1枚の表にする＋出典＋確認日」で、
流入はAIとBingがほぼ全部。Google順位ではなくAIの引用を取りに行く。
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
                                   "data", "kon_rikon_tomobataraki.json"),
                      encoding="utf-8"))

MIKON = D["shougai_mikonritsu"]
RIKON = D["rikonritsu"]
KONIN = D["konin"]
TOMO = D["tomobataraki"]

PR_HEAD = "数字を眺めたあとに、手元で変えられること"
PR_BODY = ("統計は全体の傾向を示すだけで、個々の家庭の選択を決めるものではありません。"
           "共働きでも片働きでも、日々の家事の総量を減らすことは今日から手をつけられます。"
           "買い物と献立を考える時間を削るのはその一つです。")

RELATED_COMMON = """
<h2 id="related">関連する記事とツール</h2>
<ul>
%s
</ul>
"""


def srcs(*keys):
    """sources から必要なものだけ拾う（url, label）"""
    out = []
    for s in D["sources"]:
        if any(k in s.get("label", "") for k in keys):
            out.append((s["url"], s["label"]))
    return out


# =============================================================== 生涯未婚率
def build_mikon():
    slug = "shougai-mikonritsu-data"
    latest = MIKON["latest"]
    suii_rows = [(r["year"], "%.2f%%" % r["male"], "%.2f%%" % r["female"])
                 for r in MIKON["suii"]]
    gois = "".join("<li>%s</li>" % g for g in MIKON["gois"])
    kohyou = MIKON["suikei_kohyou"]
    kanren = MIKON["suikei_kanren"]

    body = """
<blockquote><strong>「生涯未婚率」は公式の統計用語ではありません。</strong>正式には<strong>50歳時未婚割合</strong>といい、45〜49歳の未婚割合と50〜54歳の未婚割合を平均した値です。最新値は%s時点で男性%.2f%%・女性%.2f%%（%s）。国勢調査は5年ごとなので毎年の値は存在せず、次の更新は令和7年国勢調査の基本集計（2026年9月29日公表予定）です。</blockquote>

<h2 id="latest">最新の50歳時未婚割合</h2>
%s
<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a>（%s確認）</p>

<h2 id="teigi">「生涯未婚率」の定義と、よくある3つの誤用</h2>
<p>%s</p>
<p>この指標を読むときに間違えやすいのは次の点です。</p>
<ul>
%s
</ul>
<p>%s</p>

<h2 id="suii">推移（1980年〜2020年）</h2>
<p>40年間で男性は約11倍、女性は約4倍になりました。1990年までは女性のほうが高く、1990年代に男女が逆転しています。</p>
%s
<p class="srcline">%s</p>
<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">同上</a></p>

<h2 id="suikei">将来推計</h2>
<p>50歳時未婚割合そのものの将来推計は公表されていませんが、関連する推計値があります。15歳以上人口全体の未婚率は、2020年の男性%.1f%%・女性%.1f%%から、2050年には男性%.1f%%・女性%.1f%%になると推計されています。</p>
<p>より変化が大きいのは高齢の単独世帯です。65歳以上の単独世帯に占める未婚の割合は、2020年の男性%.1f%%・女性%.1f%%から、2050年には男性%.1f%%・女性%.1f%%に上がると推計されています（%s）。</p>
<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>

<h2 id="derived">公式定義で計算し直すと、ピークは2040年前後</h2>
<p>社人研は年齢階級別の未婚率を推計していますが、それを「50歳時未婚割合」の形では公表していません。そこで公式の定義（45〜49歳と50〜54歳の未婚割合の平均）にそのまま当てはめて計算したのが下の表です。<strong>公表値ではなく当サイトによる算出値</strong>である点にご注意ください。元になる年齢階級別の推計値も併記しています。</p>
%s
<p class="srcline">元データ：<a href="%s" rel="noopener" target="_blank">国立社会保障・人口問題研究所『日本の世帯数の将来推計（全国推計）令和6(2024)年推計』</a>。50歳時未婚割合の欄は、同推計の年齢階級別未婚率から公式定義に従って当サイトが算出した派生値です。</p>
<p>この計算では男性が2040年前後、女性が2040〜2045年前後で頭打ちになり、その後わずかに下がります。ただしこれは推計値を機械的に平均したものなので、実測値と同じようには扱えません。</p>

<h2 id="chui">数字を扱うときの注意</h2>
<h3>毎年の値は存在しない</h3>
<p>算出の元になる国勢調査は5年ごとです。ニュースなどで毎年のように新しい数字が出るのは、別の統計（人口動態統計の婚姻件数など）か、推計値である場合があります。</p>
<h3>2015年・2020年は不詳補完値ベース</h3>
<p>2015年と2020年の値は不詳補完値にもとづいて算出されています。2010年以前と厳密に比較する場合は、この違いに注意が必要です。</p>
<h3>母集団が統計ごとに違う</h3>
<p>50歳時未婚割合は国勢調査（全数・5年ごと）、婚姻件数や離婚件数は人口動態統計（届出の全数）、共働き世帯数は労働力調査（標本）から出ています。調査が違うので、これらの数値を掛け合わせて別の比率を作ることはできません。</p>

%s

<h2 id="faq">よくある質問（FAQ）</h2>
%s

%s
""" % (latest["year"], latest["male"], latest["female"], latest["src_label"],
       table(["区分", "50歳時未婚割合"],
             [("男性", "%.2f%%" % latest["male"]), ("女性", "%.2f%%" % latest["female"])],
             ["", "n"]),
       latest["src"], latest["src_label"], CHECKED,
       MIKON["teigi"], gois, MIKON["meisho_note"],
       table(["年（国勢調査）", "男性", "女性"], suii_rows, ["", "n", "n"]),
       MIKON["suii_note"], MIKON["suii_src"],
       kohyou["2020_male"], kohyou["2020_female"], kohyou["2050_male"], kohyou["2050_female"],
       kanren["2020_male"], kanren["2020_female"], kanren["2050_male"], kanren["2050_female"],
       kanren["jissu_note"], kohyou["src"], kohyou["src_label"],
       table(["年（推計）", "男性 45〜49歳", "男性 50〜54歳", "男性 50歳時（算出）",
              "女性 45〜49歳", "女性 50〜54歳", "女性 50歳時（算出）"],
             [(r["year"], "%.1f%%" % r["male_45_49"], "%.1f%%" % r["male_50_54"],
               "%.2f%%" % r["male"], "%.1f%%" % r["female_45_49"],
               "%.1f%%" % r["female_50_54"], "%.2f%%" % r["female"])
              for r in MIKON["suikei"]],
             ["", "n", "n", "n", "n", "n", "n"]),
       MIKON["suikei"][0]["src"],
       RELATED_COMMON % (
           '<li><a href="/articles/rikonritsu-data/">離婚率は今どれくらい？件数・都道府県別・同居期間別の実数</a></li>\n'
           '<li><a href="/articles/tomobataraki-wariai-data/">共働き世帯の割合はどれくらい？専業主婦世帯との比較</a></li>\n'
           '<li><a href="/articles/hatsushon-nenmei-data/">平均初婚年齢は何歳？</a></li>\n'
           '<li><a href="/tools/konkatsu-type-shindan/">婚活タイプ診断</a></li>'),
       faq_html(FAQ_MIKON),
       source_list(srcs("人口統計資料集2026", "世帯数の将来推計")))

    write(slug,
          "生涯未婚率の最新値は？男性%.2f%%・女性%.2f%%（2020年国勢調査）と推移" % (latest["male"], latest["female"]),
          "生涯未婚率はいま何%%？｜正式名称「50歳時未婚割合」の最新値と40年の推移",
          "生涯未婚率（正式には50歳時未婚割合）の最新値は男性%.2f%%・女性%.2f%%です（%s）。"
          "45〜49歳と50〜54歳の未婚割合を平均した値で、国勢調査は5年ごとのため毎年の数字は存在しません。"
          "1980年からの推移、将来推計、よくある3つの誤用、次の更新時期（令和7年国勢調査の基本集計・"
          "2026年9月29日公表予定）まで出典つきで整理しました。確認日は%s。"
          % (latest["male"], latest["female"], latest["year"], CHECKED),
          "生涯未婚率の正式名称は50歳時未婚割合。最新は男性%.2f%%・女性%.2f%%で、毎年の値は存在しません。"
          % (latest["male"], latest["female"]),
          FAQ_MIKON, body, TODAY, CHECKED, PR_HEAD, PR_BODY)


FAQ_MIKON = [
 ("生涯未婚率の最新値は何%ですか？",
  "%s時点で男性%.2f%%・女性%.2f%%です。出典は国立社会保障・人口問題研究所『人口統計資料集2026』表6-23で、"
  "原資料は総務省統計局の国勢調査です。国勢調査は5年ごとのため、これが確認日時点の最新値になります。"
  "令和7年国勢調査の基本集計は2026年9月29日に公表予定で、そこで5年ぶりに更新されます。"
  % (MIKON["latest"]["year"], MIKON["latest"]["male"], MIKON["latest"]["female"])),
 ("生涯未婚率は「一生結婚しない人の割合」ですか？",
  "違います。50歳時点での未婚割合を示す指標で、50歳以降の結婚を排除していません。"
  "正式名称は「50歳時未婚割合」で、45〜49歳の未婚割合と50〜54歳の未婚割合を平均して算出します。"
  "「50歳の人の未婚率」でもない点にも注意が必要です。"),
 ("なぜ毎年の生涯未婚率が発表されないのですか？",
  "算出の元になる国勢調査が5年ごとに行われるためです。毎年の数字として紹介されているものは、"
  "別の統計にもとづく値か推計値である可能性があります。引用する際は、どの調査の何年の値かを"
  "必ず確認してください。"),
 ("男性と女性でなぜこれほど差があるのですか？",
  "本記事は公表値の整理を目的としているため、原因の解釈は行いません。数値としては、"
  "1980年は女性4.45%・男性2.60%と女性のほうが高く、1990年代に男女が逆転しました。"
  "その後は男性の上昇幅が大きく、2020年には男性が女性の約1.6倍になっています。"),
 ("今後、生涯未婚率はどうなりますか？",
  "50歳時未婚割合そのものの将来推計は公表されていません。関連する推計として、"
  "国立社会保障・人口問題研究所の『日本の世帯数の将来推計（令和6年推計）』では、"
  "15歳以上人口全体の未婚率が2020年の男性34.6%・女性24.8%から2050年に男性36.5%・女性27.1%になるとされています。"
  "65歳以上の単独世帯に占める未婚の割合はより大きく変化し、2050年に男性59.7%・女性30.2%と推計されています。"),
 ("2010年以前の数字とそのまま比べていいですか？",
  "注意が必要です。2015年と2020年の値は不詳補完値にもとづいて算出されており、"
  "それ以前の値と算出方法が完全には揃っていません。長期の推移を示すこと自体は問題ありませんが、"
  "小数点以下の差を厳密に比較する用途には向きません。"),
]


# =============================================================== 離婚率
def build_rikon():
    slug = "rikonritsu-data"
    latest = RIKON["latest"]
    kakutei = RIKON["latest_kakutei"]
    suii_rows = [(r["year"], "{:,}組".format(r["kensu"]), "%.2f" % r["per_1000"], r["kubun"])
                 for r in RIKON["suii"]]
    pref_rows = [(p["name"], "%.2f" % p["per_1000"],
                  ("%.1f" % p["konin_per_1000"]) if p.get("konin_per_1000") else "—")
                 for p in RIKON["todofuken"]]
    dk_rows = [(r["range"], "{:,}組".format(r["kensu"]),
                ("%.2f%%" % r["share"]) if r.get("share") is not None else "—",
                "{:,}組".format(r["kensu_2024"]) if r.get("kensu_2024") else "—")
               for r in RIKON["doukyo_kikan"]]
    jk = RIKON["jukunen_rikon"]

    body = """
<blockquote><strong>離婚率は%sの%.2f（人口千対）で、件数は%s組です。</strong>ピークだった%sの%s組からは大きく減っています。ただし「減っている」で終わらせると実態を取り違えます。総数が減るなかで、同居期間30年以上の離婚だけは前年より増えているためです。</blockquote>

<h2 id="latest">最新の離婚率と離婚件数</h2>
%s
<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a>（%s確認）。%s</p>
<p>離婚率は人口千人あたりの離婚件数で、分母は10月1日現在の日本人人口です。パーセントではない点に注意してください。</p>

<h2 id="suii">推移（直近11年）</h2>
%s
<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>

<h2 id="konin">婚姻件数・婚姻率との対比</h2>
<p>離婚率だけを見ると分母の人口も動くため、婚姻の側と並べて見るのが基本です。%sの婚姻件数は%s組・婚姻率%.1f（人口千対）で、%sでした。平均初婚年齢は夫%.1f歳・妻%.1f歳です。再婚の割合は夫%.1f%%・妻%.1f%%でした。</p>
<p class="srcline">%s</p>

<h2 id="pref">都道府県別の離婚率ランキング（47都道府県）</h2>
<p>最も高いのは%s（%.2f）、最も低いのは%s（%.2f）でした。全国は%.2fです。</p>
%s
<p class="srcline">%s 出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>

<h2 id="doukyo">同居期間別の離婚件数（いわゆる熟年離婚）</h2>
<p>同居期間20年以上の離婚は%s組で、離婚全体の%.2f%%を占めます。%s</p>
%s
<p class="srcline">%s 出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>

<h2 id="chui">数字を扱うときの注意</h2>
<h3>「概数」は後で変わる</h3>
<p>最新年の値は概数です。確定数は翌年に公表され、諸率は国勢調査人口で再計算されるため数値が変わる可能性があると厚生労働省が明記しています。引用する際は「概数」であることを添えてください。</p>
<h3>都道府県別は「別居する前の住所」で集計される</h3>
<p>%s現住所ではないため、その都道府県に現在住んでいる人の離婚率とは意味が違います。</p>
<h3>熟年離婚は実数ではなく構成比で見る</h3>
<p>離婚の総数が減っているため、同居期間の長い区分の実数が横ばいでも構成比は上がります。1985年の同居期間20年以上は20,434組で総数の12.26%%でしたが、%sには%s組・%.2f%%になっています。実数で約2倍、シェアで約1.8倍です。</p>

%s

<h2 id="faq">よくある質問（FAQ）</h2>
%s

%s
""" % (latest["year"], latest["per_1000"], "{:,}".format(latest["kensu"]),
       RIKON["saita_kensu"]["year"], "{:,}".format(RIKON["saita_kensu"]["kensu"]),
       table(["区分", "離婚件数", "離婚率（人口千対）"],
             [(latest["year"] + "（" + latest["kubun"] + "）",
               "{:,}組".format(latest["kensu"]), "%.2f" % latest["per_1000"]),
              (kakutei["year"] + "（" + kakutei["kubun"] + "）",
               "{:,}組".format(kakutei["kensu"]), "%.2f" % kakutei["per_1000"])],
             ["", "n", "n"]),
       latest["src"], latest["src_label"], CHECKED, latest["zennen_hikaku"],
       table(["年", "離婚件数", "離婚率", "区分"], suii_rows, ["", "n", "n", ""]),
       RIKON["suii_src"], RIKON["suii_src_label"],
       KONIN["latest"]["year"], "{:,}".format(KONIN["latest"]["kensu"]),
       KONIN["latest"]["per_1000"], KONIN["latest"]["note"],
       KONIN["heikin_shokon_nenrei"]["otto"], KONIN["heikin_shokon_nenrei"]["tsuma"],
       KONIN["saikon_wariai"]["otto"], KONIN["saikon_wariai"]["tsuma"],
       KONIN["heikin_shokon_nenrei"]["note"],
       RIKON["todofuken_top5"][0]["name"], RIKON["todofuken_top5"][0]["per_1000"],
       RIKON["todofuken_bottom5"][0]["name"], RIKON["todofuken_bottom5"][0]["per_1000"],
       latest["per_1000"],
       table(["都道府県", "離婚率（人口千対）", "婚姻率（人口千対）"], pref_rows, ["", "n", "n"]),
       RIKON["todofuken_note"], RIKON["todofuken_src"], RIKON["todofuken_src_label"],
       "{:,}".format(jk["20nen_ijou_kensu"]), jk["20nen_ijou_share"], jk["note"],
       table(["同居期間", "件数（最新）", "構成比", "前年（確定数）"], dk_rows, ["", "n", "n", "n"]),
       RIKON["doukyo_kikan_note"], RIKON["doukyo_kikan_src"], RIKON["doukyo_kikan_src_label"],
       RIKON["todofuken_note"],
       latest["year"], "{:,}".format(jk["20nen_ijou_kensu"]), jk["20nen_ijou_share"],
       RELATED_COMMON % (
           '<li><a href="/articles/shougai-mikonritsu-data/">生涯未婚率はいま何%？正式名称と最新値</a></li>\n'
           '<li><a href="/articles/tomobataraki-wariai-data/">共働き世帯の割合はどれくらい？</a></li>\n'
           '<li><a href="/articles/sango-rikon/">産後に離婚を考えたとき、先に確かめること</a></li>\n'
           '<li><a href="/tools/rikongo-seikatsuhi/">離婚後の生活費シミュレーション</a></li>'),
       faq_html(FAQ_RIKON),
       source_list(srcs("人口動態統計", "人口統計資料集2026")))

    write(slug,
          "離婚率はいまどれくらい？%s %.2f（人口千対）・%s組と都道府県別の実数"
          % (latest["year"], latest["per_1000"], "{:,}".format(latest["kensu"])),
          "離婚率はいまどれくらい？｜都道府県ランキングと同居期間別の実数",
          "離婚率は%sで%.2f（人口千対）、件数は%s組です。ピークの2002年28万9,836組からは大きく"
          "減っていますが、同居期間30年以上の離婚だけは前年より増えています。直近11年の推移、"
          "都道府県別の離婚率47件、同居期間別の件数と構成比、婚姻件数との対比を出典つきで整理しました。"
          "確認日は%s。" % (latest["year"], latest["per_1000"], "{:,}".format(latest["kensu"]), CHECKED),
          "離婚率は%.2f（人口千対）・%s組。減少傾向のなかで同居期間30年以上だけが増えています。"
          % (latest["per_1000"], "{:,}".format(latest["kensu"])),
          FAQ_RIKON, body, TODAY, CHECKED, PR_HEAD, PR_BODY)


FAQ_RIKON = [
 ("いまの離婚率はどれくらいですか？",
  "%sの離婚率は%.2f（人口千対）、離婚件数は%s組です（概数）。前年の確定数は%.2f・%s組でした。"
  "離婚率は人口千人あたりの件数であってパーセントではありません。"
  % (RIKON["latest"]["year"], RIKON["latest"]["per_1000"],
     "{:,}".format(RIKON["latest"]["kensu"]), RIKON["latest_kakutei"]["per_1000"],
     "{:,}".format(RIKON["latest_kakutei"]["kensu"]))),
 ("「3組に1組が離婚」というのは本当ですか？",
  "その年の離婚件数を婚姻件数で割った数字が根拠にされることがありますが、"
  "分子と分母が別の夫婦を指すため、実際に何組に1組が離婚するかを示すものではありません。"
  "最新年でいえば婚姻%s組に対し離婚%s組で、割ればおよそ2.7分の1になりますが、"
  "この計算で「結婚した人の何割が離婚する」とは言えません。"
  % ("{:,}".format(KONIN["latest"]["kensu"]), "{:,}".format(RIKON["latest"]["kensu"]))),
 ("離婚率が高い都道府県はどこですか？",
  "最新の概数では%s（%.2f）が最も高く、次いで%s（%.2f）、%s（%.2f）です。"
  "最も低いのは%s（%.2f）と%s（%.2f）でした。全国は%.2fです。"
  "なお都道府県別の離婚は「別居する前の住所」で集計されるため、現住所ベースではありません。"
  % (RIKON["todofuken_top5"][0]["name"], RIKON["todofuken_top5"][0]["per_1000"],
     RIKON["todofuken_top5"][1]["name"], RIKON["todofuken_top5"][1]["per_1000"],
     RIKON["todofuken_top5"][2]["name"], RIKON["todofuken_top5"][2]["per_1000"],
     RIKON["todofuken_bottom5"][-1]["name"], RIKON["todofuken_bottom5"][-1]["per_1000"],
     RIKON["todofuken_bottom5"][-2]["name"], RIKON["todofuken_bottom5"][-2]["per_1000"],
     RIKON["latest"]["per_1000"])),
 ("熟年離婚は増えているのですか？",
  "構成比では増えています。同居期間20年以上の離婚は1985年に20,434組（総数の12.26%%）でしたが、"
  "最新年は%s組（%.2f%%）です。実数で約2倍、シェアで約1.8倍になりました。"
  "最新年は同居期間30年以上の区分だけが前年より増加し、他の区分は減少しています。"
  "離婚の総数が減っているため、実数の増加が小さくても構成比は上がる点に注意してください。"
  % ("{:,}".format(RIKON["jukunen_rikon"]["20nen_ijou_kensu"]),
     RIKON["jukunen_rikon"]["20nen_ijou_share"])),
 ("協議離婚はどれくらいの割合ですか？",
  "%sの離婚%s組のうち協議離婚は162,682組で、全体の%.1f%%でした。"
  "調停・裁判による離婚は残りの1割強にとどまります。"
  % (RIKON["kyougi_rikon_wariai"]["year"],
     "{:,}".format(RIKON["latest_kakutei"]["kensu"]),
     RIKON["kyougi_rikon_wariai"]["value"])),
 ("最新の数字は確定値ですか？",
  "最新年の値は概数です。確定数は翌年に公表され、さらに諸率は国勢調査人口で再計算されるため"
  "数値が変わる可能性があると厚生労働省が明記しています。資料に引用する場合は「概数」であることと"
  "公表年月を添えてください。"),
]


# =============================================================== 共働き割合
def build_tomo():
    slug = "tomobataraki-wariai-data"
    latest = TOMO["latest"]
    suii = [r for r in TOMO["suii"] if int(r["year"][:4]) % 5 == 0]
    suii_rows = [(r["year"], "{:,}万世帯".format(r["kyoudou"]),
                  "{:,}万世帯".format(r["sengyou"]),
                  "%.2f倍" % (r["kyoudou"] / r["sengyou"]) if r["sengyou"] else "—")
                 for r in suii]
    keitai_rows = [(r["year"], "{:,}万世帯".format(r["fulltime"]),
                    "{:,}万世帯".format(r["part"])) for r in TOMO["shugyou_keitai_suii"]]
    sk = TOMO["seiki_koyou_hiritsu"]
    sk_rows = [(a["age"], "%.1f%%" % a["v"]) for a in sk["female"]]

    body = """
<blockquote><strong>共働き世帯は%sで%s万世帯、専業主婦世帯は%s万世帯で、比率は%.2f倍です。</strong>よく「1997年に逆転した」と言われますが、内閣府が現在公表している系列の実数では%sに共働きが初めて上回っています。この系列は「妻が64歳以下の雇用者世帯」に限った定義で、自営業の共働きは含みません。</blockquote>

<h2 id="latest">最新の共働き世帯数と専業主婦世帯数</h2>
%s
<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a>（%s確認）</p>

<h2 id="teigi">この数字が指しているもの</h2>
<p>%s</p>
<p>つまり、自営業やフリーランスの夫婦がともに働いている場合、この統計の「共働き世帯」には入りません。妻が65歳以上の世帯も対象外です。「共働きが何割か」を語るときは、どの定義の数字かを添える必要があります。</p>

<h2 id="gyakuten">「1997年に逆転」は現行の公表系列と合わない</h2>
<p>%s</p>
<p>1997年という年が広く引用されていますが、内閣府が現在公表しているCSVの実数には該当する系列が見当たりませんでした。記事や資料に書く場合は「妻が64歳以下・雇用者世帯の系列では1991年に初めて逆転」と、条件を添えるのが安全です。</p>

<h2 id="suii">推移（5年刻み）</h2>
%s
<p class="srcline">%s</p>
<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">同上</a></p>

<h2 id="keitai">共働きの中身：フルタイムとパート</h2>
<p>共働き世帯が増えたと言っても、内訳は一様ではありません。%sの共働き%s万世帯のうち、妻がフルタイム（週35時間以上）なのは%s万世帯、パート（週35時間未満）が%s万世帯です。増えたぶんの多くはパートが占めています。</p>
%s
<p class="srcline">%s 出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>

<h2 id="seiki">女性の年齢階級別 正規雇用比率</h2>
<p>%s</p>
%s
<p class="srcline">出典：<a href="%s" rel="noopener" target="_blank">%s</a></p>

<h2 id="chui">数字を扱うときの注意</h2>
<h3>就業時間の区分であって、正規・非正規ではない</h3>
<p>白書の内訳は週35時間以上か未満かという就業時間の区分で、雇用形態の区分ではありません。共働き世帯を正規・非正規で分けた世帯数は、この資料からは分かりません。</p>
<h3>2010年・2011年は3県を除く値</h3>
<p>%s</p>
<h3>他の統計と掛け合わせない</h3>
<p>共働き世帯数は労働力調査（標本調査）、婚姻・離婚件数は人口動態統計（届出の全数）、未婚割合は国勢調査（全数・5年ごと）から出ています。調査の設計が違うので、これらを掛け合わせて別の比率を作ることはできません。</p>

%s

<h2 id="faq">よくある質問（FAQ）</h2>
%s

%s
""" % (latest["year"], "{:,}".format(latest["kyoudou"]), "{:,}".format(latest["sengyou"]),
       latest["hi"], TOMO["gyakuten_year"],
       table(["区分", "世帯数"],
             [("共働き世帯（妻64歳以下・雇用者）", "{:,}万世帯".format(latest["kyoudou"])),
              ("専業主婦世帯（妻64歳以下）", "{:,}万世帯".format(latest["sengyou"])),
              ("比率", "%.2f倍" % latest["hi"])],
             ["", "n"]),
       latest["src"], latest["src_label"], CHECKED,
       TOMO["teigi"], TOMO["gyakuten_note"],
       table(["年", "共働き世帯", "専業主婦世帯", "比率"], suii_rows, ["", "n", "n", "n"]),
       TOMO["suii_note"], TOMO["suii_src"],
       latest["year"], "{:,}".format(latest["kyoudou"]),
       "{:,}".format(TOMO["shugyou_keitai"][0]["value"]),
       "{:,}".format(TOMO["shugyou_keitai"][1]["value"]),
       table(["年", "妻フルタイム（週35時間以上）", "妻パート（週35時間未満）"], keitai_rows, ["", "n", "n"]),
       TOMO["shugyou_keitai_note"], TOMO["shugyou_keitai_src"], TOMO["shugyou_keitai_src_label"],
       sk["note"],
       table(["年齢階級", "正規雇用比率（女性）"], sk_rows, ["", "n"]),
       sk["src"], sk["src_label"],
       TOMO["suii_note"],
       RELATED_COMMON % (
           '<li><a href="/articles/shougai-mikonritsu-data/">生涯未婚率はいま何%？正式名称と最新値</a></li>\n'
           '<li><a href="/articles/rikonritsu-data/">離婚率はいまどれくらい？件数・都道府県別・同居期間別</a></li>\n'
           '<li><a href="/articles/sango-kaji-buntan/">産後の家事分担はどう決めるか</a></li>\n'
           '<li><a href="/tools/seikatsuhi-simulator/">ふたりの生活費シミュレーション</a></li>'),
       faq_html(FAQ_TOMO),
       source_list(srcs("男女共同参画白書")))

    write(slug,
          "共働き世帯の割合は？%s万世帯 対 専業主婦%s万世帯（%s・%.2f倍）"
          % ("{:,}".format(latest["kyoudou"]), "{:,}".format(latest["sengyou"]),
             latest["year"], latest["hi"]),
          "共働き世帯の割合はどれくらい？｜専業主婦世帯との比較と、増えたのはどちらか",
          "共働き世帯は%sで%s万世帯、専業主婦世帯は%s万世帯で%.2f倍です。よく言われる"
          "「1997年に逆転」は内閣府の現行公表系列と合わず、実数では1991年に初めて上回っています。"
          "40年の推移、妻のフルタイムとパートの内訳、女性の年齢階級別の正規雇用比率まで出典つきで"
          "整理しました。この統計は妻が64歳以下の雇用者世帯に限った定義である点も明記しています。確認日は%s。"
          % (latest["year"], "{:,}".format(latest["kyoudou"]),
             "{:,}".format(latest["sengyou"]), latest["hi"], CHECKED),
          "共働き%s万世帯 対 専業主婦%s万世帯で%.2f倍。増えたぶんの多くはパートです。"
          % ("{:,}".format(latest["kyoudou"]), "{:,}".format(latest["sengyou"]), latest["hi"]),
          FAQ_TOMO, body, TODAY, CHECKED, PR_HEAD, PR_BODY)


FAQ_TOMO = [
 ("共働き世帯は全体の何割ですか？",
  "内閣府『男女共同参画白書 令和7年版』の系列では、%sの共働き世帯は%s万世帯、"
  "専業主婦世帯は%s万世帯で、両者の合計に占める共働きの割合は約%.0f%%です。"
  "ただしこの系列は「妻が64歳以下で夫婦ともに非農林業の雇用者」に限った定義で、"
  "自営業の共働きや妻が65歳以上の世帯は含みません。"
  % (TOMO["latest"]["year"], "{:,}".format(TOMO["latest"]["kyoudou"]),
     "{:,}".format(TOMO["latest"]["sengyou"]),
     100.0 * TOMO["latest"]["kyoudou"] / (TOMO["latest"]["kyoudou"] + TOMO["latest"]["sengyou"]))),
 ("共働き世帯と専業主婦世帯はいつ逆転したのですか？",
  "内閣府が現在公表しているCSVの実数では1991年です。1991年に共働き871万世帯が"
  "専業主婦864万世帯を初めて上回り、1995年に一度だけ再逆転したあと、1996年以降は"
  "一貫して共働きが上回っています。「1997年に逆転」という表現が広く使われていますが、"
  "現行の公表系列には該当する年が見当たりません。"),
 ("共働きが増えたのはフルタイムですか、パートですか？",
  "パートです。%sの共働き%s万世帯のうち、妻がフルタイム（週35時間以上）は%s万世帯、"
  "パート（週35時間未満）は%s万世帯でした。1985年はフルタイム461万・パート228万だったので、"
  "パートの伸びが大きいことが分かります。なおこの区分は就業時間であって、正規・非正規の"
  "雇用形態の区分ではありません。"
  % (TOMO["latest"]["year"], "{:,}".format(TOMO["latest"]["kyoudou"]),
     "{:,}".format(TOMO["shugyou_keitai"][0]["value"]),
     "{:,}".format(TOMO["shugyou_keitai"][1]["value"]))),
 ("正規・非正規で分けた共働き世帯数はありますか？",
  "本記事で使った内閣府『男女共同参画白書』には、共働き世帯を正規・非正規で分けた世帯数の"
  "図表がありません。掲載されているのは就業時間別（週35時間以上／未満）の区分です。"
  "総務省『労働力調査（詳細集計）』の世帯編に関連する表がある見込みですが、"
  "確認日時点で実数を確認できていないため、本記事には掲載していません。"),
 ("女性の正規雇用比率はどう変化しますか？",
  "年齢階級で大きく変わります。令和6年の値では25〜29歳の60.3%%がピークで、"
  "30〜34歳で51.6%%、45〜49歳では36.6%%まで下がります。いわゆるL字カーブと呼ばれる形です。"
  "ただしこの数値の母数は全女性であり、共働き世帯の妻に限った値ではありません。"),
 ("この数字を他の統計と組み合わせて使えますか？",
  "組み合わせないでください。共働き世帯数は労働力調査（標本調査・世帯単位）、"
  "婚姻件数や離婚件数は人口動態統計（届出の全数）、未婚割合は国勢調査（全数・5年ごと）から"
  "出ています。調査の設計と母集団が違うため、掛け合わせて別の比率を作ると意味のない数字になります。"),
]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build_mikon()
    build_rikon()
    build_tomo()

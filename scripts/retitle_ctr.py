# -*- coding: utf-8 -*-
"""4〜10位にいるのにクリックが出ていないページのタイトルを直す（2026-08-29）

なぜ必要か:
GSC実測（直近14日）で 4〜10位の表示659に対しクリックは18。うち234表示ぶんの
ページがクリック0だった。順位は取れているのに押されていない＝順位ではなく
看板（title / description）の問題である可能性が高い。

**ただし表示数が10〜39と小さく、CTR 0 は統計的に強い証拠ではない。**
（8位の期待CTRを2〜3%とすると39表示で期待クリックは約1。0でも異常ではない）
なので「CTRが低いから直す」ではなく、**検索語とタイトルが噛み合っていない・
記事が持っている数字がタイトルに出ていない**という、内容から説明できる
ものだけを直す。効果は9/12以降のGSCで検証する。

直す根拠（1本ずつ）:
- with-seriousness-data … 検索語は「with 結婚率」（21表示・7位）なのに
  タイトルに「結婚率」の語が無く「真剣度」になっていた。語の不一致。
- with-nenreiso-data … 検索語「with 年齢層」（30表示）。記事の結論は
  「年齢別内訳は非公表・公表は会員数1,500万人のみ」だが、タイトルが
  「根拠を公表データで確認する」と曖昧で、答えが見えない。
- pairs-marriage-data … 記事の結論は「成婚率は非公表、公表は毎月約13,000人に
  恋人のみ」。タイトルの「本当に結婚できるのか公式数値で検証」は中身を表さない。
- kekkon-madeno-kikan-data … 記事の中心的な数字 2.8年（第16回出生動向基本調査）が
  タイトルに無い。
- success-rate-data / mens-make-konkatsu / hoikuen-tensu-nerima …
  タイトルが45〜49字でSERPで途中で切れる。前半に結論を寄せる。

タイトルは全角30〜35字を目安にする（それ以上は検索結果で省略される）。
**記事にない数字は書かない。** 上の数字はすべて記事本文から確認済み。
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIX = {
 "articles/with-seriousness-data": (
   "withの結婚率は公表されていない｜代わりに確認できる数字を整理した",
   "withの結婚率・成婚率は2026年7月時点で非公表。Pairsが「毎月約13,000人に恋人」と出しているのに対し、withは定量的な成果データを発表していない。公表されている会員数1,500万人と料金体系から、婚活に使えるかを判断する材料を整理しました。"),
 "articles/with-nenreiso-data": (
   "withの年齢層は非公表だった｜公表値は会員数1,500万人のみ",
   "「withは20代向け」とよく言われるが、年齢別の会員数内訳は公表されていない。公表値は累計会員数1,500万人のみで、男女比もアクティブ数も非公表。何が分かって何が分からないのかを、出典つきで分けて整理しました。"),
 "articles/pairs-marriage-data": (
   "ペアーズの成婚率は非公表｜公表は「毎月約13,000人に恋人」だけ",
   "ペアーズが公表しているのは「毎月約13,000人に恋人ができている」の一点で、成婚率も累計マッチング数も非公表。年間に換算すると約15万6,000人という計算になる。この数字が何を数えたものかと、婚活目的で使うときの判断材料を整理しました。"),
 "articles/kekkon-madeno-kikan-data": (
   "アプリ婚の交際期間は平均2.8年｜恋愛結婚4.9年との差はどこから来るか",
   "第16回出生動向基本調査では、ネットで知り合った夫婦の平均交際期間は2.8年。従来の恋愛結婚4.9年より2年以上短い。「平均12〜18ヶ月」という数字に公的な裏付けはなく、アプリ別・年代別の期間は各社とも公表していません。"),
 "articles/success-rate-data": (
   "マッチングアプリの結婚率｜婚活目的45.2%と登録者全体2〜4%の違い",
   "マッチングアプリの結婚率は、婚活目的の利用者で45.2%、登録者全体では約2〜4%。同じ「結婚率」でも分母が違う。ブライダル総研・こども家庭庁・MMD研究所の公表データと、各社が公表していない数字を分けて整理しました。"),
 "articles/mens-make-konkatsu": (
   "婚活写真のメンズメイク｜BBクリーム1本で青髭とクマを消す",
   "青髭・クマ・ニキビ跡をBBクリーム1本でカバーする、婚活・マッチングアプリ写真のためのメンズメイク入門。「メイクは抵抗がある」という男性向けに、バレない塗り方・アイテム比較・撮影当日の使い方まで実用的に解説します。"),
 "tools/hoikuen-tensu-nerima": (
   "練馬区の保育園 点数計算｜あなたの指数で入れた園が分かる",
   "練馬区の保育園入園の指数を区公式の保育実施基準表（令和8年度版）で計算し、令和8年4月1次利用調整の園別最低指数と照合。あなたの点数で内定が出ていた園を、地区×年齢クラスで逆引きします。無料・登録不要。"),
 # 2026-08-29 追加（CEO指示・Nは凍結中だが既存記事の看板直しは拡張に当たらない）:
 # クエリは指名系が7〜11位（ミトコア/怪しい/効果）なのにクリック0。
 # 記事の結論＝医薬品ではなく効果効能は薬機法上標榜できない・月2万円前後、を前面に。
 "articles/mitocore-kuchikomi": (
   "ミトコア300mgは月2万円前後｜「効果」を誰も謳えない理由と成分の事実",
   "ミトコア300mgは医薬品ではなく栄養補助食品で、「妊娠率が上がる」といった効果効能は薬機法上、誰も標榜できません。独自素材イースタティックミネラルの中身、夫婦利用で月2万円前後になり得る価格、口コミの読み方を、公式の公開情報だけで整理しました。"),
 "articles/kekkon-okane-data": (
   "結婚にかかるお金の総額｜婚約から新生活までを段階別に見える化",
   "婚約指輪・結婚式・新婚旅行・新生活まで、結婚にかかる費用の総額を公開データで見える化。実際の自己負担額と、段階ごとに削れる項目・削れない項目を分けて整理しました。"),
}


def main(apply_):
    n = 0
    for path, (title, desc) in sorted(FIX.items()):
        f = os.path.join(ROOT, path, "index.html")
        if not os.path.exists(f):
            print("  なし:", path); continue
        h = io.open(f, encoding="utf-8").read()
        old_t = re.search(r"<title>(.*?)</title>", h, re.S)
        old_t = old_t.group(1).strip() if old_t else ""
        full = title + "｜Noe結婚設計室" if "Noe" not in title else title
        h2 = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, h, count=1, flags=re.S)
        h2 = re.sub(r'(<meta name="description" content=")[^"]*(")',
                    lambda m: m.group(1) + desc + m.group(2), h2, count=1)
        # OGP / Twitter も揃える
        h2 = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                    lambda m: m.group(1) + title + m.group(2), h2, count=1)
        h2 = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
                    lambda m: m.group(1) + desc + m.group(2), h2, count=1)
        h2 = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")',
                    lambda m: m.group(1) + title + m.group(2), h2, count=1)
        print("  %-38s %2d字→%2d字" % (path.split("/")[-1][:38], len(old_t), len(title)))
        if apply_ and h2 != h:
            io.open(f, "w", encoding="utf-8").write(h2); n += 1
    print("\n更新: %d本" % n if apply_ else "\n--apply で適用")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main("--apply" in sys.argv)

# -*- coding: utf-8 -*-
"""Googleキーワードプランナーに投入する語のリストを作る（2026-08-28 新設・**現在は棚上げ**）

★2026-08-28 CEO判断で棚上げ。9月中旬のバンク初動判定が出るまで使わないこと。
理由: 8/27に「判定まで変数を増やさない」と決めた直後にこれを作り始めてしまった。
道具を増やすこと自体が変数になる。判定が出て、器具＋データ記事の型が伸びると
確認できてから、次にどの語を厚くするかを決める段階で使う。


なぜこれが要るか（2026-08-27の実測）:
語の形ごとに1ページ目率がまるで違う。
- 固有名詞×指標（with 結婚率／ペアーズ 成婚率／ガルガル期 診断）… 22語中8語が1ページ目＝36%
- 一般語（看護師 婚活／50代 婚活サイト）… 239語中6語＝2.5%
**同じ労力で勝率が14倍違う。** だから一般語のボリュームを調べても意味が薄い。
知りたいのは「固有名詞×指標のうち、どれが大きいか」だけ。

キーワードプランナーは無料アカウントだと範囲表示（例「1万〜10万」）になるが、
**桁が分かれば十分**。器具に載せる順番を決めるのが目的で、精密な数字は要らない。

出力する2本のリスト:
  A. 実測の需要リスト … GSCで21位以下だが表示が出ている語（＝需要はあるが取れていない）
  B. 固有名詞×指標の候補 … 収録済みのサービス名 × 指標語の総当たり

使い方:
  python scripts/kwplanner_seeds.py         # agent/kwplanner_seeds_A.txt / _B.txt を書く
  python scripts/kwplanner_seeds.py --show  # 中身を表示するだけ
"""
import datetime
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY = r"C:\Users\tatsu\matching-app\secrets\noe-gsc-key.json"
SITE = "https://www.noe-match.com/"

# 収録済みのサービス名。表記ゆれは実際に検索される形で入れる。
SERVICES = [
    "ペアーズ", "with", "Omiai", "タップル", "マリッシュ", "ユーブライド",
    "ブライダルネット", "Tinder", "ゼクシィ縁結び",
    "IBJメンバーズ", "パートナーエージェント", "ツヴァイ", "オーネット",
    "サンマリエ", "naco-do", "スマリッジ", "ムスベル", "フィオーレ",
    "ゼクシィ縁結びエージェント", "エクセレンス青山",
]

# 指標語。「固有名詞×これ」で1ページ目に入りやすい形になる。
INDICATORS = [
    "料金", "費用", "成婚率", "会員数", "年齢層", "口コミ", "評判",
    "退会", "解約", "比較", "やめとけ", "デメリット", "アプリ内課金",
    "女性 無料", "成婚料", "入会金", "月会費",
]

# 自治体バンク側。こちらは固有名詞＝制度名で、指標が付くと勝ちやすい。
SEIDO = [
    "子ども医療費助成", "病児保育", "産後ケア", "こども誰でも通園制度",
    "不妊治療 助成", "育児休業給付金", "出産育児一時金",
]
SEIDO_IND = ["いつまで", "料金", "いくら", "東京23区", "所得制限", "申請", "予約", "対象"]


def gsc_demand():
    """GSCで21位以下だが表示が出ている語＝需要の実測証拠を取る"""
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession
    creds = service_account.Credentials.from_service_account_file(
        KEY, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    s = AuthorizedSession(creds)
    end = datetime.date.today() - datetime.timedelta(days=2)
    d0 = end - datetime.timedelta(days=89)      # 90日ぶんで語を厚めに拾う
    import urllib.parse
    r = s.post("https://www.googleapis.com/webmasters/v3/sites/%s/searchAnalytics/query"
               % urllib.parse.quote(SITE, safe=""),
               json={"startDate": str(d0), "endDate": str(end),
                     "dimensions": ["query"], "rowLimit": 5000})
    if r.status_code != 200:
        print("GSC取得に失敗:", r.status_code, r.text[:120])
        return []
    rows = r.json().get("rows", [])
    deep = [x for x in rows if x["position"] > 20]
    deep.sort(key=lambda x: -x["impressions"])
    return [(x["keys"][0], x["impressions"], x["position"]) for x in deep]


def cross():
    out = []
    for s in SERVICES:
        for i in INDICATORS:
            out.append("%s %s" % (s, i))
    for s in SEIDO:
        for i in SEIDO_IND:
            out.append("%s %s" % (s, i))
    return out


def main():
    show = "--show" in sys.argv
    os.chdir(REPO)

    A = gsc_demand()
    B = cross()

    pa = "agent/kwplanner_seeds_A.txt"
    pb = "agent/kwplanner_seeds_B.txt"
    if not show:
        io.open(pa, "w", encoding="utf-8").write("\n".join(q for q, _, _ in A) + "\n")
        io.open(pb, "w", encoding="utf-8").write("\n".join(B) + "\n")

    print("A. 実測の需要リスト（GSC 90日・21位以下で表示あり）: %d 語" % len(A))
    for q, imp, pos in A[:10]:
        print("   %-34s 表示%4d 順位%5.1f" % (q[:34], imp, pos))
    print("   ...")
    print("\nB. 固有名詞×指標の候補（総当たり）: %d 語" % len(B))
    for q in B[:6]:
        print("   %s" % q)
    print("   ...")
    if not show:
        print("\n書き出し: %s / %s" % (pa, pb))
        print("キーワードプランナーの「検索のボリュームと予測のデータを確認する」に貼る。")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

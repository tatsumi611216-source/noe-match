# -*- coding: utf-8 -*-
"""Googleキーワードプランナーに投入する語のリストを作る（2026-08-28 新設）

★2026-08-28 一度棚上げにしたが、同日に判断を撤回して稼働させた。
撤回の理由: キーワードプランナーは読み取り専用で、サイトに一切触れない。
「変数を増やさない」が指しているのは**サイトを変えること**（新規ページ・既存改稿・
CTA変更・内部リンク）であって、外部で数字を調べる行為は9月の判定を汚さない。
最初に「新しい道具＝変数」とひとくくりにしたのが誤りだった。

むしろ判定より先に知る価値がある。いちばん良い順位のページ（ガルガル期 診断・8位）でも
表示は月32回しかない。**固有名詞×指標という空間そのものの大きさが未知**で、
もし全部がこの規模なら、判定が「型は効く」と出ても目標額には届かない。
それは判定の後より前に知るほうがいい。

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

# 収録済みのサービス名。アプリと相談所で付く指標が違うので分ける。
# 総当たりにすると「IBJメンバーズ アプリ内課金」のような存在しない語ができて、
# 調査枠を無駄にするうえ結果が読みにくくなる。
APPS = ["ペアーズ", "with", "Omiai", "タップル", "マリッシュ", "ユーブライド",
        "ブライダルネット", "Tinder", "ゼクシィ縁結び"]
APP_IND = ["料金", "費用", "女性 無料", "アプリ内課金", "月額", "会員数", "年齢層",
           "口コミ", "評判", "退会", "解約", "成婚率", "結婚率", "やめとけ", "デメリット"]

SOUDANJO = ["IBJメンバーズ", "パートナーエージェント", "ツヴァイ", "オーネット",
            "サンマリエ", "naco-do", "スマリッジ", "ムスベル", "フィオーレ",
            "ゼクシィ縁結びエージェント", "エクセレンス青山"]
SOU_IND = ["料金", "費用", "成婚率", "成婚料", "入会金", "月会費", "会員数",
           "口コミ", "評判", "途中解約", "返金", "やめとけ", "デメリット", "比較"]

# 制度側。制度ごとに意味の通る指標だけを組む。
SEIDO = {
    "子ども医療費助成": ["いつまで", "東京23区", "所得制限", "対象", "引っ越し", "高校生", "入院 食事代"],
    "病児保育": ["料金", "いくら", "東京23区", "予約", "当日", "事前登録", "対象年齢", "減免"],
    "産後ケア": ["料金", "いくら", "何回", "東京23区", "申し込み", "宿泊型", "助成", "非課税世帯"],
    "こども誰でも通園制度": ["料金", "いくら", "予約", "何時間", "対象", "いつから", "申し込み"],
    "不妊治療 助成": ["いくら", "東京23区", "所得制限", "申請", "先進医療", "対象", "上限"],
    "育児休業給付金": ["いくら", "計算", "延長", "上限額", "いつから", "67%", "50%"],
    "出産育児一時金": ["いくら", "申請", "直接支払制度", "差額", "50万円", "対象"],
}


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
    """固有名詞×指標の候補。重複は落とし、投入順は勝ち筋の濃い順にする。"""
    out = []
    for s in APPS:
        out += ["%s %s" % (s, i) for i in APP_IND]
    for s in SOUDANJO:
        out += ["%s %s" % (s, i) for i in SOU_IND]
    for s, inds in SEIDO.items():
        out += ["%s %s" % (s, i) for i in inds]
    seen, uniq = set(), []
    for x in out:
        if x not in seen:
            seen.add(x); uniq.append(x)
    return uniq


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

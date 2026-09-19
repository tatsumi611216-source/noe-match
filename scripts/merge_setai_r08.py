# -*- coding: utf-8 -*-
"""共働き世帯・専業主婦世帯の正本を作る（2026-09-19 新設）

入力: scripts/data/src/gender_r08_zuhyo00-05.csv（特-5図）
      scripts/data/src/gender_r08_zuhyo00-06.csv（特-6図）
      いずれも内閣府男女共同参画局『男女共同参画白書 令和8年版』のCSVを2026-09-19に取得したもの。
出力: scripts/data/setai_kyoudou_sengyou.json

なぜ別ファイルにしたか:
既存の scripts/data/kon_rikon_tomobataraki.json は令和7年版（最新値2024年）で、
/articles/tomobataraki-wariai-data/ の正本になっている。同記事は 10/13 まで判定ロック中なので、
正本を書き換えて再生成の結果を変えることはしない。令和8年版（最新値2025年）はこちらに置き、
ロック明けに既存記事をこちらへ寄せるかどうかは別途判断する。

検算（合わなければ書き出さない）:
  1. 1985〜2024年の全国値が、既存正本（令和7年版）の値と全年一致すること
  2. 各年で 共働き世帯数 −（パート＋フルタイム）が -2〜+40万世帯に収まること
     （内訳の合計は総数に一致しない年がある。差は naiyaku_gap として正本に残す）
  3. 白書本文が書いている5年ごとの増減率（専業主婦 -18.3/-22.6/-23.2％、共働き +9.0/+9.8/+6.3％）が
     CSVの値から再現できること
"""
import csv
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC5 = os.path.join(HERE, "data", "src", "gender_r08_zuhyo00-05.csv")
SRC6 = os.path.join(HERE, "data", "src", "gender_r08_zuhyo00-06.csv")
OLD = os.path.join(HERE, "data", "kon_rikon_tomobataraki.json")
OUT = os.path.join(HERE, "data", "setai_kyoudou_sengyou.json")

CHECKED = "2026年9月19日"
BASE = "https://www.gender.go.jp/about_danjo/whitepaper/r08/zentai/html/honpen/"


def read_csv(path):
    raw = io.open(path, "rb").read()
    for enc in ("utf-8-sig", "cp932"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    return list(csv.reader(io.StringIO(text)))


def year_of(label):
    m = re.search(r"（(\d{4})）年", label)
    return int(m.group(1)) if m else None


def num(s):
    s = (s or "").strip()
    return int(s) if s else None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows5 = read_csv(SRC5)
    rows6 = read_csv(SRC6)
    assert "特－５図" in rows5[0][0] or "特－5図" in rows5[0][0], rows5[0][0]
    assert "特－６図" in rows6[0][0] or "特－6図" in rows6[0][0], rows6[0][0]
    # 列の並びを見出しで確かめる（令和7年版と令和8年版で列順が違う）
    h5 = rows5[2]
    assert "無業の妻" in h5[1] and "除く" not in h5[1], h5
    assert "共働き" in h5[2] and "除く" not in h5[2], h5
    assert "無業の妻" in h5[3] and "除く" in h5[3], h5
    assert "共働き" in h5[4] and "除く" in h5[4], h5
    h6 = rows6[2]
    assert "パート" in h6[1] and "フルタイム" in h6[2], h6

    series = {}
    for r in rows5[3:]:
        y = year_of(r[0]) if r else None
        if not y:
            continue
        series[y] = {"year": y, "sengyou": num(r[1]), "kyoudou": num(r[2]),
                     "sengyou_excl3": num(r[3]), "kyoudou_excl3": num(r[4])}
    for r in rows6[3:]:
        y = year_of(r[0]) if r else None
        if not y:
            continue
        series[y]["part"] = num(r[1])
        series[y]["fulltime"] = num(r[2])
        series[y]["part_excl3"] = num(r[3])
        series[y]["fulltime_excl3"] = num(r[4])

    years = sorted(series)
    assert years[0] == 1985 and years[-1] == 2025 and len(years) == 41, (years[0], years[-1], len(years))

    # 検算1: 令和7年版の正本と全年一致
    old = json.load(io.open(OLD, encoding="utf-8"))["tomobataraki"]["suii"]
    for o in old:
        y = int(o["year"][:4])
        assert series[y]["sengyou"] == o["sengyou"], ("sengyou", y)
        assert series[y]["kyoudou"] == o["kyoudou"], ("kyoudou", y)

    # 検算2: パート＋フルタイム ≒ 共働き
    for y in years:
        s = series[y]
        if s["kyoudou"] is not None:
            gap = s["kyoudou"] - s["part"] - s["fulltime"]
            # 1985年だけ内訳の合計が総数より29万世帯小さい（ほかの年は±3万世帯以内）。
            # 内訳が総数を大きく超える・大きく欠けるなら列の読み違いなので止める。
            assert -2 <= gap <= 40, (y, s)
            s["naiyaku_gap"] = gap

    # 検算3: 白書本文の5年増減率
    def rate(key, a, b):
        return round((series[b][key] - series[a][key]) * 100.0 / series[a][key], 1)
    assert [rate("sengyou", 2010, 2015), rate("sengyou", 2015, 2020), rate("sengyou", 2020, 2025)] == [-18.3, -22.6, -23.2]
    assert [rate("kyoudou", 2010, 2015), rate("kyoudou", 2015, 2020), rate("kyoudou", 2020, 2025)] == [9.0, 9.8, 6.3]

    out = {
        "checked": CHECKED,
        "edition": "内閣府男女共同参画局『男女共同参画白書 令和8年版』（令和8年7月）",
        "unit": "万世帯",
        "teigi": {
            "sengyou": "男性雇用者と無業の妻から成る世帯（妻64歳以下）。夫が非農林業雇用者で、妻が非就業者の世帯。白書の図表名ではこれを「専業主婦世帯」と呼んでいる。",
            "kyoudou": "雇用者の共働き世帯（妻64歳以下）。夫婦ともに非農林業雇用者（非正規の職員・従業員を含む）の世帯。",
            "fukumanai": "自営業・農林業の世帯、妻が65歳以上の世帯、夫が雇用者でない世帯は、どちらにも入らない。",
            "teigi_src": "定義の文言は令和7年版 特-I図の備考による（令和8年版 特-5図は同じ表題・同じ系列で、1985〜2024年の値が全年一致することを確認済み）。",
        },
        "chousa": "1985〜2001年は総務庁『労働力調査特別調査』（各年2月）、2002年以降は総務省『労働力調査（詳細集計）』。調査方法・調査月が異なるため、時系列比較には注意を要する（令和7年版 特-I図の備考）。",
        "y2011": "2011年は東日本大震災の影響で全国値がなく、岩手県・宮城県・福島県を除く値のみが公表されている。2010年は全国値と3県を除く値の両方がある。",
        "whitepaper_rates": {
            "sengyou": {"2010-2015": -18.3, "2015-2020": -22.6, "2020-2025": -23.2},
            "kyoudou": {"2010-2015": 9.0, "2015-2020": 9.8, "2020-2025": 6.3},
            "src": BASE + "b1_s00_01.html",
            "src_label": "同白書 特集 第1節（本文）",
        },
        "series": [series[y] for y in years],
        "sources": [
            {"url": BASE + "csv/zuhyo00-05.csv",
             "label": "内閣府男女共同参画局『男女共同参画白書 令和8年版』特-5図 共働き世帯数と専業主婦世帯数の推移（妻が64歳以下の世帯）CSV"},
            {"url": BASE + "csv/zuhyo00-06.csv",
             "label": "内閣府男女共同参画局『男女共同参画白書 令和8年版』特-6図 妻の就業時間別共働き世帯数の推移（妻が64歳以下の世帯）CSV"},
            {"url": BASE + "b1_s00_01.html",
             "label": "内閣府男女共同参画局『男女共同参画白書 令和8年版』特集 第1節（特-5図・特-6図の掲載ページ）"},
            {"url": "https://www.gender.go.jp/about_danjo/whitepaper/r07/zentai/html/honpen/csv/zuhyo00-op01.csv",
             "label": "内閣府男女共同参画局『男女共同参画白書 令和7年版』特-I図 CSV（定義・備考と1985〜2024年の照合に使用）"},
        ],
        "unconfirmed": [
            "妻の年代別（30代・40代など）の専業主婦世帯の割合：この系列は妻64歳以下の合計のみで、年代別の内訳は無い。",
            "全世帯（単独世帯・高齢世帯などを含む）に占める専業主婦世帯の割合：この系列からは計算できない。",
            "正規・非正規別の共働き世帯数：白書の区分は就業時間（週35時間以上／未満）で、雇用形態ではない。",
            "都道府県別の値：この図表は全国値のみ。",
        ],
    }
    io.open(OUT, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
    print("written:", OUT, len(years), "years / latest", series[2025])


if __name__ == "__main__":
    main()

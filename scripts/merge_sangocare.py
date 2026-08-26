# -*- coding: utf-8 -*-
"""実査エージェントが書き出した産後ケアのJSONを _sangocare_data.py にまとめる。

こども誰でも通園制度で確立した手順（merge_daretsu_cities.py）と同じ考え方。
手でデータを書き写さないことで、転記ミスと数字のズレを防ぐ。

料金の「数え方」は自動判定しない。実査結果を1件ずつ読んで BASIS に確定させる。
8/25の教訓（正規表現が減免の「生活保護世帯は無料」を無償と誤読した）に加え、
産後ケアでは自治体ごとに次の3通りが混在していることが実査で分かったため:

  trip … 「1泊2日でいくら、以降1日ごとにいくら」（江戸川・板橋・練馬・杉並・世田谷・江東）
  day  … 「1日あたりいくら」。1泊2日＝2日ぶん課金（足立・大田・北・豊島・渋谷・中野）
  range… 施設ごとに実額が違い、自治体としての単価が存在しない（荒川・台東・港・新宿ほか）

range を無理に1つの数字にすると、金額を最大3倍以上取り違える。計算に使わず
レンジのまま出す。

使い方: python scripts/merge_sangocare.py [--dry]
"""
import io
import json
import os
import sys

SRC_DIR = (r"C:\Users\tatsu\AppData\Local\Temp\claude\C--Users-tatsu"
           r"\9bb7063f-23b1-4fdd-9750-dfa305ab85e1\scratchpad\sangocare")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_sangocare_data.py")
CHECKED = "2026年8月27日"

# 実査結果の本文を1件ずつ読んで確定させた（2026-08-27）。
#   stay : (基準, 初回, 追加1日あたり)  基準は trip / day / range
#   day  : 1回（1日）あたりの額。None＝自治体としての単価が無い（施設別）
#   visit: 同上。"none"＝その類型を実施していない（施設別変動と区別する）
BASIS = {
    "chiyoda":    {"stay": ("range", None, None), "day": None,  "visit": 1000},
    "chuo":       {"stay": ("range", None, None), "day": None,  "visit": None},
    "minato":     {"stay": ("range", None, None), "day": None,  "visit": None},
    "shinjuku":   {"stay": ("range", None, None), "day": None,  "visit": 1000},
    "bunkyo":     {"stay": ("range", None, None), "day": 3000,  "visit": 3000},
    "taito":      {"stay": ("range", None, None), "day": None,  "visit": None},
    "sumida":     {"stay": ("range", None, None), "day": None,  "visit": 1000},
    "koto":       {"stay": ("trip", 9800, 4900),  "day": 3500,  "visit": 1200},
    "shinagawa":  {"stay": ("range", None, None), "day": None,  "visit": 0},
    "meguro":     {"stay": ("range", None, None), "day": 2500,  "visit": 1000},
    "ota":        {"stay": ("day", 2500, None),   "day": 1500,  "visit": 500},
    "setagaya":   {"stay": ("trip", 9000, 4500),  "day": 3000,  "visit": 2000},
    "shibuya":    {"stay": ("day", 3500, None),   "day": 2000,  "visit": 1000},
    "nakano":     {"stay": ("day", 3000, None),   "day": 1000,  "visit": 2000},
    "suginami":   {"stay": ("trip", 7000, 3500),  "day": None,  "visit": "none"},
    "toshima":    {"stay": ("day", 2500, None),   "day": 1500,  "visit": 1000},
    "kita":       {"stay": ("day", 3300, None),   "day": 2500,  "visit": 1000},
    "arakawa":    {"stay": ("range", None, None), "day": None,  "visit": None},
    "itabashi":   {"stay": ("trip", 8000, 4000),  "day": 2000,  "visit": 600},
    "nerima":     {"stay": ("trip", 7000, 3500),  "day": 1500,  "visit": 500},
    "adachi":     {"stay": ("day", 2500, None),   "day": 1250,  "visit": 1000},
    "katsushika": {"stay": ("day", 0, None),      "day": 0,     "visit": 0},
    "edogawa":    {"stay": ("trip", 7000, 3500),  "day": 3000,  "visit": 2000},
}

# 23区の並び（公式の区順）
ORDER = ["chiyoda", "chuo", "minato", "shinjuku", "bunkyo", "taito", "sumida",
         "koto", "shinagawa", "meguro", "ota", "setagaya", "shibuya", "nakano",
         "suginami", "toshima", "kita", "arakawa", "itabashi", "nerima",
         "adachi", "katsushika", "edogawa"]

HEAD = '''# -*- coding: utf-8 -*-
"""産後ケア事業の自治体データ（ツールと記事の共通の正本）

各自治体の公式ページを一次確認して作成。金額は原文どおり。
stay_basis は料金の数え方: trip=「1泊2日＋以降1日ごと」/ day=「1日あたり」/
range=「施設ごとに違い自治体としての単価が無い」。range は計算に使わない。
day・visit が None のものも施設別で単価が存在しない（labelに幅を記載）。
自動生成: python scripts/merge_sangocare.py
"""
CHECKED = "%s"

CITIES = [
''' % CHECKED

TAIL = ''' {"key": "kokuhyo", "name": "上記以外の自治体（目安）", "group": "国基準",
  "stay": None, "stay_basis": "range", "stay_add": None,
  "stay_label": "自治体ごとに設定", "day": None, "day_label": "自治体ごとに設定",
  "visit": None, "visit_avail": True, "visit_label": "自治体ごとに設定",
  "day_avail": True,
  "limit_stay": "自治体ごとに設定", "limit_day": "自治体ごとに設定",
  "limit_visit": "自治体ごとに設定",
  "genmen": "住民税非課税世帯・生活保護世帯の減免を設けている自治体が多い。適用に別途申請が必要な場合がある。",
  "target": "産後1年未満の母子（母子保健法第17条の2）。対象期間は自治体が定める。",
  "apply": "利用前の申請が必要な自治体が大半。妊娠中から申し込める自治体が多い。",
  "src": "https://www.cfa.go.jp/policies/boshihoken/sango-care",
  "src_label": "こども家庭庁「産後ケア事業」", "note": "実施の有無・負担額・回数の上限は市区町村ごとに異なります。"},
]
'''


def esc(s):
    if s is None:
        return ""
    return str(s).replace('"', "”").replace("\n", " ").strip()


def main():
    dry = "--dry" in sys.argv
    files = [f for f in os.listdir(SRC_DIR) if f.endswith(".json")]
    if not files:
        print("JSONがありません")
        return

    entries = []
    for fn in files:
        d = json.load(io.open(os.path.join(SRC_DIR, fn), encoding="utf-8"))
        d["_key"] = fn[:-5]
        entries.append(d)
    entries.sort(key=lambda d: ORDER.index(d["_key"]) if d["_key"] in ORDER else 99)

    missing = [d["_key"] for d in entries if d["_key"] not in BASIS]
    if missing:
        print("BASIS未登録（実査結果を読んで追記してください）:", missing)
        return

    out = [HEAD]
    for d in entries:
        k = d["_key"]
        b = BASIS[k]
        basis, first, add = b["stay"]
        body = [' {"key": "%s", "name": "%s", "group": "%s",'
                % (k, esc(d.get("name", k)), esc(d.get("group", "東京23区")))]
        body.append('  "stay": %s, "stay_basis": "%s", "stay_add": %s,'
                    % ("None" if first is None else first, basis,
                       "None" if add is None else add))
        body.append('  "stay_label": "%s",' % esc(d.get("fee_stay_label")) or "非公表")
        for f in ("day", "visit"):
            v = b[f]
            avail = v != "none"
            body.append('  "%s": %s, "%s_avail": %s, "%s_label": "%s",'
                        % (f, "None" if not isinstance(v, int) else v,
                           f, "True" if avail else "False", f,
                           esc(d.get("fee_%s_label" % f)) or "非公表"))
        for f in ("limit_stay", "limit_day", "limit_visit", "genmen", "target", "apply"):
            body.append('  "%s": "%s",' % (f, esc(d.get(f)) or "記載なし"))
        body.append('  "src": "%s", "src_label": "%s", "note": "%s"},'
                    % (esc(d.get("src")), esc(d.get("src_label")), esc(d.get("note"))))
        out.append("\n".join(body) + "\n")
        print("取込: %-11s %-6s 宿泊[%s %s+%s] 日帰り%s 訪問%s"
              % (k, d.get("name"), basis, first, add, b["day"], b["visit"]))
    out.append(TAIL)

    text = "".join(out)
    if dry:
        print(text[:1200])
        return
    io.open(OUT, "w", encoding="utf-8").write(text)
    print("書き出し: %s（%d自治体＋国基準）" % (OUT, len(entries)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

# -*- coding: utf-8 -*-
"""実査エージェントが書き出した産後ケアのJSONを _sangocare_data.py にまとめる。

こども誰でも通園制度で確立した手順（merge_daretsu_cities.py）と同じ考え方。
手でデータを書き写さないことで、転記ミスと数字のズレを防ぐ。

料金の「数え方」は自動判定しない。実査結果を1件ずつ読んで PRICES に確定させる。
産後ケアは実査の結果、単価×回数では表せない自治体が一定数あることが分かった:

  ・相模原市は宿泊の6日目から単価が倍（1〜5日目2,500円／6〜7日目5,000円）
  ・新潟市は各類型の1回目が無料
  ・熊本市は2泊目以降の額が公式に無い
  ・荒川区・台東区・千葉市などは「施設額−自治体負担額」で自治体としての単価が存在しない

そこで各類型を「n回目の単価の並び」で持つ。最後の値が以降に繰り返す。
None＝その回の額が公表されていない（計算しない）。並び自体が None＝自治体単価なし。

  stay: (unit, prices)  unit は "day"（1泊2日は2日ぶん）か "night"（1泊あたり）
  day / visit: prices、または "none"（その類型を実施していない）

使い方: python scripts/merge_sangocare.py [--dry]
"""
import io
import json
import os
import sys

_SP = (r"C:\Users\tatsu\AppData\Local\Temp\claude\C--Users-tatsu"
       r"\9bb7063f-23b1-4fdd-9750-dfa305ab85e1\scratchpad")
SRC_DIRS = [os.path.join(_SP, "sangocare"), os.path.join(_SP, "sangocare_seirei")]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_sangocare_data.py")
CHECKED = "2026年8月27日"

R = None   # 自治体としての単価が存在しない（施設ごとに実額が決まる）

PRICES = {
    # ---- 東京23区（2026-08-27 実査。実査時に数え方を聞いていないため本文から確定） ----
    "chiyoda":    {"stay": R,                     "day": R,       "visit": [1000]},
    "chuo":       {"stay": R,                     "day": R,       "visit": R},
    "minato":     {"stay": R,                     "day": R,       "visit": R},
    "shinjuku":   {"stay": R,                     "day": R,       "visit": [1000]},
    "bunkyo":     {"stay": R,                     "day": [3000],  "visit": [3000]},
    "taito":      {"stay": R,                     "day": R,       "visit": R},
    "sumida":     {"stay": R,                     "day": R,       "visit": [1000]},
    "koto":       {"stay": ("night", [9800, 4900]), "day": [3500], "visit": [1200]},
    "shinagawa":  {"stay": R,                     "day": R,       "visit": [0]},
    "meguro":     {"stay": R,                     "day": [2500],  "visit": [1000]},
    "ota":        {"stay": ("day", [2500]),       "day": [1500],  "visit": [500]},
    "setagaya":   {"stay": ("night", [9000, 4500]), "day": [3000], "visit": [2000]},
    "shibuya":    {"stay": ("day", [3500]),       "day": [2000],  "visit": [1000]},
    "nakano":     {"stay": ("day", [3000]),       "day": [1000],  "visit": [2000]},
    "suginami":   {"stay": ("night", [7000, 3500]), "day": R,     "visit": "none"},
    "toshima":    {"stay": ("day", [2500]),       "day": [1500],  "visit": [1000]},
    "kita":       {"stay": ("day", [3300]),       "day": [2500],  "visit": [1000]},
    "arakawa":    {"stay": R,                     "day": R,       "visit": R},
    "itabashi":   {"stay": ("night", [8000, 4000]), "day": [2000], "visit": [600]},
    "nerima":     {"stay": ("night", [7000, 3500]), "day": [1500], "visit": [500]},
    "adachi":     {"stay": ("day", [2500]),       "day": [1250],  "visit": [1000]},
    "katsushika": {"stay": ("day", [0]),          "day": [0],     "visit": [0]},
    "edogawa":    {"stay": ("night", [7000, 3500]), "day": [3000], "visit": [2000]},

    # ---- 政令指定都市（2026-08-27 実査。実査時に数え方を答えさせている） ----
    "sapporo":    {"stay": ("night", [7500]),     "day": [2500],  "visit": [2500]},
    "sendai":     {"stay": ("day", [5500]),       "day": [3200],  "visit": [2000]},
    "saitama":    {"stay": ("day", [6800]),       "day": [5000],  "visit": [2700]},
    # 千葉市は「施設の利用料×10%（上限2,800円/日）」で市としての単価が無い
    "chiba":      {"stay": R,                     "day": R,       "visit": R},
    "yokohama":   {"stay": ("day", [3000]),       "day": [2400],  "visit": [1500]},
    # 川崎市は一般世帯にも5回（日）目まで1日2,500円の減免が自動で付く。
    # 市自身の計算例も減免後で示している（6泊7日＝5,000円×5日＋7,500円×2日＝40,000円）ので、
    # 課税世帯が実際に払う額に合わせる。
    "kawasaki":   {"stay": ("day", [5000, 5000, 5000, 5000, 5000, 7500]),
                   "day": [5000, 5000, 5000, 5000, 5000, 7500],
                   "visit": [2500, 2500, 2500, 2500, 2500, 5000]},
    # 相模原市は6日目から単価が倍になる
    "sagamihara": {"stay": ("day", [2500, 2500, 2500, 2500, 2500, 5000]),
                   "day": [1000, 1000, 1000, 1000, 1000, 2000],
                   "visit": [1500, 1500, 1500, 1500, 1500, 3000]},
    # 新潟市は各類型の1回目が無料
    "niigata":    {"stay": ("day", [0, 2500]),    "day": [0, 2000], "visit": [0, 1000]},
    "shizuoka":   {"stay": ("day", [6300]),       "day": [3100],  "visit": [2300]},
    # 浜松市は市公式ドメインに市民向けの産後ケアページが無く（案内は外部サイト）、
    # 利用者負担額・上限とも一次確認できなかった。推測で埋めない。
    "hamamatsu":  {"stay": R,                     "day": R,       "visit": R},
    "nagoya":     {"stay": ("day", [3520]),       "day": [2360],  "visit": [1560]},
    # 京都市は「1回＝24時間」なので1泊2日で1回。名古屋の日数カウントとは逆になる
    "kyoto":      {"stay": ("night", [4900]),     "day": [2400],  "visit": [1000]},
    "osaka":      {"stay": ("day", [2125]),       "day": [1500],  "visit": [500]},
    "sakai":      {"stay": ("night", [5200]),     "day": [2600],  "visit": [3500]},
    "kobe":       {"stay": ("day", [3000]),       "day": [2000],  "visit": [1000]},
    # 岡山市は「施設料金−市負担額」で市としての単価が無い
    "okayama":    {"stay": R,                     "day": R,       "visit": R},
    "hiroshima":  {"stay": ("night", [11136, 5568]), "day": [3409], "visit": [2200]},
    # 北九州市は2泊目以降の増額が公式に無い
    "kitakyushu": {"stay": ("night", [3000, None]), "day": [1000], "visit": [1000]},
    "fukuoka":    {"stay": ("day", [3000]),       "day": [2000],  "visit": [500]},
    # 熊本市は2泊目以降の額が公式に無いため None を置いて計算させない
    "kumamoto":   {"stay": ("night", [8000, None]), "day": [3000], "visit": [1200]},
}

ORDER = ["chiyoda", "chuo", "minato", "shinjuku", "bunkyo", "taito", "sumida",
         "koto", "shinagawa", "meguro", "ota", "setagaya", "shibuya", "nakano",
         "suginami", "toshima", "kita", "arakawa", "itabashi", "nerima",
         "adachi", "katsushika", "edogawa",
         "sapporo", "sendai", "saitama", "chiba", "yokohama", "kawasaki",
         "sagamihara", "niigata", "shizuoka", "hamamatsu", "nagoya", "kyoto",
         "osaka", "sakai", "kobe", "okayama", "hiroshima", "kitakyushu",
         "fukuoka", "kumamoto"]

HEAD = '''# -*- coding: utf-8 -*-
"""産後ケア事業の自治体データ（ツールと記事の共通の正本）

各自治体の公式ページを一次確認して作成。金額は原文どおり。
stay_prices / day_prices / visit_prices は「n回目の単価の並び」。
最後の値が以降に繰り返す。要素の None＝その回の額が非公表。
並び自体が None＝自治体としての単価が存在しない（施設ごとに実額が決まる）。
stay_unit は "day"（1泊2日は2日ぶん）か "night"（1泊あたり）。
自動生成: python scripts/merge_sangocare.py
"""
CHECKED = "%s"

CITIES = [
''' % CHECKED

TAIL = ''' {"key": "kokuhyo", "name": "上記以外の自治体（目安）", "group": "国基準",
  "stay_unit": None, "stay_prices": None, "stay_label": "自治体ごとに設定",
  "day_prices": None, "day_avail": True, "day_label": "自治体ごとに設定",
  "visit_prices": None, "visit_avail": True, "visit_label": "自治体ごとに設定",
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


def lit(v):
    """None / 数値の並び を Python リテラルにする"""
    if v is None:
        return "None"
    return "[" + ", ".join("None" if x is None else str(int(x)) for x in v) + "]"


def main():
    dry = "--dry" in sys.argv
    entries = []
    for src in SRC_DIRS:
        if not os.path.isdir(src):
            print("（未収集）", src)
            continue
        for fn in sorted(os.listdir(src)):
            if not fn.endswith(".json"):
                continue
            d = json.load(io.open(os.path.join(src, fn), encoding="utf-8"))
            d["_key"] = fn[:-5]
            entries.append(d)
    if not entries:
        print("JSONがありません")
        return
    entries.sort(key=lambda d: ORDER.index(d["_key"]) if d["_key"] in ORDER else 99)

    missing = [d["_key"] for d in entries if d["_key"] not in PRICES]
    if missing:
        print("PRICES未登録（実査結果を読んで数え方を確定させてください）:", missing)
        return

    out = [HEAD]
    for d in entries:
        k = d["_key"]
        p = PRICES[k]
        stay = p["stay"]
        unit, prices = (None, None) if stay is None else stay
        body = [' {"key": "%s", "name": "%s", "group": "%s",'
                % (k, esc(d.get("name", k)), esc(d.get("group", "東京23区")))]
        body.append('  "stay_unit": %s, "stay_prices": %s,'
                    % ('None' if unit is None else '"%s"' % unit, lit(prices)))
        body.append('  "stay_label": "%s",' % (esc(d.get("fee_stay_label")) or "非公表"))
        for f in ("day", "visit"):
            v = p[f]
            avail = v != "none"
            body.append('  "%s_prices": %s, "%s_avail": %s, "%s_label": "%s",'
                        % (f, lit(None if not avail else v), f,
                           "True" if avail else "False", f,
                           esc(d.get("fee_%s_label" % f)) or "非公表"))
        for f in ("limit_stay", "limit_day", "limit_visit", "genmen", "target", "apply"):
            body.append('  "%s": "%s",' % (f, esc(d.get(f)) or "記載なし"))
        body.append('  "src": "%s", "src_label": "%s", "note": "%s"},'
                    % (esc(d.get("src")), esc(d.get("src_label")), esc(d.get("note"))))
        out.append("\n".join(body) + "\n")
        print("取込: %-11s %-7s 宿泊[%s %s] 日帰り%s 訪問%s"
              % (k, d.get("name"), unit, lit(prices), lit(p["day"] if p["day"] != "none" else None),
                 lit(p["visit"] if p["visit"] != "none" else None)))
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

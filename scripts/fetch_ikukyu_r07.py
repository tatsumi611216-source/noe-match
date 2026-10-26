# -*- coding: utf-8 -*-
"""育休取得率の正本 scripts/data/ikukyu_shutokuritsu.json を厚労省PDFから作る（2026-10-20 新設）

出典: 厚生労働省『令和7年度雇用均等基本調査』（令和8年7月31日公表・調査時点 令和7年10月1日）
  02.pdf 事業所調査 結果概要 … 図4（推移）・表5（有期）・表6（産後パパ育休）・表12（取得期間）
  09.pdf 事業所調査 付属統計表 … 第12表（産業・事業所規模別）
  10.pdf 調査の概要 … 用語の定義・利用上の注意（＊印）

表は手で書かない。PDFのテキスト層から数値を取り、報道発表の値と assert で突き合わせる。
図4の横軸（年度）はテキスト層に出ないため、PDFを画像で目視して YEARS に書いた（2026-10-20 確認）。
使い方: python scripts/fetch_ikukyu_r07.py <PDFを置いたディレクトリ>
"""
import io
import json
import os
import re
import sys

import pypdf

BASE = "https://www.mhlw.go.jp/toukei/list/dl/71-r07/"
CHECKED = "2026年10月20日"

# 図4の横軸（平成8〜令和7年度・24点）。平成23年度は岩手・宮城・福島を除く値
YEARS = [1996, 1999, 2002, 2004, 2005, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015,
         2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]


def wareki(y):
    if y >= 2019:
        return "令和元年度" if y == 2019 else "令和%d年度" % (y - 2018)
    return "平成%d年度" % (y - 1988)


def text(path):
    return "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(path).pages)


def nums(s):
    return [float(x) for x in re.findall(r"\d+\.\d+", s)]


def main(d):
    t02 = text(os.path.join(d, "r07_02.pdf"))
    t09 = pypdf.PdfReader(os.path.join(d, "r07_09.pdf"))

    # ---- 図4: 男性の系列は「（※２）平成 22 年度までは…」の直後〜「0.0」軸目盛りの前、女性は「（年度）」の後
    i = t02.index("図４ 育児休業取得率の推移")
    j = t02.index("表５ 有期契約労働者の育児休業取得率", i)
    blk = t02[i:j]
    after = blk[blk.index("\n", blk.index("出産者（男性の場合は配偶者が出産した者）の数")) :]
    male_s, rest = after.split("\n0.0\n", 1)
    male = nums(male_s.replace("[", " ").replace("]", " "))
    fem_s = rest[rest.index("（年度）") + len("（年度）") :].split("\n40.0\n", 1)[0]
    female = nums(fem_s.replace("[", " ").replace("]", " "))
    assert len(male) == len(YEARS) == len(female), (len(male), len(female))
    assert male[-1] == 50.9 and male[-2] == 40.5 and female[-1] == 88.3 and female[-2] == 86.6
    assert male[0] == 0.12 and female[0] == 49.1 and male[9] == 2.63 and female[9] == 87.8

    # ---- 表5: 有期契約労働者（平成25〜令和7年度・13点）
    b5 = t02[j: t02.index("表６", j)]
    fl = re.search(r"女\s*\n?性\s*([\d\. ]+)\n", b5).group(1)
    ml = re.search(r"男\s*\n?性\s*([\d\. ]+)\n", b5).group(1)
    yuki_f, yuki_m = nums(fl), nums(ml)
    assert len(yuki_f) == len(yuki_m) == 13 and yuki_f[-1] == 74.8 and yuki_m[-1] == 40.4
    yuki_years = list(range(2013, 2026))

    # ---- 表6: 産後パパ育休（育休取得者に占める割合）
    papa = {"2024": {"all": 60.6, "yuki": 82.6}, "2025": {"all": 58.3, "yuki": 56.8}}
    for v in ("(60.6)", "(82.6)", "(58.3)", "(56.8)"):
        assert v in t02.replace(" ", ""), v

    # ---- 表12: 取得期間（令和6年度に育休を終えて復職した人の分布）
    b12 = t02[t02.index("表 12  取得期間別育児休業後復職者割合"):]
    kf = nums(re.search(r"女\s*\n?性\s*\n?令和\s*\n?７年度\s*([\d\. ]+)", b12).group(1))
    km = nums(re.search(r"男\s*\n?性\s*\n?令和\s*\n?７年度\s*([\d\. ]+)", b12).group(1))
    labels = ["5日未満", "5日〜2週間未満", "2週間〜1か月未満", "1か月〜3か月未満", "3か月〜6か月未満",
              "6か月〜8か月未満", "8か月〜10か月未満", "10か月〜12か月未満", "12か月〜18か月未満",
              "18か月〜24か月未満", "24か月〜36か月未満", "36か月以上", "不明"]
    assert len(kf) == len(km) == 14 and kf[0] == km[0] == 100.0
    kf, km = kf[1:], km[1:]
    assert kf[8] == 31.4 and km[3] == 30.3 and km[2] == 28.0

    # ---- 第12表: 産業・事業所規模別（付属統計表 P11）
    p = t09.pages[11].extract_text()
    assert "総　数 100.0 88.3 100.0 50.9" in p.replace("  ", " ")
    rows = []
    for line in p.splitlines():
        m = re.match(r"^(\S.*?)\s+(\*\s*)?100\.0\s+(\*\s*)?([\d\.]+)\s+100\.0\s+([\d\.]+)\s+100\.0\s+([\d\.]+)\s+([\d\.]+)\s*$", line.strip())
        if m:
            name = m.group(1).replace("　", "").strip()
            rows.append({"name": name, "female": float(m.group(4)), "male": float(m.group(5)),
                         "female_small_sample": bool(m.group(2) or m.group(3))})
    names = [r["name"] for r in rows]
    assert names[0] == "総数" and len(rows) == 1 + 16 + 5, names
    sangyo = rows[1:17]
    kibo = rows[17:]
    assert kibo[0]["name"] == "500人以上" and kibo[-1]["name"].startswith("30人以上")
    assert sangyo[0]["female_small_sample"] and not any(r["female_small_sample"] for r in rows[2:])

    out = {
        "checked": CHECKED,
        "survey": "令和7年度雇用均等基本調査",
        "published": "令和8年7月31日",
        "chousa_jiten": "令和7年10月1日",
        "bunbo": "令和5年10月1日〜令和6年9月30日の1年間に在職中に出産した女性（男性は配偶者が出産した男性）",
        "bunshi": "そのうち令和7年10月1日までに育児休業（産後パパ育休を含む）を開始した人（開始予定の申出をしている人を含む）",
        "notes": {
            "y2011": "平成23年度（2011年度）は岩手県・宮城県・福島県を除く全国の結果",
            "papa": "令和5年度（2023年度）以降は産後パパ育休を含む",
            "kikan": "平成22年度（2010年度）までは、分母が調査前年度1年間の出産者",
            "small": "＊は構成比の分母となるサンプル数が少ない（事業所数2以下・労働者数9以下）ため利用に注意を要する（調査の概要「利用上の注意」(4)）",
            "hyohon": "標本調査（全国の事業所から抽出して推計）",
        },
        "series": [{"year": y, "wareki": wareki(y), "female": f, "male": m, "excl3": y == 2011}
                   for y, f, m in zip(YEARS, female, male)],
        "yuki": [{"year": y, "female": f, "male": m} for y, f, m in zip(yuki_years, yuki_f, yuki_m)],
        "papa_ikukyu_share": papa,
        "kikan": {"labels": labels, "female": kf, "male": km,
                  "note": "令和6年4月1日〜令和7年3月31日に育児休業（産後パパ育休を含む）を終えて復職した人の、取得期間の分布（%）"},
        "sangyo": sangyo,
        "kibo": kibo,
        "sources": [
            {"url": "https://www.mhlw.go.jp/toukei/list/71-r07.html", "label": "厚生労働省『令和7年度雇用均等基本調査』（調査結果のページ）"},
            {"url": BASE + "02.pdf", "label": "同 事業所調査 結果概要（図4・表5・表6・表12）"},
            {"url": BASE + "09.pdf", "label": "同 事業所調査 付属統計表（第12表 産業・事業所規模別）"},
            {"url": BASE + "05.pdf", "label": "同 報道発表資料（令和8年7月31日）"},
            {"url": BASE + "10.pdf", "label": "同 調査の概要（用語の定義・利用上の注意）"},
        ],
    }
    here = os.path.dirname(os.path.abspath(__file__))
    with io.open(os.path.join(here, "data", "ikukyu_shutokuritsu.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("OK series=%d yuki=%d sangyo=%d kibo=%d" % (len(out["series"]), len(out["yuki"]), len(sangyo), len(kibo)))


if __name__ == "__main__":
    main(sys.argv[1])

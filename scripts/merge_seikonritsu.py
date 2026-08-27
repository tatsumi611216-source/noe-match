# -*- coding: utf-8 -*-
"""成婚率の実査JSONを _seikonritsu_data.py にまとめる（2026-08-27 新設）

このバンクの勘所:
成婚率は「率」に見えて、社ごとに分母・分子・期間・そもそもの指標の種類が違う。
だから比較記事の並びはほぼ意味をなさない。**事業者自身（ツヴァイ）が
オウンドメディアでこの計算式の違いを解説している**のが強い足場になる。

ここで軸（shihyo / bunbo_type / bunshi_type / kikan_type）を付けているが、
これは器具で「揃っていない軸」を機械的に出すためのラベルであって、
優劣の判定ではない。**表には必ず各社の原文を併記する**（8/25・8/27の教訓:
分類を勝手に決めない・原文を出す）。

使い方: python scripts/merge_seikonritsu.py [--dry]
"""
import io
import json
import os
import sys

SRC = (r"C:\Users\tatsu\AppData\Local\Temp\claude\C--Users-tatsu"
       r"\9bb7063f-23b1-4fdd-9750-dfa305ab85e1\scratchpad\seikonritsu\data.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_seikonritsu_data.py")

# 軸のラベル。各社の公表文から読み取れる範囲だけを機械可読にしたもの。
# 「非公表」は公表が無いという事実であって、無いことの推測ではない。
AXES = {
 "ibj":           ("実数（組数）",   "―（率ではない）", "婚約",                  "単年（暦年）"),
 "ibj_members":   ("率",             "退会者",           "婚約",                  "単年"),
 "partner_agent": ("率",             "在籍会員",         "非公表",                "単年"),
 "zwei":          ("実数（組数）",   "―（率ではない）", "連盟内の成婚者数",      "単年（暦年）"),
 "onet":          ("公表なし",       "非公表",           "連盟内の成婚者数",      "累計"),
 "sunmarie":      ("率（構成比）",   "非公表",           "婚約＋それに近い状態",  "2年"),
 "nacodo":        ("期間",           "―（率ではない）", "非公表",                "非公表"),
 "smarriage":     ("公表なし",       "非公表",           "結婚の意思確認",        "非公表"),
 "zexy_agent":    ("率",             "非公表",           "非公表",                "非公表"),
 "zexy_enmusubi": ("未取得",         "未取得",           "未取得",                "未取得"),
 "pairs":         ("累計人数",       "―（率ではない）", "交際＋結婚（自社調べ）", "累計"),
 "with":          ("実数（日次）",   "―（率ではない）", "マッチング成立",        "単年"),
 "omiai":         ("累計人数",       "―（率ではない）", "恋人ができた（自己申告）", "累計"),
 "youbride":      ("累計人数",       "―（率ではない）", "相手が見つかって退会",  "累計（13年）"),
 "tapple":        ("実数（月次）",   "―（率ではない）", "恋人ができた（自己申告）", "単年"),
 "marrish":       ("期間",           "―（率ではない）", "恋人ができた（自己申告・男性のみ）", "単年"),
}

HEAD = '''# -*- coding: utf-8 -*-
"""結婚相談所・マッチングアプリの成婚率データ（器具と記事の共通の正本）

各社の公式ページ・IR資料を一次確認して作成。文言は原文どおり。
shihyo / bunbo_type / bunshi_type / kikan_type は「揃っていない軸」を
機械的に出すためのラベルで、優劣の判定ではない。表には原文を併記すること。
自動生成: python scripts/merge_seikonritsu.py
"""
CHECKED = "%s"

'''


def esc(s):
    if s is None:
        return ""
    return str(s).replace('"', "”").replace("\n", " ").replace("\\", "").strip()


def main():
    d = json.load(io.open(SRC, encoding="utf-8"))
    checked = d["checked"]
    out = [HEAD % checked]

    out.append("COMPANIES = [\n")
    for c in d["companies"]:
        k = c["key"]
        if k not in AXES:
            print("軸の未定義:", k)
            return
        sh, bb, bs, kk = AXES[k]
        out.append(' {"key": "%s", "name": "%s", "type": "%s",\n' % (k, esc(c["name"]), esc(c["type"])))
        out.append('  "shihyo": "%s", "bunbo_type": "%s", "bunshi_type": "%s", "kikan_type": "%s",\n'
                   % (sh, bb, bs, kk))
        for f in ("value_label", "bunbo", "bunshi", "kikan", "src", "src_label", "note"):
            out.append('  "%s": "%s",\n' % (f, esc(c.get(f)) or "記載なし"))
        out.append('  "teigi_kohyo": %s},\n' % ("True" if c.get("teigi_kohyo") else "False"))
        print("取込: %-14s %-10s 分母=%s" % (k, sh, bb))
    out.append("]\n\n")

    out.append("# 定義がそろわない具体例（実査でまとめたもの・原文の要約）\nTEIGI = [\n")
    for t in d["teigi_no_chigai"]:
        out.append('  "%s",\n' % esc(t))
    out.append("]\n\n")

    out.append("# 出典（全件）\nSOURCES = [\n")
    for s in d["sources"]:
        out.append('  ("%s", "%s"),\n' % (esc(s["url"]), esc(s["label"])))
    out.append("]\n\n")

    out.append("# 取れなかったものと、その理由（記事に明記する）\nUNCONFIRMED = [\n")
    for u in d["unconfirmed"]:
        if isinstance(u, dict):
            out.append('  ("%s", "%s"),' % (esc(u.get("item")), esc(u.get("reason"))) + chr(10))
        else:
            out.append('  ("%s", ""),' % esc(u) + chr(10))
    out.append("]\n")

    text = "".join(out)
    if "--dry" in sys.argv:
        print(text[:2000])
        return
    io.open(OUT, "w", encoding="utf-8").write(text)
    print("書き出し: %s（%d社）" % (OUT, len(d["companies"])))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

# -*- coding: utf-8 -*-
"""子ども医療費助成（マル乳・マル子・マル青）23区のJSONを _kodomo_iryo_data.py にまとめる。

産後ケア・通園制度で確立した手順と同じ。手でデータを書き写さないことで
転記ミスと数字のズレを防ぐ。

このバンクの勘所（2026-08-27 実査で判明）:
東京都の基準は「通院1回につき最大200円の一部負担あり」「入院時食事療養標準負担額は
助成対象外」で、都のページ自身が「区市町村によって助成範囲が異なり、窓口負担のない
区市町村もあります」と明記している。つまり**区ページに「自己負担なし」「食事代も助成」と
書いてあれば、それは区独自の上乗せ**。記載が無い区は都基準のままの可能性があるので、
推測せず None のまま残す（実査エージェントにもそう指示した）。

使い方: python scripts/merge_kodomo_iryo.py [--dry]
"""
import io
import json
import os
import sys

SRC = (r"C:\Users\tatsu\AppData\Local\Temp\claude\C--Users-tatsu"
       r"\9bb7063f-23b1-4fdd-9750-dfa305ab85e1\scratchpad\kodomo_iryo")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_kodomo_iryo_data.py")
CHECKED = "2026年8月27日"

ORDER = ["chiyoda", "chuo", "minato", "shinjuku", "bunkyo", "taito", "sumida",
         "koto", "shinagawa", "meguro", "ota", "setagaya", "shibuya", "nakano",
         "suginami", "toshima", "kita", "arakawa", "itabashi", "nerima",
         "adachi", "katsushika", "edogawa"]

FIELDS = ["age_limit", "age_limit_class", "shotoku_seigen_note", "jiko_futan_note",
          "shokuji_ryoyohi", "kugai", "apply", "medical_cert_name", "r8_kaitei",
          "src", "src_label", "note"]

HEAD = '''# -*- coding: utf-8 -*-
"""子ども医療費助成（マル乳・マル子・マル青）東京23区のデータ（ツールと記事の共通の正本）

各区の公式ページを一次確認して作成。文言は原文どおり。
shotoku_seigen / jiko_futan は True/False/None の3値。
**None＝区の公式ページに記載が無い**（都基準のままの可能性があるが推測しない）。
自動生成: python scripts/merge_kodomo_iryo.py
"""
CHECKED = "%s"

# 東京都の基準（判定の基準線）。区の値がこれと違えば区独自の上乗せ。
TOKYO_KIJUN = {
    "jiko_futan": "通院1回につき最大200円の一部負担あり",
    "shokuji_ryoyohi": "入院時食事療養標準負担額は自己負担（助成対象外）",
    "note": "東京都のページ自身が「区市町村によって助成範囲が異なり、窓口負担のない区市町村もあります」と明記している。",
}

WARDS = [
''' % CHECKED


def esc(s):
    if s is None:
        return ""
    return str(s).replace('"', "”").replace("\n", " ").strip()


def tri(v):
    """True / False / None の3値をそのまま保つ"""
    if v is True:
        return "True"
    if v is False:
        return "False"
    return "None"


def main():
    dry = "--dry" in sys.argv
    files = [f for f in os.listdir(SRC) if f.endswith(".json")]
    entries = []
    for fn in files:
        d = json.load(io.open(os.path.join(SRC, fn), encoding="utf-8"))
        d["_key"] = fn[:-5]
        entries.append(d)
    entries.sort(key=lambda d: ORDER.index(d["_key"]) if d["_key"] in ORDER else 99)

    missing = [k for k in ORDER if k not in [d["_key"] for d in entries]]
    if missing:
        print("未取得の区:", missing)
        return

    out = [HEAD]
    for d in entries:
        k = d["_key"]
        body = [' {"key": "%s", "name": "%s", "group": "東京23区",' % (k, esc(d.get("name", k)))]
        body.append('  "shotoku_seigen": %s, "jiko_futan": %s,'
                    % (tri(d.get("shotoku_seigen")), tri(d.get("jiko_futan"))))
        for f in FIELDS:
            body.append('  "%s": "%s",' % (f, esc(d.get(f)) or "記載なし"))
        body.append('  "src2": "%s", "src2_label": "%s"},'
                    % (esc(d.get("src2")), esc(d.get("src2_label"))))
        out.append("\n".join(body) + "\n")
        print("取込: %-11s %-6s 所得制限%-5s 自己負担%-5s 食事%s"
              % (k, d.get("name"), tri(d.get("shotoku_seigen")),
                 tri(d.get("jiko_futan")), esc(d.get("shokuji_ryoyohi"))[:12]))
    out.append("]\n")

    text = "".join(out)
    if dry:
        print(text[:1200])
        return
    io.open(OUT, "w", encoding="utf-8").write(text)
    print("書き出し: %s（%d区）" % (OUT, len(entries)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

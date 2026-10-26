# -*- coding: utf-8 -*-
"""病児保育・不妊治療（先進医療）助成 東京23区のJSONを正本にまとめる（2026-08-27 新設）

1回の実査で2つのバンクが取れた例。取る経路が違うので面も分ける。
- 病児保育: 23区すべてが実施。差がつくのは**料金（江戸川0円〜新宿3,500円）と減免**
- 不妊治療（先進医療）: **実施16区・未実施7区**。上限額は5万円が最多だが港区は30万円

実施の有無すら区で割れるのは、この2つが「区の独自事業」だから。
子ども医療費助成（対象年齢は23区同一）とは対照的で、そこが記事の核になる。

助成額の計算式は区ごとに違い（練馬区は「先進医療費の7割−都の上限15万円」と
「区の上限5万円」の低い方）、全区ぶんは取れていない。**器具では助成額を計算しない**。
上限額・回数・対象・期限を引けるところまでにする（推測で計算させない）。

使い方: python scripts/merge_byoji_funin.py [--dry]
"""
import glob
import io
import json
import os
import sys

SRC = (r"C:\Users\tatsu\AppData\Local\Temp\claude\C--Users-tatsu"
       r"\9bb7063f-23b1-4fdd-9750-dfa305ab85e1\scratchpad\byoji_funin")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_byoji_funin_data.py")
CHECKED = "2026年8月27日"

ORDER = ["chiyoda", "chuo", "minato", "shinjuku", "bunkyo", "taito", "sumida",
         "koto", "shinagawa", "meguro", "ota", "setagaya", "shibuya", "nakano",
         "suginami", "toshima", "kita", "arakawa", "itabashi", "nerima",
         "adachi", "katsushika", "edogawa"]

B_FIELDS = ["fee_label", "genmen", "taisho", "jogen", "yoyaku", "src", "src_label"]
F_FIELDS = ["jogen_kaisu", "taisho", "taisho_chiryo", "shinsei_kigen", "src", "src_label"]

HEAD = '''# -*- coding: utf-8 -*-
"""病児保育・不妊治療（先進医療）助成 東京23区のデータ（器具と記事の共通の正本）

各区の公式ページを一次確認して作成。文言は原文どおり。
fee は数値（円／日）、jogen_gaku は数値（円）。取れなかったものは None。
**None＝区の公式ページに記載が無い**（無いことの推測ではない）。
自動生成: python scripts/merge_byoji_funin.py
"""
CHECKED = "%s"

WARDS = [
''' % CHECKED


def esc(s):
    if s is None:
        return ""
    return str(s).replace('"', "”").replace("\n", " ").replace("\\", "").strip()


def num(v):
    return str(v) if isinstance(v, (int, float)) else "None"


def main():
    entries = []
    for f in glob.glob(os.path.join(SRC, "*.json")):
        d = json.load(io.open(f, encoding="utf-8"))
        d["_key"] = os.path.basename(f)[:-5]
        entries.append(d)
    entries.sort(key=lambda d: ORDER.index(d["_key"]) if d["_key"] in ORDER else 99)

    missing = [k for k in ORDER if k not in [d["_key"] for d in entries]]
    if missing:
        print("未取得の区:", missing)
        return

    out = [HEAD]
    for d in entries:
        b = d.get("byoji") or {}
        u = d.get("funin") or {}
        p = [' {"key": "%s", "name": "%s", "group": "東京23区",' % (d["_key"], esc(d.get("name")))]
        p.append('  "byoji_jisshi": %s, "byoji_fee": %s,'
                 % ("True" if b.get("jisshi") else "False", num(b.get("fee"))))
        for f in B_FIELDS:
            p.append('  "byoji_%s": "%s",' % (f, esc(b.get(f)) or "記載なし"))
        p.append('  "funin_jisshi": %s, "funin_jogen_gaku": %s,'
                 % ("True" if u.get("jisshi") else "False", num(u.get("jogen_gaku"))))
        for f in F_FIELDS:
            p.append('  "funin_%s": "%s",' % (f, esc(u.get(f)) or "記載なし"))
        p.append('  "note": "%s"},' % esc(d.get("note")))
        out.append("\n".join(p) + "\n")
        print("取込: %-11s %-6s 病児%-6s 不妊%-6s上限%s"
              % (d["_key"], d.get("name"), num(b.get("fee")) + "円",
                 "実施" if u.get("jisshi") else "なし", num(u.get("jogen_gaku"))))
    out.append("]\n")

    text = "".join(out)
    if "--dry" in sys.argv:
        print(text[:1500])
        return
    io.open(OUT, "w", encoding="utf-8").write(text)
    print("書き出し: %s（%d区）" % (OUT, len(entries)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

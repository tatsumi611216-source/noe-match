# -*- coding: utf-8 -*-
"""実査エージェントが書き出したJSONを _daretsu_data.py の CITIES に取り込む。

各エージェントは1自治体ぶんのJSONをスクラッチパッドに残す。
このスクリプトはそれを読み、既に収録済みのキーは飛ばして追記する。
手でデータを書き写さないことで、転記ミスと数字のズレを防ぐ。

使い方: python scripts/merge_daretsu_cities.py [--dry]
"""
import io, json, os, re, sys

SRC_DIR = (r"C:\Users\tatsu\AppData\Local\Temp\claude\C--Users-tatsu"
           r"\9bb7063f-23b1-4fdd-9750-dfa305ab85e1\scratchpad\daretsu")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_daretsu_data.py")
FIELDS = ["cap_note", "fee", "fee_extra", "reserve", "apply", "facil", "age"]


def first(v):
    return v[0] if isinstance(v, list) else v


def esc(s):
    return str(s).replace('"', "”").replace("\n", " ").strip()


def main():
    dry = "--dry" in sys.argv
    src = io.open(DATA, encoding="utf-8").read()
    have = set(re.findall(r'\{"key": "([a-z]+)"', src))
    entries = []
    for fn in sorted(os.listdir(SRC_DIR)):
        if not fn.endswith(".json"):
            continue
        key = fn[:-5]
        if key in have:
            print("skip (収録済み):", key)
            continue
        d = json.load(io.open(os.path.join(SRC_DIR, fn), encoding="utf-8"))
        cap = d.get("cap")
        body = ['{"key": "%s", "name": "%s", "cap": %s, "cap_label": "%s", "group": "政令市",'
                % (key, esc(d["city_name"]), "None" if cap is None else int(cap), esc(d["cap_label"]))]
        for f in FIELDS:
            body.append('  "%s": "%s",' % (f, esc(d.get(f, "記載なし"))))
        body.append('  "src": "%s", "src_label": "%s"},'
                    % (esc(first(d["src"])), esc(first(d["src_label"]))))
        entries.append(" " + "\n ".join(body))
        print("add:", key, d["city_name"], cap)
    if not entries:
        print("追加なし")
        return
    if dry:
        print("\n".join(entries)[:1200])
        return
    anchor = ' {"key": "kokuhyo",'
    src = src.replace(anchor, "\n".join(entries) + "\n" + anchor, 1)
    io.open(DATA, "w", encoding="utf-8").write(src)
    print("追記: %d自治体" % len(entries))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

# -*- coding: utf-8 -*-
"""マッチングアプリの料金（8社）を正本にまとめる（2026-08-27 新設）

このバンクの勘所:
同じアプリ・同じプランでも、**契約する場所（Web／iPhone・Androidのアプリ内課金）で
料金が違う**。12か月ではタップルが5,200円、ブライダルネットが5,800円の差。
Omiaiには「決済方法によって料金が異なる理由」という専用のヘルプ記事があり、
会社側もこの差を公式に説明している。読者が今日から動かせる数字はここ。

「〜」表記（下限額）はそのまま保つ。丸めない。
決済方法別の内訳が公開されていない社（with・ユーブライド）は differs を
"unknown" にして、差が無いことにしない。Tinderは価格表そのものが取れていない。

使い方: python scripts/merge_app_ryokin.py [--dry]
"""
import io
import json
import os
import sys

SRC = (r"C:\Users\tatsu\AppData\Local\Temp\claude\C--Users-tatsu"
       r"\9bb7063f-23b1-4fdd-9750-dfa305ab85e1\scratchpad\app_ryokin\data.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_app_ryokin_data.py")

# 原文の表から取り出した男性有料プランの総額（円）。
# web / app が別れていない社は single に入れ、web/app は None のままにする。
# approx=True は原文が「〜」（下限額）で書かれている社。
PRICE = {
 "pairs": dict(web={1: 4100, 3: 9100, 6: 14200, 12: 20100},
               app={1: 4800, 3: 10200, 6: 15800, 12: 22400}, approx=False),
 "omiai": dict(web={1: 4400, 3: 11100, 6: 16700, 12: 25800},
               app={1: 4900, 3: 11800, 6: 17800, 12: 27800}, approx=False),
 "tapple": dict(web={1: 3700, 3: 9300, 6: 13200, 12: 18200},
                app={1: 4900, 3: 11200, 6: 16800, 12: 23400}, approx=True),
 "marrish": dict(web={1: 3800, 3: 8800, 6: 14800, 12: 19800},
                 app={1: 4800, 3: 10800, 6: 15800, 12: 22400}, approx=False),
 "bridal_net": dict(web={1: 3980, 12: 24000},
                    app={1: 5080, 12: 29800}, approx=False),
 # 決済方法別の内訳が公開されていない社。単一の表しか出ていない。
 "with": dict(single={1: 4260, 3: 10280, 6: 15800, 12: 21000}, approx=True),
 "youbride": dict(single={1: 5000, 3: 10800, 6: 17800, 12: 28800}, approx=True),
 # 価格表そのものが取れていない社。
 "tinder": dict(approx=False),
}

HEAD = '''# -*- coding: utf-8 -*-
"""マッチングアプリの料金データ（器具と記事の共通の正本）

各社の公式料金ページを一次確認して作成。文言は原文どおり。
web / app / single は男性有料プランの総額（円）を期間（か月）でひいた辞書。
**web と app が両方あるのは、決済方法別の金額を会社が公開している社だけ。**
single は決済方法別の内訳が非公開で、単一の表しか出ていない社。
approx=True は原文が「〜」（下限額）で書かれている社。
自動生成: python scripts/merge_app_ryokin.py
"""
CHECKED = "%s"

'''


def esc(s):
    if s is None:
        return ""
    return str(s).replace('"', "”").replace("\\n", " ").replace("\\", "").strip()


def flat(v):
    """dict や None が混ざる自由記述を、表示できる1つの文字列にする。"""
    if v is None:
        return ""
    if isinstance(v, str):
        return esc(v)
    if isinstance(v, dict):
        parts = []
        for k, x in v.items():
            if k in ("src",):
                continue
            parts.append("%s: %s" % (k, flat(x)) if not isinstance(x, str) else flat(x))
        return esc("／".join(p for p in parts if p))
    return esc(json.dumps(v, ensure_ascii=False))


def dic(d):
    if not d:
        return "None"
    return "{" + ", ".join("%d: %d" % (k, v) for k, v in sorted(d.items())) + "}"


def main():
    d = json.load(io.open(SRC, encoding="utf-8"))
    out = [HEAD % d["checked"], "APPS = [\n"]
    for a in d["apps"]:
        k = a["key"]
        if k not in PRICE:
            print("数値の未定義:", k)
            return
        pr = PRICE[k]
        wva = a.get("web_vs_app") or {}
        differs = wva.get("differs")
        if differs is True:
            dlabel = "differs"
        elif pr.get("single"):
            dlabel = "unknown"
        elif not pr.get("web"):
            dlabel = "unconfirmed"
        else:
            dlabel = "unknown"
        p = [' {"key": "%s", "name": "%s",' % (k, esc(a.get("name_ja", k)))]
        p.append('  "web": %s, "app": %s, "single": %s, "approx": %s,'
                 % (dic(pr.get("web")), dic(pr.get("app")), dic(pr.get("single")),
                    "True" if pr.get("approx") else "False"))
        p.append('  "differs": "%s", "differs_note": "%s",' % (dlabel, esc(wva.get("detail"))))
        p.append('  "free_range": "%s",' % flat(a.get("free_range")))
        p.append('  "female": "%s",' % flat(a.get("female_price")))
        for f in ("auto_renew", "zeikomi", "src", "src_label", "note"):
            p.append('  "%s": "%s",' % (f, esc(a.get(f)) or "記載なし"))
        p.append('  "premium": "%s"},' % flat(a.get("premium")))
        out.append("\n".join(p) + "\n")
        print("取込: %-11s %-11s web12m=%-7s app12m=%-7s"
              % (k, dlabel,
                 (pr.get("web") or {}).get(12, "―"), (pr.get("app") or {}).get(12, "―")))
    out.append("]\n\n")

    out.append("# 出典（全件）\nSOURCES = [\n")
    for s in d["sources"]:
        out.append('  ("%s", "%s"),\n' % (esc(s.get("url")), esc(s.get("label"))))
    out.append("]\n\n")

    out.append("# 取れなかったものと、その理由（記事に明記する）\nUNCONFIRMED = [\n")
    for u in d["unconfirmed"]:
        if isinstance(u, dict):
            out.append('  ("%s", "%s"),\n' % (esc(u.get("item")), esc(u.get("reason"))))
        else:
            out.append('  ("%s", ""),\n' % esc(u))
    out.append("]\n")

    text = "".join(out)
    if "--dry" in sys.argv:
        print(text[:2000])
        return
    io.open(OUT, "w", encoding="utf-8").write(text)
    print("書き出し: %s（%d社）" % (OUT, len(d["apps"])))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

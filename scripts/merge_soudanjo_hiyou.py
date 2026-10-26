# -*- coding: utf-8 -*-
"""結婚相談所の費用（10社）を正本にまとめる（2026-08-27 新設）

このバンクの勘所:
各社は「入会金」「月会費」「お見合い料」「成婚料」を別々に出すだけで、
**10社中8社が1年間の総額を公表していない**。だから読者は総額を比べられない。
総額を出すのが器具の役割で、そこが SERP1ページ目の比較メディアに無いもの。

金額は原文（NUM）から手で取り出している。取り違えると記事ごと壊れるので、
**自社で12か月総額を公表している2社と突き合わせて検算し、合わなければ落とす**。
- ツヴァイ: 118,800 + 15,950×12 = 310,200 → 公式の「12ヶ月で成婚退会した場合の総額」と一致
- スマリッジ: 6,600 + 9,900×12 = 125,400 → 公式の「年間活動費」と一致
この2本が通れば、同じ積み方をしている他社の値も信頼してよい。

**記載が無い項目は0円にしない**（None のまま）。IBJメンバーズとオーネットは
お見合い料の項目自体が料金表に存在せず、「無料と明記」しているサンマリエ等とは別物。

使い方: python scripts/merge_soudanjo_hiyou.py [--dry]
"""
import io
import json
import os
import sys

SRC = (r"C:\Users\tatsu\AppData\Local\Temp\claude\C--Users-tatsu"
       r"\9bb7063f-23b1-4fdd-9750-dfa305ab85e1\scratchpad\soudanjo_hiyou\data.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_soudanjo_hiyou_data.py")

# 原文から取り出した税込の数値。None＝料金表に項目が無い（0円ではない）。
# seikon は「同じ相談所の会員と成婚した場合」、seikon_renmei は「連盟（IBJ）会員と
# 成婚した場合」。ツヴァイとオーネットはこの2つで額が変わるので分けている。
# omiai は「無料と明記」なら0、「項目そのものが無い」なら None。
# seikon_note は成婚料に条件が付く社の但し書き。
NUM = {
 "ibj_members":       dict(init=252450, month=17050, omiai=None, seikon=220000,
                           init_note="登録料33,000円＋活動サポート費219,450円",
                           omiai_note="料金表にお見合い料の項目が無い", seikon_note=""),
 "partner_agent":     dict(init=165000, month=18700, omiai=None, seikon=220000,
                           init_note="登録料33,000円＋初期費用132,000円",
                           omiai_note="料金表にお見合い料の項目が無い", seikon_note=""),
 "zwei":              dict(init=118800, month=15950, omiai=0, seikon=0, seikon_renmei=220000,
                           init_note="入会初期費用118,800円（紹介プラン）",
                           omiai_note="無料と明記",
                           seikon_note="ツヴァイ会員同士の成婚は0円。IBJ会員との成婚は220,000円"),
 "onet":              dict(init=129800, month=19250, omiai=None, seikon=0, seikon_renmei=220000,
                           init_note="入会時お支払い費用129,800円（IBJプラン）",
                           omiai_note="料金表にお見合い料の項目が無い",
                           seikon_note="オーネット会員同士の成婚は0円。IBJ会員との成婚は220,000円"),
 "sunmarie":          dict(init=165000, month=18700, omiai=0, seikon=220000,
                           init_note="入会金33,000円＋初期活動費132,000円（ベーシックサポート）",
                           omiai_note="無料と明記", seikon_note=""),
 "nacodo":            dict(init=66000, month=16800, omiai=None, seikon=0,
                           init_note="初期費用66,000円",
                           omiai_note="料金表にお見合い料の項目が無い",
                           seikon_note="0円と明記"),
 "smarriage":         dict(init=6600, month=9900, omiai=0, seikon=0,
                           init_note="登録料6,600円",
                           omiai_note="毎月8件目まで0円、9件目以降は1,100円/件",
                           seikon_note="0円と明記"),
 "excellence_aoyama": dict(init=55000, month=7700, omiai=8800, seikon=220000,
                           init_note="初期費用55,000円（スタンダードコース）",
                           omiai_note="男性8,800円／女性5,500円。本ツールは男性の額で計算",
                           seikon_note="全コース共通"),
 "musubi":            dict(init=363000, month=16500, omiai=0, seikon=330000,
                           init_note="入会金330,000円＋事務手続費33,000円（レギュラーコース）",
                           omiai_note="無料と明記（カジュアルコースのみ11,000円/回）",
                           seikon_note="全3コース共通"),
 "fiore":             dict(init=33000, month=9900, omiai=None, seikon=110000,
                           init_note="入会時支払い33,000円（リミテッドコース プラン2／予約割引時16,500円）",
                           omiai_note="AIマッチング紹介以外で成立した場合は5,500円/回",
                           seikon_note="成立費用として110,000円"),
}

# 自社で12か月の総額を公表している社。ここが合わなければ数値の取り違えなので落とす。
KENZAN = {"zwei": 310200, "smarriage": 125400}

HEAD = '''# -*- coding: utf-8 -*-
"""結婚相談所の費用データ（器具と記事の共通の正本）

各社の公式料金ページを一次確認して作成。文言は原文どおり。
init / month / omiai / seikon は原文から取り出した税込の数値。
**omiai と seikon の None は「料金表に項目が無い」で、0円ではない。**
seikon＝同じ相談所の会員と成婚した場合／seikon_renmei＝連盟（IBJ）会員と成婚した場合。
自動生成: python scripts/merge_soudanjo_hiyou.py
"""
CHECKED = "%s"

'''


def esc(s):
    if s is None:
        return ""
    return str(s).replace('"', "”").replace("\\n", " ").replace("\\", "").strip()


def n(v):
    return str(v) if isinstance(v, int) else "None"


def main():
    d = json.load(io.open(SRC, encoding="utf-8"))

    # --- 検算。ここを通らなければ何も書き出さない ---
    for k, expect in KENZAN.items():
        v = NUM[k]
        got = v["init"] + v["month"] * 12
        if got != expect:
            print("検算に失敗: %s 12か月総額 計算%d ≠ 公表%d" % (k, got, expect))
            return
        print("検算OK: %-10s %d + %d×12 = %d（公表値と一致）" % (k, v["init"], v["month"], got))

    out = [HEAD % d["checked"], "COMPANIES = [\n"]
    for c in d["companies"]:
        k = c["key"]
        if k not in NUM:
            print("数値の未定義:", k)
            return
        v = NUM[k]
        p = [' {"key": "%s", "name": "%s",' % (k, esc(c["name"]))]
        p.append('  "init": %s, "month": %s, "omiai": %s, "seikon": %s, "seikon_renmei": %s,'
                 % (n(v["init"]), n(v["month"]), n(v["omiai"]), n(v["seikon"]),
                    n(v.get("seikon_renmei", v["seikon"]))))
        p.append('  "init_note": "%s", "omiai_note": "%s", "seikon_note": "%s",'
                 % (esc(v["init_note"]), esc(v["omiai_note"]), esc(v["seikon_note"])))
        for f in ("plan_name", "nyukai", "getsugaku", "omiai_ryo", "seikon_ryo",
                  "sonota", "zeikomi", "src", "src_label", "note"):
            p.append('  "%s": "%s",' % (f, esc(c.get(f)) or "記載なし"))
        kohyo = c.get("nenkan_sogaku_kohyo")
        p.append('  "nenkan_sogaku_kohyo": %s},'
                 % ('"%s"' % esc(kohyo) if kohyo else "None"))
        out.append("\n".join(p) + "\n")
        print("取込: %-18s 初期%7d 月%6d 成婚%s"
              % (k, v["init"], v["month"], n(v["seikon"])))
    out.append("]\n\n")

    out.append("# 取れなかったものと、その理由（記事に明記する）\nUNCONFIRMED = [\n")
    for u in d["unconfirmed"]:
        out.append('  ("%s", "%s"),\n' % (esc(u["item"]), esc(u["reason"])))
    out.append("]\n\n")

    out.append("# 調査中に見つかった注意事項\nCHUI = [\n")
    for x in d.get("chui", []):
        out.append('  "%s",\n' % esc(x))
    out.append("]\n")

    text = "".join(out)
    if "--dry" in sys.argv:
        print(text[:1500])
        return
    io.open(OUT, "w", encoding="utf-8").write(text)
    print("書き出し: %s（%d社）" % (OUT, len(d["companies"])))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

# -*- coding: utf-8 -*-
"""ひとり親支援 実査JSONのマージ＋検算（2026-08-29）

agent/research_hitorioya/*.json を読み、検算を通った分だけを
scripts/_hitorioya_data.py（バンク正本）に書き出す。

検算（1つでも落ちた区は取り込まず、理由を表示して人が読む）:
  1. 必須フィールドが揃っているか（ward / checked / 3制度 / src）
  2. src が区公式ドメイン（city.*.tokyo.jp / *.lg.jp / *.tokyo.jp）か
  3. 児童育成手当の月額が都基準（育成13,500円／障害15,500円）か。
     ※障害手当の基準は当初15,900円と誤って設定していたが、品川・墨田・千代田・
      中央の4区が独立に「15,500円」で一致したため 2026-08-29 に基準側を訂正した。
      アンカーは取得ミスの検出器であって、原文より偉いわけではない。
  4. 医療費助成の負担記述に「1割」または「負担なし/無料/非課税」を含むか
     （含まない場合は取得ミスの疑い）

実行: python scripts/merge_hitorioya.py          # 検算と差分表示のみ
      python scripts/merge_hitorioya.py --apply  # _hitorioya_data.py を書き出す
"""
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "agent", "research_hitorioya")
OUT = os.path.join(ROOT, "scripts", "_hitorioya_data.py")

WARDS23 = ["千代田区","中央区","港区","新宿区","文京区","台東区","墨田区","江東区","品川区",
           "目黒区","大田区","世田谷区","渋谷区","中野区","杉並区","豊島区","北区","荒川区",
           "板橋区","練馬区","足立区","葛飾区","江戸川区"]

OFFICIAL = re.compile(r"https?://([a-z0-9\-]+\.)*(city\.[a-z\-]+\.tokyo\.jp|[a-z\-]+\.lg\.jp|[a-z\-]+\.tokyo\.jp)/", re.I)


def official_ok(d, path="root"):
    bad = []
    def walk(x, p):
        if isinstance(x, dict):
            for k, v in x.items():
                if k == "src" and v and not OFFICIAL.match(str(v)):
                    bad.append((p + "." + k, str(v)[:60]))
                walk(v, p + "." + k)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                walk(v, "%s[%d]" % (p, i))
    walk(d, path)
    return bad


def main(apply_):
    files = sorted(glob.glob(os.path.join(SRC, "*.json")))
    ok, ng, flags = [], [], []
    seen = set()
    for f in files:
        try:
            d = json.load(io.open(f, encoding="utf-8"))
        except Exception as e:
            ng.append((f, "JSONが読めない: %s" % e)); continue
        w = d.get("ward")
        if w not in WARDS23:
            ng.append((f, "ward不正: %r" % w)); continue
        if w in seen:
            ng.append((f, "%s が重複" % w)); continue
        miss = [k for k in ("checked", "ikusei_teate", "iryo_josei", "jutaku") if not d.get(k)]
        if miss:
            ng.append((f, "欠落: %s" % ",".join(miss))); continue
        bad = official_ok(d)
        if bad:
            ng.append((f, "非公式src: %s" % "; ".join("%s=%s" % b for b in bad[:3]))); continue
        ik = d["ikusei_teate"]
        if ik.get("exists") is True:
            if ik.get("monthly") != 13500:
                flags.append((w, "育成手当 月額 %r ≠ 基準13,500" % ik.get("monthly")))
            if ik.get("shogai_monthly") not in (15500, None, "非公表"):
                flags.append((w, "障害手当 %r ≠ 基準15,500（原文優先で取り込む）" % ik.get("shogai_monthly")))
        fu = str(d["iryo_josei"].get("futan", ""))
        if not re.search(r"1割|一割|負担なし|無料|非課税|自己負担", fu):
            flags.append((w, "医療費の負担記述が基準形を含まない（取得ミスの疑い）: %s" % fu[:50]))
        seen.add(w); ok.append(d)
    ok.sort(key=lambda d: WARDS23.index(d["ward"]))
    print("取り込み可: %d / NG: %d / 未着: %d" % (len(ok), len(ng), 23 - len(seen)))
    for f, r in ng:
        print("  NG %s: %s" % (os.path.basename(f), r))
    if flags:
        print("\nFLAG（原文が基準とずれる・人が確認）:")
        for w, r in flags:
            print("  ", w, r)
    missing = [w for w in WARDS23 if w not in seen]
    if missing:
        print("\n未着:", "、".join(missing))
    if not apply_:
        print("\n--apply で _hitorioya_data.py を書き出す")
        return
    body = ("# -*- coding: utf-8 -*-\n"
            '"""ひとり親家庭支援の一次データ（東京23区）。正本。\n'
            "生成: scripts/merge_hitorioya.py（検算つき）。手で編集しない。\n"
            '取得は agent/research_hitorioya/*.json（区公式ページの原文引用）。"""\n\n'
            'CHECKED = "2026年8月29日"\n\n'
            "WARDS = " + repr(ok) + "\n")
    io.open(OUT, "w", encoding="utf-8").write(body)
    print("\n書き出し: %s（%d区）" % (OUT, len(ok)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main("--apply" in sys.argv)

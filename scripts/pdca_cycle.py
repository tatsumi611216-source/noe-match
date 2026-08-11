# -*- coding: utf-8 -*-
"""施策の効果を測るためのPDCAサイクル管理。

なぜ必要か（2026-08-09）:

この日、看板の掛け替え7本・導線追加37本・内容強化2本を一度に実施した。
だが**変更前の順位を固定していなければ、9月に効果を判定できない**。
GSCデータは上書きされるため、後からは取れない。

Plan   … agent/strategy_2026H2.md（何をやり何をやらないか）
Do     … 施策の実施（gitの履歴に残る）
Check  … **このスクリプト**。施策時点の状態を凍結し、後日その差分を出す
Act    … 差分を見て次のサイクルを決める

使い方:
    python scripts/pdca_cycle.py freeze --note "看板の掛け替え7本"
        現在のGSC状態を agent/pdca/ に凍結する。施策の直後に実行する。

    python scripts/pdca_cycle.py check
        最新のGSCと、凍結した各サイクルを突き合わせて効果を出す。
        判定日（凍結から28日後）を過ぎたものだけが対象。

判定の考え方:

- **28日待つ**。インデックスと再評価に3〜4週かかるため、それ以前の数字は読まない
- 見るのは**順位の変化**と**表示回数の変化**。クリックは母数が小さすぎて判定に使えない
- **対照群を持てない施策が多い**ので、サイト全体の平均変化と比較して切り分ける
  （全体が上がっているなら、施策ではなくドメイン評価の伸びかもしれない）
"""
import datetime
import glob
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(BASE, "agent", "pdca")
WAIT_DAYS = 28


def load_gsc():
    p = os.path.join(BASE, "agent", "gsc_data.json")
    d = json.load(io.open(p, encoding="utf-8"))
    out = {}
    for r in d["by_query_page"]:
        m = re.search(r"/articles/([\w\-]+)/", r.get("page", "") or "")
        if not m:
            continue
        slug = m.group(1)
        e = out.setdefault(slug, {"imp": 0, "clk": 0, "best": 999, "queries": {}})
        e["imp"] += r.get("impressions", 0)
        e["clk"] += r.get("clicks", 0)
        e["best"] = min(e["best"], r.get("position", 999))
        q = (r.get("query") or "").strip()
        if q:
            e["queries"][q] = round(r.get("position", 999), 1)
    return d.get("period"), out


def freeze(note):
    period, gsc = load_gsc()
    today = datetime.date.today()
    obj = {
        "frozen_at": today.isoformat(),
        "judge_at": (today + datetime.timedelta(days=WAIT_DAYS)).isoformat(),
        "note": note,
        "gsc_period": period,
        "articles": gsc,
    }
    os.makedirs(DIR, exist_ok=True)
    path = os.path.join(DIR, "cycle_%s.json" % today.strftime("%Y%m%d"))
    io.open(path, "w", encoding="utf-8").write(
        json.dumps(obj, ensure_ascii=False, indent=1))
    print("凍結: %s" % os.path.basename(path))
    print("  対象 %d本 / 判定日 %s" % (len(gsc), obj["judge_at"]))


def check():
    period, now = load_gsc()
    today = datetime.date.today().isoformat()
    files = sorted(glob.glob(os.path.join(DIR, "cycle_*.json")))
    if not files:
        print("凍結データが無い。まず freeze を実行する")
        return
    L = ["# PDCA 効果測定", "",
         "**自動生成: `scripts/pdca_cycle.py check`**", "",
         "最新GSC期間: {}".format(period), ""]
    for f in files:
        o = json.load(io.open(f, encoding="utf-8"))
        ready = o["judge_at"] <= today
        L.append("## {} ｜ {}".format(o["frozen_at"], o["note"]))
        L.append("")
        L.append("判定日 {} … **{}**".format(
            o["judge_at"], "判定可" if ready else "まだ早い（28日待つ）"))
        L.append("")
        if not ready:
            L.append("")
            continue
        old = o["articles"]
        # 全体の平均変化（対照群の代わり）
        pairs = [(v["best"], now[k]["best"]) for k, v in old.items()
                 if k in now and v["best"] < 999 and now[k]["best"] < 999]
        if pairs:
            avg = sum(b - a for a, b in pairs) / len(pairs)
            L.append("サイト全体の平均順位変化: **{:+.1f}位**（マイナスが改善）".format(avg))
            L.append("")
        rows = []
        for slug, v in old.items():
            n = now.get(slug)
            if not n:
                continue
            d_pos = (n["best"] - v["best"]) if (v["best"] < 999 and n["best"] < 999) else None
            rows.append((d_pos if d_pos is not None else 0, slug, v, n, d_pos))
        rows.sort()
        L.append("| 記事 | 順位 | 表示 | 判定 |")
        L.append("|---|---|---|---|")
        for _, slug, v, n, d_pos in rows[:40]:
            pos = "{:.1f} → {:.1f}".format(v["best"], n["best"]) if d_pos is not None else "—"
            mark = ""
            if d_pos is not None:
                mark = "**改善 {:+.1f}**".format(d_pos) if d_pos < -3 else (
                    "悪化 {:+.1f}".format(d_pos) if d_pos > 3 else "横ばい")
            L.append("| `{}` | {} | {} → {} | {} |".format(
                slug, pos, v["imp"], n["imp"], mark))
        L.append("")
    out = os.path.join(BASE, "agent", "pdca_result.md")
    io.open(out, "w", encoding="utf-8", newline="").write("\n".join(L) + "\n")
    print("生成: agent/pdca_result.md")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "freeze":
        note = sys.argv[3] if len(sys.argv) > 3 else "（記載なし）"
        freeze(note)
    else:
        check()

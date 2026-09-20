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
        # 記事とツールの両方を拾う。ツールは `tools/<slug>` で持ち、記事のslugと衝突させない。
        # （2026-09-21まで /articles/ しか見ておらず、ツールを対象にした施策は
        #   凍結データが空のまま判定日を迎えていた＝測れない計器だった）
        page = r.get("page", "") or ""
        m = re.search(r"/(articles|tools)/([\w\-]+)/", page)
        if not m:
            continue
        slug = m.group(2) if m.group(1) == "articles" else "tools/" + m.group(2)
        e = out.setdefault(slug, {"imp": 0, "clk": 0, "best": 999, "wpos": 0.0, "queries": {}})
        imp = r.get("impressions", 0)
        pos = r.get("position", 999)
        e["imp"] += imp
        e["clk"] += r.get("clicks", 0)
        e["best"] = min(e["best"], pos)
        e["wpos"] += pos * imp          # 表示加重の平均順位（best=最良クエリの順位とは別物）
        q = (r.get("query") or "").strip()
        if q:
            e["queries"][q] = round(pos, 1)
    for e in out.values():
        e["pos"] = round(e["wpos"] / e["imp"], 1) if e["imp"] else None
        del e["wpos"]
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
    n_tool = len([k for k in gsc if k.startswith("tools/")])
    print("  対象 %d本（うちツール %d本） / 判定日 %s" % (len(gsc), n_tool, obj["judge_at"]))
    if ("ツール" in note or "tools/" in note) and n_tool == 0:
        print("  ★警告: noteはツールの施策だが、凍結データにツールが1本も入っていない。"
              "GSCに表示の無いツールは後から差分を取れない（判定不能になる）")


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
        L.append("| ページ | 最良クエリ順位 | 表示加重の平均順位 | 表示 | 判定 |")
        L.append("|---|---|---|---|---|")
        for _, slug, v, n, d_pos in rows[:40]:
            pos = "{:.1f} → {:.1f}".format(v["best"], n["best"]) if d_pos is not None else "—"
            # 表示加重の平均順位。古い凍結データには pos が無いので「—」になる
            wp = "{} → {}".format(v.get("pos") or "—", n.get("pos") or "—")
            mark = ""
            if d_pos is not None:
                mark = "**改善 {:+.1f}**".format(d_pos) if d_pos < -3 else (
                    "悪化 {:+.1f}".format(d_pos) if d_pos > 3 else "横ばい")
                # 順位が上がっていても表示が大きく減っていれば、尾が消えただけのことがある
                if d_pos < -3 and n["imp"] * 2 < v["imp"]:
                    mark += "（表示が半減。順位改善の根拠にならない）"
            L.append("| `{}` | {} | {} | {} → {} | {} |".format(
                slug, pos, wp, v["imp"], n["imp"], mark))
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

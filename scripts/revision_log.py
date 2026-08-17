# -*- coding: utf-8 -*-
"""記事・ツールのリバイス記録を git 履歴から自動生成する。

なぜ手書きの台帳にしないか（2026-08-18 制定）:

この2日で185本規模の一括修正を何度も行った（CTA差し替え42本・体験主張の除去134
ファイル・出口ゼロ解消19本…）。手書きの台帳はこの規模では必ず書き漏れる。
git には全履歴が正確に残っているので、**台帳は履歴から生成するもの**とし、
人が書くのは「なぜ」だけ（＝コミットメッセージに書く）という分業にする。

用途:
1. **効果測定** … リバイス日と、その時点のGSC順位・表示を並べて出す。
   次回のGSC取得（週次）以降、リバイス前後の変化を突合できる
2. **重複作業の防止** … いつ何を直したかが記事単位で引ける
3. **鮮度の把握** … 最終更新が古い記事から並べられる

使い方:
    python scripts/revision_log.py            # agent/revision_log.md を生成
"""
import collections
import io
import json
import os
import re
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "agent", "revision_log.md")


def git_history():
    """slug -> [(date, subject), ...] 新しい順。"""
    r = subprocess.run(
        ["git", "log", "--date=short", "--format=@%ad|%s", "--name-only",
         "--", "articles/*/index.html", "tools/*/index.html"],
        capture_output=True, text=True, cwd=BASE, encoding="utf-8", errors="replace")
    hist = collections.defaultdict(list)
    date, subj = None, None
    for line in r.stdout.splitlines():
        if line.startswith("@"):
            date, subj = line[1:].split("|", 1)
        elif line.strip():
            m = re.match(r"(articles|tools)/([a-z0-9\-]+)/index\.html", line.strip())
            if m and date:
                key = ("tools/" if m.group(1) == "tools" else "") + m.group(2)
                hist[key].append((date, subj))
    return hist


def gsc():
    p = os.path.join(BASE, "agent", "gsc_data.json")
    if not os.path.exists(p):
        return {}, {}
    g = json.load(io.open(p, encoding="utf-8"))
    out = {}
    for r in g["by_page"]:
        m = re.search(r"noe-match\.com/(articles|tools)/([a-z0-9\-]+)/", r["page"])
        if m:
            key = ("tools/" if m.group(1) == "tools" else "") + m.group(2)
            out[key] = r
    return out, g.get("period", {})


def main():
    hist = git_history()
    G, period = gsc()

    # 直近のリバイス日順（新しい順）
    rows = []
    for slug, h in hist.items():
        last_date, last_subj = h[0]
        first_date = h[-1][0]
        r = G.get(slug)
        rows.append(dict(slug=slug, n=len(h), last=last_date, first=first_date,
                         subj=last_subj[:48],
                         pos=(round(r["position"], 1) if r else None),
                         imp=(r["impressions"] if r else 0),
                         ck=(r["clicks"] if r else 0)))
    rows.sort(key=lambda x: (x["last"], x["n"]), reverse=True)

    today = subprocess.run(["git", "log", "-1", "--date=short", "--format=%ad"],
                           capture_output=True, text=True, cwd=BASE).stdout.strip()

    L = ["# リバイス記録（git履歴から自動生成・scripts/revision_log.py）", "",
         "最終コミット日：%s ／ GSC期間：%s〜%s" %
         (today, period.get("start", "?"), period.get("end", "?")), "",
         "**このファイルは手で編集しない。** リバイスの「なぜ」はコミットメッセージに書く。",
         "効果測定は、リバイス日より後のGSC取得と下表の順位・表示を突合して行う。", "",
         "## 直近リバイス順（全%d本）" % len(rows), "",
         "| 最終更新 | 回数 | 順位 | 表示 | ck | ページ | 直近の変更 |",
         "|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append("| %s | %d | %s | %d | %d | `%s` | %s |" %
                 (r["last"], r["n"],
                  ("%.1f" % r["pos"]) if r["pos"] is not None else "—",
                  r["imp"], r["ck"], r["slug"], r["subj"]))

    # 長期未更新（鮮度の逆リスト）
    stale = sorted(rows, key=lambda x: x["last"])[:20]
    L += ["", "## 長く触っていないページ（古い順20本）", "",
          "| 最終更新 | ページ | 順位 | 表示 |", "|---|---|---|---|"]
    for r in stale:
        L.append("| %s | `%s` | %s | %d |" %
                 (r["last"], r["slug"],
                  ("%.1f" % r["pos"]) if r["pos"] is not None else "—", r["imp"]))
    io.open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し:", OUT)
    print("記録対象:", len(rows), "本 / 総リバイス回数:",
          sum(r["n"] for r in rows))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

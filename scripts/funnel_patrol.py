# -*- coding: utf-8 -*-
"""検索で射程内にある記事の「導線」を巡回して、欠けているものを出す。

なぜ必要か（2026-08-18の実測）:

quality_audit.py は**壊れているか**を見る。これは**繋がっているか**を見る。
GSCで射程内（30位以内・表示3以上）の46本を調べたところ、
クリック上位のほぼ全てが広告ゼロ・LINE導線ゼロだった。

  with-seriousness-data   5.9位  5click  広告0  LINE0
  civil-servant-guide    13.4位  4click  広告0  LINE0
  kyoto-guide            17.8位  4click  広告0  LINE0

流入のある場所に収益経路が無く、経路のある場所に流入が無い。
これは 2026-08-09 に台帳が指摘した「①と②のすれ違い」がまだ残っているということ。

判定の考え方:

- **集客装置クラスタ（A・F）は広告ゼロでも欠陥ではない。** KPIがLINE@登録だから。
  ただしLINE導線が無いのは欠陥。
- **回収クラスタは広告が無いのが欠陥。** ただし台帳のYMYL枠・文脈の制約があるので、
  「置ける案件があるのに置いていない」場合だけを指摘する。
- 順位が高いほど損失が大きいので、**順位×表示回数で重みをつける**。

使い方:
    python scripts/funnel_patrol.py           # agent/funnel_patrol.md を生成
    python scripts/funnel_patrol.py --json
"""
import glob
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "agent", "funnel_patrol.md")

# 集客装置＝広告が無くても欠陥ではないクラスタ（KPIはLINE@登録）
LEAD_MAGNET = set("""
garugaru-ki-guide garugaru-ki-itsumade garugaru-otto-taiou garugaru-nai-hito
garugaru-gibo-jitsubo garugaru-doukyo garugaru-ueno-ko garugaru-otto-genkai
garugaru-sangoutsu-chigai sango-crisis-guide sango-iraira sango-kaji-buntan
sango-otto-kirai sango-rikon sango-satogaeri satogaeri-shinai shinseiji-menkai
maternity-blue-chigai futarime-sango gijikka-ikitakunai ikukyu-fuufu-doji
photo-tips profile-photo profile-text konkatsu-photo-guide mens-make-konkatsu
message-strategy line-exchange pairs-men pairs-women with-women women-strategy
first-date-guide first-date-spot date-plan-2kaime ouchi-date-guide
ouchi-date-sakuhin amenohi-date-guide date-sakuhin-ng sakuhin-kachikan
enkyori-renai-guide anti-fraud fraud-detection fraud-statistics safety-guide
privacy-protection kekkon-sokou-chousa
""".split())

IN_RANGE = 30.0     # 射程内とみなす順位
MIN_IMP = 3         # 表示回数の下限


def gsc():
    p = os.path.join(BASE, "agent", "gsc_data.json")
    g = json.load(io.open(p, encoding="utf-8"))
    out = {}
    for r in g["by_page"]:
        m = re.search(r"/(articles|tools)/([a-z0-9\-]+)/", r["page"])
        if m:
            out[m.group(2)] = r
    return out, g["period"]


def check(slug, path, rec):
    h = io.open(path, encoding="utf-8").read()
    tools = sorted(set(re.findall(r"/tools/([a-z0-9\-]+)/", h)))
    # ★2026-08-18: A8だけ数えて afb(t.afi-b.com) を見落とし、
    #   広告が入っている記事を「広告無し」と誤判定した。ASPは複数ある。
    ads = len(re.findall(r'<a[^>]*href="https://(?:px\.a8\.net|t\.afi-b\.com)', h))
    line = "lin.ee" in h
    rel = len(re.findall(r'<div class="related"', h))
    gaps = []

    # 順位が良いほど、欠けの損失が大きい
    weight = rec["impressions"] * max(0.0, (IN_RANGE - rec["position"]) / IN_RANGE)

    if not tools:
        gaps.append(("ツール未接続", "クラスタの核へ送っていない"))
    if not rel:
        gaps.append(("関連リンク無し", "回遊の経路が無い"))

    if slug in LEAD_MAGNET:
        if not line:
            gaps.append(("LINE導線無し", "集客装置なのに主KPIへの経路が無い"))
    else:
        if ads == 0:
            gaps.append(("広告無し", "回収クラスタなのに収益経路が無い"))

    return dict(slug=slug, ck=rec["clicks"], imp=rec["impressions"],
                pos=round(rec["position"], 1), weight=round(weight, 1),
                tools=len(tools), ads=ads, line=int(line), rel=rel,
                magnet=slug in LEAD_MAGNET, gaps=gaps)


def main():
    G, period = gsc()
    rows = []
    for kind in ("articles", "tools"):
        for p in sorted(glob.glob(os.path.join(BASE, kind, "*", "index.html"))):
            slug = os.path.basename(os.path.dirname(p))
            r = G.get(slug)
            if not r or r["position"] > IN_RANGE or r["impressions"] < MIN_IMP:
                continue
            rows.append(check(slug, p, r))
    rows.sort(key=lambda r: -r["weight"])

    if "--json" in sys.argv:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return

    bad = [r for r in rows if r["gaps"]]
    L = ["# 導線巡回（自動生成・scripts/funnel_patrol.py）", "",
         "GSC期間：%s 〜 %s" % (period["start"], period["end"]), "",
         "対象：**%d位以内・表示%d回以上**の %d本。うち **%d本に欠け**がある。" %
         (int(IN_RANGE), MIN_IMP, len(rows), len(bad)), "",
         "重み＝表示回数 ×（順位の良さ）。**上にあるものほど、直したときの効きが大きい**。", "",
         "| 重み | 順位 | 表示 | ck | ページ | 欠けているもの |",
         "|---|---|---|---|---|---|"]
    for r in bad:
        L.append("| %.1f | %.1f | %d | %d | `%s`%s | %s |" %
                 (r["weight"], r["pos"], r["imp"], r["ck"], r["slug"],
                  "（集客装置）" if r["magnet"] else "",
                  " / ".join(g[0] for g in r["gaps"])))
    L += ["", "## 欠けの内訳", ""]
    import collections
    c = collections.Counter(g[0] for r in bad for g in r["gaps"])
    L += ["| 種類 | 件数 |", "|---|---|"] + \
         ["| %s | %d |" % (k, v) for k, v in c.most_common()]
    L += ["", "## 判定の前提", "",
          "- **集客装置クラスタ（ガルガル・産後・プロフィール・デート・安全）は広告ゼロでも欠陥ではない。**",
          "  KPIがLINE@登録だから。ただしLINE導線が無いのは欠陥として数える",
          "- 回収クラスタは広告ゼロを欠陥として数える。ただし台帳のYMYL枠・文脈の制約があるため、",
          "  **実際に置けるかは案件台帳（agent/AGENT.md）で個別に確認すること**", ""]
    io.open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し:", OUT)
    print("射程内 %d本 / 欠けあり %d本" % (len(rows), len(bad)))
    for k, v in c.most_common():
        print("  %-14s %d" % (k, v))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

# -*- coding: utf-8 -*-
"""既存記事を「①流入 × ②実効単価 × ③接続」の3観点で棚卸しし、推奨アクションを出す。

なぜこの3観点か（2026-08-09に確立）:

収益は3つの掛け算で決まる。どれか1つがゼロなら全体がゼロになる。

  ① 検索される × 勝てる … 希少資源。GSCの表示回数と順位で測る
  ② 単価 × 確定率      … 余剰資源（提携182件）。額面ではなく実効単価で見る
  ③ 接続               … ①と②が同じ記事に載っているか

この日の実測で、①と②が完全にすれ違っていることが分かった。
流入上位14本は②が不明、②が最高（実効24,000円）の nurse-guide は87位。
**記事を増やす前に、この配置を直すほうが速い。**

判定の前提:

- 未インデックスの記事は「①がゼロ」ではなく「①が未測定」。区別しないと判断を誤る。
  2026-08-09時点で、広告のある100本中42本が未インデックスだった。
- 台帳に単価の記載が無い案件は「②がゼロ」ではなく「②が不明」。
  この混同で、実際にCTAがある記事を「案件なし」と誤読した。

使い方:
    python scripts/article_audit.py      # agent/article_audit.md を再生成
"""
import collections
import glob
import io
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "agent", "article_audit.md")
# 確定率が台帳に無い案件の暫定値。実測が入るまでの仮置きであることを明示する。
ASSUMED_RATE = 0.6
IN_RANGE = (11, 50)   # 射程内。ここを強化すると10位以内に届きうる


def ledger():
    """URL断片 → (案件名, 単価, 確定率) を作る。"""
    out = []
    for line in io.open(os.path.join(BASE, "agent", "AGENT.md"), encoding="utf-8"):
        if not line.startswith("|"):
            continue
        c = [x.strip() for x in line.split("|")]
        if len(c) < 4:
            continue
        m = re.search(r"https://(?:px\.a8\.net|t\.afi-b\.com)[^\s|]*\?([^\s|\"]+)", c[2])
        if not m:
            continue
        yens = re.findall(r"([0-9,]{3,7})\s*円", c[3])
        yen = max(int(x.replace(",", "")) for x in yens) if yens else 0
        r = re.search(r"確定率\s*([0-9.]+)\s*%", c[3])
        out.append((m.group(1)[:28], re.sub(r"（.*", "", c[1]).strip(),
                    yen, float(r.group(1)) / 100 if r else None))
    return out


def main():
    led = ledger()

    # 記事 → 貼られている案件のうち実効単価が最大のもの
    placed, title, cta = {}, {}, {}
    for f in glob.glob(os.path.join(BASE, "articles", "*", "index.html")):
        slug = os.path.basename(os.path.dirname(f))
        t = io.open(f, encoding="utf-8", errors="replace").read()
        if "noindex" in t:
            continue
        hits = [(y * (r if r is not None else ASSUMED_RATE), n, y, r)
                for frag, n, y, r in led if frag in t]
        placed[slug] = max(hits) if hits else None
        m = re.search(r"<title>([^<]*)</title>", t)
        title[slug] = (m.group(1).split("｜")[0].strip() if m else slug)
        cta[slug] = len(re.findall(r'rel="nofollow sponsored noopener"', t))

    # インデックス状況
    idx = {}
    p = os.path.join(BASE, "agent", "index_status.json")
    if os.path.exists(p):
        for u, v in json.load(io.open(p, encoding="utf-8"))["results"].items():
            m = re.search(r"/articles/([\w\-]+)/", u)
            if m:
                idx[m.group(1)] = v.get("coverageState", "")

    # GSC
    gsc = collections.defaultdict(list)
    p = os.path.join(BASE, "agent", "gsc_data.json")
    if os.path.exists(p):
        for r in json.load(io.open(p, encoding="utf-8"))["by_query_page"]:
            m = re.search(r"/articles/([\w\-]+)/", r.get("page", "") or "")
            if m:
                gsc[m.group(1)].append(r)

    buckets = collections.defaultdict(list)
    for slug, best in placed.items():
        rs = gsc.get(slug, [])
        imp = sum(r.get("impressions", 0) for r in rs)
        clk = sum(r.get("clicks", 0) for r in rs)
        pos = min((r.get("position", 999) for r in rs), default=None)
        cov = idx.get(slug, "未測定")
        indexed = "and indexed" in cov

        eff = best[0] if best else 0
        known_price = bool(best and best[2])

        if not indexed:
            key = "A. 未インデックス（①が未測定）"
        elif pos is None or imp == 0:
            key = "D. 表示ゼロ（①がゼロ＝圏外）"
        elif IN_RANGE[0] <= pos <= IN_RANGE[1]:
            key = "B. 射程内（①が生きている）"
        elif pos < IN_RANGE[0]:
            key = "S. 10位以内（①が最大）"
        else:
            key = "C. 51位以下（①が弱い）"
        buckets[key].append((eff, known_price, imp, clk, pos, slug, best, cov))

    ACT = {
        "S. 10位以内（①が最大）": "**②を最大化する。**流入が既にあるので、より実効単価の高い案件に差し替えられないか検討する。単価不明なら真っ先に調べる",
        "B. 射程内（①が生きている）": "**磨いて10位以内へ。**ターゲット語が本文にあるか、競合が持っていない節があるかを見る",
        "C. 51位以下（①が弱い）": "**看板を掛け替える。**本文は活かし、タイトル・h1・導入をサイト外の固有修飾へ寄せる（到達率23.5→68.8）",
        "D. 表示ゼロ（①がゼロ＝圏外）": "同上。`silent_articles.md` の寄せ直し対象",
        "A. 未インデックス（①が未測定）": "**GSCで申請する。**申請すれば7〜8日で100%、放置すると1.7%。判定はその後",
    }

    L = ["# 記事監査：① 流入 × ② 実効単価 × ③ 接続", "",
         "**自動生成: `scripts/article_audit.py`。手で編集しない。**", "",
         "収益は3つの掛け算。どれか1つがゼロなら全体がゼロ。",
         "希少なのは①だけで、②は提携182件あって余っている。**①のある場所に②を寄せるのが基本方針**。", "",
         "実効単価 = 単価 × 確定率。確定率が台帳に無い案件は {} で仮置きしている（要実測）。".format(ASSUMED_RATE), ""]

    for key in ["S. 10位以内（①が最大）", "B. 射程内（①が生きている）",
                "C. 51位以下（①が弱い）", "D. 表示ゼロ（①がゼロ＝圏外）",
                "A. 未インデックス（①が未測定）"]:
        items = sorted(buckets.get(key, []), key=lambda x: (-x[2], -x[0]))
        L.append("## {}（{}本）".format(key, len(items)))
        L.append("")
        L.append("> {}".format(ACT[key]))
        L.append("")
        if not items:
            L.append("なし")
            L.append("")
            continue
        L.append("| 表示 | クリック | 順位 | 実効単価 | 記事 | 載っている案件 |")
        L.append("|---|---|---|---|---|---|")
        for eff, known, imp, clk, pos, slug, best, cov in items[:40]:
            price = "{:,}円".format(int(eff)) if known else ("**単価不明**" if best else "案件なし")
            L.append("| {} | {} | {} | {} | `{}` | {} |".format(
                imp, clk, "{:.1f}".format(pos) if pos else "—", price, slug,
                best[1][:20] if best else "—"))
        if len(items) > 40:
            L.append("")
            L.append("※他 {} 本は省略".format(len(items) - 40))
        L.append("")

    L.append("## 全記事一覧（テーマ × ①②③）")
    L.append("")
    L.append("`③` はCTAの設置数。**①があるのに③が0なら、貼るだけで経路ができる。**")
    L.append("")
    L.append("| 判定 | テーマ | ①順位 | ①表示 | ①クリック | ②実効単価 | ③CTA | 記事 |")
    L.append("|---|---|---|---|---|---|---|---|")
    allrows = []
    for key, items in buckets.items():
        for it in items:
            allrows.append((key,) + it)
    order = {"S": 0, "B": 1, "C": 2, "D": 3, "A": 4}
    allrows.sort(key=lambda x: (order.get(x[0][0], 9),
                                x[5] if x[5] else 9999,   # 順位の良い順
                                -x[3]))                    # 同順位なら表示回数の多い順
    for key, eff, known, imp, clk, pos, slug, best, cov in allrows:
        if key.startswith("A"):
            rank, shown, clicks = "未計測", "—", "—"
        elif not imp:
            rank, shown, clicks = "圏外", "0", "0"
        else:
            rank = "{:.1f}".format(pos)
            shown, clicks = str(imp), str(clk)
        two = "{:,}円".format(int(eff)) if known else ("単価不明" if best else "**なし**")
        L.append("| {} | {} | {} | {} | {} | {} | {} | `{}` |".format(
            key[0], title.get(slug, "")[:30], rank, shown, clicks, two, cta.get(slug, 0), slug))
    L.append("")

    # クエリに答えていない記事の検出（2026-08-09追加）
    L.append("## ★クエリに答えていない記事")
    L.append("")
    L.append("順位が付いているのに、そのクエリの語が本文にほとんど出てこない記事。")
    L.append("**開いても答えが見つからないので、順位があってもクリックされない。**")
    L.append("")
    L.append("実例（2026-08-09に発見・修正済み）: `with-seriousness-data` は「with 結婚率」で4.2位・30表示だったが、")
    L.append("本文に「結婚率」が**1回しか無かった**。`over50-guide` は「婚活サイト 50代」で上位なのに")
    L.append("本文は「マッチングアプリ」16回に対し「婚活サイト」12回で主語が逆だった。")
    L.append("")
    L.append("**答えが「その数字は公表されていない」でも構わない。**むしろ事業者は自社の不都合を書けないので空く。")
    L.append("")
    L.append("| 順位 | 表示 | クエリ | 本文での出現 | 記事 |")
    L.append("|---|---|---|---|---|")
    miss = []
    for slug, rs in gsc.items():
        f = os.path.join(BASE, "articles", slug, "index.html")
        if not os.path.exists(f):
            continue
        body = re.sub(r"<[^>]+>", "", re.sub(r"<script.*?</script>", "",
                      io.open(f, encoding="utf-8", errors="replace").read(), flags=re.S))
        for r in rs:
            qy = (r.get("query") or "").strip()
            if not qy:
                continue
            # クエリを語に割り、本文での最小出現回数を見る
            words = [w for w in re.split(r"[\s　]+", qy) if len(w) >= 2]
            if not words:
                continue
            counts = {w: body.count(w) for w in words}
            weakest = min(counts, key=counts.get)
            if counts[weakest] <= 2 and r.get("impressions", 0) >= 1:
                miss.append((r.get("position", 999), r.get("impressions", 0), qy,
                             "{}={}回".format(weakest, counts[weakest]), slug))
    for pos, imp, qy, detail, slug in sorted(miss)[:30]:
        L.append("| {:.1f} | {} | {} | **{}** | `{}` |".format(pos, imp, qy, detail, slug))
    if not miss:
        L.append("| — | — | 該当なし | — | — |")
    L.append("")

    unknown = [s for s, b in placed.items() if b and not b[2]]
    L.append("## ②が測れていない記事（{}本）".format(len(unknown)))
    L.append("")
    L.append("CTAは貼られているが、台帳に単価の記載が無いため実効単価を計算できない。")
    L.append("**空欄は「案件なし」ではない。**この混同で判断を誤ったことがある（2026-08-09）。")
    L.append("afb / A8 の管理画面で単価と確定率を確認し、`AGENT.md` に追記すること。")
    L.append("")
    L.append(", ".join("`{}`".format(s) for s in sorted(unknown)[:60]))
    L.append("")

    io.open(OUT, "w", encoding="utf-8", newline="").write("\n".join(L) + "\n")
    print("生成: agent/article_audit.md")
    for k in sorted(buckets):
        print("  {} : {}本".format(k, len(buckets[k])))
    print("  ②不明 : {}本".format(len(unknown)))


if __name__ == "__main__":
    main()

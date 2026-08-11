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


def next_move(pos, imp, eff, known, cta, gap, indexed, role):
    """④ 順位を上げる／収益化するための打ち手を1つに絞って返す。

    優先順位は「効果が出るまでの速さ」で決めている。
    インデックス > クエリ不一致 > CTA欠落 > 単価 > 看板 > 一次情報。

    **role で打ち手の「目的」が変わる**（2026-08-09・CEO指摘を2回反映）。

    - 主戦場（新生活・お金）… 磨く目的は **成約**。単価の高い案件を載せる
    - 入口（アプリ・データ）… 磨く目的は **送客量の最大化と流入の防衛**

    入口は主力4アプリに案件が無いため、その記事単体では成約しない。
    だが**磨かない理由にはならない**。順位が上がればクリックが増え、
    主戦場へ送る量が増える。加えて with-seriousness-data は4.2位・30表示で
    サイト最大の流入源であり、ここが落ちるとサイトの流入がほぼゼロになる。
    **内容の強化は入口にも必要。変わるのは②の扱いだけ。**
    """
    if not indexed:
        return "**GSCで申請**（7〜8日で100%、放置は1.7%）"
    if gap:
        w, c = gap
        return "**「{}」を本文に足す**（現在{}回・順位は付いているが答えていない）".format(w, c)
    if cta == 0:
        return "**案件を設置**（①はあるが③が無い。貼るだけで経路ができる）"
    if pos is not None and pos <= 10:
        if role == "入口":
            return "**流入源。守る＋導線を太く**（この順位を落とさない。主戦場への送客を増やす）"
        return "**②を最大化**（流入がある。より高単価の案件に差し替えられないか）"
    if role != "入口" and known and eff and eff < 3000:
        return "実効{:,}円は低い。**高単価案件への差し替えを検討**".format(int(eff))
    if pos is not None and pos <= 50:
        if role == "入口":
            return "**一次情報を足す**（目的は送客量。順位が上がれば主戦場へ送れる数が増える）"
        return "**一次情報を足す**（実測値・体験・競合が持たない節）"
    if pos is not None:
        return "**看板を掛け替え**（本文は活かし、固有修飾へ寄せる）"
    return "**看板を掛け替え**（表示ゼロ＝圏外）"


def build_roles():
    """index.html のグループ分けから、記事の役割（主戦場／入口）を決める。"""
    p = os.path.join(BASE, "index.html")
    if not os.path.exists(p):
        return {}
    idx = io.open(p, encoding="utf-8", errors="replace").read()
    pos = [m.start() for m in re.finditer(r"<h3", idx)] + [len(idx)]
    role = {}
    for a, b in zip(pos, pos[1:]):
        blk = idx[a:b]
        if not re.search(r"（\d+記事）", blk):
            continue
        name = re.sub(r"（\d+記事）", "", re.sub("<[^>]+>", "", blk[:blk.find("</h3>")])).strip()
        slugs = set(re.findall(r"/articles/([\w\-]+)/", blk))
        if "新生活" in name or "お金" in name:
            r = "**主戦場**"
        elif "アプリ選び" in name or "データ" in name:
            r = "入口"
        else:
            r = "その他"
        for sg in slugs:
            role[sg] = r
    return role


def main():
    led = ledger()
    ROLE = build_roles()

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

    # クエリに答えていない記事（④の判定に使う）
    qgap = {}
    for slug, rs in gsc.items():
        f = os.path.join(BASE, "articles", slug, "index.html")
        if not os.path.exists(f):
            continue
        body = re.sub(r"<[^>]+>", "", re.sub(r"<script.*?</script>", "",
                      io.open(f, encoding="utf-8", errors="replace").read(), flags=re.S))
        # 略語・表記ゆれ・固有名詞の一部は本文に入れても不自然なので除外する。
        # 「マチアプ」を記事に足しても読者の役に立たない（検索者の口語であって記事の語ではない）。
        SKIP = {"マチアプ", "アプリ", "サイト", "おすすめ", "比較", "人気", "無料", "口コミ",
                "ランキング", "使い方", "始め方", "選び方", "とは"}
        # 表示2回以上のクエリだけを判定に使う。GSCの56%は表示1回以下で、
        # そこから打ち手を出すのは「1件のデータで結論を出す」失敗の再演になる
        # （実害: 表示1回の「近く出会い」を根拠に nagoya-guide へ節を足した）。
        # スペースの無いクエリは語に分割できないため判定しない（丸ごとの部分一致は厳しすぎる）。
        worst = None
        for r in sorted(rs, key=lambda x: x.get("position", 999)):
            if r.get("impressions", 0) < 2:
                continue
            q = (r.get("query") or "").strip()
            words = [w for w in re.split(r"[\s　]+", q) if len(w) >= 2 and w not in SKIP]
            if len(words) < 2 and "　" not in q and " " not in q:
                continue
            for w in words:
                c = body.count(w)
                if c <= 2 and (worst is None or c < worst[1]):
                    worst = (w, c)
        if worst:
            qgap[slug] = worst

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
    L.append("**役割**: 主戦場＝新婚・新生活の実務（成約のために磨く）／入口＝アプリ・データ系（送客と防衛のために磨く）")
    L.append("")
    L.append("**順位の読み方**: ①順位は全クエリの最良値。GSCの56%は表示1回以下なので、")
    L.append("表示の少ない行の順位はノイズを含む。④の「本文に足す」判定は表示2回以上のクエリのみを根拠にしている。")
    L.append("")
    L.append("| ①順位 | ①表示 | 役割 | ②キャッシュポイント | ③CTA | ④打ち手 | テーマ | 記事 |")
    L.append("|---|---|---|---|---|---|---|---|")
    allrows = []
    for key, items in buckets.items():
        for it in items:
            allrows.append((key,) + it)
    # 順位の良い順（未計測・圏外は末尾）
    allrows.sort(key=lambda x: (x[5] if x[5] and x[5] < 999 else 9999, -x[3]))
    for key, eff, known, imp, clk, pos, slug, best, cov in allrows:
        indexed = not key.startswith("A")
        if not indexed:
            rank, shown = "未計測", "—"
        elif not imp:
            rank, shown = "圏外", "0"
        else:
            rank, shown = "{:.1f}".format(pos), str(imp)
        two = ("{}／{:,}円".format(best[1][:12], int(eff)) if known
               else ("{}／単価不明".format(best[1][:12]) if best else "**なし**"))
        role = ROLE.get(slug, "その他")
        move = next_move(pos if (indexed and imp) else None, imp, eff, known,
                         cta.get(slug, 0), qgap.get(slug), indexed, role)
        L.append("| {} | {} | {} | {} | {} | {} | {} | `{}` |".format(
            rank, shown, role, two, cta.get(slug, 0), move, title.get(slug, "")[:24], slug))
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
            # 表示2回以上のみ。分割できないクエリは判定しない（④側の判定と同じ基準に揃える）
            if not qy or r.get("impressions", 0) < 2:
                continue
            words = [w for w in re.split(r"[\s　]+", qy) if len(w) >= 2]
            if len(words) < 2 and " " not in qy and "　" not in qy:
                continue
            counts = {w: body.count(w) for w in words}
            if not counts:
                continue
            weakest = min(counts, key=counts.get)
            if counts[weakest] <= 2:
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

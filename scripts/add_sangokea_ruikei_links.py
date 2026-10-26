# -*- coding: utf-8 -*-
"""産後ケアの日帰り型・訪問型の2本を、記事一覧と産後クラスタに接続する（2026-08-29）。

factory_audit が求める条件を満たすため:
  ・articles/index.html から必ずリンクする（未リンクは構造エラー）
  ・被リンクを最低3本つける

アンカーは検索語入りにする（8/24の知見: ブランド語アンカーは順位に効かない）。
接続先は「既に人が着地しているクラスタ」＝産後クラスタから引く（8/27の知見）。
冪等: 既にリンクがあるページは触らない。
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEW = [
    ("sangokea-higaeri",
     "産後ケアの日帰り型はいくら？43自治体の料金と、単価を持たない12自治体"),
    ("sangokea-houmon",
     "産後ケアの訪問型はいくら？43自治体の料金と、枠が共通で先に消える9自治体"),
]

# 記事一覧の挿入位置（この行の直後に差し込む）
ANCHOR = ('<a href="/articles/sangokea-shukuhaku/" class="arc-link">'
          '<span class="arc-no">＋</span>産後ケアの宿泊型はいくら？金額より「数え方」で差がつく</a>')

BLOCK = """
<!-- SANGOKEA-RUIKEI-LINK -->
<div style="border-left:3px solid #7c2e42;background:#faf8f5;padding:16px 18px;margin:28px 0;">
<p style="margin:0 0 6px;font-size:.78rem;letter-spacing:.1em;color:#7c2e42;">関連データ</p>
<p style="margin:0;font-size:.92rem;line-height:1.9;color:#3a4148;">
産後ケアは類型ごとに自己負担も回数の枠も違います。
<a href="/articles/sangokea-higaeri/" style="color:#7c2e42;font-weight:700;">産後ケアの日帰り型はいくら？43自治体の料金と単価の有無</a>と、
<a href="/articles/sangokea-houmon/" style="color:#7c2e42;font-weight:700;">産後ケアの訪問型はいくら？自宅に来てもらう場合の自己負担</a>で、
各自治体の公表文のまま確認できます。
</p>
</div>
"""

TARGETS = [
    "tools/sangokea-ryokin/index.html",
    "articles/sangokea-nankai/index.html",
    "articles/sangokea-josei/index.html",
    "articles/sangokea-shukuhaku/index.html",
    "articles/sangokea-moshikomi/index.html",
    "articles/sango-crisis-guide/index.html",
    "articles/futarime-sango/index.html",
    "articles/sango-satogaeri/index.html",
    "tools/sango-recovery-check/index.html",
]


def add_to_index():
    p = os.path.join(ROOT, "articles", "index.html")
    h = io.open(p, encoding="utf-8").read()
    if all(("/articles/%s/" % s) in h for s, _ in NEW):
        print("記事一覧: 既にリンクあり")
        return
    if ANCHOR not in h:
        print("記事一覧: 挿入位置が見つからない（要手当て）")
        return
    add = "".join(
        '\n        <a href="/articles/%s/" class="arc-link">'
        '<span class="arc-no">＋</span>%s</a>' % (s, t)
        for s, t in NEW if ("/articles/%s/" % s) not in h)
    io.open(p, "w", encoding="utf-8").write(h.replace(ANCHOR, ANCHOR + add, 1))
    print("記事一覧: %d件を追加" % len(NEW))


def main():
    add_to_index()
    done, skip = [], []
    for rel in TARGETS:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            skip.append((rel, "ファイルなし")); continue
        h = io.open(p, encoding="utf-8").read()
        if "SANGOKEA-RUIKEI-LINK" in h or "/articles/sangokea-higaeri/" in h:
            skip.append((rel, "既にリンクあり")); continue
        if "<footer" not in h:
            skip.append((rel, "footerなし")); continue
        h2 = h.replace("<footer", BLOCK + "<footer", 1)
        if h2 == h:
            skip.append((rel, "挿入失敗")); continue
        io.open(p, "w", encoding="utf-8").write(h2)
        done.append(rel)
    print("被リンク挿入: %d件" % len(done))
    for s in done:
        print("  +", s)
    if skip:
        print("スキップ: %d件" % len(skip))
        for s, r in skip:
            print("  -", s, r)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

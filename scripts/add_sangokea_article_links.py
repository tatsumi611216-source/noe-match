# -*- coding: utf-8 -*-
"""産後ケアのデータ記事2本を、記事一覧と関連ページに接続する（2026-08-27）。

factory_audit が求める条件を満たすため:
  ・articles/index.html から必ずリンクする（未リンクは構造エラー）
  ・被リンクを最低3本つける

アンカーは検索語入りにする（8/24の知見: ブランド語アンカーは順位に効かない）。
冪等: 既にリンクがあるページは触らない。
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEW = [
    ("sangokea-nankai",
     "産後ケアは何回使える？43自治体の上限一覧と「合算枠」の落とし穴"),
    ("sangokea-josei",
     "産後ケアの助成はいくら？非課税世帯の減免と所得を問わない減額枠"),
]

# 記事一覧の挿入位置（この記事の直後に差し込む）
ANCHOR = '<a href="/articles/daredemo-tsuen-ryokin/" class="arc-link">'

BLOCK = """
<!-- SANGOKEA-DATA-LINK -->
<div style="border-left:3px solid #7c2e42;background:#faf8f5;padding:16px 18px;margin:28px 0;">
<p style="margin:0 0 6px;font-size:.78rem;letter-spacing:.1em;color:#7c2e42;">関連データ</p>
<p style="margin:0;font-size:.92rem;line-height:1.9;color:#3a4148;">
産後ケアは自治体ごとに使える回数も助成の内容も違います。
<a href="/articles/sangokea-nankai/" style="color:#7c2e42;font-weight:700;">産後ケアは何回使える？43自治体の上限一覧</a>と、
<a href="/articles/sangokea-josei/" style="color:#7c2e42;font-weight:700;">産後ケアの助成はいくら？非課税世帯の減免と所得を問わない減額枠</a>で、
各自治体の公表文のまま確認できます。
</p>
</div>
"""

TARGETS = [
    "tools/sangokea-ryokin/index.html",
    "articles/daredemo-tsuen-ryokin/index.html",
    "articles/sango-crisis-guide/index.html",
    "articles/futarime-sango/index.html",
    "articles/sango-satogaeri/index.html",
    "tools/sango-recovery-check/index.html",
]


def add_to_index():
    p = os.path.join(ROOT, "articles", "index.html")
    h = io.open(p, encoding="utf-8").read()
    if "/articles/sangokea-nankai/" in h:
        print("skip(一覧に設置済み)")
        return
    i = h.find(ANCHOR)
    if i < 0:
        print("一覧の挿入位置が見つかりません")
        return
    end = h.find("</a>", i) + 4
    add = "".join(
        '\n        <a href="/articles/%s/" class="arc-link"><span class="arc-no">＋</span>%s</a>'
        % (slug, title) for slug, title in NEW)
    io.open(p, "w", encoding="utf-8").write(h[:end] + add + h[end:])
    print("記事一覧に2本を追加しました")


def add_links():
    added = skipped = 0
    for rel in TARGETS:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print("NOT FOUND:", rel)
            continue
        h = io.open(p, encoding="utf-8").read()
        if "/articles/sangokea-nankai/" in h:
            print("skip(設置済み):", rel)
            skipped += 1
            continue
        i = h.find("<!-- LINE-CTA -->")
        if i < 0:
            i = h.find("<footer>")
        if i < 0:
            print("挿入位置なし:", rel)
            continue
        io.open(p, "w", encoding="utf-8").write(h[:i] + BLOCK + h[i:])
        print("added:", rel)
        added += 1
    print("設置 %d本 / スキップ %d本" % (added, skipped))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    add_to_index()
    add_links()

# -*- coding: utf-8 -*-
"""公的統計のデータ記事3本を、記事一覧と関連ページに接続する（2026-08-27）。

factory_audit は「articles/index.html から未リンク」を構造エラーとして弾く。
アンカーは検索語入りにする（8/24の知見）。冪等。
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEW = [
    ("shougai-mikonritsu-data",
     "生涯未婚率はいま何%？正式名称「50歳時未婚割合」の最新値と40年の推移"),
    ("rikonritsu-data",
     "離婚率はいまどれくらい？件数・都道府県別・同居期間別を実数で"),
    ("tomobataraki-wariai-data",
     "共働き世帯の割合はどれくらい？専業主婦世帯との比較と40年の推移"),
]

ANCHOR = '<a href="/articles/daredemo-tsuen-ryokin/" class="arc-link">'

BLOCK = """
<!-- TOUKEI-DATA-LINK -->
<div style="border-left:3px solid #7c2e42;background:#faf8f5;padding:16px 18px;margin:28px 0;">
<p style="margin:0 0 6px;font-size:.78rem;letter-spacing:.1em;color:#7c2e42;">関連データ</p>
<p style="margin:0;font-size:.92rem;line-height:1.9;color:#3a4148;">
公的統計の最新値を、出典と確認日つきで整理しています。
<a href="/articles/shougai-mikonritsu-data/" style="color:#7c2e42;font-weight:700;">生涯未婚率はいま何%</a>、
<a href="/articles/rikonritsu-data/" style="color:#7c2e42;font-weight:700;">離婚率の件数・都道府県別・同居期間別</a>、
<a href="/articles/tomobataraki-wariai-data/" style="color:#7c2e42;font-weight:700;">共働き世帯の割合と専業主婦世帯との比較</a>。
</p>
</div>
"""

TARGETS = [
    "articles/hatsushon-nenmei-data/index.html",
    "articles/success-rate-data/index.html",
    "articles/appkon-wariai-data/index.html",
    "articles/kekkon-madeno-kikan-data/index.html",
    "articles/sango-rikon/index.html",
    "tools/rikongo-seikatsuhi/index.html",
    "tools/seikatsuhi-simulator/index.html",
]


def add_to_index():
    p = os.path.join(ROOT, "articles", "index.html")
    h = io.open(p, encoding="utf-8").read()
    if "/articles/rikonritsu-data/" in h:
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
    print("記事一覧に3本を追加しました")


def add_links():
    added = skipped = 0
    for rel in TARGETS:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print("NOT FOUND:", rel)
            continue
        h = io.open(p, encoding="utf-8").read()
        if "/articles/rikonritsu-data/" in h:
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

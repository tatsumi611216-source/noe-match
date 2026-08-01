#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""記事集合の整合性チェック。

articles/ ・ sitemap.xml ・ index.html の3者が同じ記事集合を指していることを
機械的に確認する。過去に index.html への載せ漏れ（7本）と記事数表記の乖離が
発生しているため、週次実行の最後に必ず走らせること。

    python scripts/check_consistency.py

不整合があれば内容を表示して終了コード1を返す。
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_article_dirs():
    """articles/ 配下の実ディレクトリを、実記事とリダイレクトstubに分ける。"""
    dirs = {p.name for p in (ROOT / "articles").iterdir() if p.is_dir()}
    stubs = set(json.loads((ROOT / "redirects.json").read_text(encoding="utf-8")))
    return dirs - stubs, dirs & stubs


def slugs_in(path, pattern=r"/articles/([^/\"<>]+)/"):
    text = path.read_text(encoding="utf-8")
    return set(re.findall(pattern, text))


def report(errors, label, missing_from, extra_in, left_name, right_name):
    if missing_from:
        errors.append(
            f"{label}: {right_name} に無い（{len(missing_from)}件）"
            f" → {', '.join(sorted(missing_from))}"
        )
    if extra_in:
        errors.append(
            f"{label}: {left_name} に無い（{len(extra_in)}件）"
            f" → {', '.join(sorted(extra_in))}"
        )


def main():
    errors = []
    articles, stubs = load_article_dirs()
    sitemap = slugs_in(ROOT / "sitemap.xml")
    sitemap_all = slugs_in(ROOT / "sitemap-all.xml")
    index_html = (ROOT / "index.html").read_text(encoding="utf-8")
    index_slugs = set(re.findall(r'href="/articles/([^/"]+)/"', index_html))

    # 1. articles/ と sitemap.xml
    report(errors, "sitemap.xml", articles - sitemap, sitemap - articles,
           "articles/", "sitemap.xml")

    # 2. articles/ と index.html
    report(errors, "index.html", articles - index_slugs, index_slugs - articles,
           "articles/", "index.html")

    # 3. sitemap.xml と sitemap-all.xml は同一URL集合であること
    if sitemap != sitemap_all:
        diff = sitemap.symmetric_difference(sitemap_all)
        errors.append(
            f"sitemap.xml と sitemap-all.xml が不一致（{len(diff)}件）"
            f" → {', '.join(sorted(diff))}"
        )

    # 4. リダイレクトstubがsitemapに混ざっていないこと（noindex対象のため）
    leaked = stubs & (sitemap | sitemap_all)
    if leaked:
        errors.append(
            f"リダイレクトstubがsitemapに含まれている（{len(leaked)}件）"
            f" → {', '.join(sorted(leaked))}"
        )

    # 5. index.html の「全N記事」表記が実数と一致すること（複数箇所ある）
    for stated in re.findall(r"全(\d+)記事", index_html):
        if int(stated) != len(articles):
            errors.append(
                f"index.html の「全{stated}記事」が実数 {len(articles)} と不一致"
            )

    # 6. テーマグループの「（N記事）」小計の合計が実数と一致すること
    subtotals = [int(n) for n in re.findall(r"（(\d+)記事）", index_html)]
    if subtotals and sum(subtotals) != len(articles):
        errors.append(
            f"index.html のグループ小計の合計 {sum(subtotals)} が"
            f" 実数 {len(articles)} と不一致"
        )

    # 7. 記事間の内部リンクが実在する記事を指していること
    broken = {}
    for page in sorted((ROOT / "articles").glob("*/index.html")):
        if page.parent.name in stubs:
            continue
        targets = slugs_in(page, r'href="/articles/([^/"]+)/"')
        dead = targets - articles - stubs
        if dead:
            broken[page.parent.name] = dead
    for src, dead in broken.items():
        errors.append(f"リンク切れ: {src} → {', '.join(sorted(dead))}")

    print(f"実記事 {len(articles)}本 / リダイレクトstub {len(stubs)}本")
    if errors:
        print(f"\n不整合 {len(errors)}件:\n")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("整合性チェック: 問題なし")
    return 0


if __name__ == "__main__":
    sys.exit(main())

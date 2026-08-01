#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sitemap の <lastmod> を、各記事HTMLの JSON-LD dateModified に合わせる（2026-08-01制定）

なぜ必要か
----------
sitemap の lastmod は build_articles.py が「全URLに実行日を一律で書く」作りだったため、
記事の実際の更新日と乖離していた。2026-08-01時点の実測（142本）：

  lastmod > dateModified （実際より新しいと嘘をついている）  50本
      うち 40本は lastmod=2026-07-04 だが記事は 2026-05/06 のまま
  lastmod < dateModified （本当に更新したのに伝わっていない） 10本
      うち 6本は 2026-07-30 の「寄せ直し」でタイトル・h1・meta・導入を
      書き換えた記事。**効果を測りたい変更そのものが sitemap に出ていない**
  一致                                                      82本

記事ページは JSON-LD の dateModified と同じ日付を本文にも表示している
（例：「更新：2026年5月31日」）。つまり50本は
**sitemap の主張とページの表示が食い違っている**状態で、
lastmod を信用してもらえる状態ではない。

このスクリプトは lastmod を dateModified に**合わせるだけ**で、
今日の日付には決してしない。中身を変えていない記事の lastmod を今日にするのは
虚偽の鮮度シグナルであり、lastmod 全体の信頼をさらに損なうため。

dateModified を持たないURL（トップ・about・privacy・disclaimer）は触らない。

使い方
------
    python3 scripts/sitemap_sync.py --check   # 差分を表示するだけ（終了コード1なら要同期）
    python3 scripts/sitemap_sync.py           # sitemap.xml と sitemap-all.xml を書き換える
"""
import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAPS = ("sitemap.xml", "sitemap-all.xml")

URL_BLOCK_RE = re.compile(r"<url>.*?</url>", re.S)
LOC_RE = re.compile(r"<loc>\s*([^<\s]+)\s*</loc>")
LASTMOD_RE = re.compile(r"(<lastmod>)([^<]*)(</lastmod>)")
DATEMOD_RE = re.compile(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})')


def article_path(url):
    """sitemap の URL からローカルの記事HTMLを引く。記事以外は None。"""
    m = re.search(r"/articles/([^/]+)/?$", url)
    if not m:
        return None
    path = os.path.join(ROOT, "articles", m.group(1), "index.html")
    return path if os.path.exists(path) else None


_CACHE = {}


def date_modified(url):
    """記事HTMLの JSON-LD dateModified（YYYY-MM-DD）。無ければ None。"""
    if url in _CACHE:
        return _CACHE[url]
    path = article_path(url)
    value = None
    if path:
        with open(path, encoding="utf-8", errors="replace") as f:
            m = DATEMOD_RE.search(f.read())
        if m:
            value = m.group(1)
    _CACHE[url] = value
    return value


def diffs(name):
    """(url, 現在のlastmod, あるべきlastmod) の一覧を返す"""
    path = os.path.join(ROOT, name)
    if not os.path.exists(path):
        return []
    # 改行コードを変換させない（sitemap.xml=CRLF / sitemap-all.xml=LF）
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    out = []
    for block in URL_BLOCK_RE.findall(text):
        loc = LOC_RE.search(block)
        cur = LASTMOD_RE.search(block)
        if not loc or not cur:
            continue
        want = date_modified(loc.group(1))
        if want and want != cur.group(2).strip():
            out.append((loc.group(1), cur.group(2).strip(), want))
    return out


def sync(name):
    path = os.path.join(ROOT, name)
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8", newline="") as f:
        text = f.read()

    changed = [0]

    def fix_block(m):
        block = m.group(0)
        loc = LOC_RE.search(block)
        if not loc:
            return block
        want = date_modified(loc.group(1))
        if not want:
            return block

        def fix_lastmod(lm):
            if lm.group(2).strip() == want:
                return lm.group(0)
            changed[0] += 1
            return lm.group(1) + want + lm.group(3)

        return LASTMOD_RE.sub(fix_lastmod, block)

    new = URL_BLOCK_RE.sub(fix_block, text)
    if new != text:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(new)
    return changed[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="書き換えず差分だけ表示する（要同期なら終了コード1）")
    args = ap.parse_args()

    total = 0
    for name in SITEMAPS:
        d = diffs(name)
        total += len(d)
        print("%s: 要同期 %d件" % (name, len(d)))
        newer = [x for x in d if x[1] > x[2]]
        older = [x for x in d if x[1] < x[2]]
        if newer:
            print("  lastmod が実際より新しい（虚偽の鮮度）: %d件" % len(newer))
        if older:
            print("  lastmod が実際より古い（更新が伝わっていない）: %d件" % len(older))
            for u, cur, want in older:
                print("    %-56s %s → %s"
                      % (u.replace("https://www.noe-match.com", ""), cur, want))

    if args.check:
        if total:
            print("\n同期するには: python3 scripts/sitemap_sync.py")
            return 1
        print("\nすべて dateModified と一致している。")
        return 0

    if not total:
        print("\n変更なし。")
        return 0
    for name in SITEMAPS:
        n = sync(name)
        print("%s: %d件を書き換えた" % (name, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())

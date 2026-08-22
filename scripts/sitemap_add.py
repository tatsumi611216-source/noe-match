# -*- coding: utf-8 -*-
"""サイトマップに未登録のページを追加する。

`sitemap_sync.py` は lastmod を dateModified に合わせるだけで、
**新規URLの追加はしない**（虚偽の鮮度シグナルを避ける設計）。
そのため新規ページを出したあとは、こちらで追加する必要がある。

lastmod は各ページの JSON-LD の dateModified をそのまま使う
（sitemap_sync と同じ原則。今日の日付を勝手に入れない）。
"""
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.noe-match.com"
SITEMAPS = ("sitemap.xml", "sitemap-all.xml")


def page_url(path):
    p = path.replace(os.sep, "/")
    return SITE + "/" + (p[:-10] if p.endswith("index.html") else p)


def date_modified(html):
    for s in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            d = json.loads(s)
        except Exception:
            continue
        if d.get("@type") in ("Article", "BlogPosting") and d.get("dateModified"):
            return d["dateModified"]
    return None


def main():
    os.chdir(ROOT)
    pages = {}
    for f in glob.glob("articles/**/*.html", recursive=True) + \
             glob.glob("tools/**/*.html", recursive=True):
        h = io.open(f, encoding="utf-8").read()
        if 'name="robots"' in h and "noindex" in h:
            continue
        dm = date_modified(h)
        if dm:
            pages[page_url(f)] = dm

    for sm in SITEMAPS:
        if not os.path.exists(sm):
            continue
        x = io.open(sm, encoding="utf-8").read()
        have = set(re.findall(r"<loc>(.*?)</loc>", x))
        missing = [(u, d) for u, d in sorted(pages.items()) if u not in have]
        if not missing:
            print("%s: 追加なし" % sm)
            continue
        entries = "".join(
            "<url><loc>%s</loc><lastmod>%s</lastmod></url>\n" % (u, d)
            for u, d in missing)
        x = x.replace("</urlset>", entries + "</urlset>")
        io.open(sm, "w", encoding="utf-8").write(x)
        print("%s: +%d" % (sm, len(missing)))
        for u, d in missing:
            print("   ", u, d)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

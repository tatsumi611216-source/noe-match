# -*- coding: utf-8 -*-
"""記事以外（ツール・ポリシー・静的ページ）の最終更新日をgitの実績に揃える。

なぜ必要か（2026-08-29）:
freshness_sync.py は sitemap.xml から `/articles/<slug>/` だけを拾うので、
ツール24本・ポリシー4本・静的3本が対象外だった。実測で24URLの lastmod が
実際の内容変更日とずれており、`disclaimer.html` は 2026-07-04 と
**ファイルの作成日（2026-08-06）より前の日付**が入っていた。
lastmod が作成日より古いのは明白な誤りで、クロールの優先度を下げる。

freshness_sync.py と同じ STRUCTURAL_COMMITS を使い、構造だけの一括変更では
日付を動かさない。**このスクリプトも決して「今日の日付」を書かない。**

実行: python scripts/freshness_nonarticle.py           # 差分の表示のみ
      python scripts/freshness_nonarticle.py --apply   # 適用
"""
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAPS = ["sitemap.xml", "sitemap-all.xml"]


def structural():
    s = io.open(os.path.join(ROOT, "scripts", "freshness_sync.py"), encoding="utf-8").read()
    blk = re.search(r"STRUCTURAL_COMMITS = \{.*?\n\}", s, re.S).group(0)
    return set(re.findall(r'"([0-9a-f]{7})"', blk))


def content_date(rel, S):
    out = subprocess.run(["git", "log", "--format=%h|%ad", "--date=short", "--", rel],
                         cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    for line in out:
        h, d = line.split("|")
        if h[:7] in S:
            continue
        return d
    return out[-1].split("|")[1] if out else None


def local_path(loc):
    p = loc.replace("https://www.noe-match.com/", "")
    if p.endswith(".html"):
        return p, p
    return p, (p.rstrip("/") + "/index.html" if p.strip("/") else "index.html")


def main(apply_):
    S = structural()
    sm = io.open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    pairs = re.findall(r"<loc>(.*?)</loc>\s*<lastmod>(.*?)</lastmod>", sm, flags=re.S)
    fixes = []
    for loc, lm in pairs:
        p, f = local_path(loc)
        if p.startswith("articles/") or not os.path.exists(os.path.join(ROOT, f)):
            continue
        g = content_date(f, S)
        if g and lm.strip()[:10] != g:
            fixes.append((loc, lm.strip()[:10], g, f))
    print("ずれているURL: %d件" % len(fixes))
    for loc, old, new, f in fixes:
        print("  %-44s %s → %s" % (loc.replace("https://www.noe-match.com/", "")[:44], old, new))
    if not apply_:
        print("\n適用するには --apply を付ける。")
        return
    for name in SITEMAPS:
        p = os.path.join(ROOT, name)
        h = io.open(p, encoding="utf-8").read()
        for loc, old, new, f in fixes:
            # 同一 <url> ブロック内の lastmod だけを置換する
            h = re.sub(r"(<loc>%s</loc>\s*<lastmod>)[0-9-]{10}" % re.escape(loc),
                       r"\g<1>" + new, h)
        io.open(p, "w", encoding="utf-8").write(h)
    ld = 0
    for loc, old, new, f in fixes:
        p = os.path.join(ROOT, f)
        h = io.open(p, encoding="utf-8").read()
        h2 = re.sub(r'("dateModified"\s*:\s*")[0-9-]{10}', r"\g<1>" + new, h)
        if h2 != h:
            io.open(p, "w", encoding="utf-8").write(h2)
            ld += 1
    print("\nsitemap 2本を更新／ページ内 dateModified を %d件 更新" % ld)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main("--apply" in sys.argv)

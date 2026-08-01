#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""記事の「最終更新日」を、git上の実際の変更履歴に合わせて揃える。

なぜ必要か（2026-08-01）：
1記事の更新日が**3箇所**に別々に書かれており、互いにズレていた。

    ① JSON-LD の dateModified
    ② 本文の byline「最終更新：YYYY年M月D日」
    ③ sitemap.xml / sitemap-all.xml の <lastmod>

実測で19本がズレており、**方向が両方に割れていた**。
  - 9本：②が古い（07-30に寄せ直したのに表示が05-31のまま）
  - 10本：①が古い（07-26〜07-30に実際に変更したのに dateModified が05-31のまま）

つまり「①を正」としても「②を正」としても間違う。**唯一の真実はgitの変更履歴**なので、
そこから逆算して3箇所を揃える。

--------------------------------------------------------------------------
「更新」と見なす変更／見なさない変更
--------------------------------------------------------------------------
最終更新日は読者が「情報がいつ時点のものか」を判断するために見る。
**目次の挿入や広告表記の追加のような構造だけの一括変更では日付を動かさない。**
動かしてよいのは、記事が伝える内容が変わったときだけ。

除外するコミットは STRUCTURAL_COMMITS に列挙する。ここに無いコミットは
内容変更とみなす（迷ったら「更新した」側に倒すより、除外に足す方が安全）。

**このスクリプトは決して「今日の日付」を書かない。** 書くのは常にgitの実績日。
中身を変えずに日付だけ新しくするのは読者とGoogleの両方に対する虚偽であり、
それをやるくらいなら古い日付のままの方が損失が小さい。

--------------------------------------------------------------------------
使い方
--------------------------------------------------------------------------
    python3 scripts/freshness_sync.py           # ズレを報告するだけ（既定・終了コード1=ズレあり）
    python3 scripts/freshness_sync.py --stale   # 更新が古い順に一覧（鮮度メンテの対象選び）
    python3 scripts/freshness_sync.py --apply   # 3箇所をgitの実績に揃える（要・事前確認）

既知の限界（2026-08-01時点）：
--stale は「30日超 0本」と出るが、これは**信用してはいけない**。
07-26以降、目次挿入・広告表記・CTA配置・リブランドといった全記事規模の一括変更が
何度も入っており、gitのコミット日が全記事で新しくなっているため。
**「情報としての鮮度」を測るには、どのコミットを内容変更と見なすかを
STRUCTURAL_COMMITS で正しく仕分ける必要がある。** その線引きは運営者の判断事項。

既定を報告のみにしているのは、STRUCTURAL_COMMITS の線引きを誤ったまま --apply すると
**内容が変わっていない記事の日付まで一斉に進んでしまう**ため。初回実測では116本が
ズレていたが、その多くは目次やCTAを足しただけで情報は変わっていなかった。
"""
import argparse
import os
import re
import subprocess
import sys
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 構造だけを一括で変えたコミット。ここに載っているコミットしか触っていない記事は
# 「内容は変わっていない」とみなし、最終更新日を動かさない。
STRUCTURAL_COMMITS = {
    # 目次の挿入・冒頭広告表記の追加・収益導線の修正（2026-08-01）
    "bfc6291",
    # sitemapのlastmod同期のみ（記事本文は未変更・2026-08-01）
    "8f2b8d3",
}

DISPLAY_RE = re.compile(r"最終更新：(\d{4})年(\d{1,2})月(\d{1,2})日")
LD_MODIFIED_RE = re.compile(r'("dateModified"\s*:\s*")(\d{4}-\d{2}-\d{2})')
META_MODIFIED_RE = re.compile(
    r'(<meta property="article:modified_time" content=")(\d{4}-\d{2}-\d{2})')


def sh(*args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True).stdout


def live_slugs():
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        return sorted(set(re.findall(r"/articles/([^/]+)/</loc>", f.read())))


def last_content_change(slug):
    """その記事に内容変更が入った最終日を git から取る。

    構造だけのコミットは飛ばして遡る。全部が構造コミットだった場合は
    最初の（=公開時の）コミット日を返す。
    """
    path = "articles/%s/index.html" % slug
    out = sh("git", "log", "--format=%h %ad", "--date=short", "--", path)
    lines = [l.split(None, 1) for l in out.strip().splitlines() if l.strip()]
    if not lines:
        return None
    for sha, d in lines:
        if sha not in STRUCTURAL_COMMITS:
            return d.strip()
    return lines[-1][1].strip()


def read(slug):
    with open(os.path.join(ROOT, "articles", slug, "index.html"), encoding="utf-8") as f:
        return f.read()


def current_dates(html):
    ld = LD_MODIFIED_RE.search(html)
    disp = DISPLAY_RE.search(html)
    return (ld.group(2) if ld else None,
            "%s-%02d-%02d" % (disp.group(1), int(disp.group(2)), int(disp.group(3)))
            if disp else None)


def sitemap_dates():
    out = {}
    for name in ("sitemap.xml", "sitemap-all.xml"):
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            body = f.read()
        for slug, lm in re.findall(
                r"/articles/([^/]+)/</loc>\s*<lastmod>([\d-]{10})", body):
            out.setdefault(name, {})[slug] = lm
    return out


def apply_to_article(slug, target):
    """JSON-LD dateModified・article:modified_time・本文の表示を target に揃える。"""
    p = os.path.join(ROOT, "articles", slug, "index.html")
    html = read(slug)
    before = html
    html = LD_MODIFIED_RE.sub(lambda m: m.group(1) + target, html)
    html = META_MODIFIED_RE.sub(lambda m: m.group(1) + target, html)
    y, mo, d = target.split("-")
    html = DISPLAY_RE.sub("最終更新：%d年%d月%d日" % (int(y), int(mo), int(d)), html)
    if html != before:
        with open(p, "w", encoding="utf-8") as f:
            f.write(html)
        return True
    return False


def apply_to_sitemaps(targets):
    """sitemapの<lastmod>を揃える。改行コードは元のファイルのまま保つ。"""
    changed = 0
    for name in ("sitemap.xml", "sitemap-all.xml"):
        p = os.path.join(ROOT, name)
        if not os.path.exists(p):
            continue
        with open(p, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8")

        def rep(m):
            slug = m.group(1)
            t = targets.get(slug)
            return m.group(0) if not t else m.group(0).replace(m.group(2), t)

        new = re.sub(r"/articles/([^/]+)/</loc>\s*<lastmod>([\d-]{10})", rep, text)
        if new != text:
            with open(p, "wb") as f:
                f.write(new.encode("utf-8"))
            changed += 1
    return changed


def collect():
    sm = sitemap_dates()
    rows = []
    for slug in live_slugs():
        html = read(slug)
        ld, disp = current_dates(html)
        git_d = last_content_change(slug)
        rows.append({
            "slug": slug,
            "git": git_d,
            "ld": ld,
            "display": disp,
            "sitemap": sm.get("sitemap.xml", {}).get(slug),
            "sitemap_all": sm.get("sitemap-all.xml", {}).get(slug),
        })
    return rows


def mismatched(rows):
    out = []
    for r in rows:
        if not r["git"]:
            continue
        vals = [r["ld"], r["display"], r["sitemap"], r["sitemap_all"]]
        if any(v is not None and v != r["git"] for v in vals):
            out.append(r)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="報告のみ（既定）")
    ap.add_argument("--apply", action="store_true",
                    help="実際に3箇所を揃える。**STRUCTURAL_COMMITS を確認してから使うこと**")
    ap.add_argument("--stale", action="store_true", help="更新が古い順に一覧する")
    args = ap.parse_args()

    rows = collect()

    if args.stale:
        today = date.today()
        rows.sort(key=lambda r: r["git"] or "")
        print("更新が古い順（gitの実績日ベース）\n")
        print("%-30s %-12s %s" % ("slug", "最終更新", "経過"))
        for r in rows:
            if not r["git"]:
                continue
            age = (today - date(*map(int, r["git"].split("-")))).days
            mark = "★" if age > 30 else " "
            print("%s%-29s %-12s %d日" % (mark, r["slug"], r["git"], age))
        stale = [r for r in rows if r["git"] and
                 (today - date(*map(int, r["git"].split("-")))).days > 30]
        print("\n30日超が %d本 / 全%d本" % (len(stale), len(rows)))
        if stale:
            per_week = -(-len(stale) // 4)
            print("これを30日以内に一巡させるには週 %d本の実更新が要る。" % per_week)
            print("**日付だけ動かすのは虚偽なので行わない。**"
                  "実際に確認・加筆した記事だけが新しくなる。")
        return 0

    bad = mismatched(rows)
    if not args.apply:
        print("3箇所の更新日が食い違っている記事: %d本 / 全%d本" % (len(bad), len(rows)))
        for r in bad:
            print("  %-28s git:%s LD:%s 表示:%s sitemap:%s"
                  % (r["slug"], r["git"], r["ld"], r["display"], r["sitemap"]))
        if bad:
            print("\n書き換えるには --apply を付ける。ただし先に STRUCTURAL_COMMITS を見直すこと。")
            print("CTAや目次の追加のような、読者にとって情報が変わらない変更で")
            print("最終更新日を動かすのは水増しになる。")
        return 1 if bad else 0

    if not bad:
        print("すべて git の実績日と一致している。")
        return 0

    targets = {}
    n = 0
    for r in bad:
        if apply_to_article(r["slug"], r["git"]):
            n += 1
        targets[r["slug"]] = r["git"]
    sm_changed = apply_to_sitemaps(targets)
    print("記事 %d本を更新 / sitemap %dファイルを更新" % (n, sm_changed))
    for r in bad:
        print("  %-28s → %s" % (r["slug"], r["git"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

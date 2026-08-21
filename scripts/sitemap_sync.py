# -*- coding: utf-8 -*-
"""sitemap.xml と sitemap-all.xml のURL集合を一致させ、更新したページの lastmod を進める。

なぜ必要か（2026-08-21の実測）:

AGENT.md には「sitemap.xml と sitemap-all.xml は既にURL集合が同一」と書いてあるが、
実際には **206 対 197 で9本ずれていた**。片方にしか載っていないURLは、Googleが
受け取るsitemapのどちらを読むかで扱いが変わる。

  片方にしか無かった9本:
    /articles/omiai-danjohi-data/   ← URL is unknown to Google
    /tools/kekkon-shikin-keisanki/  ← URL is unknown to Google
    /articles/with-nenreiso-data/ /tools/garugaru-check/ /tools/soudanjo-simulator/
    /policy/editorial.html /policy/rating.html /policy/research.html /policy/update.html

**これが未認識の原因だと断定はできない**（garugaru-check と soudanjo-simulator は
片方だけでもインデックスされている）。だが両方に載せない理由も無く、直すのは無害で
発見の面積は増える。台帳の記述と実態が食い違っていること自体が是正対象である。

lastmod について:

AGENT.md は「空更新（年号だけ書き換える）」を禁止している。本スクリプトの --bump は
**実際に中身を変えたページにだけ**使う。引数で明示的に渡す設計にしているのは、
全件を機械的に進めて鮮度シグナルを偽装することを防ぐため。

使い方:
    python3 scripts/sitemap_sync.py --check                 # ずれの確認だけ
    python3 scripts/sitemap_sync.py                         # URL集合を一致させる
    python3 scripts/sitemap_sync.py --bump 2026-08-21 /tools/   # 接頭辞一致でlastmod更新
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.noe-match.com'
FILES = ['sitemap.xml', 'sitemap-all.xml']


def read(name):
    return io.open(os.path.join(ROOT, name), encoding='utf-8').read()


def write(name, s):
    io.open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(s)


def entries(s):
    """<url>…</url> ブロックを loc をキーに拾う。"""
    out = {}
    for m in re.finditer(r'<url>.*?</url>', s, re.S):
        loc = re.search(r'<loc>([^<]+)</loc>', m.group(0))
        if loc:
            out[loc.group(1)] = m.group(0)
    return out


def main():
    args = sys.argv[1:]
    check = '--check' in args
    bump_date, bump_prefixes = None, []
    if '--bump' in args:
        i = args.index('--bump')
        bump_date = args[i + 1]
        bump_prefixes = args[i + 2:]
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', bump_date or ''):
            print('--bump の日付は YYYY-MM-DD で指定する')
            return 2
        if not bump_prefixes:
            print('--bump には対象の接頭辞を1つ以上渡す（全件更新は空更新になるため禁止）')
            return 2

    docs = {f: read(f) for f in FILES}
    ent = {f: entries(s) for f, s in docs.items()}
    union = set().union(*[set(e) for e in ent.values()])

    print('URL数: ' + ' / '.join('%s=%d' % (f, len(ent[f])) for f in FILES))
    missing = {f: sorted(union - set(ent[f])) for f in FILES}
    total_missing = sum(len(v) for v in missing.values())
    for f, urls in missing.items():
        for u in urls:
            print('  %s に無い: %s' % (f, u.replace(SITE, '')))
    print('不足合計: %d件' % total_missing)

    if check:
        return 1 if total_missing else 0

    changed = []
    for f in FILES:
        s = docs[f]
        add = missing[f]
        if add:
            src = {}
            for g in FILES:
                src.update(ent[g])
            block = '\n'.join(src[u] for u in add)
            s = s.replace('</urlset>', block + '\n</urlset>')
            changed.append('%s に %d件を追加' % (f, len(add)))
        if bump_date:
            n = 0
            def fix(m):
                nonlocal n
                blk = m.group(0)
                loc = re.search(r'<loc>([^<]+)</loc>', blk).group(1).replace(SITE, '')
                if not any(loc.startswith(p) for p in bump_prefixes):
                    return blk
                n += 1
                if '<lastmod>' in blk:
                    return re.sub(r'<lastmod>[^<]*</lastmod>',
                                  '<lastmod>%s</lastmod>' % bump_date, blk)
                return blk.replace('</loc>', '</loc><lastmod>%s</lastmod>' % bump_date)
            s = re.sub(r'<url>.*?</url>', fix, s, flags=re.S)
            if n:
                changed.append('%s の lastmod を %d件更新（%s）' % (f, n, bump_date))
        if s != docs[f]:
            write(f, s)

    for c in changed:
        print('  ' + c)
    print('完了' if changed else '変更なし')
    return 0


if __name__ == '__main__':
    sys.exit(main())

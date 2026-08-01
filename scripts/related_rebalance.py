# -*- coding: utf-8 -*-
"""関連記事ボックスの収益導線比率を点検・是正する。

AGENT.md「関連記事ボックスの収益枠下限」ルールの実装。
各記事の関連記事ボックスについて、CTA保有記事へのリンクが2本未満なら、
その記事の本文中で既にリンクしている収益記事を繰り上げて枠に入れる。

本文にない記事は絶対に足さない（関連性のないリンクを機械的に生やさないため）。
本文にも候補がない場合は是正せず「要手当」として報告する。

使い方:
    python scripts/related_rebalance.py            # 点検のみ（変更しない）
    python scripts/related_rebalance.py --apply    # 是正を書き込む
"""
import re, sys, json, glob, os
from collections import Counter

MIN_REVENUE = 2   # 関連記事ボックス内に必要なCTA保有記事の最低本数
MAX_ITEMS = 6     # ボックスの上限（build_articles.py の既存仕様に合わせる）

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CTA_RE = re.compile(r't\.afi-b\.com|px\.a8\.net')
REL_RE = re.compile(r'(<div class="related">.*?</div>)', re.S)
LI_RE = re.compile(r'<li><a href="/articles/([a-z0-9\-]+)/">([^<]*)</a></li>')


def load():
    """リダイレクトstubを除いた実記事を読み込む。"""
    stub = set()
    rpath = os.path.join(ROOT, 'redirects.json')
    if os.path.exists(rpath):
        red = json.load(open(rpath, encoding='utf-8'))
        stub = set(red.keys()) if isinstance(red, dict) else set()
    arts = {}
    for p in glob.glob(os.path.join(ROOT, 'articles', '*', 'index.html')):
        slug = os.path.basename(os.path.dirname(p))
        if slug in stub or os.path.getsize(p) < 1000:
            continue
        arts[slug] = p
    return arts


def title_of(html, slug):
    """関連記事ボックス用の短いラベルを作る。

    <title> はSEO用に長いので、区切り（｜【（）や副題の前で切り、
    既存の手書きラベル（例「with完全ガイド」）と粒度を揃える。
    """
    m = re.search(r'<title>(.*?)</title>', html)
    t = (m.group(1) if m else slug).strip()
    t = re.split(r'[｜|【]', t)[0].strip()   # 括弧は語の一部なので切らない
    q = t.find('？')                        # 問いかけ型タイトルは疑問符で切る
    if 0 < q <= 28:
        return t[:q + 1]
    return (t[:22] + '…') if len(t) > 23 else t


def main():
    apply_mode = '--apply' in sys.argv
    arts = load()
    html = {s: open(p, encoding='utf-8').read() for s, p in arts.items()}
    cta = {s: len(CTA_RE.findall(h)) for s, h in html.items()}

    fixed, already, nocands, nobox = [], 0, [], 0
    for slug, h in sorted(html.items()):
        m = REL_RE.search(h)
        if not m:
            nobox += 1
            continue
        box = m.group(1)
        items = LI_RE.findall(box)
        if not items:
            nobox += 1
            continue
        rev = [s for s, _ in items if cta.get(s, 0) > 0]
        if len(rev) >= MIN_REVENUE:
            already += 1
            continue

        # 本文（ボックス外）で既にリンクしている収益記事だけを候補にする
        body = REL_RE.sub('', h)
        inbox = {s for s, _ in items}
        cands = [s for s in dict.fromkeys(re.findall(r'/articles/([a-z0-9\-]+)/', body))
                 if s in cta and cta[s] > 0 and s not in inbox and s != slug]
        need = MIN_REVENUE - len(rev)
        add = cands[:need]
        if len(add) < need:
            nocands.append((slug, len(rev), len(cands)))
            if not add:
                continue

        new_items = items + [(s, title_of(html[s], s)) for s in add]
        # 収益記事を前に寄せる（枠の上限で切られても導線が残るように）
        new_items.sort(key=lambda it: 0 if cta.get(it[0], 0) > 0 else 1)
        new_items = new_items[:MAX_ITEMS]
        # 切り詰めで収益枠が下限を割るなら、切らずに残す
        if sum(1 for s, _ in new_items if cta.get(s, 0) > 0) < min(MIN_REVENUE, len(rev) + len(add)):
            new_items = (items + [(s, title_of(html[s], s)) for s in add])

        lis = ''.join(f'<li><a href="/articles/{s}/">{t}</a></li>' for s, t in new_items)
        newbox = f'<div class="related"><h2>📚 関連記事</h2><ul>{lis}</ul></div>'
        if apply_mode:
            open(arts[slug], 'w', encoding='utf-8').write(h.replace(box, newbox, 1))
        fixed.append((slug, len(rev), len(rev) + len(add)))

    print(f'実記事 {len(arts)} 本 / 関連記事ボックスなし {nobox} 本')
    print(f'既に基準を満たす（収益記事 {MIN_REVENUE} 本以上）: {already} 本')
    print(f'{"是正した" if apply_mode else "是正できる"}: {len(fixed)} 本')
    for s, before, after in fixed:
        print(f'  {s:36} 収益枠 {before} → {after}')
    if nocands:
        print(f'\n要手当（本文に収益記事へのリンクがなく、機械的に是正できない）: {len(nocands)} 本')
        for s, rev, c in nocands:
            print(f'  {s:36} 収益枠 {rev} / 本文候補 {c}')
    if not apply_mode and fixed:
        print('\n※ 点検のみ。書き込むには --apply を付けて再実行してください。')
    return 0


if __name__ == '__main__':
    sys.exit(main())

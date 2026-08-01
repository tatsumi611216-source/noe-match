# -*- coding: utf-8 -*-
"""インデックス済みページからクロール経路のない記事に、相互リンクで経路を通す。

なぜ必要か（2026-08-01の実測）：
URL Inspection API で記事142本を検査したところ、
  Submitted and indexed             47本（33%）
  Discovered - currently not indexed 81本（57%）
  URL is unknown to Google           14本（10%）
表示ゼロ117本のうち (a)未インデックスが95本（81%）で、AGENT.md 5-7 の反証条件
「(b)が3割以下なら流通側の点検を最優先」に該当した。

sitemap・robots・canonical・配信（HTTP 200）はいずれも正常。残る差は
**Googleが実際に辿れる経路があるか**で、52本がインデックス済みページから
1本も貼られていなかった。未インデックスのページからいくらリンクされていても、
クローラはそこを通らないので経路として機能しない。

このスクリプトは、記事Aが既にインデックス済み記事Bへリンクしている場合に限り、
BからAへの相互リンクを関連記事ボックスに追加する。**両者は既に関連しているので
新たな関連性の判断を持ち込まない**（関連性のないリンクを生やさないための制約）。

CTAを増やす変更ではないため、AGENT.md 4-0 の計測ゲートが閉じていても実行してよい。

使い方:
    python scripts/crawl_path_fix.py            # 点検のみ
    python scripts/crawl_path_fix.py --apply    # 相互リンクを書き込む
"""
import re, os, sys, json, glob
from collections import defaultdict

# 関連記事ボックスの上限。6は build_articles.py（旧ビルダー）の実装値にすぎず、
# ARTICLE_TEMPLATE_GUIDE.md は関連記事リンク9個を想定しているため、
# クロール経路を通す目的に限り8まで許容する。
MAX_ITEMS = 8
MIN_REVENUE = 2    # 収益枠の下限（AGENT.md「関連記事ボックスの収益枠下限」）

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CTA_RE = re.compile(r't\.afi-b\.com|px\.a8\.net')
REL_RE = re.compile(r'(<div class="related">.*?</div>)', re.S)
LI_RE = re.compile(r'<li><a href="/articles/([a-z0-9\-]+)/">([^<]*)</a></li>')


def label(html, slug):
    """関連記事ボックス用の短いラベル（related_rebalance.py と同じ規則）。"""
    m = re.search(r'<title>(.*?)</title>', html)
    t = (m.group(1) if m else slug).strip()
    t = re.split(r'[｜|【]', t)[0].strip()
    q = t.find('？')
    if 0 < q <= 28:
        return t[:q + 1]
    return (t[:22] + '…') if len(t) > 23 else t


def main():
    apply_mode = '--apply' in sys.argv
    status = json.load(open(os.path.join(ROOT, 'agent', 'index_status.json'), encoding='utf-8'))['results']
    state = {u.rstrip('/').split('/')[-1]: v.get('coverageState')
             for u, v in status.items() if '/articles/' in u}
    indexed = {s for s, v in state.items() if v == 'Submitted and indexed'}

    paths = {os.path.basename(os.path.dirname(p)): p
             for p in glob.glob(os.path.join(ROOT, 'articles', '*', 'index.html'))
             if os.path.getsize(p) >= 1000}
    html = {s: open(p, encoding='utf-8').read() for s, p in paths.items()}
    cta = {s: len(CTA_RE.findall(h)) for s, h in html.items()}

    out = {s: {t for t in re.findall(r'/articles/([a-z0-9\-]+)/', h) if t != s and t in html}
           for s, h in html.items()}
    inbound = defaultdict(set)
    for s, ts in out.items():
        for t in ts:
            inbound[t].add(s)

    # インデックス済みページからの被リンクが1本もない記事
    orphans = [s for s in sorted(html) if s in state and not (inbound[s] & indexed)]

    def box(slug):
        m = REL_RE.search(html[slug])
        return (m.group(1), LI_RE.findall(m.group(1))) if m else (None, None)

    added, skipped = [], []
    load = defaultdict(int)   # 1ページに集中させないための追加回数
    for a in orphans:
        # A が既にリンクしている先のうち、インデックス済みのものだけを候補にする
        cands = sorted(out[a] & indexed, key=lambda b: (load[b], len(box(b)[1] or []), b))
        placed = False
        for b in cands:
            raw, items = box(b)
            if raw is None or a in {s for s, _ in items}:
                continue
            new = items + [(a, label(html[a], a))]
            if len(new) > MAX_ITEMS:
                continue                       # 枠を溢れさせない
            if sum(1 for s, _ in new if cta.get(s, 0) > 0) < MIN_REVENUE:
                continue                       # 収益枠の下限を割らない
            lis = ''.join(f'<li><a href="/articles/{s}/">{t}</a></li>' for s, t in new)
            html[b] = html[b].replace(raw, f'<div class="related"><h2>📚 関連記事</h2><ul>{lis}</ul></div>', 1)
            load[b] += 1
            added.append((a, b))
            placed = True
            break
        if not placed:
            skipped.append(a)

    if apply_mode:
        for b in {b for _, b in added}:
            open(paths[b], 'w', encoding='utf-8').write(html[b])

    print(f'記事 {len(html)} 本 / インデックス済み {len(indexed)} 本')
    print(f'インデックス済みページからの経路がない記事: {len(orphans)} 本')
    print(f'{"経路を通した" if apply_mode else "経路を通せる"}: {len(added)} 本')
    for a, b in added:
        print(f'  {a:34} ← {b}')
    if skipped:
        print(f'\n通せない（インデックス済みページと接点がない・枠が満杯）: {len(skipped)} 本')
        for a in skipped:
            print(f'  {a}')
    if not apply_mode and added:
        print('\n※ 点検のみ。書き込むには --apply を付けて再実行してください。')
    return 0


if __name__ == '__main__':
    sys.exit(main())

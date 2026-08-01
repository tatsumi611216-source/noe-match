#!/usr/bin/env python3
"""表示ゼロ記事の検出と寄せ直しリストの再生成（2026-07-30制定）

`agent/silent_articles.md` を毎回作り直す。手で書いたリストは更新されないので、
GSCデータが更新されるたびに機械が並べ直す。

背景（2026-07-30の原因調査）：
表示ゼロの原因は技術でも記事の年齢でもなく、狙ったクエリのSERP競合の厚さだった。
無修飾ヘッドタームを狙った15本は公開2ヶ月で1本も表示が立っていない（0%）のに対し、
地域名・職業名で絞ったものは8/9（89%）が表示に到達している。
詳細は agent/rule_changes.md の「2026-07-30(3)」。

使い方:
    python3 scripts/silent_scan.py                # リストを再生成
    python3 scripts/silent_scan.py --check-queue  # キューの未処理分をクエリ型で検査
    python3 scripts/silent_scan.py --dry-run      # 書き込まず表示だけ
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GSC = os.path.join(ROOT, 'agent', 'gsc_data.json')
QUEUE = os.path.join(ROOT, 'agent', 'keyword_queue.json')
REWRITES = os.path.join(ROOT, 'agent', 'rewrites.json')
OUT = os.path.join(ROOT, 'agent', 'silent_articles.md')

# 寄せ直してから表示に到達したかを判定するまでの猶予
REWRITE_GRACE_DAYS = 21

# --- クエリ型の判定 -------------------------------------------------------
# 実測（2026-07-30）：無修飾ヘッドターム 0/15（0%）／ニッチ内定番トピック 約20%
#                     指名 20%／サイト外の固有修飾 8/9（89%）
#
# パターンマッチの粗い分類なので、判定は「警告」であって「禁止」ではない。
# 迷ったら人間・エージェントの判断を優先する。リストは実測に応じて手で育てる。

# 無修飾ヘッドターム：ジャンル名＋汎用語だけで成立してしまうもの
HEAD_TERMS = (
    'ranking', 'compare-price', 'price-comparison', 'compare-popular', 'compare-konkatsu',
    'compare-20s', 'members-data', 'free-vs-paid', 'safety-guide', 'konkatsu-roadmap',
    'faq-troubleshooting', 'success-stories', 'renkatsu-vs-konkatsu', 'agency-vs-app',
    'app-plus-agency', 'privacy-protection', 'age-data',
)
# サービス名（指名検索）
BRANDS = (
    'pairs', 'omiai', 'tapple', 'youbride', 'marrish', 'bachelor', 'pappy', 'naco',
    'mitas', 'myseed', 'mitocore',
)
# サイト外の固有修飾：地域名・職業名・具体的な属性や商材
PROPER = (
    'tokyo', 'osaka', 'kyoto', 'sapporo', 'fukuoka', 'nagoya', 'kobe', 'inaka',
    'nurse', 'civil-servant', 'student', 'seishain', 'batsuichi', 'hitomishiri',
    'pocchari', 'tantei', 'uwaki', 'rikon', 'yachin', 'kaden', 'sim', 'hikari',
    'osechi', 'shikijo', 'konyaku', 'gosyugi', 'uchiiwai', 'houkoku', 'maedori',
    'trunkroom', 'credit', 'kouza', 'ryokou', 'nengajou', 'oisix', 'tenshoku',
    'ninkatsu', 'make', 'party', 'photojoy',
)

TIER_HEAD = '無修飾ヘッドターム'
TIER_CORE = 'ニッチ内の定番トピック'
TIER_BRAND = '指名（サービス名）'
TIER_PROPER = 'サイト外の固有修飾'

TIER_ORDER = [TIER_HEAD, TIER_CORE, TIER_BRAND, TIER_PROPER]


def tier_of(slug):
    if any(h in slug for h in HEAD_TERMS):
        return TIER_HEAD
    if any(b in slug for b in BRANDS):
        return TIER_BRAND
    if any(p in slug for p in PROPER):
        return TIER_PROPER
    return TIER_CORE


# --- データ読み込み -------------------------------------------------------

def live_slugs():
    with open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8') as f:
        return sorted(set(re.findall(r'/articles/([^/]+)/</loc>', f.read())))


def article_meta(slug):
    path = os.path.join(ROOT, 'articles', slug, 'index.html')
    with open(path, encoding='utf-8', errors='replace') as f:
        html = f.read()
    d = re.search(r'"datePublished"\s*:\s*"([\d-]{10})', html)
    t = re.search(r'<title>(.*?)</title>', html, re.S)
    return (d.group(1) if d else None,
            re.sub(r'\s+', ' ', t.group(1)).strip() if t else '')


def load_rewrites():
    """寄せ直しの台帳。{slug: {"date": "YYYY-MM-DD", "from": "...", "to": "..."}}"""
    if not os.path.exists(REWRITES):
        return {}
    with open(REWRITES, encoding='utf-8') as f:
        return json.load(f)


def days_between(a, b):
    from datetime import date
    return (date(*map(int, b.split('-'))) - date(*map(int, a.split('-')))).days


# --- 本体 -----------------------------------------------------------------

def scan():
    with open(GSC, encoding='utf-8') as f:
        gsc = json.load(f)
    window_end = gsc['period']['end']
    seen = {}
    for p in gsc.get('by_page', []):
        m = re.search(r'/articles/([^/]+)/', p['page'])
        if m:
            seen[m.group(1)] = p

    slugs = live_slugs()
    meta = {s: article_meta(s) for s in slugs}
    rewrites = load_rewrites()

    # 計測対象＝計測期間の終了までに公開された記事だけ。
    # 期間後に公開された記事は表示が立ちようがないので沈黙に数えない。
    eligible = [s for s in slugs if meta[s][0] and meta[s][0] <= window_end]
    silent = [s for s in eligible if s not in seen]

    tiers = defaultdict(lambda: {'total': 0, 'reached': 0, 'silent': []})
    for s in eligible:
        t = tiers[tier_of(s)]
        t['total'] += 1
        if s in seen:
            t['reached'] += 1
        else:
            t['silent'].append(s)

    # 寄せ直しの効果測定：猶予期間を過ぎたものだけ評価する
    effect = {'evaluated': 0, 'reached': 0, 'pending': 0, 'rows': []}
    for slug, rec in sorted(rewrites.items()):
        age = days_between(rec['date'], window_end)
        if age < REWRITE_GRACE_DAYS:
            effect['pending'] += 1
            status = f'観測中（寄せ直しから{age}日）'
        else:
            effect['evaluated'] += 1
            if slug in seen:
                effect['reached'] += 1
                status = f'表示到達（{seen[slug]["impressions"]}表示）'
            else:
                status = '寄せ直し後も表示ゼロ'
        effect['rows'].append((slug, rec['date'], status, rec.get('to', '')))

    return {
        'window': gsc['period'],
        'eligible': eligible,
        'silent': silent,
        'seen': seen,
        'meta': meta,
        'tiers': tiers,
        'rewrites': rewrites,
        'effect': effect,
    }


def render(r):
    w = r['window']
    tiers, meta, rewrites = r['tiers'], r['meta'], r['rewrites']
    n_elig, n_silent = len(r['eligible']), len(r['silent'])

    lines = [
        '# 表示ゼロ記事の寄せ直しリスト（自動生成）',
        '',
        '**このファイルは `scripts/silent_scan.py` が生成する。手で編集しない。**',
        'GSCデータが更新されるたびに作り直されるので、寄せ直した記事は自動で消える。',
        '',
        f'計測期間：{w["start"]} 〜 {w["end"]} ／ '
        f'計測対象 {n_elig}本中 表示ゼロ {n_silent}本',
        '',
        '## なぜ表示がゼロなのか（2026-07-30の原因調査の結論）',
        '',
        '技術要因（canonical・noindex・内部リンク・記事間の重複）はすべて実測で否定された。',
        '原因は **狙ったクエリのSERP競合の厚さ** である。',
        '**表示ゼロは「インデックス未了」ではなく「圏外（100位以内に入っていない）」を意味する。**',
        '調査の詳細は `agent/rule_changes.md` の「2026-07-30(3)」。',
        '',
        '## クエリ型別の表示到達率（毎回再計測）',
        '',
        '| クエリの型 | 本数 | 表示あり | 到達率 |',
        '|-----------|------|---------|-------|',
    ]
    for t in TIER_ORDER:
        d = tiers.get(t)
        if not d or not d['total']:
            continue
        rate = d['reached'] / d['total'] * 100
        lines.append(f'| {t} | {d["total"]} | {d["reached"]} | {rate:.1f}% |')

    lines += [
        '',
        '## 寄せ直しの手順',
        '',
        '**削除も全面リライトもしない。** タイトル・h1・導入の切り口を、',
        'サイト外の固有修飾（地域名・職業名・具体的な属性）側へ寄せる。',
        '本文の構成と情報はそのまま活かす。1回の実行で最大2本。',
        '寄せ直したら `agent/rewrites.json` に記録すること（効果測定に使う）。',
        '',
    ]

    for t in TIER_ORDER:
        d = tiers.get(t)
        if not d or not d['silent']:
            continue
        prio = '最優先' if t == TIER_HEAD else '次点' if t == TIER_CORE else '経過観察'
        lines += [
            f'### {t}（{prio}） — 表示ゼロ {len(d["silent"])}本',
            '',
            '| slug | 公開日 | 現在のタイトル |',
            '|------|-------|--------------|',
        ]
        for s in sorted(d['silent'], key=lambda x: meta[x][0] or ''):
            lines.append(f'| {s} | {meta[s][0]} | {meta[s][1][:60]} |')
        lines.append('')

    e = r['effect']
    lines += ['## 寄せ直しの効果測定', '']
    if not rewrites:
        lines += ['まだ寄せ直しの記録がない（`agent/rewrites.json` が空）。', '']
    else:
        lines += [
            f'評価対象 {e["evaluated"]}本（寄せ直しから{REWRITE_GRACE_DAYS}日以上） / '
            f'うち表示到達 {e["reached"]}本 / 観測中 {e["pending"]}本',
            '',
            '| slug | 寄せ直し日 | 状態 | 寄せ直し後のタイトル |',
            '|------|----------|------|------------------|',
        ]
        for slug, date, status, to in e['rows']:
            lines.append(f'| {slug} | {date} | {status} | {to[:40]} |')
        lines.append('')
        if e['evaluated'] >= 3 and e['reached'] == 0:
            lines += [
                '> **⚠ 寄せ直しという打ち手そのものが効いていない可能性がある。**',
                f'> 猶予期間を過ぎた{e["evaluated"]}本すべてが表示ゼロのままなら、',
                '> タイトルの寄せ直しでは足りず、記事の主題そのものを変える必要がある。',
                '> Phase 5でルール改定の対象にすること。',
                '',
            ]
    return '\n'.join(lines)


def check_queue():
    """キューの未処理分に無修飾ヘッドタームが混ざっていないか検査する"""
    with open(QUEUE, encoding='utf-8') as f:
        queue = json.load(f)['queue']
    pending = [i for i in queue if i.get('status') in ('pending', 'proposed')]
    flagged = [i for i in pending if tier_of(i['slug']) == TIER_HEAD]
    print(f'キューの未処理 {len(pending)}件を検査')
    for i in pending:
        t = tier_of(i['slug'])
        mark = '⚠' if t == TIER_HEAD else ' '
        print(f'  {mark} [{t:12s}] {i["slug"]:28s} {i.get("title_hint","")[:40]}')
    if flagged:
        print(f'\n⚠ 無修飾ヘッドタームの疑いが{len(flagged)}件。'
              'この層の表示到達率は実測0%。切り口を固有修飾側へ寄せるか、キューから外すこと')
        return 1
    print('\n無修飾ヘッドタームの疑いなし')
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-queue', action='store_true',
                        help='キューの未処理分をクエリ型で検査する')
    parser.add_argument('--dry-run', action='store_true', help='書き込まず表示のみ')
    args = parser.parse_args()

    if args.check_queue:
        return check_queue()

    if not os.path.exists(GSC):
        sys.exit('agent/gsc_data.json が無い。先にGSCデータを取得すること。')

    r = scan()
    doc = render(r)
    if args.dry_run:
        print(doc)
        return 0

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(doc)

    print(f'agent/silent_articles.md を再生成した'
          f'（計測対象{len(r["eligible"])}本 / 表示ゼロ{len(r["silent"])}本）')
    for t in TIER_ORDER:
        d = r['tiers'].get(t)
        if d and d['total']:
            print(f'  {t:14s} {d["reached"]:3d}/{d["total"]:3d} '
                  f'（到達率 {d["reached"]/d["total"]*100:.1f}%）')
    e = r['effect']
    if r['rewrites']:
        print(f'  寄せ直し: 評価{e["evaluated"]}本 / 到達{e["reached"]}本 / 観測中{e["pending"]}本')
    return 0


if __name__ == '__main__':
    sys.exit(main())

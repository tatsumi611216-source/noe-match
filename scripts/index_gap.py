# -*- coding: utf-8 -*-
"""sitemap掲載URLのうち、Googleにインデックスされていないものを洗い出す。

なぜ必要か:

実測則「申請すれば7日で90〜100%インデックス／放置は8日で1.7%」（agent/rule_changes.md
2026-08-09）がある以上、未インデックスのページは **順位が悪いのではなく、まだ試合を
していない**。流入ゼロの原因として真っ先に潰すべきものだが、記事監査は articles/ しか
見ず、ツール監査は tools/ しか見ないため、**サイト全体を1枚で見る台帳が無かった。**

2026-08-21の初回実行では、sitemap 206URLのうち 71本（34%）が未インデックスだった。

3つの状態を区別する:

  URL is unknown to Google … sitemapに載っているのにGoogleが存在を知らない。最も重い
  Discovered - not indexed … 発見済みでクロール待ち。申請が効く典型
  Submitted and indexed    … 正常

申請してはいけないものがある:

  note対照実験の5本（agent/index_request_queue.md）は、noteがクロール需要を動かすかを
  測っている対照群である。**申請すると実験が壊れる。**本スクリプトは自動で除外し、
  除外したことを明記する。

使い方:
    python3 scripts/index_gap.py      # agent/index_gap.md を再生成
"""
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.noe-match.com'
OUT = os.path.join(ROOT, 'agent', 'index_gap.md')

INDEXED = 'Submitted and indexed'
UNKNOWN = 'URL is unknown to Google'

# note対照実験の5本。申請すると実験が壊れるので絶対に申請リストへ入れない。
NOTE_CONTROL = {
    'kaden-rental-vs-kounyu', 'nurse-konkatsu-soudanjo', 'soudanjo-hikaku',
    'tantei-erabikata', 'yachin-credit-shiharai',
}

# 申請の優先順位。decision_gate.md の投資方針（固有修飾クラスタとデータ・統計が
# 10位以内に最も近い）に合わせる。上ほど先に申請する。
def priority(path):
    slug = path.strip('/').split('/')[-1]
    if path.startswith('/tools/'):
        return (1, 'ツール（AI要約に食われない防御資産）')
    if re.search(r'(guide)$', slug) and re.search(
            r'(shizuoka|niigata|tokyo|kyoto|osaka|nagoya|sapporo|fukuoka|okinawa|saitama|chiba|kobe|yokohama|inaka)', slug):
        return (2, '地域ガイド（平均15.7位＝サイト最良）')
    if slug.endswith('-data'):
        return (3, 'データ・統計（クリック/本 1.00＝サイト最良）')
    if re.match(r'^(garugaru|sango|maternity|shinseiji)', slug):
        return (4, '産後クラスタ（10位台の実績あり）')
    if not path.startswith('/articles/'):
        return (6, '規約・方針ページ（収益に直結しないが運営者情報のシグナル）')
    return (5, 'その他記事')


def main():
    sitemap = set()
    for f in ('sitemap.xml', 'sitemap-all.xml'):
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            sitemap |= set(re.findall(r'<loc>([^<]+)</loc>', io.open(p, encoding='utf-8').read()))

    idx = json.load(io.open(os.path.join(ROOT, 'agent', 'index_status.json'), encoding='utf-8'))
    res = idx['results']
    gsc = json.load(io.open(os.path.join(ROOT, 'agent', 'gsc_data.json'), encoding='utf-8'))
    imp = {r['page']: r['impressions'] for r in gsc['by_page']}

    rows = []
    unchecked = []
    for url in sorted(sitemap):
        st = res.get(url)
        if st is None:
            unchecked.append(url)
            continue
        state = st.get('coverageState', '')
        if state == INDEXED:
            continue
        path = url.replace(SITE, '')
        slug = path.strip('/').split('/')[-1]
        rank, why = priority(path)
        rows.append({
            'url': url, 'path': path, 'state': state,
            'checked': (st.get('checked_at') or '')[:10],
            'imp': imp.get(url, 0),
            'excluded': slug in NOTE_CONTROL,
            'rank': rank, 'why': why,
        })

    unknown = [r for r in rows if r['state'] == UNKNOWN]
    excluded = [r for r in rows if r['excluded']]
    stale = [r for r in rows if r['imp'] > 0 and not r['excluded']]
    actionable = sorted([r for r in rows if not r['excluded']],
                        key=lambda r: (r['state'] != UNKNOWN, r['rank'], r['path']))

    o = []
    o.append('# インデックス欠落リスト（sitemap掲載URLのうち未インデックスのもの）')
    o.append('')
    o.append('**自動生成: `scripts/index_gap.py`。手で編集しない。**')
    o.append('')
    o.append('index_status 取得: %s / GSC期間: %s〜%s'
             % (idx.get('fetched_at', '?')[:10], gsc['period']['start'], gsc['period']['end']))
    o.append('')
    o.append('sitemap %d URL のうち **未インデックス %d本（%.0f%%）**。'
             % (len(sitemap), len(rows), len(rows) / max(len(sitemap), 1) * 100))
    o.append('')
    o.append('実測則「申請すれば7日で90〜100%%／放置は8日で1.7%%」より、'
             'この%d本は**順位が悪いのではなく、まだ試合をしていない**。' % len(rows))
    o.append('')
    if unchecked:
        o.append('※ sitemapにあるが index_status に無いURLが %d本ある（未検査）。' % len(unchecked))
        o.append('')

    o.append('## ⛔ 申請してはいけない（note対照実験）')
    o.append('')
    if excluded:
        o.append('noteがクロール需要を動かすかの対照群。**申請すると実験が壊れる。**')
        o.append('')
        for r in excluded:
            o.append('- `%s` — %s（確認 %s）' % (r['path'], r['state'], r['checked']))
        o.append('')
        o.append('（対照群5本のうち、他4本は既にインデックス済み。'
                 '未インデックスで残っているのはこれだけなので、実験の観測点として保持する）')
    else:
        o.append('（該当なし）')
    o.append('')

    o.append('## A. Google がURLの存在を知らない（%d本・最優先）' % len(unknown))
    o.append('')
    o.append('sitemapに載っていて内部リンクもあるのに未認識。申請で解消しない場合は、'
             'リンク先URLの綴り・実URLの200応答・sitemap再送信を順に確認する。')
    o.append('')
    o.append('| URL | 確認日 | 優先理由 |')
    o.append('|---|---|---|')
    for r in sorted(unknown, key=lambda r: (r['rank'], r['path'])):
        o.append('| `%s` | %s | %s |' % (r['path'], r['checked'], r['why']))
    o.append('')

    o.append('## B. 申請キュー（1日10本・上から順に消化）')
    o.append('')
    o.append('手順は `agent/index_request_queue.md` と同じ。'
             'Search Console にURLを貼って「インデックス登録をリクエスト」。')
    o.append('')
    day, n = 1, 0
    for r in actionable:
        if n % 10 == 0:
            o.append('')
            o.append('### Day %d' % day)
            o.append('')
            o.append('```')
            day += 1
        o.append(r['url'])
        n += 1
        if n % 10 == 0:
            o.append('```')
    if n % 10:
        o.append('```')
    o.append('')

    o.append('## 優先順の内訳')
    o.append('')
    o.append('| 順 | 区分 | 本数 |')
    o.append('|---|---|---|')
    seen = {}
    for r in actionable:
        seen.setdefault((r['rank'], r['why']), 0)
        seen[(r['rank'], r['why'])] += 1
    for (rank, why), c in sorted(seen.items()):
        o.append('| %d | %s | %d |' % (rank, why, c))
    o.append('')

    if stale:
        o.append('## ⚠ 判定が古い可能性（未インデックスなのにGSCに表示がある）')
        o.append('')
        o.append('index_status の確認日が古く、その後インデックスされた可能性がある。'
                 '**申請前にGSCで実機確認してよい。**')
        o.append('')
        o.append('| URL | 表示 | 確認日 |')
        o.append('|---|---|---|')
        for r in sorted(stale, key=lambda r: -r['imp']):
            o.append('| `%s` | %d | %s |' % (r['path'], r['imp'], r['checked']))
        o.append('')

    io.open(OUT, 'w', encoding='utf-8').write('\n'.join(o) + '\n')
    print('wrote %s' % OUT)
    print('  未インデックス %d本 / うち申請対象 %d本 / 除外 %d本 / Google未認識 %d本'
          % (len(rows), len(actionable), len(excluded), len(unknown)))


if __name__ == '__main__':
    main()

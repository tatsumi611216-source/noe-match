# -*- coding: utf-8 -*-
"""ツールページ（/tools/）を「インデックス × 流入 × 内部リンク」で棚卸しする。

なぜ記事と分けて見るか（2026-08-21に確立）:

ツールは `strategy_2026_ai_search.md` で「AIに要約されない防御資産」として作った
別カテゴリの資産である。記事監査（article_audit.py）は articles/ しか見ないため、
ツール11本はどの台帳にも載っておらず、実績が誰にも見えていなかった。

実際に見たら、11本中3本が未インデックスで、そのうち1本は内部リンク35本を
持ちながら Google に認識すらされていなかった。**記事の索引は毎日見ているのに、
ツールの索引は一度も見ていなかった**というのが原因である。

見る3列の意味:

  インデックス … 読まれる可能性があるか。無ければ他の2列は測定不能
  流入         … GSCの表示・クリック・平均順位
  内部リンク   … 記事側からの導線。多いのに流入ゼロなら「導線不足」ではなく
                  「そのクエリで勝てていない」と読む（打ち手が正反対になる）

使い方:
    python3 scripts/tools_audit.py      # agent/tools_audit.md を再生成
"""
import glob
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.noe-match.com'
OUT = os.path.join(ROOT, 'agent', 'tools_audit.md')

INDEXED = 'Submitted and indexed'


def read(path):
    with io.open(path, encoding='utf-8') as fh:
        return fh.read()


def load(path):
    return json.loads(read(path))


def tool_slugs():
    return sorted(os.path.basename(p.rstrip(os.sep))
                  for p in glob.glob(os.path.join(ROOT, 'tools', '*', '')))


def title_of(slug):
    path = os.path.join(ROOT, 'tools', slug, 'index.html')
    if not os.path.exists(path):
        return ''
    m = re.search(r'<title>([^<]*)</title>', read(path))
    return m.group(1).split('｜')[0].strip() if m else ''


def inbound_counts(slugs):
    """記事・トップからツールへの内部リンク本数（リンク元ファイル数）。"""
    pages = glob.glob(os.path.join(ROOT, 'articles', '*', 'index.html'))
    pages += [os.path.join(ROOT, f) for f in ('index.html', 'about.html')]
    bodies = []
    for p in pages:
        if os.path.exists(p):
            bodies.append(read(p))
    return {s: sum(1 for b in bodies if '/tools/%s/' % s in b) for s in slugs}


def main():
    gsc = load(os.path.join(ROOT, 'agent', 'gsc_data.json'))
    idx = load(os.path.join(ROOT, 'agent', 'index_status.json'))
    slugs = tool_slugs()
    inbound = inbound_counts(slugs)

    by_page = {r['page']: r for r in gsc.get('by_page', [])}
    queries = {}
    for r in gsc.get('by_query_page', []):
        if '/tools/' in r['page']:
            queries.setdefault(r['page'], []).append(r)

    rows = []
    for s in slugs:
        url = '%s/tools/%s/' % (SITE, s)
        st = idx['results'].get(url, {})
        g = by_page.get(url, {})
        rows.append({
            'slug': s,
            'title': title_of(s),
            'url': url,
            'state': st.get('coverageState', '未確認'),
            'checked': (st.get('checked_at') or '')[:10],
            'imp': g.get('impressions', 0),
            'clk': g.get('clicks', 0),
            'pos': g.get('position'),
            'inbound': inbound[s],
        })
    rows.sort(key=lambda r: (-r['imp'], -r['clk'], r['slug']))

    live = [r for r in rows if r['state'] == INDEXED]
    dead = [r for r in rows if r['state'] != INDEXED]
    tot_i = sum(r['imp'] for r in rows)
    tot_c = sum(r['clk'] for r in rows)

    o = []
    o.append('# ツール監査：インデックス × 流入 × 内部リンク')
    o.append('')
    o.append('**自動生成: `scripts/tools_audit.py`。手で編集しない。**')
    o.append('')
    o.append('GSC期間: %s 〜 %s（取得 %s） / index_status 取得: %s'
             % (gsc['period']['start'], gsc['period']['end'],
                gsc.get('fetched_at', '?')[:10], idx.get('fetched_at', '?')[:10]))
    o.append('')
    o.append('ツール %d本 / インデックス済み %d本 / 未インデックス %d本 / 総表示 %d・総クリック %d'
             % (len(rows), len(live), len(dead), tot_i, tot_c))
    o.append('')
    o.append('## 一覧')
    o.append('')
    o.append('| 表示 | クリック | 平均順位 | 内部リンク | インデックス | ツール |')
    o.append('|---|---|---|---|---|---|')
    for r in rows:
        pos = '%.1f' % r['pos'] if r['pos'] is not None else '—'
        mark = '' if r['state'] == INDEXED else ' ⚠'
        o.append('| %d | %d | %s | %d | %s%s | `%s`<br>%s |'
                 % (r['imp'], r['clk'], pos, r['inbound'], r['state'], mark,
                    r['slug'], r['title']))
    o.append('')

    if dead:
        o.append('## ⚠ 未インデックス（読まれる可能性がゼロ）')
        o.append('')
        o.append('`agent/index_request_queue.md` の未申請欄に入れて、人間がGSCから申請する。')
        o.append('')
        for r in dead:
            o.append('- **`/tools/%s/`** — %s（確認 %s）／内部リンク %d本'
                     % (r['slug'], r['state'], r['checked'] or '不明', r['inbound']))
            if r['state'] == 'URL is unknown to Google' and r['inbound'] > 0:
                o.append('  - 内部リンクが %d本あってGoogleが認識していない。申請で解消しない場合は'
                         'リンク先URLの綴り・実URLの200応答・sitemap再送信を順に確認する' % r['inbound'])
        o.append('')

    o.append('## 流入のあるクエリ')
    o.append('')
    if queries:
        o.append('| 平均順位 | 表示 | クリック | クエリ | ツール |')
        o.append('|---|---|---|---|---|')
        flat = [r for rs in queries.values() for r in rs]
        for r in sorted(flat, key=lambda r: -r['impressions']):
            o.append('| %.1f | %d | %d | %s | `%s` |'
                     % (r['position'], r['impressions'], r['clicks'], r['query'],
                        r['page'].replace(SITE + '/tools/', '').strip('/')))
    else:
        o.append('（GSCの取得範囲内に、ツールページのクエリ行が無い）')
    o.append('')
    o.append('※ `gsc_data.json` の `by_query_page` は250行上限で切れる。'
             '表示の小さいクエリは載らないため、この表は下限値である。')
    o.append('')

    o.append('## 読み方（打ち手が正反対になる分岐）')
    o.append('')
    o.append('- **内部リンクが多いのに表示ゼロ** … 導線不足ではない。'
             'そのクエリで勝てていない。リンクを増やしても変わらないので、'
             '勝てるクエリへ看板を掛け替えるか、投資対象から外す')
    o.append('- **未インデックス** … 流入ゼロは「負けた」ではなく「まだ試合をしていない」。'
             '申請が先で、内容の評価はその後')
    o.append('- **表示はあるが31位以下** … 収益に一切つながらない。'
             '判定指標には使わない（`agent/decision_gate.md`）')
    o.append('')

    io.open(OUT, 'w', encoding='utf-8').write('\n'.join(o) + '\n')
    print('wrote %s (%d tools, %d not indexed)' % (OUT, len(rows), len(dead)))


if __name__ == '__main__':
    main()

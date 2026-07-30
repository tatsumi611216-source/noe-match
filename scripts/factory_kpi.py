#!/usr/bin/env python3
"""記事工場のKPI計測（Phase 5：自己最適化の入力・2026-07-30制定）

gsc_data.json と記事の実体から、工場自身の性能を測る。
結果は agent/kpi_history.json に追記され、時系列で比較できる。

このスクリプトは判断をしない。数字を出すだけ。
数字を見てAGENT.mdのルールを書き換えるのはエージェントの仕事（Phase 5）。

測る対象は「記事の出来」ではなく「工場のルールが正しいか」：

  1. 順位帯別のクリック収率  → 「どの順位から先が金になるか」
  2. クラスタ別のクリック効率 → 「どのテーマを作るべきか」
  3. 選定ルールの的中率      → 「キーワード選定は当たっているか」
  4. 強化ルールの有効性      → 「追記強化は順位を上げているか」

使い方:
    python3 scripts/factory_kpi.py              # 計測してレポート表示＋履歴に追記
    python3 scripts/factory_kpi.py --no-append  # 履歴に追記せず表示だけ
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
HISTORY = os.path.join(ROOT, 'agent', 'kpi_history.json')

# クラスタ判定（スラッグのパターン → クラスタ名）。上から順に最初に当たったもの。
CLUSTERS = [
    ('データ・統計', ('-data', 'success-rate', 'wariai')),
    ('地域ガイド', ('tokyo-', 'osaka-', 'kyoto-', 'sapporo-', 'fukuoka-', 'nagoya-',
                  'kobe-', 'inaka-', '-guide-area')),
    ('探偵・離婚', ('tantei', 'uwaki', 'rikon', 'sokou')),
    ('相談所', ('soudanjo', 'agency', 'naco', 'excellence')),
    ('結婚準備', ('kekkon-', 'shikijo', 'propose', 'yubiwa', 'uchiiwai', 'houkoku',
               'maedori', 'bridal', 'osechi', 'gosyugi')),
    ('新生活', ('shinkon', 'dousei', 'shinkyo', 'kaden', 'yachin', 'hikari', 'sim')),
    ('属性別', ('nurse', 'civil-servant', 'student', 'batsuichi', '20s', '30s', '40s',
              'hitomishiri', 'pocchari', 'seishain')),
    ('アプリ別', ('youbride', 'marrish', 'omiai', 'tapple', 'pairs', 'with-', 'bachelor')),
    ('ノウハウ', ('message', 'photo', 'profile', 'fraud', 'date-', 'first-date',
               'anti-', 'time-management')),
]


def cluster_of(slug):
    for name, pats in CLUSTERS:
        if any(p in slug for p in pats):
            return name
    return 'その他'


def slug_of(url):
    m = re.search(r'/articles/([^/]+)/', url)
    return m.group(1) if m else '(top)'


def band_of(pos):
    if pos <= 10:
        return '1-10位'
    if pos <= 30:
        return '11-30位'
    if pos <= 50:
        return '31-50位'
    return '51位以下'


def load_gsc():
    if not os.path.exists(GSC):
        sys.exit('agent/gsc_data.json が無い。先にGSCデータを取得すること。')
    with open(GSC, encoding='utf-8') as f:
        return json.load(f)


def measure(gsc):
    by_page = gsc.get('by_page', [])
    by_qp = gsc.get('by_query_page', [])

    total_clicks = sum(p['clicks'] for p in by_page)
    total_imp = sum(p['impressions'] for p in by_page)

    # 1. 順位帯別のクリック収率（クエリ×ページ粒度でしか順位が取れないためこちらを使う）
    bands = defaultdict(lambda: {'impressions': 0, 'clicks': 0})
    for r in by_qp:
        b = bands[band_of(r['position'])]
        b['impressions'] += r['impressions']
        b['clicks'] += r['clicks']
    for b in bands.values():
        b['ctr'] = round(b['clicks'] / b['impressions'] * 100, 1) if b['impressions'] else 0.0

    # 2. クラスタ別のクリック効率
    clusters = defaultdict(lambda: {'pages': 0, 'impressions': 0, 'clicks': 0, '_wpos': 0})
    for p in by_page:
        slug = slug_of(p['page'])
        if slug == '(top)':
            continue
        c = clusters[cluster_of(slug)]
        c['pages'] += 1
        c['impressions'] += p['impressions']
        c['clicks'] += p['clicks']
        c['_wpos'] += p.get('position', 0) * p['impressions']
    for c in clusters.values():
        c['avg_position'] = round(c['_wpos'] / c['impressions'], 1) if c['impressions'] else None
        c['clicks_per_page'] = round(c['clicks'] / c['pages'], 2) if c['pages'] else 0
        c['ctr'] = round(c['clicks'] / c['impressions'] * 100, 1) if c['impressions'] else 0.0
        del c['_wpos']

    # 3. 選定ルールの的中率：10位以内に入っているクエリ／記事はどれだけあるか
    top10_queries = sorted({r['query'] for r in by_qp if r['position'] <= 10})
    top10_pages = sorted({slug_of(r['page']) for r in by_qp if r['position'] <= 10})
    pages_with_clicks = sorted({slug_of(p['page']) for p in by_page if p['clicks'] > 0})

    live = live_article_count()
    measured = len({slug_of(p['page']) for p in by_page}) - (1 if any(
        slug_of(p['page']) == '(top)' for p in by_page) else 0)

    return {
        'period': gsc.get('period'),
        'fetched_at': gsc.get('fetched_at'),
        'totals': {
            'live_articles': live,
            'articles_with_impressions': measured,
            'silent_rate': round((live - measured) / live * 100, 1) if live else None,
            'impressions': total_imp,
            'clicks': total_clicks,
            'ctr': round(total_clicks / total_imp * 100, 2) if total_imp else 0.0,
        },
        'position_bands': dict(bands),
        'clusters': dict(clusters),
        'top10_queries': top10_queries,
        'top10_pages': top10_pages,
        'pages_with_clicks': pages_with_clicks,
    }


def live_article_count():
    with open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8') as f:
        return len(set(re.findall(r'/articles/([^/]+)/</loc>', f.read())))


def report(kpi, prev):
    t = kpi['totals']
    print(f"■ 計測期間: {kpi['period']['start']} 〜 {kpi['period']['end']}")
    print(f"稼働記事 {t['live_articles']}本 / 表示のあった記事 {t['articles_with_impressions']}本 "
          f"（沈黙率 {t['silent_rate']}%）")
    print(f"表示 {t['impressions']} / クリック {t['clicks']} / CTR {t['ctr']}%")
    if prev:
        pt = prev['totals']
        print(f"  前回比: クリック {pt['clicks']} → {t['clicks']}  "
              f"沈黙率 {pt['silent_rate']}% → {t['silent_rate']}%")

    print('\n■ 順位帯別のクリック収率（どの順位から金になるか）')
    for b in ('1-10位', '11-30位', '31-50位', '51位以下'):
        d = kpi['position_bands'].get(b)
        if d:
            print(f"  {b:8s} 表示{d['impressions']:5d}  クリック{d['clicks']:4d}  CTR {d['ctr']:5.1f}%")

    print('\n■ クラスタ別のクリック効率（何を作るべきか）')
    rows = sorted(kpi['clusters'].items(), key=lambda x: -x[1]['clicks_per_page'])
    print(f"  {'クラスタ':14s}{'本':>3s}{'クリック':>7s}{'クリック/本':>10s}{'CTR':>7s}{'平均順位':>8s}")
    for name, c in rows:
        pos = f"{c['avg_position']}" if c['avg_position'] is not None else '-'
        print(f"  {name:14s}{c['pages']:3d}{c['clicks']:7d}{c['clicks_per_page']:10.2f}"
              f"{c['ctr']:6.1f}%{pos:>8s}")

    print(f"\n■ 10位以内のクエリ {len(kpi['top10_queries'])}件 / 該当記事 {len(kpi['top10_pages'])}本")
    for q in kpi['top10_queries']:
        print(f"  ・{q}")
    print(f"■ クリックを得た記事 {len(kpi['pages_with_clicks'])}本")
    for p in kpi['pages_with_clicks']:
        print(f"  ・{p}")

    print('\n■ 反証チェック（AGENT.mdのルールが実測と矛盾していないか）')
    for line in falsification_checks(kpi):
        print(f"  {line}")


def falsification_checks(kpi):
    """AGENT.mdの各ルールに紐づく反証条件を実測に当てて判定する。

    ここで「反証」と出たルールは、Phase 5でエージェントが書き換える対象になる。
    """
    out = []
    bands = kpi['position_bands']
    clusters = kpi['clusters']

    # ルール: 選定は「10位以内に入れるか」で決める（表示回数で決めない）
    low = sum(bands.get(b, {}).get('clicks', 0) for b in ('31-50位', '51位以下'))
    low_imp = sum(bands.get(b, {}).get('impressions', 0) for b in ('31-50位', '51位以下'))
    if low_imp == 0:
        out.append('△ 選定ルール: 31位以下の表示が無く判定不能')
    elif low == 0:
        out.append(f'✔ 選定ルール 維持: 31位以下の表示{low_imp}回からクリック0件。'
                   '順位重視の選定基準は妥当')
    else:
        out.append(f'✘ 選定ルール 反証: 31位以下の表示{low_imp}回からクリック{low}件が発生。'
                   '「31位以下は0円」という前提が崩れた。閾値を見直すこと')

    # ルール: クラスタの良し悪しはクリックで見る（表示回数で見ない）
    if clusters:
        by_clicks = max(clusters.items(), key=lambda x: x[1]['clicks_per_page'])
        by_imp = max(clusters.items(),
                     key=lambda x: x[1]['impressions'] / x[1]['pages'] if x[1]['pages'] else 0)
        if by_clicks[0] != by_imp[0]:
            out.append(f'✔ 指標ルール 維持: クリック最優秀「{by_clicks[0]}」と'
                       f'表示最優秀「{by_imp[0]}」が不一致。表示回数で判断すると誤る')
        else:
            out.append(f'△ 指標ルール: クリックと表示の最優秀が同じ「{by_clicks[0]}」。'
                       '今期は両指標が一致しており判別力なし')

    # ルール: 沈黙記事が過半なら、生産より流通（インデックス・内部リンク）が問題
    t = kpi['totals']
    if t['silent_rate'] is not None and t['silent_rate'] >= 50:
        out.append(f'⚠ 生産ルール 要検討: 稼働記事の{t["silent_rate"]}%が表示ゼロ。'
                   '新規生産より、既存記事のインデックス・内部リンクの点検が先')

    # ルール: 11-30位ゾーンの強化は有効か
    mid = bands.get('11-30位')
    if mid and mid['impressions'] >= 10:
        if mid['clicks'] == 0:
            out.append(f'✘ 強化ルール 反証: 11-30位の表示{mid["impressions"]}回でクリック0件。'
                       '強化対象ゾーンの下限を10位側へ引き上げることを検討')
        else:
            out.append(f'✔ 強化ルール 維持: 11-30位でクリック{mid["clicks"]}件。'
                       'このゾーンへの投資は回収できている')
    else:
        out.append('△ 強化ルール: 11-30位の標本が少なく判定不能（表示10回未満）')

    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-append', action='store_true', help='履歴に追記しない')
    args = parser.parse_args()

    gsc = load_gsc()
    kpi = measure(gsc)

    history = []
    if os.path.exists(HISTORY):
        with open(HISTORY, encoding='utf-8') as f:
            history = json.load(f)
    prev = history[-1] if history else None

    report(kpi, prev)

    if not args.no_append:
        # 同一計測期間の再実行は上書きする（週次で回しても履歴が汚れないように）
        history = [h for h in history if h.get('period') != kpi['period']]
        history.append(kpi)
        history.sort(key=lambda h: h['period']['end'])
        with open(HISTORY, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=1)
        print(f'\nagent/kpi_history.json に追記した（通算{len(history)}期分）')

    return 0


if __name__ == '__main__':
    sys.exit(main())

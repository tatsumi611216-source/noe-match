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
  5. コホート別の露出到達    → 「新記事は表示に到達しているか（インデックスの進行）」

注意：「表示ゼロ」は「インデックスされていない」ではない。インデックス済みでも
どのクエリでも100位以内に入らなければ表示は立たない。この2つは GSC の
検索パフォーマンスだけでは区別できないので、混同しないこと。

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


def publish_dates():
    """スラッグ → 公開日。キュー管理外の記事は None（＝キュー導入前から存在）。

    sitemap.xml の lastmod は「最終更新日」であって公開日ではない
    （2026-07-04に56本が一括更新されている）ため、公開日の代わりには使えない。
    """
    with open(QUEUE, encoding='utf-8') as f:
        queue = json.load(f)['queue']
    return {i['slug']: i.get('published') for i in queue if i.get('published')}


def cohorts(slugs, pub, window_start, window_end):
    """計測期間との前後関係で記事を3つに分ける。

    - legacy   : キュー管理外。計測期間より前から存在する初期の記事群
    - in_window: 計測期間の途中で公開された記事（露出の機会が期間より短い）
    - after    : 計測期間の終了後に公開された記事。**分母に入れてはいけない**
    """
    legacy, in_window, after = set(), set(), set()
    for s in slugs:
        d = pub.get(s)
        if d is None:
            legacy.add(s)
        elif d > window_end:
            after.add(s)
        else:
            in_window.add(s)
    return legacy, in_window, after


def rewrite_effect(measured_slugs, window_end, grace_days=21):
    """寄せ直し（agent/rewrites.json）が表示到達につながったかを集計する。

    寄せ直し直後は評価できないので、猶予期間を過ぎたものだけを分母にする。
    """
    path = os.path.join(ROOT, 'agent', 'rewrites.json')
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        rewrites = json.load(f)
    if not rewrites:
        return {'evaluated': 0, 'reached': 0, 'pending': 0}

    from datetime import date

    def age(d):
        return (date(*map(int, window_end.split('-'))) - date(*map(int, d.split('-')))).days

    evaluated = reached = pending = 0
    for slug, rec in rewrites.items():
        if age(rec['date']) < grace_days:
            pending += 1
            continue
        evaluated += 1
        if slug in measured_slugs:
            reached += 1
    return {'evaluated': evaluated, 'reached': reached, 'pending': pending}


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

    # 4. コホート別の露出到達（インデックスの進行を見る）
    #    計測期間の終了後に公開された記事を分母に入れると沈黙率が過大に出る。
    #    2026-07-30の初回計測では、この誤りで 73.0% を 88.0% と報告していた。
    live_slugs_set = set(live_slugs())
    pub = publish_dates()
    ws = gsc['period']['start']
    we = gsc['period']['end']
    legacy, in_window, after = cohorts(live_slugs_set, pub, ws, we)
    measured_slugs = {slug_of(p['page']) for p in by_page} - {'(top)'}

    eligible = legacy | in_window
    measured_eligible = measured_slugs & eligible

    cohort_stats = {}
    for name, members in (('legacy', legacy), ('in_window', in_window), ('after_window', after)):
        seen = measured_slugs & members
        cohort_stats[name] = {
            'articles': len(members),
            'with_impressions': len(seen),
            'reach_rate': round(len(seen) / len(members) * 100, 1) if members else None,
        }

    live = len(live_slugs_set)
    silent = (len(eligible) - len(measured_eligible)) / len(eligible) * 100 if eligible else None

    return {
        'period': gsc.get('period'),
        'fetched_at': gsc.get('fetched_at'),
        'totals': {
            'live_articles': live,
            'eligible_articles': len(eligible),
            'excluded_published_after_window': len(after),
            'articles_with_impressions': len(measured_eligible),
            'silent_rate': round(silent, 1) if silent is not None else None,
            'impressions': total_imp,
            'clicks': total_clicks,
            'ctr': round(total_clicks / total_imp * 100, 2) if total_imp else 0.0,
        },
        'cohorts': cohort_stats,
        'rewrites': rewrite_effect(measured_slugs, we),
        'position_bands': dict(bands),
        'clusters': dict(clusters),
        'top10_queries': top10_queries,
        'top10_pages': top10_pages,
        'pages_with_clicks': pages_with_clicks,
    }


def live_slugs():
    """sitemap.xml に載っている＝出荷済みの記事スラッグ"""
    with open(os.path.join(ROOT, 'sitemap.xml'), encoding='utf-8') as f:
        return set(re.findall(r'/articles/([^/]+)/</loc>', f.read()))


def report(kpi, prev):
    t = kpi['totals']
    print(f"■ 計測期間: {kpi['period']['start']} 〜 {kpi['period']['end']}")
    print(f"稼働記事 {t['live_articles']}本（うち期間終了後に公開された "
          f"{t['excluded_published_after_window']}本は計測対象外）")
    print(f"計測対象 {t['eligible_articles']}本 / 表示のあった記事 "
          f"{t['articles_with_impressions']}本（表示ゼロ率 {t['silent_rate']}%）")
    print(f"表示 {t['impressions']} / クリック {t['clicks']} / CTR {t['ctr']}%")
    if prev:
        pt = prev['totals']
        print(f"  前回比: クリック {pt['clicks']} → {t['clicks']}  "
              f"表示到達 {pt['articles_with_impressions']}本 → {t['articles_with_impressions']}本")

    print('\n■ コホート別の露出到達（インデックスの進行）')
    labels = {'legacy': 'キュー管理外（初期）', 'in_window': '期間中に公開',
              'after_window': '期間後に公開（対象外）'}
    for key, label in labels.items():
        c = kpi['cohorts'][key]
        rate = f"{c['reach_rate']}%" if c['reach_rate'] is not None else '-'
        print(f"  {label:22s} {c['articles']:3d}本中 表示あり {c['with_impressions']:3d}本  到達率 {rate}")

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

    # ルール: 表示ゼロが多いとき、生産より流通が問題なのか
    #
    # 2026-07-30改定：旧版は「稼働記事の50%以上が表示ゼロなら流通が詰まっている」と
    # 判定していたが、①計測期間の終了後に公開された記事まで分母に入れていた
    # ②公開からの経過日数を無視していた、の2点で誤りだった。
    # 新記事は表示に到達しているのに「流通が詰まっている」と誤判定する。
    # 判定は静的な比率ではなく、新旧コホートの到達率の差と、期間をまたいだ増減で見る。
    t = kpi['totals']
    co = kpi.get('cohorts', {})
    new_reach = co.get('in_window', {}).get('reach_rate')
    old_reach = co.get('legacy', {}).get('reach_rate')

    if new_reach is not None and old_reach is not None and co['in_window']['articles'] >= 3:
        if new_reach >= old_reach:
            out.append(f'✔ 流通ルール 維持: 期間中に公開した記事の表示到達率{new_reach}%が'
                       f'初期記事{old_reach}%以上。インデックスは進んでおり、'
                       'パイプラインは詰まっていない')
        else:
            out.append(f'✘ 流通ルール 反証: 新記事の表示到達率{new_reach}%が'
                       f'初期記事{old_reach}%を下回った。新記事が拾われなくなっている'
                       '（sitemap・内部リンク・クロール状況を点検すること）')
    elif t['silent_rate'] is not None and t['silent_rate'] >= 50:
        out.append(f'△ 流通ルール: 計測対象{t["eligible_articles"]}本の'
                   f'{t["silent_rate"]}%が表示ゼロだが、コホート比較の標本が足りず'
                   '流通の問題かは判定不能')

    # ルール: 表示ゼロ記事は「タイトルを固有修飾側へ寄せ直す」ことで救える
    #        （2026-07-30制定。打ち手そのものが効いているかを毎月疑う）
    rw = kpi.get('rewrites')
    if rw and rw['evaluated'] >= 3:
        if rw['reached'] == 0:
            out.append(f'✘ 寄せ直しルール 反証: 猶予期間を過ぎた{rw["evaluated"]}本すべてが'
                       '表示ゼロのまま。タイトルの寄せ直しでは足りない。'
                       '記事の主題そのものを変える打ち手へ切り替えること')
        else:
            rate = rw['reached'] / rw['evaluated'] * 100
            out.append(f'✔ 寄せ直しルール 維持: 評価{rw["evaluated"]}本中{rw["reached"]}本が'
                       f'表示に到達（{rate:.0f}%）。打ち手は効いている')
    elif rw and rw['evaluated'] + rw['pending'] > 0:
        out.append(f'△ 寄せ直しルール: 評価可能な標本が{rw["evaluated"]}本で不足'
                   f'（観測中{rw["pending"]}本）')

    # 表示ゼロの主体が初期記事側に偏っているなら、対象は新規生産ではなく初期記事の見直し
    if old_reach is not None and old_reach < 50 and co['legacy']['articles'] >= 20:
        out.append(f'⚠ 初期記事 要検討: キュー管理外の初期{co["legacy"]["articles"]}本の'
                   f'表示到達率が{old_reach}%。公開から最も時間が経っているのに'
                   '表示に至っていない（2026-07-30の調査では原因は狙ったクエリの'
                   '競合の厚さだった）。`scripts/silent_scan.py` の最優先欄から寄せ直すこと')

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

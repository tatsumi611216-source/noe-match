#!/usr/bin/env python3
"""GSC定点レポート — 取りこぼしクリック数で改善優先度を並べ、週次の変化を可視化する。

`agent/gsc_data.json`（fetch_gsc.py の出力）を読み、
順位別の期待CTRと実績CTRの差から「取りこぼしているクリック数」を算出して
改善優先度を機械的に決める。週次スナップショットを `agent/gsc_history.json` に
積み、前回との差分（順位・クリック・表示）も出す。

判断はしない。数字を出して並べるだけ。何を書き直すかは人間が決める。

使い方:
    python3 scripts/gsc_report.py                  # 計測 → HTML出力 → 履歴に追記
    python3 scripts/gsc_report.py --no-append      # 履歴に追記しない
    python3 scripts/gsc_report.py --top 30         # 上位30件まで表示（既定20）
    python3 scripts/gsc_report.py --output out.html
"""
import argparse
import datetime
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GSC = os.path.join(ROOT, 'agent', 'gsc_data.json')
HISTORY = os.path.join(ROOT, 'agent', 'gsc_history.json')
OUT_DIR = os.path.join(ROOT, 'outputs')

# 順位別の期待CTR（推定値）。
# 出典：検索順位とCTRの関係についての公開調査の代表値をならしたもの。
# サイトやクエリの性質で実際は上下するため、これは「絶対的な正解」ではなく
# 記事を横並びで比べるための共通のものさしとして使う。
# 自サイトの実績で補正したい場合は EXPECTED_CTR を書き換えること。
EXPECTED_CTR = [
    (1, 0.28), (2, 0.15), (3, 0.11), (4, 0.08), (5, 0.06),
    (6, 0.05), (7, 0.04), (8, 0.03), (9, 0.028), (10, 0.025),
    (15, 0.015), (20, 0.010), (30, 0.005), (50, 0.002), (100, 0.001),
]

# 「ここまで上げられたら」と仮定する到達順位。取りこぼしの計算基準。
TARGET_POSITION = 5

# 表示がこれ未満のページは母数が小さすぎるため優先度リストから外す
MIN_IMPRESSIONS = 5


def expected_ctr(position):
    """順位から期待CTRを返す（表の間は線形で補間する）"""
    if position <= EXPECTED_CTR[0][0]:
        return EXPECTED_CTR[0][1]
    for i in range(len(EXPECTED_CTR) - 1):
        p1, c1 = EXPECTED_CTR[i]
        p2, c2 = EXPECTED_CTR[i + 1]
        if p1 <= position <= p2:
            ratio = (position - p1) / (p2 - p1)
            return c1 + (c2 - c1) * ratio
    return EXPECTED_CTR[-1][1]


def classify(page):
    """改善の型を判定する。何をすべきかが型で決まる。"""
    pos, imp, clicks = page['position'], page['impressions'], page['clicks']
    ctr = clicks / imp if imp else 0
    if pos <= 10:
        # 1ページ目にいるのに取れていない = 見出しで負けている
        return ('タイトル負け', 'タイトル・説明文の書き直し') if ctr < expected_ctr(pos) * 0.6 \
            else ('好調', '維持。内部リンクの供給元に使う')
    if pos <= 20:
        return ('あと一歩', '内部リンク追加・見出し補強で1ページ目へ')
    if pos <= 50:
        return ('圏外', '狙うクエリの見直し。競合が厚い可能性')
    return ('遠い', '記事の作り直しか、別クエリへの寄せ直し')


def analyze(data, top_n=20):
    pages = [p for p in data.get('by_page', []) if p['impressions'] >= MIN_IMPRESSIONS]
    target_ctr = expected_ctr(TARGET_POSITION)

    rows = []
    for p in pages:
        imp, clicks, pos = p['impressions'], p['clicks'], p['position']
        potential = imp * target_ctr           # TARGET_POSITION まで上げた場合の想定クリック
        lost = max(0.0, potential - clicks)    # 取りこぼしているクリック数
        kind, action = classify(p)
        rows.append({
            'page': p['page'],
            'slug': p['page'].rstrip('/').split('/')[-1],
            'impressions': imp,
            'clicks': clicks,
            'ctr': round(clicks / imp * 100, 1) if imp else 0.0,
            'position': pos,
            'expected_ctr': round(expected_ctr(pos) * 100, 1),
            'lost_clicks': round(lost, 1),
            'kind': kind,
            'action': action,
        })
    rows.sort(key=lambda r: -r['lost_clicks'])

    by_page = data.get('by_page', [])
    totals = {
        'pages_with_impressions': len(by_page),
        'impressions': sum(p['impressions'] for p in by_page),
        'clicks': sum(p['clicks'] for p in by_page),
        'lost_clicks_total': round(sum(r['lost_clicks'] for r in rows), 1),
    }
    totals['ctr'] = round(totals['clicks'] / totals['impressions'] * 100, 2) if totals['impressions'] else 0.0

    # ページ別クエリ（何で拾われているか。書き直しの手がかりになる）
    queries = {}
    for q in data.get('by_query_page', []):
        queries.setdefault(q['page'], []).append(q)
    for page, qs in queries.items():
        qs.sort(key=lambda x: -x['impressions'])

    return {'rows': rows[:top_n], 'all_rows': rows, 'totals': totals, 'queries': queries}


def load_history():
    if not os.path.exists(HISTORY):
        return []
    with open(HISTORY, encoding='utf-8') as f:
        return json.load(f)


def diff_with_previous(rows, history):
    """前回スナップショットとの差分をつける。初回は None のまま。"""
    if not history:
        return rows
    prev = {r['slug']: r for r in history[-1].get('rows', [])}
    for r in rows:
        p = prev.get(r['slug'])
        if not p:
            r['delta'] = {'new': True}
            continue
        r['delta'] = {
            'new': False,
            'position': round(p['position'] - r['position'], 1),   # 正なら順位が上がった
            'clicks': r['clicks'] - p['clicks'],
            'impressions': r['impressions'] - p['impressions'],
        }
    return rows


def append_history(result, data):
    history = load_history()
    history.append({
        'recorded_at': datetime.datetime.now().isoformat(timespec='seconds'),
        'period': data.get('period'),
        'totals': result['totals'],
        'rows': [{k: r[k] for k in ('slug', 'position', 'clicks', 'impressions', 'lost_clicks')}
                 for r in result['all_rows']],
    })
    with open(HISTORY, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=1)
    return len(history)


def delta_html(delta, key, unit='', invert=False):
    """差分を色付きで表示する。invert=True は「小さいほど良い」指標用。"""
    if not delta or delta.get('new'):
        return '<span class="d-new">NEW</span>' if delta else ''
    v = delta.get(key, 0)
    if v == 0:
        return '<span class="d-flat">±0</span>'
    good = (v > 0) if not invert else (v < 0)
    sign = '+' if v > 0 else ''
    return f'<span class="{"d-up" if good else "d-down"}">{sign}{v}{unit}</span>'


def render_html(result, data, history_count):
    t = result['totals']
    period = data.get('period', {})
    generated = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

    kind_class = {'タイトル負け': 'k-title', 'あと一歩': 'k-near',
                  '圏外': 'k-far', '遠い': 'k-none', '好調': 'k-good'}

    trend_rows = ''
    for h in load_history()[-8:]:
        ht = h['totals']
        trend_rows += (f"<tr><td>{h['period']['start']}〜{h['period']['end']}</td>"
                       f"<td class='num'>{ht['impressions']}</td>"
                       f"<td class='num'>{ht['clicks']}</td>"
                       f"<td class='num'>{ht['ctr']}%</td>"
                       f"<td class='num'>{ht['lost_clicks_total']}</td></tr>")
    if not trend_rows:
        trend_rows = "<tr><td colspan='5' class='muted'>今回が初回のため推移はまだありません</td></tr>"

    body_rows = ''
    for i, r in enumerate(result['rows'], 1):
        qs = result['queries'].get(r['page'], [])[:3]
        qtext = ' / '.join(f"{q['query']}({q['impressions']})" for q in qs) or '—'
        d = r.get('delta')
        body_rows += f"""
        <tr>
          <td class="num">{i}</td>
          <td><a href="{r['page']}" target="_blank" rel="noopener">{r['slug']}</a>
              <span class="q">{qtext}</span></td>
          <td class="num">{r['position']} {delta_html(d, 'position')}</td>
          <td class="num">{r['impressions']} {delta_html(d, 'impressions')}</td>
          <td class="num">{r['clicks']} {delta_html(d, 'clicks')}</td>
          <td class="num">{r['ctr']}% <span class="muted">/{r['expected_ctr']}%</span></td>
          <td class="num lost"><span class="bar" style="width:{min(100, r['lost_clicks'] / max(1, result['rows'][0]['lost_clicks']) * 100):.0f}%"></span>{r['lost_clicks']}</td>
          <td><span class="kind {kind_class.get(r['kind'], '')}">{r['kind']}</span><br>
              <span class="muted">{r['action']}</span></td>
        </tr>"""

    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GSC定点レポート {period.get('end', '')}</title>
<style>
 :root {{ --bg:#12161C; --card:#1B212A; --line:#2C3542; --ink:#E6EAEF; --dim:#8B97A6;
          --accent:#5FA8E8; --hot:#E8A54A; --good:#5FBF8F; --bad:#E8705F; }}
 * {{ box-sizing:border-box }}
 body {{ margin:0; background:var(--bg); color:var(--ink); font-size:14px; line-height:1.6;
        font-family:"Hiragino Kaku Gothic ProN","Noto Sans JP","Yu Gothic UI",Meiryo,sans-serif }}
 .wrap {{ max-width:1240px; margin:0 auto; padding:24px 18px 60px }}
 header {{ border-bottom:2px solid var(--accent); padding-bottom:12px; margin-bottom:20px }}
 h1 {{ margin:0; font-size:22px; letter-spacing:.03em }}
 .sub {{ color:var(--dim); font-size:12px; margin-top:4px }}
 .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-bottom:22px }}
 .card {{ background:var(--card); border:1px solid var(--line); border-radius:6px; padding:12px 14px }}
 .card .k {{ font-size:11px; color:var(--dim); letter-spacing:.1em }}
 .card .v {{ font-size:24px; font-weight:700; font-variant-numeric:tabular-nums }}
 .card.hot .v {{ color:var(--hot) }}
 h2 {{ font-size:13px; letter-spacing:.14em; color:var(--dim); margin:26px 0 10px; font-weight:700 }}
 .scroll {{ overflow-x:auto; border:1px solid var(--line); border-radius:6px }}
 table {{ width:100%; border-collapse:collapse; background:var(--card); min-width:820px }}
 th,td {{ padding:8px 10px; text-align:left; border-top:1px solid var(--line); vertical-align:top }}
 th {{ background:#222A35; font-size:11px; letter-spacing:.08em; color:var(--dim); position:sticky; top:0 }}
 td.num {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap }}
 a {{ color:var(--accent); text-decoration:none }} a:hover {{ text-decoration:underline }}
 .q {{ display:block; color:var(--dim); font-size:11px; margin-top:2px }}
 .muted {{ color:var(--dim); font-size:11px }}
 .kind {{ display:inline-block; font-size:11px; padding:1px 7px; border-radius:3px; font-weight:700 }}
 .k-title {{ background:#4A3418; color:#E8A54A }} .k-near {{ background:#1C3A2C; color:#5FBF8F }}
 .k-far {{ background:#3A2320; color:#E8705F }} .k-none {{ background:#2C3542; color:#8B97A6 }}
 .k-good {{ background:#1B3348; color:#5FA8E8 }}
 td.lost {{ position:relative; font-weight:700; color:var(--hot) }}
 .bar {{ position:absolute; left:0; top:0; bottom:0; background:rgba(232,165,74,.14) }}
 .d-up {{ color:var(--good); font-size:11px }} .d-down {{ color:var(--bad); font-size:11px }}
 .d-flat {{ color:var(--dim); font-size:11px }} .d-new {{ color:var(--accent); font-size:10px; font-weight:700 }}
 .notes {{ margin-top:24px; padding:14px 16px; background:var(--card); border:1px solid var(--line);
           border-radius:6px; font-size:12px; color:var(--dim) }}
 .notes b {{ color:var(--ink) }}
</style></head><body><div class="wrap">
<header>
  <h1>GSC定点レポート — noe-match</h1>
  <div class="sub">対象期間 {period.get('start', '?')} 〜 {period.get('end', '?')} ／ 生成 {generated} ／ 第{history_count}回</div>
</header>

<div class="cards">
  <div class="card"><div class="k">表示のあるページ</div><div class="v">{t['pages_with_impressions']}</div></div>
  <div class="card"><div class="k">表示回数</div><div class="v">{t['impressions']}</div></div>
  <div class="card"><div class="k">クリック</div><div class="v">{t['clicks']}</div></div>
  <div class="card"><div class="k">CTR</div><div class="v">{t['ctr']}%</div></div>
  <div class="card hot"><div class="k">取りこぼしクリック</div><div class="v">{t['lost_clicks_total']}</div></div>
</div>

<h2>改善優先度（取りこぼしクリック数の多い順）</h2>
<div class="scroll"><table>
 <tr><th>#</th><th>記事 / 主なクエリ（表示数）</th><th>順位</th><th>表示</th><th>クリック</th>
     <th>CTR /期待</th><th>取りこぼし</th><th>型と打ち手</th></tr>
 {body_rows}
</table></div>

<h2>週次の推移</h2>
<div class="scroll"><table>
 <tr><th>期間</th><th>表示</th><th>クリック</th><th>CTR</th><th>取りこぼし合計</th></tr>
 {trend_rows}
</table></div>

<div class="notes">
 <b>数字の読み方</b><br>
 ・「取りこぼしクリック」＝ 表示回数 × {TARGET_POSITION}位相当の期待CTR − 実クリック。
   その記事を{TARGET_POSITION}位まで押し上げられたら増えるはずのクリック数。<br>
 ・期待CTRは公開されている順位別CTR調査の代表値をならした<b>推定値</b>で、実測ではない。
   記事を横並びで比べるものさしとして使う。絶対値は保証しない。<br>
 ・表示{MIN_IMPRESSIONS}回未満のページは母数が小さいため優先度リストから除外している
   （全{t['pages_with_impressions']}ページ中、掲載は{len(result['all_rows'])}ページ）。<br>
 ・差分（±表記）は前回スナップショットとの比較。順位は<b>上昇を＋</b>で表記している。<br>
 ・このレポートは判断をしない。何を書き直すかは人間が決める。
</div>
</div></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--top', type=int, default=20)
    ap.add_argument('--no-append', action='store_true')
    ap.add_argument('--output')
    args = ap.parse_args()

    if not os.path.exists(GSC):
        sys.exit(f'GSCデータがありません: {GSC}\n先に scripts/fetch_gsc.py を実行してください。')

    with open(GSC, encoding='utf-8') as f:
        data = json.load(f)

    result = analyze(data, top_n=args.top)
    result['rows'] = diff_with_previous(result['rows'], load_history())

    history_count = len(load_history()) + (0 if args.no_append else 1)
    if not args.no_append:
        append_history(result, data)

    os.makedirs(OUT_DIR, exist_ok=True)
    out = args.output or os.path.join(
        OUT_DIR, f"gsc_report_{data.get('period', {}).get('end', 'latest')}.html")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(render_html(result, data, history_count))

    t = result['totals']
    print(f"期間 {data.get('period', {}).get('start')} 〜 {data.get('period', {}).get('end')}")
    print(f"表示 {t['impressions']} / クリック {t['clicks']} / CTR {t['ctr']}% "
          f"/ 取りこぼし {t['lost_clicks_total']}クリック")
    print(f"\n改善優先度トップ5:")
    for i, r in enumerate(result['rows'][:5], 1):
        print(f"  {i}. {r['slug']:28s} {r['position']:5.1f}位 表示{r['impressions']:4d} "
              f"クリック{r['clicks']:3d} 取りこぼし{r['lost_clicks']:5.1f}  [{r['kind']}]")
    print(f"\nレポート: {out}")


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
"""判定ゲート（agent/decision_gate.md）の現在値 P1・P2・P3 を出す。

なぜ3指標だけか（2026-08-21に確立）:

総表示回数は判定指標として壊れている。2026-07-26→08-20の実測で
表示は235→1,775（7.6倍）に伸びたが、クリックは9→35に留まり、
CTRは3.83%→1.97%へ半減した。増えた分の大半は31位以下の表示で、
収益に一切つながらない。「頑張っている感」だけが出る指標なので使わない。

代わりに見るのは次の3つ:

  P1 10位以内クエリ数 … 質の伴った流入。GSCのbest position<=10のユニーククエリ
  P2 総クリック       … 実際にサイトへ来た人数
  P3 ASP確定件数      … 1円が発生したか（発生ではなく確定）

判定日と閾値は agent/decision_gate.md が正本。本スクリプトは値を出すだけで
判定はしない（閾値をコードに埋めると、閾値を変えた記録が残らないため）。

P1の注意:
  gsc_data.json の by_query_page はAPI取得時に250行で切れる。下位クエリを
  取りこぼすため P1 は下限値である。P1が上限250行に張り付いている場合は警告を出す。

使い方:
    python3 scripts/decision_gate.py
"""
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GSC = os.path.join(ROOT, 'agent', 'gsc_data.json')
KPI = os.path.join(ROOT, 'agent', 'kpi_history.json')
ASP = os.path.join(ROOT, 'agent', 'asp_results.md')

ROW_CAP = 250  # GSC取得時の行数上限。P1の取りこぼし判定に使う


def load(path):
    with io.open(path, encoding='utf-8') as fh:
        return json.load(fh)


def p1_top10_queries(gsc):
    """best position <= 10 のユニーククエリ数（下限値）。"""
    best = {}
    for row in gsc.get('by_query_page', []):
        q = row.get('query')
        pos = row.get('position')
        if q is None or pos is None:
            continue
        if q not in best or pos < best[q]:
            best[q] = pos
    return sorted(q for q, pos in best.items() if pos <= 10), len(best)


def p2_clicks(gsc, kpi):
    """総クリック。by_page の合計を使い、kpi_history の totals と突き合わせる。"""
    by_page = gsc.get('by_page', [])
    clicks = sum(r.get('clicks', 0) for r in by_page)
    imps = sum(r.get('impressions', 0) for r in by_page)
    latest = kpi[-1]['totals'] if kpi else {}
    return clicks, imps, latest


def p3_confirmed():
    """asp_results.md の確定件数。表を機械で読まず、人間の記入を要求する。

    このファイルは自由記述の台帳なので、数値を推測でパースすると
    「測っていない」と「測って0」を取り違える。合計行が無ければ不明を返す。
    """
    if not os.path.exists(ASP):
        return None
    text = io.open(ASP, encoding='utf-8').read()
    rows = re.findall(r'\|\s*\*\*合計\*\*\s*\|([^\n]*)', text)
    if not rows:
        return None
    cells = [c.strip().strip('*') for c in rows[-1].split('|')]
    nums = [c for c in cells if re.fullmatch(r'\d+', c)]
    # 合計行は「クリック / 発生 / 確定」の順。確定は3つ目。
    return int(nums[2]) if len(nums) >= 3 else None


def main():
    gsc = load(GSC)
    kpi = load(KPI)

    top10, uniq = p1_top10_queries(gsc)
    clicks, imps, totals = p2_clicks(gsc, kpi)
    confirmed = p3_confirmed()
    period = gsc.get('period', {})

    print('判定ゲート 現在値（正本: agent/decision_gate.md）')
    print('GSC期間: %s 〜 %s  (取得 %s)' % (
        period.get('start', '?'), period.get('end', '?'), gsc.get('fetched_at', '?')))
    print('')
    print('P1 10位以内クエリ数 : %d  （ユニーククエリ %d 件中・下限値）' % (len(top10), uniq))
    for q in top10:
        print('     - %s' % q)
    if len(gsc.get('by_query_page', [])) >= ROW_CAP:
        print('  ⚠ by_query_page が %d 行の上限に張り付いている。P1は取りこぼしを含む下限値。' % ROW_CAP)
    print('')
    print('P2 総クリック       : %d  （表示 %d / CTR %.2f%%）' % (
        clicks, imps, (clicks / imps * 100) if imps else 0.0))
    if totals:
        print('     kpi_history の直近 totals: クリック %s / 表示 %s' % (
            totals.get('clicks'), totals.get('impressions')))
    print('')
    if confirmed is None:
        print('P3 ASP確定件数      : 不明（asp_results.md に合計行が無い。人間が記入する）')
    else:
        print('P3 ASP確定件数      : %d' % confirmed)
    print('')
    print('判定日: 2026-09-09 / 2026-10-09 / 2026-12-09')
    print('閾値と分岐は agent/decision_gate.md を見て、判定ログに追記すること。')


if __name__ == '__main__':
    main()

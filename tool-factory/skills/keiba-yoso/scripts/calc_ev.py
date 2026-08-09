#!/usr/bin/env python3
"""
競馬 期待値（EV）計算スクリプト
====================================
使い方:
  python calc_ev.py <horse_data.json>

入力JSON形式:
  {
    "race_id": "202645040611",
    "race_name": "疾風迅雷賞(A2)",
    "dist": "ダ900",
    "horses": [
      {
        "umaban": "4",
        "name": "ハーフブルー",
        "horse_id": "2022107209",
        "win_odds": 2.3,
        "fukusho_odds_min": 1.1,  # 複勝下限（任意）
        "fukusho_odds_max": 1.4,  # 複勝上限（任意）
        "results": [
          {"rank": "1", "dist": "ダ1200", "odds": "4.0", "pop": "2"},
          {"rank": "4", "dist": "ダ1200", "odds": "4.6", "pop": "3"},
          ...
        ]
      }
    ]
  }

出力:
  レースEVレポート（stdout + {race_id}_ev.txt）
"""

import json
import sys
import os
import re
from pathlib import Path


def parse_dist(dist_str: str) -> tuple[str, int]:
    """
    "ダ1200" → ("ダ", 1200)
    "芝1600" → ("芝", 1600)
    """
    match = re.match(r'([ダ芝障])(\d+)', dist_str.replace('左', '').replace('右', '').strip())
    if match:
        return match.group(1), int(match.group(2))
    return '', 0


def calc_horse_ev(horse: dict, target_surface: str, target_dist: int) -> dict:
    """
    1頭分のEVを計算する。

    EV（期待値）= 推定勝率 × 単勝オッズ - 1
    例) 勝率30%・単勝3.0倍 → EV = 0.30 × 3.0 - 1 = -0.10  （マイナス10%）
    例) 勝率40%・単勝3.0倍 → EV = 0.40 × 3.0 - 1 = +0.20  （プラス20%）

    日本の馬券は約25%のテイクレートがあるため、
    無作為な馬に賭け続けた場合のEV ≈ -0.25 がベースライン。
    EV > -0.10 なら「妙味あり」、EV > 0 なら「理論的にプラス期待値」。
    """
    results = horse.get('results', [])
    name = horse.get('name', '?')
    win_odds = float(horse.get('win_odds') or 0)

    if not results:
        return {
            'umaban': horse.get('umaban', '?'),
            'name': name,
            'n_all': 0,
            'n_filtered': 0,
            'win_rate_all': None,
            'place_rate_all': None,
            'win_rate_filtered': None,
            'place_rate_filtered': None,
            'win_odds': win_odds,
            'ev_win_all': None,
            'ev_win_filtered': None,
            'ev_fuku_all': None,
            'ev_fuku_filtered': None,
            'note': '過去成績なし',
        }

    # --- 全成績での勝率・複勝率 ---
    valid_all = [r for r in results if r.get('rank', '').isdigit()]
    n_all = len(valid_all)
    wins_all = sum(1 for r in valid_all if r['rank'] == '1')
    places_all = sum(1 for r in valid_all if int(r['rank']) <= 3)
    win_rate_all = wins_all / n_all if n_all > 0 else None
    place_rate_all = places_all / n_all if n_all > 0 else None

    # --- 同条件（同馬場・近似距離±300m）での勝率・複勝率 ---
    filtered = []
    for r in valid_all:
        surf, dist = parse_dist(r.get('dist', ''))
        if surf == target_surface and abs(dist - target_dist) <= 300:
            filtered.append(r)
    n_filtered = len(filtered)
    wins_f = sum(1 for r in filtered if r['rank'] == '1')
    places_f = sum(1 for r in filtered if int(r['rank']) <= 3)
    win_rate_filtered = wins_f / n_filtered if n_filtered >= 3 else None  # サンプル3走未満は信頼度低
    place_rate_filtered = places_f / n_filtered if n_filtered >= 3 else None

    # --- EV計算 ---
    # 複勝オッズは出馬表には出ないため、参考値として win_odds から推算
    # 一般に複勝オッズ ≈ 単勝オッズ^0.45（経験則）
    fuku_odds_est = win_odds ** 0.45 if win_odds > 1 else None
    fuku_odds_given = horse.get('fukusho_odds_min')  # 取得できていれば優先

    fuku_odds = float(fuku_odds_given) if fuku_odds_given else fuku_odds_est

    def ev(rate, odds):
        if rate is None or odds is None or odds == 0:
            return None
        return round(rate * odds - 1, 3)

    ev_win_all = ev(win_rate_all, win_odds)
    ev_win_filtered = ev(win_rate_filtered, win_odds)
    ev_fuku_all = ev(place_rate_all, fuku_odds)
    ev_fuku_filtered = ev(place_rate_filtered, fuku_odds)

    # --- EV評価ラベル ---
    def ev_label(e):
        if e is None:
            return 'データ不足'
        if e >= 0.10:
            return '★★★ 高期待値'
        if e >= 0.00:
            return '★★  プラス期待値'
        if e >= -0.10:
            return '★   妙味あり'
        if e >= -0.20:
            return '    平均的'
        return '    割高（買い控え推奨）'

    # 優先するEV: 同条件サンプルが3走以上あれば filtered、なければ all
    best_ev_win = ev_win_filtered if win_rate_filtered is not None else ev_win_all
    best_ev_fuku = ev_fuku_filtered if place_rate_filtered is not None else ev_fuku_all

    return {
        'umaban': horse.get('umaban', '?'),
        'name': name,
        'n_all': n_all,
        'n_filtered': n_filtered,
        'win_rate_all': round(win_rate_all, 3) if win_rate_all is not None else None,
        'place_rate_all': round(place_rate_all, 3) if place_rate_all is not None else None,
        'win_rate_filtered': round(win_rate_filtered, 3) if win_rate_filtered is not None else None,
        'place_rate_filtered': round(place_rate_filtered, 3) if place_rate_filtered is not None else None,
        'win_odds': win_odds,
        'fuku_odds_used': round(fuku_odds, 2) if fuku_odds else None,
        'ev_win_all': ev_win_all,
        'ev_win_filtered': ev_win_filtered,
        'ev_fuku_all': ev_fuku_all,
        'ev_fuku_filtered': ev_fuku_filtered,
        'best_ev_win': best_ev_win,
        'best_ev_fuku': best_ev_fuku,
        'ev_win_label': ev_label(best_ev_win),
        'ev_fuku_label': ev_label(best_ev_fuku),
        'note': f'同条件{n_filtered}走 / 全{n_all}走',
    }


def calc_race_ev_score(horse_evs: list) -> dict:
    """
    レース全体のEVスコアを計算する。

    期待値の高いレースとは:
    - 「実力と人気に乖離がある馬」が複数いるレース
    - 1頭だけでなく、複数頭が正or妙味ありEVを持つレース
    （そういうレースは馬券の組み合わせで効率よく回収できる）
    """
    valid = [h for h in horse_evs if h['best_ev_win'] is not None]
    if not valid:
        return {'race_ev_score': None, 'top_ev_horse': None, 'positive_ev_count': 0}

    sorted_by_ev = sorted(valid, key=lambda x: x['best_ev_win'], reverse=True)
    top = sorted_by_ev[0]

    # 妙味あり馬（EV > -0.10）の数
    positive_ev_count = sum(1 for h in valid if h['best_ev_win'] >= -0.10)

    # レースEVスコア = 上位3頭のEV平均
    top3 = sorted_by_ev[:3]
    race_ev_score = sum(h['best_ev_win'] for h in top3) / len(top3)

    return {
        'race_ev_score': round(race_ev_score, 3),
        'top_ev_horse': top,
        'positive_ev_count': positive_ev_count,
        'sorted_horses': sorted_by_ev,
    }


def format_report(race_data: dict, horse_evs: list, race_score: dict) -> str:
    """人間が読みやすいEVレポートを生成する"""
    lines = []
    lines.append('=' * 60)
    lines.append(f"📊 EV分析: {race_data.get('race_name', '')} [{race_data.get('race_id', '')}]")
    lines.append(f"   距離: {race_data.get('dist', '')}  頭数: {len(horse_evs)}頭")
    lines.append('=' * 60)

    score = race_score.get('race_ev_score')
    pos_count = race_score.get('positive_ev_count', 0)
    lines.append(f"\n🏆 レースEVスコア: {score:+.3f}" if score is not None else "\n🏆 レースEVスコア: データ不足")
    lines.append(f"   妙味あり馬数(EV≥-0.10): {pos_count}頭")

    if score is not None:
        if score >= 0.00:
            lines.append("   → ★★★ 優秀！複数頭に期待値あり。積極的に買える。")
        elif score >= -0.10:
            lines.append("   → ★★  良好。上位人気に妙味あり。")
        elif score >= -0.20:
            lines.append("   → ★   平均的。選択的に買う。")
        else:
            lines.append("   → 割高レース。見送りまたは少額にとどめる。")

    lines.append('\n' + '-' * 60)
    lines.append(f"{'馬番':<4} {'馬名':<14} {'単勝':<6} {'EV(単)':<9} {'EV(複)':<9} {'評価'}")
    lines.append('-' * 60)

    sorted_horses = race_score.get('sorted_horses', horse_evs)
    for h in sorted_horses:
        umaban = h.get('umaban', '?')
        name = h.get('name', '?')[:12]
        odds = f"{h['win_odds']:.1f}" if h.get('win_odds') else '---'
        ev_w = f"{h['best_ev_win']:+.3f}" if h.get('best_ev_win') is not None else '  ---'
        ev_f = f"{h['best_ev_fuku']:+.3f}" if h.get('best_ev_fuku') is not None else '  ---'
        label = h.get('ev_win_label', '')
        n_note = h.get('note', '')
        lines.append(f"  {umaban:<3} {name:<14} {odds:<6} {ev_w:<9} {ev_f:<9} {label}  ({n_note})")

    lines.append('\n' + '=' * 60)
    lines.append("【期待値の見方】")
    lines.append("  EV = 推定勝率 × オッズ - 1")
    lines.append("  EV +0.10以上 → 長期的にプラス収支が期待できる")
    lines.append("  EV  0.00以上 → 理論的にプラス")
    lines.append("  EV -0.10以上 → テイクレート(25%)より良い（妙味あり）")
    lines.append("  EV -0.25未満 → 割高（無作為に賭けるより悪い）")
    lines.append("  ※ 過去成績が少ない馬（3走未満）は推定精度が低い")
    lines.append('=' * 60)

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("使い方: python calc_ev.py <horse_data.json>")
        print("       python calc_ev.py <race1.json> <race2.json> ...  # 複数レース比較")
        sys.exit(1)

    all_race_scores = []

    for filepath in sys.argv[1:]:
        with open(filepath, 'r', encoding='utf-8') as f:
            race_data = json.load(f)

        race_id = race_data.get('race_id', 'unknown')
        target_dist_str = race_data.get('dist', '')
        target_surface, target_dist = parse_dist(target_dist_str)

        horse_evs = []
        for horse in race_data.get('horses', []):
            ev = calc_horse_ev(horse, target_surface, target_dist)
            horse_evs.append(ev)

        race_score = calc_race_ev_score(horse_evs)
        report = format_report(race_data, horse_evs, race_score)

        print(report)
        print()

        # ファイルにも保存
        out_path = filepath.replace('.json', '_ev.txt')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"→ 保存: {out_path}\n")

        all_race_scores.append({
            'race_id': race_id,
            'race_name': race_data.get('race_name', ''),
            'dist': target_dist_str,
            'race_ev_score': race_score.get('race_ev_score'),
            'positive_ev_count': race_score.get('positive_ev_count', 0),
            'top_ev_horse': race_score.get('top_ev_horse', {}).get('name'),
            'top_ev_value': race_score.get('top_ev_horse', {}).get('best_ev_win'),
        })

    # 複数レースを比較するサマリー
    if len(all_race_scores) > 1:
        print('\n' + '=' * 60)
        print("📋 レース比較サマリー（期待値スコア順）")
        print('=' * 60)
        ranked = sorted(all_race_scores, key=lambda x: x['race_ev_score'] or -99, reverse=True)
        for i, r in enumerate(ranked, 1):
            score_str = f"{r['race_ev_score']:+.3f}" if r['race_ev_score'] is not None else '  ---'
            print(f"  {i}位 {r['race_name']:<20} EVスコア:{score_str}  妙味馬:{r['positive_ev_count']}頭  最高EV馬:{r['top_ev_horse']}")
        print('=' * 60)


if __name__ == '__main__':
    main()

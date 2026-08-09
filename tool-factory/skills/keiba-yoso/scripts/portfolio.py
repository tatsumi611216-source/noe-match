#!/usr/bin/env python3
"""
馬券ポートフォリオ構築スクリプト
====================================
使い方:
  python portfolio.py <ev_result.json> --budget 10000 [--mode jra|nar|all]

入力: calc_ev.py の出力JSONに買い目情報を追加したもの
出力: 各買い目の投資額（100円単位）と期待収支

## ポートフォリオ構築の考え方

### 1. 予算配分（レース間）
  レースEVスコアに比例して予算を分配する。
  EVが高いレースに多く張り、低いレースは少額に抑える。

### 2. 買い目配分（レース内）
  ケリー基準（Half-Kelly）で各買い目の最適賭け金を算出する。
  Half-Kelly にすることで破産リスクを低減しながら長期収支を最大化する。

  Kelly formula: f = (b×p - q) / b
  Half-Kelly:    f = kelly / 2

  ここで:
    b = オッズ - 1（純利益倍率）
    p = 推定的中確率
    q = 1 - p（ハズレ確率）

### 3. 最小単位・丸め
  日本の馬券は 100円単位。100円未満は切り捨て。
  最小賭け金: 100円。ケリーがマイナスの買い目は購入しない（期待値マイナス）。

### 4. 予算超過の場合
  全買い目のケリー額合計が予算を超えた場合、比例スケールダウンする。
"""

import json
import sys
import math
from pathlib import Path


def kelly_fraction(win_prob: float, odds: float) -> float:
    """ケリー基準で最適賭け割合を計算（純利益ベース）"""
    if odds <= 1.0 or win_prob <= 0 or win_prob >= 1:
        return 0.0
    b = odds - 1.0   # 純利益倍率
    p = win_prob
    q = 1.0 - p
    f = (b * p - q) / b
    return max(0.0, f)


def half_kelly(win_prob: float, odds: float) -> float:
    """Half-Kelly（破産リスク低減）"""
    return kelly_fraction(win_prob, odds) / 2.0


def allocate_budget_across_races(races: list, total_budget: int) -> dict:
    """
    複数レースへの予算配分。
    EVスコアが正の値のみに比例配分。マイナスEVのレースには0円。
    """
    ev_scores = {}
    for r in races:
        score = r.get('race_ev_score', 0) or 0
        ev_scores[r['race_id']] = max(0.0, score + 0.25)  # ベースライン補正（-0.25がゼロ基準）

    total_ev = sum(ev_scores.values())
    if total_ev == 0:
        return {r['race_id']: total_budget // len(races) for r in races}

    allocations = {}
    remaining = total_budget
    races_sorted = sorted(races, key=lambda r: ev_scores[r['race_id']], reverse=True)

    for i, race in enumerate(races_sorted):
        if i == len(races_sorted) - 1:
            allocations[race['race_id']] = remaining
        else:
            share = int((ev_scores[race['race_id']] / total_ev) * total_budget / 100) * 100
            share = max(500, share)  # 最低500円
            allocations[race['race_id']] = share
            remaining -= share

    return allocations


def build_race_portfolio(race: dict, budget: int) -> list:
    """
    1レースの買い目と投資額を構築する。

    raceには以下が必要:
    {
      "race_id": ...,
      "race_name": ...,
      "bets": [
        {
          "type": "馬連",        # 馬券種別
          "horses": ["4", "7"],  # 馬番リスト
          "names": ["ハーフブルー", "スモークフレイバー"],
          "odds": 5.2,           # 推定オッズ
          "win_prob": 0.25,      # 推定的中確率（EV計算から逆算 or 指定）
          "ev": 0.30,            # 期待値
          "label": "◎-○"        # 印ラベル
        }
      ]
    }
    """
    bets = race.get('bets', [])
    if not bets:
        return []

    results = []
    kelly_amounts = []

    for bet in bets:
        ev = bet.get('ev', -1)
        odds = bet.get('odds', 1)
        win_prob = bet.get('win_prob')

        # win_prob が指定されていなければ odds と ev から逆算
        if win_prob is None and odds > 0:
            win_prob = (ev + 1) / odds if ev is not None else 0

        if win_prob is None or win_prob <= 0:
            kelly_amounts.append(0)
            continue

        frac = half_kelly(win_prob, odds)
        raw_amount = int(frac * budget / 100) * 100  # 100円単位
        kelly_amounts.append(max(0, raw_amount))

    # 合計が予算を超えた場合スケールダウン
    total_kelly = sum(kelly_amounts)
    scale = min(1.0, budget / total_kelly) if total_kelly > 0 else 1.0

    used_budget = 0
    for i, bet in enumerate(bets):
        amount = int(kelly_amounts[i] * scale / 100) * 100
        amount = max(100, amount) if kelly_amounts[i] > 0 else 0  # 最小100円
        if amount == 0 and bet.get('ev', -1) < -0.20:
            continue  # EV -20%以下は購入しない

        ev = bet.get('ev', 0) or 0
        expected_return = amount * bet.get('odds', 1) * bet.get('win_prob', 0)
        expected_profit = expected_return - amount

        results.append({
            **bet,
            'amount': amount,
            'expected_return': round(expected_return),
            'expected_profit': round(expected_profit),
            'kelly_fraction': round(half_kelly(bet.get('win_prob', 0) or 0, bet.get('odds', 1)), 4),
        })
        used_budget += amount

    return results


def format_portfolio_report(races_with_portfolios: list, total_budget: int) -> str:
    """ポートフォリオレポートを人間が読みやすい形式で出力"""
    lines = []
    lines.append('=' * 65)
    lines.append(f'💰 馬券ポートフォリオ  総予算: ¥{total_budget:,}')
    lines.append('=' * 65)

    total_spend = 0
    total_expected_profit = 0

    for race in races_with_portfolios:
        race_budget = race.get('allocated_budget', 0)
        portfolio = race.get('portfolio', [])
        race_spend = sum(p['amount'] for p in portfolio)
        total_spend += race_spend

        lines.append(f"\n📍 {race['race_name']}  配分予算: ¥{race_budget:,}  実使用: ¥{race_spend:,}")
        lines.append(f"   {race.get('venue','')} {race.get('dist','')} {race.get('n_horses','?')}頭  "
                     f"EVスコア: {race.get('race_ev_score', '?')}")
        lines.append(f"   {'馬券種':<8} {'組み合わせ':<20} {'オッズ':<7} {'EV':<8} {'賭け金':>7}  期待収支")
        lines.append('   ' + '-' * 62)

        race_exp_profit = 0
        for p in portfolio:
            horses_str = '-'.join(p.get('horses', []))
            names_str = '×'.join(p.get('names', []))[:16]
            bet_type = p.get('type', '?')[:6]
            odds = p.get('odds', 0)
            ev = p.get('ev', 0) or 0
            amount = p.get('amount', 0)
            exp_profit = p.get('expected_profit', 0)
            race_exp_profit += exp_profit

            ev_mark = '★' if ev >= 0 else ('△' if ev >= -0.1 else '▼')
            lines.append(f"   {bet_type:<8} {names_str:<20} {odds:<7.1f} {ev:+.3f}{ev_mark}  "
                         f"¥{amount:>5,}  {exp_profit:+,}円")

        total_expected_profit += race_exp_profit
        lines.append(f"   {'小計':>50} ¥{race_spend:>5,}  {race_exp_profit:+,}円")

    lines.append('\n' + '=' * 65)
    lines.append(f"{'合計':>55} ¥{total_spend:>5,}")
    lines.append(f"{'期待収支（長期平均）':>48} {total_expected_profit:+,}円")
    lines.append(f"{'未使用予算':>55} ¥{total_budget - total_spend:>5,}")
    lines.append('=' * 65)
    lines.append('\n【注意事項】')
    lines.append('・賭け金はHalf-Kelly基準（EV×安全係数）で算出')
    lines.append('・期待収支は長期的な統計的期待値であり、1回の結果ではありません')
    lines.append('・EVがマイナスの買い目は購入非推奨として除外しています')
    lines.append('・馬券購入は自己責任でお願いします')

    return '\n'.join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='馬券ポートフォリオ構築')
    parser.add_argument('input', help='EVデータJSONファイル（複数可）', nargs='+')
    parser.add_argument('--budget', type=int, default=10000, help='総予算（円）デフォルト: 10000')
    parser.add_argument('--mode', choices=['jra', 'nar', 'all'], default='all')
    args = parser.parse_args()

    # 全レースのEVデータを読み込む
    all_races = []
    for fp in args.input:
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # calc_ev.py の出力JSON形式を想定
        if isinstance(data, list):
            all_races.extend(data)
        else:
            all_races.append(data)

    if not all_races:
        print('レースデータがありません')
        return

    # レース間の予算配分
    budget_alloc = allocate_budget_across_races(all_races, args.budget)

    # 各レースのポートフォリオ構築
    races_with_portfolios = []
    for race in all_races:
        race_budget = budget_alloc.get(race['race_id'], 0)
        portfolio = build_race_portfolio(race, race_budget)
        races_with_portfolios.append({
            **race,
            'allocated_budget': race_budget,
            'portfolio': portfolio,
        })

    # レポート出力
    report = format_portfolio_report(races_with_portfolios, args.budget)
    print(report)

    # JSONも保存
    out_path = f"portfolio_{args.budget}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(races_with_portfolios, f, ensure_ascii=False, indent=2)
    print(f'\n→ JSON保存: {out_path}')


if __name__ == '__main__':
    main()

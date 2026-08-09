#!/usr/bin/env python3
"""
競馬予想HTMLレポート生成スクリプト
====================================
使い方:
  python generate_report.py <portfolio.json> --date 20260406 --output report.html

入力: portfolio.py の出力JSON（ポートフォリオ情報付き）
出力: 見栄えのいいHTMLレポート（挿絵・EV可視化・買い目一覧付き）
"""

import json
import sys
import math
from datetime import datetime
from pathlib import Path


# ========== SVGアセット ==========

HORSE_SILHOUETTE = """
<svg viewBox="0 0 200 120" xmlns="http://www.w3.org/2000/svg" class="horse-svg">
  <!-- 馬のシルエット -->
  <g fill="currentColor" opacity="0.85">
    <!-- 胴体 -->
    <ellipse cx="100" cy="70" rx="45" ry="22"/>
    <!-- 首 -->
    <ellipse cx="138" cy="52" rx="14" ry="20" transform="rotate(-20 138 52)"/>
    <!-- 頭 -->
    <ellipse cx="155" cy="38" rx="12" ry="9" transform="rotate(-10 155 38)"/>
    <!-- 鼻面 -->
    <ellipse cx="166" cy="42" rx="6" ry="5" transform="rotate(10 166 42)"/>
    <!-- 耳 -->
    <polygon points="150,28 154,18 158,28"/>
    <polygon points="156,26 160,16 164,27"/>
    <!-- 前脚 -->
    <rect x="128" y="88" width="7" height="28" rx="3" transform="rotate(-8 128 88)"/>
    <rect x="118" y="89" width="7" height="28" rx="3" transform="rotate(5 118 89)"/>
    <!-- 後脚 -->
    <rect x="72" y="88" width="7" height="26" rx="3" transform="rotate(8 72 88)"/>
    <rect x="62" y="87" width="7" height="26" rx="3" transform="rotate(-3 62 87)"/>
    <!-- 尾 -->
    <path d="M58,68 Q40,55 42,75 Q44,90 52,85" stroke="currentColor" stroke-width="5" fill="none" stroke-linecap="round"/>
    <!-- たてがみ -->
    <path d="M138,38 Q142,30 148,36 Q152,26 158,32 Q162,22 166,30" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round"/>
  </g>
</svg>
"""

TROPHY_SVG = """<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg" width="28" height="28">
  <path d="M8 4h24v10c0 7-4 12-10 14v4h4v4H14v-4h4v-4C12 26 8 21 8 14V4z" fill="#FFD700"/>
  <path d="M4 4h4v8c0 2 2 4 4 5V4H4zM36 4h-4v13c2-1 4-3 4-5V4z" fill="#FFA500"/>
  <rect x="15" y="34" width="10" height="2" fill="#8B7355" rx="1"/>
</svg>"""

FIRE_SVG = """<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="#FF6B35"><path d="M12 2c-4 4-4 8-2 10-1-2 0-4 2-4-2 4 2 8 4 6-1 2-3 4-6 4-3.3 0-6-2.7-6-6 0-4 4-8 8-10z"/></svg>"""


# ========== EV バー生成 ==========

def ev_bar(ev_value):
    """EV値を視覚的なバーで表示"""
    if ev_value is None:
        return '<span class="ev-bar ev-unknown">—</span>'
    pct = min(100, max(0, int((ev_value + 0.3) / 0.6 * 100)))
    cls = 'ev-high' if ev_value >= 0 else ('ev-mid' if ev_value >= -0.1 else 'ev-low')
    sign = '+' if ev_value >= 0 else ''
    return f'<div class="ev-container"><div class="ev-bar {cls}" style="width:{pct}%"></div><span class="ev-text">{sign}{ev_value:.3f}</span></div>'


def mark_badge(mark):
    """印バッジのHTML"""
    marks = {
        '◎': ('honmei', '本'),
        '○': ('taikou', '対'),
        '▲': ('tanaana', '穴'),
        '△': ('renge', '連'),
        '☆': ('ana', '☆'),
        '×': ('kiken', '×'),
    }
    info = marks.get(mark, ('other', mark))
    return f'<span class="mark-badge mark-{info[0]}">{mark}</span>'


def ev_star(ev):
    """EV評価スター"""
    if ev is None: return '—'
    if ev >= 0.10: return '★★★'
    if ev >= 0.00: return '★★'
    if ev >= -0.10: return '★'
    return ''


# ========== レースカード生成 ==========

def render_race_card(race: dict, rank: int) -> str:
    race_name = race.get('race_name', '不明')
    venue = race.get('venue', '')
    dist = race.get('dist', '')
    n_horses = race.get('n_horses', '?')
    ev_score = race.get('race_ev_score')
    portfolio = race.get('portfolio', [])
    horses_ev = race.get('horses_ev', [])
    allocated = race.get('allocated_budget', 0)

    ev_score_str = f'{ev_score:+.3f}' if ev_score is not None else '—'
    rank_label = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'][rank] if rank < 5 else f'{rank+1}'

    # 枠順テーブル
    horse_rows = ''
    sorted_horses = sorted(horses_ev, key=lambda h: h.get('best_ev_win') or -99, reverse=True)
    for h in sorted_horses:
        ev_w = h.get('best_ev_win')
        ev_f = h.get('best_ev_fuku')
        odds = h.get('win_odds', '—')
        n_races = h.get('n_all', 0)
        n_filt = h.get('n_filtered', 0)
        win_rate = h.get('win_rate_filtered') or h.get('win_rate_all')
        place_rate = h.get('place_rate_filtered') or h.get('place_rate_all')
        win_r_str = f'{win_rate:.0%}' if win_rate is not None else '—'
        place_r_str = f'{place_rate:.0%}' if place_rate is not None else '—'
        star = ev_star(ev_w)
        row_class = 'ev-positive-row' if (ev_w or -1) >= 0 else ''
        horse_rows += f"""
        <tr class="{row_class}">
          <td class="umaban">⑧{h.get('umaban','?')}</td>
          <td class="horse-name">{h.get('name','?')}<small class="n-races">({n_filt}/{n_races}走)</small></td>
          <td class="odds-cell">{odds}倍</td>
          <td class="winrate">{win_r_str}</td>
          <td class="placerate">{place_r_str}</td>
          <td class="ev-cell">{ev_bar(ev_w)}</td>
          <td class="ev-fuku">{ev_bar(ev_f)}</td>
          <td class="star-cell">{star}</td>
        </tr>"""

    # 買い目テーブル
    bet_rows = ''
    total_amount = 0
    for bet in portfolio:
        if bet.get('amount', 0) == 0:
            continue
        bet_type = bet.get('type', '?')
        horses = '-'.join(bet.get('horses', []))
        names = '×'.join(bet.get('names', []))
        odds_b = bet.get('odds', 0)
        ev_b = bet.get('ev', 0) or 0
        amount = bet.get('amount', 0)
        exp_p = bet.get('expected_profit', 0)
        total_amount += amount
        ev_cls = 'positive' if ev_b >= 0 else ('mid' if ev_b >= -0.1 else 'low')
        exp_cls = 'profit' if exp_p >= 0 else 'loss'
        bet_rows += f"""
        <tr>
          <td><span class="bet-type">{bet_type}</span></td>
          <td class="bet-horses">{horses}</td>
          <td class="bet-names">{names}</td>
          <td>{odds_b:.1f}倍</td>
          <td class="ev-{ev_cls}">{ev_b:+.3f}</td>
          <td class="amount">¥{amount:,}</td>
          <td class="{exp_cls}">{exp_p:+,}円</td>
        </tr>"""

    return f"""
    <div class="race-card" id="race-{rank+1}">
      <div class="race-header">
        <div class="race-rank">{rank_label}</div>
        <div class="race-title-block">
          <h2 class="race-name">{race_name}</h2>
          <div class="race-meta">
            <span class="badge venue-badge">{venue}</span>
            <span class="badge dist-badge">{dist}</span>
            <span class="badge horses-badge">{n_horses}頭</span>
          </div>
        </div>
        <div class="race-ev-score">
          <div class="ev-score-label">EVスコア</div>
          <div class="ev-score-value {'positive' if (ev_score or -1) >= 0 else ''}">{ev_score_str}</div>
        </div>
        <div class="horse-decoration">{HORSE_SILHOUETTE}</div>
      </div>

      <div class="race-body">
        <!-- 印・結論 -->
        <div class="picks-section">
          <h3>📊 EV分析・印</h3>
          <div class="picks-grid">
            {render_picks(race)}
          </div>
        </div>

        <!-- 馬別EV表 -->
        <div class="ev-table-section">
          <h3>🐎 各馬EV一覧</h3>
          <div class="table-wrapper">
            <table class="ev-table">
              <thead>
                <tr>
                  <th>馬番</th><th>馬名</th><th>単勝</th><th>勝率</th><th>複勝率</th>
                  <th>EV(単)</th><th>EV(複)</th><th>評価</th>
                </tr>
              </thead>
              <tbody>{horse_rows}</tbody>
            </table>
          </div>
        </div>

        <!-- 馬券・ポートフォリオ -->
        <div class="portfolio-section">
          <h3>💰 買い目 &amp; ポートフォリオ
            <span class="budget-tag">配分: ¥{allocated:,} → 使用: ¥{total_amount:,}</span>
          </h3>
          <div class="table-wrapper">
            <table class="bet-table">
              <thead>
                <tr><th>券種</th><th>組番</th><th>馬名</th><th>推定オッズ</th><th>EV</th><th>賭け金</th><th>期待収支</th></tr>
              </thead>
              <tbody>{bet_rows if bet_rows else '<tr><td colspan="7" class="no-data">買い目データなし（EV計算後に設定）</td></tr>'}</tbody>
            </table>
          </div>
        </div>
      </div>
    </div>"""


def render_picks(race: dict) -> str:
    """印セクションのHTML"""
    picks = race.get('picks', {})
    if not picks:
        return '<p class="no-picks">予想データを計算後に表示されます</p>'

    items = [
        ('◎', 'honmei', picks.get('honmei')),
        ('○', 'taikou', picks.get('taikou')),
        ('▲', 'tanaana', picks.get('tanaana')),
        ('△', 'renge', picks.get('renge')),
        ('☆', 'ana', picks.get('ana')),
    ]
    html = ''
    for mark, cls, horse in items:
        if horse:
            ev = horse.get('best_ev_win')
            ev_str = f'EV {ev:+.3f}' if ev is not None else ''
            html += f"""
            <div class="pick-item pick-{cls}">
              <span class="pick-mark">{mark}</span>
              <div class="pick-horse">
                <span class="pick-num">⑧{horse.get('umaban','?')}</span>
                <span class="pick-name">{horse.get('name','?')}</span>
                <span class="pick-odds">{horse.get('win_odds','—')}倍</span>
                <span class="pick-ev">{ev_str}</span>
              </div>
            </div>"""
    danger = picks.get('kiken')
    if danger:
        html += f"""
        <div class="pick-item pick-danger">
          <span class="pick-mark danger">⚠</span>
          <div class="pick-horse">
            <span class="pick-num">⑧{danger.get('umaban','?')}</span>
            <span class="pick-name">{danger.get('name','?')}</span>
            <small>危険な人気馬</small>
          </div>
        </div>"""
    return html


# ========== メインHTML ==========

def generate_html(races_data: list, total_budget: int, date_str: str) -> str:
    race_cards = '\n'.join(render_race_card(r, i) for i, r in enumerate(races_data))
    total_spend = sum(sum(b.get('amount', 0) for b in r.get('portfolio', [])) for r in races_data)
    total_exp = sum(sum(b.get('expected_profit', 0) for b in r.get('portfolio', [])) for r in races_data)
    n_races = len(races_data)

    # サマリー行
    summary_rows = ''
    for i, r in enumerate(races_data):
        spend = sum(b.get('amount', 0) for b in r.get('portfolio', []))
        ev = r.get('race_ev_score')
        ev_str = f'{ev:+.3f}' if ev is not None else '—'
        pos_horses = r.get('positive_ev_count', 0)
        top_horse = r.get('top_ev_horse', {})
        summary_rows += f"""
        <tr onclick="document.getElementById('race-{i+1}').scrollIntoView({{behavior:'smooth'}})">
          <td>{'🥇🥈🥉4️⃣5️⃣'[i] if i < 5 else str(i+1)}</td>
          <td class="race-link">{r.get('race_name','?')}</td>
          <td>{r.get('venue','')}</td>
          <td>{r.get('dist','')}</td>
          <td class="{'pos' if (ev or -1) >= 0 else ''}">{ev_str}</td>
          <td>{pos_horses}頭</td>
          <td>{top_horse.get('name','—')}</td>
          <td>¥{spend:,}</td>
        </tr>"""

    now_str = datetime.now().strftime('%Y/%m/%d %H:%M')

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>競馬予想レポート {date_str}</title>
<style>
/* ============================================================
   KEIBA YOSO REPORT  -  Racing Dark Theme
   ============================================================ */
:root {{
  --bg: #0d1117;
  --bg2: #161b22;
  --bg3: #1c2333;
  --border: #30363d;
  --gold: #d4af37;
  --gold2: #f0c040;
  --text: #e6edf3;
  --muted: #8b949e;
  --green: #3fb950;
  --red: #f85149;
  --orange: #d29922;
  --blue: #58a6ff;
  --purple: #bc8cff;
  --honmei: #ff4444;
  --taikou: #4488ff;
  --tanaana: #ff9922;
  --renge: #44cc88;
  --ana: #cc88ff;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  background: var(--bg);
  color: var(--text);
  font-family: 'Segoe UI', 'Hiragino Sans', 'Noto Sans JP', sans-serif;
  font-size: 14px;
  line-height: 1.6;
}}

/* ---- ヘッダー ---- */
.site-header {{
  background: linear-gradient(135deg, #0d1117 0%, #1a1f2e 50%, #0d1117 100%);
  border-bottom: 2px solid var(--gold);
  padding: 20px 32px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: sticky;
  top: 0;
  z-index: 100;
}}

.header-logo {{
  display: flex;
  align-items: center;
  gap: 10px;
}}

.logo-icon {{ font-size: 32px; }}

.logo-text {{
  font-size: 22px;
  font-weight: 800;
  background: linear-gradient(90deg, var(--gold), var(--gold2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: 2px;
}}

.header-meta {{
  margin-left: auto;
  text-align: right;
  color: var(--muted);
  font-size: 12px;
}}

.header-date {{
  font-size: 18px;
  color: var(--text);
  font-weight: 600;
}}

/* ---- ナビ ---- */
.race-nav {{
  background: var(--bg2);
  border-bottom: 1px solid var(--border);
  padding: 8px 32px;
  display: flex;
  gap: 8px;
  overflow-x: auto;
}}

.nav-item {{
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 4px 14px;
  cursor: pointer;
  white-space: nowrap;
  font-size: 12px;
  color: var(--muted);
  transition: all 0.2s;
}}

.nav-item:hover {{ border-color: var(--gold); color: var(--gold); }}

/* ---- サマリー ---- */
.summary-section {{
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  margin: 24px 32px;
  overflow: hidden;
}}

.summary-title {{
  background: linear-gradient(90deg, var(--bg3), var(--bg2));
  padding: 14px 20px;
  font-size: 16px;
  font-weight: 700;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 8px;
}}

.budget-pills {{
  display: flex;
  gap: 10px;
  padding: 12px 20px;
  flex-wrap: wrap;
}}

.budget-pill {{
  background: var(--bg3);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 16px;
  text-align: center;
}}

.pill-label {{ font-size: 11px; color: var(--muted); }}
.pill-value {{ font-size: 20px; font-weight: 700; color: var(--gold); }}

.summary-table {{ width: 100%; border-collapse: collapse; }}
.summary-table th, .summary-table td {{
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  text-align: left;
}}
.summary-table th {{ background: var(--bg3); color: var(--muted); font-size: 12px; font-weight: 600; }}
.summary-table tr:hover td {{ background: rgba(212,175,55,0.05); cursor: pointer; }}
.summary-table .race-link {{ color: var(--gold2); font-weight: 600; }}
.summary-table .pos {{ color: var(--green); font-weight: 700; }}

/* ---- レースカード ---- */
.race-card {{
  background: var(--bg2);
  border: 1px solid var(--border);
  border-radius: 12px;
  margin: 20px 32px;
  overflow: hidden;
  transition: border-color 0.2s;
}}

.race-card:hover {{ border-color: var(--gold); }}

.race-header {{
  background: linear-gradient(135deg, var(--bg3) 0%, #1e2433 60%, #12192a 100%);
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-bottom: 1px solid var(--border);
  position: relative;
  overflow: hidden;
}}

.race-rank {{ font-size: 28px; }}

.race-title-block {{ flex: 1; }}

.race-name {{
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(90deg, var(--gold), var(--gold2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 6px;
}}

.race-meta {{ display: flex; gap: 6px; flex-wrap: wrap; }}

.badge {{
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}}

.venue-badge {{ background: rgba(88,166,255,0.15); border: 1px solid rgba(88,166,255,0.4); color: var(--blue); }}
.dist-badge {{ background: rgba(63,185,80,0.15); border: 1px solid rgba(63,185,80,0.4); color: var(--green); }}
.horses-badge {{ background: rgba(188,140,255,0.15); border: 1px solid rgba(188,140,255,0.4); color: var(--purple); }}

.race-ev-score {{
  text-align: center;
  background: rgba(0,0,0,0.3);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 16px;
  min-width: 100px;
}}

.ev-score-label {{ font-size: 10px; color: var(--muted); margin-bottom: 4px; }}
.ev-score-value {{ font-size: 22px; font-weight: 800; color: var(--muted); }}
.ev-score-value.positive {{ color: var(--green); }}

.horse-decoration {{
  position: absolute;
  right: -10px;
  top: -10px;
  width: 120px;
  opacity: 0.06;
  color: var(--gold);
}}

.race-body {{ padding: 20px 24px; }}

/* ---- セクション共通 ---- */
.race-body h3 {{
  font-size: 13px;
  font-weight: 700;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0 0 12px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}}

.picks-section, .ev-table-section, .portfolio-section {{
  margin-bottom: 24px;
}}

/* ---- 印 ---- */
.picks-grid {{ display: flex; gap: 10px; flex-wrap: wrap; }}

.pick-item {{
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg3);
  border-radius: 8px;
  padding: 8px 12px;
  border-left: 3px solid var(--border);
}}

.pick-honmei {{ border-left-color: var(--honmei); }}
.pick-taikou {{ border-left-color: var(--taikou); }}
.pick-tanaana {{ border-left-color: var(--tanaana); }}
.pick-renge {{ border-left-color: var(--renge); }}
.pick-ana {{ border-left-color: var(--ana); }}
.pick-danger {{ border-left-color: var(--red); background: rgba(248,81,73,0.08); }}

.pick-mark {{
  font-size: 20px;
  font-weight: 900;
  min-width: 24px;
  text-align: center;
}}

.pick-honmei .pick-mark {{ color: var(--honmei); }}
.pick-taikou .pick-mark {{ color: var(--taikou); }}
.pick-tanaana .pick-mark {{ color: var(--tanaana); }}
.pick-renge .pick-mark {{ color: var(--renge); }}
.pick-ana .pick-mark {{ color: var(--ana); }}
.pick-mark.danger {{ color: var(--red); font-size: 16px; }}

.pick-horse {{ display: flex; flex-direction: column; gap: 1px; }}
.pick-num {{ font-size: 11px; color: var(--muted); }}
.pick-name {{ font-size: 15px; font-weight: 700; }}
.pick-odds {{ font-size: 11px; color: var(--orange); }}
.pick-ev {{ font-size: 11px; color: var(--green); }}

/* ---- EV表 ---- */
.table-wrapper {{ overflow-x: auto; }}

.ev-table, .bet-table {{ width: 100%; border-collapse: collapse; }}
.ev-table th, .ev-table td,
.bet-table th, .bet-table td {{
  padding: 8px 10px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  white-space: nowrap;
}}
.ev-table th, .bet-table th {{ background: var(--bg3); font-size: 11px; color: var(--muted); font-weight: 600; }}
.ev-table tr:hover td, .bet-table tr:hover td {{ background: rgba(255,255,255,0.02); }}
.ev-positive-row td {{ background: rgba(63,185,80,0.04); }}

.umaban {{ color: var(--muted); font-size: 12px; width: 36px; }}
.horse-name {{ font-weight: 600; }}
.n-races {{ color: var(--muted); font-size: 11px; margin-left: 4px; }}
.odds-cell {{ color: var(--orange); font-weight: 600; }}
.winrate, .placerate {{ font-size: 12px; }}
.star-cell {{ color: var(--gold); letter-spacing: -1px; }}

/* ---- EV バー ---- */
.ev-container {{ display: flex; align-items: center; gap: 6px; min-width: 90px; }}
.ev-bar {{
  height: 6px;
  border-radius: 3px;
  min-width: 4px;
  transition: width 0.3s;
}}
.ev-high {{ background: linear-gradient(90deg, #3fb950, #58e06a); }}
.ev-mid {{ background: linear-gradient(90deg, #d29922, #e8b84d); }}
.ev-low {{ background: linear-gradient(90deg, #8b949e, #aab4be); }}
.ev-unknown {{ color: var(--muted); }}
.ev-text {{ font-size: 11px; font-weight: 600; white-space: nowrap; color: var(--text); }}

/* ---- 買い目表 ---- */
.bet-type {{
  background: rgba(88,166,255,0.15);
  border: 1px solid rgba(88,166,255,0.3);
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 11px;
  color: var(--blue);
}}
.bet-horses {{ font-weight: 700; color: var(--gold2); }}
.bet-names {{ color: var(--muted); font-size: 12px; }}
.amount {{ font-weight: 700; color: var(--text); }}
.ev-positive {{ color: var(--green); font-weight: 700; }}
.ev-mid {{ color: var(--orange); }}
.ev-low {{ color: var(--muted); }}
.profit {{ color: var(--green); }}
.loss {{ color: var(--red); }}
.no-data {{ text-align: center; color: var(--muted); padding: 16px; }}

.portfolio-section h3 {{ display: flex; align-items: center; gap: 10px; }}
.budget-tag {{
  background: rgba(212,175,55,0.15);
  border: 1px solid rgba(212,175,55,0.3);
  border-radius: 12px;
  padding: 2px 10px;
  font-size: 11px;
  color: var(--gold);
  font-weight: normal;
  text-transform: none;
  letter-spacing: 0;
}}

/* ---- フッター ---- */
.site-footer {{
  text-align: center;
  padding: 32px;
  color: var(--muted);
  font-size: 12px;
  border-top: 1px solid var(--border);
  margin-top: 20px;
}}

/* ---- レスポンシブ ---- */
@media (max-width: 600px) {{
  .site-header, .race-card, .summary-section {{ margin: 8px; padding: 12px; }}
  .race-header {{ flex-wrap: wrap; }}
  .horse-decoration {{ display: none; }}
}}
</style>
</head>
<body>

<!-- ヘッダー -->
<header class="site-header">
  <div class="header-logo">
    <span class="logo-icon">🐎</span>
    <span class="logo-text">KEIBA YOSO AI</span>
  </div>
  <div class="header-meta">
    <div class="header-date">{date_str}</div>
    <div>生成: {now_str} | EV期待値ベース予想</div>
  </div>
</header>

<!-- ナビ -->
<nav class="race-nav">
  {''.join(f'<div class="nav-item" onclick="document.getElementById(\'race-{i+1}\').scrollIntoView({{behavior:\'smooth\'}})">{i+1}. {r.get("race_name","?")[:12]}</div>' for i, r in enumerate(races_data))}
</nav>

<!-- サマリー -->
<section class="summary-section">
  <div class="summary-title">
    {TROPHY_SVG} 本日の予想サマリー — {n_races}レース選定
  </div>
  <div class="budget-pills">
    <div class="budget-pill">
      <div class="pill-label">総予算</div>
      <div class="pill-value">¥{total_budget:,}</div>
    </div>
    <div class="budget-pill">
      <div class="pill-label">使用額</div>
      <div class="pill-value">¥{total_spend:,}</div>
    </div>
    <div class="budget-pill">
      <div class="pill-label">未使用</div>
      <div class="pill-value">¥{total_budget - total_spend:,}</div>
    </div>
    <div class="budget-pill">
      <div class="pill-label">期待収支</div>
      <div class="pill-value" style="color:{'var(--green)' if total_exp >= 0 else 'var(--red)'}">
        {total_exp:+,}円
      </div>
    </div>
  </div>
  <table class="summary-table">
    <thead>
      <tr><th>順位</th><th>レース名</th><th>競馬場</th><th>距離</th><th>EVスコア</th><th>妙味馬数</th><th>最高EV馬</th><th>配分額</th></tr>
    </thead>
    <tbody>{summary_rows}</tbody>
  </table>
</section>

<!-- レースカード -->
{race_cards}

<!-- フッター -->
<footer class="site-footer">
  <p>🤖 KEIBA YOSO AI — EV期待値ベース競馬予想システム</p>
  <p style="margin-top:8px">※ 本レポートは参考情報です。馬券購入は自己責任でお願いします。のめり込まない程度に楽しみましょう。</p>
</footer>

</body>
</html>"""


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='ポートフォリオJSON')
    parser.add_argument('--date', default=datetime.now().strftime('%Y年%m月%d日'))
    parser.add_argument('--budget', type=int, default=10000)
    parser.add_argument('--output', default='keiba_report.html')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    html = generate_html(data, args.budget, args.date)

    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'✅ HTMLレポート生成完了: {args.output}')


if __name__ == '__main__':
    main()

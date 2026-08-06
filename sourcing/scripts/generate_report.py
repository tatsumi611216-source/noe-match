#!/usr/bin/env python3
"""営業リストのHTMLレポートを生成する（ダークテーマ）。

- カテゴリ別サマリー（現在有効な求人数・企業数）
- 成長スタートアップ営業リスト（直近調達×採用強化を上位に）
- 上場企業営業リスト（採用の困り度スコア順）
usage: python3 generate_report.py [--db ../data/sourcing.db] [--out ../outputs/report.html]
"""
import argparse
import html
from datetime import date
from pathlib import Path

from common import DEFAULT_DB, connect

BASE_DIR = Path(__file__).resolve().parent.parent


def _rows(conn, sql, params=()):
    cur = conn.execute(sql, params)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _esc(v):
    return html.escape(str(v)) if v is not None else "-"


def _target_table(rows, cols):
    if not rows:
        return '<p class="empty">該当なし</p>'
    head = "".join(f"<th>{html.escape(label)}</th>" for _, label in cols)
    body = ""
    for r in rows:
        tds = ""
        for key, _ in cols:
            v = r.get(key)
            if key == "priority_score" and v is not None:
                bar = min(100, float(v))
                tds += (f'<td><span class="score"><span class="bar" style="width:{bar}%"></span>'
                        f'<span class="num">{v:.0f}</span></span></td>')
            else:
                tds += f"<td>{_esc(v)}</td>"
        body += f"<tr>{tds}</tr>"
    return f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def build_html(conn, today: str) -> str:
    cat = _rows(conn, "SELECT category, active_jobs, companies FROM v_category_summary")
    startups = _rows(conn, """SELECT name, funding_stage, employee_count, last_funding_date,
                                     priority_score, active_jobs, categories, prefecture, website
                              FROM v_startup_targets LIMIT 50""")
    listed = _rows(conn, """SELECT name, ticker, listing_market, priority_score, active_jobs,
                                   categories, employee_count, prefecture, website
                            FROM v_listed_targets LIMIT 50""")
    tot_companies = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    tot_active = conn.execute("SELECT COUNT(*) FROM job_postings WHERE is_active=1").fetchone()[0]

    max_cat = max((c["active_jobs"] for c in cat), default=0) or 1
    cat_bars = "".join(
        f'<div class="catrow"><span class="catname">{_esc(c["category"])}</span>'
        f'<span class="catbar"><span style="width:{100*c["active_jobs"]//max_cat}%"></span></span>'
        f'<span class="catval">{c["active_jobs"]}件 / {c["companies"]}社</span></div>'
        for c in cat
    )

    startup_cols = [("name", "企業"), ("funding_stage", "調達"), ("last_funding_date", "調達日"),
                    ("employee_count", "従業員"), ("priority_score", "困り度"),
                    ("active_jobs", "求人"), ("categories", "職種"), ("prefecture", "地域")]
    listed_cols = [("name", "企業"), ("ticker", "証券コード"), ("listing_market", "市場"),
                   ("priority_score", "困り度"), ("active_jobs", "求人"), ("categories", "職種"),
                   ("employee_count", "従業員"), ("prefecture", "地域")]

    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>採用HR営業リスト {today}</title>
<style>
:root{{color-scheme:dark}}
body{{background:#0f1420;color:#e6e9ef;font-family:system-ui,'Hiragino Kaku Gothic ProN',sans-serif;margin:0;padding:24px;line-height:1.5}}
h1{{font-size:20px;margin:0 0 4px}} h2{{font-size:16px;margin:28px 0 10px;color:#9fb3ff}}
.sub{{color:#8892a6;font-size:13px;margin-bottom:16px}}
.kpis{{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}}
.kpi{{background:#1a2233;border:1px solid #263049;border-radius:10px;padding:12px 18px}}
.kpi b{{display:block;font-size:24px;color:#fff}} .kpi span{{font-size:12px;color:#8892a6}}
.catrow{{display:flex;align-items:center;gap:10px;margin:4px 0;font-size:13px}}
.catname{{width:130px;flex:none}} .catval{{width:110px;flex:none;color:#8892a6;text-align:right}}
.catbar{{flex:1;background:#1a2233;border-radius:4px;height:14px;overflow:hidden}}
.catbar span{{display:block;height:100%;background:linear-gradient(90deg,#4d7cff,#7aa2ff)}}
.wrap{{overflow-x:auto}}
table{{border-collapse:collapse;width:100%;font-size:13px;margin-top:6px}}
th,td{{text-align:left;padding:7px 10px;border-bottom:1px solid #222c40;white-space:nowrap}}
th{{color:#8892a6;font-weight:600;position:sticky;top:0;background:#0f1420}}
tr:hover td{{background:#161d2e}}
.score{{display:inline-flex;align-items:center;gap:6px;min-width:90px}}
.score .bar{{height:8px;background:linear-gradient(90deg,#ff7a4d,#ffb84d);border-radius:4px;display:inline-block;min-width:2px}}
.score .num{{color:#ffb84d;font-variant-numeric:tabular-nums}}
.empty{{color:#8892a6;font-size:13px}}
.note{{color:#8892a6;font-size:12px;margin-top:24px;border-top:1px solid #222c40;padding-top:12px}}
</style></head><body>
<h1>採用・HR営業リスト</h1>
<div class="sub">生成日 {today} ／ 「困り度」= 求人件数・掲載日数・新規・職種数から算出した営業優先度</div>
<div class="kpis">
  <div class="kpi"><b>{tot_companies}</b><span>登録企業</span></div>
  <div class="kpi"><b>{tot_active}</b><span>有効求人</span></div>
  <div class="kpi"><b>{len(startups)}</b><span>スタートアップ対象</span></div>
  <div class="kpi"><b>{len(listed)}</b><span>上場企業対象</span></div>
</div>
<h2>カテゴリ別サマリー</h2>{cat_bars or '<p class="empty">データなし</p>'}
<h2>🚀 成長スタートアップ 営業リスト（調達済み・採用強化を優先）</h2>
<div class="wrap">{_target_table(startups, startup_cols)}</div>
<h2>🏢 上場企業 営業リスト（採用の困り度順）</h2>
<div class="wrap">{_target_table(listed, listed_cols)}</div>
<p class="note">収集元は規約クリーンなソース（自社採用ページのJobPosting構造化データ／公開スタートアップリスト／資金調達リリース）に限定。大手有料媒体・会員限定データは対象外。</p>
</body></html>"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--out", default=str(BASE_DIR / "outputs" / "report.html"))
    parser.add_argument("--today", default=str(date.today()))
    args = parser.parse_args()
    conn = connect(args.db)
    try:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build_html(conn, args.today), encoding="utf-8")
        print(f"レポート生成: {out}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

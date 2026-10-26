# -*- coding: utf-8 -*-
"""収益PDCAレポート自動生成（2026-08-26 新設）

毎週、収益ファネルを機械で測って agent/revenue_pdca.md に書き出す。
判定と提案までを自動化し、適用（CTAの差し替え等）はCEO承認後に行う
（noe-metrics C31 と同じ「提案まで」の原則）。

ファネル: セッション → aff_click（8/26に全261ページへ計測注入） → A8成果（手動: asp_results.md）
          セッション → line_add_click → LINE友だち数（noematch_line・日次）

データ源:
- noe-metrics/metrics.db … noematchブランドの ga4_* / line（C30で毎朝6:45自動収集）
- agent/gsc_data.json    … 週次GSC（fetch-gsc.yml）
- agent/asp_results.md   … A8実測（月1・手動）の last_updated 監視

実行: python scripts/revenue_pdca.py
定期: 毎週月曜 7:20（定期タスク【アフィリ】収益PDCA週次）
"""
import io
import json
import os
import re
import sqlite3
import sys
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = r"C:\Users\tatsu\noe-metrics\metrics.db"
OUT = os.path.join(ROOT, "agent", "revenue_pdca.md")

DEADLINES = [
    ("2026-09-08", "A8実測の30日ルール期限（過ぎると新規CTA設置が自動停止）"),
    ("2026-09-21", "ツール9本の語寄せ判定（agent/pdca/cycle_20260824.json）"),
    ("2026-09-23", "11〜30位帯の押し上げ判定（agent/pdca/cycle_20260826.json）"),
    # データバンクの鮮度期限（agent/data_bank.md）。確認日を明記する型なので、
    # 元データが古いまま置くとその確認日が嘘になる。期限が来たら再取得する。
    ("2026-09-29", "令和7年国勢調査 基本集計の公表。生涯未婚率が5年ぶりに更新される"
                   "→ scripts/data/kon_rikon_tomobataraki.json と該当記事の再生成"),
    ("2026-09-30", "令和7年 人口動態統計の確定数の公表（現在の離婚率・婚姻率は概数）"),
    ("2026-12-01", "人口動態の諸率が令和7年国勢調査人口で再計算される（数値が変わりうる）"),
]


def q(conn, metric, days):
    """直近days日の合計（noematchブランド）"""
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    row = conn.execute(
        "select coalesce(sum(value),0) from metrics "
        "where brand='noematch' and metric=? and date>=?", (metric, since)).fetchone()
    return int(row[0])


def latest(conn, metric, channel):
    row = conn.execute(
        "select value, date from metrics where brand='noematch' and metric=? "
        "and channel=? order by date desc limit 1", (metric, channel)).fetchone()
    return (int(row[0]), row[1]) if row else (0, "-")


def sources(conn, days):
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    return conn.execute(
        "select dims, sum(value) from metrics "
        "where brand='noematch' and metric='ga4_sessions_by_source' and date>=? "
        "group by dims order by 2 desc", (since,)).fetchall()


def main():
    conn = sqlite3.connect(DB)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    s7, s28 = q(conn, "ga4_sessions", 7), q(conn, "ga4_sessions", 28)
    aff7, aff28 = q(conn, "ga4_aff_click", 7), q(conn, "ga4_aff_click", 28)
    line7, line28 = q(conn, "ga4_line_add_click", 7), q(conn, "ga4_line_add_click", 28)
    tool7 = q(conn, "ga4_tool_result", 7)
    followers, fdate = latest(conn, "followers", "line")

    src = sources(conn, 7)
    total_src = sum(v for _, v in src) or 1
    non_google = sum(v for d, v in src if d not in ("google", "(direct)", "", "(not set)"))

    # A8実測の鮮度
    asp = io.open(os.path.join(ROOT, "agent", "asp_results.md"), encoding="utf-8").read()
    m = re.search(r"last_updated:\s*([0-9-]+)", asp)
    asp_date = m.group(1) if m else "不明"
    asp_age = (datetime.now() - datetime.strptime(asp_date, "%Y-%m-%d")).days if m else 999

    # 機械提案（ルールベース。適用はCEO承認後）
    props = []
    if s7 and aff7 == 0:
        props.append("直近7日で aff_click が0件。セッションはあるのにCTAが踏まれていない。"
                     "計測注入直後（8/26）なら数日待つ。1週間続くなら、入口上位ページのCTA位置"
                     "（記事末尾→本文中段）を1本だけ動かしてABに使う。")
    if s7 and line7 == 0:
        props.append("直近7日で line_add_click が0件。18記事＋全ツールに導線はあるので、"
                     "次の疑い先は文言（『受け取る』の価値提示）。1本だけ具体的な特典文言"
                     "（例: 46自治体の一覧PDF）に替えて差を見る。")
    if aff7 > 0:
        props.append(f"aff_click {aff7}件/7日。A8管理画面の発生と突合し、クリックはあるのに"
                     "発生0が続く案件は訴求文と読者層のミスマッチを疑う（台帳ルール）。")
    if line7 > 0 and followers <= 1:
        props.append("line_add_click は発火しているのに友だち数が増えていない。"
                     "リンク先（lin.ee）の遷移とあいさつメッセージを確認する。")
    if asp_age > 23:
        props.append(f"A8実測が {asp_age}日前（{asp_date}）。9/8の30日ルールが近い。"
                     "A8『新レポートβ→日別』でクリック・発生・確定を取り asp_results.md を更新する。")
    if not props:
        props.append("警告なし。ファネル数値の推移のみ確認。")

    lines = [
        "# 収益PDCA週次レポート（自動生成: scripts/revenue_pdca.py）",
        "",
        f"生成: {now} ／ データ源: noe-metrics/metrics.db（C30日次収集）",
        "",
        "## ファネル実測",
        "",
        "| 指標 | 直近7日 | 直近28日 |",
        "|---|---|---|",
        f"| セッション（GA4） | {s7} | {s28} |",
        f"| aff_click（アフィリCTAクリック） | {aff7} | {aff28} |",
        f"| line_add_click | {line7} | {line28} |",
        f"| tool_result（ツール実行） | {tool7} | - |",
        f"| LINE友だち数（最新 {fdate}） | {followers} | - |",
        f"| A8成果（手動実測 {asp_date}） | asp_results.md 参照 | - |",
        "",
        f"非Google流入比率（7日）: {non_google}/{total_src} = {non_google/total_src*100:.0f}%",
        "",
        "### 参照元（直近7日）",
        "",
        "| source | sessions |",
        "|---|---|",
    ]
    for d, v in src[:10]:
        lines.append(f"| {d or '(none)'} | {int(v)} |")
    lines += [
        "",
        "## 機械提案（適用はCEO承認後）",
        "",
    ]
    for p in props:
        lines.append(f"- {p}")
    lines += ["", "## 期限", ""]
    today = datetime.now().strftime("%Y-%m-%d")
    for d, label in DEADLINES:
        left = (datetime.strptime(d, "%Y-%m-%d") - datetime.now()).days
        if left >= -3:
            flag = "⚠️ " if left <= 5 else ""
            lines.append(f"- {flag}{d}（あと{left}日）: {label}")
    lines += [
        "",
        "## 注記",
        "",
        "- aff_click の計測開始は 2026-08-26（それ以前は0が正常）",
        "- GA4は 2026-08-26 に内部トラフィック除外を有効化。比較の起点は 8/26",
        "- 適用（CTA差し替え・文言変更）は必ず1変数ずつ。同時に2つ動かすと判定できない",
    ]
    io.open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("書き出し:", OUT)
    print(f"セッション7日 {s7} / aff_click {aff7} / line_add {line7} / 友だち {followers}")
    for p in props[:3]:
        print(" -", p[:70])


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

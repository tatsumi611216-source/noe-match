#!/usr/bin/env python3
"""
Phase 移行判断スクリプト (phase_check.py)
==========================================
Notion の「競馬予想ログ」DB からデータを取得し、
累積回収率と 95% 信頼区間を計算して Phase 移行の判断を出力する。

使い方:
  python3 scripts/phase_check.py                  # 全データで集計
  python3 scripts/phase_check.py --phase Phase1   # Phase1 のみ
  python3 scripts/phase_check.py --phase Phase2   # Phase2 のみ
  python3 scripts/phase_check.py --test           # ダミーデータ10件でテスト

環境変数:
  NOTION_API_KEY  Notion API キー（必須）
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("⚠️  requests が未インストールです: pip install requests --break-system-packages")
    sys.exit(1)

try:
    import numpy as np
    from scipy import stats
except ImportError:
    print("⚠️  numpy/scipy が未インストールです:")
    print("   pip install numpy scipy --break-system-packages")
    sys.exit(1)

# ── 定数 ─────────────────────────────────────────────────────────

DATABASE_ID = "785bde47451e4ed99b73f1eab36381f2"
NOTION_VER  = "2022-06-28"
QUERY_URL   = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"


# ── Notion DB からレコード全取得 ──────────────────────────────────

def fetch_all_records(api_key: str, phase_filter: str | None = None) -> list:
    """
    ページネーション対応で全レコードを取得する。
    結果が「見送り」のレコードは除外（購入したレースのみ）。
    """
    headers = {
        "Authorization":  f"Bearer {api_key}",
        "Notion-Version": NOTION_VER,
        "Content-Type":   "application/json",
    }

    # フィルター構築
    filter_conditions = [
        {
            "property": "結果",
            "select":   {"does_not_equal": "見送り"}
        }
    ]
    if phase_filter:
        filter_conditions.append({
            "property": "Phase",
            "select":   {"equals": phase_filter}
        })

    body = {
        "filter": (
            {"and": filter_conditions}
            if len(filter_conditions) > 1
            else filter_conditions[0]
        ),
        "page_size": 100,
    }

    records = []
    start_cursor = None

    while True:
        if start_cursor:
            body["start_cursor"] = start_cursor

        resp = requests.post(QUERY_URL, headers=headers, json=body, timeout=30)

        if resp.status_code != 200:
            print(f"❌ Notion API エラー: {resp.status_code}", file=sys.stderr)
            try:
                print(json.dumps(resp.json(), ensure_ascii=False, indent=2), file=sys.stderr)
            except Exception:
                print(resp.text, file=sys.stderr)
            sys.exit(1)

        data = resp.json()
        records.extend(data.get("results", []))

        if data.get("has_more") and data.get("next_cursor"):
            start_cursor = data["next_cursor"]
        else:
            break

    return records


def parse_record(page: dict) -> dict:
    """Notion ページオブジェクトから必要フィールドを抽出する"""
    props = page.get("properties", {})

    def get_number(key):
        p = props.get(key, {})
        return p.get("number")  # None の場合もあり

    def get_select(key):
        p = props.get(key, {})
        s = p.get("select")
        return s.get("name") if s else None

    def get_rich_text(key):
        p = props.get(key, {})
        rt = p.get("rich_text", [])
        return rt[0]["text"]["content"] if rt else ""

    def get_title(key):
        p = props.get(key, {})
        t = p.get("title", [])
        return t[0]["text"]["content"] if t else ""

    return {
        "レース名":     get_title("レース名"),
        "購入金額":     get_number("購入金額"),
        "払戻金":       get_number("払戻金"),
        "回収率":       get_number("回収率"),
        "結果":         get_select("結果"),
        "Claude確信度": get_select("Claude確信度"),
        "馬券種":       get_select("馬券種"),
        "Phase":        get_select("Phase"),
    }


# ── 統計計算 ─────────────────────────────────────────────────────

def phase_check(records: list) -> dict:
    """
    records: parse_record() で変換したリスト
    戻り値: 集計結果 dict
    """
    returns = []
    for r in records:
        amount = r.get("購入金額") or 0
        payout = r.get("払戻金")  or 0
        if amount > 0:
            returns.append(payout / amount)
        else:
            returns.append(0.0)

    n = len(returns)
    if n == 0:
        return {"status": "データなし", "n": 0}

    arr     = np.array(returns)
    mean_r  = float(np.mean(arr))
    se      = float(stats.sem(arr)) if n > 1 else 0.0

    # 信頼区間（サンプル1件の場合は CI = mean）
    if n > 1:
        ci_lower_95 = mean_r - stats.t.ppf(0.975, df=n - 1) * se
        ci_lower_90 = mean_r - stats.t.ppf(0.95,  df=n - 1) * se
    else:
        ci_lower_95 = ci_lower_90 = mean_r

    # ── Phase 移行判断 ────────────────────────────────────────────
    if n >= 1000 and mean_r >= 1.03 and ci_lower_95 >= 1.01:
        judgment = "🚀 Phase 2 本格移行 OK"
    elif n >= 500 and mean_r >= 1.03 and ci_lower_90 >= 1.005:
        judgment = "🟡 部分移行 OK（少額で馬連並行開始可）"
    elif n >= 500 and mean_r >= 1.03 and ci_lower_95 >= 0.97:
        judgment = "🟠 移行候補（CI幅まだ広め、継続確認）"
    elif n >= 300 and mean_r >= 1.02:
        judgment = "🔵 移行検討開始（データ蓄積を続ける）"
    elif n >= 500 and mean_r < 0.97:
        judgment = "⚠️  フィルター条件見直しを検討"
    else:
        judgment = "⏳ Phase 1 継続（データ蓄積中）"

    # ── 確信度別・馬券種別の内訳 ─────────────────────────────────
    def group_stats(key):
        groups = {}
        for r, ret in zip(records, returns):
            val = r.get(key) or "不明"
            groups.setdefault(val, []).append(ret)
        result = {}
        for val, rets in sorted(groups.items()):
            result[val] = {
                "count": len(rets),
                "mean_roi_pct": round(float(np.mean(rets)) * 100, 1),
            }
        return result

    # ── 次の移行基準までの残りレース数 ──────────────────────────
    def remaining(target_n):
        return max(0, target_n - n)

    next_milestones = [
        ("移行検討開始",  300,  "回収率102%以上"),
        ("部分移行 OK",   500,  "回収率103%以上 + 90%CI下限100.5%超"),
        ("本格移行",     1000,  "回収率103%以上 + 95%CI下限101%超"),
    ]

    return {
        "n":             n,
        "mean_roi":      round(mean_r * 100, 1),
        "ci_lower_95":   round(ci_lower_95 * 100, 1),
        "ci_lower_90":   round(ci_lower_90 * 100, 1),
        "judgment":      judgment,
        "by_confidence": group_stats("Claude確信度"),
        "by_ticket":     group_stats("馬券種"),
        "next_milestones": [
            {
                "label":     label,
                "remaining": remaining(target_n),
                "total":     target_n,
                "condition": cond,
            }
            for label, target_n, cond in next_milestones
        ],
    }


# ── テキスト出力 ─────────────────────────────────────────────────

def print_report(result: dict, phase_label: str = "全体"):
    print(f"\n=== Phase 移行チェック ({phase_label}) ===")
    print(f"集計対象: 購入レース（見送り除く）")
    print()

    if result.get("status") == "データなし":
        print("  データがありません。")
        return

    n           = result["n"]
    mean_roi    = result["mean_roi"]
    ci95        = result["ci_lower_95"]
    ci90        = result["ci_lower_90"]
    judgment    = result["judgment"]

    print(f"{'サンプル数':<16}: {n:>6} レース")
    print(f"{'平均回収率':<16}: {mean_roi:>6.1f}%")
    print(f"{'95%CI 下限':<16}: {ci95:>6.1f}%")
    print(f"{'90%CI 下限':<16}: {ci90:>6.1f}%")

    # 確信度別
    by_conf = result.get("by_confidence", {})
    if by_conf:
        print(f"\nClaude確信度別:")
        for k, v in by_conf.items():
            print(f"  {k:<8}: {v['count']:>4}レース  回収率 {v['mean_roi_pct']:>6.1f}%")

    # 馬券種別
    by_ticket = result.get("by_ticket", {})
    if by_ticket:
        print(f"\n馬券種別:")
        for k, v in by_ticket.items():
            print(f"  {k:<6}: {v['count']:>4}レース  回収率 {v['mean_roi_pct']:>6.1f}%")

    print(f"\n判定: {judgment}")

    # 次の移行基準
    print(f"\n次の移行基準:")
    for ms in result.get("next_milestones", []):
        rem  = ms["remaining"]
        tot  = ms["total"]
        cond = ms["condition"]
        if rem == 0:
            status = "✅ 達成済"
        else:
            status = f"あと {rem:>4}R（計 {tot}R）"
        print(f"  {ms['label']:<12} → {status}  かつ {cond}")

    print()


# ── テストデータ ─────────────────────────────────────────────────

def make_test_records(n: int = 10) -> list:
    """ダミーレコードを生成（的中3件・非的中7件）"""
    import random
    random.seed(42)
    results = []
    for i in range(n):
        is_hit    = (i % 3 == 0)
        amount    = 1000
        payout    = random.randint(2000, 4000) if is_hit else 0
        results.append({
            "レース名":     f"テストレース{i+1:02d}",
            "購入金額":     amount,
            "払戻金":       payout,
            "回収率":       payout / amount if amount > 0 else 0,
            "結果":         "的中" if is_hit else "非的中",
            "Claude確信度": "high" if i < 5 else "medium",
            "馬券種":       "複勝",
            "Phase":        "Phase1",
        })
    return results


# ── メイン ───────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Notion DB から競馬予想ログを取得して Phase 移行判断を出力する"
    )
    parser.add_argument(
        "--phase", default=None,
        choices=["Phase1", "Phase2"],
        help="集計対象を Phase で絞り込む"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="ダミーデータ10件でテスト実行（Notion 接続不要）"
    )
    args = parser.parse_args()

    # テストモード
    if args.test:
        print("【テストモード】ダミーデータ10件で集計します\n")
        records = make_test_records(10)
        result  = phase_check(records)
        print_report(result, "テスト（10件）")
        return

    # API KEY チェック
    api_key = os.environ.get("NOTION_API_KEY", "")
    if not api_key:
        print("❌ 環境変数 NOTION_API_KEY が設定されていません", file=sys.stderr)
        print("   export NOTION_API_KEY='secret_xxxx...'", file=sys.stderr)
        sys.exit(1)

    phase_label = args.phase if args.phase else "全体"
    print(f"Notion DB からレコードを取得中... (Phase: {phase_label})")

    pages   = fetch_all_records(api_key, args.phase)
    records = [parse_record(p) for p in pages]

    print(f"取得完了: {len(records)} 件\n")

    result = phase_check(records)
    print_report(result, phase_label)


if __name__ == "__main__":
    main()

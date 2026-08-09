#!/usr/bin/env python3
"""
Notion 競馬予想ログ記録スクリプト (notion_logger.py)
=====================================================
予想結果（的中・非的中・見送り）を Notion の「競馬予想ログ」DB に
1レース1レコードで記録する。

DB URL      : https://www.notion.so/785bde47451e4ed99b73f1eab36381f2
data_source : f12d7651-4e6a-43fc-a323-3e2af5a0c144
API KEY     : 環境変数 NOTION_API_KEY から取得

使い方:
  # 的中
  python3 scripts/notion_logger.py \
    --race_id "202305010101" --race_name "3歳未勝利" \
    --date "2023-05-01" --venue "東京" --dist "芝1600" \
    --field_size 10 --track "良" --filter_score 5 \
    --claude_score "high" --ticket_type "複勝" \
    --horse "テスト馬A" --amount 1000 --result "的中" \
    --payout 2800 --phase "Phase1"

  # dry-run（Notion に送信せず出力確認のみ）
  python3 scripts/notion_logger.py ... --dry-run
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

# ── 定数 ─────────────────────────────────────────────────────────

DATABASE_ID  = "785bde47451e4ed99b73f1eab36381f2"
API_URL      = "https://api.notion.com/v1/pages"
NOTION_VER   = "2022-06-28"

VENUE_OPTIONS = [
    "東京", "中山", "阪神", "京都", "中京",
    "札幌", "函館", "福島", "新潟", "小倉",
    "大井", "川崎", "船橋", "浦和", "名古屋",
    "笠松", "園田", "高知", "佐賀", "その他",
]
TRACK_OPTIONS        = ["良", "稍重", "重", "不良"]
CLAUDE_SCORE_OPTIONS = ["high", "medium", "low", "skip"]
TICKET_OPTIONS       = ["複勝", "馬連", "ワイド", "単勝", "なし"]
RESULT_OPTIONS       = ["的中", "非的中", "見送り"]
PHASE_OPTIONS        = ["Phase1", "Phase2"]


# ── Notion プロパティ構築 ─────────────────────────────────────────

def build_properties(args) -> dict:
    props = {}

    # TITLE: レース名
    props["レース名"] = {
        "title": [{"text": {"content": args.race_name}}]
    }

    # DATE: 日付
    props["日付"] = {"date": {"start": args.date}}

    # SELECT: 競馬場
    if args.venue:
        props["競馬場"] = {"select": {"name": args.venue}}

    # RICH_TEXT: race_id
    props["race_id"] = {
        "rich_text": [{"text": {"content": args.race_id}}]
    }

    # RICH_TEXT: 距離
    if args.dist:
        props["距離"] = {
            "rich_text": [{"text": {"content": args.dist}}]
        }

    # NUMBER: 頭数
    if args.field_size is not None:
        props["頭数"] = {"number": args.field_size}

    # SELECT: 馬場
    if args.track:
        props["馬場"] = {"select": {"name": args.track}}

    # NUMBER: 歪みスコア
    if args.filter_score is not None:
        props["歪みスコア"] = {"number": args.filter_score}

    # SELECT: Claude確信度
    if args.claude_score:
        props["Claude確信度"] = {"select": {"name": args.claude_score}}

    # SELECT: 馬券種
    if args.ticket_type:
        props["馬券種"] = {"select": {"name": args.ticket_type}}

    # RICH_TEXT: 予想馬
    if args.horse:
        props["予想馬"] = {
            "rich_text": [{"text": {"content": args.horse}}]
        }

    # NUMBER: 購入金額
    if args.amount is not None:
        props["購入金額"] = {"number": args.amount}

    # SELECT: 結果
    if args.result:
        props["結果"] = {"select": {"name": args.result}}

    # NUMBER: 払戻金
    payout = args.payout if args.payout is not None else 0
    props["払戻金"] = {"number": payout}

    # NUMBER: 回収率（自動計算）
    if args.amount and args.amount > 0:
        roi = payout / args.amount
        props["回収率"] = {"number": round(roi, 4)}

    # RICH_TEXT: EV上位馬
    if args.ev_horses:
        props["EV上位馬"] = {
            "rich_text": [{"text": {"content": args.ev_horses}}]
        }

    # SELECT: Phase
    if args.phase:
        props["Phase"] = {"select": {"name": args.phase}}

    # RICH_TEXT: メモ
    if args.memo:
        props["メモ"] = {
            "rich_text": [{"text": {"content": args.memo}}]
        }

    return props


# ── Notion API 呼び出し ───────────────────────────────────────────

def post_to_notion(properties: dict, api_key: str) -> dict:
    headers = {
        "Authorization":  f"Bearer {api_key}",
        "Notion-Version": NOTION_VER,
        "Content-Type":   "application/json",
    }
    payload = {
        "parent":     {"type": "database_id", "database_id": DATABASE_ID},
        "properties": properties,
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    return resp


# ── メイン ───────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="競馬予想結果を Notion DB に記録する",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--race_id",      required=True,  help="レースID (例: 202305010101)")
    p.add_argument("--race_name",    required=True,  help="レース名 (例: 3歳未勝利)")
    p.add_argument("--date",         required=True,  help="開催日 YYYY-MM-DD")
    p.add_argument("--venue",        default=None,   help=f"競馬場 ({'/'.join(VENUE_OPTIONS)})")
    p.add_argument("--dist",         default=None,   help="距離 (例: 芝1600)")
    p.add_argument("--field_size",   type=int,       default=None, help="頭数")
    p.add_argument("--track",        default=None,   help=f"馬場 ({'/'.join(TRACK_OPTIONS)})")
    p.add_argument("--filter_score", type=int,       default=None, help="歪みスコア")
    p.add_argument("--claude_score", default=None,   help=f"Claude確信度 ({'/'.join(CLAUDE_SCORE_OPTIONS)})")
    p.add_argument("--ticket_type",  default=None,   help=f"馬券種 ({'/'.join(TICKET_OPTIONS)})")
    p.add_argument("--horse",        default=None,   help="予想馬名")
    p.add_argument("--amount",       type=int,       default=None, help="購入金額（円）")
    p.add_argument("--result",       required=True,  help=f"結果 ({'/'.join(RESULT_OPTIONS)})")
    p.add_argument("--payout",       type=int,       default=0,    help="払戻金（円）")
    p.add_argument("--ev_horses",    default=None,   help="EV上位馬 (例: 馬A(0.32), 馬B(0.18))")
    p.add_argument("--phase",        default=None,   help=f"Phase ({'/'.join(PHASE_OPTIONS)})")
    p.add_argument("--memo",         default=None,   help="メモ")
    p.add_argument("--dry-run",      action="store_true", help="Notion に送信せず確認のみ")
    return p


def validate_args(args):
    errors = []
    if args.venue and args.venue not in VENUE_OPTIONS:
        errors.append(f"--venue は {VENUE_OPTIONS} のいずれかを指定してください")
    if args.track and args.track not in TRACK_OPTIONS:
        errors.append(f"--track は {TRACK_OPTIONS} のいずれかを指定してください")
    if args.claude_score and args.claude_score not in CLAUDE_SCORE_OPTIONS:
        errors.append(f"--claude_score は {CLAUDE_SCORE_OPTIONS} のいずれかを指定してください")
    if args.ticket_type and args.ticket_type not in TICKET_OPTIONS:
        errors.append(f"--ticket_type は {TICKET_OPTIONS} のいずれかを指定してください")
    if args.result not in RESULT_OPTIONS:
        errors.append(f"--result は {RESULT_OPTIONS} のいずれかを指定してください")
    if args.phase and args.phase not in PHASE_OPTIONS:
        errors.append(f"--phase は {PHASE_OPTIONS} のいずれかを指定してください")
    return errors


def main():
    parser = build_parser()
    args = parser.parse_args()

    # バリデーション
    errors = validate_args(args)
    if errors:
        for e in errors:
            print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    # API KEY チェック
    api_key = os.environ.get("NOTION_API_KEY", "")
    if not api_key and not args.dry_run:
        print("❌ 環境変数 NOTION_API_KEY が設定されていません", file=sys.stderr)
        print("   export NOTION_API_KEY='secret_xxxx...'", file=sys.stderr)
        sys.exit(1)

    # プロパティ構築
    properties = build_properties(args)

    # dry-run
    if args.dry_run:
        print("【dry-run モード】以下のデータを Notion に送信する予定です:\n")
        print(json.dumps(properties, ensure_ascii=False, indent=2))
        print(f"\n✅ dry-run 完了: {args.race_name} ({args.race_id})")
        return

    # Notion に送信
    resp = post_to_notion(properties, api_key)

    if resp.status_code in (200, 201):
        page_id = resp.json().get("id", "")
        print(f"✅ Notionに記録しました: {args.race_name} ({args.race_id})")
        if page_id:
            print(f"   ページID: {page_id}")
    else:
        print(f"❌ Notion API エラー: {resp.status_code}", file=sys.stderr)
        try:
            err_body = resp.json()
            print(json.dumps(err_body, ensure_ascii=False, indent=2), file=sys.stderr)
        except Exception:
            print(resp.text, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

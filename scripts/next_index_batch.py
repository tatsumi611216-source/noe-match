#!/usr/bin/env python3
"""今日申請するインデックス申請バッチ（10本）を表示する。

正本は agent/index_request_batches.md の Day 節と agent/index_requests_done.json。
このスクリプトは「次はどのDayか」を機械的に決めて、そのURLを貼れる形で出すだけ。
申請したら index_requests_done.json の days に日付を書き、pending から番号を消すこと。
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    done = json.loads((ROOT / "agent" / "index_requests_done.json").read_text(encoding="utf-8"))
    pending = sorted(done.get("pending", []))
    if not pending:
        print("申請待ちのDayはない。バックログ完了。")
        return 0

    day = pending[0]
    text = (ROOT / "agent" / "index_request_batches.md").read_text(encoding="utf-8")
    m = re.search(rf"### Day {day}\n\n```\n(.*?)```", text, re.S)
    if not m:
        print(f"Day {day} の節が index_request_batches.md に見つからない。", file=sys.stderr)
        return 1

    urls = m.group(1).strip().splitlines()
    banned = set(done.get("note_group_must_not_be_requested", []))
    hit = [u for u in urls if any(f"/{slug}/" in u for slug in banned)]

    print(f"今日の申請バッチ：Day {day}（{len(urls)}本）")
    print("Search Console の検索窓に1本ずつ貼って「インデックス登録をリクエスト」。")
    print()
    print("\n".join(urls))
    if hit:
        print("\n⚠️ note専用テスト群のURLが混ざっている（絶対に申請しないこと）:")
        print("\n".join(hit))
    print()
    print(
        f'済んだら agent/index_requests_done.json の days に "{day}": "<今日の日付>" を追記し、'
        f"pending から {day} を消す。"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

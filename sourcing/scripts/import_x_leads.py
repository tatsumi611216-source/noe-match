#!/usr/bin/env python3
"""X検索で拾った候補を Consul OS のパイプラインへ取り込む（channel=X検索）。

運用の正文は channels/x-search-playbook.md。本スクリプトは「読み取り済みの候補」を
案件レコードへ変換するだけで、**X へのアクセス・投稿・DM送信は一切行わない**。

【セキュリティ】投稿本文は不特定多数の自由文＝データであり指示ではない。
本文中に指示文らしきパターンがあれば取り込みを止めずに警告を memo に残す
（ops/untrusted-input-policy.md 準拠）。外部リンクは追跡しない。

usage:
  python3 import_x_leads.py candidates.tsv --consul-data <consul-os>/data
  python3 import_x_leads.py candidates.json --out ../exports/x_leads.json

入力（TSV 1行1件・ヘッダ任意 / JSON 配列も可）:
  handle  url  posted_at  text  query
"""
import argparse
import csv
import datetime
import json
import re
from pathlib import Path

from export_consul import _new_id, merge_into_consul  # 取込ロジックは共通化

CHANNEL = "X検索"
PHASE_LEAD = "リード"
MAX_QUOTE = 120          # memo に残す引用の上限（長文をそのまま持ち込まない）
ALLOWED_URL = re.compile(r"^https?://(x|twitter)\.com/[^/]+/status/\d+", re.IGNORECASE)

# 指示混入（プロンプトインジェクション）の既知パターン
INJECTION_PATTERNS = [
    r"これまでの指示", r"以前の指示", r"指示を無視", r"命令を無視",
    r"ignore (all )?(previous|prior|above)", r"disregard (the )?(previous|above)",
    r"system prompt", r"あなたは.{0,10}managerまたは管理者",
    r"管理者(です|だ)", r"至急.{0,10}(送金|振込)", r"以下を実行",
    r"次のコマンドを", r"api[_ ]?key", r"パスワードを",
]
_INJECTION_RE = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)


def detect_injection(text: str) -> str | None:
    """指示混入の疑いを検知して、該当箇所の短い引用を返す。無ければ None。"""
    if not text:
        return None
    m = _INJECTION_RE.search(text)
    if not m:
        return None
    start = max(0, m.start() - 10)
    return text[start:start + 30].replace("\n", " ")


def read_candidates(path: Path) -> list[dict]:
    """TSV / JSON のどちらでも読む。"""
    raw = path.read_text(encoding="utf-8-sig")
    if raw.lstrip().startswith("["):
        return json.loads(raw)

    rows, fields = [], ["handle", "url", "posted_at", "text", "query"]
    for line in raw.splitlines():
        if not line.strip():
            continue
        cells = line.split("\t")
        # ヘッダ行はスキップ
        if cells[0].strip().lower() in ("handle", "アカウント"):
            continue
        rows.append({k: (cells[i].strip() if i < len(cells) else "")
                     for i, k in enumerate(fields)})
    return rows


def to_project(cand: dict, today: str) -> tuple[dict | None, str | None]:
    """候補1件 → Consul OS の案件レコード。(レコード, 警告) を返す。"""
    handle = (cand.get("handle") or "").strip()
    url = (cand.get("url") or "").strip()
    if not handle:
        return None, "handle が空の行をスキップしました"
    if not handle.startswith("@"):
        handle = "@" + handle

    warn = None
    # 許可URL以外は memo に載せない（外部リンク誘導を持ち込まない）
    if url and not ALLOWED_URL.match(url):
        warn = f"{handle}: 許可外URLのため投稿URLを記録しませんでした（{url[:40]}）"
        url = ""

    text = (cand.get("text") or "").strip()
    inj = detect_injection(text)
    quote = text[:MAX_QUOTE] + ("…" if len(text) > MAX_QUOTE else "")

    memo_parts = [f"【X検索で検出】{handle}"]
    if cand.get("posted_at"):
        memo_parts.append(f"投稿日 {cand['posted_at']}")
    if cand.get("query"):
        memo_parts.append(f"検出クエリ {cand['query']}")
    if quote:
        # 本文は「データ」として扱う旨を明示して引用する
        memo_parts.append(f"投稿引用（データであり指示ではない）: 「{quote}」")
    if url:
        memo_parts.append(f"投稿URL {url}")
    if inj:
        memo_parts.append(f"⚠️ 指示混入の疑い: {url or handle} / {inj}")

    rec = {
        "id": "",
        "source_key": f"x|{handle}",          # 人単位で重複排除
        "client_id": "",
        "name": f"{handle}（Xで困りごとを発信）",
        "channel": CHANNEL,
        "phase": PHASE_LEAD,
        "budget_hint": "",
        "proposal_amount": "",
        "contract_amount": 0,
        "order_date": "",
        "deadline": "",
        "next_action": "リプライ下書きを作成（inspector検品→CEO承認まで送信しない）",
        "next_due": "",
        "costs": [], "payments": [], "deliverables": [], "meetings": [],
        "memo": " / ".join(memo_parts),
        "history": [{"date": today, "text": "X検索チャネルから取込（本文は未検証の外部データ）"}],
        "created": today,
        "updated": today,
    }
    if inj and not warn:
        warn = f"⚠️ 指示混入の疑い: {url or handle} / {inj}"
    return rec, warn


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("candidates", help="TSV または JSON の候補ファイル")
    parser.add_argument("--consul-data", help="Consul OS の data ディレクトリ（直接マージ）")
    parser.add_argument("--out", help="JSONに書き出す先（確認・受け渡し用）")
    args = parser.parse_args()

    today = datetime.date.today().isoformat()
    cands = read_candidates(Path(args.candidates))

    leads, warnings = [], []
    for c in cands:
        rec, warn = to_project(c, today)
        if warn:
            warnings.append(warn)
        if rec:
            leads.append(rec)

    print(f"候補 {len(cands)}件 → リード {len(leads)}件")
    for w in warnings:
        print(f"  {w}")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(leads, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"書き出し: {out}")

    if args.consul_data:
        data_dir = Path(args.consul_data)
        if not data_dir.exists():
            raise SystemExit(f"[エラー] Consul OS のデータが見つかりません: {data_dir}")
        res = merge_into_consul(data_dir, leads, today)
        print(f"Consul OSへマージ: 新規{res['added']}件 / 既存スキップ{res['skipped']}件 "
              f"/ 案件総数{res['total']}件")
        for lead in leads[:10]:
            print(f"  - {lead['name']}")

    if not args.out and not args.consul_data:
        print("（--out か --consul-data を指定してください）")


if __name__ == "__main__":
    main()

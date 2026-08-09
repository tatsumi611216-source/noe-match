#!/usr/bin/env python3
"""営業リストを Consul OS のパイプライン（data/projects.json）へ流し込む。

ソーシングツールが集めた「採用に困っている企業」を、Consul OS の案件レコード
（phase=リード）として登録する。Consul OS 側の sync_jobs_csv と同じ作法で、
source_key による重複排除を行うため何度実行しても重複しない。

usage:
  # 1) JSONに書き出すだけ（Actions成果物・確認用）
  python3 export_consul.py --out ../exports/consul_leads.json

  # 2) Consul OS のデータへ直接マージ（ローカルPCで実行）
  python3 export_consul.py --consul-data C:\\Users\\tatsu\\consul-os\\data

Consul OS 側の projects.json のスキーマに合わせている（server.py sync_jobs_csv 準拠）。
フェーズ語彙: リード / 提案中 / 面談 / 受注 / 稼働中 / 納品 / 失注
"""
import argparse
import datetime
import json
import re
from pathlib import Path

from common import DEFAULT_DB, connect

CHANNEL = "ソーシング"          # platforms.json に無ければ追加する媒体名
PHASE_LEAD = "リード"
MIN_SCORE_DEFAULT = 0.0
BASE_DIR = Path(__file__).resolve().parent.parent


def _new_id(prefix: str, items: list[dict]) -> str:
    """Consul OS の new_id と同じ採番（P-1, P-2, ...）。"""
    n = 0
    for it in items:
        m = re.match(rf"{prefix}-(\d+)$", str(it.get("id", "")))
        if m:
            n = max(n, int(m.group(1)))
    return f"{prefix}-{n + 1}"


def fetch_leads(conn, min_score: float, limit: int, include_listed: bool) -> list[dict]:
    """営業対象企業を取得する。未上場（スタートアップ）を優先し、任意で上場も含める。"""
    rows = []
    q_unlisted = """
        SELECT c.id, c.name, c.prefecture, c.industry, c.employee_count,
               c.funding_stage, c.last_funding_date, c.website, c.careers_url,
               c.priority_score, c.is_listed,
               COUNT(jp.id)                    AS active_jobs,
               GROUP_CONCAT(DISTINCT cat.name) AS categories,
               MIN(jp.first_seen_at)           AS oldest_posting
        FROM companies c
        JOIN job_postings jp ON jp.company_id = c.id AND jp.is_active = 1
        LEFT JOIN categories cat ON cat.id = jp.category_id
        WHERE c.sales_status = '未接触'
          AND c.priority_score >= ?
          {listed_filter}
        GROUP BY c.id
        ORDER BY c.priority_score DESC, active_jobs DESC
        LIMIT ?
    """
    filt = "" if include_listed else "AND c.is_listed = 0"
    cur = conn.execute(q_unlisted.format(listed_filter=filt), (min_score, limit))
    cols = [d[0] for d in cur.description]
    for r in cur.fetchall():
        rows.append(dict(zip(cols, r)))
    return rows


def to_project(lead: dict, today: str) -> dict:
    """企業1社 → Consul OS の案件レコード（phase=リード）。"""
    name = lead["name"]
    jobs = lead.get("active_jobs") or 0
    cats = lead.get("categories") or "-"
    score = lead.get("priority_score") or 0

    # 営業の切り口が一目で分かるメモを組み立てる
    memo_parts = [
        f"【ソーシング自動検出】採用の困り度スコア {score:.0f}",
        f"有効求人 {jobs}件（{cats}）",
    ]
    if lead.get("oldest_posting"):
        memo_parts.append(f"最古の掲載検知 {lead['oldest_posting']}")
    if lead.get("funding_stage"):
        fund = lead["funding_stage"]
        if lead.get("last_funding_date"):
            fund += f"・直近調達 {lead['last_funding_date']}"
        memo_parts.append(fund)
    if lead.get("employee_count"):
        memo_parts.append(f"従業員 {lead['employee_count']}名")
    for label, key in (("業種", "industry"), ("所在地", "prefecture")):
        if lead.get(key):
            memo_parts.append(f"{label} {lead[key]}")
    for label, key in (("採用ページ", "careers_url"), ("企業サイト", "website")):
        if lead.get(key):
            memo_parts.append(f"{label} {lead[key]}")
    if lead.get("is_listed"):
        memo_parts.append("※上場企業")

    return {
        "id": "",                                   # マージ時に採番
        "source_key": f"sourcing|{name}",           # 企業単位で一意（重複排除キー）
        "client_id": "",
        "name": f"{name}（採用支援の提案）",
        "channel": CHANNEL,
        "phase": PHASE_LEAD,
        "budget_hint": "",
        "proposal_amount": "",
        "contract_amount": 0,
        "order_date": "",
        "deadline": "",
        "next_action": "初回アプローチ（求人内容を踏まえた提案文の作成）",
        "next_due": "",
        "costs": [], "payments": [], "deliverables": [], "meetings": [],
        "memo": " / ".join(memo_parts),
        "history": [{"date": today, "text": "ソーシングツールから自動取込（採用中の企業を検出）"}],
        "created": today,
        "updated": today,
    }


def merge_into_consul(data_dir: Path, leads: list[dict], today: str) -> dict:
    """Consul OS の projects.json へマージする（source_key で重複排除）。"""
    ppath = data_dir / "projects.json"
    projects = json.loads(ppath.read_text(encoding="utf-8")) if ppath.exists() else []
    known = {p.get("source_key") for p in projects if p.get("source_key")}

    added = 0
    for lead in leads:
        if lead["source_key"] in known:
            continue
        rec = dict(lead)
        rec["id"] = _new_id("P", projects)
        projects.append(rec)
        known.add(rec["source_key"])
        added += 1

    if added:
        # 破損に備えて書き込み前にバックアップ（Consul OS の慣習に合わせる）
        if ppath.exists():
            bak = data_dir / f"projects.json.bak-{today.replace('-', '')}-sourcing"
            bak.write_text(ppath.read_text(encoding="utf-8"), encoding="utf-8")
        ppath.write_text(json.dumps(projects, ensure_ascii=False, indent=2), encoding="utf-8")

    # 媒体マスタに「ソーシング」が無ければ追加（Consul OS はデータ駆動で追加可）
    plpath = data_dir / "platforms.json"
    pf_added = False
    if plpath.exists():
        platforms = json.loads(plpath.read_text(encoding="utf-8"))
        if not any(p.get("name") == CHANNEL for p in platforms):
            platforms.append({
                "id": _new_id("pf", platforms),
                "name": CHANNEL,
                "url": "",
                "patrol": True,
                "notes": "ソーシングツール（noe-match/sourcing）が自動検出したアウトバウンド先。"
                         "採用ページのJobPosting構造化データから求人を収集し、"
                         "採用の困り度スコア順にリード化する。応募型ではなくこちらから提案する経路。",
            })
            plpath.write_text(json.dumps(platforms, ensure_ascii=False, indent=2), encoding="utf-8")
            pf_added = True

    return {"added": added, "skipped": len(leads) - added, "total": len(projects),
            "platform_added": pf_added}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--consul-data", help="Consul OS の data ディレクトリ（直接マージする）")
    parser.add_argument("--out", help="JSONに書き出す先（マージせず確認・受け渡し用）")
    parser.add_argument("--min-score", type=float, default=MIN_SCORE_DEFAULT,
                        help="この困り度スコア以上の企業だけを対象にする")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--include-listed", action="store_true",
                        help="上場企業も含める（既定は未上場＝スタートアップのみ）")
    args = parser.parse_args()

    today = datetime.date.today().isoformat()
    conn = connect(args.db)
    try:
        raw = fetch_leads(conn, args.min_score, args.limit, args.include_listed)
    finally:
        conn.close()
    leads = [to_project(r, today) for r in raw]
    print(f"営業リード: {len(leads)}社（スコア{args.min_score}以上"
          f"{'・上場含む' if args.include_listed else '・未上場のみ'}）")

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(leads, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"書き出し: {out}")

    if args.consul_data:
        data_dir = Path(args.consul_data)
        if not data_dir.exists():
            raise SystemExit(f"[エラー] Consul OS のデータディレクトリが見つかりません: {data_dir}")
        res = merge_into_consul(data_dir, leads, today)
        print(f"Consul OSへマージ: 新規{res['added']}件 / 既存スキップ{res['skipped']}件 "
              f"/ 案件総数{res['total']}件")
        if res["platform_added"]:
            print(f"媒体マスタに「{CHANNEL}」を追加しました")
        for lead in leads[:10]:
            print(f"  - {lead['name']}")

    if not args.out and not args.consul_data:
        print("（--out か --consul-data を指定してください）")


if __name__ == "__main__":
    main()

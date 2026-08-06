#!/usr/bin/env python3
"""EDINET関係会社抽出のオフライン検証（APIキー不要）。

有報CSV相当の行データから子会社を抽出し、corporate_relations と
companies(is_subsidiary=1) に反映されること、v_group_targets に出ることを確認。
"""
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from common import connect  # noqa: E402
from edinet_client import extract_subsidiaries, store_relations  # noqa: E402
from update_db import ingest_batch  # noqa: E402

# 有報CSV（TSV）相当: 項目名/値 のペア行
SAMPLE_ROWS = [
    {"項目名": "関係会社の状況 名称", "値": "サンプル電子デバイス株式会社"},
    {"項目名": "関係会社の状況 議決権の所有割合", "値": "100.0"},
    {"項目名": "子会社 名称", "値": "サンプルソフト株式会社"},
    {"項目名": "子会社 議決権の所有割合", "値": "80.0"},
    {"項目名": "その他 名称", "値": "無関係な項目"},   # 関係会社文脈でないので拾わない
    {"項目名": "関係会社の状況 名称", "値": "サンプル製造株式会社"},  # 親と同名でない子会社
]


def run():
    tmp = Path(tempfile.mkdtemp())
    db = tmp / "edinet.db"
    subprocess.run([sys.executable, str(SCRIPTS.parent / "init_db.py"), "--db", str(db)],
                   check=True, capture_output=True)
    conn = connect(db)
    parent = "サンプルホールディングス株式会社"

    subs = extract_subsidiaries(SAMPLE_ROWS, parent)
    names = {s["child_name"] for s in subs}
    assert names == {"サンプル電子デバイス株式会社", "サンプルソフト株式会社", "サンプル製造株式会社"}, names
    pct = {s["child_name"]: s["ownership_pct"] for s in subs}
    assert pct["サンプル電子デバイス株式会社"] == 100.0 and pct["サンプルソフト株式会社"] == 80.0, pct
    print(f"[OK] 子会社抽出: {len(subs)}社（無関係項目は除外・議決権割合もパース）")

    n = store_relations(conn, parent, subs, "2026-08-06", parent_corporate_number="1111111111111")
    assert n == 3
    rel = conn.execute("SELECT COUNT(*) FROM corporate_relations WHERE parent_name=?", (parent,)).fetchone()[0]
    sub_flag = conn.execute("SELECT COUNT(*) FROM companies WHERE is_subsidiary=1").fetchone()[0]
    assert rel == 3 and sub_flag == 3, f"relations={rel} sub={sub_flag}"
    print(f"[OK] DB反映: corporate_relations {rel}件 / companies is_subsidiary {sub_flag}社")

    # 子会社が採用していれば v_group_targets に出る
    ingest_batch(conn, [{
        "company": {"name": "サンプルソフト株式会社"},
        "records": [{"source_site": "c", "source_job_id": "j1",
                     "company_name": "サンプルソフト株式会社", "title": "エンジニア",
                     "employment_type": "FULL_TIME", "location": "東京都",
                     "salary_min": None, "salary_max": None, "url": "u", "posted_at": "2026-07-01"}],
    }], "careers", "2026-08-06")
    grp = conn.execute("SELECT name, parent_name FROM v_group_targets").fetchall()
    assert any(r[0] == "サンプルソフト株式会社" and r[1] == parent for r in grp), grp
    print(f"[OK] v_group_targets: {grp[0][0]} ← 親 {grp[0][1]}")

    conn.close()
    print("\n=== EDINET関係会社 全テスト通過 ===")


if __name__ == "__main__":
    run()

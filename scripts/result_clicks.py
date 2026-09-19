# -*- coding: utf-8 -*-
"""主KPI「結果直後のクリック数」を期間指定で出す（2026-09-19 新設・API未使用）

定義（agent/strategy_2026Q4.md 2026-09-19 改訂）:
  GA4内蔵 click のうち
    (a) linkId が "aff-" で始まるもの（結果直後の広告。aff-result / aff-hoken / aff-oisix …）
    (b) linkDomain が lin.ee のもの（LINE友だち追加）
  の合計。分母は Direct除きセッション＝ total.sessions −〔by_page の channel=Direct の sessions 合計〕。

データは agent/ga4_archive/YYYY-MM-DD.json の clicks キー（fetch_ga4.py が保存）。
clicks キーが無い日は「未取得」と数えて表示する（0件と混同しない）。
  埋めるには: python scripts/fetch_ga4.py --backfill-clicks

使い方:
  python scripts/result_clicks.py                          直近28日
  python scripts/result_clicks.py --days 14
  python scripts/result_clicks.py --start 2026-09-01 --end 2026-09-16
"""
import argparse
import collections
import datetime
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARC = os.path.join(ROOT, "agent", "ga4_archive")
AFF_DOMAINS = ("px.a8.net", "t.afi-b.com")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--start")
    ap.add_argument("--end")
    a = ap.parse_args()
    days = sorted(f[:-5] for f in os.listdir(ARC) if f.endswith(".json"))
    end = a.end or days[-1]
    start = a.start or (datetime.date.fromisoformat(end)
                        - datetime.timedelta(days=a.days - 1)).isoformat()

    n_days = missing = sessions = direct = 0
    aff_id = collections.Counter()      # (path, linkId)
    line = collections.Counter()        # path
    aff_other = collections.Counter()   # 広告ドメインだが id が aff- でない（結果直後ではない広告）
    for ds in days:
        if not (start <= ds <= end):
            continue
        d = json.load(io.open(os.path.join(ARC, ds + ".json"), encoding="utf-8"))
        n_days += 1
        sessions += d["total"]["sessions"]
        direct += sum(r["sessions"] for r in d["by_page"] if r.get("channel") == "Direct")
        if "clicks" not in d:
            missing += 1
            continue
        for c in d["clicks"]:
            if c.get("linkId", "").startswith("aff-"):
                aff_id[(c["path"], c["linkId"])] += c["count"]
            elif c.get("linkDomain") in AFF_DOMAINS:
                aff_other[c["path"]] += c["count"]
            if c.get("linkDomain") == "lin.ee":
                line[c["path"]] += c["count"]

    total = sum(aff_id.values()) + sum(line.values())
    nd = sessions - direct
    print("期間 %s 〜 %s（アーカイブ %d日・うち clicks 未取得 %d日）" % (start, end, n_days, missing))
    print("\n■ 主KPI 結果直後のクリック数: %d" % total)
    print("   広告（linkId が aff-）: %d" % sum(aff_id.values()))
    for (p, i), n in aff_id.most_common():
        print("     %3d  %s  #%s" % (n, p, i))
    print("   LINE（lin.ee）       : %d" % sum(line.values()))
    for p, n in line.most_common():
        print("     %3d  %s" % (n, p))
    print("\n■ 分母 セッション: 全体 %d ／ Direct %d ／ Direct除き %d（%.1f/日）"
          % (sessions, direct, nd, nd / max(n_days, 1)))
    if nd > 0:
        print("   結果直後クリック ÷ Direct除きセッション = %.2f%%" % (100.0 * total / nd))
    print("\n■ 参考: id が aff- でない広告リンクのクリック（結果直後以外）: %d" % sum(aff_other.values()))
    for p, n in aff_other.most_common():
        print("     %3d  %s" % (n, p))
    if missing:
        print("\n※ clicks 未取得の日がある。python scripts/fetch_ga4.py --backfill-clicks で埋めてから読むこと。")


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    main()

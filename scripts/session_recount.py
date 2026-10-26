# -*- coding: utf-8 -*-
"""セッション単位で流入を数え直す（2026-10-08 新設）

    python scripts/session_recount.py --start 2026-09-08 --end 2026-10-05
    python scripts/session_recount.py --days 28          直近28日（アーカイブの最終日まで）
    python scripts/session_recount.py --top 30           入口ページの表示行数

使うのは日次アーカイブの by_source（チャネル×参照元・ページなし）と by_landing（入口ページ）。
どちらもセッション単位なので、行を足しても重複しない。by_page（ページ×チャネル）は
1セッションが見たページの数だけ行が出るため、Direct除きやチャネル構成の計算に使ってはいけない
（9/8〜10/5 の Direct除きが、旧方式 428 に対しセッション単位では 464）。

流入元の区分（1セッションは必ず1つに入る。上から順に判定）:
  Direct → AI（参照元に chatgpt/openai/perplexity/copilot/gemini/claude）→ 検索（Organic Search
  または参照元が検索エンジン。Google/Bing/Yahoo/その他）→ note（note.com）→ その他
by_source の無い日は数えず、件数を「欠測」として出す（0 とは扱わない）。
"""
import argparse, datetime, glob, io, json, os, re, sys
from collections import Counter

ARC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agent", "ga4_archive")
AI = re.compile(r"(chatgpt|openai|perplexity|copilot|gemini|claude)", re.I)
SE = {"google": "検索:Google", "bing": "検索:Bing", "yahoo": "検索:Yahoo"}


def bucket(channel, source):
    s = (source or "").lower()
    if channel == "Direct":
        return "Direct"
    if AI.search(s):
        return "AI"
    for k, v in SE.items():
        if s.startswith(k) or ("." + k + ".") in s:
            return v
    if channel == "Organic Search" or re.match(r"(duckduckgo|ecosia|baidu|yandex|naver|msn|search\.)", s):
        return "検索:その他"
    if "note.com" in s:
        return "note"
    return "その他:" + channel


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--start"); ap.add_argument("--end")
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--top", type=int, default=20)
    a = ap.parse_args()
    fs = sorted(glob.glob(os.path.join(ARC, "*.json")))
    dates = [os.path.basename(f)[:-5] for f in fs]
    end = a.end or dates[-1]
    start = a.start or (datetime.date.fromisoformat(end) - datetime.timedelta(days=a.days - 1)).isoformat()
    tot = n = 0; missing = []
    mix = Counter(); land = Counter(); land_ch = {}
    for f, ds in zip(fs, dates):
        if not (start <= ds <= end):
            continue
        d = json.load(io.open(f, encoding="utf-8"))
        if "by_source" not in d:
            missing.append(ds); continue
        n += 1; tot += d["total"]["sessions"]
        for r in d["by_source"]:
            mix[bucket(r["channel"], r["source"])] += r["sessions"]
        for r in d.get("by_landing", []):
            b = bucket(r["channel"], r["source"])
            if b == "Direct":
                continue
            land[r["landing"]] += r["sessions"]
            land_ch.setdefault(r["landing"], Counter())[b] += r["sessions"]
    nd = sum(v for k, v in mix.items() if k != "Direct")
    print("期間 %s〜%s ／ 集計 %d日 ／ 欠測 %d日%s" % (start, end, n, len(missing),
          ("（" + ",".join(missing[:5]) + ("…" if len(missing) > 5 else "") + "）") if missing else ""))
    print("total.sessions %d ／ by_source 合計 %d（差はGA4の閾値処理）" % (tot, sum(mix.values())))
    print("Direct除きセッション %d" % nd)
    for k, v in mix.most_common():
        print("  %-14s %5d  %5.1f%%" % (k, v, 100.0 * v / max(sum(mix.values()), 1)))
    srch = sum(v for k, v in mix.items() if k.startswith("検索"))
    print("  └ 検索 合計 %d ／ AI %d ／ note %d（重複なし）" % (srch, mix["AI"], mix["note"]))
    print("\n入口ページ（Direct除き・セッション単位） 合計 %d" % sum(land.values()))
    for p, v in land.most_common(a.top):
        print("  %4d  %-48s %s" % (v, p, dict(land_ch[p].most_common(3))))


if __name__ == "__main__":
    main()

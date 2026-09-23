# -*- coding: utf-8 -*-
"""流入チャネルの内訳を出す（GSCが見ていない Bing・AI を可視化する）

    python scripts/channel_mix.py            直近28日
    python scripts/channel_mix.py --days 56  期間を変える
    python scripts/channel_mix.py --weekly   週次の推移も出す

計器の注意（agent/knowledge.md 2026-09-19 の項）:
  by_page の行はページ×チャネル単位なので、複数ページを見たセッションは重複して数えられる。
  ここで出す内訳は「構成比を見るための値」で、セッションの絶対数は total を使うこと。
  GSC は Google しか見ていない。Yahoo! JAPAN の検索結果は Google のインデックス由来だが、
  GSC の数字には出ない場合がある。Bing と AI アシスタントは GSC には一切出ない。
"""
import json, glob, os, sys, datetime
from collections import defaultdict

ARCHIVE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agent", "ga4_archive")

AI_SOURCES = ("chatgpt", "perplexity", "copilot", "gemini", "claude", "openai")

def bucket(channel, source):
    s = (source or "").lower()
    if any(a in s for a in AI_SOURCES):
        return "AI（ChatGPT等）"
    if channel == "Direct":
        return "Direct"
    if "bing" in s:
        return "Bing"
    if "yahoo" in s:
        return "Yahoo"
    if "google" in s:
        return "Google"
    if channel in ("Referral", "Organic Social", "Paid Search"):
        return channel
    return "その他"

def load(days):
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    out = []
    for f in sorted(glob.glob(os.path.join(ARCHIVE, "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        if start.isoformat() <= d["date"] <= end.isoformat():
            out.append(d)
    return out

def main():
    days = 28
    if "--days" in sys.argv:
        days = int(sys.argv[sys.argv.index("--days") + 1])
    data = load(days)
    if not data:
        print("対象期間のアーカイブが無い")
        return
    tot = sum(d["total"]["sessions"] for d in data)
    mix = defaultdict(int)
    for d in data:
        for r in d.get("by_page", []):
            mix[bucket(r["channel"], r.get("source"))] += r["sessions"]
    rows = sum(mix.values())
    print(f"期間 {data[0]['date']}〜{data[-1]['date']}（{len(data)}日）  total.sessions {tot}")
    print(f"{'内訳（by_page行の合算・重複あり）':<24} {'行':>5}  {'構成比':>6}")
    for k, v in sorted(mix.items(), key=lambda x: -x[1]):
        print(f"  {k:<22} {v:>5}  {100*v/rows:>5.1f}%")
    search = sum(v for k, v in mix.items() if k in ("Google", "Yahoo"))
    blind = sum(v for k, v in mix.items() if k in ("Bing", "AI（ChatGPT等）"))
    if search + blind:
        print(f"\nGSCが見ている範囲（Google＋Yahoo）: {search}行")
        print(f"GSCに出ない範囲（Bing＋AI）: {blind}行 ＝ 検索流入の {100*blind/(search+blind):.0f}%")

    if "--weekly" in sys.argv:
        wk = defaultdict(lambda: defaultdict(int))
        for d in data:
            dt = datetime.date.fromisoformat(d["date"])
            w = (dt - datetime.timedelta(days=dt.weekday())).isoformat()
            for r in d.get("by_page", []):
                wk[w][bucket(r["channel"], r.get("source"))] += r["sessions"]
        keys = ["Google", "Yahoo", "Bing", "AI（ChatGPT等）", "Direct"]
        print("\n週次（月曜始）")
        print("week       " + "".join(f"{k:>16}" for k in keys))
        for w in sorted(wk):
            print(f"{w}  " + "".join(f"{wk[w][k]:>16}" for k in keys))

if __name__ == "__main__":
    main()

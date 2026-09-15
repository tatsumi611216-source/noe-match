# -*- coding: utf-8 -*-
"""SEO Rank Watch の計測器（2026-09-16 新設）

監視キーワード（agent/seo/watchwords.json）の順位を、GSC日別アーカイブ
（agent/gsc_archive/*.json・gsc-archive.yml が毎日追記）から集計して表示する。
改善の選定・判定は .claude/skills/seo-rank-watch/SKILL.md の手順で人（Claude）が行う。

なぜAPIを直接叩かないか:
アーカイブは日別×クエリ×ページの粒度で全期間そろっているので、7日・28日の窓を
あとから何度でも切り直せる。鍵が無い環境（クラウドのセッション）でも同じ数字が出る。
アーカイブが古いときだけ --refresh で gsc_archive.py（鍵が要る）を先に回す。

順位の出し方:
  対象ページの行だけを取り、表示回数で重み付けした平均掲載順位。
  GSC画面の「クエリ×ページ」フィルタと同じ見方。別ページに表示が出ていれば others に並べる
  （カニバリの検知用。順位の計算には混ぜない）。

使い方:
  python scripts/seo_rank_watch.py                    # 28日窓で全監視語の状況・選定順・レビュー判定
  python scripts/seo_rank_watch.py --days 7           # 効果判定用の7日窓
  python scripts/seo_rank_watch.py --append           # 28日窓と7日窓を rank-history.json に追記
  python scripts/seo_rank_watch.py --candidates       # 未登録の有望クエリ（20位以内・表示あり）
  python scripts/seo_rank_watch.py --refresh          # 先にGSCアーカイブを差分更新
  python scripts/seo_rank_watch.py --repo <PATH>      # 別の場所のリポジトリを対象にする
"""
import argparse
import datetime
import glob
import io
import json
import os
import subprocess
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SITE = "https://www.noe-match.com"
STALE_DAYS = 7          # アーカイブ最終日が今日からこれ以上古ければ警告（通常でも4〜5日遅れ）
MIN_JUDGE_IMP = 5       # 判定窓の表示回数がこれ未満なら「判定不能」と表示する

# 掲載順位ごとのクリック率の目安（一般的な公開調査の丸め値。自社データは少なすぎて曲線が引けない）。
# 選定の並べ替えにだけ使う。見込みクリックを報告で「予測」として断定しないこと。
CTR_CURVE = [0.28, 0.15, 0.10, 0.07, 0.05, 0.04, 0.03, 0.025, 0.02, 0.018]


def ctr_at(rank):
    if rank is None:
        return 0.0
    r = max(1, round(rank))
    if r <= 10:
        return CTR_CURVE[r - 1]
    return 0.01 if r <= 20 else 0.005


def score_of(ww, m):
    """選定スコア = 1位になったときの見込みクリック増（28日） × 受け皿係数（1 + 受け皿単価/5000円）。
    単価は成果額であって売上ではない（承認率が案件で違う）ので、係数は緩くしてある。"""
    gain = m["impressions"] * (ctr_at(1) - ctr_at(m["rank"])) if m["rank"] else 0.0
    coef = 1 + ww.get("ctaYen", 0) / 5000
    return round(gain, 1), round(gain * coef, 1)


def norm_query(q):
    return " ".join(q.replace("　", " ").lower().split())


def to_path(url):
    p = url.replace(SITE, "").split("#")[0].split("?")[0]
    return p if p.startswith("/") else "/" + p


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_archive(repo, days):
    files = sorted(glob.glob(os.path.join(repo, "agent", "gsc_archive", "*.json")))
    if not files:
        sys.exit("ERROR: agent/gsc_archive が空。python scripts/gsc_archive.py を先に実行する")
    last = datetime.date.fromisoformat(os.path.basename(files[-1])[:10])
    start = last - datetime.timedelta(days=days - 1)
    rows = []
    for fp in files:
        d = datetime.date.fromisoformat(os.path.basename(fp)[:10])
        if d < start:
            continue
        with open(fp, encoding="utf-8") as f:
            rows.extend(json.load(f).get("by_query_page", []))
    return {"start": start.isoformat(), "end": last.isoformat(), "days": days}, rows


def aggregate(rows):
    """(query, path) -> {imp, clicks, pos(表示重み付き平均)}"""
    acc = {}
    for r in rows:
        key = (norm_query(r["q"]), to_path(r["p"]))
        a = acc.setdefault(key, {"imp": 0, "clicks": 0, "posw": 0.0})
        a["imp"] += r["imp"]
        a["clicks"] += r["clicks"]
        a["posw"] += r["pos"] * r["imp"]
    for a in acc.values():
        a["pos"] = round(a["posw"] / a["imp"], 1) if a["imp"] else None
        del a["posw"]
    return acc


def measure(ww, acc):
    kw = norm_query(ww["keyword"])
    target = ww["targetPath"]
    hit = acc.get((kw, target), {"imp": 0, "clicks": 0, "pos": None})
    others = sorted(
        [{"path": p, "rank": v["pos"], "impressions": v["imp"]}
         for (q, p), v in acc.items() if q == kw and p != target],
        key=lambda o: -o["impressions"])
    return {"rank": hit["pos"], "impressions": hit["imp"], "clicks": hit["clicks"], "others": others[:3]}


def prev_rank(history, keyword, target, days, before_end):
    past = [h for h in history
            if h["keyword"] == keyword and h["targetPath"] == target
            and h["window"]["days"] == days and h["window"]["end"] < before_end]
    return past[-1] if past else None


def fmt(v):
    return "-" if v is None else str(v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--days", type=int, default=28)
    ap.add_argument("--append", action="store_true", help="28日窓と7日窓を rank-history.json に追記")
    ap.add_argument("--candidates", action="store_true")
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()
    repo = os.path.abspath(args.repo)
    seo = os.path.join(repo, "agent", "seo")

    if args.refresh:
        subprocess.run([sys.executable, os.path.join(repo, "scripts", "gsc_archive.py")], check=False)

    watch = load_json(os.path.join(seo, "watchwords.json"), {"keywords": []})["keywords"]
    hist_path = os.path.join(seo, "rank-history.json")
    history = load_json(hist_path, {"entries": []})
    log_doc = load_json(os.path.join(seo, "improvement-log.json"), {"items": []})
    log = log_doc["items"]
    status_of = {(i["keyword"], i["targetPath"]): i for i in log}
    today = datetime.date.today()
    locked = {l["path"]: l["until"] for l in log_doc.get("locks", []) if l["until"] >= today.isoformat()}
    observing_paths = {i["targetPath"] for i in log if i.get("status") == "observing"}

    # 28日窓＝状況と選定、7日窓＝効果判定、14日窓＝7日窓で表示が足りないときの判定。
    windows = sorted({28, 14, 7, args.days}, reverse=True)
    results = {}
    for days in windows:
        win, rows = load_archive(repo, days)
        acc = aggregate(rows)
        results[days] = (win, acc, [(ww, measure(ww, acc)) for ww in watch])

    win, acc, measured = results[28 if args.append else args.days]
    lag = (today - datetime.date.fromisoformat(win["end"])).days
    print(f"GSCアーカイブ {win['start']}〜{win['end']}（{win['days']}日窓・今日から{lag}日遅れ）")
    if lag >= STALE_DAYS:
        print(f"⚠ アーカイブが{lag}日古い。gsc-archive.yml の実行状況を確認するか --refresh を付ける")

    def status_label(ww):
        status = status_of.get((ww["keyword"], ww["targetPath"]), {}).get("status", "active")
        if status == "active" and ww["targetPath"] in locked:
            return f"locked〜{locked[ww['targetPath']]}"
        if status == "active" and ww["targetPath"] in observing_paths:
            return "active(同ページ観察中)"
        return status

    print("\n## 監視キーワード")
    print("| keyword | target | status | rank | 前回 | 差 | imp | clk | 次回review | 他ページ |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for ww, m in measured:
        item = status_of.get((ww["keyword"], ww["targetPath"]), {})
        pv = prev_rank(history["entries"], ww["keyword"], ww["targetPath"], win["days"], win["end"])
        delta = round(pv["rank"] - m["rank"], 1) if pv and pv["rank"] and m["rank"] else None
        others = " ".join(f"{o['path']}({o['rank']}/{o['impressions']})" for o in m["others"])
        print(f"| {ww['keyword']} | {ww['targetPath']} | {status_label(ww)} | {fmt(m['rank'])} "
              f"| {fmt(pv['rank'] if pv else None)} | {fmt(delta)} | {m['impressions']} | {m['clicks']} "
              f"| {item.get('nextReviewDate', '-')} | {others} |")

    # 選定順: 28日窓で2〜20位の active 語を、見込みクリック増×受け皿係数の降順に並べる。
    ranked = []
    for ww, m in results[28][2]:
        if status_label(ww) != "active" or not m["rank"] or not (1.5 <= m["rank"] <= 20):
            continue
        gain, score = score_of(ww, m)
        ranked.append((score, gain, ww, m))
    ranked.sort(key=lambda x: -x[0])
    print("\n## 選定順（28日窓・2〜20位・active のみ。スコア＝1位時の見込みクリック増×(1+受け皿単価/5000)）")
    print("| # | keyword | target | rank | imp | 見込み増/28日 | 受け皿単価 | スコア |")
    print("|---|---|---|---|---|---|---|---|")
    for n, (score, gain, ww, m) in enumerate(ranked, 1):
        print(f"| {n} | {ww['keyword']} | {ww['targetPath']} | {m['rank']} | {m['impressions']} | {gain} "
              f"| {ww.get('ctaYen', 0):,}円 | {score} |")
    if not ranked:
        print("候補なし（改善しない）")

    # 施策の効果は「施策日の翌日以降だけで7日」そろって初めて測れる。GSCは4〜5日遅れるので、
    # nextReviewDate（施策日+7）の時点ではまだ窓の大半が施策前になる。そこで判定は窓の開始日で縛る。
    # 7日窓で表示が足りなければ、施策後だけで14日そろった時点の14日窓で読む。
    def by_key(days):
        return {(ww["keyword"], ww["targetPath"]): m for ww, m in results[days][2]}
    w7, w14 = results[7][0], results[14][0]
    m7, m14 = by_key(7), by_key(14)
    due = [i for i in log if i.get("status") == "observing" and i.get("nextReviewDate", "9999") <= today.isoformat()]
    print(f"\n## レビュー期日到来（observing かつ nextReviewDate <= 今日）7日窓 {w7['start']}〜{w7['end']} / 14日窓 {w14['start']}〜")
    if not due:
        print("なし")
    for i in due:
        key = (i["keyword"], i["targetPath"])
        last = i["actions"][-1] if i.get("actions") else {}
        head = f"- {i['keyword']} {i['targetPath']}: 施策時 {fmt(last.get('rankAtAction'))}"
        if last.get("date", "") >= w7["start"]:
            ready = (datetime.date.fromisoformat(last["date"]) + datetime.timedelta(days=7)).isoformat()
            print(f"{head} → データ待ち（施策 {last['date']}・アーカイブ末日が {ready} 以降になったら判定）")
            continue
        m = m7.get(key, {})
        if m.get("impressions", 0) >= MIN_JUDGE_IMP:
            print(f"{head} → 7日窓 {fmt(m.get('rank'))} / imp {m['impressions']} clk {m['clicks']}（判定可・7日窓）")
            continue
        if last.get("date", "") >= w14["start"]:
            ready = (datetime.date.fromisoformat(last["date"]) + datetime.timedelta(days=14)).isoformat()
            print(f"{head} → 7日窓は表示{m.get('impressions', 0)}で不足。14日窓待ち（アーカイブ末日が {ready} 以降）")
            continue
        m = m14.get(key, {})
        if m.get("impressions", 0) >= MIN_JUDGE_IMP:
            print(f"{head} → 14日窓 {fmt(m.get('rank'))} / imp {m['impressions']} clk {m['clicks']}（判定可・14日窓）")
        else:
            print(f"{head} → 14日窓でも表示{m.get('impressions', 0)}で不足（判定不能→active に戻す）")

    if args.candidates:
        registered = {norm_query(k) for w in watch for k in [w["keyword"], *w.get("variants", [])]}
        cands = [(q, p, v) for (q, p), v in acc.items()
                 if q not in registered and v["pos"] and v["pos"] <= 20 and v["imp"] >= 3]
        cands.sort(key=lambda c: (c[2]["pos"] > 10, -c[2]["imp"], c[2]["pos"]))
        print("\n## 未登録の有望クエリ（20位以内・表示3以上）")
        print("| query | page | rank | imp | clk |")
        print("|---|---|---|---|---|")
        for q, p, v in cands[:25]:
            print(f"| {q} | {p} | {v['pos']} | {v['imp']} | {v['clicks']} |")

    if args.append:
        seen = {(h["keyword"], h["targetPath"], h["window"]["end"], h["window"]["days"]) for h in history["entries"]}
        added = 0
        for days in (28, 7):
            w, _, ms = results[days]
            for ww, m in ms:
                key = (ww["keyword"], ww["targetPath"], w["end"], days)
                if key in seen:
                    continue
                history["entries"].append({
                    "measuredOn": today.isoformat(), "keyword": ww["keyword"], "targetPath": ww["targetPath"],
                    "source": "gsc-archive", "window": w, "rank": m["rank"],
                    "impressions": m["impressions"], "clicks": m["clicks"], "others": m["others"]})
                added += 1
        with open(hist_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=1)
        print(f"\nrank-history.json に {added} 件追記（同じ窓の既存行はスキップ・過去行は書き換えない）")


if __name__ == "__main__":
    main()

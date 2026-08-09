#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""インデックス状態の変化を、事前登録した実験の枠に当てて読む。

なぜ必要か（2026-08-09）：
`index_check.py --report` は「今どうなっているか」しか出さない。
だが今回知りたいのは「申請が効いたのか」であって、そのためには
**申請前（2026-08-01）と今を比べ、申請した群と申請していない群で差が出たか**を
見なければならない。全体が増えていても、申請していない群も同じだけ増えていれば、
それは申請の効果ではなく時間の効果である。

このスクリプトは agent/index_request_batches.md と agent/index_experiment.md を
**唯一の情報源**として群を組み立てる。手でリストを二重管理すると必ずずれる。

使い方:
    python3 scripts/index_diff.py                 # 既定の baseline と最新を比較
    python3 scripts/index_diff.py --baseline agent/index_baseline_20260801.json
    python3 scripts/index_diff.py --current  agent/index_status.json

前提: `python scripts/index_check.py --refresh` を先に回して
      agent/index_status.json を最新にしておくこと。
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

from index_check import classify, INDEXED_KINDS  # noqa: E402
from silent_scan import tier_of, TIER_ORDER  # noqa: E402

BASELINE = os.path.join(ROOT, "agent", "index_baseline_20260801.json")
CURRENT = os.path.join(ROOT, "agent", "index_status.json")
BATCHES = os.path.join(ROOT, "agent", "index_request_batches.md")
EXPERIMENT = os.path.join(ROOT, "agent", "index_experiment.md")
DONE = os.path.join(ROOT, "agent", "index_requests_done.json")

URL_RE = re.compile(r"https://www\.noe-match\.com/articles/[a-z0-9-]+/")


def slug(url):
    return url.rstrip("/").rsplit("/", 1)[-1]


# ------------------------------------------------------------------ 群の構成

def parse_batches():
    """index_request_batches.md の `### Day N` 見出しごとにURLを集める。"""
    if not os.path.exists(BATCHES):
        return OrderedDict()
    text = open(BATCHES, encoding="utf-8").read()
    days = OrderedDict()
    parts = re.split(r"^### Day (\d+)\s*$", text, flags=re.M)
    # parts = [前置き, "1", 本文, "2", 本文, ...]
    for i in range(1, len(parts) - 1, 2):
        days[int(parts[i])] = [slug(u) for u in URL_RE.findall(parts[i + 1])]
    return days


def parse_day0():
    """Day 0（2026-08-01 に実施済みの10本）は index_experiment.md 側にある。"""
    if not os.path.exists(EXPERIMENT):
        return []
    text = open(EXPERIMENT, encoding="utf-8").read()
    return [slug(u) for u in URL_RE.findall(text)]


def parse_note_group():
    """note専用テスト群。**Google申請してはいけない5本**。"""
    if not os.path.exists(BATCHES):
        return []
    text = open(BATCHES, encoding="utf-8").read()
    m = re.search(r"note専用テスト群.*?```\n(.*?)```", text, flags=re.S)
    if not m:
        return []
    return [l.strip() for l in m.group(1).splitlines() if l.strip()]


def executed_days():
    """実際に申請を出した Day の番号。人間の報告を agent/index_requests_done.json に記録する。

    ここが空だと「申請済み群」が作れず、比較そのものが成り立たない。
    憶測で埋めないこと。実施の確認が取れた日だけを入れる。
    """
    if not os.path.exists(DONE):
        return None
    d = json.load(open(DONE, encoding="utf-8"))
    return d.get("days", {})


# ------------------------------------------------------------------ 読み込み

def load(path):
    if not os.path.exists(path):
        sys.exit("見つからない: %s" % path)
    d = json.load(open(path, encoding="utf-8"))
    kinds = {}
    for url, entry in d["results"].items():
        if entry.get("error"):
            continue
        kinds[slug(url)] = classify(entry)[0]
    return d.get("fetched_at", "?"), kinds


def rate(kinds, slugs):
    """対象スラッグのうち、両スナップショットで検査できたものだけを分母にする。"""
    seen = [s for s in slugs if s in kinds]
    hit = [s for s in seen if kinds[s] in INDEXED_KINDS]
    return len(hit), len(seen)


def pct(a, b):
    return "%5.1f%%" % (100.0 * a / b) if b else "    -"


# ------------------------------------------------------------------ 出力

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline", default=BASELINE)
    ap.add_argument("--current", default=CURRENT)
    args = ap.parse_args()

    b_at, before = load(args.baseline)
    c_at, after = load(args.current)
    stale = b_at == c_at
    if stale:
        print("!! baseline と current の取得時刻が同じ（%s）。" % b_at)
        print("   比較する対象が無いので、判定は出さない。")
        print("   先に `python scripts/index_check.py --refresh` を回すこと。\n")

    common = sorted(set(before) & set(after))
    print("=" * 72)
    print("インデックス状態の変化   %s → %s   （両方で検査できた %d本）"
          % (b_at[:10], c_at[:10], len(common)))
    print("=" * 72)

    # ---- 1. 全体
    print("\n■ 全体の内訳")
    kb, kc = Counter(before[s] for s in common), Counter(after[s] for s in common)
    for kind in sorted(set(kb) | set(kc), key=lambda k: -kc.get(k, 0)):
        d = kc.get(kind, 0) - kb.get(kind, 0)
        print("   %-14s %3d → %3d   %+d" % (kind, kb.get(kind, 0), kc.get(kind, 0), d))
    ib, nb = rate(before, common)
    ic, nc = rate(after, common)
    print("   %-14s %s → %s" % ("インデックス率", pct(ib, nb), pct(ic, nc)))

    # ---- 2. 遷移
    print("\n■ 遷移（変化があったものだけ）")
    moves = Counter((before[s], after[s]) for s in common if before[s] != after[s])
    if not moves:
        print("   変化なし")
    for (a, b), n in moves.most_common():
        print("   %-14s → %-14s %3d本" % (a, b, n))

    gained = sorted(s for s in common
                    if before[s] not in INDEXED_KINDS and after[s] in INDEXED_KINDS)
    lost = sorted(s for s in common
                  if before[s] in INDEXED_KINDS and after[s] not in INDEXED_KINDS)
    print("\n   新たにインデックスされた: %d本" % len(gained))
    print("   インデックスから外れた  : %d本%s"
          % (len(lost), ("  → " + ", ".join(lost)) if lost else ""))

    # ---- 3. 群別（ここが本題）
    days = parse_batches()
    day0 = parse_day0()
    note = parse_note_group()
    done = executed_days()

    print("\n" + "=" * 72)
    print("■ 群別：申請した群としていない群で差が出たか")
    print("=" * 72)

    if done is None:
        print("\n!! agent/index_requests_done.json が無い。")
        print("   どの Day まで実際に申請したかが分からないと、この比較は成り立たない。")
        print('   例: {"days": {"0": "2026-08-01", "1": "2026-08-02", "2": "2026-08-08"}}')
        done = {}

    requested, pending = set(), set()
    rows = []
    groups = [(0, day0)] + list(days.items())
    for n, slugs in groups:
        key = str(n)
        did = key in done
        (requested if did else pending).update(slugs)
        rows.append((n, did, done.get(key, ""), slugs))

    note_set = set(note)
    requested -= note_set
    pending -= note_set
    control = [s for s in common if s not in requested and s not in pending
               and s not in note_set]

    print("\n%-22s %-12s %10s %10s %8s" % ("群", "申請日", "申請前", "現在", "増加"))
    print("-" * 72)
    for n, did, when, slugs in rows:
        ib_, nb_ = rate(before, slugs)
        ic_, nc_ = rate(after, slugs)
        label = "Day %d（%d本）" % (n, len(slugs))
        print("%-22s %-12s %s %s %8s"
              % (label, when if did else "未実施", pct(ib_, nb_), pct(ic_, nc_),
                 "%+d" % (ic_ - ib_)))
    print("-" * 72)

    for label, slugs, note_txt in (
        ("申請済み 合計", sorted(requested), ""),
        ("申請待ち 合計", sorted(pending), "← 申請の効果を見る対照群"),
        ("note専用テスト群", note, "← 申請禁止。noteの効果を見る"),
        ("その他（既存インデックス等）", control, ""),
    ):
        ib_, nb_ = rate(before, slugs)
        ic_, nc_ = rate(after, slugs)
        print("%-22s %-12s %s %s %8s  %s"
              % (label, "%d本" % len(slugs), pct(ib_, nb_), pct(ic_, nc_),
                 "%+d" % (ic_ - ib_), note_txt))

    # ---- 4. 事前登録した判定
    print("\n" + "=" * 72)
    print("■ 事前登録した判定表への当てはめ")
    print("=" * 72)
    r_hit, r_n = rate(after, sorted(requested))
    r_hit0, _ = rate(before, sorted(requested))
    p_hit, p_n = rate(after, sorted(pending))
    p_hit0, _ = rate(before, sorted(pending))
    r_gain = (100.0 * (r_hit - r_hit0) / r_n) if r_n else 0.0
    p_gain = (100.0 * (p_hit - p_hit0) / p_n) if p_n else 0.0
    print("\n   申請済み群の伸び : %+.1f ポイント（%d本中 %+d本）" % (r_gain, r_n, r_hit - r_hit0))
    print("   申請待ち群の伸び : %+.1f ポイント（%d本中 %+d本）" % (p_gain, p_n, p_hit - p_hit0))
    diff = r_gain - p_gain
    print("   差               : %+.1f ポイント" % diff)
    if stale:
        print("\n   → 判定は保留。同じスナップショットを比べているだけなので、"
              "ここに意味のある差は出ない。")
    elif r_n and p_n:
        if diff >= 20:
            print("\n   → **申請は効いている。**行列の問題は順番待ちであって品質評価ではない。")
            print("      残りの Day を最後まで消化する価値がある。")
        elif diff <= 5:
            print("\n   → **申請では動いていない。**申請待ち群も同じだけ伸びており、"
                  "時間の効果と区別できない。")
            print("      需要側（外部評価）の打ち手に軸足を移すこと。")
        else:
            print("\n   → どちらとも言えない。申請を最後まで消化してから再判定する。")

    n_hit, n_n = rate(after, note)
    n_hit0, _ = rate(before, note)
    print("\n   note専用テスト群 : %d本中 %+d本（%s → %s）"
          % (n_n, n_hit - n_hit0, pct(n_hit0, n_n), pct(n_hit, n_n)))
    if n_n and not stale:
        if n_hit - n_hit0 > 0:
            print("      → **noteはクロール需要を動かす。**申請していないのに入った。"
                  "SNS投資の判断根拠になる")
        else:
            print("      → 現時点では動いていない。予約投稿の公開日から日が浅い可能性があるので、"
                  "次回も追うこと")

    # ---- 5. クエリ型別
    print("\n" + "=" * 72)
    print("■ クエリ型別（ヘッドタームだけ落ちているかの確認）")
    print("=" * 72)
    print("\n%-22s %10s %10s %8s" % ("型", "申請前", "現在", "増加"))
    print("-" * 56)
    for tier in TIER_ORDER:
        slugs = [s for s in common if tier_of(s) == tier]
        ib_, nb_ = rate(before, slugs)
        ic_, nc_ = rate(after, slugs)
        print("%-22s %s %s %8s  (%d本)"
              % (tier, pct(ib_, nb_), pct(ic_, nc_), "%+d" % (ic_ - ib_), nc_))

    print("\n※ 増えていても、申請待ち群が同じだけ増えていれば申請の効果ではない。"
          "必ず上の「差」を見ること。")


if __name__ == "__main__":
    main()

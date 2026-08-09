#!/usr/bin/env python3
"""
期待値歪みフィルター (ev_distortion_filter.py)
================================================
出馬表データを受け取り、「期待値歪みスコア」を計算して
高期待値レースのみを通過させるフィルター。

使い方:
  # 単一レース
  python3 scripts/ev_distortion_filter.py race_202305010101.json

  # 複数レース一括
  python3 scripts/ev_distortion_filter.py race1.json race2.json race3.json

  # stdin からパイプ（calc_ev.py と連携）
  python3 scripts/calc_ev.py race*.json | python3 scripts/ev_distortion_filter.py --stdin

  # テスト実行（ダミーデータ）
  python3 scripts/ev_distortion_filter.py --test
"""

import json
import sys
import os
import re
from datetime import date


# ── スコアリングルール定義 ────────────────────────────────────────

FILTER_RULES = [
    # (条件名, 点数, 判定関数)
    ("少頭数",          2, lambda r: r.get("field_size", 99) <= 12),
    ("乗り替わり",      2, lambda r: any(
        h.get("prev_jockey") and h.get("jockey") != h.get("prev_jockey")
        for h in r.get("horses", [])
    )),
    ("馬場変化",        1, lambda r: any(
        h.get("prev_track_condition")
        and h.get("prev_track_condition") != r.get("track_condition")
        for h in r.get("horses", [])
    )),
    ("距離変化",        1, lambda r: _has_dist_change(r)),
    ("1番人気オッズ",   2, lambda r: _fav_odds_check(r)),
    ("条件戦クラス",    1, lambda r: any(
        kw in r.get("race_name", "")
        for kw in ["未勝利", "条件", "1勝", "2勝"]
    )),
]

PASS_THRESHOLD = 3  # 3点以上で通過


def _parse_dist_num(dist_str: str) -> int:
    """'芝1600' / 'ダ1200' → 1600 / 1200"""
    m = re.search(r'\d+', str(dist_str))
    return int(m.group()) if m else 0


def _has_dist_change(race: dict) -> bool:
    """レース距離と各馬の直前出走距離の差が200m以上の馬がいるか"""
    race_dist = _parse_dist_num(race.get("dist", ""))
    if race_dist == 0:
        return False
    for h in race.get("horses", []):
        prev = h.get("prev_dist")
        if prev and abs(race_dist - int(prev)) >= 200:
            return True
    return False


def _fav_odds_check(race: dict) -> bool:
    """umaban=='1' の馬の単勝オッズが3.5以上なら True（1番人気が飛ぶ可能性）"""
    for h in race.get("horses", []):
        if str(h.get("umaban", "")) == "1":
            return float(h.get("win_odds") or 0) >= 3.5
    return False


# ── prev_* フィールドを results[0] から補完 ───────────────────────

def enrich_prev_fields(race: dict) -> dict:
    """
    horses[].prev_jockey / prev_dist / prev_track_condition が未設定の場合、
    results[0]（直近1走）から補完する。
    parse_horse_results.py の出力形式に対応。
    """
    for h in race.get("horses", []):
        results = h.get("results", [])
        if not results:
            continue
        latest = results[0]
        if not h.get("prev_jockey"):
            h["prev_jockey"] = latest.get("jockey", "")
        if not h.get("prev_dist"):
            # parse_horse_results は "distance" フィールドで数値を返す
            h["prev_dist"] = latest.get("prev_dist") or latest.get("distance")
        if not h.get("prev_track_condition"):
            # parse_horse_results は "track" フィールドで "ダ"/"芝" を返す
            h["prev_track_condition"] = (
                latest.get("track_condition")
                or latest.get("track", "")
            )
    return race


# ── 1レース評価 ──────────────────────────────────────────────────

def evaluate_race(race: dict) -> dict:
    """
    レースデータを受け取り、各条件の充足・スコア・通過判定を返す。
    """
    race = enrich_prev_fields(race)

    conditions = {}
    total_score = 0

    for name, points, func in FILTER_RULES:
        try:
            met = bool(func(race))
        except Exception:
            met = False
        conditions[name] = met
        if met:
            total_score += points

    passed = total_score >= PASS_THRESHOLD

    return {
        "race_id":    race.get("race_id", "unknown"),
        "race_name":  race.get("race_name", ""),
        "dist":       race.get("dist", ""),
        "field_size": race.get("field_size"),
        "score":      total_score,
        "passed":     passed,
        "conditions": conditions,
    }


# ── 表示 ─────────────────────────────────────────────────────────

def print_results(results: list):
    header = (
        f"{'race_id':<16} | {'スコア':^5} | {'通過':^4} | "
        f"{'少頭数':^4} | {'乗替':^4} | {'馬場':^4} | {'距離':^4} | {'人気':^4} | {'条件戦':^5}"
    )
    sep = "-" * 90

    print("\n=== 歪みフィルター結果 ===")
    print(header)
    print(sep)

    for r in results:
        c = r["conditions"]
        passed_mark = "✅" if r["passed"] else "❌"
        row = (
            f"{r['race_id']:<16} | "
            f" {r['score']}点   | "
            f"  {passed_mark}  | "
            f"  {'✅' if c.get('少頭数')        else '-'}   | "
            f"  {'✅' if c.get('乗り替わり')    else '-'}   | "
            f"  {'✅' if c.get('馬場変化')      else '-'}   | "
            f"  {'✅' if c.get('距離変化')      else '-'}   | "
            f"  {'✅' if c.get('1番人気オッズ') else '-'}   | "
            f"  {'✅' if c.get('条件戦クラス')  else '-'}"
        )
        print(row)

    passed_count = sum(1 for r in results if r["passed"])
    print(sep)
    print(f"通過レース: {passed_count}件 / {len(results)}件\n")


def save_json(results: list) -> str:
    today = date.today().strftime("%Y%m%d")
    out_path = f"{today}_filter_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return out_path


# ── テストデータ ─────────────────────────────────────────────────

TEST_RACES = [
    {
        "race_id":         "202305010101",
        "race_name":       "3歳未勝利",
        "dist":            "芝1600",
        "field_size":      10,
        "track_condition": "良",
        "horses": [
            {
                "umaban":               "1",
                "name":                 "テスト馬A",
                "horse_id":             "2021100001",
                "win_odds":             4.5,
                "jockey":               "川田将雅",
                "prev_jockey":          "福永祐一",  # 乗り替わり
                "prev_dist":            1400,        # 距離変化 +200
                "prev_track_condition": "重",        # 馬場変化
                "results":              [],
            },
            {
                "umaban":               "2",
                "name":                 "テスト馬B",
                "horse_id":             "2021100002",
                "win_odds":             8.0,
                "jockey":               "武豊",
                "prev_jockey":          "武豊",
                "prev_dist":            1600,
                "prev_track_condition": "良",
                "results":              [],
            },
        ],
    },
    {
        "race_id":         "202305010102",
        "race_name":       "4歳以上2勝クラス",
        "dist":            "ダ1200",
        "field_size":      15,
        "track_condition": "稍重",
        "horses": [
            {
                "umaban":               "1",
                "name":                 "テスト馬C",
                "horse_id":             "2020100001",
                "win_odds":             2.1,
                "jockey":               "岩田康誠",
                "prev_jockey":          "岩田望来",  # 乗り替わり
                "prev_dist":            1200,
                "prev_track_condition": "稍重",
                "results":              [],
            },
        ],
    },
    {
        "race_id":         "202305010103",
        "race_name":       "5歳以上オープン",
        "dist":            "芝2000",
        "field_size":      16,
        "track_condition": "良",
        "horses": [
            {
                "umaban":               "1",
                "name":                 "テスト馬D",
                "horse_id":             "2019100001",
                "win_odds":             2.5,
                "jockey":               "松山弘平",
                "prev_jockey":          "松山弘平",
                "prev_dist":            2000,
                "prev_track_condition": "良",
                "results":              [],
            },
        ],
    },
]


# ── メイン ───────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    # --test モード
    if "--test" in args:
        print("【テストモード】ダミーデータ3レースを評価します\n")
        results = [evaluate_race(r) for r in TEST_RACES]
        print_results(results)
        out = save_json(results)
        print(f"→ JSON保存: {out}")
        return

    # --stdin モード（パイプ入力）
    if "--stdin" in args:
        raw = sys.stdin.read().strip()
        races = []
        try:
            data = json.loads(raw)
            if isinstance(data, list):
                races = data
            elif isinstance(data, dict):
                races = [data]
        except json.JSONDecodeError:
            # 複数の独立JSONオブジェクトをデコード
            decoder = json.JSONDecoder()
            pos = 0
            while pos < len(raw):
                try:
                    obj, idx = decoder.raw_decode(raw, pos)
                    if isinstance(obj, list):
                        races.extend(obj)
                    elif isinstance(obj, dict):
                        races.append(obj)
                    pos = idx
                    raw = raw[pos:].lstrip()
                    pos = 0
                except json.JSONDecodeError:
                    break

        if not races:
            print("⚠️  stdin からレースデータを読み取れませんでした", file=sys.stderr)
            sys.exit(1)

        results = [evaluate_race(r) for r in races]
        print_results(results)
        out = save_json(results)
        print(f"→ JSON保存: {out}")
        return

    # ファイル指定モード
    if not args:
        print("使い方: python3 scripts/ev_distortion_filter.py <race.json> [race2.json ...]")
        print("        python3 scripts/ev_distortion_filter.py --test")
        print("        python3 scripts/ev_distortion_filter.py --stdin")
        sys.exit(1)

    results = []
    for filepath in args:
        if not os.path.exists(filepath):
            print(f"⚠️  ファイルが見つかりません: {filepath}", file=sys.stderr)
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            race_data = json.load(f)
        if isinstance(race_data, list):
            for r in race_data:
                results.append(evaluate_race(r))
        else:
            results.append(evaluate_race(race_data))

    if not results:
        print("評価対象のレースがありませんでした", file=sys.stderr)
        sys.exit(1)

    print_results(results)
    out = save_json(results)
    print(f"→ JSON保存: {out}")


if __name__ == "__main__":
    main()

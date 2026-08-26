# -*- coding: utf-8 -*-
"""データ記事ゲート（2026-08-27 新設）

なぜ必要か: データ記事は通常記事の5.3倍の実力があるが（30日・direct除きで
1本1.28セッション vs 0.24）、名乗るだけで中身が無ければ通常記事と同じになる。
実際に効いている4本（appkon-wariai-data / success-rate-data / members-data /
kaiin-age-cross-data）に共通するのは「複数の公表値を横断で1枚の表にしてある」こと。

もうひとつの実測: データ記事の流入はAI14＋bing13に対しgoogle/yahooは2しかない。
**Googleの1ページ目は大手が占有していて取れないが、AIとBingは公表値の表を引きに来る。**
したがってデータ記事はGoogle順位ではなく「AIが引用しやすい形」に最適化する。

このゲートが見るのは3点:
  A. 需要      … Googleサジェスト（4件以上を目安。0〜1件は作らない）
  B. 一次データ … 公表元が実在するか（人が確認する。ここは機械化しない）
  C. 横断性    … 1社・1自治体で終わらず、複数を並べられるか

使い方:
  python scripts/data_gate.py "マッチングアプリ 会員数" "産後ケア 何回"
  python scripts/data_gate.py --sweep    （候補リストを一括判定して台帳に書く）
"""
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "agent", "data_candidates.md")
MIN_SUGGESTS = 4

# 自社に一次データがある領域、または公表値を横断で集められる領域に絞る
CANDIDATES = [
    # 婚活・アプリ（既存の勝ちデータ記事と同じ領域。AI/Bingが拾う）
    "マッチングアプリ 会員数", "マッチングアプリ 男女比", "マッチングアプリ 成婚率",
    "マッチングアプリ 年齢層", "マッチングアプリ 料金 比較", "結婚相談所 成婚率",
    "結婚相談所 費用", "婚活パーティー カップル率",
    # 結婚・お金
    "初婚年齢 平均", "結婚式 費用 平均", "結婚 貯金 平均", "共働き 割合",
    "結婚 年収", "生涯未婚率",
    # 産後・育児（自社に43自治体の一次データあり）
    "産後ケア 何回", "産後ケア 助成", "産後ケア 料金", "出産費用 平均",
    "出産育児一時金", "育休 取得率", "育児休業給付金 いくら", "待機児童 数",
    "こども誰でも通園制度 料金", "保育料 平均",
    # 離婚
    "離婚率", "養育費 相場", "母子家庭 手当",
]


def suggests(q):
    url = ("https://suggestqueries.google.com/complete/search?client=firefox&hl=ja&q="
           + urllib.parse.quote(q))
    try:
        d = json.load(urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=15))
        return d[1] if len(d) > 1 else []
    except Exception:
        return None


def judge(q):
    s = suggests(q)
    if s is None:
        return q, None, "取得失敗", []
    n = len(s)
    if n == 0:
        return q, n, "NO-GO", s
    if n < MIN_SUGGESTS:
        return q, n, "CHECK", s
    return q, n, "GO", s


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    sweep = "--sweep" in sys.argv
    words = CANDIDATES if sweep else args
    if not words:
        print(__doc__)
        return

    results = []
    for q in words:
        r = judge(q)
        results.append(r)
        print("[%-6s] %-26s サジェスト%-4s %s"
              % (r[2], r[0], r[1], " / ".join(r[3][:4])))
        time.sleep(0.8)

    if not sweep:
        return

    go = [r for r in results if r[2] == "GO"]
    check = [r for r in results if r[2] == "CHECK"]
    ng = [r for r in results if r[2] == "NO-GO"]
    lines = [
        "# データ記事の候補台帳（自動生成: scripts/data_gate.py --sweep）",
        "",
        "判定基準: Googleサジェスト4件以上をGO、1〜3件をCHECK、0件をNO-GO。",
        "GOでも「一次データが実在するか」「複数を横断で並べられるか」は人が確認する。",
        "データ記事はGoogle順位ではなくAI・Bingの引用を取りに行く型（30日実測: AI14＋bing13 vs google/yahoo2）。",
        "",
        "## GO（作ってよい）", "",
        "| 語 | サジェスト | サジェストの中身 |", "|---|---|---|",
    ]
    for q, n, _, s in sorted(go, key=lambda x: -x[1]):
        lines.append("| %s | %d | %s |" % (q, n, " / ".join(s[:4])))
    lines += ["", "## CHECK（需要が薄い。作るなら他の語と束ねる）", ""]
    for q, n, _, s in check:
        lines.append("- %s（%d件）" % (q, n))
    lines += ["", "## NO-GO（検索されていない。作らない）", ""]
    for q, n, _, s in ng:
        lines.append("- %s" % q)
    io.open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n書き出し: %s（GO %d / CHECK %d / NO-GO %d）"
          % (OUT, len(go), len(check), len(ng)))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

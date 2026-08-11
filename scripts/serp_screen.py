# -*- coding: utf-8 -*-
"""記事を書く前に、狙うクエリに需要があるかを機械的にゲートする。

なぜ必要か（2026-08-09の実測）:

この日、14テーマのSERPを人手で調べて、生き残ったのは1つだけだった。
落ちた13のうち複数は「SERPに記事が1本も無い」状態で、一見すると空白に見えた。
だが実際は **空白ではなく、そもそも検索されていなかった**。

  例: Dark Angel（楽天の年間ランキング上位・レビュー26万件）
      → SERPに解説記事ゼロ。しかし主力商品名の検索ボリュームは測定不能。
      → 楽天内で売れることと、Googleで指名検索されることは別物だった。

**空白には2種類ある。「誰も気づいていない空白」と「誰も書かない理由がある空白」。**
SERPの見た目だけでは区別できない。需要の有無を先に確認する必要がある。

Googleのサジェストは実際の検索量に基づいて出るので、需要の有無のゲートとして使える。
`suggestqueries.google.com` は **認証不要** で叩ける（2026-08-09に確認）。
ただし分かるのは有無だけで、実数は出ない。実数はキーワードプランナーが要る。

使い方:
    python scripts/serp_screen.py "ペット 婚活" "オタク 婚活" "子連れ 再婚"
    python scripts/serp_screen.py --file agent/query_candidates.txt

判定の読み方:
    サジェストなし          → 検索されていない。**書かない**
    サジェストあり・修飾語のみ → 需要はあるが薄い。長尾として検討
    「口コミ」「比較」「おすすめ」等が並ぶ → 購入直前クエリ。**本命**
"""
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ENDPOINT = "https://suggestqueries.google.com/complete/search"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
# 購入・比較の意図を示す語。これが並ぶクエリは成約に近い。
INTENT = ["口コミ", "評判", "比較", "おすすめ", "料金", "費用", "サイズ", "解約", "デメリット", "選び方"]


def suggest(q):
    url = "{}?{}".format(ENDPOINT, urllib.parse.urlencode(
        {"client": "firefox", "hl": "ja", "q": q}))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read().decode("utf-8", errors="replace")
    try:
        return json.loads(raw)[1]
    except Exception:
        return []


def judge(q, items):
    if not items:
        return "書かない", "サジェストなし＝検索されていない"
    hits = [w for w in INTENT if any(w in s for s in items)]
    if hits:
        return "本命", "購入直前の語が出る: {}".format(" / ".join(hits))
    if len(items) >= 5:
        return "検討", "需要はあるが購入意図の語が無い"
    return "弱い", "サジェストが少ない"


def main():
    args = sys.argv[1:]
    if args and args[0] == "--file":
        queries = [l.strip() for l in io.open(args[1], encoding="utf-8") if l.strip() and not l.startswith("#")]
    else:
        queries = args
    if not queries:
        print(__doc__)
        return

    lines = []
    for q in queries:
        try:
            items = suggest(q)
        except Exception as e:
            lines.append("{}\t取得失敗\t{}".format(q, e))
            continue
        verdict, why = judge(q, items)
        lines.append("[{}] {}".format(verdict, q))
        lines.append("    {}".format(why))
        lines.append("    候補: {}".format(" / ".join(items[:8]) if items else "（なし）"))
        lines.append("")
        time.sleep(0.6)

    text = "\n".join(lines)
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "agent", "serp_screen_last.txt")
    io.open(out, "w", encoding="utf-8", newline="").write(text)
    try:
        print(text)
    except UnicodeEncodeError:
        # Windowsのコンソールは既定がCP932なので、出せない字があっても落とさない
        print(text.encode("cp932", errors="replace").decode("cp932"))
    print("\n保存: agent/serp_screen_last.txt")


if __name__ == "__main__":
    main()

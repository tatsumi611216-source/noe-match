# -*- coding: utf-8 -*-
"""サジェストのあいうえお展開で「意図の面積」を測る（2026-08-27 新設）

なぜ必要か:
完全一致フレーズのサジェスト件数は、ボリュームの代理指標になっていないと実証された
（20位以内の20語で検証。4件以上の語は平均8.0表示、3件以下は平均9.7表示で相関なし）。
さらに旧ゲートは自社最強の語「ガルガル期 診断」を完全一致1件でCHECKに落としていた。

Bing Webmaster Tools のキーワード調査で実ボリュームを取ろうとしたが、
2026-08-27 時点で語・言語を問わず "Invalid request" を返して機能していない
（レガシーAPI廃止の告知がバナーに出ている時期と重なる）。
Search Performance も「48時間待て」の状態だった。

そこで**絶対ボリュームは諦め、意図の面積を測る**方針に切り替えた。
これはラッコキーワードの無料機能と同じ処理を自前でやるもので、
頭の語にあ〜ん・a〜zを付けてサジェストを総なめし、
どれだけ独立した問いがぶら下がっているかを見る。

戦略上の根拠:
「表記ゆれを増やしても面積は増えない。独立した検索意図を増やすと増える」
（30s-konkatsu は19語拾って全部同一意図の表記ゆれで45表示・全部60〜99位。
　ガルガル期は5語で異なる意図を拾って76表示）。
このスクリプトが数えるのは、まさにその「独立した意図の数」。

使い方:
  python scripts/keyword_expand.py "産後ケア"
  python scripts/keyword_expand.py "産後ケア" --full   （a-zと数字も回す。遅い）
"""
import collections
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KANA = list("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほ"
            "まみむめもやゆよらりるれろわをん")
ALNUM = list("abcdefghijklmnopqrstuvwxyz0123456789")


def suggests(q):
    url = ("https://suggestqueries.google.com/complete/search?client=firefox&hl=ja&q="
           + urllib.parse.quote(q))
    try:
        d = json.load(urllib.request.urlopen(
            urllib.request.Request(url, headers={"User-Agent": UA}), timeout=15))
        return d[1] if len(d) > 1 else []
    except Exception:
        return []


_GSC = None


def gsc_lookup():
    """自社GSCの実表示を辞書で返す。既に表示が出ている語は表示数がほぼ実ボリューム。"""
    global _GSC
    if _GSC is None:
        _GSC = {}
        try:
            d = json.load(io.open(os.path.join(ROOT, "agent", "gsc_data.json"),
                                  encoding="utf-8"))
            for r in d.get("by_query_page", []):
                cur = _GSC.setdefault(r["query"], {"i": 0, "p": []})
                cur["i"] += r["impressions"]
                cur["p"].append(r["position"])
        except Exception:
            pass
    return _GSC


def expand(head, full=False):
    seen = set()
    prefixes = [""] + KANA + (ALNUM if full else [])
    for i, p in enumerate(prefixes):
        q = head if not p else "%s %s" % (head, p)
        for s in suggests(q):
            if s.startswith(head):
                seen.add(s)
        time.sleep(0.35)
        if (i + 1) % 15 == 0:
            print("   ... %d/%d 走査" % (i + 1, len(prefixes)), file=sys.stderr)
    return sorted(seen)


def second_token(head, phrase):
    """「産後ケア 料金 相場」→「料金」。意図の代表語"""
    rest = phrase[len(head):].strip()
    if not rest:
        return "（頭の語のみ）"
    return re.split(r"[\s　]+", rest)[0]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    full = "--full" in sys.argv
    if not args:
        print(__doc__)
        return
    head = args[0]
    print("■ 「%s」のサジェスト展開%s" % (head, "（a-z・数字も含む）" if full else ""))
    phrases = expand(head, full)
    print("  拾えたフレーズ: %d件" % len(phrases))
    print()

    groups = collections.defaultdict(list)
    for p in phrases:
        groups[second_token(head, p)].append(p)
    gsc = gsc_lookup()

    print("■ 独立した意図（2語目でまとめた）: %d種" % len(groups))
    print("  %-14s %4s  %s" % ("意図", "語数", "例／自社GSCの実表示"))
    for k, v in sorted(groups.items(), key=lambda x: -len(x[1])):
        hit = [(p, gsc[p]) for p in v if p in gsc]
        note = ""
        if hit:
            best = max(hit, key=lambda x: x[1]["i"])
            note = "  ← 自社 %d表示（%.1f位）: %s" % (
                best[1]["i"], sum(best[1]["p"]) / len(best[1]["p"]), best[0])
        print("  %-14s %4d  %s%s" % (k, len(v), v[0][:34], note))
    print()

    covered = [p for p in phrases if p in gsc]
    print("■ 自社が既に表示を取れているフレーズ: %d / %d" % (len(covered), len(phrases)))
    for p in sorted(covered, key=lambda x: -gsc[x]["i"])[:10]:
        v = gsc[p]
        print("    %4d表示 %5.1f位  %s" % (v["i"], sum(v["p"]) / len(v["p"]), p))
    print()
    print("■ 読み方")
    print("  ・意図の種類が多いほど、1つのデータバンクから出せる面が多い")
    print("  ・自社GSCに出ているフレーズは、その表示数がほぼ実ボリューム（1〜2ページ目にいる場合）")
    print("  ・絶対ボリュームは測れない。必要ならキーワードプランナー等の外部ツールが要る")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

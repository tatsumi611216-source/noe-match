#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai_smell.py — 台本の「AIっぽさ」を機械検出する。

依存ライブラリなし。python3 だけで動く。

  python3 tools/ai_smell.py draft/script.md
  python3 tools/ai_smell.py draft/script.md --verbose

検出するもの:
  1. AI特有の言い回し（禁止表現）
  2. 一文が長すぎる箇所
  3. 文長が均一すぎる（人間は長短がばらつく）
  4. 語尾の連続（同じ終わり方が続く）
  5. 体言止めの多用
  6. 三点セット列挙
  7. 具体性の欠如（数字・固有名詞の密度）
  8. 章ごとの文字数の均一性
"""

import re
import sys
import statistics
from collections import Counter

# ---------------------------------------------------------------- 禁止表現

# (パターン, 説明, 重み)
NG_PATTERNS = [
    (r"ではないでしょうか", "AI作文の定番。断言に書き換える", 3),
    (r"と言え(る|ます)でしょう", "同上", 3),
    (r"いかがでし(た|ょう)", "締めのテンプレ。即バレする", 5),
    (r"参考になれば", "締めのテンプレ", 4),
    (r"本記事では", "動画台本に書く語ではない", 5),
    (r"この記事で(は|も)", "同上", 4),
    (r"まとめると", "話し言葉なら「つまり」", 2),
    (r"重要です", "何が重要かを具体で言う", 2),
    (r"が求められ(る|ます)", "主語のない硬い言い回し", 3),
    (r"注目され(て|ます)", "誰が注目しているのか不明", 3),
    (r"目覚ましい", "紋切り型", 3),
    (r"近年", "話し言葉では使わない", 3),
    (r"昨今", "同上", 3),
    (r"を活用(する|し|して)", "具体的な動詞に置換", 2),
    (r"実現(する|し|でき)", "抽象名詞。何がどうなるかを書く", 2),
    (r"効率化", "具体的に何分減るのかを書く", 1),
    (r"最大限に", "紋切り型", 2),
    (r"徹底解説", "動画タイトル以外では不要", 2),
    (r"ぜひ.*してみてください", "テンプレCTA", 2),
    (r"様々な", "具体を書け のサイン", 2),
    (r"多岐にわたる", "紋切り型", 3),
    (r"と言っても過言ではありません", "紋切り型", 4),
    (r"驚くべきことに", "紋切り型", 3),
    (r"革新的", "中身がない形容", 3),
    (r"シームレス", "カタカナ抽象語", 2),
    (r"一方で、", "接続詞の機械的使用。多発なら要注意", 1),
    (r"つまり、.*つまり、", "同じ接続詞の反復", 2),
]

# 文末の「動詞・助動詞で終わっている」判定用
VERB_TAIL = "るたすねよいだんうくけばろまでかしせぬむぐずびちりつ"

SENT_SPLIT = re.compile(r"(?<=[。！？])")
HEADING = re.compile(r"^#{1,6}\s*(.+)$")
CODE_FENCE = re.compile(r"^```")


def load(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def strip_noise(text):
    """コードブロックと見出しを除いた本文を返す。"""
    out, in_code = [], False
    for line in text.splitlines():
        if CODE_FENCE.match(line.strip()):
            in_code = not in_code
            continue
        if in_code:
            continue
        if HEADING.match(line):
            continue
        if line.strip().startswith(("|", ">", "-", "*")):
            continue
        out.append(line)
    return "\n".join(out)


def sentences(body):
    res = []
    for raw in SENT_SPLIT.split(body):
        s = raw.strip()
        if len(s) >= 2:
            res.append(s)
    return res


def chapters(text):
    """見出し単位で本文を分割する。"""
    chaps, cur, name = [], [], None
    for line in text.splitlines():
        m = HEADING.match(line)
        if m:
            if name is not None:
                chaps.append((name, "\n".join(cur)))
            name, cur = m.group(1).strip(), []
        else:
            cur.append(line)
    if name is not None:
        chaps.append((name, "\n".join(cur)))
    return chaps


# ---------------------------------------------------------------- 各チェック

def check_ng(body, verbose):
    hits, score = [], 0
    for pat, why, w in NG_PATTERNS:
        for m in re.finditer(pat, body):
            s = max(0, m.start() - 25)
            hits.append((m.group(0), why, w, body[s:m.end() + 25].replace("\n", "")))
            score += w
    if hits:
        print(f"\n【1】禁止表現  {len(hits)}件  (減点 {score})")
        agg = Counter(h[0] for h in hits)
        for word, n in agg.most_common():
            why = next(h[1] for h in hits if h[0] == word)
            print(f"  ✗ 「{word}」 ×{n}  → {why}")
            if verbose:
                for h in hits:
                    if h[0] == word:
                        print(f"      …{h[3]}…")
    else:
        print("\n【1】禁止表現  なし ✓")
    return score


def check_length(sents, verbose):
    lens = [len(s) for s in sents]
    if not lens:
        return 0
    avg = statistics.mean(lens)
    med = statistics.median(lens)
    sd = statistics.pstdev(lens)
    longs = [s for s in sents if len(s) > 80]

    print(f"\n【2】文の長さ  平均{avg:.1f}字 / 中央値{med:.0f}字 / 最長{max(lens)}字 / 標準偏差{sd:.1f}")
    score = 0
    if longs:
        score += len(longs) * 2
        print(f"  ✗ 80字超の文が {len(longs)}件（耳で聞くと理解できない）")
        for s in (longs if verbose else longs[:5]):
            print(f"      [{len(s)}字] {s[:60]}…")
        if not verbose and len(longs) > 5:
            print(f"      …他 {len(longs)-5}件（--verbose で全件）")

    # 均一性は変動係数で見る。話し言葉は一文が短いぶん標準偏差も小さくなるため、
    # 絶対値で判定すると自然な口語を誤検知する。
    cv = sd / avg if avg else 0
    if len(lens) > 20:
        if cv < 0.30:
            score += 15
            print(f"  ✗ 文長が均一すぎる（変動係数 {cv:.2f} < 0.30）")
            print("      → 短い文（10字前後）を意図的に混ぜる")
        elif cv < 0.38:
            score += 6
            print(f"  △ 文長のばらつきがやや小さい（変動係数 {cv:.2f}）")
        else:
            print(f"  ✓ 長短のリズムは十分（変動係数 {cv:.2f}）")
    return score


def check_tails(sents, verbose):
    tails = [s[-4:-1] if len(s) > 4 else s[:-1] for s in sents]
    score, runs = 0, []
    run, prev = 1, None
    for t in tails:
        if t == prev:
            run += 1
        else:
            if run >= 3 and prev:
                runs.append((prev, run))
            run, prev = 1, t
    if run >= 3 and prev:
        runs.append((prev, run))

    print(f"\n【3】語尾  種類 {len(set(tails))} / 文 {len(tails)}")
    top = Counter(tails).most_common(5)
    for t, n in top:
        ratio = n / len(tails) * 100 if tails else 0
        mark = "✗" if ratio > 25 else " "
        print(f"  {mark} 「…{t}」 {n}回 ({ratio:.0f}%)")
        if ratio > 25:
            score += 8
    if runs:
        score += sum(r[1] for r in runs)
        print(f"  ✗ 同じ語尾の3連続以上が {len(runs)}箇所")
        for t, n in runs[:5]:
            print(f"      「…{t}」が {n}回連続")
    return score


def check_taigen(sents, verbose):
    hits = []
    for s in sents:
        if not s.endswith("。"):
            continue
        c = s[-2]
        if re.match(r"[一-鿿゠-ヿ]", c) and c not in VERB_TAIL:
            hits.append(s)
    ratio = len(hits) / len(sents) * 100 if sents else 0
    score = 0
    print(f"\n【4】体言止め  {len(hits)}件 ({ratio:.1f}%)")
    if ratio > 8:
        score += int(ratio)
        print("  ✗ 多すぎる。話し言葉では不自然に聞こえる")
        for s in (hits if verbose else hits[:5]):
            print(f"      {s[:50]}")
    else:
        print("  ✓ 許容範囲")
    return score


def check_triples(body):
    # 単語を3つ並べるだけの列挙は口語でも自然に出る。
    # AIの癖が出るのは、修飾のついた「句」を3つ並べる構文なので、
    # 各要素が6字以上のものだけを数える。
    # 閾値は絶対数ではなく密度で見る。実在チャンネル31本(288,296字)の生実測は
    # 0.29件/1000字だが、自動字幕は読点が7.9個/1000字しかなく（普通の文章は20超）、
    # 読点密度で補正すると人間の水準は約0.9件/1000字。
    pat = re.compile(r"[^。、]{6,25}、[^。、]{6,25}、(?:そして|また、?)?[^。、]{6,25}[。]")
    flat = re.sub(r"\s", "", body)
    n = len(pat.findall(flat))
    dens = n / len(flat) * 1000 if flat else 0
    print(f"\n【5】三点セット列挙（句レベル）  {n}件 ({dens:.2f}件/1000字, 補正済み人間水準≈0.9)")
    if dens > 1.8:
        print("  ✗ 人間の話し言葉の水準を大きく超えている。列挙を文にほどく")
        for m in list(pat.finditer(flat))[:3]:
            print(f"      {m.group(0)[:60]}")
        return int((dens - 0.9) * 8)
    if dens > 1.2:
        print("  △ やや多い。目立つものだけほどく")
        return 6
    print("  ✓ 人間の水準")
    return 0


def check_concreteness(body, sents):
    nums = len(re.findall(r"[0-9０-９]+", body))
    urls = len(re.findall(r"https?://", body))
    kata = len(re.findall(r"[゠-ヿ]{3,}", body))
    per = len(sents) / nums if nums else 999
    print(f"\n【6】具体性  数字 {nums} / URL {urls} / カタカナ語 {kata}")
    score = 0
    if nums == 0:
        score += 20
        print("  ✗ 数字が1つもない。AI作文の典型")
    elif per > 12:
        score += 10
        print(f"  ✗ 数字の密度が低い（{per:.0f}文に1回）。8文に1回を目標に")
    else:
        print(f"  ✓ {per:.0f}文に1回、数字が出ている")
    return score


def check_chapters(text):
    chaps = [(n, len(re.sub(r"\s", "", strip_noise(b)))) for n, b in chapters(text)]
    chaps = [c for c in chaps if c[1] > 100]
    if len(chaps) < 3:
        return 0
    lens = [c[1] for c in chaps]
    sd = statistics.pstdev(lens)
    avg = statistics.mean(lens)
    cv = sd / avg if avg else 0
    print(f"\n【7】章ごとの文字数  {len(chaps)}章 / 平均{avg:.0f}字 / 変動係数{cv:.2f}")
    for n, l in chaps:
        bar = "█" * max(1, int(l / 150))
        print(f"      {l:>5}字 {bar} {n[:28]}")
    if cv < 0.18:
        print("  ✗ 章の長さが均等すぎる。AIが機械的に配分した痕跡")
        print("      → 山場の章を厚く、繋ぎの章を薄くする")
        return 15
    print("  ✓ メリハリがある")
    return 0


# ---------------------------------------------------------------- main

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    if not args:
        print(__doc__)
        sys.exit(1)

    path = args[0]
    text = load(path)
    body = strip_noise(text)
    plain = re.sub(r"\s", "", body)
    sents = sentences(body)

    print("=" * 62)
    print(f" AI臭チェック : {path}")
    print(f" 本文 {len(plain):,}字 / {len(sents)}文")
    print("=" * 62)

    total = 0
    total += check_ng(body, verbose)
    total += check_length(sents, verbose)
    total += check_tails(sents, verbose)
    total += check_taigen(sents, verbose)
    total += check_triples(body)
    total += check_concreteness(body, sents)
    total += check_chapters(text)

    print("\n" + "=" * 62)
    print(f" 減点合計: {total}")
    if total == 0:
        verdict, note = "A", "そのまま出せる"
    elif total <= 20:
        verdict, note = "B", "軽微。指摘箇所だけ直す"
    elif total <= 60:
        verdict, note = "C", "リライト必須"
    elif total <= 120:
        verdict, note = "D", "AI生成そのまま。全面的に書き直す"
    else:
        verdict, note = "E", "提出不可"
    print(f" 判定: {verdict}  — {note}")
    print("=" * 62)
    print("\n※ このスコアは目安。最終判断は必ず音読で行うこと。")

    sys.exit(0 if total <= 20 else 1)


if __name__ == "__main__":
    main()

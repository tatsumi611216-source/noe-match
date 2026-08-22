#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
style_extract.py — 複数の文字起こしから、チャンネルの「型」を定量抽出する。

依存ライブラリなし。.vtt / .srt / .txt をまとめて読める。

  python3 tools/style_extract.py refs/                  # ディレクトリごと
  python3 tools/style_extract.py refs/ --per-file       # 動画ごとにも出す
  python3 tools/style_extract.py refs/ --out refs/style.md

yt-dlp が吐く .vtt をそのまま放り込んでよい。
タイムスタンプ・重複行・話者タグは自動で除去する。
"""

import os
import re
import sys
import glob
import statistics
from collections import Counter

# ------------------------------------------------------------ 前処理

TS = re.compile(r"^\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->")
CUE_NUM = re.compile(r"^\d+$")
TAG = re.compile(r"<[^>]+>")
BRACKET = re.compile(r"[\[［(（][^\]］)）]{0,20}[\]］)）]")
HEAD = re.compile(r"^(WEBVTT|Kind:|Language:|NOTE\b|STYLE\b)")


def read_transcript(path):
    """VTT/SRT/TXT を素のテキストにする。VTTの重複行も潰す。"""
    with open(path, encoding="utf-8", errors="replace") as f:
        raw = f.read()

    lines = []
    for line in raw.splitlines():
        s = line.strip()
        if not s or TS.match(s) or CUE_NUM.match(s) or HEAD.match(s):
            continue
        s = TAG.sub("", s)          # <c>, <00:00:01.000> 等
        s = BRACKET.sub("", s)      # [音楽] (笑) 等
        s = s.strip()
        if s:
            lines.append(s)

    # VTTのローリング字幕は同じ行が連続で出る。直前と同じ／内包される行は落とす。
    dedup = []
    for s in lines:
        if dedup and (s == dedup[-1] or s in dedup[-1]):
            continue
        if dedup and dedup[-1] in s:
            dedup[-1] = s
            continue
        dedup.append(s)

    return "\n".join(dedup)


def to_sentences(text):
    """句点がない自動字幕にも対応する。"""
    flat = re.sub(r"\s+", "", text)
    if "。" in flat or "！" in flat or "？" in flat:
        parts = re.split(r"(?<=[。！？])", flat)
    else:
        # 句読点がない自動字幕。行単位を1発話とみなす。
        parts = [re.sub(r"\s+", "", l) for l in text.splitlines()]
    return [p for p in parts if len(p) >= 2]


# ------------------------------------------------------------ 抽出

CALLS = ["みなさん", "皆さん", "あなた", "みんな", "みなさま", "皆様"]
FILLERS = ["えー", "あの", "まあ", "なんか", "ちょっと", "やっぱり", "ほんとに", "実は"]


def analyze(name, text):
    sents = to_sentences(text)
    plain = re.sub(r"\s", "", text)
    lens = [len(s) for s in sents] or [0]

    tails = []
    for s in sents:
        t = s.rstrip("。！？")
        if len(t) >= 3:
            tails.append(t[-3:])

    return {
        "name": name,
        "chars": len(plain),
        "sents": len(sents),
        "avg": statistics.mean(lens),
        "med": statistics.median(lens),
        "sd": statistics.pstdev(lens),
        "cv": statistics.pstdev(lens) / statistics.mean(lens) if statistics.mean(lens) else 0,
        "max": max(lens),
        "min": min(lens),
        "tails": Counter(tails),
        "calls": Counter({c: text.count(c) for c in CALLS if text.count(c)}),
        "fillers": Counter({f: text.count(f) for f in FILLERS if text.count(f)}),
        "nums": len(re.findall(r"[0-9０-９]+", text)),
        "kata": len(re.findall(r"[゠-ヿ]{3,}", text)),
        "desumasu": len(re.findall(r"(です|ます)[。、！？\s]", text)),
        "dearu": len(re.findall(r"(だ|である)[。！？\s]", text)),
        "opening": sents[:8],
    }


def fmt(a, per_file=False):
    out = []
    w = out.append
    w(f"### {a['name']}")
    w("")
    w(f"- 本文 {a['chars']:,}字 / {a['sents']}発話")
    w(f"- 一文: 平均 {a['avg']:.1f}字 / 中央値 {a['med']:.0f}字 / "
      f"最短 {a['min']} / 最長 {a['max']} / 変動係数 {a['cv']:.2f}")
    total = a["desumasu"] + a["dearu"]
    if total:
        w(f"- 文体: ですます {a['desumasu']/total*100:.0f}% / だ・である {a['dearu']/total*100:.0f}%")
    if a["calls"]:
        w(f"- 呼びかけ: " + " / ".join(f"「{k}」{v}回" for k, v in a["calls"].most_common()))
    else:
        w("- 呼びかけ: 検出なし")
    if a["fillers"]:
        w(f"- フィラー: " + " / ".join(f"「{k}」{v}" for k, v in a["fillers"].most_common(6)))
    per = a["sents"] / a["nums"] if a["nums"] else 0
    w(f"- 具体性: 数字 {a['nums']}回" + (f"（{per:.1f}発話に1回）" if per else ""))
    w("")
    w("**語尾トップ10**")
    w("")
    w("| 語尾 | 回数 | 比率 |")
    w("|---|---:|---:|")
    tot = sum(a["tails"].values()) or 1
    for t, n in a["tails"].most_common(10):
        w(f"| …{t} | {n} | {n/tot*100:.1f}% |")
    w("")
    if per_file and a["opening"]:
        w("**冒頭8発話**")
        w("")
        for i, s in enumerate(a["opening"], 1):
            w(f"{i}. {s}")
        w("")
    return "\n".join(out)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    per_file = "--per-file" in sys.argv
    out_path = None
    if "--out" in sys.argv:
        out_path = sys.argv[sys.argv.index("--out") + 1]

    if not args:
        print(__doc__)
        sys.exit(1)

    target = args[0]
    if os.path.isdir(target):
        files = sorted(
            p for ext in ("vtt", "srt", "txt", "md")
            for p in glob.glob(os.path.join(target, f"*.{ext}"))
        )
    else:
        files = [target]

    if not files:
        print(f"文字起こしが見つかりません: {target}")
        print("  .vtt / .srt / .txt / .md を置いてください")
        sys.exit(1)

    reports, all_text = [], []
    for p in files:
        text = read_transcript(p)
        if len(re.sub(r"\s", "", text)) < 200:
            print(f"  スキップ（短すぎ）: {os.path.basename(p)}", file=sys.stderr)
            continue
        all_text.append(text)
        reports.append(analyze(os.path.basename(p), text))

    if not reports:
        print("解析できるファイルがありませんでした")
        sys.exit(1)

    joined = "\n".join(all_text)
    punctuated = joined.count("。") > len(reports) * 5

    body = []
    body.append(f"# 文体分析レポート（{len(reports)}本）\n")
    if not punctuated:
        body.append(
            "> **注意：句読点のない自動字幕として解析しました。**\n"
            "> 行の区切りを1発話とみなしているため、一文の長さと語尾の数値は参考値です。\n"
            "> 語尾トップに「…PTの」のような文の途中が混じるのはこのためです。\n"
            "> 精度を上げるには、手動字幕（`--sub-langs ja`）か、\n"
            "> 句読点つきの文字起こしを使ってください。\n"
        )
    body.append("## 全体\n")
    body.append(fmt(analyze(f"合算 {len(reports)}本", "\n".join(all_text))))

    if per_file or len(reports) <= 12:
        body.append("\n## 動画ごと\n")
        for a in reports:
            body.append(fmt(a, per_file=per_file))

    body.append("\n## 台本を書くときのルール（この数値から導く）\n")
    agg = analyze("agg", "\n".join(all_text))
    top = agg["tails"].most_common(5)
    body.append(f"- 一文は平均 **{agg['avg']:.0f}字** を狙う。{agg['max']}字を超えたら切る")
    body.append(f"- 変動係数 {agg['cv']:.2f} を再現する。均一に書かない")
    if top:
        body.append("- 語尾は " + "、".join(f"「…{t}」" for t, _ in top[:3]) + " を主軸にする")
    if agg["calls"]:
        c = agg["calls"].most_common(1)[0][0]
        body.append(f"- 視聴者の呼び方は **「{c}」** に統一する")
    if agg["nums"]:
        body.append(f"- 数字を {agg['sents']/agg['nums']:.1f}発話に1回の密度で入れる")

    text = "\n".join(body) + "\n"
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"書き出しました: {out_path}")
    else:
        print(text)


if __name__ == "__main__":
    main()

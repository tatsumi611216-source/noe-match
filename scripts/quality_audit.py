# -*- coding: utf-8 -*-
"""既存記事の品質・整合性を機械的に検査し、欠陥リストを出す。

なぜ必要か（2026-08-17に確立）:

article_audit.py は「①流入 × ②実効単価 × ③接続」＝**収益の配置**を見る。
だが2026-08-16〜17の作業で、それとは別種の欠陥が次々に見つかった。

  - `nyuseki-2027-guide` が仏滅の日を「大安」と書き、親世代への通りが良いと勧めていた（9.2位で表示中）
  - 42本の記事が文脈と無関係な「あなたに合うアプリを見つけよう」で終わっていた
  - 134ファイルに検証できない体験の主張（のべマッチ数300件以上）が入っていた
  - キリル文字・ハングルの混入が3件

いずれも**読めば分かるが、読まないと分からない**種類の欠陥で、
記事数が増えるほど人手では追えなくなる。だから機械で洗う。

使い方:
    python scripts/quality_audit.py            # agent/quality_audit.md を生成
    python scripts/quality_audit.py --json     # 標準出力にJSON
"""
import glob
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "agent", "quality_audit.md")

# 重大度。fix=すぐ直すべき / check=人の判断が要る / note=記録のみ
SEV = {"fix": 0, "check": 1, "note": 2}


def text_of(html):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", t)


def real_articles():
    out = []
    for d in sorted(os.listdir(os.path.join(BASE, "articles"))):
        p = os.path.join(BASE, "articles", d, "index.html")
        if not os.path.isdir(os.path.join(BASE, "articles", d)) or not os.path.exists(p):
            continue
        h = io.open(p, encoding="utf-8").read()
        if len(h) < 3000 or 'http-equiv="refresh"' in h.lower():
            continue
        m = re.search(r'<link rel="canonical" href="([^"]+)"', h)
        if m and ("/articles/%s/" % d) not in m.group(1):
            continue
        out.append((d, p, h))
    return out


def tools():
    return [(os.path.basename(os.path.dirname(p)), p, io.open(p, encoding="utf-8").read())
            for p in sorted(glob.glob(os.path.join(BASE, "tools", "*", "index.html")))]


def check(slug, h, exists):
    """1ページ分の欠陥を返す。"""
    d = []
    body = text_of(h)

    # --- 文字の混入 -------------------------------------------------
    for pat, name in [(r"[Ѐ-ӿ]+", "キリル文字"), (r"[가-힣]+", "ハングル"),
                      (r"[�]", "文字化け")]:
        m = re.findall(pat, body)
        if m:
            d.append(("fix", "混入", "%s: %s" % (name, "".join(m[:3])[:24])))

    # 日本語の途中に紛れた英単語（訳し漏れ）
    for m in re.finditer(r"[ぁ-んァ-ヶ一-龥]\s?(the|and|about|similar|because|however)\s?[ぁ-んァ-ヶ一-龥]",
                         body, re.I):
        d.append(("fix", "混入", "英単語の紛れ込み: %s" % m.group(0)))

    # --- 内部リンク -------------------------------------------------
    for u in sorted(set(re.findall(r'href="(/(?:articles|tools)/[a-z0-9\-]+/)"', h))):
        if u not in exists:
            d.append(("fix", "リンク", "リンク切れ: %s" % u))

    # --- 構造化データ -----------------------------------------------
    types = []
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
        try:
            types.append(json.loads(b).get("@type"))
        except Exception:
            d.append(("fix", "LD", "JSON-LDが壊れている"))
    if len(types) != len(set(types)):
        d.append(("fix", "LD", "@typeが重複: %s" % types))
    for u in re.findall(r'"(?:@id|url)":\s*"(https://www\.noe-match\.com/articles/[^"]+)"', h):
        if slug not in u:
            d.append(("fix", "LD", "他ページのURLが混入: %s" % u))

    # --- 広告の作法 -------------------------------------------------
    for a in re.finditer(r'<a[^>]*href="https://px\.a8\.net[^"]*"[^>]*>', h):
        tag = a.group(0)
        if "nofollow" not in tag or "sponsored" not in tag:
            d.append(("fix", "広告", "rel属性が不足: %s" % tag[:60]))
        if 'target="_blank"' not in tag:
            d.append(("check", "広告", "target=_blank が無い"))
    # ★JS文字列内の候補まで数えると誤検知になる（結果連動型ツールで11件と出た）。
    #   実際にリンクとして出るのは <a> タグだけなので、そこで数える。
    ads = len(re.findall(r'<a[^>]*href="https://px\.a8\.net', h))
    if ads and ">PR<" not in h and "【PR】" not in h and "本ページはプロモーション" not in h:
        d.append(("fix", "広告", "PRラベルが見当たらない（広告%d件）" % ads))
    if ads > 4:
        d.append(("check", "広告", "1ページの広告が%d件（台帳の上限は4）" % ads))

    # --- 断定表現（景表法・薬機法）----------------------------------
    # ★誤検知に注意（2026-08-17に3度踏んだ）:
    #   1. 「必ず成婚料を含めて計算してください」→ 別語を拾った
    #   2. 「成婚を保証するものではありません」→ **正しい注記**を違反として拾った
    #   3. 「3年以内に必ず結婚したい」→ **読者が書くプロフィール文の例**（しかも書かない方がよいという文脈）
    #   誤報が出る監査は使われなくなる。**願望・条件・否定は違反ではない**ので厳密に切り分ける。
    #   違反なのは「必ず結婚できる」のように**結果を断定**している場合だけ。
    NEG_TAIL = r"(?!\s*(?:するもの|するわけ|もの|わけ)?(?:でも|では|じゃ)?\s*(?:あり)?(?:ませ|な[いく])|\s*とは限)"
    NG = [
        # 願望（〜したい／しなければ）は除外し、可能・断定の語形だけを見る
        (r"必ず(?:結婚|成婚)(?:でき|できます|します|する)" + NEG_TAIL, "結果の断定"),
        (r"(?:結婚|成婚)(?:率|)を保証" + NEG_TAIL, "成果の保証"),
        (r"(?:シミ|しみ|しわ|抜け毛)が(?:消え|治り)(?:る|ます)" + NEG_TAIL, "医薬品的な効能"),
        (r"絶対に(?:安全|大丈夫|得|痩せ)" + NEG_TAIL, "断定"),
        (r"誰でも(?:結婚|成婚)(?:でき|できます)" + NEG_TAIL, "断定"),
    ]
    for pat, why in NG:
        for m in re.finditer(pat, body):
            d.append(("fix", "表現", "%s: %s" % (why, body[max(0, m.start() - 12):m.end() + 12].strip())))

    # --- 検証できない主張 -------------------------------------------
    for pat in [r"のべマッチ数", r"デート経験\d+回", r"実使用経験", r"登録・課金して検証"]:
        if re.search(pat, body):
            d.append(("fix", "主張", "検証できない体験の主張: %s" % pat))

    # --- 鮮度 -------------------------------------------------------
    m = re.search(r"最終更新[：:]\s*(\d{4})年(\d{1,2})月", body)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        if (2026 - y) * 12 + (8 - mo) >= 6:
            d.append(("check", "鮮度", "最終更新が%d年%d月" % (y, mo)))
    for m in re.finditer(r"(20(2[0-4]))年(現在|時点|最新|版)", body):
        d.append(("check", "鮮度", "古い年の表記: %s" % m.group(0)))

    # --- 見出しと本文 -----------------------------------------------
    h2 = re.findall(r"<h2[^>]*>(.*?)</h2>", h, re.S)
    h2t = [" ".join(re.sub(r"<[^>]+>", "", x).split()) for x in h2]
    COMMON = {"関連記事", "関連記事・ツール", "よくある質問", "まとめ"}
    dup = [x for x in h2t if h2t.count(x) > 1 and x not in COMMON]
    if dup:
        d.append(("check", "構成", "h2が重複: %s" % sorted(set(dup))[:2]))
    if len(body.replace(" ", "")) < 1500:
        d.append(("check", "構成", "本文が薄い（%d字）" % len(body.replace(" ", ""))))
    return d


def main():
    arts = real_articles()
    tls = tools()
    exists = set()
    for s, _, _ in arts:
        exists.add("/articles/%s/" % s)
    for s, _, _ in tls:
        exists.add("/tools/%s/" % s)

    rows = []
    for slug, p, h in arts + tls:
        kind = "tool" if any(slug == t[0] for t in tls) else "article"
        for sev, cat, msg in check(slug, h, exists):
            rows.append({"slug": slug, "kind": kind, "sev": sev, "cat": cat, "msg": msg})

    rows.sort(key=lambda r: (SEV[r["sev"]], r["cat"], r["slug"]))

    if "--json" in sys.argv:
        print(json.dumps(rows, ensure_ascii=False, indent=1))
        return

    import collections
    bycat = collections.Counter((r["sev"], r["cat"]) for r in rows)
    byslug = collections.Counter(r["slug"] for r in rows if r["sev"] == "fix")

    L = ["# 品質監査（自動生成・scripts/quality_audit.py）", "",
         "対象：記事 %d本／ツール %d本" % (len(arts), len(tls)), "",
         "重大度 **fix**＝すぐ直すべき／**check**＝人の判断が要る／note＝記録のみ", "",
         "## 集計", "", "| 重大度 | 分類 | 件数 |", "|---|---|---|"]
    for (sev, cat), n in sorted(bycat.items(), key=lambda x: (SEV[x[0][0]], -x[1])):
        L.append("| %s | %s | %d |" % (sev, cat, n))
    L += ["", "**fix 合計 %d件／check 合計 %d件**" %
          (sum(1 for r in rows if r["sev"] == "fix"),
           sum(1 for r in rows if r["sev"] == "check")), ""]
    if byslug:
        L += ["## fixが多いページ", "", "| ページ | 件数 |", "|---|---|"]
        for s, n in byslug.most_common(15):
            L.append("| `%s` | %d |" % (s, n))
        L.append("")
    L += ["## 明細", ""]
    cur = None
    for r in rows:
        key = (r["sev"], r["cat"])
        if key != cur:
            cur = key
            L += ["", "### [%s] %s" % (r["sev"], r["cat"]), ""]
        L.append("- `%s` — %s" % (r["slug"], r["msg"]))
    io.open(OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("書き出し:", OUT)
    print("fix %d件 / check %d件" %
          (sum(1 for r in rows if r["sev"] == "fix"),
           sum(1 for r in rows if r["sev"] == "check")))
    for (sev, cat), n in sorted(bycat.items(), key=lambda x: (SEV[x[0][0]], -x[1])):
        print("  %-6s %-6s %d" % (sev, cat, n))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

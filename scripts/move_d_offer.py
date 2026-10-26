# -*- coding: utf-8 -*-
"""Dクラスタ（アプリ選定）のオファーを、読者が来た表の直後へ移す（2026-09-04）

なぜ:
Dは21日でセッション51とサイト最大だが、広告クリックは1件。理由は2つ実測で分かっている。
1. **到達しない** — オファーは本文の55〜90%地点にあるが、90%スクロール到達は
   matching-app-ranking で11%（19PV中2）、members-data も11%（9PV中1）。
2. **滞在が短い** — Dの3分の2はChatGPT経由で、chatgpt.com は35秒/セッション・関与率40%。
   BingやYahooの半分しか読まれていない。**数字を1つ確かめて離脱する読者**が主体。

したがって「読者が確かめに来た表の直後」に置く。出典の注記は表とセットで信頼性の一部なので、
**注記の下**に入れる（表と出典の間には割り込ませない）。

1変数だけ動かす。**文言も案件も変えない。位置だけ。**
既にオファーがあるページは移設（move）、無いページは同じ形で新設（add）として記録を分ける。

  python scripts/move_d_offer.py --dry-run
  python scripts/move_d_offer.py --apply
"""
import argparse
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AFI = "https://t.afi-b.com/visit.php?a=62571t-63703183&p=C982892I"

NEW_BLOCK = ('<div style="background:#f7f5f2;border:1px solid #e6e2dc;border-radius:0;'
             'padding:20px 22px;margin:26px 0;text-align:center">'
             '<p style="font-size:.7rem;color:#999;margin:0 0 6px;text-align:left">PR</p>'
             '<p style="font-weight:700;margin:0 0 12px">{lead}</p>'
             '<a href="' + AFI + '" rel="nofollow sponsored noopener" target="_blank" '
             'style="display:inline-block;background:#3f6ea8;color:#fff;font-weight:700;'
             'padding:13px 32px;text-decoration:none">婚活目的のサービスを見る</a>'
             '<p style="font-size:.74rem;color:#888;margin:10px 0 0">料金・機能・会員数は'
             '変更される場合があります。申し込み前に公式サイトでご確認ください。'
             '成婚を保証するものではありません</p></div>')

# 新設ページの一文。ページが答えている問いの「次の一歩」に合わせる（事実の主張はしない）
LEADS = {
    "price-comparison": "料金の次は、婚活目的の濃さで見る",
    # 本文中にインラインの広告リンクがあるページ。既存のリンクはそのまま、
    # 表の直後にPR枠を新設する（本文には触らない）
    "matching-app-ranking": "ランキングの次は、婚活目的の濃さで見る",
    "free-vs-paid": "無料と有料の次は、婚活目的の濃さで見る",
    "compare-konkatsu": "比較の次は、成婚の実数を公表しているかで見る",
    "tapple-vs-pairs": "2社の次は、婚活目的の濃さで見る",
    "omiai-vs-pairs": "2社の次は、婚活目的の濃さで見る",
    "with-vs-pairs": "2社の次は、婚活目的の濃さで見る",
    "matching-dansei-cost-data": "費用の次は、婚活目的の濃さで見る",
    "matching-josei-cost-data": "費用の次は、婚活目的の濃さで見る",
}


PR_BLOCK = re.compile(
    r'<div style="[^"]*text-align:center">\s*<p style="[^"]*">\s*PR\s*</p>.*?</div>', re.S)


def find_block(html):
    """PR枠として自己完結しているオファーブロックだけを対象にする。

    **文中のインラインリンクを掴んではいけない。** 一般化して「広告リンクの直前のdiv」を
    ブロックとみなす実装を一度書いたところ、matching-app-ranking で本文中のリンクに当たり、
    節を3つ巻き込んで切り出した（2026-09-04・全ファイルを戻した）。
    ここは PR 表記を持つ中央寄せのdivに限定し、それ以外は skip する。
    """
    for m in PR_BLOCK.finditer(html):
        b = m.group(0)
        if 'href="https://px.a8.net' in b or 'href="https://t.afi-b.com' in b:
            return m.start(), m.end()
    return None


def has_inline_offer(html):
    """PR枠の外に広告リンクがあるか（あるなら本文に埋まっている＝触らない）"""
    stripped = PR_BLOCK.sub("", html)
    return ('href="https://px.a8.net' in stripped
            or 'href="https://t.afi-b.com' in stripped)


def insert_point(html):
    """最初の表の直後。表の直後に出典の注記があればその下に置く。"""
    t = html.find("</table>")
    if t < 0:
        return None
    p = t + len("</table>")
    if html[p:p + 6] == "</div>":            # table-scroll のラッパ
        p += 6
    while True:                              # 表に付いている注記は表側に残す
        m = re.match(r'\s*<p>\s*<small>.*?</small>\s*</p>', html[p:], re.S)
        if not m:
            break
        p += m.end()
    return p


def process(slug, apply_):
    path = os.path.join(ROOT, "articles", slug, "index.html")
    if not os.path.exists(path):
        return slug, "skip", "ファイルが無い"
    html = io.open(path, encoding="utf-8").read()
    html_orig = html
    if "<table" not in html:
        return slug, "skip", "表が無い"

    b = find_block(html)
    if b is None and has_inline_offer(html) and slug not in LEADS:
        return slug, "skip", "広告が本文中のリンク（PR枠でない）ので触らない"
    ip = insert_point(html)
    if ip is None:
        return slug, "skip", "表の終わりが取れない"

    if b:
        s, e = b
        if s < ip < e:
            return slug, "skip", "既に表の直後にある"
        block = html[s:e]
        pct_before = round(s / len(html) * 100)
        html = html[:s] + html[e:]
        ip = insert_point(html)
        new = html[:ip] + block + html[ip:]
        kind, note = "move", "文字位置 %d%% → %d%%（実画面での位置は別途実測）" % (pct_before, round(ip / len(new) * 100))
    else:
        lead = LEADS.get(slug)
        if not lead:
            return slug, "skip", "新設用の一文が未定義"
        new = html[:ip] + NEW_BLOCK.format(lead=lead) + html[ip:]
        kind, note = "add", "表の直後（%d%%）に新設" % round(ip / len(new) * 100)

    # 安全装置: 移設は「同じものを別の場所へ」でなければならない。
    # 一度、本文中のリンクをブロックと誤認して節を3つ巻き込んだ（2026-09-04）。
    if kind == "move":
        if len(new) != len(html_orig):
            return slug, "ABORT", "長さが変わった（%d→%d）" % (len(html_orig), len(new))
        for tag in ("<table", "<h2", "<h3", "</p>", "<div"):
            if new.count(tag) != html_orig.count(tag):
                return slug, "ABORT", "%s の数が変わった" % tag
    else:
        if new.count("<table") != html_orig.count("<table"):
            return slug, "ABORT", "表の数が変わった"

    if apply_:
        io.open(path, "w", encoding="utf-8", newline="").write(new)
    return slug, kind, note


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import importlib.util
    sp = importlib.util.spec_from_file_location("cg", os.path.join(ROOT, "scripts", "cluster_gsc.py"))
    cg = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(cg)
    cmap, _ = cg.build_map()
    targets = sorted(s for s, c in cmap.items() if c[0] == "D" and not s.startswith("tool:"))

    tally = {}
    for slug in targets:
        s, kind, note = process(slug, a.apply)
        tally[kind] = tally.get(kind, 0) + 1
        print("  %-28s %-5s %s" % (s, kind, note))
    print("\n" + ("適用" if a.apply else "下見のみ（--apply で書き込む）") + "  " +
          " / ".join("%s %d" % kv for kv in sorted(tally.items())))


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    main()

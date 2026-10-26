# -*- coding: utf-8 -*-
"""結婚資金計算機の計算スクリプトが、他のツールのフッターに混入している不具合を直す（2026-10-08）

    python scripts/fix_footer_calc_js_20261008.py --check   混入しているページを出す（書き込まない）
    python scripts/fix_footer_calc_js_20261008.py --apply   混入した計算スクリプトだけを外す

原因: build_kekkonritsu_tool.py ほか7本のビルドスクリプトが、tools/kekkon-shikin-keisanki/index.html の
「<footer 以降」をそのままフッターとして流用していた。そこには結婚資金計算機の計算スクリプト（IIFE）が
入っているため、計算機の要素（calcBtn ほか）が無いページで開くたびに
  Cannot read properties of null (reading 'addEventListener')
が出ていた。IIFE が例外で止まるため、同じ <script> にある「↑」ボタンの表示切替（onscroll）も動いていなかった。
外すのは IIFE だけで、onscroll の行は残す（ボタンが動くようになる）。本文・広告・計測には触らない。
ビルドスクリプト側も同じ関数（strip_calc）で外すように直した。
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALC_RE = re.compile(r'<script>\n\(function\(\)\{\n"use strict";\n// 金額はすべて万円.*?\n\}\)\(\);\n(?=onscroll=)', re.S)
KEEP = "tools/kekkon-shikin-keisanki/index.html"   # 本物の計算機。ここは触らない


def strip_calc(html):
    """フッター（または全文）から、計算機の要素が無い場合に限って計算スクリプトを外す"""
    if 'id="calcBtn"' in html:
        return html
    return CALC_RE.sub("<script>\n", html)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    apply = "--apply" in sys.argv
    n = 0
    for d in sorted(os.listdir(os.path.join(ROOT, "tools"))):
        rel = "tools/%s/index.html" % d
        p = os.path.join(ROOT, rel)
        if rel == KEEP or not os.path.exists(p):
            continue
        s = io.open(p, encoding="utf-8").read()
        t = strip_calc(s)
        if t != s:
            n += 1
            print(("外した  " if apply else "混入あり ") + rel)
            if apply:
                io.open(p, "w", encoding="utf-8", newline="").write(t)
    print("対象 %dページ" % n)


if __name__ == "__main__":
    main()

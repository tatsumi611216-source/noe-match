# -*- coding: utf-8 -*-
"""実流入のある着地ツールのうち、LINE導線が無い1本に導線を入れる（2026-11-04 新設）

GA4日別アーカイブ 10/19〜11/01（14日・Direct除き）の着地上位25ページを lin.ee の有無と
突き合わせたら、導線が無いのは /about.html・トップ・次のツール1本だけだった。
  /tools/koisaihi-simulator/   bing 3・google 2（広告も0。locks は 10/05 で期限切れ）
形式・挿入位置は add_line_cta_landing_0917.py と同一（BLOCK をそのまま使う）。
ツールなので gtag のパラメータは article ではなく tool にする（他ツールと同じ）。
冪等: すでに lin.ee があるページは触らない。
実行: python scripts/add_line_cta_landing_1104.py
"""
import io
import os
import sys

import add_line_cta_landing_0917 as base

TARGETS = {
 "koisaihi-simulator": ("デート代の決め方を、ふたりで話す前に",
  "割り勘・交互払い・月の予算の決め方をまとめています。<br>月１回お送りしています。"),
}


def main():
    blk_tpl = base.BLOCK.replace("{article:'%(slug)s'}", "{tool:'%(slug)s'}")
    assert blk_tpl != base.BLOCK
    for slug, (head, body) in TARGETS.items():
        p = os.path.join(base.ROOT, "tools", slug, "index.html")
        h = io.open(p, encoding="utf-8").read()
        if "lin.ee" in h:
            print("-", slug, "既にLINEあり"); continue
        if h.count("<footer") != 1:
            print("-", slug, "footerが1つではない"); continue
        h2 = h.replace("<footer", blk_tpl % {"head": head, "body": body, "slug": slug} + "<footer", 1)
        io.open(p, "w", encoding="utf-8").write(h2)
        print("+", slug)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

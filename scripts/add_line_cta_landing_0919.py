# -*- coding: utf-8 -*-
"""実流入のある着地ページのうち、LINE導線が無いデータ記事2本に導線を入れる（2026-09-19 新設）

9/17の突き合わせ（8/27〜9/14・3セッション以上）以降のアーカイブで計算し直すと、
9/10〜9/17（direct/(not set)除き）で2セッション以上の着地ページのうち導線が無いのは次の2本だけだった。
  /articles/nashikon-data/       bing 2
  /articles/omiai-danjohi-data/  bing 1・yahoo 1
形式・挿入位置は add_line_cta_landing_0917.py と同一（BLOCK と main をそのまま使う）。
冪等: すでに lin.ee があるページは触らない。
実行: python scripts/add_line_cta_landing_0919.py
"""
import sys

import add_line_cta_landing_0917 as base

base.TARGETS = {
 "nashikon-data": ("結婚式の費用と実施率の公表値が更新されたら",
  "調査ごとに数字の取り方が違うので、出典つきで追っています。<br>変わった点だけを月１回お送りしています。"),
 "omiai-danjohi-data": ("アプリの公表値は、静かに書き換わります",
  "Omiai・Pairs・withの男女比と会員数の注記を追っています。<br>変わった点だけを月１回お送りしています。"),
}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    base.main()

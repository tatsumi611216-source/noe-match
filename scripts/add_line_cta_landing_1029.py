# -*- coding: utf-8 -*-
"""実流入のある着地ページのうち、LINE導線が無い2本に導線を入れる（2026-10-29 新設）

GA4日別アーカイブ 10/13〜10/26（14日・Direct除き）の着地上位20ページを lin.ee の有無と
突き合わせたら、導線が無いのは次の2本だけだった（どちらも locks / observing の対象外）。
  /articles/with-guide/               google 6・bing 1（Google経由の着地では上位）
  /articles/kekkonshiki-isho-rental/  openai 4・ecosia 1・bing 1
形式・挿入位置は add_line_cta_landing_0917.py と同一（BLOCK と main をそのまま使う）。
冪等: すでに lin.ee があるページは触らない。
実行: python scripts/add_line_cta_landing_1029.py
"""
import sys

import add_line_cta_landing_0917 as base

base.TARGETS = {
 "with-guide": ("アプリの仕様は、静かに書き換わります",
  "with・Pairs・Omiaiの機能や料金の改定を追っています。<br>変わった点だけを月１回お送りしています。"),
 "kekkonshiki-isho-rental": ("親族の装いは、早めに決めておくと楽になる",
  "留袖・訪問着・ドレスの手配の段取りをまとめています。<br>迷ったら、追加後そのままトークでどうぞ。"),
}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    base.main()

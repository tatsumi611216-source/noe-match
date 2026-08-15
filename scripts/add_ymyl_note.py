# -*- coding: utf-8 -*-
"""保険（YMYL枠）の設置箇所に「契約の判断はご自身で」の注記を入れる。

なぜ必要か（2026-08-15）:

2026-08-15のCEO判断で、保険ランドリーの設置先の限定を解除し、産後・ライフイベント
文脈（クラスタA）への設置を正式に許可した。**ただし表現の制約は解除していない。**
台帳（agent/AGENT.md）が必須としている「契約の判断はご自身で」の注記が、
実地監査の結果5ページすべてで欠けていたため、機械的に補う。

これは価値判断ではなく、YMYL領域での実務上の要請（読者が広告を助言と誤読しない
ようにする）である。設置先を広げるほど、この注記の重要度は上がる。

冪等：既に注記がある箇所は触らない。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODES = ("4B8B4Q+42GRGA",)  # 保険ランドリー
NOTE = "契約の判断はご自身で行ってください。"

PAGES = ["tools/garugaru-check", "tools/fugenbyo-check", "tools/saigenbyo-check",
         "articles/garugaru-ki-guide", "articles/sango-crisis-guide",
         "articles/garugaru-gibo-jitsubo", "articles/garugaru-nai-hito",
         "articles/garugaru-doukyo", "articles/garugaru-otto-genkai"]

NOTE_P = ('<p style="font-size:.72rem;color:#8a8f95;margin:10px 0 0">'
          '当サイトは相談窓口を選択肢として紹介しており、特定の保険商品を推奨するものではありません。'
          + NOTE + '</p>')


def main():
    for page in PAGES:
        p = os.path.join(ROOT, page, "index.html")
        h = open(p, encoding="utf-8").read()
        if NOTE in h:
            print("SKIP (already noted):", page)
            continue
        done = 0
        for code in CODES:
            # 該当リンクの </a> の直後に注記を差し込む
            for m in re.finditer(r'<a href="[^"]*%s[^"]*"[^>]*>.*?</a>' % re.escape(code),
                                 h, re.S):
                h = h[:m.end()] + NOTE_P + h[m.end():]
                done += 1
                break  # 1ページ1箇所（台帳の定め）
        if done:
            open(p, "w", encoding="utf-8").write(h)
            print("added note:", page)
        else:
            print("no insurance link:", page)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

# -*- coding: utf-8 -*-
"""子育て制度ツール7本の相互結線（2026-08-29・クラスタ強化②）

なぜ必要か:
病児保育・子ども医療費・誰でも通園・産後ケア・不妊助成・育休延長・練馬保育園は
同じ読者（子育て世帯）が使うのに、各ツールが孤立していて隣の制度への導線が無い。
記事→ツールの結線は済んだので、次はツール→ツールの回遊を作る。

- 挿入位置: LINE-CTA の直前（結果を見終わった読者が次に目を落とす場所）
- 各ツール3リンク・ライフステージの近い順
- 横断クリックは gtag('event','tool_cross',{from,to}) で計測する
  （効果が測れない改善はしない）
- 冪等: TOOL-FAMILY マーカーがあれば何もしない
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DESC = {
 "byoji-hoiku-ryokin":      ("病児保育は1日いくらか", "東京23区の料金・減免・予約方法を並べて確認"),
 "kodomo-iryohi-jichitai":  ("子ども医療費助成、23区で何が違うか", "対象年齢・窓口負担・入院時の食事代の扱い"),
 "daredemo-tsuen-jichitai": ("誰でも通園制度、月何時間まで使えるか", "46自治体の上限時間・料金・予約方法"),
 "sangokea-ryokin":         ("産後ケアの自己負担はいくらか", "43自治体の料金・回数上限・減免"),
 "funin-josei-jichitai":    ("不妊治療の助成、あなたの区はいくらまで", "東京23区の上乗せ助成の有無と上限額"),
 "ikukyu-encho-hantei":     ("育休延長の条件判定", "延長できる条件と必要書類をその場で判定"),
}

FAMILY = {
 "funin-josei-jichitai":    ["sangokea-ryokin", "kodomo-iryohi-jichitai", "daredemo-tsuen-jichitai"],
 "sangokea-ryokin":         ["daredemo-tsuen-jichitai", "byoji-hoiku-ryokin", "kodomo-iryohi-jichitai"],
 "daredemo-tsuen-jichitai": ["byoji-hoiku-ryokin", "kodomo-iryohi-jichitai", "sangokea-ryokin"],
 "byoji-hoiku-ryokin":      ["kodomo-iryohi-jichitai", "daredemo-tsuen-jichitai", "sangokea-ryokin"],
 "kodomo-iryohi-jichitai":  ["byoji-hoiku-ryokin", "daredemo-tsuen-jichitai", "sangokea-ryokin"],
 "ikukyu-encho-hantei":     ["daredemo-tsuen-jichitai", "byoji-hoiku-ryokin", "kodomo-iryohi-jichitai"],
 "hoikuen-tensu-nerima":    ["daredemo-tsuen-jichitai", "byoji-hoiku-ryokin", "kodomo-iryohi-jichitai"],
}

ROW = ('<li style="margin:0 0 12px"><a href="/tools/%(to)s/" '
       'onclick="try{gtag(\'event\',\'tool_cross\',{from:\'%(frm)s\',to:\'%(to)s\'});}catch(e){}" '
       'style="font-weight:700;color:#7c2e42">%(head)s</a>'
       '<span style="display:block;font-size:.82rem;color:#6b7178;margin-top:2px">%(body)s</span></li>')

BOX = ('\n<!-- TOOL-FAMILY -->\n'
       '<section style="max-width:680px;margin:40px auto 8px;padding:26px 24px;background:#f7f5f2;border:1px solid #e3ddd3">'
       '<p style="margin:0 0 6px;font-size:12px;letter-spacing:.16em;color:#7c2e42;font-family:Georgia,serif">RELATED TOOLS</p>'
       '<p style="margin:0 0 16px;font-weight:700;font-size:1.02rem">同じ自治体の、ほかの制度も確かめられます</p>'
       '<ul style="list-style:none;margin:0;padding:0">%(rows)s</ul>'
       '<p style="margin:12px 0 0;font-size:.72rem;color:#8a8f95">いずれも無料・登録不要。公式ページの一次確認にもとづく数字だけを載せています。</p>'
       '</section>\n')


def main(apply_):
    n = 0
    for frm, tos in sorted(FAMILY.items()):
        f = os.path.join(ROOT, "tools", frm, "index.html")
        h = io.open(f, encoding="utf-8").read()
        if "TOOL-FAMILY" in h:
            print("  済:", frm); continue
        anchor = "<!-- LINE-CTA -->"
        if anchor not in h:
            print("  アンカーなし:", frm); continue
        rows = "".join(ROW % {"frm": frm, "to": t, "head": DESC[t][0], "body": DESC[t][1]} for t in tos)
        h2 = h.replace(anchor, BOX % {"rows": rows} + anchor, 1)
        print("  +%s → %s" % (frm, ",".join(tos)))
        if apply_:
            io.open(f, "w", encoding="utf-8").write(h2); n += 1
    print("\n%s: %d本" % ("適用" if apply_ else "dry-run", n))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main("--apply" in sys.argv)

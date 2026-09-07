# -*- coding: utf-8 -*-
"""区選択ハブ（/tools/kosodate-shien-23ku/）への結線（2026-09-08）

既存バンク5本のツール（TOOL-FAMILY）と、そのデータ記事の関連リストへ
ハブへのリンクを1行ずつ足す。生成物を直接編集する（9/6の教訓: 生成スクリプトは再実行しない）。
同じ行は生成スクリプト側（wire_tool_family.py / build_hitorioya.py / build_kodomo_iryo.py /
build_byoji.py / build_sangocare_articles.py / build_daretsu_ryokin_article.py）にも写してある。

- 冪等: 既にハブのURLがあるファイルは何もしない
- 挿入位置は「マーカーの直後で最初の </ul>」の直前。マーカーが無ければ触らない
- 安全装置: 挿入前後で <li> の個数が +1、それ以外のタグ数が不変

使い方: python scripts/add_kosodate_hub_links.py [--apply]
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HUB = "kosodate-shien-23ku"
HUB_URL = "/tools/%s/" % HUB

TOOL_ROW = ('<li style="margin:0 0 12px"><a href="%s" '
            'onclick="try{gtag(\'event\',\'tool_cross\',{from:\'%%s\',to:\'%s\'});}catch(e){}" '
            'style="font-weight:700;color:#7c2e42">うちの区の子育て支援を1画面で（23区ハブ）</a>'
            '<span style="display:block;font-size:.82rem;color:#6b7178;margin-top:2px">区を選ぶと、ひとり親手当・医療費助成・病児保育・誰でも通園・産後ケアの5制度が並びます</span></li>'
            % (HUB_URL, HUB))
ART_ROW = '<li><a href="%s">23区の子育て支援を比較｜区を選ぶと5つの制度が1画面</a></li>\n' % HUB_URL

TOOLS = ["hitorioya-shien-jichitai", "kodomo-iryohi-jichitai", "byoji-hoiku-ryokin",
         "daredemo-tsuen-jichitai", "sangokea-ryokin"]
ARTICLES = {  # slug: マーカー
    "hitorioya-shien-data": '<h2 id="related">',
    "kodomo-iryohi-data": '<h2 id="related">',
    "byoji-hoiku-data": '<h2 id="related">',
    "sangokea-josei": '<h2 id="related">',
    "daredemo-tsuen-ryokin": '<div class="related">',
}


def tag_counts(h):
    return {t: len(re.findall(r"<%s\b" % t, h)) for t in ("li", "ul", "a", "div", "section", "p", "h2", "span")}


def insert_before_first_ul_close(h, marker, row):
    i = h.find(marker)
    if i < 0:
        return None, "マーカーなし"
    j = h.find("</ul>", i)
    if j < 0:
        return None, "</ul>なし"
    return h[:j] + row + h[j:], "ok"


def check(before, after):
    b, a = tag_counts(before), tag_counts(after)
    assert a["li"] == b["li"] + 1, "li が +1 ではない: %s→%s" % (b["li"], a["li"])
    for t in b:
        if t in ("li", "a", "span"):
            continue
        assert a[t] == b[t], "%s の個数が変わった" % t
    assert a["a"] == b["a"] + 1


def main(apply_):
    n = 0
    jobs = [(os.path.join(ROOT, "tools", t, "index.html"), "<!-- TOOL-FAMILY -->", TOOL_ROW % t) for t in TOOLS]
    jobs += [(os.path.join(ROOT, "articles", a, "index.html"), m, ART_ROW) for a, m in ARTICLES.items()]
    for path, marker, row in jobs:
        rel = os.path.relpath(path, ROOT)
        h = io.open(path, encoding="utf-8").read()
        if HUB_URL in h:
            print("  済:", rel); continue
        h2, why = insert_before_first_ul_close(h, marker, row)
        if h2 is None:
            print("  スキップ(%s):" % why, rel); continue
        check(h, h2)
        print("  +", rel)
        if apply_:
            io.open(path, "w", encoding="utf-8", newline="").write(h2); n += 1
    print("\n%s: %d本" % ("適用" if apply_ else "dry-run", n))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main("--apply" in sys.argv)

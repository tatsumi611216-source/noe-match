# -*- coding: utf-8 -*-
"""専業主婦の割合（器具＋データ記事）へ、同じクラスタ（B・生活費）から内部リンクを張る（2026-09-19）

出荷基準「同クラスタからの内部リンク3本以上」への対応。既存の本文には触らず、
<!-- LINE-CTA --> の直前に独立したブロックを1つ足すだけにしてある（他ブランチとの衝突を避けるため）。
判定ロック中のページ（agent/seo/improvement-log.json の locks[]）には張らない。
何度実行しても二重に入らない。
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = "<!-- SENGYOSHUFU-LINK -->"
ANCHOR = "<!-- LINE-CTA -->"
TARGETS = [
    "articles/sengyoshufu-seikatsuhi/index.html",
    "articles/tomobataraki-shokuji-data/index.html",
    "articles/kakeibo-app-fuufu/index.html",
    "tools/seikatsuhi-simulator/index.html",
]
BLOCK = MARK + """
<div style="border-left:3px solid #7c2e42;background:#faf8f5;padding:16px 18px;margin:28px 0;">
<p style="margin:0 0 6px;font-size:.78rem;letter-spacing:.1em;color:#7c2e42;">関連データ</p>
<p style="margin:0;font-size:.92rem;line-height:1.9;color:#3a4148;">
専業主婦世帯と共働き世帯の数を、内閣府の公表値で1985年から1年刻みで確かめられます。
<a href="/tools/sengyoshufu-wariai/" style="color:#7c2e42;font-weight:700;">専業主婦の割合を年別に調べるツール</a>、
<a href="/articles/sengyoshufu-wariai-data/" style="color:#7c2e42;font-weight:700;">専業主婦の割合｜最新値と40年の推移データ</a>。
</p>
</div>
"""


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    locks = {l["path"] for l in json.load(io.open(os.path.join(ROOT, "agent", "seo", "improvement-log.json"),
                                                  encoding="utf-8")).get("locks", [])}
    for t in TARGETS:
        path = "/" + t[:-len("index.html")]
        assert path not in locks, "判定ロック中: %s" % path
        p = os.path.join(ROOT, t)
        h = io.open(p, encoding="utf-8", newline="").read()
        if MARK in h:
            print("skip（済）:", t)
            continue
        # LINE-CTA の目印が無い旧テンプレは </article> の直前に入れる
        anchor = ANCHOR if h.count(ANCHOR) == 1 else "</article>"
        assert h.count(anchor) == 1, (t, anchor, h.count(anchor))
        nl = "\r\n" if "\r\n" in h else "\n"
        h = h.replace(anchor, BLOCK.replace("\n", nl) + anchor)
        io.open(p, "w", encoding="utf-8", newline="").write(h)
        print("added:", t)


if __name__ == "__main__":
    main()

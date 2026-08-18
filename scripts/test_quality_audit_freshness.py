# -*- coding: utf-8 -*-
"""quality_audit.py の鮮度チェックの回帰テスト。

2026-08-19 の改修（CEO承認済み）で入れた。狙いは2つ。

  - 出典の公表時点を正しく書いている記述を拾わないこと（旧実装の誤検知3件）
  - 古い年を「最新」と称している本物の陳腐化を拾うこと（旧実装の見逃し）

真陽性のケースは hatsushon-nenmei-data の**改修前の実物**（コミット 3edf834 の
親）から取っている。旧実装はこの3箇所を1つも検知できていなかった。

    python scripts/test_quality_audit_freshness.py
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from quality_audit import stale_recency, text_of  # noqa: E402

# --- 真陽性: 古い年を「最新」と称している（検知されなければならない）-------
TRUE_POSITIVE = [
    # hatsushon-nenmei-data の改修前の実物
    "<h2>日本の初婚年齢：最新データ（2023年）</h2>",
    "<tr><td>2023年（最新）</td><td>31.1歳</td><td>29.7歳</td></tr>",
    "<li><strong>最新値（2023年）：</strong>男性31.1歳・女性29.7歳</li>",
    # 旧実装でも拾えていた形（退行させない）
    "<title>マッチングアプリ比較【2024年最新版】</title>",
    "<p>2024年現在、この年代の利用者が最も多い。</p>",
    "<p>2023年最新のランキングは次のとおり。</p>",
]

# --- 偽陽性: 出典の公表時点を正しく書いている（検知してはならない）---------
FALSE_POSITIVE = [
    # 旧実装が拾っていた実測3件
    "<p>2024年時点の累計会員数は約1,000万人（各社公式発表）。</p>",
    "<h4>2024年時点での年齢層分布</h4><p>（Noe編集部・2025年ユーザー調査より推計）</p>",
    "<td>2023年時点</td><td>こども家庭庁関連調査・内閣府調査</td>",
    # 出典名を含む括弧の中の年
    "<p>初婚年齢の平均は次のとおり（厚生労働省 人口動態調査・2023年より）。</p>",
    "<p>Tapple：2,000万人（株式会社タップル公式発表・2024年4月末時点）</p>",
    "<p>Omiai：1,000万人（株式会社エニトグループ公式発表・2024年7月時点）</p>",
    # 現行年の表記は対象外
    "<title>ユーブライド完全ガイド【2026年版】</title>",
    "<tr><td>2025年（最新・概数）</td><td>31.0歳</td></tr>",
    "<tr><td>2024年（確定数）</td><td>31.1歳</td></tr>",
]


def main():
    fails = []
    for s in TRUE_POSITIVE:
        if not stale_recency(text_of(s)):
            fails.append("検知できなかった（真陽性）: %s" % s)
    for s in FALSE_POSITIVE:
        hit = stale_recency(text_of(s))
        if hit:
            fails.append("誤検知（偽陽性）: %s -> %s" % (s, hit))

    # 改修前の実物ファイルがあれば、そちらでも3箇所を拾えることを確認する
    # 拡張子を .txt にしてあるのは、GitHub Pages が記事の重複ページとして
    # 配信してしまうのを避けるため（中身はHTMLのスナップショット）。
    fixture = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "fixtures", "hatsushon-nenmei-data.before.html.txt")
    if os.path.exists(fixture):
        hits = stale_recency(text_of(io.open(fixture, encoding="utf-8").read()))
        if len(hits) < 3:
            fails.append("改修前の実物から拾えた箇所が%d件しかない: %s" % (len(hits), hits))
        else:
            print("改修前の実物から検知: %s" % hits)

    if fails:
        print("FAIL %d件" % len(fails))
        for f in fails:
            print("  -", f)
        return 1
    print("PASS  真陽性%d件を検知 / 偽陽性%d件を不検知"
          % (len(TRUE_POSITIVE), len(FALSE_POSITIVE)))
    return 0


sys.exit(main())

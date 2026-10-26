# -*- coding: utf-8 -*-
"""産後リカバリー診断への内部リンクのアンカーを、検索語の語順に寄せる（2026-08-27）。

なぜ必要か: 8/24の実測で「ブランド語アンカーは被リンク数が多くても順位に効かない。
検索語入りの文言に変えると効く」ことが確認できている（被リンク33本で表示0のツール vs
検索語アンカーで9位のツール）。産後リカバリー診断は内部リンク31本を持ちながら
GSC表示0で、アンカーの大半が「産後リカバリー診断｜…」というブランド語先頭だった。

寄せる先は tool_gate.py でGO判定だった実需要語:
  「産後 老けた」（サジェスト4件・SERP上位に器具なし）
  「産後 抜け毛 いつまで」（サジェスト6件・同）
どちらもツール本体が扱っている内容なので、内容と語がずれない。

冪等: 置換後の文言が既に入っているページは変化しない。
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HREF = '/tools/sango-recovery-check/'
NEW = "産後の抜け毛はいつまで？老けたと感じる時期の目安を項目別に出す（無料）"

# <a href="/tools/sango-recovery-check/" ...>ここ</a> の中身だけを差し替える
PAT = re.compile(r'(<a[^>]+href="%s"[^>]*>)(.*?)(</a>)' % re.escape(HREF), re.S)


def main():
    changed = same = 0
    for root, _, files in os.walk(ROOT):
        if os.sep + '.git' in root:
            continue
        for fn in files:
            if fn != 'index.html':
                continue
            p = os.path.join(root, fn)
            h = io.open(p, encoding='utf-8').read()
            if HREF not in h:
                continue
            # トップのツールカードのように <div>/<p> を内包するリンクがある。
            # 中身ごと差し替えるとカードの構造を壊すので、ブロック要素を含む
            # リンクは触らない（2026-08-27にトップを壊して気づいた）。
            def _sub(m):
                if any(t in m.group(2) for t in ('<div', '<p ', '<p>', '<img', '<ul', '<section')):
                    return m.group(0)
                return m.group(1) + NEW + m.group(3)

            new_h, n = PAT.subn(_sub, h)
            if n and new_h != h:
                io.open(p, 'w', encoding='utf-8').write(new_h)
                print('置換 %d件: %s' % (n, os.path.relpath(p, ROOT)))
                changed += 1
            else:
                same += 1
    print('変更 %d本 / 変更なし %d本' % (changed, same))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()

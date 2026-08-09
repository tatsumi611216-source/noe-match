# -*- coding: utf-8 -*-
"""インデックス状態の推移を週次で記録し、脱落（デインデックス）を検出する。

なぜ必要か（2026-08-01）：
index_check.py は「今どうなっているか」の1点しか分からない。1回の検査では
  ・公開直後にインデックスされ、後から外されている
  ・そもそも一度も入っていない
を区別できず、打ち手が変わる。実際、公開月別のインデックス率は
  2026-05: 27%（3ヶ月経過） / 2026-06: 20% / 2026-07: 37%（1ヶ月未満）
と、古い記事ほど低い。脱落が起きている疑いがあるが、1点の観測では確定できない。

このスクリプトは index_check.py の出力を毎週スナップショットとして積み、
前回との差分（新規インデックス／脱落／新規発見）を出す。
2〜3週ぶん貯まれば、脱落が起きているかが実測で確定する。

前提: 先に `python scripts/index_check.py --refresh` を実行して
      agent/index_status.json を最新化しておくこと（--refresh を付けないと
      取得済みURLがスキップされ、状態の変化を拾えない）。

使い方:
    python scripts/index_watch.py           # 差分を表示して履歴に追記
    python scripts/index_watch.py --dry-run # 表示のみ（履歴に書かない）

出力: agent/index_history.json
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATUS = os.path.join(ROOT, 'agent', 'index_status.json')
HISTORY = os.path.join(ROOT, 'agent', 'index_history.json')

INDEXED = 'Submitted and indexed'


def slug(url):
    return url.rstrip('/').split('/')[-1]


def main():
    dry = '--dry-run' in sys.argv
    if not os.path.exists(STATUS):
        print('agent/index_status.json がありません。先に index_check.py を実行してください。')
        return 2
    cur = json.load(open(STATUS, encoding='utf-8'))
    states = {slug(u): v.get('coverageState')
              for u, v in cur.get('results', {}).items() if '/articles/' in u}
    if not states:
        print('記事URLの検査結果が入っていません。index_check.py の実行を確認してください。')
        return 2

    hist = []
    if os.path.exists(HISTORY):
        hist = json.load(open(HISTORY, encoding='utf-8')).get('snapshots', [])

    snap = {
        'fetched_at': cur.get('fetched_at'),
        'total': len(states),
        'indexed': sum(1 for v in states.values() if v == INDEXED),
        'states': states,
    }

    print(f"検査日時 {snap['fetched_at']}")
    print(f"記事 {snap['total']} 本 / インデックス済み {snap['indexed']} 本 "
          f"({snap['indexed'] / snap['total'] * 100:.0f}%)")

    if not hist:
        print('\n前回のスナップショットがありません。今回を基準として記録します。')
        print('※ 差分（脱落の有無）は次回以降に出ます。')
    else:
        prev = hist[-1]
        pv = prev['states']
        gained = sorted(s for s, v in states.items()
                        if v == INDEXED and pv.get(s) not in (None, INDEXED))
        lost = sorted(s for s, v in states.items()
                      if v != INDEXED and pv.get(s) == INDEXED)
        added = sorted(s for s in states if s not in pv)
        print(f"\n前回 {prev['fetched_at']} からの差分")
        print(f"  新規インデックス : {len(gained)}本")
        for s in gained:
            print(f'     + {s}')
        print(f"  脱落（インデックス済 → 外れた）: {len(lost)}本")
        for s in lost:
            print(f'     - {s}  ({states[s]})')
        if added:
            print(f"  新規記事 : {len(added)}本")
        delta = snap['indexed'] - prev['indexed']
        print(f"\n  インデックス数 {prev['indexed']} → {snap['indexed']} ({delta:+d})")
        if lost:
            print('\n⚠ 脱落が発生しています。公開直後に入って後から外れる型なら、'
                  '記事を足しても在庫が増えるだけになるため、公開ペースの判断材料になります。')

    if not dry:
        hist.append(snap)
        hist = hist[-26:]   # 半年ぶん（週次26回）だけ保持してファイルの肥大を防ぐ
        json.dump({'snapshots': hist}, open(HISTORY, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)
        print(f'\n履歴に記録しました（保持 {len(hist)} 件）: agent/index_history.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())

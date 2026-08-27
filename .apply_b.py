# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
q = json.load(open('.queue.json', encoding='utf-8'))
urls = q['need'] + q['rereq']            # 再申請1本は末尾に回す
RQ = 'agent/index_request_queue.md'
t = open(RQ, encoding='utf-8').read()

# 台帳側で「改稿待ちで対象外」と明記されているもの
DEFER_NOTE = {'nashikon-data': '台帳では「改稿待ちで対象外」。8/23に公表値更新済みなので申請可否を人間が判断する'}

lines = []
lines.append('\n---\n')
lines.append('## gsc_verify_queue 判定分（2026-08-26起票・%d本）\n' % len(urls))
lines.append('`agent/gsc_verify_queue.md`「判定結果（2026-08-26）」で **実質未申請** と判定された分。')
lines.append('定期タスク `affiliate-index-verify-20260826` が転記した。**1日10件**で上から消化する。')
lines.append('済んだら行頭に `[済 M/D]` を付ける。\n')
lines.append('判定根拠：8/19の起票から7日が経過した本日、`index_check.py --refresh` で未インデックスのまま')
lines.append('残ったもの。実測則「申請すれば7日で90〜100%／放置なら1.7%」より、申請が通っていないと読む。\n')
lines.append('※Fクラスタ9本（本ファイル「残り（8/26以降）」）と重複するURLがあるが、')
lines.append('  同じ申請なので下の日次バッチに一本化してよい。\n')

for i in range(0, len(urls), 10):
    day = i // 10 + 1
    lines.append('### バッチ%d（%d本）\n' % (day, len(urls[i:i+10])))
    lines.append('```')
    for u in urls[i:i+10]:
        s = u.rstrip('/').rsplit('/', 1)[-1]
        tail = ''
        if u in q['rereq']:
            tail = '   ← 再申請（8/13申請済みだが13日経っても未インデックス）'
        elif s in DEFER_NOTE:
            tail = '   ← ' + DEFER_NOTE[s]
        lines.append(u + tail)
    lines.append('```\n')

lines.append('**除外**：note対照群5本（kaden-rental-vs-kounyu / nurse-konkatsu-soudanjo /')
lines.append('soudanjo-hikaku / tantei-erabikata / yachin-credit-shiharai）は本バッチに含めない。')
lines.append('いずれも gsc_verify_queue.md の2リストに元から入っていなかった。\n')
lines.append('**判定保留**：`/articles/sakuhin-kachikan/`（8/25申請）は申請から7日未経過のため対象外。')
lines.append('9月上旬に再確認する。')

open(RQ, 'w', encoding='utf-8').write(t.rstrip('\n') + '\n' + '\n'.join(lines) + '\n')
print('B欄へ %d本を %d バッチで転記' % (len(urls), (len(urls) + 9) // 10))

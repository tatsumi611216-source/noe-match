# -*- coding: utf-8 -*-
import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'scripts')
from index_check import classify

res = json.load(open('agent/index_status.json', encoding='utf-8'))['results']
VQ = 'agent/gsc_verify_queue.md'
text = open(VQ, encoding='utf-8').read()

# 7日ルールが適用できない例外（直近に申請記録があるもの）
HOLD = {'sakuhin-kachikan': '8/25', 'shizuoka-niigata-guide': '8/24'}
# 申請記録はあるが7日を過ぎても未インデックス（＝実質未申請ではない・再申請枠）
REREQ = {'garugaru-ki-itsumade': '8/13'}

blocks = re.findall(r'```(.*?)```', text, re.S)
groups = {}
for name, b in zip(['PRIORITY', 'GARUGARU'], blocks):
    urls = [l.strip() for l in b.strip().splitlines() if l.strip()]
    done, need, hold, rereq = [], [], [], []
    for u in urls:
        s = u.rstrip('/').rsplit('/', 1)[-1]
        k, label = classify(res[u])
        if k == 'INDEXED':
            done.append(u)
        elif s in HOLD:
            hold.append((u, k, label, HOLD[s]))
        elif s in REREQ:
            rereq.append((u, k, label, REREQ[s]))
        else:
            need.append((u, k, label))
    groups[name] = dict(urls=urls, done=done, need=need, hold=hold, rereq=rereq)

# --- 1) インデックス済みの行頭に [済] を付ける ---
new = text
for g in groups.values():
    for u in g['done']:
        new = re.sub(r'(?m)^' + re.escape(u) + r'\s*$', '[済] ' + u, new)

# --- 2) 判定結果の節を追記 ---
def fmt(items, tail):
    return '\n'.join('%s  ← %s%s' % (u, lab, tail) for u, k, lab, *rest in
                     [(x[0], x[1], x[2], *(x[3:])) for x in items])

P, G = groups['PRIORITY'], groups['GARUGARU']
n_done = len(P['done']) + len(G['done'])
n_need = len(P['need']) + len(G['need'])
n_hold = len(P['hold']) + len(G['hold'])
n_rereq = len(P['rereq']) + len(G['rereq'])

sec = []
sec.append('\n---\n')
sec.append('## 判定結果（2026-08-26）\n')
sec.append('定期タスク `affiliate-index-verify-20260826` による一回限りの判定。')
sec.append('`scripts/index_check.py --refresh`（2026-08-26 13:56 UTC 取得・216URL）と')
sec.append('`scripts/index_diff.py` の結果を、本ファイルの2リスト（優先63本＋ガルガル群20本＝83本）に突合した。\n')
sec.append('**判定基準**：実測則「申請すれば7日で90〜100%インデックス／放置なら1.7%」に基づき、')
sec.append('8/19の起票から7日が経過した本日なお未インデックスのものを「実質未申請」とみなす。\n')
sec.append('| 区分 | 本数 |')
sec.append('|------|------|')
sec.append('| インデックス済み（行頭に `[済]`） | %d本 |' % n_done)
sec.append('| **実質未申請 → 要申請** | **%d本** |' % n_need)
sec.append('| 申請済みだが7日超で未インデックス → 再申請 | %d本 |' % n_rereq)
sec.append('| 判定保留（申請から7日未経過） | %d本 |' % n_hold)
sec.append('| 合計 | %d本 |\n' % (n_done + n_need + n_rereq + n_hold))
sec.append('`index_diff.py` の群別内訳もこの判定を裏づけている：')
sec.append('Day 4 は100%インデックスで実際に申請されていたが、Day 5〜8 は 20% / 30% / 20% / 40% と')
sec.append('放置群に近い水準にとどまる。**Day 5〜8 の大半は申請されていなかった**と読める。\n')

sec.append('### 要申請（%d本）— 優先リスト由来 %d本\n' % (n_need, len(P['need'])))
sec.append('```')
for u, k, lab in P['need']:
    sec.append('%s  → 要申請（%s）' % (u, lab))
sec.append('```\n')
sec.append('### 要申請 — ガルガル群由来 %d本\n' % len(G['need']))
sec.append('8/15-16に19本申請済みという記録は台帳のどこにも見つからなかった。')
sec.append('この4本は申請記録も無く、7日を大きく過ぎて未インデックスなので実質未申請と判定する。\n')
sec.append('```')
for u, k, lab in G['need']:
    sec.append('%s  → 要申請（%s）' % (u, lab))
sec.append('```\n')

sec.append('### 再申請（%d本）\n' % n_rereq)
sec.append('申請記録が台帳にあるが、7日どころか13日を過ぎても未インデックスのもの。')
sec.append('「実質未申請」ではないが、放置しても入らないことが実測で出ているので再申請する。\n')
sec.append('```')
for u, k, lab, d in P['rereq'] + G['rereq']:
    sec.append('%s  → 再申請（%s・%s申請済み）' % (u, lab, d))
sec.append('```\n')

sec.append('### 判定保留（%d本）\n' % n_hold)
sec.append('未インデックスだが、申請から7日が経っていないため本判定の対象外。9月上旬に再確認する。\n')
sec.append('```')
for u, k, lab, d in P['hold'] + G['hold']:
    sec.append('%s  （%s申請済み・%s）' % (u, d, lab))
sec.append('```\n')
sec.append('※note対照群5本（kaden-rental-vs-kounyu / nurse-konkatsu-soudanjo / soudanjo-hikaku /')
sec.append('tantei-erabikata / yachin-credit-shiharai）は本タスクでは申請対象にしない。')
sec.append('いずれも本ファイルの2リストには含まれていなかった。\n')
sec.append('※本タスクは判定のみ。GSCでの申請操作は毎朝8:00の定期タスク')
sec.append('`affiliate-gsc-request-20260823` が index_request_queue.md のB欄から消化する。')

new = new.rstrip('\n') + '\n' + '\n'.join(sec) + '\n'
open(VQ, 'w', encoding='utf-8').write(new)
json.dump({'need': [u for u, k, l in P['need'] + G['need']],
           'rereq': [u for u, k, l, d in P['rereq'] + G['rereq']],
           'n_done': n_done, 'n_need': n_need, 'n_rereq': n_rereq, 'n_hold': n_hold},
          open('.queue.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('済 %d / 要申請 %d / 再申請 %d / 保留 %d' % (n_done, n_need, n_rereq, n_hold))

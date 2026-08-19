# インデックス申請キュー（2026-08-09制定）

人間が毎日ここを見て、Search Console から申請する。**1日10本まで。**

手順：Search Console 上部の検索窓にURLを貼る → Enter → 「インデックス登録をリクエスト」。

済んだら「申請済み」欄へ移し、`agent/index_requests_done.json` に日付を記録する。

**なぜこれをやるのか**：申請済み群と申請待ち群を対照して測った結果、
**7日で 90〜100% インデックスされる vs 8日で 1.7%** という差が出た。
記事を書いても申請しなければ読まれない。詳細は `agent/rule_changes.md`「2026-08-09」。

---

## A. 既存記事のバックログ（Day 4〜8・50本）

**リストの正本は `agent/index_request_batches.md` の `### Day 4`〜`### Day 8`。**
ここには転記しない（二重管理するとずれる）。上から順に1日1グループずつ消化する。

| Day | 状態 |
|-----|------|
| 0〜3 | ✅ 申請済み（2026-08-01 / 08-02 / 08-08 / 08-09） |
| 4〜8 | ⚠️ **状態不明（2026-08-19 訂正）**。GSC実機の抜き取り3本（Day4先頭・Day5・Day8末尾）は「リクエスト済み」だったが、done.json は pending のまま＝人間の報告が無い。**3本の抜き取りで50本を済みと断定したのは誤り**。要照合リストは agent/gsc_verify_queue.md。1日10件ずつGSCで照合し、未申請なら申請する |

**除外：note専用テスト群5本には絶対に申請しない**
（`kaden-rental-vs-kounyu` / `nurse-konkatsu-soudanjo` / `soudanjo-hikaku` /
`tantei-erabikata` / `yachin-credit-shiharai`）。
noteがクロール需要を動かすかを測っている対照群で、申請すると壊れる。

---

## B. 新規公開記事（毎回の記事生成で追加される）

エージェントは記事を公開したら、その日のうちにここへ追記すること
（AGENT.md「あなたのタスク」手順9）。**週2本なら1回30秒×2。**

### 未申請

（なし——2026-08-19にGSC実機で全件「リクエスト済み」を確認し、下の申請済みへ移した）

```
```
（konkatsu-soudan-saki / pocchari-konkatsu は 2026-08-09 公開。zexy-enmusubi-data / pairs-kaiin-data は 2026-08-10 公開。omiai-danjohi-data / with-nenreiso-data は 2026-08-17 公開。Day バックログとは別枠で申請してよい）

### 申請済み

| URL | 公開日 | 申請日 | 7日後の状態 |
|-----|-------|-------|-----------|
| /articles/garugaru-ki-guide/ | 2026-08-13 | 2026-08-13 | |
| /tools/garugaru-check/ | 2026-08-13 | 2026-08-13 | |
| /articles/garugaru-ki-itsumade/ | 2026-08-13 | 2026-08-13 | |
| /articles/sango-crisis-guide/ | 2026-08-13 | 2026-08-13 | |
| /tools/fugenbyo-check/ | 2026-08-13 | 2026-08-13 | |
| /tools/saigenbyo-check/ | 2026-08-13 | 2026-08-13 | |
| /articles/konkatsu-soudan-saki/ | 2026-08-09 | 〜2026-08-19確認 | |
| /articles/pocchari-konkatsu/ | 2026-08-09 | 〜2026-08-19確認 | |
| /articles/zexy-enmusubi-data/ | 2026-08-10 | 〜2026-08-19確認 | |
| /articles/pairs-kaiin-data/ | 2026-08-10 | 〜2026-08-19確認 | |
| /articles/omiai-danjohi-data/ | 2026-08-17 | 〜2026-08-19確認 | |
| /articles/with-nenreiso-data/ | 2026-08-17 | 〜2026-08-19確認 | |
| /tools/koisaihi-simulator/ | 2026-08-18 | **2026-08-19** | |
| /articles/marrish-saikon-data/（再クロール） | — | **2026-08-19** | |
| /tools/rikongo-seikatsuhi/ | 2026-08-16 | **2026-08-19** | |
| | | | |

---

## 消化が終わったら

Day 8 の申請から7日後に判定する。

```
python scripts\index_check.py --refresh
python scripts\index_diff.py
```

そのあとは B だけを回す運用になる（週2本＝週2件の申請）。
バックログを抱えない限り、この作業は週に1分で済む。

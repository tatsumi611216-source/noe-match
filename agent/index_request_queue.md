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
| **4** | **← 次はここ** |
| 5〜8 | 未申請 |

**除外：note専用テスト群5本には絶対に申請しない**
（`kaden-rental-vs-kounyu` / `nurse-konkatsu-soudanjo` / `soudanjo-hikaku` /
`tantei-erabikata` / `yachin-credit-shiharai`）。
noteがクロール需要を動かすかを測っている対照群で、申請すると壊れる。

---

## B. 新規公開記事（毎回の記事生成で追加される）

エージェントは記事を公開したら、その日のうちにここへ追記すること
（AGENT.md「あなたのタスク」手順9）。**週2本なら1回30秒×2。**

### 未申請


```
https://www.noe-match.com/articles/konkatsu-soudan-saki/
https://www.noe-match.com/articles/pocchari-konkatsu/
https://www.noe-match.com/articles/zexy-enmusubi-data/
https://www.noe-match.com/articles/pairs-kaiin-data/
```
（konkatsu-soudan-saki / pocchari-konkatsu は 2026-08-09 公開。zexy-enmusubi-data / pairs-kaiin-data は 2026-08-10 公開。Day バックログとは別枠で申請してよい）

### 申請済み

| URL | 公開日 | 申請日 | 7日後の状態 |
|-----|-------|-------|-----------|
| /articles/garugaru-ki-guide/ | 2026-08-13 | 2026-08-13 | |
| /tools/garugaru-check/ | 2026-08-13 | 2026-08-13 | |
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

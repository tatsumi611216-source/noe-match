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

---

## 2026-08-22 の実測でわかったこと（重要・運用の前提が変わる）

### 1. 未登録69件は「2種類」あり、対処が違う

`agent/index_status.json`（8/22取得）の coverageState 内訳：

| 状態 | 件数 | 意味 | 申請は効くか |
|---|---|---|---|
| Submitted and indexed | 138 | 登録済み | — |
| **Discovered - currently not indexed** | **51** | Googleは見つけたうえで登録していない | **効きにくい**。発見の問題ではないため |
| **URL is unknown to Google** | **17** | Googleがまだ認識していない | **効く**。優先クロールキューに入る |
| Crawled - currently not indexed | 1 | クロール済みだが未登録 | 効きにくい |

**「未登録57本を申請する」という運用は、実は51本が的外れだった。**
申請で動くのは「認識されていない」側だけ。「検出済み・未登録」はGoogleが
品質・優先度で判断して見送っている状態なので、申請ではなく記事側の問題。

### 2. 再申請は無意味（Google自身が明言）

申請完了ダイアログの原文：
> URL を優先クロール キューに追加しました。**ページを複数回送信してもキューの順番や優先順位は変わりません。**

→ **一度申請した記事を再申請する作業は、やるだけ無駄。** 台帳の照合キューで
「済みかどうか」を確認していたのは正しいが、確認の目的は「二重申請を避ける」ではなく
**「まだ申請していないものを見つける」**であると理解し直す。

### 3. 1日の割り当ては約11件（実測）

11件目まで通り、12件目で
> 1 日の割り当て量を超えたため、リクエストを処理できませんでした。明日、もう一度お試しください。

**台帳の「1日10本まで」は実測とほぼ一致していた。** この上限は据え置く。

### 4. sitemapは正常。ただし綴り間違いの登録が残っている

| サイトマップ | 状態 | 検出ページ数 | 最終読込 |
|---|---|---|---|
| /sitemap.xml | 成功 | 206 | 2026/08/22 |
| /sitemap-all.xml | 成功 | 197 | 2026/08/22 |
| **/sitemap.xm** | **取得できませんでした** | 0 | （2026/07/26に送信・以降ずっと失敗） |

`/sitemap.xm`（末尾の l が欠落）が7/26から失敗し続けている。
**害はないが、サイトマップレポートに恒久的なエラーが1件出たままになる。**
削除はCEO判断を要するため未実施。

### 5. ドメインプロパティは未登録

`sc-domain:noe-match.com` は「このプロパティへのアクセス権がありません」＝未登録。
登録するとhttp/https・www有無・全サブドメインをまとめて見られるが、
**DNSのTXTレコード認証が必要**。DNSは dnsv.jp（お名前.com系）なので
レジストラへのログインが要る。CEO対応事項。

## 2026-08-22 に申請した11件

| URL | 申請前の状態 |
|---|---|
| /articles/junyuchu-biyou/ | 新規公開 |
| /articles/sango-biyou-itsukara/ | 新規公開 |
| /articles/garugaru-doukyo/ | 検出-未登録 |
| /articles/garugaru-ueno-ko/ | 未認識 |
| /articles/maternity-blue-chigai/ | 未認識 |
| /articles/sango-rikon/ | 未認識 |
| /articles/anti-fraud/ | 未認識 |
| /articles/faq-troubleshooting/ | 未認識 |
| /articles/kekkon-jutaku-loan/ | 未認識 |
| /articles/keiyaku-jisshitsu-wana/ | 未認識 |
| /articles/pairs-marriage-data/ | 未認識 |

**明日に持ち越し（未申請・未認識の残り4件）**：
pet-konkatsu / shinkon-osechi / shizuoka-niigata-guide / success-stories

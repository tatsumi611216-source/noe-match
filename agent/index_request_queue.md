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

**除外：note専用テスト群5本には絶対に申請しない** ← **2026-08-22 CEO判断で一部解除**。
note実験は 2026-08-09 に打ち切り済み（`agent/note_group_final_state_20260809.md`）のため
禁止の根拠は消えている。**`nurse-konkatsu-soudanjo` は「看護師 婚活」39位・27表示で
白衣コン（4万円・提携中最高単価）が載る収益ページ**なので、8/22に寄せ直しのうえ申請対象に戻した。
残り4本（kaden/soudanjo-hikaku/tantei/yachin）も禁止の根拠は無いが、優先度が低いので後回し。

（旧記載）
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

### 1. 未登録69件の内訳（※当初の解釈は誤り。2026-08-22に訂正済み）

`agent/index_status.json`（8/22取得）の coverageState 内訳：

| 状態 | 件数 | 意味 |
|---|---|---|
| Submitted and indexed | 138 | 登録済み |
| **Discovered - currently not indexed** | **51** | Googleは把握しているが、まだ登録していない |
| **URL is unknown to Google** | **17** | Googleがまだ認識していない |
| Crawled - currently not indexed | 1 | クロール済みだが未登録 |

**⚠️ 訂正（重要）**：この内訳を最初に書いたとき、「検出済み・未登録の51件は
Googleが品質で見送っているので申請は効きにくい」と結論したが、**これは誤り**だった。
一般的なSEOの通説をそのまま当てはめただけで、本サイトの実測を見ていなかった。

**実測（8/22・申請日が判明している30本で検証）**：

| 申請群 | 登録率 |
|---|---|
| Day 1（8/02申請） | 10/10 ＝ **100%** |
| Day 2（8/08申請） | 5/10 ＝ 50% |
| Day 3（8/09申請） | 10/10 ＝ **100%** |
| **合計** | **25/30 ＝ 83.3%** |

**申請すればほぼ登録される。** 台帳冒頭の「7日で90〜100% vs 8日で1.7%」という
既存の対照実験とも一致する。「検出済み・未登録」は品質で落とされた状態ではなく、
**申請するまで優先クロールキューに入らないだけ**と解釈するのが実態に合う。

したがって運用は変えない——**未登録は全部、上限まで申請していく。**

### 2. 再申請は無意味（Google自身が明言）

申請完了ダイアログの原文：
> URL を優先クロール キューに追加しました。**ページを複数回送信してもキューの順番や優先順位は変わりません。**

→ **一度申請した記事を再申請する作業は、やるだけ無駄。** 台帳の照合キューで
「済みかどうか」を確認していたのは正しいが、確認の目的は「二重申請を避ける」ではなく
**「まだ申請していないものを見つける」**であると理解し直す。

**注意**：この「複数回送信しても変わらない」は**同じURLの再送信**についての話であり、
**初回申請が効かないという意味ではない**。上の実測どおり初回申請は83〜100%効く。
この2つを混同しないこと（8/22に一度混同して誤った結論を書いた）。

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

## 2026-08-22 追記：割り当ては時間窓で回復する（実測）

11件目で上限→数時間後に2件通る→再び上限。**1日の上限は固定11件ではなく、
24時間の移動窓で回復する**と見るのが実態に近い。申請は「朝と夜の2回に分ける」と
1日の処理数を増やせる可能性がある（未検証・明日試す）。本日の合計は13件。
追加で通った2件：pet-konkatsu / shinkon-osechi。

## 2026-08-23 に申請する（8/22は割り当て上限で持ち越し）

```
https://www.noe-match.com/articles/nurse-konkatsu-soudanjo/   ← 寄せ直し済み・対照群解除・最優先
https://www.noe-match.com/articles/kekkon-houkoku-nengajou/   ← 寄せ直し済み（季節物・10月まで）
https://www.noe-match.com/articles/propose-guide/             ← 寄せ直し済み
https://www.noe-match.com/articles/kyoto-guide/               ← 寄せ直し済み
https://www.noe-match.com/articles/success-rate-data/         ← 寄せ直し済み
https://www.noe-match.com/articles/shizuoka-niigata-guide/    ← 未認識
https://www.noe-match.com/articles/success-stories/           ← 未認識
https://www.noe-match.com/tools/app-kekkonritsu-data/          ← 新規ツール（8/22公開・E核）
https://www.noe-match.com/articles/kekkon-madeno-kikan-data/   ← 8/22公的統計へ差し替え（10.4位・再クロール優先）
https://www.noe-match.com/articles/soudanjo-hikaku/            ← 8/22型A改稿
https://www.noe-match.com/articles/over50-guide/               ← 8/22型A改稿
https://www.noe-match.com/articles/agency-vs-app/              ← 8/22型A改稿
https://www.noe-match.com/tools/kekkon-shikin-keisanki/        ← J核・表示ゼロ。8/23に公表値更新＋ハナユメ結果連動
https://www.noe-match.com/articles/kekkon-okane-data/          ← 8/23公表値へ更新
https://www.noe-match.com/articles/nashikon-data/              ← 8/23公表値へ更新
https://www.noe-match.com/articles/shikijo-erabi-guide/        ← 8/23型A全面改稿（ハナユメ受け皿・78位）
https://www.noe-match.com/articles/gosyugi-shiharai-houhou/    ← 8/23寄せ直し＋4,000字
https://www.noe-match.com/articles/shinkon-ryokou-credit/      ← 8/23寄せ直し＋4,000字
https://www.noe-match.com/articles/age-data/                   ← 8/23型A再構成（48表示・Dの主力）
https://www.noe-match.com/articles/youbride-guide/             ← 8/23料金改定反映＋4,000字
https://www.noe-match.com/articles/marrish-guide/              ← 8/23公表状況＋4,000字
```
※寄せ直した5本は既にインデックス済みだが、タイトル変更の再クロールを早める目的で申請する。

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

- [済 8/25] /articles/tapple-nenreiso-data/　（2026-08-24 公開）
- [済 8/25] /articles/pairs-nenreiso-data/　（2026-08-24 公開）
- [ ] /articles/nagano-guide/　（2026-08-27 公開）
- [ ] /articles/kagoshima-guide/　（2026-08-27 公開）

```
```
（konkatsu-soudan-saki / pocchari-konkatsu は 2026-08-09 公開。zexy-enmusubi-data / pairs-kaiin-data は 2026-08-10 公開。omiai-danjohi-data / with-nenreiso-data は 2026-08-17 公開。Day バックログとは別枠で申請してよい）

### 2026-08-26 判定分（GSC照合キューの実質未申請 37本）

`affiliate-index-verify-20260826` の判定結果。正本は `agent/gsc_verify_queue.md`「判定結果（2026-08-26）」。**上から順に1日10件（上限が出るまで）。**
Googleが一度も認識していない（未認識）ものを先頭に置いた。

**Day A（10本）**

```
[済 8/27] https://www.noe-match.com/articles/compare-price/                    ← Googleがこのページを認識していない
[済 8/27] https://www.noe-match.com/articles/matching-josei-cost-data/         ← Googleがこのページを認識していない
[済 8/27] https://www.noe-match.com/articles/myseed-kuchikomi/                 ← Googleがこのページを認識していない
[済 8/27] https://www.noe-match.com/articles/pairs-guide/                      ← Googleがこのページを認識していない
[済 8/27] https://www.noe-match.com/articles/tapple-guide/                     ← Googleがこのページを認識していない
[済 8/27] https://www.noe-match.com/articles/tapple-vs-pairs/                  ← Googleがこのページを認識していない
[済 8/27] https://www.noe-match.com/articles/tomobataraki-shokuji-data/        ← Googleがこのページを認識していない
[済 8/27] https://www.noe-match.com/articles/with-guide/                       ← Googleがこのページを認識していない
[済 8/27] https://www.noe-match.com/articles/free-vs-paid/                     ← クロール済み・インデックス未登録
[済 8/27] https://www.noe-match.com/articles/konkatsu-roadmap/                 ← クロール済み・インデックス未登録
```

**Day B（10本）**

```
[済 8/27] https://www.noe-match.com/articles/dousei-kaisho/                    ← 検出済み・未クロール
https://www.noe-match.com/articles/dousei-kekkon-hikaku/             ← 検出済み・未クロール
https://www.noe-match.com/articles/first-date-guide/                 ← 検出済み・未クロール
https://www.noe-match.com/articles/fraud-statistics/                 ← 検出済み・未クロール
https://www.noe-match.com/articles/hatsushon-nenmei-data/            ← 検出済み・未クロール
https://www.noe-match.com/articles/kaiin-age-cross-data/             ← 検出済み・未クロール
https://www.noe-match.com/articles/kinsen-kachikan-check/            ← 検出済み・未クロール
https://www.noe-match.com/articles/koninhiyou-guide/                 ← 検出済み・未クロール
https://www.noe-match.com/articles/konkatsu-party-guide/             ← 検出済み・未クロール
https://www.noe-match.com/articles/late-20s-strategy/                ← 検出済み・未クロール
```

**Day C（10本）**

```
https://www.noe-match.com/articles/line-exchange/                    ← 検出済み・未クロール
https://www.noe-match.com/articles/members-data/                     ← 検出済み・未クロール
https://www.noe-match.com/articles/nashikon-data/                    ← 検出済み・未クロール
https://www.noe-match.com/articles/pairs-men/                        ← 検出済み・未クロール
https://www.noe-match.com/articles/pairs-women/                      ← 検出済み・未クロール
https://www.noe-match.com/articles/price-comparison/                 ← 検出済み・未クロール
https://www.noe-match.com/articles/privacy-protection/               ← 検出済み・未クロール
https://www.noe-match.com/articles/profile-text/                     ← 検出済み・未クロール
https://www.noe-match.com/articles/renkatsu-vs-konkatsu/             ← 検出済み・未クロール
https://www.noe-match.com/articles/shinkyo-kagu-yosan/               ← 検出済み・未クロール
```

**Day D（7本）**

```
https://www.noe-match.com/articles/usuge-konkatsu-eikyou/            ← 検出済み・未クロール
https://www.noe-match.com/articles/with-vs-pairs/                    ← 検出済み・未クロール
https://www.noe-match.com/articles/garugaru-ki-itsumade/             ← Googleがこのページを認識していない
https://www.noe-match.com/articles/garugaru-otto-genkai/             ← 検出済み・未クロール
https://www.noe-match.com/articles/garugaru-sangoutsu-chigai/        ← 検出済み・未クロール
https://www.noe-match.com/articles/sango-iraira/                     ← 検出済み・未クロール
https://www.noe-match.com/articles/shinseiji-menkai/                 ← 検出済み・未クロール
```

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
[済 8/24] https://www.noe-match.com/articles/nurse-konkatsu-soudanjo/   ← 寄せ直し済み・対照群解除・最優先  ← 持ち越し（8/23 割り当て上限）
[済 8/24] https://www.noe-match.com/articles/kekkon-houkoku-nengajou/   ← 寄せ直し済み（季節物・10月まで）  ← 持ち越し（8/23 割り当て上限）
[済 8/24] https://www.noe-match.com/articles/propose-guide/             ← 寄せ直し済み  ← 持ち越し（8/23 割り当て上限）
[済 8/24] https://www.noe-match.com/articles/kyoto-guide/               ← 寄せ直し済み  ← 持ち越し（8/23 割り当て上限）
[済 8/24] https://www.noe-match.com/articles/success-rate-data/         ← 寄せ直し済み  ← 持ち越し（8/23 割り当て上限）
[済 8/24] https://www.noe-match.com/articles/shizuoka-niigata-guide/    ← 未認識  ← 持ち越し（8/23 割り当て上限）
[済 8/24] https://www.noe-match.com/articles/success-stories/           ← 未認識  ← 持ち越し（8/23 割り当て上限）
[済 8/23] https://www.noe-match.com/tools/app-kekkonritsu-data/          ← 新規ツール（8/22公開・E核）  ← [済 8/23]
https://www.noe-match.com/articles/kekkon-madeno-kikan-data/   ← 8/22公的統計へ差し替え（10.4位・再クロール優先）  ← [済 8/23]
https://www.noe-match.com/articles/soudanjo-hikaku/            ← 8/22型A改稿  ← 持ち越し（8/23 割り当て上限）
[済 8/24] https://www.noe-match.com/articles/over50-guide/               ← 8/22型A改稿  ← 持ち越し（8/23 割り当て上限）
[済 8/24] https://www.noe-match.com/articles/agency-vs-app/              ← 8/22型A改稿  ← 持ち越し（8/23 割り当て上限）
[済 8/24] https://www.noe-match.com/tools/kekkon-shikin-keisanki/        ← J核・表示ゼロ。8/23に公表値更新＋ハナユメ結果連動
https://www.noe-match.com/articles/kekkon-okane-data/          ← 8/23公表値へ更新
https://www.noe-match.com/articles/nashikon-data/              ← 8/23公表値へ更新
https://www.noe-match.com/articles/shikijo-erabi-guide/        ← 8/23型A全面改稿（ハナユメ受け皿・78位）
https://www.noe-match.com/articles/gosyugi-shiharai-houhou/    ← 8/23寄せ直し＋4,000字
https://www.noe-match.com/articles/shinkon-ryokou-credit/      ← 8/23寄せ直し＋4,000字
https://www.noe-match.com/articles/age-data/                   ← 8/23型A再構成（48表示・Dの主力）
https://www.noe-match.com/articles/youbride-guide/             ← 8/23料金改定反映＋4,000字
https://www.noe-match.com/articles/marrish-guide/              ← 8/23公表状況＋4,000字
https://www.noe-match.com/articles/omiai-guide/                ← 8/23料金・統計を公式値に（15.5位）
https://www.noe-match.com/articles/compare-popular/            ← 8/23抜け殻節を型Aに
```
※寄せ直した5本は既にインデックス済みだが、タイトル変更の再クロールを早める目的で申請する。

### 2026-08-23 実行結果（自動タスク）

割り当て上限に到達したため **2件成功・11件持ち越し** で打ち切り。

| # | URL | 結果 |
|---|-----|------|
| 1 | /tools/app-kekkonritsu-data/ | ✅ 優先クロールキューに追加 |
| 2 | /articles/kekkon-madeno-kikan-data/ | ✅ 優先クロールキューに追加 |
| 3 | /articles/nurse-konkatsu-soudanjo/ | ❌「割り当て量を超えています」→ここで打ち切り |
| 4〜13 | 残り10本 | 未実行（持ち越し） |

3本目でダイアログ「1日の割り当て量を超えたため、リクエストを処理できませんでした」。
8/22 は11件目で上限だったので、**8/22 夜の申請分が24時間窓にまだ残っている**状態。
再試行・アカウント切替は行っていない。

※この節の残り9本（kekkon-shikin-keisanki / kekkon-okane-data / nashikon-data /
shikijo-erabi-guide / gosyugi-shiharai-houhou / shinkon-ryokou-credit / age-data /
youbride-guide / marrish-guide）は 8/23 の自動タスクの割り当て対象外。改稿後に別途申請する。

## Fクラスタ（集客装置）の未登録分（2026-08-23起票・8/24以降に1日上限まで）

```
[済 8/25] https://www.noe-match.com/articles/women-strategy/
[済 8/25] https://www.noe-match.com/articles/with-women/
[済 8/25] https://www.noe-match.com/articles/sakuhin-kachikan/
[済 8/25] https://www.noe-match.com/articles/safety-guide/
https://www.noe-match.com/articles/profile-text/
https://www.noe-match.com/articles/privacy-protection/
https://www.noe-match.com/articles/photo-tips/
https://www.noe-match.com/articles/pairs-women/
https://www.noe-match.com/articles/pairs-men/
https://www.noe-match.com/articles/line-exchange/
https://www.noe-match.com/articles/fraud-statistics/
https://www.noe-match.com/articles/first-date-guide/
https://www.noe-match.com/articles/anti-fraud/
```
※ 8/22までに申請済みのものは「リクエスト済み」表示でスキップされる。Fは26本中16本が未登録で、クリック0の主因。

## 新規ツール（2026-08-23公開）

```
[済 8/24] https://www.noe-match.com/tools/sango-recovery-check/
```

## ツール改名分（2026-08-23・再クロール優先）

```
[済 8/24] https://www.noe-match.com/tools/kekkon-shikin-keisanki/
[済 8/24] https://www.noe-match.com/tools/koisaihi-simulator/
[済 8/24] https://www.noe-match.com/tools/seikatsuhi-simulator/
[済 8/24] https://www.noe-match.com/tools/rikongo-seikatsuhi/
[済 8/25] https://www.noe-match.com/tools/soudanjo-simulator/
[済 8/25] https://www.noe-match.com/tools/kekkon-yarukoto/
```
※「計算機／シミュレーター」という検索されない機能名から、検索される言い方（自己負担 平均／デート代 平均／二人暮らし 生活費／養育費 いくら／結婚相談所 成婚料／結婚 準備 リスト）へタイトル・h1・descriptionを改名。本体は無変更。

## 2026-08-23 申請実績

- [済 8/23] /tools/seikatsuhi-simulator/（8/22時点で未認識だったため最優先。成功）
- [済 8/23] /tools/app-kekkonritsu-data/（窓の回復後に1件通過）
- 3件目（kekkon-madeno-kikan-data）で再び上限。**以降は毎朝8:00の定期タスク `affiliate-gsc-request-20260823` が台帳の未申請を上限まで自動処理する**（8/23 CEO承認で一回限り→毎日に変更）


## 産後周辺記事（8/23生成・未申請）
- [済 8/24] /articles/sango-nukege-itsu-modoru/
- [済 8/25] /articles/sango-fukeru-taisaku/
- [済 8/25] /articles/sango-taikei-itsu-modoru/
- [済 8/25] /tools/hoikuen-tensu-nerima/（8/24新設・練馬区保育園点数ツール）

## 2026-08-24 実行結果（自動タスク affiliate-gsc-request-20260823）

**14件成功・15件目で割り当て上限に到達し打ち切り。** 8/22の11件・8/23の2件を上回り、本タスク開始以来の最多。

| # | URL | 結果 |
|---|-----|------|
| 1 | /articles/nurse-konkatsu-soudanjo/ | ✅ 優先クロールキューに追加 |
| 2 | /articles/kekkon-houkoku-nengajou/ | ✅ |
| 3 | /articles/propose-guide/ | ✅ |
| 4 | /articles/kyoto-guide/ | ✅ |
| 5 | /articles/success-rate-data/ | ✅ |
| 6 | /articles/shizuoka-niigata-guide/ | ✅ |
| 7 | /articles/success-stories/ | ✅ |
| 8 | /articles/over50-guide/ | ✅ |
| 9 | /articles/agency-vs-app/ | ✅ |
| 10 | /tools/sango-recovery-check/ | ✅ |
| 11 | /tools/kekkon-shikin-keisanki/ | ✅ |
| 12 | /tools/koisaihi-simulator/ | ✅ |
| 13 | /tools/seikatsuhi-simulator/ | ✅ |
| 14 | /tools/rikongo-seikatsuhi/ | ✅ |
| 15 | /tools/soudanjo-simulator/ | ❌「割り当て量を超えています」→ここで打ち切り |

再試行・アカウント切替は行っていない。`soudanjo-hikaku` は note対照群の残り4本に含まれるため
台帳ルールどおりスキップした（`nurse-konkatsu-soudanjo` のみ解除済み）。

### 残り（8/25以降）

- ツール改名分：/tools/soudanjo-simulator/ ・ /tools/kekkon-yarukoto/
- Fクラスタ13本：women-strategy / with-women / sakuhin-kachikan / safety-guide / profile-text /
  privacy-protection / photo-tips / pairs-women / pairs-men / line-exchange / fraud-statistics /
  first-date-guide / anti-fraud
- 産後周辺4本：sango-nukege-itsu-modoru / sango-fukeru-taisaku / sango-taikei-itsu-modoru /
  tools/hoikuen-tensu-nerima
- 改稿待ちで対象外のまま：kekkon-okane-data / nashikon-data / shikijo-erabi-guide /
  gosyugi-shiharai-houhou / shinkon-ryokou-credit / age-data / youbride-guide / marrish-guide /
  omiai-guide / compare-popular

### 実測メモ：1日の上限は11件固定ではない

8/22は11件目、8/23は3件目で上限だったが、本日は**14件通った**。
「1日◯件」ではなく24時間移動窓での回復とする 8/22 の見立てを支持する。
台帳冒頭の「1日10本まで」は下限の目安であって、実際は**上限が出るまで回すのが正しい**。


※8/24 手動申請1件で割り当て上限（「割り当て量を超えています」表示）。残る3件（sango-fukeru-taisaku／sango-taikei-itsu-modoru／hoikuen-tensu-nerima）は8/25朝8:00の定期タスクで申請する。

### 2026-08-25 追加分（申請待ち）

- [済 8/25] /tools/daredemo-tsuen-jichitai/（新規公開・最優先）
- [済 8/25] /tools/hoikuen-tensu-nerima/（8/24時点で「検出-インデックス未登録」）
- /tools/sango-recovery-check/（8/24時点で「URL は Google に認識されていません」）

## 2026-08-25 実行結果（自動タスク affiliate-gsc-request-20260823）

**12件成功・13件目で割り当て上限に到達し打ち切り。**

| # | URL | 結果 |
|---|-----|------|
| 1 | /tools/daredemo-tsuen-jichitai/ | ✅ 優先クロールキューに追加 |
| 2 | /articles/tapple-nenreiso-data/ | ✅ |
| 3 | /articles/pairs-nenreiso-data/ | ✅ |
| 4 | /tools/soudanjo-simulator/ | ✅ |
| 5 | /tools/kekkon-yarukoto/ | ✅ |
| 6 | /articles/sango-fukeru-taisaku/ | ✅（1回目は送信エラー・再実行で成功） |
| 7 | /articles/sango-taikei-itsu-modoru/ | ✅ |
| 8 | /tools/hoikuen-tensu-nerima/ | ✅（1回目は送信エラー・再実行で成功） |
| 9 | /articles/women-strategy/ | ✅ |
| 10 | /articles/with-women/ | ✅ |
| 11 | /articles/sakuhin-kachikan/ | ✅ |
| 12 | /articles/safety-guide/ | ✅ |
| 13 | /articles/profile-text/ | ❌「割り当て量を超えています」→ここで打ち切り |

再試行・アカウント切替は行っていない（送信エラー2件のみ、同一URLを1回だけ再実行）。

### 実測メモ：送信エラーは割り当て上限とは別物

2件で「インデックス登録リクエストの送信中に問題が発生しました。しばらくしてから
もう一度お試しください」が出たが、いずれも**同じURLを1回やり直しただけで成功**した。
「割り当て量を超えています」とは別の一過性エラーなので、打ち切り条件に含めない。

### 残り（8/26以降）

- Fクラスタ9本：profile-text / privacy-protection / photo-tips / pairs-women / pairs-men /
  line-exchange / fraud-statistics / first-date-guide / anti-fraud
- 改稿待ちで対象外のまま：kekkon-okane-data / nashikon-data / shikijo-erabi-guide /
  gosyugi-shiharai-houhou / shinkon-ryokou-credit / age-data / youbride-guide / marrish-guide /
  omiai-guide / compare-popular
- note対照群の残り4本（kaden / soudanjo-hikaku / tantei / yachin）は台帳ルールどおり申請しない

### 2026-08-25 申請実施（Chrome MCP経由・4本すべて「インデックス登録をリクエスト済み」を確認）

| URL | 申請時点の状態 |
|---|---|
| /tools/daredemo-tsuen-jichitai/ | すでに登録済み → 内容を6区→43自治体に大幅更新したため再リクエスト |
| /articles/daredemo-tsuen-ryokin/ | 未登録（URLがGoogleに認識されていない）→ 新規リクエスト |
| /tools/hoikuen-tensu-nerima/ | 8/24は「検出-未登録」だったが**登録済みに変化**していた → 再リクエスト |
| /tools/sango-recovery-check/ | 8/24は「Google未認識」だったが**登録済みに変化**していた → 再リクエスト |

**手順のメモ**: GSCの `inspect?resource_id=...&id=<URL>` 形式のディープリンクは404になる。
上部の検索バーに入力してEnterする経路しかない。モーダルが開いている状態でEnterを押すと
「公開URLをテスト」が走ってしまうので、必ずサマリー画面に戻してから検索バーに入れ直す。
リクエストボタンは `find` でrefを取ってrefクリックするのが確実（座標クリックは効かないことがある）。

## 2026-08-27 実行結果（自動タスク affiliate-gsc-request-20260823）

**11件成功、12件目で割り当て上限に到達し打ち切り。** 処理順は台帳の「2026-08-26 判定分」Day A → Day B。

| # | URL | 結果 |
|---|-----|------|
| 1 | /articles/compare-price/ | ✅ 優先クロール キューに追加 |
| 2 | /articles/matching-josei-cost-data/ | ✅ |
| 3 | /articles/myseed-kuchikomi/ | ✅ |
| 4 | /articles/pairs-guide/ | ✅ |
| 5 | /articles/tapple-guide/ | ✅ |
| 6 | /articles/tapple-vs-pairs/ | ✅ |
| 7 | /articles/tomobataraki-shokuji-data/ | ✅ |
| 8 | /articles/with-guide/ | ✅ |
| 9 | /articles/free-vs-paid/ | ✅ |
| 10 | /articles/konkatsu-roadmap/ | ✅ |
| 11 | /articles/dousei-kaisho/ | ✅ |
| 12 | /articles/dousei-kekkon-hikaku/ | ❌「割り当て量を超えています」→ここで打ち切り |

Day A（10本）は全件通過。再試行・アカウント切替は行っていない（送信エラーは0件）。

### 残り（8/28以降）

- 2026-08-26 判定分の残26本：Day B の9本（dousei-kekkon-hikaku / first-date-guide / fraud-statistics /
  hatsushon-nenmei-data / kaiin-age-cross-data / kinsen-kachikan-check / koninhiyou-guide /
  konkatsu-party-guide / late-20s-strategy）と Day C（10本）・Day D（7本）
- Fクラスタ9本：profile-text / privacy-protection / photo-tips / pairs-women / pairs-men /
  line-exchange / fraud-statistics / first-date-guide / anti-fraud
  ※うち profile-text / privacy-protection / pairs-women / pairs-men / line-exchange は Day C、
  fraud-statistics / first-date-guide は Day B と重複する。Day 順で処理すればFも埋まる
- 改稿待ちで対象外のまま：kekkon-okane-data / nashikon-data / shikijo-erabi-guide /
  gosyugi-shiharai-houhou / shinkon-ryokou-credit / age-data / youbride-guide / marrish-guide /
  omiai-guide / compare-popular
- note対照群の残り4本（kaden / soudanjo-hikaku / tantei / yachin）は台帳ルールどおり申請しない

### 実測メモ：上限は11件（8/22と同じ）

8/24は14件、8/25は12件、8/23は2件、8/27は11件。
24時間移動窓での回復という見立てと矛盾しない。上限が出るまで回す運用を維持する。

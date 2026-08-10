# note専用テスト群の最終状態（2026-08-09・実験はここで打ち切り）

## 何が起きたか

`index_request_batches.md` で設定された **note専用テスト群5本**（Google申請を絶対にしない群）のうち
**4本に、2026-08-09 に誤ってGoogleインデックス申請を出した**。

原因: 別セッションがGSC申請リストを作る際、単価順で機械的に並べただけで
`index_requests_done.json` の `note_group_must_not_be_requested` を確認しなかった。

→ **この4本について「noteだけでクロールが動くか」は、今後もう測れない。**

## 救えたもの：申請直前（2026-08-09）の実測値

申請の直前に、たまたまURL検査APIで5本すべての状態を測っていた。
**8/1のテスト群設定から8日間、note施策のみを与えた結果**として、この数字は有効に使える。

| 記事 | 2026-08-09 の状態（申請前） |
|---|---|
| nurse-konkatsu-soudanjo | **Submitted and indexed** ← Google申請なしでインデックスされた |
| soudanjo-hikaku | Discovered - currently not indexed |
| tantei-erabikata | Discovered - currently not indexed |
| yachin-credit-shiharai | Discovered - currently not indexed |
| kaden-rental-vs-kounyu | **URL is unknown to Google** ← 7/28公開で12日経っても未認識 |

**note施策のみ・8日間の結果 ＝ 5本中1本（20%）がインデックス。**
うち1本は認識すらされていない。

## この数字の使い方

Google申請を出した群の同期間のインデックス率と比較すれば、
「申請に効果があるか」は依然として判定できる。必要なのは申請群側の同条件の集計。

比較対象として使えるのは 8/1（Day 0・10本）と 8/2 の群。
8/8 と 8/9 の申請分は経過日数が足りないので、数日後に再測すること。

## 再発防止

**GSC申請リストを作る前に必ず読むファイル:**
- `agent/index_requests_done.json` … `note_group_must_not_be_requested` と実施日
- `agent/index_request_batches.md` … 群の割り振り
- `agent/index_experiment.md` … 実験設計

単価やクエリの重要度だけでリストを作らないこと。
このリポジトリは複数セッションが同時に触るため、**先行する実験設計が存在しうる前提で確認する。**

## 未申請のまま残った1本

`konkatsu-party-guide` は今回の申請対象から外れた（ユーザー判断）。
テスト群ではないので、通常の申請対象として扱ってよい。

# ツール監査：インデックス × 流入 × 内部リンク

**自動生成: `scripts/tools_audit.py`。手で編集しない。**

GSC期間: 2026-07-21 〜 2026-08-18（取得 2026-08-20） / index_status 取得: 2026-08-20

ツール 11本 / インデックス済み 8本 / 未インデックス 3本 / 総表示 36・総クリック 4

## 一覧

| 表示 | クリック | 平均順位 | 内部リンク | インデックス | ツール |
|---|---|---|---|---|---|
| 27 | 3 | 9.0 | 22 | Submitted and indexed | `garugaru-check`<br>ガルガル期診断 |
| 4 | 1 | 15.5 | 10 | Submitted and indexed | `nyuseki-calendar`<br>入籍日カレンダー2026〜2030 |
| 2 | 0 | 6.0 | 5 | Discovered - currently not indexed ⚠ | `saigenbyo-check`<br>帰宅恐怖症・妻源病チェックシート |
| 1 | 0 | 53.0 | 8 | Submitted and indexed | `fugenbyo-check`<br>夫源病チェックシート |
| 1 | 0 | 49.0 | 9 | Submitted and indexed | `rikongo-seikatsuhi`<br>離婚後の生活費シミュレーション |
| 1 | 0 | 9.0 | 7 | Submitted and indexed | `soudanjo-simulator`<br>結婚相談所の費用シミュレーション |
| 0 | 0 | — | 35 | URL is unknown to Google ⚠ | `kekkon-shikin-keisanki`<br>結婚費用シミュレーション |
| 0 | 0 | — | 21 | Submitted and indexed | `kekkon-yarukoto`<br>結婚の段取り・やることリスト |
| 0 | 0 | — | 16 | Submitted and indexed | `koisaihi-simulator`<br>デート代・交際費の平均と年間総額 |
| 0 | 0 | — | 71 | Submitted and indexed | `konkatsu-type-shindan`<br>婚活はアプリ・相談所・パーティーのどれ？向き不向きを60秒で診断【無料・登録なし】 |
| 0 | 0 | — | 31 | Discovered - currently not indexed ⚠ | `seikatsuhi-simulator`<br>二人暮らしの生活費 分担シミュレーション |

## ⚠ 未インデックス（読まれる可能性がゼロ）

`agent/index_request_queue.md` の未申請欄に入れて、人間がGSCから申請する。

- **`/tools/saigenbyo-check/`** — Discovered - currently not indexed（確認 2026-08-15）／内部リンク 5本
- **`/tools/kekkon-shikin-keisanki/`** — URL is unknown to Google（確認 2026-08-15）／内部リンク 35本
  - 内部リンクが 35本あってGoogleが認識していない。申請で解消しない場合はリンク先URLの綴り・実URLの200応答・sitemap再送信を順に確認する
- **`/tools/seikatsuhi-simulator/`** — Discovered - currently not indexed（確認 2026-08-20）／内部リンク 31本

## 流入のあるクエリ

| 平均順位 | 表示 | クリック | クエリ | ツール |
|---|---|---|---|---|
| 11.2 | 13 | 1 | ガルガル期 診断 | `garugaru-check` |
| 53.0 | 1 | 0 | 夫源病チェックシート | `fugenbyo-check` |
| 49.0 | 1 | 0 | 熟年離婚後 生活費 シュミレーション | `rikongo-seikatsuhi` |

※ `gsc_data.json` の `by_query_page` は250行上限で切れる。表示の小さいクエリは載らないため、この表は下限値である。

## 読み方（打ち手が正反対になる分岐）

- **内部リンクが多いのに表示ゼロ** … 導線不足ではない。そのクエリで勝てていない。リンクを増やしても変わらないので、勝てるクエリへ看板を掛け替えるか、投資対象から外す
- **未インデックス** … 流入ゼロは「負けた」ではなく「まだ試合をしていない」。申請が先で、内容の評価はその後
- **表示はあるが31位以下** … 収益に一切つながらない。判定指標には使わない（`agent/decision_gate.md`）


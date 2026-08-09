# 部品: file-intake（手元ファイルの取り込み）

- カテゴリ: data ／ 由来: 発注フォームQ3「手元のファイル」に対応部品がなかった欠品補充 ／ 使用実績: 未使用

## 何をする部品か

Excel・PDF・CSV・Word などのファイルを読み取り、後続処理が使える形（表・テキスト）にする。
ファイルの置き場所（Google Drive／ローカル）によって取り方が変わるので、その使い分けを決める。

## 組み込みブロック

```markdown
### ファイルの取り込み

**まず置き場所を確認する。** 発注時に「どこにあるファイルか」を必ず特定しておくこと
（parts/input/spec-drilldown の「対象の特定」）。

#### Google Drive にある場合

1. `search_files` でファイルを探す → fileId を取得
   （クエリ例：`title contains '売上' and mimeType = 'application/vnd.google-apps.spreadsheet'`）
   ※ ファイル名から fileId を推測してはいけない。必ず検索して実物のIDを得る
2. 中身を読む：
   - 自然文として読む → `read_file_content`（スプレッドシート・文書・PDF・画像に対応）
   - 元データとして扱う → `download_file_content`（Google形式は exportMimeType の指定が必要）
3. 取得結果はファイルに保存してから処理する（parts/data/file-per-item）

#### 手元（ローカル）にある場合

ファイル形式ごとに専用スキルを使う：

| 形式 | 使うもの |
|---|---|
| .xlsx / .csv | xlsx スキル |
| .pdf | pdf スキル |
| .docx | docx スキル |
| .pptx | pptx スキル |

#### 共通ルール

- **読む前に必ず1件だけ中身を確認する。** 列名・単位・欠損の有無を掴んでから全件処理に入る
- 列名や書式が想定と違ったら、勝手に解釈せず確認する（parts/safety/hallucination-guard）
- 大量ファイルは1件1ファイルで保存してから統合する（parts/data/file-per-item）
- 読み取れなかったファイルは「未取得」として件数と理由を残す。黙って飛ばさない
```

## カスタマイズポイント

- 案件冒頭で「対象ファイルの一覧」を確定させる。毎回探し直すと事故る
- 定期実行なら、前回以降に更新されたファイルだけを対象にする（`modifiedTime >` で絞る）
- ファイルの構造（列名・シート名）は案件ごとに固定で書き出しておく。推測に頼らない

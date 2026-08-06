# 部品: web-scraping（ブラウザ取得ルール）

- カテゴリ: data ／ 由来: web-data-pipeline ／ 使用実績: web-data-pipeline, keiba-yoso

## 何をする部品か

Webサイトからのデータ取得で、ブラウザツールを正しく使い分ける。
トークン浪費（get_page_text）と取得失敗（CSP制約サイト）を防ぐ。

## 組み込みブロック

```markdown
### ブラウザツールの使い分け

**基本方針：まず `javascript_tool` を試す。undefinedや空が返ったら `find` + `read_page` に切り替える。**

#### `javascript_tool` が使えるサイト（推奨）

DOM操作でピンポイントに抽出。querySelectorAllで行を集め、`|`区切りで結合して返す。

#### `javascript_tool` が動かないサイト → `find` + `read_page`

1. navigate で対象URLを開く
2. find で取得したい要素のキーワード（テーブルID・見出しテキスト）を検索 → ref_id を取得
3. read_page で ref_id を指定（depth=2, max_chars=70000）
4. 出力を {識別子}.txt に保存

#### 共通ルール

- `get_page_text` は絶対に使わない（HTMLゴミでトークン浪費）
- 結果は必ずファイルに保存してからコンテキストに読み込む
- 取得データは {識別子}.txt の形式で1件1ファイル保存（parts/data/file-per-item 参照）

#### サイトごとの動作確認表（案件で埋める）

| サイト | javascript_tool | find+read_page | 推奨 |
|---|---|---|---|
| [対象サイト1] | | | |
```

## カスタマイズポイント

- 案件開始時に必ず動作確認表を埋める（keiba-yoso の netkeiba 表が実例）
- 動かないサイトの発見は資産。表に追記して次回の試行錯誤を省く

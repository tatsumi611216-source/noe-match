---
name: web-data-pipeline
description: >
  Webからデータを定期収集・分析・レポート化する汎用パイプラインスキル。
  「〇〇のデータを定期的に取って分析したい」「Webスクレイピングで情報収集して比較したい」
  「定期レポートを自動化したい」などの依頼に使う。
  競馬・株・不動産・EC価格・スポーツ成績など、「Webからデータを取って何かする」
  という構造の案件はすべてこのスキルをベースにカスタマイズして対応する。
---

# Web Data Pipeline — 汎用ベーススキル

「Webからデータを収集 → ファイルに保存 → 分析 → レポート化」という
共通パターンをまとめたベーススキル。個別案件ではこのスキルの手順を継承し、
対象サイトや分析ロジックをカスタマイズして使う。

## パイプラインの全体構造

```
Step 1: 対象リストの取得（一覧ページ・検索結果など）
  ↓ スクリーニング（取得コスト削減のため、不要なものを早めに除外）
Step 2: 個別データの収集（詳細ページ・API）
  ↓ 1件1ファイル保存 → 並行取得で高速化
Step 3: パース・クレンジング（複数フォーマットを自動判定）
  ↓ キャッシュ活用（前回データを差分更新）
Step 4: 分析・スコアリング（Pythonスクリプト）
Step 5: HTMLレポート生成 → outputs/ に保存
```

---

## ブラウザツールの使い分け

### `javascript_tool` が使えるサイト（推奨）

DOM操作でピンポイントにデータを抽出できる。不要なHTMLゴミを含まず高速。

```javascript
// 典型的な抽出パターン
const rows = document.querySelectorAll('.data-row');
const data = [];
rows.forEach(row => {
  const cells = row.querySelectorAll('td');
  if (cells.length < 3) return;
  data.push([
    cells[0]?.textContent?.trim(),
    cells[1]?.textContent?.trim(),
    cells[2]?.textContent?.trim()
  ].join('|'));
});
data.join('\n');
```

**注意点:**
- `get_page_text` は絶対に使わない（HTMLのゴミが大量に含まれてトークンを浪費）
- 結果はファイルに保存してからコンテキストに読み込む
- 取得データは `{識別子}.txt` の形式で1件1ファイル保存

### `javascript_tool` が動かないサイト → `find` + `read_page`

一部のサイトはCSP等の制約で `javascript_tool` が機能しない（undefinedや空が返る）。
その場合は Accessibility Tree (AT) 経由で取得する:

```
1. navigate で対象URLを開く
2. find で取得したい要素のキーワードを検索 → ref_id を取得
   （テーブルID、セクション名、見出しテキストなど）
3. read_page ref_id を指定（depth=2, max_chars=70000）
4. 出力を {識別子}.txt に保存
```

**`find` のキーワード候補例:**
- テーブルのid属性値（例: "race_results", "price_table"）
- セクションの見出しテキスト
- ページ固有のクラス名・要素名

**サイズ超過の対処:**
- `read_page` が50000字を超える場合 → `max_chars=70000` で指定
- それでも溢れる場合 → JSON overflowファイルを `json.load` して `type=='text'` 要素を抽出
- ページ全体のATが返ってきた場合 → `find` からやり直して要素のref_idを正確に指定

### どちらか判断がつかない場合

まず `javascript_tool` を試す。undefinedや空が返ったら `find` + `read_page` に切り替える。

---

## 1件1ファイル方式（並行取得の基本）

大量のページを取得する場合は、共有ファイルへの同時書き込みを避けるため
必ず「1件 = 1ファイル」で保存する。

```
data/
  raw/
    {id_001}.txt   ← 個別取得ファイル（並行書き込みOK）
    {id_002}.txt
    ...
  parsed/
    {id_001}.json  ← パース済み（後で統合）
    {id_002}.json
all_data.json      ← 全件統合（全取得完了後に生成）
```

**並行エージェントのルール:**
- 1エージェントに割り当てるのは最大5〜10件
- 全エージェント完了後に統合処理を実行
- パース失敗の検知: 全レコードが空またはデフォルト値の場合は元ファイルを確認

---

## データパースの自動判定

Webから取得したテキストのフォーマットは3パターンある。
`scripts/auto_parser.py` が自動判定してパースする。

### パターン1: Accessibility Tree (AT) 形式
```
link "2024-03-15" [ref_123] href="..."
generic "データ値A"
generic "データ値B"
link "関連リンク" [ref_124] href="..."
```
判定条件: `link "` または `generic "` を含む

### パターン2: プレーンテキスト形式
```
2024-03-15
データ値A
データ値B
関連情報
```
判定条件: 識別子（日付など）が単独行で存在

### パターン3: CSV形式
```
2024-03-15,値A,値B,値C,値D,値E
2024-03-16,値A,値B,値C,値D,値E
```
判定条件: 識別子を含む行にカンマが5個以上

---

## 差分キャッシュ（前回データの再利用）

定期実行タスクでは、前回取得したデータを再利用することで取得量を大幅に削減できる。

**適用判断:**
- データの鮮度要件を確認（例: 3日以内なら再利用可）
- 前回キャッシュから同じIDのレコードを抽出して再利用
- 更新が確実なものだけ再取得（例: 当日出走した競走馬は再取得）

**実装パターン:**
```python
import json, os

def load_cache(cache_path):
    if not os.path.exists(cache_path):
        return {}
    with open(cache_path) as f:
        cache = json.load(f)
    return {item['id']: item for item in cache.get('items', [])}

def needs_refresh(cached_item, max_age_days=3):
    from datetime import datetime, timezone
    if not cached_item.get('cached_at'):
        return True
    cached_at = datetime.fromisoformat(cached_item['cached_at'])
    age = (datetime.now(timezone.utc) - cached_at).days
    return age > max_age_days
```

---

## スクリーニング（取得コストの削減）

詳細データの取得は1件あたりコストが高い（ページ遷移・パース処理）。
一覧データから取得不要なものを事前に除外することで全体の工数を削減できる。

**典型的なスクリーニング基準:**
- スコア・指標が明らかに範囲外（EV計算不能、条件未満など）
- ステータスが無効（取消・除外・非公開など）
- 前回キャッシュが新鮮（再取得不要）

スクリーニング後の取得件数を事前に見積もり、多い場合は並行エージェントを使う。

---

## Pythonスクリプトの配置規則

```
scripts/
  auto_parser.py      ← フォーマット自動判定パーサー（このスキルにバンドル済み）
  analyze.py          ← 分析・スコアリング（案件ごとにカスタマイズ）
  generate_report.py  ← HTMLレポート生成（案件ごとにカスタマイズ）
```

スクリプトのパスは `SKILL_DIR/scripts/` を使う:
```bash
SKILL_DIR="[このSKILL.mdがあるディレクトリ]"
python3 $SKILL_DIR/scripts/analyze.py input.json
python3 $SKILL_DIR/scripts/generate_report.py results.json --output report.html
```

---

## HTMLレポートの標準構成

案件ごとに `generate_report.py` をカスタマイズするが、以下の構成を標準とする:

```html
<!-- 標準レポート構成 -->
<header>タイトル・日付・サマリー数値</header>
<section class="highlights">注目データ上位N件（スコア付き）</section>
<section class="table">全データテーブル（ソート・フィルタ可）</section>
<section class="notes">注記・除外データ・データ品質</section>
```

**スタイル指針:**
- ダークテーマ推奨（長時間閲覧に向く）
- テーブルは横スクロール対応
- スコア・指標は視覚的バー or バッジで表示

最終成果物は必ずHTMLファイルを `outputs/` に保存して `computer://` リンクで共有する。

---

## 定期タスクへの組み込み

このパイプラインをスケジュールタスクとして自動化する場合の標準フロー:

```
朝のキャッシュタスク（軽量）:
  - 一覧ページから当日対象を取得
  - スクリーニングで対象を絞り込み
  - 差分キャッシュと照合して新規分だけ詳細取得
  - {日付}_cache.json に保存

日中の分析タスク:
  - キャッシュを読み込んでスクリプト実行
  - レポート生成

夜の突合タスク（結果確認がある案件）:
  - 結果データを取得して予測と照合
  - 精度指標を蓄積（ログに追記）
```

---

## 案件カスタマイズのチェックリスト

新しい案件でこのスキルをベースにする場合に確認すること:

- [ ] 対象サイトで `javascript_tool` が動くか確認
- [ ] 一覧ページから個別ページへのIDの抽出方法を確認
- [ ] スクリーニング基準を定義（何を除外するか）
- [ ] パースしたいフィールドを列挙
- [ ] キャッシュの鮮度要件を決める（何日まで再利用可か）
- [ ] 分析スコアの定義（何を「良い」とするか）
- [ ] レポートに表示する項目を決める

---

## 運用ルール

- 実データに基づくこと。推測・記憶での回答禁止。
- 取得データはすべてファイルに保存してからコンテキストに読み込む（コンテキスト汚染防止）。
- 大量取得（50件以上）は並行エージェントを使う（1エージェント最大10件）。
- 最終成果物は必ずHTMLレポートを生成してユーザーに提示すること。
- **作業後は必ず課題・改善点をユーザーに報告する。スキルの更新はユーザーの判断で行う。**

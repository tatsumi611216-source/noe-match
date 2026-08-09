# 部品: html-report（HTMLレポート標準構成）

- カテゴリ: output ／ 由来: web-data-pipeline ／ 使用実績: web-data-pipeline, keiba-yoso, gsc-report

## 何をする部品か

データ分析系ツールの最終成果物であるHTMLレポートの標準構成。
案件ごとに generate_report.py をカスタマイズするが骨格は共通。

## 組み込みブロック

```markdown
### HTMLレポートの標準構成

<header>タイトル・日付・サマリー数値</header>
<section class="highlights">注目データ上位N件（スコア付き）</section>
<section class="table">全データテーブル（ソート・フィルタ可）</section>
<section class="notes">注記・除外データ・データ品質</section>

**スタイル指針：**
- ダークテーマ推奨（長時間閲覧に向く）
- テーブルは横スクロール対応
- スコア・指標は視覚的バー or バッジで表示

最終成果物は必ずHTMLファイルを outputs/ に保存してユーザーに提示する。
```

## カスタマイズポイント

- highlights の「上位N件」の選定基準＝案件のスコア定義そのもの。先に決める
- notes 節には screening での除外件数・パース失敗件数を必ず載せる（信頼性の担保）
- 雛形コードは `~/.claude/skills/web-data-pipeline/references/customization_guide.md` を参照

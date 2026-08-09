# 部品カタログ

既存ツールを分解して抽出した再利用部品の全一覧。
新ツール製造時は、まずこのカタログから部品を選ぶこと。

## 既存ツールの分解結果

### noe-brain（ビジネス仮説設計）を分解すると

| 抽出部品 | 部品ID |
|---|---|
| モード自動判定（STARTUP/SMALL BIZ） | input/mode-detection |
| 文脈引き出し質問＋品質スコア4軸 | input/context-intake |
| 収益化可能性3軸チェック＋分岐テーブル | quality/branch-table |
| 抽象表現禁止ルール | quality/concreteness-rules |
| ストレステスト（3カテゴリ×失敗理由×回避行動） | process/stress-test |
| 72時間アクション設計（誰に・何を・どうやって・いつまでに） | process/action-design |
| NOE RELAY連携（起動コマンド生成・合流命令） | integration/skill-handoff |
| 最終サマリー表 | output/summary-table |
| メタ進化フッター | output/meta-evolution |
| ハルシネーション抑制（推定前提の明示） | safety/hallucination-guard |

### noe-relay（多エージェント討論）を分解すると

| 抽出部品 | 部品ID |
|---|---|
| 自動キャスティング＋8ターン討論＋審判介入 | process/debate-engine |
| 抽象論禁止・固有名詞/数値強制 | quality/concreteness-rules |
| WebSearch裏取り＋数字補正表 | quality/fact-check |
| 信頼度スコアA〜E＋改善ロードマップ | quality/confidence-score |
| メタサマリー（確定事実・アクションリスト） | output/summary-table |

### keiba-yoso（競馬予想）を分解すると

| 抽出部品 | 部品ID |
|---|---|
| ブラウザ取得ルール（javascript_tool vs find+read_page） | data/web-scraping |
| 1件1ファイル＋並行取得 | data/file-per-item |
| 差分キャッシュ | data/diff-cache |
| スコアリング（EV計算） | ※案件固有ロジック（部品化対象外、構造は quality/branch-table を参照） |
| HTMLレポート生成 | output/html-report |
| Notionログ | integration/notion-task |
| 結果突合・振り返り | integration/scheduled-task（夜の突合タスク） |

### web-data-pipeline（汎用パイプライン）を分解すると

| 抽出部品 | 部品ID |
|---|---|
| ブラウザ取得ルール | data/web-scraping |
| 1件1ファイル＋並行取得 | data/file-per-item |
| フォーマット自動判定パース | data/auto-parse |
| 差分キャッシュ | data/diff-cache |
| スクリーニング | data/screening |
| HTMLレポート標準構成 | output/html-report |
| 定期タスク組み込み（朝/日中/夜の3分割） | integration/scheduled-task |

### secretary（個人秘書）を分解すると

| 抽出部品 | 部品ID |
|---|---|
| キーワードトリガー処理（「宿題:」） | input/mode-detection |
| Notion登録・更新 | integration/notion-task |
| Gmail/Calendar操作パターン | integration/scheduled-task（参照） |
| 秘書口調・報告フォーマット | output/secretary-tone |
| 不可逆操作の確認ルール | safety/irreversible-confirm |

---

## 部品一覧（カテゴリ別）

### input（入力系）

| 部品ID | 機能 | 由来 | 使用実績 |
|---|---|---|---|
| input/context-intake | ユーザーから質の高い文脈を引き出す質問テンプレ＋品質スコア | noe-brain | noe-brain |
| input/mode-detection | 入力内容からモード・トリガーを自動判定して分岐 | noe-brain, secretary | noe-brain, secretary |
| input/spec-drilldown | ヒアリング後に案件専用の追加質問を生成して要件確定 | ツール発注フロー | noe-tool-lab |

### quality（品質系）

| 部品ID | 機能 | 由来 | 使用実績 |
|---|---|---|---|
| quality/concreteness-rules | 抽象論禁止・固有名詞/数値の強制 | noe-brain, noe-relay | noe-brain, noe-relay |
| quality/fact-check | WebSearchで数字を裏取りして補正表を作る | noe-relay | noe-relay |
| quality/confidence-score | 出力の信頼度をA〜Eで自己採点＋改善ロードマップ | noe-relay | noe-relay, noe-brain |
| quality/branch-table | スコア・チェック結果による処理分岐テーブル | noe-brain | noe-brain |
| quality/feasibility-check | 着手前の実現可否判定（◎○△＋代替案） | ツール発注フォーム | noe-tool-lab |

### process（処理系）

| 部品ID | 機能 | 由来 | 使用実績 |
|---|---|---|---|
| process/debate-engine | キャスティング→ターン制討論→審判介入の討論エンジン | noe-relay | noe-relay |
| process/stress-test | カテゴリ別に失敗理由と回避行動を強制生成 | noe-brain | noe-brain |
| process/action-design | 「誰に・何を・どうやって・いつまでに」形式の即実行アクション | noe-brain | noe-brain, noe-relay |
| process/gap-scoring | 期待値と実績の差分で改善・投資の優先度を機械的に決める | gsc-report, keiba-yoso | gsc-report |

### data（データ系）

| 部品ID | 機能 | 由来 | 使用実績 |
|---|---|---|---|
| data/web-scraping | ブラウザツールの使い分け（javascript_tool / find+read_page） | web-data-pipeline | web-data-pipeline, keiba-yoso |
| data/file-per-item | 1件1ファイル保存＋並行エージェント取得 | web-data-pipeline | web-data-pipeline, keiba-yoso |
| data/auto-parse | 取得テキストのフォーマット自動判定パース | web-data-pipeline | web-data-pipeline, keiba-yoso |
| data/diff-cache | 差分キャッシュで再取得を削減 | web-data-pipeline | web-data-pipeline, keiba-yoso |
| data/screening | 詳細取得前のスクリーニングでコスト削減 | web-data-pipeline | web-data-pipeline, keiba-yoso |

### output（出力系）

| 部品ID | 機能 | 由来 | 使用実績 |
|---|---|---|---|
| output/summary-table | 全工程の結果を1画面のサマリー表に圧縮 | noe-brain, noe-relay | noe-brain, noe-relay |
| output/html-report | HTMLレポートの標準構成とスタイル指針 | web-data-pipeline | web-data-pipeline, keiba-yoso |
| output/secretary-tone | 秘書口調・先回り報告フォーマット | secretary | secretary |
| output/meta-evolution | 出力末尾に次回改良ポイントを自動出力 | noe-brain | noe-brain |
| output/proposal-doc | 製造前の提案書（出力サンプル・スコープ外・検収条件） | ツール発注フロー | noe-tool-lab |

### integration（連携系）

| 部品ID | 機能 | 由来 | 使用実績 |
|---|---|---|---|
| integration/notion-task | NotionのDBへタスク登録・ステータス更新 | secretary, keiba-yoso | secretary, keiba-yoso |
| integration/skill-handoff | 別スキルへの起動コマンド生成と結果合流 | noe-brain | noe-brain⇔noe-relay |
| integration/scheduled-task | 定期タスク化（朝キャッシュ/日中分析/夜突合の3分割） | web-data-pipeline | web-data-pipeline, keiba-yoso, morning |

### safety（安全系）

| 部品ID | 機能 | 由来 | 使用実績 |
|---|---|---|---|
| safety/irreversible-confirm | 不可逆操作の実行前確認ルール | secretary | secretary |
| safety/hallucination-guard | 推定と事実を区別して明示するルール | noe-brain | noe-brain |

---

## カタログの更新ルール

- 新部品を parts/ に追加したら、必ずこのカタログの該当カテゴリ表に1行追加する
- 既存スキルで重複実装を見つけたら「既存ツールの分解結果」に追記して部品に切り出す
- 使用実績列は、新ツールがその部品を採用するたびに更新する（利用頻度＝部品の価値）

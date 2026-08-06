# Noe ツールメイキング工場

「既存ツールを部品化 → 部品を組み合わせて新ツールを高速製造」するための工場。

## なぜ工場が必要か

既存5スキル（noe-brain / noe-relay / keiba-yoso / web-data-pipeline / secretary）を
分解した結果、**同じ機能が別々のスキルで重複製造されていた**：

| 重複していた機能 | 実装1 | 実装2 |
|---|---|---|
| 品質・信頼度スコアリング | noe-brain（文脈品質スコア） | noe-relay（信頼度A〜E） |
| 抽象論禁止・具体性強制 | noe-brain（禁止表現ルール） | noe-relay（審判介入ルール） |
| WebSearch裏取り | noe-relay（インターミッション） | noe-brain STEP5-R（間接参照） |
| ブラウザデータ取得ルール | web-data-pipeline | keiba-yoso（ほぼ同文を再掲） |
| Notion連携 | secretary（宿題登録） | keiba-yoso（notion_logger.py） |
| 定期タスク組み込み | web-data-pipeline | morning（Setup節） |
| サマリー表出力 | noe-brain STEP7 | noe-relay メタサマリー |

新ツールを作るたびにこれらをゼロから書き直すのは無駄。
今後は部品ライブラリから取り出して組み立てる。

## 工場の構成

```
tool-factory/
  README.md            ← このファイル（工場の概要）
  PARTS_CATALOG.md     ← 部品カタログ（全部品の一覧・既存ツールの分解結果）
  ASSEMBLY_GUIDE.md    ← 組み立てガイド（SKILL.mdテンプレ＋製造手順）
  parts/               ← 部品ライブラリ（コピペで使える組み込みブロック）
    input/             ← 入力系（文脈引き出し・モード判定）
    quality/           ← 品質系（スコアリング・裏取り・具体性強制）
    process/           ← 処理系（討論・ストレステスト・アクション設計）
    data/              ← データ系（Web取得・パース・キャッシュ）
    output/            ← 出力系（サマリー表・HTMLレポート・口調）
    integration/       ← 連携系（Notion・スキル間連携・定期タスク）
    safety/            ← 安全系（不可逆確認・ハルシネーション抑制）
  skills/
    noe-tool-factory/  ← 工場スキル本体（~/.claude/skills/ に配置して使う）
```

## 使い方

### 新ツールを作るとき

1. Claude に「〇〇するツールを作って」と依頼する（noe-tool-factory スキルが起動）
2. 工場スキルが PARTS_CATALOG.md を参照して必要な部品を選定
3. ASSEMBLY_GUIDE.md のテンプレに部品を組み込んで SKILL.md を生成
4. 足りない部品は新造し、**必ず parts/ とカタログに登録**（次回から再利用可能に）

### 工場スキルのインストール

```bash
cp -r tool-factory/skills/noe-tool-factory ~/.claude/skills/
```

## 工場の運用ルール（重要）

1. **部品ファースト**：新ツールに書くロジックは、まず「既存部品で賄えないか」をカタログで確認する
2. **新造したら登録**：新ツールのために新しい機能を書いたら、汎用化して parts/ に登録する
3. **重複を見つけたら統合**：既存スキル同士の重複を見つけたら、部品に切り出してカタログに記録する
4. **部品には由来を書く**：どのスキルから抽出したか・どのスキルで使用中かを部品ファイルに明記する

# 部品: auto-parse（フォーマット自動判定パース）

- カテゴリ: data ／ 由来: web-data-pipeline（scripts/auto_parser.py） ／ 使用実績: web-data-pipeline, keiba-yoso

## 何をする部品か

Web取得テキストの3パターン（Accessibility Tree形式／プレーンテキスト／CSV）を
自動判定してパースする。実装は `~/.claude/skills/web-data-pipeline/scripts/auto_parser.py` にバンドル済み。

## 組み込みブロック

```markdown
### データパース

取得テキストのフォーマットは3パターンあり、auto_parser.py が自動判定する：

- パターン1: Accessibility Tree形式（`link "` / `generic "` を含む）
- パターン2: プレーンテキスト形式（識別子が単独行）
- パターン3: CSV形式（識別子行にカンマ5個以上）

実行：
SKILL_DIR="[web-data-pipelineスキルのディレクトリ]"
python3 $SKILL_DIR/scripts/auto_parser.py data/raw/ --output data/parsed/
```

## カスタマイズポイント

- 案件固有のフィールド抽出は auto_parser.py をコピーして拡張する（本体は書き換えない）
- 新フォーマットに遭遇したら判定条件を1つ追加し、この部品ファイルにも追記する

# 部品: notion-task（Notion登録・更新）

- カテゴリ: integration ／ 由来: secretary（宿題DB）, keiba-yoso（notion_logger.py） ／ 使用実績: secretary

## 何をする部品か

NotionのDBへレコードを登録・更新する定型処理。タスク管理・実行ログの両方に使う。

## 組み込みブロック

```markdown
### Notion登録

1. メッセージ・処理結果から登録内容を抽出する
2. Notionの「[DB名]」DBに登録する
   - ツール: notion-create-pages
   - parent: {"type": "data_source_id", "data_source_id": "[DBのdata_source_id]"}
   - properties:
     {
       "[タイトル列名]": "（抽出した内容）",
       "ステータス": "[初期値]",
       "カテゴリ": "（内容から判断: [カテゴリ候補を列挙]）",
       "メモ": "（登録元・補足）"
     }
3. 登録完了を報告する
4. 複数件が一度に来た場合はまとめて一括登録する

### ステータス更新

notion-update-page でステータスを「[完了値]」に更新する。

### 一覧確認

notion-query-database-view または notion-fetch で [DBのURL] を参照する。
```

## カスタマイズポイント

- data_source_id と列名はDBごとに異なる。ツール製造時に実物のDBを確認して埋める
- 実績DB（既知のID）：
  - Cowork宿題DB: data_source_id `aec293fc-0d53-49c0-a87b-093ac36e81b2` ／ URL `https://www.notion.so/9082bd552e06431aa901b501d31d7d3e` ／ 列: タスク名・ステータス・カテゴリ・メモ
- カテゴリ判定ルールは必ず候補を列挙して書く（自由記述にすると表記ゆれが蓄積する）

# ツール発注フォーム — 質問セット

フォームに答えるだけで新ツールを発注できる仕組み。運用は2ルート：

- **ルートA：Webフォーム**（`order-form.html`）— 回答に連動して部品が自動選定され、
  発注書テキストが自動生成される。コピーしてClaudeに貼るだけ
- **ルートB：Google Form** — 下の質問セットをそのままGoogle Formに転記して使う。
  回答（日本語のまま）をClaudeに貼れば、noe-tool-factory が部品にマッピングする

どちらも「①部品に名前がある ②機能が明示されている ③キャンバスでカテゴライズされている」
というカタログの構造があるから成立する。フォームは工場の**受付窓口**にあたる。

---

## Google Form 転記用 質問セット

タイトル：**Noe ツール発注フォーム**
説明：質問に答えるだけで、Claudeのツール工場に新ツールを発注できます。回答をコピーしてClaudeに貼ってください。

### Q1. ツール名（仮でOK）〔記述式・任意〕

### Q2. 一言定義〔記述式・必須〕
「誰が・何に困っていて・何を出すツール？」を1〜2行で。
例：中古物件を探す自分が、割安か判断できずに困っている。候補物件をスコア付きレポートで出すツール。

### Q3. 入力の受け取り方〔チェックボックス〕
- 話しかけたら内容で自動判定してほしい
- 最初に質問で詳しい文脈を引き出してほしい

### Q4. 外部データ〔チェックボックス〕
- Webサイトからデータを集める
- 同じデータを定期的に取り直す
- 外部データは使わない

### Q5. 中核の処理〔チェックボックス〕
- 出した案の弱点・失敗理由も出してほしい
- 賛成・反対を討論させて検証してほしい
- 結論を「すぐやる行動」に落としてほしい
- 独自の計算・スコアリングがある（内容はQ9に記入）

### Q6. 品質の担保〔チェックボックス〕
- 数字はWeb検索で裏取りしてほしい
- 結論の信頼度を採点してほしい
- 抽象論禁止。固有名詞と数値で語らせたい
- 途中に合否ゲートを置いて足切りしたい

### Q7. 出力の形〔チェックボックス〕
- 1画面のサマリー表
- HTMLレポート
- 秘書口調の短い報告
- 毎回「次回の改良ポイント」も出してほしい

### Q8. 連携・安全〔チェックボックス〕
- 結果をNotionに登録・記録したい
- 毎日・毎週など定期実行したい
- 条件次第で別ツールに引き継ぎたい
- 送信・削除など取り返しのつかない操作がある
- 推定と事実をはっきり分けてほしい（推奨）

### Q9. 補足〔記述式・任意〕
独自ロジックの内容・参考にしたい既存ツール・こだわり等

---

## 回答→部品マッピング表（工場スキルが参照する）

| フォームの回答 | 割り当て部品 | ブロック |
|---|---|---|
| 話しかけたら自動判定 | input/mode-detection | ① INPUT |
| 質問で文脈を引き出す | input/context-intake | ① INPUT |
| Webからデータを集める | data/web-scraping + file-per-item + auto-parse + screening | ④ DATA |
| 定期的に取り直す | data/diff-cache | ④ DATA |
| 弱点・失敗理由も出す | process/stress-test | ③ PROCESS |
| 討論で検証 | process/debate-engine | ③ PROCESS |
| すぐやる行動に落とす | process/action-design | ③ PROCESS |
| 独自の計算・スコアリング | 新造（固有ロジック） | ③ PROCESS |
| 数字の裏取り | quality/fact-check | ② QUALITY |
| 信頼度を採点 | quality/confidence-score | ② QUALITY |
| 抽象論禁止 | quality/concreteness-rules | ② QUALITY |
| 合否ゲート | quality/branch-table | ② QUALITY |
| 1画面サマリー表 | output/summary-table | ⑤ OUTPUT |
| HTMLレポート | output/html-report | ⑤ OUTPUT |
| 秘書口調 | output/secretary-tone | ⑤ OUTPUT |
| 次回の改良ポイント | output/meta-evolution | ⑤ OUTPUT |
| Notionに登録 | integration/notion-task | ⑥ INTEGRATION |
| 定期実行 | integration/scheduled-task | ⑥ INTEGRATION |
| 別ツールに引き継ぎ | integration/skill-handoff | ⑥ INTEGRATION |
| 不可逆操作あり | safety/irreversible-confirm | ⑦ SAFETY |
| 推定と事実を分ける | safety/hallucination-guard | ⑦ SAFETY |

**マッピングのルール：**
- 表にない自由記述の要望は、まずカタログ全体から近い部品を探す。なければ新造候補とする
- Q2（一言定義）が空欄・曖昧な場合のみ、製造前に1問だけ確認する
- フォーム経由の発注は、キャンバス確認（工場スキルSTEP 3）を省略してよい。
  ただし回答間に矛盾（例：データなし＋HTMLレポート希望で対象データ不明）がある場合のみ質問する

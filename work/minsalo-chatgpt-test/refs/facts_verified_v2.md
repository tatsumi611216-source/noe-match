# ファクトチェック結果表（script.md）

- 対象：`script.md` に付けていた【要確認】タグ **全4件**
- 確認日時：**2026-08-22 14:15〜14:20（JST）**
- 使用した一次ソース：OpenAI公式のみ（help.openai.com / chatgpt.com の料金ページ）
- まとめサイト・ブログは1件も開いていない
- 補足：WebFetchは openai.com / help.openai.com とも **HTTP 403** で全滅したため、
  Chrome（Claude in Chrome）で同じ一次ソースを開いて照合した。照合作業は画面録画に含まれる。

## 判定サマリ

| 判定 | 件数 |
|---|---|
| ✅ 一次ソースで確認できた | **4件** |
| ❌ 誤りだったので本文を修正 | **0件** |
| ⚠️ 確認できず【削除候補】を付けて残した | **0件** |

---

## 照合表

| # | 台本に書く内容 | 判定 | 根拠URL | ページからの原文引用 | 確認日時 |
|---|---|---|---|---|---|
| 1 | カスタム指示の文字数上限は有料プランで5,000字。2026年7月15日に1,500字から拡大 | ✅ | https://help.openai.com/en/articles/6825453-chatgpt-release-notes | July 15, 2026 / Increased custom instructions limit —「We're increasing the character limit for custom instructions in ChatGPT. Plus, Pro, Enterprise, Business, and Education users can now save up to 5,000 characters, up from 1,500, giving them more room to customize ChatGPT's response style and behavior.」 | 2026-08-22 14:17 |
| 2 | クラウド上のファイルを直接読ませる機能はGoogleドライブ。ウェブ版のPlus以上に配信中。マイドライブと自分あて共有ファイルが対象で、共有ドライブは未対応 | ✅ | https://help.openai.com/en/articles/6825453-chatgpt-release-notes | August 13, 2026 / Google Drive is now in Library —「You can also quickly pull up a Drive file from the composer or with @mentions and add it to any chat—without uploading it again.」／「The initial experience includes My Drive and files and folders shared directly with you; Shared Drives aren't included yet.」／「Rolling out to Plus, Pro, Enterprise, Edu, Healthcare and Business users on the web in both the Chat and Work toggles. Mobile support will follow.」 | 2026-08-22 14:18 |
| 3 | クイズ機能は2026年8月14日に追加。個人向け全プランと教育向けプランで、ウェブとスマホから使える | ✅ | https://help.openai.com/en/articles/6825453-chatgpt-release-notes | August 14, 2026 / ChatGPT app experience updates —「Practice with interactive quizzes. Ask ChatGPT to quiz you on a topic and answer questions directly in your conversation. Available to all consumer ChatGPT plans and Edu plans on web and mobile.」 | 2026-08-22 14:18 |
| 4 | 無料プランと有料プランでモデルの選べる範囲が違う（無料は速い役が無制限／有料は推論モデルとその上位が使える） | ✅ | https://chatgpt.com/ja-JP/pricing/ | 無料版：「GPT-5.6 Luna でのテキストチャットは無制限」／Plus：「GPT-5.6 による高度なリーズニングモデル」／Pro：「GPT-5.6 Sol Pro による Pro 推論」／比較表に「モデル」行として GPT-5.6 Sol / Sol Pro / Terra / Luna / GPT-5 Thinking Mini / レガシーモデル が並ぶ | 2026-08-22 14:20 |

---

## 本文の修正記録（タグ外し）

| # | 修正前（【要確認】タグ付き） | 修正後（本文） |
|---|---|---|
| 1 | 「ここは【要確認：カスタム指示に入力できる文字数の上限と、プランごとの差】。上限の数字は伸びたり縮んだりするので、私の口からは言わないでおきます。」 | 「有料プランだと5,000字まで書けて、これは2026年7月15日に1,500字から広がったものですね。ただ上限の数字はまた動くので、実際に打つときは画面の残り文字数を見てください。」 |
| 2 | 「連携できるサービスと、使えるプランは【要確認：外部ストレージ連携の対象サービスとプラン条件】。」 | 「いま使えるのはGoogleドライブで、ウェブ版のPlus以上のプランから順に配られています。私のドライブと、自分あてに共有されたファイルまでが対象で、共有ドライブはまだ入ってません。」 |
| 3 | 「対象プランは【要確認：学習向けクイズ機能の名称と、利用できるプランの範囲】。」 | 「これは2026年8月14日に入った機能で、個人向けの全プランと教育向けプランで、ウェブとスマホから使えます。」 |
| 4 | 「このへんは【要確認：2026年8月時点の各プランで選択できるモデルの範囲】。金額も動きやすいので、数字は収録前に公式の料金ページで見てください。」 | 「無料だと、いちばん速い役のモデルは無制限で使えますけど、じっくり考える役は上限つきなんですよ。有料にすると、じっくり考える役と、そのさらに上の役が使えるようになります。ここも金額と名前は動くので、収録前に公式の料金ページで見てください。」 |

※ ❌（誤りだったもの）は0件のため、修正前後の記録はタグ外しのみ。

---

## 台本に書かなかったこと（意図的に落とした）

| 内容 | 理由 |
|---|---|
| 各プランの具体的な月額（Free / Go / Plus / Pro の金額） | 公式料金ページ上で金額が「/ 月」と表示され、**数値が取得できなかった**。二次情報では16,800円と30,000円が割れていたため、金額そのものを台本に書かない判断（章2は役割で覚えさせる構成に変更済み） |
| モデルの正式名称（GPT-5.6 Sol / Terra / Luna 等） | 公式ページで実在は確認できたが、**変わりやすい固有名詞は役割（早い・じっくり・コード用）に置き換える**方針のため本文には出さない |
| o3の提供終了日、DALL·E GPTの廃止日 | 今回の台本の構成に含めなかったため、確認対象外 |

## 残っている収録前タスク

- 【収録時実測】12箇所（凡例1件を除く）：画面に出た実際の値へ差し替え
- 【体験談差し替え】2箇所（凡例1件を除く）：トオルさん本人の実話へ差し替え
- 料金ページはモデル名・価格とも変動が速いため、**収録直前にもう一度開く**

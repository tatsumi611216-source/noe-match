# 台本 script_本番.md ／【要確認】タグ 裏取り結果

- 確認日時：2026-08-22（JST）
- 対象：`work/minsalo-chatgpt-test/draft/script_本番.md` の【要確認】タグ 全15件
- 一次ソース：OpenAI公式（help.openai.com / openai.com）、インボイス1件のみ国税庁（nta.go.jp）
- **確認方法についての注記**：WebFetch は openai.com / help.openai.com のすべてに対して
  HTTP 403 を返したため、同一URLを**ブラウザ（Claude in Chrome）で実際に開いて**
  ページ本文を読み、そこに書いてある記述とだけ突き合わせた。引用はすべてページ原文のまま。
  まとめサイト・ブログ・ニュース記事は一切使用していない。

判定：✅一致 9件／❌不一致 4件／⚠️確認不能 2件

---

## 判定表

| # | 行 | タグ内容 | 判定 | 根拠URL | 根拠となるページ内の記述（原文のまま） |
|---|---|---|---|---|---|
| 1 | 69 | 更新の頻度（モデル名が数ヶ月に1回入れ替わる） | ✅一致 | https://help.openai.com/en/articles/9624314-model-release-notes | 「GPT-5.4 Thinking in ChatGPT (March 5, 2026)」／「GPT-5.5 Instant Update (May 28, 2026)」／「Introducing GPT-5.6 Sol in ChatGPT (July 9, 2026)」／「Retiring GPT-5.1 models (March 11, 2026) As of March 11, 2026, GPT-5.1 models are no longer available in ChatGPT.」<br>→ 直近1年で 5.1→5.2→5.3→5.4→5.5→5.6 と推移。約2ヶ月に1回のペースで、台本の「数ヶ月に1回」は範囲内。 |
| 2 | 88 | 終了日と対象のモデル名（思考型モデルが1つ引退） | ❌不一致 | https://help.openai.com/en/articles/9624314-model-release-notes | 「Retiring OpenAI o3 and GPT-4.5 (May 28, 2026)　Today, we're continuing to retire older models with limited usage in ChatGPT so we can better serve our newer, most capable models. OpenAI o3 will be retired from ChatGPT on August 26, 2026 following a 90-day sunset period」<br>→ o3 は **2026年8月26日に引退予定**であり、収録日（8/22）時点ではまだ「引退しました」（過去形）ではない。 |
| 3 | 106 | メモリ／カスタム指示／プロジェクトの正式な機能名 | ✅一致 | https://help.openai.com/en/articles/8590148-memory-faq<br>https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions<br>https://help.openai.com/en/articles/10169521-projects-in-chatgpt | 「Memory controls are available in Settings > Personalization > Memory.」／「Custom instructions allow you to share anything you'd like ChatGPT to consider in its response.」／「Projects are smart workspaces that keep everything related to a long-running effort in one place.」<br>→ 3機能とも Memory / Custom Instructions / Projects として実在。 |
| 4 | 117 | メニューの名前と場所（右上のアイコン→設定） | ⚠️確認不能 | https://help.openai.com/en/articles/7730893-data-controls-faq | 「On Web (Signed-in):　Click your profile icon　Select Settings」<br>→ 「プロフィールアイコンを押す→Settings（設定）」までは一致。ただし**そのアイコンが「右上」にあるという記述は、OpenAIのどのヘルプ記事にも無い**（同じページで署名外の導線は「Click the ? icon in the bottom-right corner」と位置を明示しているのに、プロフィールアイコンについては位置を書いていない）。位置の断定が裏取りできないため⚠️。 |
| 5 | 128 | 項目の名前（パーソナライズ） | ✅一致 | https://help.openai.com/en/articles/8590148-memory-faq | 「Memory controls are available in Settings > Personalization > Memory.」<br>→ 設定内の項目名は Personalization（日本語UI：パーソナライズ）で一致。 |
| 6 | 170 | 設定内の項目名（カスタム指示を書く場所） | ✅一致 | https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions | 「Web & Desktop　In your Settings, select Personalization.　Please make sure that Enable customization is toggled ON.　Enter your instructions in the Custom Instructions field.」<br>→ メモリと同じ Settings > Personalization の中。「さっきと同じ設定の中」で一致。 |
| 7 | 172 | 上限の文字数とプランごとの差 | ✅一致 | https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions | 「Is there a character limit for custom instructions?　Free and Go users can save up to 1,500 characters in custom instructions. Plus, Pro, Enterprise, Business, and Education users can save up to 5,000 characters.」<br>→ 「有料のプランだと上限が広がる」で一致。**具体値は無料/Go＝1,500字、Plus/Pro/Enterprise/Business/Edu＝5,000字**（本文は数字を出していないので、ルール通り本文は未変更。数字を入れたい場合はここを使ってください）。 |
| 8 | 176 | 既存チャットへの反映仕様 | ❌不一致 | https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions | 「Custom instructions allow you to share anything you'd like ChatGPT to consider in its response. **Your custom instructions are applied immediately to all chats.**」／「Enabling Custom Instructions　**Updates to custom instructions settings are applied immediately across all chats (including existing conversations).**」<br>→ 公式は「既存の会話も含め、即座に全チャットに反映される」と明記。台本の「前から開いてるチャットには反映されないことがある」は逆。<br>※同記事のFAQには「updates to your instructions are reflected only in future conversations」という一文もあるが、これは「過去の会話ログに残った旧バージョンの指示文の表示」についての設問への回答であり、反映仕様の見出し記述と矛盾する。見出し・概要側の明示的な記述を採用した。 |
| 9 | 184 | インボイスの判断条件の説明として正確か | ❌不一致 | https://www.nta.go.jp/taxes/shiraberu/taxanswer/shohi/6501.htm<br>https://www.nta.go.jp/taxes/shiraberu/zeimokubetsu/shohi/keigenzeiritsu/invoice_about.htm | 「その課税期間の基準期間…における課税売上高が1,000万円以下である場合には、原則として、納税義務が免除されます。」／「**課税期間の基準期間における課税売上高が1,000万円以下であっても、適格請求書発行事業者の登録を受けている場合には、納税義務は免除されません。**」／「買手側が仕入税額控除の適用を受けるためには、原則として、売手（取引相手）であるインボイス発行事業者からインボイスを交付してもらい、そのインボイスを保存しておく必要があります。」<br>→ **1,000万円は「消費税の納税義務が免除されるかどうか」の基準であって、インボイス登録するかしないかの境目ではない**。売上1,000万円以下でも登録は可能（登録すれば課税事業者になる）。登録の判断軸は取引先の仕入税額控除。 |
| 10 | 197 | 機能名と使えるプラン（プロジェクト） | ✅一致 | https://help.openai.com/en/articles/10169521-projects-in-chatgpt | 「Projects are smart workspaces that keep everything related to a long-running effort in one place. Group together chats, upload reference files, and add custom instructions so ChatGPT remembers what matters and stays on-topic.」／「**Projects are available to all free and paid subscription types globally.**」／「Click New project in the sidebar.」<br>→ 「案件ごとにチャットをまとめておける箱」で一致。無料含む全プランで利用可。左サイドバーの「新しいプロジェクト」も一致。 |
| 11 | 353 | 以下3つすべて、対象プランと提供状況 | ✅一致 | https://help.openai.com/en/articles/6825453-chatgpt-release-notes | ①「Rolling out to Plus, Pro, Enterprise, Edu, Healthcare and Business users on the web in both the Chat and Work toggles. Mobile support will follow.」（August 13, 2026）<br>②「This update is available on all ChatGPT plans.」（プロジェクトのメモリ設定変更）<br>③「Practice with interactive quizzes. … **Available to all consumer ChatGPT plans and Edu plans on web and mobile.**」（August 14, 2026）<br>→ 3つとも提供状況・プランが異なり、①は有料・Webのみ。台本の「収録した時点の話として聞いてください」という但し書きは適切で、修正不要。 |
| 12 | 360 | 連携できるサービス名 | ⚠️確認不能 | https://help.openai.com/en/articles/6825453-chatgpt-release-notes<br>https://help.openai.com/en/articles/11487775-apps-in-chatgpt | 「If you have the Google Drive plugin connected, you can now see and browse your Google Drive files and folders directly from Library… You can also quickly pull up a Drive file from the composer or with @mentions and add it to any chat—without uploading it again.」（August 13, 2026）<br>「**For the current list of available workflows, open the Plugins Directory.**」／「What other apps will be available in the future?　Open the Plugins Directory for the current set of available workflows and included apps.」<br>→ **アットマークでファイルを呼ぶ動作が公式に確認できるのは Google ドライブ1件のみ**。それ以外に何が繋げられるかは、OpenAIが固定リストを公開しておらず「Plugins Directoryを見てくれ」としか書いていないため、サービス名を列挙する形での裏取りは不能。 |
| 13 | 380 | 変更できる項目と条件（プロジェクトの後から変更） | ❌不一致 | https://help.openai.com/en/articles/6825453-chatgpt-release-notes<br>https://help.openai.com/en/articles/10169521-projects-in-chatgpt | 「**Edit memory settings for existing projects**　You can now change a project's **memory setting** after you create it. Open the project, select the three-dot menu, choose Project settings, and select Default memory or Project-only memory under Memory.」／「This update is available on all ChatGPT plans.」<br>「Click on the three dots on the upper right hand corner of your project and select Project settings to **add project instructions**.」<br>→ 「後から変えられるようになった」新機能は**メモリ設定**であって、指示文ではない。**指示文（プロジェクト指示）はもともと三点メニュー→プロジェクト設定から編集でき、作り直す必要は無かった**。台本は新機能を指示文の編集だと説明しており不一致。 |
| 14 | 395 | 専用の機能名があるか（クイズ形式） | ✅一致 | https://help.openai.com/en/articles/6825453-chatgpt-release-notes | 「**Practice with interactive quizzes. Ask ChatGPT to quiz you on a topic and answer questions directly in your conversation.** Available to all consumer ChatGPT plans and Edu plans on web and mobile.」（August 14, 2026）<br>→ トグルやメニューではなく「チャットで頼む」形。台本が「使い方」として紹介しているのは公式の説明と一致。 |
| 15 | 436 | 規定は会社ごとに違うので断定しない | ✅一致 | （検証対象＝断定していないかの自己チェック。OpenAI側の事実主張なし） | 該当文：「会社によっては、仕事で使うこと自体にルールがあるので、まず社内の規定を1回だけ読んでください。」<br>→ 「会社によっては」と条件付きで述べており、社内規定の内容を断定していない。修正不要。 |

---

## ❌不一致の修正記録（修正前 → 修正後）

### #2（88行目）思考型モデルの引退

- 修正前：
  > 実際、少し前まで使えていた思考型のモデルが、1つ引退しました。【要確認：終了日と対象のモデル名】
- 修正後：
  > 実際、o3という思考型のモデルが、この8月26日で引退します。予告が出たのが5月28日なので、ちょうど3ヶ月前ですね。
- 根拠：「Retiring OpenAI o3 and GPT-4.5 (May 28, 2026) … OpenAI o3 will be retired from ChatGPT on August 26, 2026 following a 90-day sunset period」
  （https://help.openai.com/en/articles/9624314-model-release-notes ）
- 補足：直前の文「古いモデルは、予告は出るんですけど、期限が来るとそのまま使えなくなるんです」の実例として、
  予告日と終了日の両方が一次ソースで取れるこの1件に差し替えた。

### #8（176行目）カスタム指示の既存チャットへの反映

- 修正前：
  > 貼ったら、必ず新しいチャットで試してください。
  > 前から開いてるチャットには反映されないことがあって、ここで「効いてない」と勘違いする方が多いんです。【要確認：既存チャットへの反映仕様】
- 修正後：
  > 貼ったら、そのまま試してください。
  > 公式には、更新した内容はその場で全部のチャットに反映されます。前から開いてるチャットも含めてです。
- 根拠：「Updates to custom instructions settings are applied immediately across all chats (including existing conversations).」
  （https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions ）

### #9（184行目）インボイスの判断条件

- 修正前：
  > 今度は1行目が「登録するかしないかを、売上1,000万円を境に判断します」でした。【要確認：インボイスの判断条件の説明として正確か】
- 修正後：
  > 今度は1行目が「取引先が仕入税額控除を使うかどうかで、登録するかを判断します」でした。
- 根拠：「課税期間の基準期間における課税売上高が1,000万円以下であっても、適格請求書発行事業者の登録を受けている場合には、納税義務は免除されません。」
  （https://www.nta.go.jp/taxes/shiraberu/taxanswer/shohi/6501.htm ）
  「買手側が仕入税額控除の適用を受けるためには、原則として、売手（取引相手）であるインボイス発行事業者からインボイスを交付してもらい、そのインボイスを保存しておく必要があります。」
  （https://www.nta.go.jp/taxes/shiraberu/zeimokubetsu/shohi/keigenzeiritsu/invoice_about.htm ）

### #13（380行目）プロジェクトの後から変更

- 修正前：
  > あれ、以前は中の設定を変えるのに、作り直すしかなかったんです。
  > それが後から変えられるようになりました。【要確認：変更できる項目と条件】
  > （中略）
  > 出てきたメニューから設定を選ぶと、中の指示を書き換える画面になります。
  > 「予算は年間240万円」の行を「120万円」に直して閉じるだけで、かかる時間は10秒くらいですね。
- 修正後：
  > あれ、箱ごとの記憶の設定は、作るときに決めたら、あとから変えられなかったんです。
  > それが後から変えられるようになりました。全プランで使えます。
  > （中略）
  > 出てきたメニューからプロジェクト設定を選ぶと、メモリという項目があります。
  > ここで、いつも通りの記憶にするか、この箱の中だけの記憶にするかを選んで、保存するだけですね。
- 根拠：「Edit memory settings for existing projects　You can now change a project's memory setting after you create it. Open the project, select the three-dot menu, choose Project settings, and select Default memory or Project-only memory under Memory.」／「This update is available on all ChatGPT plans.」
  （https://help.openai.com/en/articles/6825453-chatgpt-release-notes ）
- 補足：指示文（プロジェクト指示）はもともと編集可能だったため、「作り直すしかなかった」対象を
  メモリ設定に直した。周辺の「担当者が代わった／予算が半分になった」のくだりも、
  記憶の切り替えの話として通るように文をならしてある。

---

## ⚠️確認不能（【削除候補】マーカーを付けた箇所。削除・変更の判断はCEO）

### #4（117行目）

> 【削除候補】右上のアイコンを押して、設定を開きます。

- 確認できたこと：「プロフィールアイコンを押す → Settings（設定）を選ぶ」という導線は公式に存在する。
- 確認できなかったこと：そのアイコンが**「右上」にある**という記述。OpenAIのヘルプは位置を書いていない。
- 最小修正案（採用するかはCEO判断）：「プロフィールのアイコンを押して、設定を開きます。」に変えれば、
  一次ソースの原文（「Click your profile icon / Select Settings」）と完全に一致する。

### #12（360行目）

> 【削除候補】連携をつないでおくと、この手間がまるごと消えます。

- 確認できたこと：Googleドライブについては、アットマークでファイルを呼び出してチャットに追加できると公式に明記されている（2026年8月13日）。ただし対象は Plus / Pro / Enterprise / Edu / Healthcare / Business のWeb版で、無料プランは含まれない。
- 確認できなかったこと：Googleドライブ以外にどのサービスが繋げられるか。OpenAIは固定リストを公開しておらず「Plugins Directoryを開いて確認してほしい」としか書いていない。
- 最小修正案（採用するかはCEO判断）：サービス名をGoogleドライブ1つに限定し、
  「Googleドライブを繋いでおくと、この手間がまるごと消えます」とすれば裏が取れる。

---

## タグ外だが、収録前に一度見てほしい箇所（今回は本文を触っていません）

### 129〜133行目：メモリを1件ずつゴミ箱で消す手順

台本は「一覧が出たら、右側にゴミ箱のマークが並んでるはずです。いらない行のゴミ箱を押すだけで1件3秒で消える」
と説明しているが、これは**旧方式（legacy saved memories）**の画面。
現行のメモリは「メモリー概要（memory summary）」方式で、UIも消し方も違う。

- https://help.openai.com/en/articles/8590148-memory-faq
  - 「To make edits to the memory summary:　Type what you want changed into the text box at the bottom of the memory summary and it will update accordingly.　You can highlight any text in the memory summary to make a specific correction.」
  - 「You can delete the memories shown on your memory summary page and turn memory off by selecting **Delete and turn off memory** from the three-dot menu.」
  - 「If you prefer to revert to the legacy saved memories system, go to Settings > Memory and select the "saved memories" link below "Memory summary".」

→ 現行画面では「1件ずつゴミ箱で消す」ではなく、**下の入力欄に消したい内容を書く／該当箇所を選んで直す**が公式手順。
　1件ずつ削除できるのは旧方式に戻した場合。**タグが付いていない範囲なので今回は書き換えていない**が、
　画面を映す場面なので、収録前に実機を見て文を合わせることを勧めます。

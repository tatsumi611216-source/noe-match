# 領域5: Off-SERP/他プラットフォーム

- **調査日**: 2026-08-27
- **担当領域**: Off-SERP / Search Everywhere Optimization / 他プラットフォーム寄生
- **参照ソース数**: 約95URL（WebSearch 28回で収集。うち本文中に明示引用したもの 78件）
- **対象サイト**: noe-match.com「Noe結婚設計室」（婚活・結婚・新生活アフィリエイト、個人運営、2026年6月ドメイン開設）

---

## 調査条件の開示（重要・先に読むこと）

本調査は次の制約下で行われた。数値の信頼度判定に必要なので先に書く。

1. **WebFetch（直接読み込み）がネットワーク側で遮断された。** searchengineland.com / developers.google.com / sparktoro.com / otterly.ai / semrush.com / ahrefs.jp / growth-memo.com / ja.wikipedia.org / chiebukuro.yahoo.co.jp などへの直接アクセスがすべて egress proxy にブロックされた。よって**一次ソースのURLは特定できているが、本文を全文検証できていない**。本文中の数値は検索エンジンが返した要約スニペット経由である。
2. そのため各手法の出典に **[一次]**（Google公式/消費者庁/プラットフォーム公式/著名調査元）と **[二次]**（SEOメディア・要約記事）のタグを付けた。**[二次]のみで支えられている数字は、実装前に必ず原典で再検証すること。**
3. WebSearchの実行回数上限（200回/セッション）に到達したため、後半に予定していた日本語クエリ2本（「みん評 婚活 比較 掲載」「Ahrefs brand mentions AI Overview 相関」）が未実行。該当箇所は「日本語言及度：未検証」と明記した。
4. **実際に実行した日本語クエリは以下12本のみ**。これ以外の「日本での言及度」は、日本語SEO情報流通の一般傾向からの推定であり、その旨を各項目に明記した。
   - `Pinterest 日本 月間利用者数 2026 ユーザー数 公式`
   - `ステマ規制 景品表示法 アフィリエイト 事業者の表示 該当 2026 消費者庁`
   - `バーナクルSEO パラサイトSEO 日本語 解説`
   - `Yahoo!知恵袋 公式回答 企業 制度 参加`
   - `Pinterest SEO 日本語 やり方 集客 ブログ流入`
   - `Google Discover 日本語 最適化 流入 攻略`
   - `ポッドキャスト SEO 日本語 文字起こし 被リンク ゲスト出演`
   - `note.com SEO ドメインパワー 上位表示 パラサイト 規約 商用利用`
   - `Reddit 日本 ユーザー数 2026 日本語 subreddit 規模`
   - `LINE公式アカウント 友だち数 2026 統計 月間利用者 メルマガ 開封率 日本`
   - `Wikipedia 日本語版 特筆性 企業記事 利益相反 有償編集 方針`
   - `Pinterest ウェディング 結婚 日本 検索 トレンド 2026 花嫁`

---

## 前提1: 2026年の「Off-SERP」が意味を持つ理由（数値の土台）

この領域の全手法は、以下の構造変化を前提にしている。個別手法の前に共通の根拠として置く。

- **AI検索の引用元はUGC/コミュニティに偏っている。** コミュニティプラットフォームがAI引用全体の **48〜54%** を占めるという集計がある（[二次] https://www.farandwide.io/blog/reddit-quora-ai-citations ）。
- **Redditが単独最大の被引用ドメイン。** 生成AIエンジン横断の集計でRedditが約 **40%** の被引用頻度シェア（[二次] https://everything-pr.com/ai-platform-citation-source-index-2026 ）。Google AI Overviewsの引用の **21%**、Perplexityでは**引用の5件に1件**がRedditという報告（[二次] 同上／ https://searchengineland.com/ai-search-engines-cite-reddit-youtube-and-linkedin-most-study-473138 [一次寄り：Search Engine Landの調査報道]）。
- **この数値の裏にある調査は4系統。** Peec AIの3,000万ソース分析、Semrushの32.5万プロンプト分析、Profoundの6モデル・140万引用分析、SE Rankingの12.9万ドメイン分析（[二次] https://contently.com/2026/04/29/top-sources-llms-cite/ ）。**4系統とも独立に「Reddit/YouTube/Wikipedia/LinkedInが上位」を出している点が重要**で、単一調査の癖ではない。
- **自社サイト外が支配的。** Kevin Indig「ブランドメンションの85%は自社サイト外の要因で決まる」（[二次] https://previsible.io/seo-ai-news/ai-visibility-has-nothing-to-do-with-your-website/ ／原典 [一次] https://www.growth-memo.com/p/state-of-ai-search-optimization-2026 ）。
- **参照トラフィックの前提が崩れている。** 大手パブリッシャーの対Google自然流入は、2026年6月までの12か月で USA Today 約-50%、CNN 約-25%、Politico -23%、Business Insider -85%超（[二次] https://www.emarketer.com/content/reddit-reportedly-weighs-ending-google-content-licensing-deal-publisher-traffic-concerns-mount ）。**個人運営の新規ドメインが「自サイトの検索順位」だけに賭けるのが不合理**という結論はここから来る。

## 前提2: 日本のステマ規制（本レポートの全判定の基準線）

- 2023年10月1日施行の景品表示法告示「一般消費者が事業者の表示であることを判別することが困難である表示」（[一次] 消費者庁 https://www.caa.go.jp/policies/policy/representation/fair_labeling/assets/representation_cms216_200901_01.pdf ）。
- 運用基準上、**アフィリエイトは「事業者が第三者をして行わせる表示」に含まれる**（[二次] https://www.seedinc.jp/column/affiliate/stealth-marketing-regulations/ ）。
- **本レポートにおける判定ルール**:
  - noe-matchが**自分で書き、自分のアフィリエイトリンク/自サイト誘導を含む**投稿 → **「事業者の表示」に該当**。プラットフォーム上でも **PR表記が必要**。
  - noe-matchが**対価を払って第三者に書かせる**（レビュー依頼、口コミ投稿依頼、有償リスティクル掲載でPR表記なし）→ **不可（ステマ規制違反リスク直撃）**。
  - **第三者が自発的に無償で言及する** → 規制対象外。これが「被引用設計」の唯一の合法ルート。
- **英語圏でなぜ緩く見えるか**: 米国のFTC Endorsement Guidesも「material connection」の開示を求める点は同じだが、(a) 執行が事後・個別、(b) プラットフォーム側の自主ルール（Reddit/Quoraのself-promotion規約）が実質的な規律になっており、(c) 「対価なしのUGC上での自然言及」を作るためのPR/コミュニティ運用が産業として成立している。**「日本では違法で海外では合法」なのではなく、「海外の実務書が前提としている“無償の第三者言及を大量に発生させる体力”を、日本の個人メディアが持ちにくい」**というのが実態差。

---

## 5-01. サイト評判の不正使用ポリシー後のパラサイトSEO（Parasite SEO post-Site Reputation Abuse）

- **一言で**: 他人の強いドメインに記事を間借りして上位を取る手法。2026年時点で「ドメインパワーの又貸し」部分は死んでおり、生き残ったのは「そのプラットフォームの本来の目的に沿った、編集監督のあるコンテンツ」だけ。
- **海外での出典**:
  - [一次] Google Search スパムに関するポリシー（site reputation abuse セクション）https://developers.google.com/search/docs/essentials/spam-policies ※本文直接検証は egress ブロックにより不可
  - [二次] Parasite SEO in 2026: What Still Works After Google's Crackdown https://heroicrankings.com/seo/managed/what-is-parasite-seo/
  - [二次] Site Reputation Abuse: 2026 Survival Guide https://khalidseo.com/google-site-reputation-abuse-guide/
  - [二次] Siteimprove: Understand Google's site reputation abuse policy https://www.siteimprove.com/blog/understand-googles-site-reputation-abuse-policy/
- **仕組み／なぜ効くか**: 元々は「ホストドメインの権威をページ単位で継承する」ことが効いていた。Googleは2024年3月にポリシー化（手動対策のみ）→2024年11月に対象拡大→**2025年8月のSpam Updateでアルゴリズム的執行に移行**したとされる（[二次] heroicrankings / khalidseo）。現在Googleは、ホスト内のセクションを**親サイトから切り離して単独評価**する挙動を取る。つまり「借りた権威」は乗らない。残るのは「そのプラットフォーム自体がそのクエリで持っている本来の可視性」（＝これは5-02のBarnacleに近い）と、**AI引用面での露出**。
- **具体手順**:
  1. 対象プラットフォームが「自分の本来の目的に沿った第三者コンテンツ」として自分の記事を扱うか判定する（note・Reddit・YouTubeは○、ニュースサイトの提供枠・クーポン枠は×）。
  2. そのプラットフォーム内での検索・レコメンドで戦えるフォーマットに合わせて書く（Google順位を狙わない）。
  3. 自サイトへの誘導は「続きの深い情報」への導線に限定し、記事単体でも完結させる（プラットフォームの規約違反回避）。
  4. **有償の記事枠買い（sponsored post での順位借り）は行わない**。
  5. 3か月ごとにプラットフォーム別の流入・被引用を計測し、死んだ面は撤退。
- **日本での言及度**: **中**。実検索クエリ `バーナクルSEO パラサイトSEO 日本語 解説` → Ahrefs日本語ブログ（ https://ahrefs.jp/blog/seo/parasite-seo/ ）、Web担当者Forum用語集（ https://webtan.impress.co.jp/g/barnacle_seo ）、東京SEOメーカー（ https://www.switchitmaker2.com/seo/parasite-seo/ ）などが上位。**用語としては流通している。ただし日本語記事の論点が「メリット/手順」に偏り、2024-2025年のポリシー変更と2025年8月のアルゴリズム執行以降どう変わったかの記述が薄い。** Ahrefs日本語版が「churn and burn（使い捨て）アプローチ」に言及している程度。
- **日本市場での成立性**: 成立する。日本のプラットフォームでは note（会員777万人超、ドメインパワー96.4という試算 [二次] https://www.sungrove.co.jp/note-seo/ ／ https://note.com/alpaka_ai/n/nbcf99684616a ）が実質的な受け皿。noe-matchは既にnote寄生14本を稼働中。
- **noe-match適用度**: **B**。既に着手済みなので追加投資というより「方針の再定義」。**note記事を“Googleで上位を取るための器”ではなく、“note内検索・note内レコメンド・AI引用のための器”に書き換える**のが2026年の正解。工数: 既存14本の棚卸しに8〜12時間。
- **リスク・反証**:
  - **ステマ規制**: note記事に自サイトのアフィリエイト導線を置く場合、**noe-match自身の表示**なので「PR」「広告」表記が必要。**表記があれば可。なければ不可。**
  - **Google側リスク**: 「主に順位操作を目的とした第三者コンテンツ」と判定されればホスト側ごと処分される。noteのようなUGCプラットフォームは元々第三者投稿が本来目的なので直撃はしにくいが、**同一テーマの大量投稿は scaled content abuse 側で引っかかる**。
  - **反証**: 「借りた権威は乗らない」が2026年の前提なので、**note寄生の期待値は2023年比で大幅に低下している**と考えるべき。ここに再投資するより5-03〜5-11に配分したほうがよい可能性が高い。

---

## 5-02. バーナクルSEO（Barnacle SEO）

- **一言で**: 自分が上位を取るのではなく、**既にそのクエリで上位にいる他人のページの中で自分が名指しされる**状態を作る。パラサイトSEOと違い「ページを作る」のではなく「既存ページに寄生する」。
- **海外での出典**:
  - [二次] AIOSEO: How to Use Barnacle SEO https://aioseo.com/how-to-use-barnacle-seo/
  - [二次] Barnacle SEO in 2026: What It Is and How to Use It https://theclaymedia.com/barnacle-seo/
  - [二次] Barnacle SEO Examples (2026) https://theclaymedia.com/barnacle-seo-examples-2026/
  - [二次] SEOptimer（日本語版あり） https://www.seoptimer.com/ja/blog/barnacle-seo/
- **仕組み／なぜ効くか**: 検索1ページ目が「まとめ記事」「レビューサイト」「ディレクトリ」で埋まっているクエリでは、**個人が1位を取るより、その1ページ目のページ群に載るほうが早くて安い**。2026年の追加論点として、**AIアシスタント（ChatGPT/Perplexity/AI Overviews）が同じ第三者ページを引用元にしている**ため、1回の掲載が「Google1ページ目」と「AI回答内」の両方に効く（[二次] theclaymedia 2026版）。
- **具体手順**:
  1. 主要10クエリ（例:「結婚相談所 おすすめ」「婚活アプリ 比較」）のSERP1ページ目を全部書き出し、**自分が“載る側”になれるページ**を分類（まとめ記事／口コミサイト／Q&A／YouTube／Pinterest）。
  2. 各ページの掲載条件を調べる（掲載依頼フォーム、寄稿受付、取材募集）。
  3. **無償で掲載される正当な理由**を作る（独自データ、独自の体験談、専門家コメント提供）。
  4. 掲載依頼を送る。有償枠を提示された場合は5-22のリスク判定に従う。
  5. 掲載後、そのページがAI回答で引用されているかを月次でモニタする。
- **日本での言及度**: **低〜中**。上記の日本語クエリで用語解説（Web担、SEOptimer日本語版）は出るが、**「2026年のAI引用面まで含めたBarnacle戦略」を書いた日本語記事は上位に見当たらなかった**。日本語圏では「サジェスト対策」「MEO」に話が寄りがちで、**“他人の1位ページの中身になる”という発想の記事が薄い**。
- **日本市場での成立性**: 高い。むしろ日本のほうが成立しやすい。婚活/結婚領域の日本のSERPは「ゼクシィ」「マイナビウエディング」「みんなのウェディング」等の大手比較メディアが占有しており、**個人が1位を取るのはほぼ不可能な代わりに、載る先は明確に存在する**。
- **noe-match適用度**: **A**。個人運営・新規ドメインという条件に対して最も費用対効果が高い。工数: 初期のSERP棚卸し6時間＋掲載交渉が月4〜8時間の継続。
- **リスク・反証**:
  - **ステマ規制**: 「対価を払って掲載してもらい、PR表記なし」→**不可**。「取材を受ける」「専門家として無償でコメント提供する」→**可（対価がないので事業者の表示にならない）**。ただし**自社サイトの宣伝を条件に金銭・物品を受け渡した瞬間にアウト**。
  - **反証**: 個人メディアは「独自データ」や「専門家性」を提示しにくく、掲載が取れない可能性が高い。→ 5-25（Kindle出版で著者性を作る）、5-27（HARO型）と組み合わせないと単体では詰む。

---

## 5-03. Redditでの被引用設計（Reddit as the AI citation layer）

- **一言で**: 2026年のAI検索で単独最大の引用元がRedditである以上、**Reddit上で第三者が自分のブランド名を書いている状態**を作ることが、AI回答に載る最短経路になっている。
- **海外での出典**:
  - [一次寄り] Search Engine Land: AI search engines cite Reddit, YouTube, and LinkedIn most https://searchengineland.com/ai-search-engines-cite-reddit-youtube-and-linkedin-most-study-473138
  - [二次] AI Platform Citation Source Index 2026（Reddit 約40%） https://everything-pr.com/ai-platform-citation-source-index-2026
  - [二次] Contently: Top 10 Sources LLMs Cite Most in 2026（Peec AI 3,000万ソース／Semrush 32.5万プロンプト／Profound 140万引用／SE Ranking 12.9万ドメイン） https://contently.com/2026/04/29/top-sources-llms-cite/
  - [二次] Reddit×ChatGPT 120万引用調査 https://maxaeo.ai/blog/reddit-chatgpt-recommendations/
  - [一次] Google-Reddit $60M/年ライセンス契約（2024年2月） https://www.tomsguide.com/ai/google-strikes-dollar60m-deal-with-reddit-for-ai-training-data-what-you-need-to-know
  - [一次] CNBC: Reddit、Google AIコンテンツ契約を更新しない可能性（2026年7月22日） https://www.cnbc.com/2026/07/22/reddit-stock-google-ai-content-deal.html
- **仕組み／なぜ効くか**: (a) Googleは2024年2月からRedditに年6,000万ドルを払ってリアルタイムコンテンツにアクセスしており、Google製品内でRedditコンテンツが前面に出るようになった。(b) LLM側はReddit投稿を「体験ベースかつコミュニティ検証済み」の一次情報として扱う。結果、**Redditスレッド1本が、Google検索・AI Overviews・ChatGPT・Perplexityの4面に同時に影響する**。
- **具体手順**:
  1. 対象subredditを選ぶ（英語圏なら r/weddingplanning, r/Marriage, r/dating_advice。**日本語圏は r/japanlife 等しかなく、日本語ユーザー向けには機能しない — 後述**）。
  2. アカウントを2〜4週間「熟成」させる。主要subredditは投稿に **100〜1,000カルマ** を要求する（[二次] https://www.teract.ai/resources/get-reddit-karma-2026 ／ https://www.soar.sh/blog/karma-to-create-subreddit-2026 ）。
  3. 80/20ルール: **80%は自社と無関係な有益コメント、20%だけブランド文脈**（[二次] https://www.subredditanalyzer.com/how-to-do-a-reddit-ama ）。
  4. 自社に言及する際は**所属を明示**（Redditの規約とステマ規制の両方を同時に満たす唯一の書き方）。
  5. 「無関係なRedditorが自発的に自社名を出す」状態を最終目標に置く（[二次] https://www.withkarmic.com/reddit-marketing-guide が "white whale" と表現）。
  6. 直接宣伝したい場合は**Reddit広告を使う**（規約準拠かつ表示が広告として明示される）。
- **日本での言及度**: **ほぼ無**（AI引用元としてのReddit戦略に限れば）。実検索クエリ `Reddit 日本 ユーザー数 2026 日本語 subreddit 規模` → 出てきたのは「Redditとは何か」「海外掲示板の使い方」「Reddit広告の紹介」系（ https://www.icrossborderjapan.com/blog/archives/11642/ ／ https://statusbrew.co.jp/insights/reddit-social-media-marketing ）。**「Redditに書かれることでAI回答に載る」という2026年の中核論点を扱った日本語記事は上位に皆無。** これは本調査で最も日本語言及が薄い領域のひとつ。
- **日本市場での成立性**: **低い（これが最大の落とし穴）**。RASA JAPANの357人調査で日本人の**59%がRedditを認知**しているものの、**日本のRedditユーザーの多くはライトユーザーで、アクティブ層は少数派**と明記されている（[一次] プレスリリース https://prtimes.jp/main/html/rd/p/000000033.000062299.html ）。日本語で婚活を検索する人はRedditにいない。**ただし「日本語クエリに対するAI回答の引用元」がRedditである可能性は別問題**で、日本語プロンプトでも英語Redditが引用されるケースはある。noe-matchの読者は日本語話者なので、**Redditは“読者獲得”ではなく“AI引用”のためだけのチャネル**という位置づけになる。
- **noe-match適用度**: **C**（日本語読者向けとしては）／**限定的にB**（英語圏の国際結婚・在日外国人配偶者クエリ向けなら）。工数: カルマ熟成に週2時間×4週＝8時間、その後継続で週1〜2時間。**投資対効果は日本語メディアとしては低い。**
- **リスク・反証**:
  - **Reddit規約**: 複数アカウント運用、自演アップボート、レビュー投稿依頼は **IP/デバイス/行動パターンで検出され一括BAN**（[二次] https://webofpicasso.net/blog/reddit-marketing-without-getting-banned ）。
  - **ステマ規制**: 「自演でnoe-matchを推奨する日本語投稿」→**不可**。「所属を明示して回答する」→**可**。
  - **最大の反証**: Redditは2026年7月時点でGoogleとのライセンス契約を更新しない可能性を検討中で、報道でReddit株が9%下落した（[一次] https://qz.com/reddit-stock-google-ai-content-deal-072226 ／ https://www.cnbc.com/2026/07/22/reddit-stock-google-ai-content-deal.html ）。**契約が切れればRedditの被引用シェア40%という前提自体が崩れる可能性がある。この手法に重投資するのは2026年後半時点では危険。**

---

## 5-04. Reddit AMA（Ask Me Anything）

- **一言で**: 「専門家として何でも聞いて」スレッドを立て、**質問と回答のセットを一気に生成する**手法。Q&A形式はLLMの引用フォーマットとして最も噛み合う。
- **海外での出典**:
  - [二次] The Brand AMA Playbook: How to Run a Reddit AMA in 2026 https://forkoff.xyz/blog/reddit-marketing/brand-ama-reddit-playbook-2026
  - [二次] How to Do a Reddit AMA (Complete 2026 Playbook) https://www.subredditanalyzer.com/how-to-do-a-reddit-ama
  - [二次] Reddit AMA Strategy for Founders https://redditgrow.ai/guides/reddit-ama-strategy
  - [二次] Reddit AMAs: Building Brand Authority in 2026 https://www.imarkinfotech.com/reddit-amas-the-secret-to-building-brand-authority/
- **仕組み／なぜ効くか**: AMAは (a) 自己言及が**規約上明示的に許可された唯一の形式**、(b) 一度のセッションで数十のQ&Aペアが生成され、それが長期にわたりインデックス・引用される、(c) mod承認プロセスが「第三者による検証」の役目を果たしE-E-A-T的シグナルになる。
- **具体手順**:
  1. **ニッチsubredditを選ぶ。** r/IAmA（最大だが承認が最も難しく相応の知名度が要る）より、テーマ特化subredditのほうが成果が高い（[二次] subredditanalyzer）。
  2. 事前に30日、当該subredditで非宣伝的なコメントを積む。
  3. **目標日の1〜2週間前にmodmailでmodに連絡**し、認証要件・ルールを確認。
  4. 本番は最低2〜3時間フル張り付き、24時間以内に追加質問へ再訪。
  5. 終了後、AMAスレッドを自サイトの記事に転載（要約＋出典リンク）して二次利用。
- **日本での言及度**: **ほぼ無**。日本語で「AMA」は「Ask Me Anything」より先に別語義がヒットする状態で、**マーケ手法としてのAMA運用ガイドの日本語記事は流通していない**（`Reddit 日本 ユーザー数...` クエリの結果からも、日本語圏のReddit記事は入門解説止まり）。
- **日本市場での成立性**: **低い。** 日本語圏に相当プラットフォームがない。**最も近い日本の代替は (a) Yahoo!知恵袋の企業公式アカウント（5-06）、(b) X（Twitter）のスペース＋質問箱、(c) noteのコメント/メンバーシップQ&A**。ただしいずれもAMAほどの「一括Q&A生成×高権威ドメイン」効果はない。
- **noe-match適用度**: **C**。英語圏読者を取りに行かないなら不要。ただし**「AMA的フォーマット（想定質問30個に一気に答える）」を自サイトとnoteで再現する**という形式の輸入は **B** の価値がある。工数: フォーマット輸入なら記事1本4時間。
- **リスク・反証**: mod承認なしのAMAは削除＋BAN。ステマ規制上は「所属を明示した本人による回答」なので**問題なし（そもそも本人と分かる形式）**。反証: 知名度ゼロの個人がAMAを立てても質問が集まらず、空振りスレッドが残るだけになるリスクが高い。

---

## 5-05. Quora / 英語圏Q&A と、日本のQ&A公式回答制度

- **一言で**: Q&Aサイトは「質問文＝検索クエリそのもの」なのでAIが引用しやすい。**日本では自演不可だが、Yahoo!知恵袋には“企業公式アカウント”という完全に合法な公式回答制度が存在し、これがほぼ知られていない。**
- **海外での出典**:
  - [二次] Quora SEO: Q&A for AI Visibility https://thestacc.com/blog/quora-seo-ai-visibility/
  - [二次] Reddit and Quora drive over half of AI citations https://www.farandwide.io/blog/reddit-quora-ai-citations
  - [二次] 100+ AI SEO Statistics 2026 https://www.position.digital/blog/ai-seo-statistics/
- **日本側の出典**:
  - [一次] Yahoo!知恵袋 公式・専門家 https://chiebukuro.yahoo.co.jp/expert/
  - [一次] Yahoo!知恵袋 企業公式アカウント一覧 https://chiebukuro.yahoo.co.jp/expert/enterprise.html
  - [一次] Yahoo!知恵袋 お知らせ「企業公式および専門家の投稿履歴が閲覧できるようになりました」2025-01-29 https://chiebukuro.yahoo.co.jp/blog/2025/01/29-01.html
  - [一次] 第一生命保険「Yahoo!知恵袋 企業公式アカウントによる質問回答の開始について」2020-09-23 https://www.dai-ichi-life.co.jp/information/pdf/index_048.pdf
- **仕組み／なぜ効くか**: Quoraは **AI Overviews引用の約5%** を占め、被引用ドメイン全体で4位という集計がある。Semrushは **Google AI Modeで引用された26,000のQuora URL** を分析している（[二次] thestacc）。またQuoraは2023年6月比で **+379.33%** の成長という数字も出ている（同）。理屈としては、Q&Aの「質問文」が自然言語クエリと1:1で対応するため、retrievalで最短距離になる。
- **具体手順（日本での合法ルート）**:
  1. Yahoo!知恵袋の**企業公式アカウント**登録を専用フォームから申請する（花王公式サポート、シェアフル、ルルルン等が既に運用中）。
  2. 承認後、自社の商品・サービス・専門領域に関する質問にのみ回答する（他社比較・宣伝は不可）。
  3. 回答は「公式」バッジ付きで表示されるため、**開示が構造的に担保され、ステマ規制を自動的にクリアする**。
  4. 2025年1月以降、企業公式・専門家の投稿履歴がMy知恵袋で一覧閲覧できるので、そのページ自体を実績ページとして扱う。
  5. 並行して、英語圏向けにはQuoraで実名＋所属明記で回答する。
- **日本での言及度**: **ほぼ無（これが本調査のトップ発見のひとつ）**。実検索クエリ `Yahoo!知恵袋 公式回答 企業 制度 参加` → 出てくるのは**知恵袋公式のお知らせページと参加企業のプレスリリースのみで、「SEO/AEO手法としてこれを使え」と論じた日本語マーケ記事が上位に一切ない**。知恵袋ユーザー自身が「企業公式アカウントって何？」と知恵袋で質問しているレベル（ https://detail.chiebukuro.yahoo.co.jp/qa/question_detail/q11179348101 ）。**制度は6年前から存在するのにマーケ手法として全く語られていない。**
- **日本市場での成立性**: 制度としては確実に存在し稼働中（参加企業一覧が公開されている）。ただし **noe-matchのような個人運営メディアが「企業公式」として承認されるかは未確認**。「専門家」枠のほうが個人には現実的な可能性がある。※この承認可否は本調査では確認できていない。**未解決事項に記載。**
- **noe-match適用度**: **B**（承認が取れれば **A**）。婚活/結婚は知恵袋の質問密度が極めて高い領域。工数: 申請＋要件確認に3〜5時間、承認後は週1〜2時間。
- **リスク・反証**:
  - **ステマ規制**: 企業公式アカウント＝**開示済みなので完全に合法**。逆に**一般アカウントで自演質問・自演回答をして自サイトに誘導するのは明確に不可**（事業者の表示の隠蔽）。
  - **反証**: 知恵袋のGoogleでの可視性は近年低下傾向にあり、Quoraの英語圏でのAI被引用シェアがそのまま知恵袋に当てはまる保証はない。**「知恵袋がAI回答で日本語クエリの引用元になっているか」の実測データは本調査では発見できなかった（未解決事項）。**

---

## 5-06. YouTube SEO（長尺・how-to）

- **一言で**: 2026年のAI Overviewsで最も引用される動画ソースがYouTubeで、しかも**再生数ではなく「説明欄の長さ」と「チャプター構造」が引用の主要予測因子**という反直感的な実測がある。
- **海外での出典**:
  - [二次] Citation Share Report: YouTube Now Owns 23% of Every Google AI Answer https://www.5wpr.com/research/youtube-ai-citation-share-report-2026/
  - [二次] YouTube AI Citation Study 2026 (OtterlyAI) https://otterly.ai/blog/youtube-ai-citation-study-2026/
  - [二次] 50 Video SEO Statistics for 2026 https://vidico.com/news/video-seo-statistics/
  - [二次] YouTube SEO for AI Citations: A Technical 2026 Guide https://nadiamohamed.me/insights/youtube-seo-ai-citations/
- **仕組み／なぜ効くか**:
  - YouTubeはGoogle AI Overviews引用の **約23.3%**（次いでWikipedia 18.4%、Google.com 16.4%）（[二次] 5WPR）。別集計では **AI Overviewsの29.5%がYouTubeを引用**（[二次] Otterly）。
  - ソーシャル/動画系引用の中では **YouTubeが31.8%** を占め、そのうち **長尺が94%、Shortsが5.7%**（[二次] Otterly）。→ **AI引用目的ならShortsではなく長尺**。
  - **再生数・高評価・登録者数は引用頻度とほぼ無相関。最強の予測因子は「説明文の長さ」と「タイムスタンプ/チャプター構造」**（[二次] Otterly）。これは「LLMは動画の再生数を見ていない、テキストを見ている」という当然の帰結で、**個人チャンネルでも構造さえ作れば引用され得る**ことを意味する。
  - 一方、**Google SERPの動画枠は縮小中**: 2026年7月20日時点で動画は追跡結果の **38.5%** に出現、90日間で最低、ピークの53.7%から下落（[二次] vidico）。
- **具体手順**:
  1. 「婚活 何から始める」「結婚 挨拶 手順」等、**手順型（how-to）クエリ**に絞って動画を作る。
  2. **説明欄を長文で書く**（要約＋章立て＋各章の要点をテキストで）。ここが引用の主戦場。
  3. **チャプター（タイムスタンプ）を必ず設定**する。
  4. 字幕は自動生成任せにせず修正版をアップ（テキスト精度が引用精度に直結）。
  5. 動画ページから自サイトの対応記事へリンク、記事側にも動画を埋め込む。
  6. Otterly系ツールで「自チャンネルがAI回答に出るか」を月次モニタ。
- **日本での言及度**: **低**。日本語の「YouTube SEO」記事は大量にあるが、**「AI Overviewsの引用元としてのYouTube」「再生数は引用と無相関」「長尺94% vs Shorts 5.7%」という2026年の実測を扱った日本語記事は本調査の検索範囲では確認できなかった**。※日本語専用クエリ未実行のため厳密には未検証。日本語SEO情報の一般傾向から「低」と推定。
- **日本市場での成立性**: 高い。YouTubeは日本最大級の動画プラットフォームで、婚活/結婚領域の日本語動画需要は明確に存在する。
- **noe-match適用度**: **A**。ただし**動画制作コストが個人には重い**のが唯一のネック。工数: 1本あたり企画〜公開で6〜10時間。**回避策として「顔出しなし・スライド＋ナレーション」で説明欄とチャプターだけ本気で作る形式なら1本3時間程度に圧縮でき、引用目的なら十分**（引用予測因子が説明文とチャプターである以上、映像品質は二の次）。
- **リスク・反証**:
  - **ステマ規制**: 動画内でアフィリエイト先を紹介するなら**動画内表示＋説明欄冒頭に「PR」表記が必要**。
  - **反証**: SERPの動画枠自体は縮小中（53.7%→38.5%）なので、「Google検索での動画枠占有」を狙う旧来の理由は弱まっている。**やるならAI引用目的で、指標もAI引用率で見るべき。**

---

## 5-07. YouTube Shorts / ショート動画の検索インデックス化

- **一言で**: GoogleはYouTube Shorts / Instagram Reels / TikTokをインデックスしており、ショート動画が検索面に出るようになった。**ただしAI引用面では長尺に大差で負ける。**
- **海外での出典**:
  - [二次] How YouTube Shorts Discovery Works: Search, Indexing, and Identity Signals https://www.social-searcher.com/2026/03/13/youtube-shorts-search-discovery/
  - [二次] YouTube Shorts SEO in 2026 (Lawrence Hitches) https://www.lawrencehitches.com/youtube-shorts-seo/
  - [二次] Search-First YouTube Shorts in 2026 https://miraflow.ai/blog/search-first-youtube-shorts-2026-formats-that-win-google-youtube-search
  - [二次] Otterly（Shortsは動画引用の5.7%） https://otterly.ai/blog/youtube-ai-citation-study-2026/
- **仕組み／なぜ効くか**: Googleがショート動画をインデックスし、YouTubeのAI検索サマリーもShortsを直接引用するようになった。マルチモーダルモデルが動画本体を解析する方向に進んでいるため、オンスクリーンテキスト・キャプションが読まれる。**ただし現時点の実測ではShortsのAI引用シェアは5.7%にとどまる。**
- **具体手順**:
  1. 長尺動画の「1つの問いに30秒で答える」部分を切り出す。
  2. **オンスクリーンテキストで問いと答えを明示**（音声だけに依存しない）。
  3. タイトル・説明・キャプションにクエリ語をそのまま入れる。
  4. Shortsから長尺・自サイトへの導線を固定文で置く。
  5. 効果測定は「Shorts単体の引用」ではなく「チャンネル全体の指名検索増」で見る。
- **日本での言及度**: **中**。日本語の「ショート動画運用」記事は多いが、**「Googleがショートをインデックスしていること」「AI引用では長尺が94%」という切り分けの記述は薄い**と推定（日本語専用クエリ未実行、未検証）。
- **日本市場での成立性**: 高い。ショート動画の視聴習慣は日本でも一般化している。
- **noe-match適用度**: **B**。長尺の副産物としてなら低コスト。**Shorts単体に投資する根拠は現時点の数字では弱い。** 工数: 長尺1本から3〜5本切り出しで2時間。
- **リスク・反証**: ステマ規制上は5-06と同じ（PR表記必須）。反証: **「ショートは伸びる」という日本語圏の一般論と、「AI引用ではショートは弱い」という実測が矛盾する。目的（読者獲得 vs AI引用）で判断を分けること。**

---

## 5-08. TikTok SEO / TikTokを検索面として使う

- **一言で**: 「Z世代はGoogleよりTikTokで検索する」は**半分正しく半分は誇張**で、2026年のデータでは"TikTokをGoogleより優先する"層はむしろ半減している。
- **海外での出典**:
  - [一次寄り] SEJ: Gen Z Preference For TikTok Over Google Drops 50%, Data Shows https://www.searchenginejournal.com/gen-z-preference-for-tiktok-over-google-drops-50-data-shows/568267/
  - [二次] 49% of U.S. Consumers Now Use TikTok as a Search Engine https://almcorp.com/blog/tiktok-as-search-engine-2026-data/
  - [二次] TikTok SEO Statistics 2026 (Rise at Seven) https://riseatseven.com/blog/tiktok-seo-statistics/
  - [二次] Is TikTok the New Search Engine? (SEO Sherpa) https://seosherpa.com/tiktok-search-engine/
- **仕組み／なぜ効くか**: Adobe 2026調査でZ世代の **65%** が「TikTokを検索エンジンとして使ったことがある」（2025年は64%）。米消費者の **49%** がTikTokを検索に使う。**一方で「GoogleよりTikTokに頼る」と答えたZ世代は2024年の8%から2026年は4%へ半減**（[一次寄り] SEJ）。→ **TikTokは"Googleの代替"ではなく"検索エコシステムの1ノード"**というのが2026年の正確な読み。
- **具体手順**:
  1. 「〜のやり方」「〜の相場」型の短い問いに絞る。
  2. 冒頭2秒で問いをオンスクリーンテキストで提示。
  3. キャプション・ハッシュタグにクエリ語を自然文で入れる。
  4. プロフィール欄に自サイトリンク（TikTokは投稿本文からの外部リンクが弱いため）。
  5. TikTok経由の指名検索増を Search Console のブランドクエリで測る。
- **日本での言及度**: **中**。日本語の「TikTok SEO」記事は増えているが、**「Z世代のTikTok優先は半減した」という反証データを載せている日本語記事は稀**と推定（未検証）。
- **日本市場での成立性**: TikTokの日本ユーザー規模は大きいが、**婚活・結婚相談所という「高関与・高単価・慎重に比較する」商材とTikTokの相性は良くない**。TikTokは認知には効くが比較検討フェーズの流入にはなりにくい。
- **noe-match適用度**: **C**。工数対効果が低い。個人運営でYouTube・Pinterest・noteを回しながらTikTokまで持つのは非現実的。
- **リスク・反証**: ステマ規制上、アフィリエイト誘導するならPR表記必須。反証: 上記のとおり「TikTok検索」の伸びは頭打ちの兆候がある。

---

## 5-09. InstagramのGoogleインデックス化を利用する

- **一言で**: 2025年7月10日から、**公開のInstagramビジネス/クリエイターアカウントの投稿がGoogleにインデックスされるようになった**。Instagramが実質「サブドメイン」化した。
- **海外での出典**:
  - [一次寄り] Forbes: What Google Indexing Instagram Means For Your Business Visibility https://www.forbes.com/sites/chelseatobin/2025/07/10/what-google-indexing-instagram-means-for-your-business-visibility/
  - [二次] PPC Land: Instagram content becomes searchable on Google starting July 10 https://ppc.land/instagram-content-becomes-searchable-on-google-starting-july-10/
  - [二次] Does Google Index Instagram? 2026 Guide https://www.inro.social/blog/instagram-google-indexing-2025
  - [二次] Google's Social Indexing Shift: What It Means for Brands in 2026 https://www.diamond-group.co/blog/googles-social-indexing-shift-what-it-means-for-brands-in-2026
- **仕組み／なぜ効くか**: 対象は**公開のビジネス/クリエイター/18歳以上アカウントのみ**（個人アカ・非公開・未成年は対象外）。投稿URLが検索結果・AI Overviews・音声検索に出るようになった。LinkedIn/YouTube/Instagramのページが「ブランドのサブドメインのように振る舞う」という表現が使われている。
- **具体手順**:
  1. アカウントを**プロフェッショナル（ビジネスまたはクリエイター）に切り替え、公開に設定**（これをしないとインデックス対象外）。
  2. ユーザー名・bio・キャプション・オンスクリーンテキスト・altテキストにクエリ語を入れる（Instagram自身がこれらを走査する）。
  3. キャプションを「短い煽り文」ではなく**検索されうる問いへの答え**として書く。
  4. 保存されやすいカルーセル（チェックリスト型）を作る。
  5. Search Consoleではなく、`site:instagram.com/自アカウント` でインデックス状況を目視確認。
- **日本での言及度**: **低**。日本語の「Instagram運用」記事は膨大だが、**「2025年7月からGoogleインデックス対象になった」という技術的変更と、それに伴うキャプション設計の変更を論じた日本語記事は薄い**と推定（未検証）。
- **日本市場での成立性**: 非常に高い。**日本の婚活・ウェディング領域はInstagram利用が極めて濃い**（プレ花嫁文化）。ただしnoe-matchは現在Xを2アカウント運用しており、Instagram新規はリソース勝負になる。
- **noe-match適用度**: **B**。婚活/ウェディング領域とInstagramの親和性は高いが、Pinterest（5-10）と食い合う。**Pinterest優先、Instagramは同じ縦画像素材の二次利用にとどめる**のが現実的。工数: Pinterest素材の転用なら追加2時間/週。
- **リスク・反証**: ステマ規制上、アフィリエイト・PR案件はキャプション冒頭に「PR」必須。反証: インデックスされることと**上位に出ることは別**。Instagram投稿が競合の記事を押しのけて上位化する保証はない。

---

## 5-10. Pinterest SEO（結婚・ウェディング領域）

- **一言で**: **英語圏では結婚領域における最大級の流入源。Pinterestは「SNS」ではなく「意思決定前のビジュアル検索エンジン」で、婚約前から使われ始めるという点が他チャネルと決定的に違う。**
- **海外での出典**:
  - [一次] Pinterest公式データ（Social Media Today報道）: Pinterest Releases New Data on How People Use the Platform for Wedding Plans https://www.socialmediatoday.com/social-business/pinterest-releases-new-data-how-people-use-platform-wedding-plans
  - [二次] Pinterest Bridal Trends https://bridalbuyer.com/business/business/pinterest-bridal-trends-2019--9659
  - [二次] 6 Pinterest SEO Tips for Wedding Photographers https://photobugcommunity.com/business-advice/5-pinterest-seo-tips-for-wedding-photographers/
  - [二次] 135 Wedding Industry Statistics and Trends (2026 Update) https://saradoesseo.com/wedding-marketing/wedding-industry-statistics/
  - [二次] How Pinterest Can Become Your Wedding Biz Bestie https://studiogail.co/pinterest-for-wedding-business/
- **仕組み／なぜ効くか**:
  - **4,000万人超が結婚式の計画にPinterestを使い、結婚関連検索は年間3億7,800万回**（[一次寄り] Pinterest公式データ／Social Media Today）。
  - **エンゲージ済みPinnerの81%が「婚約する前から」ピンを始めている**（同）。→ **競合の婚活メディアが「婚約後」を取りに行っている間に、Pinterestは「婚約前」を取れる。noe-matchが婚活〜結婚〜新生活を縦に持つのと構造が一致する。**
  - Pinnerの27%が1日に数回結婚式の計画をする（非Pinnerは18%）。
  - **繁忙期は1〜3月**（同）。
  - **ピンの寿命が6〜12か月と長い**（[二次] 日本語記事 https://aidaim.co.jp/pinterest-seo/ ）。SNS投稿の寿命が数時間なのに対し桁が違う。
  - トラフィックの85%がモバイルアプリ経由。
- **具体手順**:
  1. ビジネスアカウント作成＋**ウェブサイトの所有権確認（Claim your website）**。これをしないと分析もリッチピンも使えない。
  2. 既存記事から**縦長画像（2:3）**を1記事あたり3〜5枚生成。同じ記事に対して異なる切り口の画像を作る（Pinterestは同一URLへの複数ピンを許容する）。
  3. **ピンのタイトル・説明文を「Pinterest内検索クエリ」で書く**（「結婚式 席次表 テンプレート」等）。ボードの名前と説明も検索対象。
  4. **1〜3月の繁忙期に向けて、3〜4か月前（10〜12月）からピンを投入**（ピンの評価に時間がかかるため）。
  5. リッチピン（Article Rich Pin）を有効化してタイトル・説明を自動同期。
  6. 効果は「3〜6か月で表示回数と保存数、6〜12か月でアウトバウンドクリック」という段階で見る（[二次] aidaim）。
- **日本での言及度**: **低〜中（ただし“ウェディング領域の実データ”に限れば ほぼ無）**。実検索クエリ `Pinterest SEO 日本語 やり方 集客 ブログ流入` → SEO Japan（ https://seojapan.com/column/all-about-pinterest/ ）、アイダイム（ https://aidaim.co.jp/pinterest-seo/ ）等、**運用ノウハウ記事は一定数存在する**。しかし実検索クエリ `Pinterest ウェディング 結婚 日本 検索 トレンド 2026 花嫁` → **返ってきたのはゼクシィ・マイナビウエディング等の“花嫁向けトレンド記事”ばかりで、「Pinterestが結婚領域の流入源である」という日本語のマーケ論考は1件も出てこなかった。** ここが本調査で最も明確な空白。
- **日本市場での成立性**: **成立する。ただし規模は英語圏の1/50程度と見るべき。**
  - Pinterest日本の月間利用者数は **1,280万人**（2025年3月時点、ニールセン調査、[二次] https://www.comnico.jp/we-love-social/sns-users ）。別集計では**約1,050万人/月**（[二次] https://www.uniad.co.jp/260204 ）。
  - グローバルMAUは **6億3,100万人**（2026年Q1、[二次] https://www.icrossborderjapan.com/blog/archives/17341/ ）。→ **日本比率は約2%。**
  - つまり「4,000万人が結婚式計画に使う」という米国主体の数字を日本にそのまま当てはめてはいけない。**しかし競合密度も同じ比率で薄いため、参入コストあたりのリターンはむしろ日本のほうが高い可能性がある。**
- **noe-match適用度**: **A（本調査での最優先推奨）**。理由: (a) 個人運営で唯一「ドメインパワー不要・被リンク不要・記事を書き直さなくていい」チャネル、(b) 既存記事の資産をそのまま縦画像に変換するだけで在庫が作れる、(c) ピン寿命6〜12か月で新規ドメインのハンデが効かない、(d) **婚約前の層を取れる唯一のチャネル**。工数: 初期セットアップ4時間＋既存記事の画像化が1記事30分×本数。週2時間で回せる。
- **リスク・反証**:
  - **ステマ規制**: ピンから自サイト（アフィリエイト記事）へ飛ばす場合、**ピン自体には表記不要だが、着地する自サイト記事にPR表記が必要**（自サイト側で担保されていればOK）。**ピンの説明文で直接アフィリエイトリンクを貼るのは、Pinterest規約上もステマ規制上も避けるべき。**
  - **Pinterest規約**: アフィリエイトリンクの直貼りは過去に禁止→解禁→制限と変遷しており、**現行ポリシーの直接確認が必要（本調査では未確認、未解決事項）。**
  - **反証1**: 日本語圏のPinterest人口が1,280万人という数字は「月間利用者」であり、**そのうち結婚式を計画中の層が何人いるかは不明**。「日本のPinterestウェディング需要」の実データは本調査では発見できなかった。
  - **反証2**: 日本語記事に「Pinterestのリピンが被リンクになる」という主張がある（ https://sb-wegazine.net/seo-pinterest-backlink/ ）が、**Pinterestの外部リンクは基本的にnofollow相当であり、被リンク効果を期待するのは誤り**。流入と認知のチャネルとして評価すべき。

---

## 5-11. Wikipedia記事化（エンティティ登録の正攻法）

- **一言で**: WikipediaはAI Overviews引用の **18.4%**（YouTubeに次ぐ2位）を占める。**ただし個人運営メディアは「特筆性」を満たさないので、正攻法では原則不可能。**
- **海外での出典**:
  - [二次] 5WPR Citation Share Report（Wikipedia 18.4%） https://www.5wpr.com/research/youtube-ai-citation-share-report-2026/
  - [二次] Wikipedia for Brand SEO: The LLM Citation Playbook https://seoengico.com/blog/wikipedia-brand-seo-llm-citations-2026
  - [二次] 12 Wikipedia Notability Requirements https://staydigitalmarketers.com/2026/03/30/wikipedia-notability-requirements/
  - [一次] Wikipedia:利益相反行為（日本語版） https://ja.wikipedia.org/wiki/Wikipedia:%E5%88%A9%E7%9B%8A%E7%9B%B8%E5%8F%8D%E8%A1%8C%E7%82%BA
  - [一次] Wikipedia:有償の寄稿の開示（ウィキメディア財団方針かつ日本語版方針） https://ja.wikipedia.org/wiki/Wikipedia:%E6%9C%89%E5%84%9F%E3%81%AE%E5%AF%84%E7%A8%BF%E3%81%AE%E9%96%8B%E7%A4%BA
- **仕組み／なぜ効くか**: WikipediaはGoogleナレッジパネルとWikidataの供給源であり、LLMの学習・retrieval双方で高い重みを持つ。記事があると**ブランド名検索でナレッジパネルがほぼ確実に出る**。
- **具体手順（正攻法のみ）**:
  1. **記事を書く前に「特筆性」を満たす証拠を集める**: 「独立した信頼できる二次情報源における有意な言及」が複数必要。プレスリリース・自社サイト・アフィリエイト記事は**すべて不可**。
  2. 満たしていない場合、**先に外部メディア掲載を作る**（5-27のHARO型、業界誌への寄稿、新聞・雑誌の取材）。これが数年単位の話になる。
  3. 満たしてから、**利益相反を必ず開示**して編集依頼を出す（自分で書かない）。
  4. 有償で編集代行を使う場合、**「有償の寄稿の開示」方針により開示義務がある**。無開示の有償編集は方針違反。
  5. 個人名（運営者名）での立項も、著書・メディア出演等の特筆性がなければ同様に不可。
- **日本での言及度**: **低**。実検索クエリ `Wikipedia 日本語版 特筆性 企業記事 利益相反 有償編集 方針` → 上位はWikipedia自身の方針ページと、**note上のマーケター記事（フランクマーケティング／PR型LLMO・相澤）が数本**（ https://note.com/frank_pr/n/nef9138ac63c0 ／ https://note.com/frank_marketing/n/n323afea23659 ）。**「AI検索時代のWikipedia戦略」を論じた日本語記事は、ほぼこの1〜2アカウントのnote記事に依存している状態で、業界的な流通はしていない。**
- **日本市場での成立性**: 制度としては当然存在。ただし**日本語版Wikipediaは企業記事の特筆性判定が英語版より厳しい傾向があり、削除依頼も活発**。
- **noe-match適用度**: **C**（現時点）。2026年6月開設・個人運営のアフィリエイトメディアが特筆性を満たす見込みはゼロ。**ただし「将来的にWikipedia立項可能な状態」を目標に置くこと自体は、5-25（書籍出版）・5-27（メディア掲載）の方向性を規定する良い指針になる。**
- **リスク・反証**:
  - **ステマ規制**: 「自社について有償で書かせ、開示しない」→**景表法以前にWikipedia方針違反。かつ事業者の表示の隠蔽としてステマ規制にも触れうる。不可。**
  - **反証**: 無理に立項を試みると削除依頼＋ブロック＋「ネガティブな痕跡」が残る。**やらないほうがマシな典型例。**

---

## 5-12. Wikidataへのエンティティ登録

- **一言で**: **Wikipediaより参入障壁が低い構造化データ層。ナレッジグラフとLLMのエンティティ認識に直接効く。「Wikipediaは無理でもWikidataなら」という抜け道として英語圏では定番化しているが、日本語圏ではほぼ語られていない。**
- **海外での出典**:
  - [二次] MLforSEO: Wikidata for Brands — Notability Criteria and a Realistic Path https://www.mlforseo.com/knowledge-graph-strategy/wikidata-for-brands-notability-criteria-and-a-realistic-path/
  - [二次] ReputationX: Wikidata for SEO — How Brands Use It to Win Google [2026] https://www.reputationx.com/blog/wikidata
  - [二次] Wikidata and SEO: The Secret Tool Behind Google's Knowledge Graph https://www.wikibusines.com/wikidata-seo-knowledge-graph
- **仕組み／なぜ効くか**: WikidataはWikipediaの下層にある機械可読データ層で、**Google、LLMの学習パイプライン、多くのナレッジグラフ実装に直接エンティティ情報を供給している**（[二次] MLforSEO）。**Wikipediaと違い、ほとんどの事業者は通知性要件なしに手動でWikidataエントリを作成できる**（[二次] ReputationX）。ただし**障壁はゼロではなく**、要件を誤解して削除されるケースが多い（[二次] MLforSEO）。
- **具体手順**:
  1. Wikidataの notability 要件（3項目のいずれか、特に「serious and publicly available references」）を読む。
  2. 外部の識別子（公式サイト、SNSアカウント、ISBN、ORCID等）を先に揃える。**識別子が多いほど削除されにくい。**
  3. 最小限のステートメント（instance of / official website / country / inception）で作成する。
  4. **自分と関係のあるエンティティを作る場合は利益相反を開示**。
  5. 自サイト側に `sameAs` を含むschema.org構造化データを置き、Wikidata QIDを参照させる。
- **日本での言及度**: **ほぼ無**。上記の日本語Wikipediaクエリでも、Wikidata単体を「SEO/AEO手法」として論じた日本語記事は上位に出てこなかった。**日本語圏では「Wikidata」はほぼ図書館情報学・オープンデータ文脈でしか語られていない。本調査における日本語言及度が最も低い項目のひとつ。**
- **日本市場での成立性**: 成立する。Wikidataは言語非依存の構造化データなので、**日本語ラベルを付けたエンティティを作れば日本語クエリにも効く。しかも競合が誰もやっていない。**
- **noe-match適用度**: **B**。ただし「Noe結婚設計室」というアフィリエイトメディアがWikidataの notability を満たすかは微妙。**先に5-25（Kindle出版）でISBN/ASIN等の外部識別子を作り、「著者」としてのエンティティを立てるルートのほうが現実的**。工数: 要件確認＋作成で4〜6時間、ただし削除リスクあり。
- **リスク・反証**:
  - **ステマ規制**: Wikidataは「事実の構造化記録」であり広告表示ではないため、**開示さえすれば規制対象外**。
  - **反証**: **Wikidataエントリ単体でAI引用が増えるという実証データは本調査では発見できなかった。** 「ナレッジグラフに効く」は理屈としては妥当だが、効果の定量は不明（未解決事項）。削除されればゼロ。

---

## 5-13. Google Discover最適化

- **一言で**: 検索クエリを経由せずGoogleアプリのフィードに直接配信される面。**日本では珍しく「言及度が高い」数少ないOff-SERP手法**だが、2026年2月のDiscoverコアアップデートで要件が変わった。
- **海外での出典**:
  - [二次] Google's February 2026 Discover Core Update: Complete Publisher Guide https://almcorp.com/blog/google-february-2026-discover-core-update-guide/
  - [二次] The Ultimate Google Discover Optimization Guide (2026) https://www.newsifier.com/blog/news-seo/the-ultimate-google-discover-optimization-guide-12-tips-on-how-to-get-more-traffic-2026
  - [一次寄り] Search Engine Land: How to increase Google Discover traffic with technical fixes https://searchengineland.com/google-discover-technical-fixes-470448
- **仕組み／なぜ効くか**: Discoverはクエリなしのフィード。**2026年2月のコアアップデートで、オリジナルコンテンツの重みが増し、要約のみのコンテンツが降格、E-E-A-Tの比重が上がった**とされる（[二次] ALM Corp）。技術要件は明快で、**1,200px以上の大きな画像＋`max-image-preview:large`メタタグ**が必須。
- **具体手順**:
  1. 全記事に `<meta name="robots" content="max-image-preview:large">` を設定。
  2. アイキャッチを**横1,200px以上**にする（これが未対応だとそもそも候補に入らない）。
  3. **著者名を明示**し、著者プロフィールページを作る（E-E-A-T）。
  4. トピック領域を絞って継続投稿し「エンティティ権威」を作る。
  5. Search Console > 検索パフォーマンス > **Discover レポート**で計測（Discoverタブは掲載が始まると初めて出現する）。
  6. GA4ではDiscover流入が Referral 扱いになりやすいので、`page_referrer` に `googleapis.com` を含むセッションで抽出する（[二次] 日本語記事 https://quickly.co.jp/knowledge_blog/2026/02/2026/02/20/7582/ ）。
- **日本での言及度**: **高**。実検索クエリ `Google Discover 日本語 最適化 流入 攻略` → アウンコンサルティング、ミエルカ、はてなブログ開発ブログ、コナックス等、**質の高い日本語記事が多数。GA4での計測手法まで日本語で解説されている。** → **この手法は「日本語圏でほとんど流通していない」という依頼条件には当てはまらない。ただし婚活領域での実装例は少ない。**
- **日本市場での成立性**: 完全に成立。日本はGoogleアプリ/Chromeの Discover 利用が多く、日本語メディアの主要流入源になっているケースが実際にある。
- **noe-match適用度**: **B**。技術要件は1日で満たせるので**やらない理由がない（コストが極小）**。ただし新規ドメイン・アフィリエイトメディアがDiscoverに載る確率は低く、**期待値ではなく“保険”として実装すべき**。工数: 4時間。
- **リスク・反証**:
  - **ステマ規制**: 記事側でPR表記が担保されていれば問題なし。
  - **反証**: Discoverは**流入がボラティルで、コアアップデートで一夜にしてゼロになる**。ここに依存した収益設計は不可。またアフィリエイト色の強いサイトはDiscoverに載りにくい傾向がある。

---

## 5-14. Google News / Publisher Center

- **一言で**: **2025年4月25日以降、Publisher Centerから自分の媒体を追加できなくなり、Google Newsへの掲載は完全にアルゴリズム判定になった**。「申請して通す」時代は終わっている。
- **海外での出典**:
  - [一次寄り] Search Engine Land: Google Publisher Center to stop allowing you to add publications https://searchengineland.com/google-publisher-center-to-stop-allowing-you-to-add-publications-439978
  - [二次] Google News Publisher Center Setup Guide (2026) https://www.hinditechnews.com/2026/07/google-news-publisher-center-setup-guide.html
  - [二次] RebelMouse: Google News Publisher Center guide https://www.rebelmouse.com/google-news-publisher-center-guide
- **仕組み／なぜ効くか**: Googleがアルゴリズムでニュース媒体性を判定し、**自動で publication ページを作る**。よって2026年のPublisher Centerは「承認申請の窓口」ではなく「管理・確認ツール」。可視性を決めるのは**クロール可能性、編集方針の明示、発行者情報の透明性、技術的健全性、構造化データ、Google Newsポリシー準拠**。
- **具体手順**:
  1. サイトに「編集方針」「運営者情報」「問い合わせ先」「訂正方針」の固定ページを置く（透明性シグナル）。
  2. 記事に `NewsArticle` 構造化データと著者情報を入れる。
  3. ニュースサイトマップを用意する。
  4. Publisher Centerは管理ツールとして接続だけしておく。
  5. **「申請すれば載る」という日本語記事の指示に従わない**（既に廃止済みの手順）。
- **日本での言及度**: **低〜中**。日本語で「Googleニュース 登録方法」は大量に存在するが、**「2025年4月に申請経路が廃止された」という事実を反映していない古い記事が多数残っている**と推定（日本語専用クエリ未実行、未検証）。**ここは"言及が薄い"というより"古い情報が支配している"タイプの空白。**
- **日本市場での成立性**: 成立するが、**婚活・結婚は「ニュース」領域ではない**ため、そもそもGoogle Newsの対象になりにくい。
- **noe-match適用度**: **C**。ニュース性のない評価型コンテンツが中心なので対象外。ただし「編集方針・運営者情報の明示」という副次要件は**E-E-A-T全般とDiscover（5-13）に効くので、そちらの理由で実装する価値はある**。
- **リスク・反証**: リスク低。反証: 婚活メディアがニュース媒体として認定される見込みは薄い。**この項目は「やらない」という判断のために調べる価値がある項目。**

---

## 5-15. Web Stories（生死判定）

- **一言で**: **2026年時点で「生きているが縮小した」。2024年2月にGoogle画像検索での扱いが変更され、以降Googleからの新機能投資はほぼ止まっている。**
- **海外での出典**:
  - [一次] Google Web Story Content Policies（ドキュメントは2026年8月現在も存続） https://developers.google.com/search/docs/appearance/web-stories-content-policy
  - [二次] Google 'Removes' Web Stories From Images https://anotherconcept.co.uk/insights/google-removes-web-stories-from-images
- **仕組み／なぜ効くか**: AMPベースのフルスクリーン・タップ送り形式。かつてはDiscoverとGoogle画像検索に専用枠があった。**2024年2月にGoogle画像検索からWeb Storiesアイコンが消え（Googleは後に「画像検索には出続けるがアイコンなし」と補足）、露出面が縮小した。**
- **具体手順**: （実装を推奨しないため簡略）
  1. WordPressなら Web Stories プラグインで作成。
  2. Discover向けに縦画像で構成。
  3. **投資判断の前に、Search ConsoleのDiscoverレポートで自サイトのDiscover掲載実績を確認する。実績ゼロならWeb Storiesも意味がない。**
- **日本での言及度**: **低**。日本語圏では2021-2022年に一時的に話題になったあと、ほぼ言及が止まっている。
- **日本市場での成立性**: 技術的には成立するが、**投資先として合理性がない**。
- **noe-match適用度**: **C（非推奨）**。
- **リスク・反証**: **本調査ではWeb Storiesの2026年時点の正式なステータス（Googleが公式に非推奨化したか否か）を確定できなかった。** 検索では2026年の廃止アナウンスは見つからず、ポリシードキュメントは存続している。**「生きているが投資に値しない」が本調査の結論。未解決事項に記載。**

---

## 5-16. LinkedIn 記事・ニュースレター

- **一言で**: **LinkedInはAI検索で被引用ドメインの第2位。しかも引用されるのは投稿ではなく「長文記事とニュースレター」で、これが引用の50〜66%を占める。**
- **海外での出典**:
  - [一次寄り] Semrush: We Analyzed 89K LinkedIn URLs Cited in AI Search https://www.semrush.com/blog/linkedin-ai-visibility-study/
  - [一次] LinkedIn公式: How to Leverage LinkedIn for AI Visibility in 2026 https://www.linkedin.com/business/marketing/blog/content-marketing/how-to-leverage-linkedin-for-ai-visibility-in-2026
  - [二次] OtterlyAI: LinkedIn AI Search Citations Study 2026 https://otterly.ai/blog/linkedin-ai-search-citations-study/
  - [二次] ALM Corp: LinkedIn Is the #2 Most Cited Source in AI Search（Semrush 32.5万プロンプト） https://almcorp.com/blog/linkedin-ai-search-citations-2026/
  - [二次] Social Media Today: LinkedIn Articles Are Getting More Citations in AI Responses https://www.socialmediatoday.com/news/linkedin-articles-are-getting-more-citations-in-ai-responses/809563/
- **仕組み／なぜ効くか**: LinkedInはRedditに次ぐ被引用ドメイン2位。**プロフェッショナル系クエリに限れば全プラットフォームで1位**。長文記事・ニュースレター・投稿が引用の**60%**を占め、うち**記事だけで50〜66%**。**800〜1,200語**のレンジが有効とされる（[二次] ALM Corp / Otterly）。LinkedInが公式にAI可視化プレイブックを出している点も重要（[一次]）。
- **具体手順**:
  1. 個人プロフィールを整備（会社ページより個人のほうが引用されやすい）。
  2. **短い投稿ではなくLinkedIn記事（Article）で800〜1,200語**を書く。
  3. LinkedInニュースレター機能を有効化して定期発行。
  4. 見出しを問い形式にし、各セクションを自己完結させる（LLMがチャンク単位で拾えるように）。
  5. 自サイトの記事を丸ごと転載せず、**LinkedIn向けに要点再構成**（重複コンテンツ回避）。
- **日本での言及度**: **ほぼ無（婚活領域では特に）**。日本語圏でLinkedInは「転職・B2B」の文脈でしか語られておらず、**「LinkedInがAI引用の第2位ドメインである」という2026年の事実を扱った日本語記事は流通していない**と推定（未検証）。
- **日本市場での成立性**: **低い。** LinkedInの日本ユーザーは増えているがB2B・転職文脈に偏り、**婚活・結婚という完全にB2Cかつプライベートな領域とはミスマッチ**。日本語で婚活情報をLinkedInで探す人はいない。
- **noe-match適用度**: **C**。ドメインの被引用力は魅力的だが、テーマとの不一致が致命的。**唯一の抜け道は「結婚と仕事の両立」「共働き夫婦の家計」といったキャリア接点テーマ**で、これならLinkedInの文脈に乗る。その範囲でのみ **B**。工数: 記事1本4時間。
- **リスク・反証**: ステマ規制上、記事内でアフィリエイト誘導するならPR表記必須。反証: **「被引用ドメインとして強い」ことと「そのドメイン上の自分のコンテンツが引用される」ことは別問題**。無名アカウントの記事が引用される保証はない。

---

## 5-17. Newsletter / Substack（Owned Audience）

- **一言で**: **プラットフォームのアルゴリズム変更で消えない唯一の資産。SEOへの間接効果（指名検索・直帰率・再訪）と、AI検索でトラフィックが消えても残る収益経路の両方を担う。**
- **海外での出典**:
  - [二次] Sprout Social: Substack SEO — Grow Newsletter Reach in 2026 https://sproutsocial.com/insights/substack-seo/
  - [二次] Substack: Usage, Revenue, Valuation & Growth Statistics https://fueler.io/blog/substack-usage-revenue-valuation-growth-statistics
  - [二次] Newsletter Marketing in 2026: Why Email Lists Are the Most Resilient Brand Asset You Own https://www.imarkinfotech.com/newsletter-marketing-in-2026-why-email-lists-are-the-most-resilient-brand-asset-you-own/
  - [一次] SparkToro: In 2026, Less than One Third of Google Searches Still Send a Click https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/
- **仕組み／なぜ効くか**:
  - Substackは2026年時点で **3,500万人以上のアクティブ読者**、**約10万の有料パブリケーション**（2025年5月の5万から倍増）、**有料購読者100万人超**（[二次] fueler.io）。
  - Substackの平均開封率は **44%**（業界標準の約2倍）、クリック率20%（[二次] fueler / Sprout Social）。
  - **Substackの投稿はGoogleにインデックスされ検索順位が付く**ため、「メール配信」と「パラサイトSEO」を兼ねる（[二次] Sprout Social）。
  - SEOへの間接効果: 指名検索の増加、リピート訪問、直接流入の増加。**AI検索でクリックが減っても、メールは配信到達がアルゴリズムに依存しない。**
- **具体手順**:
  1. 自サイト内にメール登録フォームを設置（記事末＋サイドバー＋離脱時）。
  2. 登録動機を作る（例:「婚活の費用シミュレーションシート」「両家顔合わせ進行台本テンプレ」）。
  3. **配信基盤を選ぶ。Substack（英語圏デフォルト）／日本語圏なら theLetter, Steady, Beehiiv, もしくはメール配信＋LINE併用。**
  4. 記事の要約＋その週の考察を週1配信。
  5. 配信本文をSubstack/noteに公開版として置き、検索面も取る。
- **日本での言及度**: **低**。「メルマガ」は日本でも古くから語られているが、**「owned audience論」「zero-click時代の耐障害資産としてのニュースレター」という2026年の文脈での日本語記事は薄い**と推定（未検証）。SubstackそのものはB2Bマーケ界隈でしか話題になっていない。
- **日本市場での成立性**: **成立するが形が違う。日本ではSubstackよりLINEが強い（5-18参照）。** ニュースレター文化は日本では英語圏ほど根付いていない。
- **noe-match適用度**: **B**。婚活〜結婚〜新生活は**顧客の関心が2〜3年にわたって連続的に移動する**という珍しい特性を持つ（婚活→結婚式→新居→保険）。**リスト保持のLTV効果が非常に高い商材構造**。工数: 初期構築8時間＋週1配信1時間。
- **リスク・反証**:
  - **ステマ規制**: **メール本文にアフィリエイトリンクを含める場合もPR表記が必要**（媒体を問わず「事業者の表示」に該当）。ここは見落とされやすい。
  - **反証**: 「ニュースレターROI 30〜40倍」という数字（[二次] imarkinfotech）は**出典が弱く、D2C文脈の一般論であり婚活アフィリエイトに適用できる根拠がない。この数字は使わないほうがよい。**
  - 個人運営で週次配信を続けられるかが最大の実行リスク。

---

## 5-18. LINE公式アカウント（日本版 Owned Audience）

- **一言で**: **英語圏の"newsletter/owned audience"論の日本における正しい翻訳先。ただし2026年の実態調査では「ブロック率が高く、クーポン目的の登録が支配的」というシビアな数字が出ている。**
- **海外での出典（概念側）**:
  - [一次] SparkToro: Zero-Click Content https://sparktoro.com/blog/zero-click-content-the-counterintuitive-way-to-succeed-in-a-platform-native-world/
  - [二次] Newsletter Marketing in 2026 https://www.imarkinfotech.com/newsletter-marketing-in-2026-why-email-lists-are-the-most-resilient-brand-asset-you-own/
- **日本側の出典**:
  - [一次] LINE公式アカウント利用実態調査2026（TimeTechnologies、1,000名調査） https://prtimes.jp/main/html/rd/p/000000016.000041525.html
  - [二次] LINE公式アカウントの利用実態調査2026 https://linestep.jp/2026/03/31/line-official-account-survey-2026
  - [一次] LINEヤフー for Business 友だち分析マニュアル https://www.lycbiz.com/jp/manual/OfficialAccountManager/insight_friends/
- **仕組み／なぜ効くか**: 到達率がメールより高く、日本の生活者の日常導線上にある。**ただし1,000人調査の実データはかなり厳しい**:
  - **23.3%が「LINE公式アカウントを1つも登録していない」**
  - 最多回答は「1〜2アカウント」で **21.7%**
  - 友だち追加の最大理由は「クーポン・キャンペーン情報」で **56.3%**
  - **約70%がブロック経験あり**。理由は「不要な情報が多い」「配信頻度が高い」
  （すべて [一次] TimeTechnologies 1,000名調査）
- **具体手順**:
  1. **登録特典を「クーポン」ではなく「情報資産」にする**（婚活費用シミュレータ、式場見学チェックリスト）。クーポン目的の登録者は離脱前提。
  2. **配信頻度を週1以下に固定**（ブロック理由の1位が頻度）。
  3. リッチメニューを「よくある質問→記事」の目次にする（Off-SERPの導線を私有地内に作る）。
  4. セグメント配信（婚活中／結婚準備中／新婚）で関心フェーズに合わせる。
  5. LINEからの自サイト流入をUTMで計測。
- **日本での言及度**: **高**。実検索クエリ `LINE公式アカウント 友だち数 2026 統計 月間利用者 メルマガ 開封率 日本` → 調査リリース、運用ガイド、LINEヤフー公式マニュアルまで揃っている。**日本語圏で最も情報が充実しているOff-SERP手法。** → 依頼条件の「日本で語られていない」には該当しない。**しかし「英語圏のowned audience論と接続して語られること」はほぼない。**
- **日本市場での成立性**: 完全に成立。
- **noe-match適用度**: **B**。婚活領域は「相談したい」需要が強くLINEと相性が良い。ただし**アフィリエイトメディアがLINEで何を配信するかの設計が難しい**（商材を売る場ではなく、信頼を作る場として使う必要がある）。工数: 初期設計8時間＋週1配信1時間。
- **リスク・反証**:
  - **ステマ規制**: **LINE配信内にアフィリエイトリンクを含める場合もPR表記が必要。** 「1:1のメッセージだから広告ではない」は通らない。
  - **反証**: ブロック率70%という数字は、**個人メディアのLINEアカウントが「登録されたが読まれない」状態になる確率が高いことを示す**。Xのフォロワー（既存2アカウント）からの流入がなければリスト構築自体が始まらない。

---

## 5-19. ポッドキャストへのゲスト出演（Guest Podcasting）

- **一言で**: **1回の出演で「ショーノートからの被リンク」「トランスクリプトへのブランド名記載」「音声プラットフォーム内検索での露出」が同時に手に入る。英語圏では2026年の最有力オフページ手法のひとつとして扱われている。**
- **海外での出典**:
  - [二次] Bill Hartzer: Why Guest Podcasting May Be the Strongest SEO Signal for Service Businesses in 2026 https://www.billhartzer.com/seo/guest-podcasting-strongest-seo-signal/
  - [二次] Podcast Guest SEO: How One Podcast Interview Can Rank You on Google for Years https://icpcast.com/blog/podcast-guest-seo-guide
  - [二次] Podcast Link Building Guide: Earn Backlinks from Show Notes https://linkindex.us/methods/podcast-link-building/
  - [二次] Podcast Backlinks: The Ultimate SEO Strategy for 2026 https://www.expertbookers.com/podcast-marketing-authority-blog/podcast-backlinks-seo-strategy
- **仕組み／なぜ効くか**: (a) ショーノートは通常dofollowの編集リンクで、**購入リンクではないためリンクスパムに当たらない**。(b) 番組が公開するトランスクリプトに氏名・ブランド名・専門語彙がクロール可能なテキストとして残る。(c) 同じ番組に繰り返し出演すると「同一ドメインからの継続的な言及」となり、単発より強い推薦シグナルとして扱われる（[二次] linkindex）。(d) Spotify/Appleの内部検索でもトランスクリプトが検索対象になる。
- **具体手順**:
  1. 対象番組リストを作る（婚活・恋愛・ライフプラン・お金・地方移住など隣接領域を広く取る）。
  2. **「番組のリスナーに何を提供できるか」を1段落で書いたピッチ**を送る（自己紹介ではなく企画提案）。
  3. 出演時に「詳しくはこのページで」と**具体的なURL付きリソースを1つ**用意しておく（ショーノートに載せてもらう根拠になる）。
  4. 出演後、自サイトに「出演一覧」ページを作り、逆に番組へリンクを返す（関係の継続化）。
  5. 同じ番組への再出演を狙う。
- **日本での言及度**: **低**。実検索クエリ `ポッドキャスト SEO 日本語 文字起こし 被リンク ゲスト出演` → 出てきたのは**「自分の番組を伸ばすためのポッドキャストSEO」記事**（ https://podcastar.jp/archives/1008 、 https://otonal.co.jp/audio-marketing-insights/43600 ）が中心で、**「他人の番組にゲスト出演することが自サイトのSEO施策になる」という英語圏の中核論点を扱った日本語記事は上位に見当たらなかった。** 論点がずれている典型例。
- **日本市場での成立性**: **成立するが番組供給が薄い。** 日本のポッドキャスト市場は英語圏より小さく、婚活・結婚領域の番組数は限られる。**代替として「YouTubeチャンネルへのゲスト出演」「Xスペースへのゲスト参加」のほうが日本では現実的**。
- **noe-match適用度**: **B**。無料・被リンク獲得・E-E-A-T構築を同時に満たす数少ない手法。工数: ピッチ作成4時間＋1出演あたり3時間。**ただし出演が決まるかは相手次第で、コントロール不能。**
- **リスク・反証**:
  - **ステマ規制**: **出演料や掲載料を払った場合は「事業者の表示」となりPR表記が必要**。無償出演なら規制対象外。**「ゲスト出演枠を買う」サービスは日本では要注意。**
  - **Google側リスク**: 有償のポッドキャスト出演＋リンクは**リンクスパムポリシーに抵触**する可能性がある。無償の編集判断による出演のみが安全。
  - **反証**: 個人運営で実績のないメディア運営者にゲスト依頼が来る/受け入れられる確率は低い。**5-25（書籍）や5-27（メディア掲載実績）が先に必要。**

---

## 5-20. 自主ポッドキャスト＋トランスクリプト公開

- **一言で**: 自分で番組を持ち、**全エピソードのトランスクリプトを自サイトに公開**して、音声を検索可能なテキスト資産に変換する。
- **海外での出典**:
  - [二次] SEO for Podcasts: 2026 Ultimate Guide https://www.thespearpoint.com/blog/seo-for-podcasts
  - [二次] Podcast SEO in 2026: The New Rules for Discoverability https://whatsgood-productions.com/blog/podcast-seo-in-2026
  - [二次] Understanding Podcast SEO in 2026 https://www.cueproductions.com/post/understanding-podcast-seo
- **仕組み／なぜ効くか**: 「2026年にトランスクリプトは任意ではなく必須。検索エンジンは音声を聴けないから」が英語圏のコンセンサス（[二次] whatsgood）。Spotifyは文字起こしが検索結果にヒットする仕組みを持つ（[二次] 日本語記事 https://otonal.co.jp/audio-marketing-insights/43600 ）。**副次効果として、1回の収録が (a) 音声、(b) 自サイトの長文記事、(c) YouTube動画、(d) ショート切り抜き、(e) ニュースレター本文の5素材になる。**
- **具体手順**:
  1. 週1回30分の収録（対談形式が望ましい）。
  2. AI文字起こし→人力で修正。
  3. **自サイトにエピソードページを作り、全文トランスクリプト＋要約＋関連記事リンクを掲載。**
  4. Spotify/Apple/YouTubeに同時配信し、各説明欄に自サイトのエピソードURLを置く。
  5. トランスクリプトを再編集して記事化（1収録＝1記事）。
- **日本での言及度**: **中**。日本語でも「ポッドキャストの文字起こし」記事は存在する（ https://podsqueeze.com/blog/ja/everything-you-need-to-know-about-podcast-transcription/ ）。**ただし「トランスクリプトを自サイトに置いてSEO資産にする」という接続は薄い。**
- **日本市場での成立性**: 成立する。ただし日本のポッドキャスト聴取人口は限定的なので、**「聴取者獲得」ではなく「テキスト資産の生産手段」として位置づけるべき**。
- **noe-match適用度**: **B**。**「記事を書くのが遅い個人運営者にとって、話す→文字起こし→記事化のパイプラインは執筆速度を上げる」**という制作効率の観点で価値がある。工数: 1エピソードあたり収録0.5h＋編集1h＋記事化1.5h＝3時間。
- **リスク・反証**: ステマ規制上、アフィリエイト言及時はPR表記必須（音声内でも口頭で明示すべき）。反証: **AI生成的なトランスクリプト記事はscaled content abuse判定のリスクがある。「話した内容を整えただけ」なら問題ないが、量産目的で使うと危険。**

---

## 5-21. リスティクル掲載（Listicle Placement）

- **一言で**: **「〇〇おすすめ10選」型の第三者記事に自分を載せてもらう。2026年に「最も強力なAI引用獲得手法」と呼ばれるようになった。ただし有償枠は日本ではステマ規制に直撃する。**
- **海外での出典**:
  - [二次] Listicle Placements: The New Most Powerful AI Citation Tactic in 2026 https://linkbuildingjournal.co.uk/listicle-placements-ai-citation-tactic/
  - [二次] How to Rank in AI Search: The Listicle Strategy (2026) https://tjrobertson.com/how-to-rank-in-ai-search-listicle-strategy/
  - [二次] Exploding Topics: How to Rank on AI Search Engines in 2026 https://explodingtopics.com/blog/ai-search-optimization-guide
  - [二次] Yotpo: LLM Optimization — 12 Tips https://www.yotpo.com/blog/llm-optimization-guide/
- **仕組み／なぜ効くか**: リスティクルは**LLMが最も解析しやすい構造**（各項目が「名称＋説明＋価格/機能」で一貫している）。また「〇〇のおすすめは？」というプロンプトに対する retrieval の第一候補になる。**ニッチなリスティクルほど引用枠の競争が少なく、プロンプト意図との一致度が高い**（[二次] gen-optima）。
- **具体手順（合法ルートのみ）**:
  1. 「婚活アプリ おすすめ」「結婚相談所 比較」等で上位のリスティクル記事を50本リスト化。
  2. **各記事の運営者に、掲載依頼ではなく「情報提供」を送る**（自社の独自データ、独自の切り口）。
  3. 自分でも**ニッチなリスティクルを作る**（「30代後半・地方在住向けの婚活サービス7選」など、競合が作っていない粒度）。これは自サイト側の施策だが、AI引用の獲得目的では最も再現性が高い。
  4. 各項目を「名称／料金／対象／特徴」の一貫した構造で書き、表形式にする。
  5. 3〜6か月ごとに更新日を明示して更新する（フレッシュネス）。
- **日本での言及度**: **未検証**（該当日本語クエリが検索回数上限により未実行）。ただし**「有償リスティクル掲載」の是非をステマ規制と接続して論じた日本語記事は、一般的な流通状況から見て薄いと推定される。**
- **日本市場での成立性**: 成立する。日本の婚活領域は比較記事が飽和しており、掲載先は豊富。
- **noe-match適用度**: **B**（自作ニッチリスティクル）／**C**（第三者への掲載交渉：個人メディアが載せてもらう理由が弱い）。工数: 自作なら1本8時間。
- **リスク・反証**:
  - **ステマ規制**: **英語圏の記事が推奨する「$100〜200の有償掲載」（[二次] tjrobertson）は、日本では極めて危険。** 対価を払って第三者に自社を推奨させ、PR表記がなければ**明確にステマ規制違反**。**日本では不可。**
  - **なぜ海外では成立するか**: 米国のFTCガイドも material connection の開示を求めるため厳密には同じ問題を抱えているが、(a) 執行が個別・事後的、(b) 「sponsored」表記付きの有償掲載が業界慣行として存在、(c) B2B SaaS領域では「ディレクトリ掲載料」という商慣行が確立している、という3点で運用上グレーが許容されている。**日本の告示は「判別困難な表示」を包括的に不当表示と指定しているため、同じことをすると直撃する。**
  - **Google側リスク**: 対価を伴うリンク付き掲載は**リンクスパムポリシー違反**。
  - **反証**: 「有償枠を買えばAIに引用される」という主張は、**そのリスティクル記事自体が引用されるほどの権威を持っている場合にのみ成立する**。無名の掲載サイトを買っても意味がない。

---

## 5-22. 比較サイト・アグリゲータ／ディレクトリ掲載（Product Hunt / G2 型）

- **一言で**: **AIアシスタントが「おすすめは？」に答えるとき、Product Hunt・G2・Crunchbase等のアグリゲータをクロスリファレンスしている。未掲載のプロダクトはAIから見て存在しないに等しい。**
- **海外での出典**:
  - [一次] Product Hunt公式フォーラム: Case Study — how Product Hunt can improve AI visibility in 2026 https://www.producthunt.com/p/producthunt/case-study-how-product-hunt-can-improve-ai-visibility-in-2026
  - [二次] 100+ Free Startup Directories to Submit Your Product To in 2026（Product Hunt DR 91、G2/Crunchbase DR 80-92） https://tools.launchllama.co/blog/100-free-startup-directories-to-submit-your-product-to-in-2026
  - [二次] Best AI Search Visibility Tools for Businesses in 2026 https://trustmary.com/ai-visibility/best-ai-search-visibility-tools/
- **仕組み／なぜ効くか**: ChatGPT/Claude/Perplexityがツール推薦クエリに答える際、これらのハブを参照して検証する。**未掲載＝AI推薦の候補集合に入らない**（[二次] launchllama）。加えてDR 80〜92の被リンクが新規ドメインに入る。
- **具体手順**:
  1. 自分のカテゴリで**AIが実際に参照しているハブを特定する**（ChatGPTに「日本の婚活サービスのおすすめは？」と聞き、引用元URLを列挙させる）。
  2. そのハブに掲載可能かを確認（無料掲載枠があるか）。
  3. 掲載時のプロダクト説明は**LLMが解析しやすい構造**（名称・カテゴリ・対象・価格・特徴）で書く。
  4. カテゴリ名・命名が可視性に影響する（[二次] launchllama「naming alone can materially change visibility」）ため、名称は検索されうる語を含める。
  5. 四半期ごとに掲載情報を更新。
- **日本での言及度**: **未検証**（該当クエリが上限により未実行）。ただし**Product Hunt/G2は日本語圏ではスタートアップ界隈でのみ言及され、「AI引用のために掲載する」という文脈での日本語記事はほぼ無いと推定。**
- **日本市場での成立性**: **Product Hunt/G2はB2B SaaS向けであり、婚活メディアには直接使えない。日本での相当物は「価格.com」「みん評」「みんなのウェディング」「ゼクシィ」といった比較・口コミプラットフォーム。ただしこれらは“サービス提供者”が掲載される場であり、“メディア”は掲載対象外**という構造的な壁がある。※日本の該当プラットフォームの掲載可否は本調査では未確認（未解決事項）。
- **noe-match適用度**: **C**。noe-matchは「メディア」であって「サービス」ではないため、掲載枠がない。**唯一の適用先は「メディア/ブログのディレクトリ」だが、これらは2026年時点でSEO的価値が低い。**
- **リスク・反証**: 有償掲載＋PR表記なしは**不可（ステマ規制）**。無料掲載は問題なし。反証: **アフィリエイトメディアが掲載されるアグリゲータは実質存在しない。この手法は「noe-matchが将来サービス（有料の婚活相談等）を持ったとき」に初めて意味を持つ。**

---

## 5-23. 高DRプラットフォームへのドキュメント配置（SlideShare / Issuu / Scribd / Notion / GitHub）

- **一言で**: 高ドメイン権威のドキュメント共有サイトに資料を置いて、被リンク・リファラル・エンティティ露出を取る。**2010年代の定番手法で、2026年時点では効果が大幅に減衰しているが、Notion公開ページだけは例外的に生きている。**
- **海外での出典**:
  - [二次] 100 Document Sharing Sites List 2026 https://www.w3era.com/blog/seo/document-sharing-sites-list/
  - [二次] Notion, GitBook and Public Docs as Surprising Link Sources https://linkbuildingjournal.co.uk/notion-public-page-links/
  - [二次] Top Free PDF Submission Sites for SEO in 2026 https://techeasify.com/pdf-submission-sites/
- **仕組み／なぜ効くか**: SlideShare（2020年からScribd傘下、7,000万人超のリーチ）、Issuu、Calaméo、Speaker Deck、Academia.edu 等が高DRを保持している（[二次] w3era）。**Notionの公開ページは、公開後に「検索エンジンによるインデックス登録→ウェブ上で検出可能」を明示的にONにしないとインデックスされない**。SEOタイトル・説明のカスタマイズとカスタムドメイン接続は有料プラン限定（[二次] linkbuildingjournal）。
- **具体手順**:
  1. **1つの「本気の資料」を作る**（例:「結婚までの費用カレンダー完全版（PDF 20ページ）」）。量産はしない。
  2. Notion公開ページとして公開し、**インデックス設定をONにする**。
  3. 同じ資料をSpeaker Deck/Issuuにも置く。
  4. 各所から自サイトの詳細ページへリンク。
  5. **効果測定は被リンクではなくリファラル流入で行う**（これらのリンクはnofollowまたは価値が低い）。
- **日本での言及度**: **低（かつ古い情報が支配）**。日本語圏では「PDF投稿サイト一覧」的な2015年前後のSEO記事が残っているが、**2026年時点の有効性を検証した日本語記事は見当たらない**と推定（未検証）。
- **日本市場での成立性**: プラットフォームは日本からも使えるが、**日本語ユーザーのSlideShare/Issuu利用は極めて少ない**。Notionは日本でも普及している。
- **noe-match適用度**: **C**（SlideShare/Issuu/Scribd）／**B**（Notion公開ページ1本のみ）。工数: Notion公開ページ1本で4時間。
- **リスク・反証**:
  - **ステマ規制**: 資料内でアフィリエイト誘導するならPR表記必須。
  - **Google側リスク**: **「PDF投稿サイトに大量投稿」は典型的な旧式リンクスパムで、2026年時点では無価値かマイナス。** 上記の英語記事群は品質が低く、この手法を推す根拠は弱い。
  - **反証**: **本項目は「英語圏で語られているが実際にはもう効かない手法」の代表例。羅列としては記載するが、noe-matchが投資すべきではない。**

---

## 5-24. Amazon Kindle（KDP）出版による著者性シグナル

- **一言で**: **書籍を出すことで「著者」という第三者検証可能なエンティティを作り、E-E-A-T・Wikidata・ゲスト出演・メディア掲載の全ての前提条件を一気に満たす。英語圏の実務では「authority stacking」の起点として扱われる。**
- **海外での出典**:
  - [二次] Amazon Kindle SEO: A Complete Guide for KDP Book Publishers https://www.zonguru.com/blog/amazon-kindle-seo-guide
  - [二次] SEO for Amazon KDP: A Comprehensive Guide https://revenusmedia.com/seo-for-amazon-kdp/
  - [一次] Kindle Direct Publishing（Wikipedia、制度概要） https://en.wikipedia.org/wiki/Kindle_Direct_Publishing
  - [二次] Advanced SEO for Amazon KDP https://www.udemy.com/course/advanced-seo-for-amazon-kdp/
- **仕組み／なぜ効くか**:
  - **注意: 本調査で見つかった英語ソースはいずれも「Amazon内での本の売り方（Amazon SEO）」を扱っており、「著者性シグナルとしてのKDP」を実証的に論じたものは見つからなかった。** 検索結果にも「E-E-A-TやGoogleナレッジパネルの話は結果に含まれていない」と明記された。**したがって以下は理屈ベースの整理であり、実証データはない。**
  - 理屈: (a) Amazonの著者ページとASINは外部から参照可能な識別子になり、Wikidata（5-12）のnotability要件を助ける。(b) 「著書がある」ことでポッドキャスト出演（5-19）・メディア取材（5-27）のピッチ通過率が上がる。(c) Google/LLMが「著者」エンティティを認識する材料になる。
  - Amazon内のランキング要因は relevance（タイトル・サブタイトル・説明・7つのキーワード・2カテゴリ）と performance（売上・レビュー・CTR）。
- **具体手順**:
  1. 自サイトの主要記事を再編集して**1冊分（3〜5万字）**にまとめる。
  2. タイトル・サブタイトルに検索語を入れる。キーワード7枠・カテゴリ2枠を設定。
  3. **著者名を、自サイトの運営者名・SNS・記事の署名と完全に一致させる**（エンティティの同一性が全て）。
  4. Amazon著者セントラルで著者ページを作り、自サイトURLを記載。
  5. 自サイトの著者プロフィールページから書籍へリンクし、`sameAs` で相互参照。
- **日本での言及度**: **低**。日本語圏でKDPは「副業・印税」の文脈でしか語られておらず、**「SEO/E-E-A-Tのための著者性構築手段」としてのKDPを論じた日本語記事はほぼ無いと推定**（未検証）。
- **日本市場での成立性**: 成立する。KDPは日本でも普通に使え、日本語書籍を出せる。
- **noe-match適用度**: **B**。既存記事の再編集なので追加取材が不要。**個人運営メディアが「著者性」を得るための、日本において最も現実的で安価な手段。** 工数: 既存記事の再編集で20〜30時間（一度きり）。
- **リスク・反証**:
  - **ステマ規制**: 書籍内でアフィリエイトリンクを使う場合は表記が必要。書籍を「実績」として自サイトに掲載するのは問題なし。
  - **反証（重要）**: **「Kindle出版がE-E-A-Tに効く」という実証データは本調査では発見できなかった。** 低品質なKDP本が氾濫しているため、Googleが「著書がある」を権威シグナルとして扱っている保証はない。**期待できるのは間接効果（ピッチ通過率、信頼の可視化）のみと考えるべき。** 未解決事項に記載。

---

## 5-25. HARO型ソースプラットフォームでの専門家コメント提供（Digital PR）

- **一言で**: **記者・ライターの取材募集に専門家として無償で回答し、編集リンク付きでメディアに引用される。「対価なし」なので日本のステマ規制を構造的に回避できる、数少ない被リンク獲得手法。**
- **海外での出典**:
  - [二次] 12+ Connectively (HARO) Alternatives for 2026 https://www.prezly.com/academy/the-best-haro-alternatives
  - [二次] 10 HARO Alternatives for 2026: Qwoted, Featured, Source of Sources https://everything-pr.com/haro-earned-media-placements
  - [二次] HARO Alternatives for Link Building in 2026 https://eseospace.com/blog/haro-alternatives-for-link-building-in-2026-7-platforms-to-earn-editorial-links/
- **仕組み／なぜ効くか**: 記者側が「〇〇の専門家のコメントが欲しい」と募集を出し、応募者の中から採用する。**採用されると記事内で氏名・所属・URLが紹介される＝完全な編集リンク**。
  - HARO（Connectively）は **2024年12月9日に一度停止**、**2025年4月に旧ブランドで再開**したが、AI生成回答の氾濫と品質管理の欠如で評価が落ちている（[二次] prezly）。
  - 2026年の実質的な主戦場は **Qwoted**（HARO上級者の移住先）、**Featured.com**（回答から24〜48時間で掲載が決まる最速）、**Source of Sources**（HARO創業者Peter Shankmanが2024年に立ち上げた無料メール版）、**Help a B2B Writer**。
- **具体手順**:
  1. Qwoted / Featured / Source of Sources に登録（無料枠あり）。
  2. プロフィールに専門領域を明記（「婚活・結婚準備の費用設計」等）。
  3. **回答は「使える引用文」の形で書く**（記者がそのまま貼れる2〜3文）。AIで書いた汎用文は落ちる。
  4. 1日1〜2件、関連する募集にだけ応答する。
  5. 掲載されたら自サイトに「メディア掲載」ページを作って集約（これが5-11 Wikipedia、5-19 ポッドキャストの前提条件になる）。
- **日本での言及度**: **ほぼ無**。**日本語圏には「HARO」に相当する概念自体がほとんど紹介されていない。** これは本調査で最も日本語言及が薄い手法のひとつ。
- **日本市場での成立性**: **低い（ここが本手法の最大の弱点）。日本語圏にHARO相当のプラットフォームが存在しない。** 日本での近似手段は:
  - **PR TIMESの「取材リクエスト」機能**
  - **ExpertsのようなB2Bマッチング**
  - **記者へのSNS（X）経由の直接アプローチ**（日本の記者はXで取材募集をすることがある）
  - **専門家紹介サービスへの登録**
  ※これら日本側の代替手段の実効性は本調査では未検証（未解決事項）。
- **noe-match適用度**: **C**（英語圏プラットフォーム）／**B**（日本での代替: Xで「#取材募集」等を監視し、婚活・結婚関連の取材募集に応答する運用）。工数: 監視と応答で週1〜2時間。
- **リスク・反証**:
  - **ステマ規制**: **無償の専門家コメント提供は「事業者が第三者をして行わせる表示」に当たらないため、規制対象外。** これが本手法の最大の価値。
  - **Google側リスク**: なし（編集判断による自然リンク）。
  - **反証**: 個人運営のアフィリエイトメディア運営者が「専門家」として採用される確率は低い。**5-24（著書）が先にあると通過率が変わる。** また英語圏でもAI生成回答の氾濫で採用率が落ちている。

---

## 5-26. コミュニティ主導成長（Community-Led Growth：Discord / Slack / 私有地化）

- **一言で**: **検索エンジンにもAIにも見えない「ダークソーシャル」に自分の場を持ち、そこで指名検索と口コミを発生させる。B2Bの推薦の80%以上が私的チャネルで起きているとされる。**
- **海外での出典**:
  - [二次] Community-Led Growth: Slack & Discord vs Cold Outreach https://www.revsure.ai/blog/community-led-growth-why-private-slack-discord-groups-outperform-cold-outreach
  - [二次] 15 Growth Hacking Trends in 2026 https://venture-lab.org/2026/growth-hacking-trends-2026/
  - [二次] Community-led growth engagement and retention statistics (2026) https://blog.mean.ceo/community-led-growth-engagement-retention-statistics/
- **仕組み／なぜ効くか**: 2026年の成長トレンド上位3つが「community-led growth」「dark social influence（B2B推薦の80%以上が私的チャネルで発生）」「AIパーソナライゼーション」とされる。**コンテンツ共有の最大84%が私的チャネル経由**という推計もある（[二次] venture-lab）。構造化されたオンボーディングパスで**初回貢献までの時間が28日→9日、リテンションが2倍**という事例（[二次] blog.mean.ceo）。
- **具体手順**:
  1. Discordサーバー（または LINEオープンチャット）を作る。婚活は**匿名性が必要**なので、実名前提のプラットフォームは避ける。
  2. **チャンネル設計を「フェーズ別」にする**（婚活中／交際中／結婚準備／新生活）。noe-matchのコンテンツ構造と一致させる。
  3. **最初の30日の導線を設計**（自己紹介→質問→回答の型を用意し、初回貢献を早める）。
  4. コミュニティ内での質問を、そのまま自サイトの記事ネタにする（一次情報の生産装置になる）。
  5. **コミュニティ内でアフィリエイトを売らない**。売った瞬間に場が死ぬ。
- **日本での言及度**: **低**。日本語では「オンラインサロン」「コミュニティ運営」の文脈で語られるが、**「SEO/AI可視性の基盤としてのコミュニティ」という接続はほぼ無い**と推定（未検証）。
- **日本市場での成立性**: **成立する。日本ではDiscordよりLINEオープンチャットのほうが婚活層にリーチしやすい**（匿名参加可能、参加障壁が低い）。
- **noe-match適用度**: **B**。**婚活は「他人に相談しにくい」領域なので、匿名コミュニティの需要が構造的に大きい。しかし運営負荷が非常に高く、個人運営では炎上・トラブル対応のリスクが大きい。** 工数: 立ち上げ20時間＋週5時間以上の継続運営。
- **リスク・反証**:
  - **ステマ規制**: **コミュニティ内で運営者がアフィリエイト商材を推奨する場合、PR表記が必要。** 「コミュニティだから広告ではない」は通らない。
  - **反証**: **効果がSEOに直接可視化されない**（ダークソーシャルなので計測できない）。指名検索数の変化でしか測れず、個人運営では投資判断が難しい。運営負荷に対してリターンが読めない。

---

## 5-27. Zero-Click Content / Search Everywhere Optimization（メタ手法）

- **一言で**: **「クリックさせるための予告編」ではなく「その場で完結する価値」をプラットフォーム上に置く。2026年のGoogle検索の3分の2以上がクリックを発生させない以上、これは選択ではなく前提条件になった。**
- **海外での出典**:
  - [一次] SparkToro: In 2026, Less than One Third of Google Searches Still Send a Click https://sparktoro.com/blog/in-2026-less-than-one-third-of-google-searches-still-send-a-click/
  - [一次] SparkToro: Zero-Click Content（Amanda Natividadが2022年に提唱） https://sparktoro.com/blog/zero-click-content-the-counterintuitive-way-to-succeed-in-a-platform-native-world/
  - [一次] SparkToro: New Research — Search Happens Everywhere（41サイトの検索行動分析） https://sparktoro.com/blog/new-research-search-happens-everywhere-an-analysis-of-41-websites-with-significant-search-activity/
  - [一次] SparkToro: If Search Captures Demand, Public Evidence Creates It https://sparktoro.com/blog/if-search-captures-demand-public-evidence-creates-it/
  - [二次] Similarweb: Zero-Click Marketing — What the 2026 Data Means https://similarweb.com/blog/marketing/geo/zero-click-marketing
- **仕組み／なぜ効くか**: SEOを "Search Engine Optimization" ではなく **"Search Everywhere Optimization"** と再定義し、**オーディエンスが注意を払っている全ての場所に出る**という考え方（[一次] SparkToro）。「zero-click content」はプラットフォーム上で完結する自己充足的なコンテンツを指し、クリックがなくても教育・情報提供・インスピレーションを与える。**SparkToroの主張は「クリックではなく影響力とブランド認知を得よ」。**
- **具体手順**:
  1. **各記事の"最も価値ある1点"を、リンクなしでプラットフォーム上に完結させて投稿する**（Xの1投稿、Pinterestの1枚、YouTubeの1本）。
  2. **リンクを本文に入れず、プロフィール/固定投稿に置く**（アルゴリズムのリンクペナルティ回避）。
  3. 効果測定を「クリック数」から**「指名検索数（Search Consoleのブランドクエリ）」「AI回答での言及率」**に変える。
  4. 同じ内容を各プラットフォームのネイティブ形式に作り変える（転載ではなく再構成）。
  5. 四半期ごとに「どのプラットフォームで指名検索が増えたか」で配分を変える。
- **日本での言及度**: **ほぼ無**。「ゼロクリック検索」という単語は日本語でも紹介されているが、**「zero-click content（クリックさせない設計を意図的に採る）」という能動的戦略としての日本語記事はほぼ存在しない**と推定（未検証）。日本語圏の議論は「ゼロクリック＝流入減という脅威」で止まっており、**「ならばクリックを前提にしない設計にする」という次の一手に進んでいない。**
- **日本市場での成立性**: 完全に成立する（考え方なのでプラットフォーム非依存）。
- **noe-match適用度**: **A**。**個人運営・新規ドメインにとって、これは戦略の前提そのもの。** 追加工数ゼロ（既存の投稿の書き方を変えるだけ）。
- **リスク・反証**:
  - **ステマ規制**: プラットフォーム上の投稿が自社サービスやアフィリエイト商材の推奨を含むなら、その投稿自体にPR表記が必要。**「リンクを貼っていないから広告ではない」は通らない**点に注意。
  - **反証（最重要）**: **アフィリエイトメディアはクリックがなければ1円も入らない。** zero-click contentは「認知→後で指名検索→サイト訪問→収益化」という長い経路を前提にしており、**noe-matchのような収益化を急ぐ個人メディアとは時間軸が合わない可能性がある。** SparkToroはSaaS企業の視点で書いている点を割り引くべき。

---

## 5-28. llms.txt（反証項目：やらなくていいことの明確化）

- **一言で**: **「AI向けのrobots.txt」として2025年に流行した規格。2026年の実測では、Googleは明確に無視、AIクローラーもほぼ読んでいない。やらなくていい。**
- **海外での出典**:
  - [二次] llms.txt: What the 2026 Data Actually Shows https://geojacker.com/llms-txt
  - [二次] llms.txt Got a Major Update. Google Says Skip It Anyway https://www.refontelearning.com/blog/implementing-llms-txt
  - [二次] llms.txt in 2026: Adoption Data and When to Use It https://organikpi.com/blog/distribution/llms-txt-adoption-impact/
  - [二次] Wix: Debunking LLMs.txt Myths https://www.wix.com/studio/ai-search-lab/llms-txt-myths
- **仕組み／なぜ効くか（効かない根拠）**:
  - **2025年7月、GoogleのGary Illyesが「Googleはllms.txtをサポートしないし、する予定もない」と明言**。John Muellerは「keywordsメタタグと同じ」と評した（[二次] refontelearning）。GoogleはAI OverviewsとAI Modeを含め、検索においてこのファイルを無視する。
  - SE Rankingの**30万ドメイン調査で採用率10.13%**。しかし**AI被引用トップ50ドメインのうち llms.txt を持っていたのは1つだけ**（[二次] geojacker）。
  - **90日間で5億回超のAIボットアクセスを観測し、llms.txtを直接叩いたのはわずか408回**。GPTBot / ClaudeBot / PerplexityBot / OAI-SearchBot / Google-Extended はいずれもこのファイルを飛ばしてHTMLを直接クロールしている（[二次] geojacker）。
  - **2026年Q1時点で、OpenAI・Google・Anthropic・Meta・Mistralのいずれも、本番システムでllms.txtを読むと公表していない**（[二次] geojacker）。
- **具体手順**: **実装しない。** 代わりに (a) HTMLのセマンティック構造を正しくする、(b) 見出しを問い形式にする、(c) 各セクションを自己完結させる、に工数を回す。
- **日本での言及度**: **中〜高（しかも誤った方向で）**。日本語圏では2025年に「llms.txtを設置しよう」という記事が大量に出た。**「効かない」という2026年の実測を反映した日本語記事は少ないと推定**（未検証）。**これは"言及が薄い"のではなく"間違った言及が多い"タイプの空白。**
- **日本市場での成立性**: —（実装不要）
- **noe-match適用度**: **C（実装しない）**。工数ゼロで済むのが最大の価値。
- **リスク・反証**: リスクは「効くと思って工数を使うこと」のみ。**反証としては、llms.txtの提唱側は「将来的に採用されうる」と主張している。設置コストが極小（1ファイル）なので「保険として置く」判断もあり得るが、優先順位は最下位。**

---

## 5-29. Redditの被引用シェアへの依存を分散する（リスクヘッジ手法）

- **一言で**: **「AI引用の40%がRedditだから Reddit をやれ」という2026年前半のコンセンサスは、2026年7月のGoogle-Redditライセンス契約更新リスクによって前提が揺らいでいる。単一プラットフォーム依存を意図的に避ける設計が必要。**
- **海外での出典**:
  - [一次] CNBC: Reddit stock sinks on report it may not renew Google AI content deal（2026年7月22日） https://www.cnbc.com/2026/07/22/reddit-stock-google-ai-content-deal.html
  - [一次] Quartz: Reddit stock drops 9% as Google AI content deal nears expiration https://qz.com/reddit-stock-google-ai-content-deal-072226
  - [二次] eMarketer: Reddit reportedly weighs ending Google content licensing deal https://www.emarketer.com/content/reddit-reportedly-weighs-ending-google-content-licensing-deal-publisher-traffic-concerns-mount
  - [二次] Columbia Journalism Review: Reddit Is Winning the AI Game https://www.cjr.org/analysis/reddit-winning-ai-licensing-deals-openai-google-gemini-answers-rsl.php
- **仕組み／なぜ効くか**: RedditのGoogle向け年6,000万ドル契約は**期限が近づいており、Reddit側が更新しない可能性を検討していると報じられ、株価が9%下落した**。**契約が切れれば、Google検索・AI OverviewsでのReddit露出は構造的に減る可能性がある。** 一方でRedditはOpenAI等とも個別にライセンス契約を持つため、ChatGPT側の引用は残る可能性が高い。**つまり「Redditに賭ける」ことは「Googleの契約更新に賭ける」ことと同義になっている。**
- **具体手順**:
  1. AI引用獲得の投資を**Reddit単独に集中させない**。
  2. 引用元の多様化: **YouTube（AIO引用23.3%）、Wikipedia（18.4%）、LinkedIn（第2位）、Quora（約5%）** に分散。
  3. **最も安全な引用元は「自サイト自身」**。第三者プラットフォームは全て他社の意思決定に依存する。
  4. 四半期ごとに「AI回答での自社言及の引用元URL」を実測し、依存度を可視化する。
  5. プラットフォーム契約ニュース（Reddit/OpenAI/Google）を四半期でウォッチ。
- **日本での言及度**: **ほぼ無**。日本語圏では「RedditがAIに引用される」という話自体が浸透していないため、**その前提が崩れかけているという次の議論には当然到達していない。**
- **日本市場での成立性**: —（リスク管理の考え方）
- **noe-match適用度**: **A**（判断基準として）。工数ゼロ。**「Redditをやるべきか」への回答は、日本語メディアであることと契約リスクの両方から『No』。**
- **リスク・反証**: 反証として、**契約が更新される可能性も同等にある**。CJRの分析ではRedditはAIライセンス市場で優位に立っているとされ、Google側にも継続の動機がある。**確定情報ではなく報道段階であることに留意。**

---

## 領域5の未解決事項

**A. 数値の一次検証ができていない（最重要）**
1. 本調査は WebFetch が egress proxy に全面ブロックされたため、**すべての数値が検索スニペット経由**である。特に以下は実装判断の前に原典で再検証が必要:
   - Reddit 被引用シェア40%、AI Overviews 21%（everything-pr、Peec AI原典を要確認）
   - YouTube AI Overviews引用 23.3% / 29.5%（5WPR と Otterly で数字が食い違っている。**同じ現象を測って23.3%と29.5%が出るのは方法論が違う証拠。両方の方法論を確認するまでどちらも使うべきでない**）
   - 「長尺94% vs Shorts 5.7%」「再生数と引用は無相関」（Otterly原典を要確認。**これが本当なら個人チャンネルの戦略が根本から変わるので、検証優先度が最も高い**）
   - Pinterest「4,000万人が結婚式計画に利用」「年間3.78億回の結婚関連検索」は Pinterest 公式データだが、**発表年が古い可能性がある**（Social Media Today記事の日付を要確認）
2. Google のスパムポリシー原文（site reputation abuse / scaled content abuse）を **developers.google.com で直接読めていない**。ポリシーの正確な文言は必ず原典確認すること。

**B. 日本市場側で確認できなかった事実**
3. **Yahoo!知恵袋「企業公式アカウント」に、個人運営メディアが登録できるか。** 「専門家」枠との違い、審査基準、費用の有無。→ 問い合わせフォームから直接確認するのが最短。**本調査で最も有望な発見なので、これは実際に問い合わせる価値がある。**
4. **Pinterest の現行アフィリエイトリンクポリシー（日本）。** 直貼りの可否が本調査では確定できなかった。
5. **日本のPinterestにおける「結婚・ウェディング」需要の実データ。** 日本の月間1,280万人のうち、結婚準備層が何人いるか。Pinterest Business Japan の公式資料に当たる必要がある。
6. **知恵袋・OKWAVE・教えて!gooが、日本語プロンプトに対するAI回答の引用元になっているか。** 英語圏のQuora 5%に相当する日本語データが存在しない。→ ChatGPT/Perplexityに日本語の婚活クエリを50本投げて引用元ドメインを集計すれば自前で作れる（推奨）。
7. **Google Web Storiesの2026年時点の正式ステータス。** 廃止アナウンスは見つからず、ポリシードキュメントは存続。Google公式ブログの確認が必要。
8. **日本におけるHARO相当の仕組み。** PR TIMES取材リクエスト、Xでの記者の取材募集の実効性が未検証。
9. **日本の比較・口コミプラットフォーム（みん評、みんなのウェディング、価格.com等）へのメディア掲載可否。** WebSearch回数上限により未調査。

**C. 論理的な穴**
10. **「AI引用が増えると収益が増える」という接続が、アフィリエイトメディアについては未実証。** 本レポートの多くの手法は「AI回答に載る」を成果指標としているが、**AI回答に載っても読者がクリックしなければアフィリエイト収益はゼロ**。zero-click content論（5-27）はSaaS・B2Bの文脈で作られており、**成果報酬型メディアへの適用可能性は誰も検証していない。これはnoe-matchにとって最も重要な未解決問題。**
11. **noe-matchが既に稼働させているnote寄生14本の実測データが手元にない。** 5-01の「借りた権威は乗らなくなった」という結論が、実際のnote記事の順位推移と一致するかを、まず自前データで確認すべき。**外部の一般論より自前の実測が優先される。**
12. 本レポートの英語ソースの多くは **SEO業者の自社ブログ（集客目的）** であり、統計を誇張する動機を持つ。**Search Engine Land、SparkToro、Semrush公式調査、Google公式、Pinterest公式、消費者庁以外は、すべて割り引いて読むこと。**

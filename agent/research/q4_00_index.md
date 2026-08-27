# Q4 海外SEO/GEOノウハウ 網羅羅列（索引）

- **調査日**: 2026-08-27
- **目的**: 海外では定番として語られているが、日本語圏のSEO情報にほとんど流通していない手法を、統合・要約せずに網羅的に羅列する
- **成果**: 8領域 / **192手法** / 参照ユニークURL 871件 / 5,732行
- **ブランチ**: `claude/q4-overseas-methods-research-ke217c`

この索引は結論を出す文書ではない。**羅列された192手法の入口**である。
各手法の詳細（出典URL・具体手順・日本での言及度・noe-match適用度A/B/C・リスクと反証）は
各領域ファイルの該当番号を直接読むこと。

---

## ⚠ この調査の信頼性の限界（実装判断の前に必ず読む）

本セッションの実行環境に2つの制約があり、**192手法すべてが「検索スニペット経由の情報」である**。

### 制約1: 外部サイトの本文取得が全面遮断

WebFetch / curl が egress proxy によって全ドメインでブロックされた
（`developers.google.com` / `ahrefs.com` / `searchengineland.com` / `searchenginejournal.com` /
`blog.cloudflare.com` / `arxiv.org` / `e-stat.go.jp` / `wikipedia.org` すべて 403 または EGRESS_BLOCKED）。

**英語一次ソースの本文を1本も読めていない。** 記載URLは検索エンジンが実在ページとして
返した文字列であり、捏造ではないが、中身は目視確認していない。
各ファイル内では該当箇所に `【全文未確認】` `【要再検証】` `※抜粋経由` を付けてある。

### 制約2: Web検索クォータの枯渇

セッション全体で共有される200回の検索枠を、8並列の途中で使い切った。
その結果、**依頼の中核だった「日本での言及度の実検証」がほとんど実行できていない。**

| 領域 | 日本語言及度の実検証 |
|---|---|
| 領域1 | 26手法中 **2手法**のみ実検証。残り24は推定 |
| 領域2 | 日本語検証クエリ **8本**実行（最も検証が進んでいる） |
| 領域3 | 26手法中 **4手法**のみ実検証 |
| 領域4 | 26手法中 **2手法**のみ実検証 |
| 領域5 | 日本語クエリ2本が未実行 |
| 領域6 | 23手法中 **2手法**のみ実検証 |
| 領域7 | ライブ検索8回で打ち止め。`[検証済]`/`[知識ベース]`/`[要原文確認]` でラベル分け |
| 領域8 | **0回**。18論点中7論点で停止（8-08〜8-18は未着手） |

つまり **「海外にあって日本に無い」という判定そのものが、大半の手法で未確認**である。
各ファイル末尾に「実行すべき日本語クエリ一覧」を置いてあるので、検索枠が戻り次第そこを埋める。

### だからGPT / Gemini 側が本体になる

GPT / Gemini の Deep Research はページ本文を実際に読める。
`q4_prompts_for_gpt_gemini.md` のプロンプトをそれぞれに投げ、
戻りを `q4_09_gpt.md` / `q4_10_gemini.md` として置けば、
3エンジンの突き合わせで「一致した手法（信頼度高）／1エンジンだけの手法（穴場候補）／
矛盾した手法（要実測）」に仕分けできる。出力フォーマットは3エンジンで統一してある。

---

## 領域別サマリ

| 領域 | ファイル | 手法数 | 参照URL | 行数 |
|---|---|---|---|---|
| 領域1: GEO/LLMO/AI検索最適化 | `q4_01_geo_llmo.md` | 26 | 151 | 667 |
| 領域2: デジタルPR/リンクアーニング | `q4_02_digital_pr.md` | 25 | 116 | 581 |
| 領域3: pSEO/オープンデータ/データバンク | `q4_03_pseo_databank.md` | 26 | 144 | 791 |
| 領域4: テクニカルSEO/情報設計 | `q4_04_technical.md` | 26 | 88 | 626 |
| 領域5: Off-SERP/他プラットフォーム | `q4_05_off_serp.md` | 29 | 139 | 797 |
| 領域6: 計測・分析・実験設計 | `q4_06_measurement.md` | 23 | 121 | 738 |
| 領域7: コンテンツ戦略・編集設計 | `q4_07_content.md` | 30 | 62 | 1199 |
| 領域8: 2026年最前線と日英情報ギャップ | `q4_08_frontier.md` | 7 | 50 | 333 |
| **合計** | 8ファイル | **192** | **871** | **5732** |

---

## 全192手法の一覧

### 領域1: GEO/LLMO/AI検索最適化

`q4_01_geo_llmo.md` — 26手法 / 参照URL 151件 / 667行

- **1-01.** llms.txt / llms-full.txt（llms.txt standard）
- **1-02.** チャンクレベル最適化 / 自己完結チャンク（Chunk-level Optimization / Self-contained Chunks）
- **1-03.** Citation Engineering（統計・引用・出典の同一文内配置）
- **1-04.** Query Fan-out 対応設計（Query Fan-out / Synthetic Queries）
- **1-05.** AIクローラの用途別制御（GPTBot / OAI-SearchBot / ClaudeBot / Claude-SearchBot / Google-Extended / PerplexityBot / CCBot）
- **1-06.** Cloudflare Pay Per Crawl / AI Crawl Control（クロール課金・デフォルト遮断）
- **1-07.** AIクローラはJavaScriptを実行しない（No-JS Rendering / SSR前提設計）
- **1-08.** AIエージェント向けMarkdown配信 / コンテンツネゴシエーション（Serving Markdown to Agents）
- **1-09.** Entity SEO / Wikidata・sameAs・ナレッジパネル掌握
- **1-10.** ProfilePage / Person スキーマによる著者エンティティ構築
- **1-11.** ブランド言及（Unlinked Mentions）優先の外部施策
- **1-12.** サードパーティ・リスティクル掲載（Listicle Placement / Off-site GEO）
- **1-13.** エンジン別の引用元プロファイルに合わせた出し分け
- **1-14.** 「取得されるが引用されない」問題への対処（Retrieval ≠ Citation）
- **1-15.** Bing インデックス確保 / IndexNow（ChatGPT引用の前提条件）
- **1-16.** utm_source=chatgpt.com とAIリファラのGA4計測
- **1-17.** Search Console 生成AIパフォーマンスレポートの読み方
- **1-18.** AIボットのサーバーログ解析（Log File Analysis for AI Crawlers）
- **1-19.** プロンプトリサーチ（Prompt Research / Conversational Query Research）
- **1-20.** AI可視性計測ツール（Profound / Peec AI / Otterly / Scrunch / Semrush AI Toolkit / Ahrefs Brand Radar）と自作計測
- **1-21.** リーセンシーバイアスの利用（Recency Bias / dateModified の機械可読化）
- **1-22.** セマンティック・トリプル文体（Subject-Predicate-Object / Koray Framework）
- **1-23.** エンティティ・サリエンス測定（Entity Salience / Google Cloud NLP API）
- **1-24.** Dataset スキーマ＋Google Dataset Search（一次データの機械可読化）
- **1-25.** 廃止済み／表示なしスキーマの「AI向け信号」としての残存利用（Speakable / ClaimReview / FAQ）
- **1-26.** コサイン類似度によるコンテンツ自己監査（Embedding-based Content Audit）

### 領域2: デジタルPR/リンクアーニング

`q4_02_digital_pr.md` — 25手法 / 参照URL 116件 / 581行

- **2-01.** データ主導ヒーローキャンペーン（Data-led Hero Campaign）
- **2-02.** リアクティブPR / ニュースジャック（Reactive PR / Newsjacking）
- **2-03.** エキスパートコメンタリー：HARO後継プラットフォーム群（Journalist Request Platforms）
- **2-04.** #JournoRequest ハッシュタグ監視（X / Bluesky）
- **2-05.** 日本版ジャーナリストリクエスト・プラットフォーム（メディチョク / 企画の窓口）
- **2-06.** 統計まとめページ戦法（Statistics Page Play）
- **2-07.** 未リンク言及の回収（Unlinked Brand Mention Reclamation）
- **2-08.** リンク切れ利用（Broken Link Building）
- **2-09.** 失われた被リンク／404リダイレクト回収（Lost Link & 404 Reclamation）
- **2-10.** リソースページ・リンクビルディング（Resource Page Link Building）
- **2-11.** リンクギャップ分析／競合被リンクのリバースエンジニアリング（Link Gap Analysis）
- **2-12.** オリジナル調査（アンケート）の設計とパネル調達（Original Research / Survey Design）
- **2-13.** データジャーナリズム型リンクベイト（公的オープンデータの再集計＋自治体ランキング化）
- **2-14.** 情報公開請求ベースのキャンペーン（FOI-led Campaign）
- **2-15.** 無料ツールをリンクマグネットにする（Free Tool as Link Magnet）
- **2-16.** バーナクルSEO（Barnacle SEO）
- **2-17.** ポッドキャストゲスト出演（Podcast Guesting）
- **2-18.** エゴベイト／エキスパートラウンドアップ（Ego Bait / Expert Roundup）
- **2-19.** アワード／バッジ配布（Awards & Badge Link Building）
- **2-20.** 公的機関・教育機関からのリンク（.gov / .edu 相当＝.go.jp / .lg.jp / .ac.jp）
- **2-21.** 画像・図表の無断利用からのリンク回収（Image Link Reclamation / Reverse Image Search）
- **2-22.** Wikipedia のデッドリンク／要出典枠（Wikipedia Dead Link & Citation Needed）＋ Wikimedia Commons
- **2-23.** 記念日カレンダーによる先行企画（Awareness Day / Forward-Planning Calendar）
- **2-24.** 検索データ主導PR（Google Trends / Search-Volume-Led PR）
- **2-25.** 【手法ではなく制約条件】デジタルPRの「やりすぎ」リスクとGoogle側の見解

### 領域3: pSEO/オープンデータ/データバンク

`q4_03_pseo_databank.md` — 26手法 / 参照URL 144件 / 791行

- **3-01.** データバンク型プログラマティックSEO（Data-Backed Programmatic SEO）
- **3-02.** head/torso/tail のテンプレ三層設計（Head-Torso-Tail Template Architecture）
- **3-03.** キーワード修飾子マトリクス（Keyword Modifier Matrix / Two-Modifier Pattern）
- **3-04.** ページごとの固有 value-add 強制注入（Unique Value-Add per Page）
- **3-05.** Google spam policy 準拠設計（Scaled Content Abuse Compliance）
- **3-06.** 段階リリース＋インデックス率ゲート（Staged Rollout with Indexation Gate）
- **3-07.** noindex→index の品質昇格パイプライン（Quality Promotion Pipeline）
- **3-08.** Index bloat の剪定と「正しい削除順序」（Index Bloat Pruning / Correct Removal Order）
- **3-09.** 「Crawled – currently not indexed」のトリアージ（Crawl-Not-Indexed Triage）
- **3-10.** GSC Crawl Stats ＋ ログファイル分析（Crawl Budget Forensics）
- **3-11.** GSC Bulk Data Export → BigQuery（全量クエリデータの確保）
- **3-12.** IndexNow ＋ Google Indexing API の「限界の正確な理解」
- **3-13.** sitemap lastmod の誠実運用（Lastmod Hygiene）
- **3-14.** sitemap 分割を「診断装置」として使う（Sitemap Segmentation as a Diagnostic）
- **3-15.** Dataset 構造化データ ＋ Google Dataset Search（Dataset Schema / DCAT）
- **3-16.** 再集計による新規性の生成（Derivative Data / Re-aggregation）
- **3-17.** 独自指数・合成スコアの設計（Composite Index / Proprietary Score）
- **3-18.** 埋め込みコード配布によるリンク獲得（Embed-Code Distribution / Widget Link Bait）
- **3-19.** 「◯◯統計」ページ＝リンク磁石（Statistics Page as Linkable Asset）
- **3-20.** アルゴリズム的内部リンク（Algorithmic Internal Linking / Embedding-Based）
- **3-21.** hub-spoke の自動生成とリンク整流（Hub & Spoke / Link Equity Routing）
- **3-22.** ファセットナビゲーションの設計（Faceted Navigation: 事前生成ホワイトリスト方式）
- **3-23.** Content decay の検知とトリアージ（Content Decay Triage）
- **3-24.** 大規模剪定（Content Pruning at Scale）
- **3-25.** 一次ソース台帳＝データ出所の証跡管理（Data Provenance Ledger）
- **3-26.** 静的サイト（GitHub Pages）でのpSEO実装制約と回避策

### 領域4: テクニカルSEO/情報設計

`q4_04_technical.md` — 26手法 / 参照URL 88件 / 626行

- **4-01.** インフォメーションゲイン・スコア（Information Gain Score）
- **4-02.** コンテンツ・プルーニング／統合（Content Pruning / Consolidation）
- **4-03.** トピカルオーソリティの定量設計（Topical Map / Koray Framework）
- **4-04.** クエリ・カニバリゼーションの機械的検出（GSC API × page-query 1:1マッピング）
- **4-05.** ストライキングディスタンス分析（Striking Distance / 11〜20位の刈り取り）
- **4-06.** 内部リンクスカルプティングとPageRankフロー（Internal Link Sculpting）
- **4-07.** オーファンページ検出（Orphan Page Detection）
- **4-08.** AI抽出を前提とした情報設計（Content Chunking / Passage-level 最適化）
- **4-09.** Article と BlogPosting の使い分け／構造化データ型の一貫性
- **4-10.** 著者エンティティの構築（Author Entity Building / Person schema + sameAs）
- **4-11.** Organization エンティティの強化（knowsAbout / founder / publisher の連結）
- **4-12.** 一次体験の証明（Proof of Experience / オリジナル画像）
- **4-13.** Core Web Vitals の実際の重み（過大評価への反証を含む）
- **4-14.** ログファイル解析の個人向け代替（GSC Crawl Stats / Cloudflare / GA4）
- **4-15.** dateModified と「空更新」問題
- **4-16.** クエリ・ファンアウト対応（Query Fan-Out / AI Mode 最適化）
- **4-17.** Speakable / ItemList / 高度な構造化データ型の取捨選択
- **4-18.** コンテンツ・ディケイ（Content Decay）の定量監視とリフレッシュ
- **4-19.** レンダリング戦略：静的HTMLの構造的優位
- **4-20.** llms.txt は入れなくてよい（やらないことの特定）
- **4-21.** Google公式の否認 vs リーク／訴訟で判明した実態
- **4-22.** サイト構造：フラット vs サイロ（クリック深度の実務結論）
- **4-23.** サイトマップと「差分」の整合（lastmod・分割・網羅率）
- **4-24.** 国内単一言語サイトの地域・実体シグナル（hreflang不要ケース）
- **4-25.** `<table>` と定義リストのセマンティック実装（抽出しやすさ）
- **4-26.** インデックス制御の測定基盤（IndexNow／申請運用の位置づけ）

### 領域5: Off-SERP/他プラットフォーム

`q4_05_off_serp.md` — 29手法 / 参照URL 139件 / 797行

- **5-01.** サイト評判の不正使用ポリシー後のパラサイトSEO（Parasite SEO post-Site Reputation Abuse）
- **5-02.** バーナクルSEO（Barnacle SEO）
- **5-03.** Redditでの被引用設計（Reddit as the AI citation layer）
- **5-04.** Reddit AMA（Ask Me Anything）
- **5-05.** Quora / 英語圏Q&A と、日本のQ&A公式回答制度
- **5-06.** YouTube SEO（長尺・how-to）
- **5-07.** YouTube Shorts / ショート動画の検索インデックス化
- **5-08.** TikTok SEO / TikTokを検索面として使う
- **5-09.** InstagramのGoogleインデックス化を利用する
- **5-10.** Pinterest SEO（結婚・ウェディング領域）
- **5-11.** Wikipedia記事化（エンティティ登録の正攻法）
- **5-12.** Wikidataへのエンティティ登録
- **5-13.** Google Discover最適化
- **5-14.** Google News / Publisher Center
- **5-15.** Web Stories（生死判定）
- **5-16.** LinkedIn 記事・ニュースレター
- **5-17.** Newsletter / Substack（Owned Audience）
- **5-18.** LINE公式アカウント（日本版 Owned Audience）
- **5-19.** ポッドキャストへのゲスト出演（Guest Podcasting）
- **5-20.** 自主ポッドキャスト＋トランスクリプト公開
- **5-21.** リスティクル掲載（Listicle Placement）
- **5-22.** 比較サイト・アグリゲータ／ディレクトリ掲載（Product Hunt / G2 型）
- **5-23.** 高DRプラットフォームへのドキュメント配置（SlideShare / Issuu / Scribd / Notion / GitHub）
- **5-24.** Amazon Kindle（KDP）出版による著者性シグナル
- **5-25.** HARO型ソースプラットフォームでの専門家コメント提供（Digital PR）
- **5-26.** コミュニティ主導成長（Community-Led Growth：Discord / Slack / 私有地化）
- **5-27.** Zero-Click Content / Search Everywhere Optimization（メタ手法）
- **5-28.** llms.txt（反証項目：やらなくていいことの明確化）
- **5-29.** Redditの被引用シェアへの依存を分散する（リスクヘッジ手法）

### 領域6: 計測・分析・実験設計

`q4_06_measurement.md` — 23手法 / 参照URL 121件 / 738行

- **6-01.** SEOスプリットテスト（SEO A/B Test / SearchPilot型ページ分割テスト）
- **6-02.** CausalImpact（ベイズ構造時系列による介入効果推定）
- **6-03.** CUPED（事前実験データによる分散削減）
- **6-04.** 時系列対照群デザイン / Difference-in-Differences / スイッチバック
- **6-05.** Incrementality測定（ホールドアウト／地理的ホールドアウト／アフィリエイト増分）
- **6-06.** Page × Query マトリクスによるカニバリゼーション検出
- **6-07.** CTRカーブからの期待値差分（Expected CTR Gap / Opportunity Score）
- **6-08.** Striking Distance分析（11〜20位帯の狙い撃ち）
- **6-09.** GSCデータの既知の罠の体系的理解（Anonymized queries / Position定義 / 16ヶ月 / サンプリング）
- **6-10.** GSC Bulk Data Export → BigQuery（匿名化フラグとパーティション設計）
- **6-11.** クエリの意味クラスタリング（Embedding + SERP Overlap Clustering）
- **6-12.** Content Decay検出と更新ROIの優先順位付け
- **6-13.** 季節調整済みYoY / STL・MSTL分解 / Prophetによる予測
- **6-14.** ベイズによる小標本意思決定（Beta-Binomial、「n=4クリックで何が言えるか」）
- **6-15.** 統計的検出力の事前計算（Power Analysis / MDE）— 「そもそもこの実験は可能か」の判定
- **6-16.** 週次の順位変動の統計的有意性判定
- **6-17.** AI流入の計測（utm_source=chatgpt.com / GA4カスタムチャネルグループ / dark traffic）
- **6-18.** Share of Model / LLM引用率の自前モニタリング
- **6-19.** Share of Search / ブランド需要を先行指標にする
- **6-20.** ログファイル / クロールバジェットの実測と個人規模での代替
- **6-21.** Rank Trackingの限界とSERP Feature / Pixel Position トラッキングへの移行
- **6-22.** Attribution: アフィリエイトのラストクリック問題と assisted conversion
- **6-23.** 海外で使われている無料/低額の計測ツールスタック

### 領域7: コンテンツ戦略・編集設計

`q4_07_content.md` — 30手法 / 参照URL 62件 / 1199行

- **7-01.** トピカルマップ／セマンティック・コンテンツ・ネットワーク（Topical Map / Semantic Content Network）
- **7-02.** ソース・コンテキスト（Source Context）
- **7-03.** Central Entity と Attribute 起点の見出し設計
- **7-04.** Core Section / Outer Section と公開順序
- **7-05.** インフォメーション・ゲイン（Information Gain）—— "10x content" 以降
- **7-06.** コンテンツ・マーケット・フィット（Content-Market Fit）
- **7-07.** 検索意図の細分化（Know Simple / Know / Do / Website / Visit-in-person）
- **7-08.** SERPからの意図逆算と mixed intent SERP の扱い
- **7-09.** インテント・シフトの検出（Intent Shift Detection）
- **7-10.** ペインポイントSEO／ボトム・オブ・ファネル優先（Pain Point SEO / BOFU-First）
- **7-11.** プロダクト・レッド・コンテンツ（Product-Led Content）
- **7-12.** セカンドオーダー・ペインポイント（Second-Order Pain Points）
- **7-13.** "Best X for Y" のモディファイア粒度設計
- **7-14.** "X Alternatives" ページ
- **7-15.** "X vs Y" コンパリゾン・ページ
- **7-16.** オリジナル・リサーチ・フライホイール（Original Research Flywheel）
- **7-17.** "How We Test" / テスト方法論ページ（Testing Methodology Page）
- **7-18.** ファーストハンド・テスティング・プロトコル（First-Hand Testing Protocol）
- **7-19.** Reviews System 要求要素チェックリスト（Google公式の逐条リスト化）
- **7-20.** Helpful Content 自己評価質問群と "Who / How / Why"
- **7-21.** エディトリアル・スタンダード／訂正ポリシー／ファクトチェックページ
- **7-22.** 著者バイライン と "Who is behind this site"
- **7-23.** コンテンツ・リフレッシュの型と "Significant Update" の定義
- **7-24.** コンテンツ・プルーニング／統合（Content Pruning / Consolidation）
- **7-25.** グロッサリー／定義ページの資産化（Glossary / "What is X" Pages）
- **7-26.** カリキュレーター／インタラクティブ・ツール
- **7-27.** プログラマティックFAQ生成の罠（Scaled Content Abuse）
- **7-28.** アフィリサイト壊滅事例の逆算分析（HouseFresh / Retro Dodo 型）
- **7-29.** 小サイトが大手に勝つ実例の逆算（Detailed.com / r/juststart 型）
- **7-30.** Site Reputation Abuse を逆手に取る（大手の弱点の構造的利用）

### 領域8: 2026年最前線と日英情報ギャップ

`q4_08_frontier.md` — 7手法 / 参照URL 50件 / 333行

- **8-01.** Search Console の生成AIパフォーマンスレポート（Generative AI Performance Reports in Search Console）
- **8-02.** Query fan-out（クエリ・ファンアウト）
- **8-03.** llms.txt はほぼ決着した（2026年時点）
- **8-04.** Cloudflare の AIクローラー既定ブロックと Pay Per Crawl → Pay Per Use
- **8-05.** OpenAI が Instant Checkout を撤回した（2026年3月）
- **8-06.** エージェント購買プロトコルが乱立している（ACP / UCP / AP2 / MCP / A2A / Visa TAP）
- **8-07.** 「AI経由トラフィックは高コンバージョン」説の実際（数値が1.2倍〜23倍までばらついている）

---

## 複数領域から重複して挙がった手法（＝独立に複数の角度から支持された）

8つの領域は互いに独立して調査した。それでも同じ手法が複数領域から挙がったものは、
**その分だけ海外で広く言われている**と読める（ただし一次ソース未確認という制約は同じ）。

| 手法 | 出現箇所 |
|---|---|
| llms.txt（**やらなくていい**という決着） | 1-01 / 5-28 / 8-03 |
| Query fan-out 対応設計 | 1-04 / 4-16 / 8-02 |
| AIクローラの用途別制御・Cloudflare既定遮断 | 1-05 / 1-06 / 8-04 |
| ログファイル分析（AIボット含む） | 1-18 / 3-10 / 6-20 |
| GSC Bulk Data Export → BigQuery | 3-11 / 6-10 |
| Search Console 生成AIレポート | 1-17 / 8-01 |
| utm_source=chatgpt.com によるAI流入計測 | 1-16 / 6-17 |
| Share of Model / AI可視性の自前計測 | 1-20 / 6-18 |
| Dataset スキーマ ＋ Google Dataset Search | 1-24 / 3-15 |
| チャンク設計（自己完結チャンク） | 1-02 / 4-08 |
| Koray のトピカルマップ体系 | 4-03 / 7-01〜7-04 |
| 統計まとめページ＝リンク磁石 | 2-06 / 3-19 |
| 公的オープンデータの再集計・自治体ランキング化 | 2-13 / 3-16 |
| 未リンク言及の回収 | 1-11 / 2-07 |
| サードパーティ・リスティクル掲載 | 1-12 / 5-21 |
| ポッドキャストのゲスト出演 | 2-17 / 5-19 |
| バーナクルSEO | 2-16 / 5-02 |
| Wikidata へのエンティティ登録 | 1-09 / 5-12 |
| HARO型の専門家コメント提供 | 2-03 / 5-25 |
| 無料ツール／埋め込みコードによるリンク獲得 | 2-15 / 3-18 |
| Content decay の検知と剪定 | 3-23 / 3-24 / 6-12 |

---

## 副産物: リポジトリ実査で確定した不具合（海外ノウハウ以前の穴）

領域3・4・6のエージェントがリポジトリを実査して発見し、**索引作成時に独立して再確認した**もの。
これらは調査の副産物だが、192手法のどれよりも先に手を打つ価値がある。

| # | 事実 | 確認方法 | なぜ問題か |
|---|---|---|---|
| 1 | **sitemap の記事欠落**。記事ディレクトリ256 vs `sitemap.xml` 234 vs `sitemap-all.xml` 230 | `ls -d articles/*/` と `grep -c '<loc>'` で再確認済み | `AGENT.md` に「一覧とsitemapの記事集合は常に一致させること」と明記されているルールが効いていない。インデックス申請の運用が流入の生命線である以上、載っていない記事は存在しないのと同じ |
| 2 | **`build_articles.py` が全URLに実行日を lastmod として出力**（`write_sitemap(date.today().isoformat())`、L436） | 該当行を再確認済み | 更新していない記事にも今日の日付が付く。Googleがサイト単位で lastmod を信用しなくなる典型パターン。**鮮度シグナルを自分で潰している** |
| 3 | **`author` が `Person` のものが0件**（`Organization` を author にしている記事が208本） | `grep -rl '"@type": *"Person"' articles/` = 0 | 領域1（1-10 ProfilePage/Person）・領域4（4-10 著者エンティティ）・領域7（E-E-A-T）が全部ここに依存する。`geo_entity_design.md` の「著者/編集部情報でEntityを立てる」構想の土台が未実装 |
| 4 | **`<dl>`（定義リスト）の使用が0件** | `grep -rl '<dl' articles/` = 0 | 4-25「AI抽出のためのセマンティクス」の余地がまるごと残っている |
| 5 | **`scripts/fetch_gsc.py` の3つの実装欠損** — `rowLimit: 500` 固定、`startRow` のページネーションなし、**履歴の永続保存なし** | L41 を再確認済み | **GSCのデータは16ヶ月で消える。保存していない期間は永久に取り返せない。** ドメイン開設が2026年6月なので、今ならまだ全期間が残っている。ここは時間切れのある問題 |
| 6 | 内部オーファン59件（256本中23%） | **未再確認**（領域4エージェントの報告値。要検証） | 事実なら、書いた記事の4本に1本がどこからもリンクされていない |
| 7 | スキーマ型の混在（Article 132 / BlogPosting 77 / 型なし48） | **未再確認**（領域4エージェントの報告値。要検証） | 型なし48本はリッチリザルトにも構造化理解にも乗らない |

---

## 未解決事項の総数

各領域ファイル末尾に「未解決事項」セクションがある。これは**この調査で答えが出なかった論点**であり、
GPT / Gemini 側に投げるべき問いのリストでもある。

- 領域1: 10項目
- 領域2: 10項目
- 領域3・4・5・6・7・8: 各ファイル末尾を参照
- 領域8は特に、18論点中11論点（8-08〜8-18）が**未着手のまま空欄**として残っている

出典間で数値が食い違っており、使用前に方法論の確認が必要なもの:

- **YouTubeのAI引用率**: 23.3% と 29.5% で出典間に食い違い（領域5）
- **AI経由トラフィックのコンバージョン倍率**: 1.2倍〜23倍までばらつく。母数はAIが全セッションの0.18%（領域8）

---

## 次の一手

1. **GPT / Gemini に `q4_prompts_for_gpt_gemini.md` のプロンプトを投げる**（一次ソース精読はこちらが本体）
2. 戻りを `q4_09_gpt.md` / `q4_10_gemini.md` として置き、3エンジンの突き合わせ索引を作る
3. **検索枠が戻り次第、各ファイル末尾の「日本語クエリ一覧」を実行して言及度を埋める**（この調査の最大の欠損）
4. 領域8の未着手11論点を再実行する
5. 上表の副産物1〜5は、192手法の検証を待たずに着手できる

**Cloudflare の AIクローラー既定遮断が2026年9月15日**（領域8・8-04、要一次確認）。
noe-match.com が Cloudflare 配下かどうかを先に確認すること。該当するなら3週間しかない。

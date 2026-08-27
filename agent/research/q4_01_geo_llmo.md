# 領域1: GEO/LLMO/AI検索最適化

- **調査日**: 2026-08-27
- **参照したソース数**: 一次・二次あわせて約90URL（うち英語ソース約80、日本語ソース約13）。実際に検索クエリを投げた回数は26回（WebSearch）、直接フェッチ試行8回。
- **担当領域**: GEO / LLMO / AI検索最適化（AIに引用される側に回るための技術）
- **方針**: 統合・結論づけをせず「羅列」する。数字には必ず出典URLを付ける。出典が確認できない数字は書かない。

---

## ⚠️ 本レポートの限界（先に開示）

1. **WebFetch（直接ページ取得）がネットワーク側で全面ブロックされていた**。searchengineland.com / searchenginejournal.com / ahrefs.com / arxiv.org / developers.google.com / platform.openai.com / blog.cloudflare.com / ipullrank.com / wikipedia.org のいずれも `EGRESS_BLOCKED` で本文取得不可。したがって**一次ソースのURLは特定できているが、本文全文の目視確認はできていない**。本文中の数値は検索エンジンが返した抜粋に基づく。**孫引きリスクが残る数値には「※抜粋経由」と明記**した。使う前に必ず原典URLを開いて数字を確認すること。
2. **日本語での言及度検証は、セッション共有の検索クォータ（200回）を使い切ったため、2手法（1-01 llms.txt / 1-02 チャンク最適化）しか実検索できていない**。残りは「推定（未検証）」とラベルし、**実行すべき日本語クエリを明記**した。この推定は私のドメイン知識に基づく推測であり、事実ではない。
3. 事実と推測の区別: 「【事実】」＝出典URLで確認できた記述、「【推測】」＝私の解釈・当てはめ、と明示する。

---

## 1-01. llms.txt / llms-full.txt（llms.txt standard）

- **一言で**: サイトのLLM向け目次をMarkdownで `/llms.txt` に置き、全文版を `/llms-full.txt` に置く提案仕様。2026年時点で「主要AI企業のどこも公式に使っていない」ことがデータで示されており、賛否が完全に割れている。
- **海外での出典**:
  - Search Engine Journal「Google Says LLMs.txt Is Purely Speculative For Now」 https://www.searchenginejournal.com/google-says-llms-txt-is-purely-speculative-for-now/577576/ （John Muellerがllms.txtを「keywordsメタタグ」に例えた件）
  - Rankability「LLMS.txt Adoption: 8.7% of the Top 1,000 (June 2026)」 https://www.rankability.com/data/llms-txt-adoption/ （2026年6月時点、上位1,000サイトの8.7%が設置）
  - Casey Burridge「Does anyone actually have an llms.txt? I checked millions of websites」 https://caseyrb.com/blog/state-of-llms-txt-adoption/
  - Presenc AI「State of llms.txt 2026」 https://presenc.ai/research/state-of-llms-txt-2026 （Gary Illyesが「Googleはサポートしないし予定もない」と発言、Google 2026年の生成AI関連ドキュメントが llms.txt を "unnecessary tactics" に列挙）
  - Stan Ventures「Google: Noindex LLMs.txt to Avoid Search Clutter」 https://www.stanventures.com/news/noindex-llms-txt-google-recommendation-3674/
  - Kai Spriestersbach「The llms.txt is dead. More precisely: a dud.」 https://medium.com/@kaispriestersbach/the-llms-txt-is-dead-more-precisely-a-dud-ab7bee4f469c
- **仕組み／なぜ効くか**: RAG型AIがHTMLをパースするコストを省き、正規化されたMarkdownを直接読ませる想定。理屈上はトークン節約と誤パース回避に効く。ただし**受け手（クローラ側）が読みに来なければゼロ**。【事実】Limy.aiの5億件超のAIボットイベント分析で `/llms.txt` を直接叩いたリクエストは数百件しかなく、GPTBot / ClaudeBot / PerplexityBot / OAI-SearchBot / Google-Extended は圧倒的にHTMLを取りに来ていた（※抜粋経由、原典: https://presenc.ai/research/state-of-llms-txt-2026 、 https://geojacker.com/llms-txt ）。
- **具体手順**:
  1. 設置コストが低いなら置く（静的ファイル1本）。ただし**期待値をゼロに設定**する。
  2. `/llms.txt` は「H1＋サイト概要＋主要URLのMarkdownリンク一覧＋各1行説明」の形式にする。
  3. `/llms-full.txt` を作るなら全記事の本文結合版。258記事なら数MB級になるので、カテゴリ別に分割する（例: `/llms-marriage.txt`）。
  4. Googleは llms.txt を検索結果に出さないよう **noindex 推奨**（上記Stan Ventures）。`X-Robots-Tag: noindex` をこのパスにだけ付ける。
  5. **サーバーログで `/llms.txt` への実アクセスを月次で数える**。ゼロならメンテを止める。この「効果測定して止める」までをセットにするのが海外の実務。
- **日本での言及度**: **高（実検証済み）**。日本語クエリ「llms.txt SEO 効果 意味ない 日本語」で検索した結果、シンプリック https://simplique.jp/llms-txt-strategy/ 、ANEMA https://anema.co.jp/blog/llms-txt/ 、unType https://www.untype.jp/blog/llms-txt-agent-readability/ 、Cominka https://service.cominka.co.jp/llms-txt-not-required/ など**日本語記事が大量に存在し、しかも「意味がない」という結論まで到達している**。つまりこれは「日本で流通していない手法」ではない。**ただし `llms-full.txt` の分割運用、noindex推奨、サーバーログでの実アクセス計測という運用面は日本語記事でほぼ触れられていない**（unTypeの記事が例外的にエージェント可読性の観点で踏み込んでいる）。
- **noe-match適用度**: **C（不適に近いB）**。設置コスト自体は30分だが、**期待リターンが実測でほぼゼロ**。個人運営のリソースを割く優先度は最下位。工数0.5h。やるなら「noindexを付ける」「ログで数える」までセットで。
- **リスク・反証**: 【事実】Muellerの反証が最も強い。「サイト運営者が自己申告する内容は keywords メタタグと同じで操作可能だから検索側は使わない」という構造的な指摘。また「LLMにHTMLを読ませてllms.txtを生成し、別のLLMがHTMLを読まなくて済むようにする」という自己矛盾も指摘されている（上記SEJ）。【事実】採用率10%前後（SE Ranking 300,000ドメイン調査で10.13%、※抜粋経由 https://organikpi.com/blog/distribution/llms-txt-adoption-impact/ ）に対して、クローラの参照はほぼゼロ。

---

## 1-02. チャンクレベル最適化 / 自己完結チャンク（Chunk-level Optimization / Self-contained Chunks）

- **一言で**: AI検索はページ単位ではなく「チャンク（数百トークンの断片）」単位で検索・引用するため、**1見出しブロックだけを切り出しても意味が通る**ように書く。代名詞を排し、主語を毎回明示する。
- **海外での出典**:
  - Lumar「Content Chunking & AI Extractability」 https://www.lumar.io/blog/best-practice/content-chunking-ai-extractability-geo-aeo-explainer/
  - Averi「How AI Agents Actually Read Your Content: Chunking, Embeddings, and Retrieval」 https://www.averi.ai/blog/how-ai-reads-content-chunking-embeddings-retrieval
  - Wellows「Chunk Optimization: Improving Content for AI SERPs」 https://wellows.com/blog/chunk-optimization-for-ai-search/
  - Lumar「Semantic Relevance for GEO / AEO」 https://www.lumar.io/blog/best-practice/geo-aeo-semantic-relevance-for-ai-search-visibility/
  - 背景理論として Anthropic の Contextual Retrieval（チャンクに文脈を前置してから埋め込む手法）が引用されている（※抜粋経由）
- **仕組み／なぜ効くか**: RAGパイプラインは①クエリをfan-outで分解 → ②ベクトル検索で各サブクエリに合致する**チャンク**を取得 → ③そのチャンクだけをLLMに渡す。つまりLLMが見るのは「あなたのページ」ではなく「あなたのページの1ブロック」。前段落を読まないと意味が通らない文（「これは」「上記の通り」「その場合」）はチャンク単体で無価値になり、リランカで落とされる。
- **具体手順**:
  1. H2/H3ごとに「その見出し配下だけで完結する」ようリライトする。冒頭2文に**固有名詞（婚活、結婚相談所、○○市など）を必ず入れる**。
  2. 指示語（これ・それ・上記・前述・後述）を機械的にgrepして固有名詞に置換する。
  3. 1チャンク＝150〜300字程度のまとまりを意識し、H2直下に「結論の1文」を置く（answer-first）。
  4. **アコーディオン／タブ／モーダルの中に本文を入れない**（JS依存＝AIクローラに見えない。1-13参照）。
  5. テーブルは `<table>` で書く。画像化した表・スクショの表は引用されない。
  6. 記事末の「まとめ」に情報を集約しない。**各セクションが独立して完結**しているほうが引用面が増える。
- **日本での言及度**: **低（実検証済み）**。日本語クエリ「チャンク最適化 LLMO 自己完結 パッセージ 検索 AI 引用」で検索した結果、上位はすべて「LLMOとは？」系の総論記事（SiTest https://sitest.jp/blog/?p=34404 、Speee https://webanalytics.speee.jp/media/article/what-is-llmo/ 、デジタルドロップ https://digitaldrop.co.jp/blog/llmo-countermeasures-method/ など）で、**RAG／チャンク／パッセージの語は出るが「自己完結チャンクの書き方」という実装レベルの指示にまで落ちている日本語記事は見当たらなかった**。「サイテーション（言及）が重要」という抽象論で止まっている。
- **noe-match適用度**: **A（即実行可）**。258記事あるので全面改稿は非現実的だが、**指示語のgrep置換＋H2直下に結論1文追加**は機械的に進められる。上位20〜30記事に絞れば工数15〜25h。テンプレート化すれば新規記事はゼロコスト。
- **リスク・反証**: 「チャンク最適化で引用率2〜4倍」という数字が複数のベンダーブログに出回っているが（例 https://wellows.com/blog/chunk-optimization-for-ai-search/ ）、**査読済み研究や大規模実測に紐づく出典を確認できなかった**。ベンダー主張として扱うべき。また、自己完結を徹底すると人間の読者には冗長になる（同じ語の反復）ため、UX劣化とのトレードオフがある。

---

## 1-03. Citation Engineering（統計・引用・出典の同一文内配置）

- **一言で**: GEO論文が実験的に検証した「AIに引用されやすい文の型」。**統計の追加・引用符付きの他者発言の追加・出典の明記**が生成AI回答内での可視性を有意に上げる。
- **海外での出典**:
  - Aggarwal, Murahari, Rajpurohit, Kalyan, Narasimhan, Deshpande「GEO: Generative Engine Optimization」KDD 2024 https://arxiv.org/pdf/2311.09735 （arXiv: 2311.09735）
  - Princeton University 公開ページ https://collaborate.princeton.edu/en/publications/geo-generative-engine-optimization/
  - 後続研究「Think Before Writing: Feature-Level Multi-Objective Optimization for Generative Citation Visibility」 https://arxiv.org/pdf/2604.19113
  - 後続研究「From Citation Selection to Citation Absorption」 https://arxiv.org/pdf/2604.25707
- **仕組み／なぜ効くか**: 【事実】GEO論文は10,000クエリ規模の GEO-bench を作り、9種の最適化手法を比較。**Statistics Addition（統計の追加）と Quotation Addition（引用の追加）が全指標で強い改善**を示し、ベストな手法は Position-Adjusted Word Count で+41%、Subjective Impression で+28%の改善（※抜粋経由、原典 https://arxiv.org/pdf/2311.09735 で要確認）。逆にキーワード詰め込み（Keyword Stuffing）は効果がないか悪化した。理屈としては、生成エンジンが「検証可能な具体性」を持つ文を回答に組み込みやすく、かつ引用注を付ける口実になるため。
- **具体手順**:
  1. **1つの文の中に「数値＋出典元名＋年月」を同居させる**。例:「厚生労働省の2025年人口動態統計によれば、日本の平均初婚年齢は男性31.1歳である」。分割して別文にすると、チャンク切断で数値だけが孤立し引用されなくなる。
  2. 「according to X」構文の日本語版＝「〜によれば」「〜の調査では」を段落の**冒頭**に置く。
  3. 専門家・当事者の発言を `「」` で括った直接引用として最低1本入れる（Quotation Addition）。
  4. 定義文を各セクション冒頭に置く（「◯◯とは、〜である。」）。
  5. 統計は**必ずリンク付き**にする。リンクなし数値はAI側の検証に落ちる可能性がある。
  6. キーワード反復を増やす方向の最適化は**やらない**（GEO論文で無効）。
- **日本での言及度**: **ほぼ無〜低（推定・未検証）**。実行すべき日本語クエリ:「GEO 論文 Princeton 統計追加 引用追加 可視性」「生成エンジン最適化 論文 KDD 2024」。【推測】日本語のLLMO記事は「一次情報を持て」「E-E-A-T」という抽象論に寄っており、**GEO論文の手法別効果量（Statistics Addition / Quotation Addition / Cite Sources）を名指しで解説した日本語記事はほぼ流通していない**と考えられる。要検証。
- **noe-match適用度**: **A（即実行可）**。noe-matchは既に自治体データ43件の一次データバンクを持っているので、**「統計＋出典＋日付を1文に同居」というライティングルールに落とすだけ**。既存記事のリライトルールに追加。工数: ルール策定2h＋主要30記事適用10h。
- **リスク・反証**: 【事実】GEO論文の実験は2023年時点のGenerative Engine（当時のBing Chat類）を模した環境で行われており、**2026年のAI Mode / ChatGPT Search にそのまま外挿できる保証はない**。後続の測定論文（ https://arxiv.org/pdf/2604.07585 「Don't Measure Once: Measuring Visibility in AI Search」）は、**AI検索の可視性測定自体が1回の計測では不安定**であることを指摘しており、効果検証には反復測定が必要。また統計の水増し（無関係な数字の挿入）は品質劣化とスパム判定リスク。

---

## 1-04. Query Fan-out 対応設計（Query Fan-out / Synthetic Queries）

- **一言で**: Google AI ModeとAI Overviewsは1つのプロンプトを裏で数十の「合成クエリ」に分解して同時検索する。元クエリだけに最適化した記事は、分解後のサブクエリに引っかからず取得されない。
- **海外での出典**:
  - Search Engine Land「How AI Mode and AI Overviews work based on patents and why we need new strategic focus on SEO」 https://searchengineland.com/how-ai-mode-ai-overviews-work-patents-456346
  - 特許 US20240289407A1「Search with Stateful Chat」（2024年8月29日公開）※抜粋経由、出典 https://julien-gourdon.fr/article/en/what-is-query-fan-out 、 https://wordlift.io/blog/en/query-fan-out-ai-search/
  - iPullRank「Query Fan-Out in Practice」 https://ipullrank.com/query-fanout-how-to
  - Michael King「Everything You MFs Should Know About Query Fan Out」 https://speakerdeck.com/techseoconnect/michael-king-everything-you-mfs-should-know-about-query-fan-out
  - Semrush「We Tested Query Fan-Out Optimization」 https://www.semrush.com/blog/query-fan-out-experiment/
  - Digiday「WTF is query fan-out in Google's AI mode?」 https://digiday.com/media/wtf-is-query-fan-out-in-googles-ai-mode/
- **仕組み／なぜ効くか**: 【事実】LLMに「intent diversity（比較・探索）」「lexical variation（同義語・言い換え）」「entity-based reformulation（ブランド名・特徴の付加）」を持つ多様なクエリ群を生成させ、それぞれを並列検索してからパッセージを統合する（※抜粋経由、上記Search Engine Land / WordLift）。【事実】Ahrefsの1.4Mプロンプト調査では、**タイトル／URLと fan-out クエリのコサイン類似度が引用可否の最大の決定要因**とされている（ https://ahrefs.com/blog/why-chatgpt-cites-pages/ ）。
- **具体手順**:
  1. **Qforia**（iPullRank製・無償OSS）で対象キーワードのfan-outをシミュレーションする。 https://github.com/iPullRank-dev/qforia （Gemini APIキーが必要、AI Mode / AI Overviewモードを選択、20〜30の派生クエリが出る）
  2. 出てきた派生クエリのうち、自サイトが答えていないものを**H2として既存記事に追加**する（新規記事を作らない：1記事で fan-out 空間を面で覆う）。
  3. 派生クエリのタイプ（比較／定義／手順／価格／地域）ごとにブロックを用意する。
  4. **タイトルとURLスラッグを、広いキーワードではなく狭い派生クエリに寄せる**（Ahrefs: 記述的スラッグは引用率89.78% vs 非記述的81.11%、※抜粋経由 https://ahrefs.com/blog/why-chatgpt-cites-pages/ ）。
  5. 記事内にFAQPage（既に実装済み）だけでなく、**本文中の質問形H2**として持たせる（スキーマだけでは本文チャンクにならない）。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「クエリファンアウト AI Mode 対策」「query fan-out 日本語 SEO」。【推測】「クエリファンアウト」という語自体は2025年後半から日本語記事にも出始めているが、**Qforiaでの実シミュレーション手順、コサイン類似度とスラッグ設計の関係まで書いた日本語記事はほぼ無い**と推定。要検証。
- **noe-match適用度**: **A**。婚活領域は派生クエリが極めて多い（「結婚相談所 費用」→「入会金 相場」「成婚料 なし」「20代 女性 安い」「地方 少ない」…）。Qforiaは無料＋Gemini APIキーのみ。工数: 初期セットアップ2h＋主要30キーワード分析10h。
- **リスク・反証**: 【事実】Qforiaの出力は「Geminiに合成クエリを作らせている」だけで、**Googleが実際に発行した合成クエリのログではない**（確率的な近似）。iPullRank自身が "the goal is accuracy, not precision" と断っている（※抜粋経由）。また、Mike King は「レガシーSEOツール各社が『AI検索に出るページはどのクエリでもランクしていない』というレポートを出している」と指摘しており（ https://x.com/iPullRank/status/1989673617097957781 ）、fan-out最適化の効果測定自体が難しい。

---

## 1-05. AIクローラの用途別制御（GPTBot / OAI-SearchBot / ClaudeBot / Claude-SearchBot / Google-Extended / PerplexityBot / CCBot）

- **一言で**: 「学習用クローラ」と「検索用クローラ」はUAが別なので、**学習は拒否しつつAI検索の引用対象には残る**という設定が可能。日本ではrobots.txtを「全部許可」か「全部拒否」の二択で語りがち。
- **海外での出典**:
  - Sites That Grow「Should You Let AI Crawlers Read Your Website? Robots.txt, GPTBot, OAI-SearchBot, and Google-Extended」 https://sitesthatgrow.com/blog/should-you-let-ai-crawlers-read-your-website-robots-txt-gptbot-oai-searchbot-google-extended
  - Cite.sh「Which AI Crawlers to Allow in robots.txt: 2026 List」 https://www.cite.sh/blog/ai-crawler-guide/
  - GEO Scout「OAI-SearchBot, GPTBot, and robots.txt」 https://geoscout.pro/en/blog/oai-searchbot-gptbot-and-robots-txt-for-ai
  - AI Crawler Check「Google-Extended vs Googlebot: The 2026 Difference」 https://aicrawlercheck.com/blog/google-extended-vs-googlebot
  - OpenAI公式ボット一覧 https://platform.openai.com/docs/bots （※本セッションでは取得不可。必ず自分で開くこと）
  - Google公式クローラ一覧 https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers （同上）
- **仕組み／なぜ効くか**: 【事実】用途分離が進んだ結果、GPTBot＝モデル学習用、OAI-SearchBot＝ChatGPTの検索機能でのリンク発見用、ChatGPT-User＝ユーザー操作起因のフェッチ、と役割が分かれている。Google-Extended は Gemini の学習用で、**ブロックしてもGooglebot／Google検索の順位には影響しない**（※抜粋経由、上記各URL）。【事実】robots.txt は RFC 9309 として標準化されているが**あくまで自主的な要請**であり、法的拘束力も技術的ブロック力もない。実強制はサーバー／CDNレイヤで行う。
- **具体手順**:
  1. 現状のrobots.txtに**AIボットの行が1行もない＝全許可**であることを認識する（デフォルトは許可）。
  2. 方針を「学習NG・検索OK」にするなら:
     - `User-agent: GPTBot` → `Disallow: /`
     - `User-agent: OAI-SearchBot` → `Allow: /`
     - `User-agent: ClaudeBot` → `Disallow: /`（学習）／`Claude-SearchBot` → `Allow: /`
     - `User-agent: Google-Extended` → `Disallow: /`（Gemini学習）
     - `User-agent: PerplexityBot` → `Allow: /`（Perplexityは検索兼用）
     - `User-agent: CCBot` → `Disallow: /`（Common Crawl＝各社の学習データ源）
  3. **ただしアフィリエイトメディアは「引用されて流入を得る」のが目的なので、原則は検索系を全許可**。学習系をどうするかだけが判断ポイント。
  4. UA偽装を潰すため、**逆引きDNS（GPTBotなら `*.openai.com`）で検証**してから拒否を適用する。
  5. robots.txtを変えたら1-22（ログ解析）でクロールが実際に変化したか確認する。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「GPTBot OAI-SearchBot 使い分け robots.txt」「Google-Extended ブロック 検索順位」。【推測】「GPTBotをブロックすべきか」という記事は日本語にもあるが、**OAI-SearchBot / Claude-SearchBot という「検索専用UA」の存在と、それを使った非対称設定を明示した日本語記事はほとんど無い**と推定。要検証。
- **noe-match適用度**: **A（即実行可、ただし推奨は「ほぼ全許可」）**。工数0.5h。**引用流入を取りに行く立場なので、検索系（OAI-SearchBot, Claude-SearchBot, PerplexityBot, Google-Extended※）は絶対にブロックしない**。CCBotだけ拒否する、という中庸案が現実的。
- **リスク・反証**: 【事実】Google-Extendedをブロックすると**AI Overviews / AI Modeでの利用可否にも影響し得る**（GeminiとGoogle検索のAI機能の境界が不透明）という指摘があり、収益をAIからの流入に依存する媒体では**ブロックは逆効果**。また robots.txt は強制力がなく、無視するクローラも存在する。「学習を拒否したのに流入も消えた」という失敗が最大のリスク。

---

## 1-06. Cloudflare Pay Per Crawl / AI Crawl Control（クロール課金・デフォルト遮断）

- **一言で**: Cloudflareが2025年7月1日から新規サイトでAIクローラをデフォルト遮断し、「1クロールいくら」で課金するマーケットプレイスを開始した。**クローラの目的（学習／推論／検索）の申告を求める仕組み**も導入された。
- **海外での出典**:
  - Cloudflare プレスリリース（2025-07-01）「Cloudflare Just Changed How AI Crawlers Scrape the Internet-at-Large」 https://www.cloudflare.com/press/press-releases/2025/cloudflare-just-changed-how-ai-crawlers-scrape-the-internet-at-large/
  - Cloudflare Blog「Your site, your rules: new AI traffic options for all customers」 https://blog.cloudflare.com/content-independence-day-ai-options/
  - Nieman Journalism Lab（2025-07） https://www.niemanlab.org/2025/07/cloudflare-will-block-ai-scraping-by-default-and-launches-new-pay-per-crawl-marketplace/
  - Search Engine Land https://searchengineland.com/cloudflare-to-block-ai-crawlers-by-default-with-new-pay-per-crawl-initiative-457708
  - Cloudflare Blog「The crawl before the fall… of referrals」 https://blog.cloudflare.com/ai-search-crawl-refer-ratio-on-radar/
  - Cloudflare Blog「A deeper look at AI crawlers: breaking down traffic by purpose and industry」 https://blog.cloudflare.com/ai-crawler-traffic-by-purpose-and-industry/
- **仕組み／なぜ効くか**: 【事実】オプトアウト（拒否を書かなければ許可）からオプトイン（明示許可がなければ拒否）へのモデル転換。パブリッシャーが単価を設定し、AI企業が受諾するかを選ぶ。【事実】背景にあるのが **crawl-to-refer ratio（何回クロールして何回流入を返すか）** という指標で、Cloudflare Radarが公開している。2025年7月時点で Anthropic の ClaudeBot は 38,065:1、OpenAI は約 1,091:1（※抜粋経由 https://seomator.com/blog/crawl-to-refer-ratio-ai-crawlers-llm-bots ）。2026年7月時点では Mistral 3,389:1、Anthropic 2,237:1（別集計では1,917:1）、OpenAI 217:1 と改善傾向（※抜粋経由 https://nobori.ai/blog/crawl-to-refer-ratio-ai-crawler-traffic-b2b-2026 ）。**この比率を自サイトで自前計算する**のが実務上の応用。
- **具体手順**:
  1. CloudflareのダッシュボードでAI Crawl Controlを開き、**現状が「デフォルト遮断」になっていないか確認**する（新規サイトは遮断がデフォルトになった経緯があるため、意図せず遮断している可能性）。
  2. 検索系クローラ（OAI-SearchBot等）は明示的にAllowにする。
  3. **自サイトのcrawl-to-refer ratio を月次で算出**する：サーバーログのボット別ヒット数 ÷ GA4のそのAI由来リファラ数。
  4. 比率が極端に悪いボット（＝取るだけ取って返さない）だけを個別に遮断候補にする。
  5. Pay Per Crawl は現状ベータかつ大手パブリッシャー向け。**個人メディアは「使う」より「業界の力学を知る」目的**で追う。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「Cloudflare Pay Per Crawl 日本語」「crawl to refer ratio クロール 流入 比率」。【推測】Cloudflareのニュース自体は日本語のIT系メディアで報じられたが、**crawl-to-refer ratio を自サイトのKPIとして計算する運用の話は日本語圏でほぼ見ない**と推定。要検証。
- **noe-match適用度**: **B（条件付き）**。noe-matchがCloudflare配下ならAI Crawl Controlの確認は必須（誤って遮断していたら致命的）。Pay Per Crawl自体は不適。crawl-to-refer比の自前計測は**AI流入のROIを語る唯一の定量指標**なので価値が高い。工数: 確認1h＋月次計測の仕組み3h。
- **リスク・反証**: 【事実】Cloudflareのデフォルト遮断は「知らないうちにAI検索から消えている」事故を生む。アフィリエイト媒体にとっては**遮断＝機会損失**。また crawl-to-refer ratio は「学習用クローラは構造的に流入を返せない」ので、比率が悪い＝悪質とは限らない（Cloudflare自身が用途別に分解している）。

---

## 1-07. AIクローラはJavaScriptを実行しない（No-JS Rendering / SSR前提設計）

- **一言で**: 主要AIクローラはJSファイルを**取得はするが実行しない**。CSRで描画される本文・タブ内テキスト・遅延読み込みのFAQは、AIから見えていない。
- **海外での出典**:
  - Vercel「The rise of the AI crawler」 https://vercel.com/blog/the-rise-of-the-ai-crawler （ChatGPTのフェッチの11.50%、Claudeの23.84%がJSファイルだが実行はされない）
  - Vercel「How AI is changing SEO: lessons from a billion crawler requests」 https://vercel.com/i/how-ai-is-changing-seo
  - Radiant Elephant「Server-Side Rendering for AI Search: No AI Crawler Renders JavaScript」 https://www.radiantelephant.com/server-side-rendering-ai-crawlers/
  - SearchOptimo「Do AI Crawlers Render JavaScript? GPTBot, ClaudeBot, and Perplexity in 2026」 https://searchoptimo.com/blog/do-ai-crawlers-render-javascript
- **仕組み／なぜ効くか**: 【事実】VercelとMERJの共同分析で5億件超のGPTBotフェッチを追跡し、**JS実行の証拠はゼロ**（※抜粋経由）。【事実】2026年6月時点で GPTBot / OAI-SearchBot / ChatGPT-User / ClaudeBot / Claude-SearchBot / PerplexityBot / Meta-ExternalAgent / Bytespider のいずれもJSレンダリングしない。例外は **GeminiがGooglebotのインフラを使うためレンダリングする**点と、AppleBotがブラウザベースでレンダリングする点（※抜粋経由 https://searchoptimo.com/blog/do-ai-crawlers-render-javascript ）。
- **具体手順**:
  1. 主要記事を `curl -A "GPTBot" https://noe-match.com/xxx | wc -c` で取得し、**本文が生HTMLに含まれているか**を目視確認する。
  2. WordPressテーマ／プラグインの「アコーディオンFAQ」「タブ切替」「もっと見る」ボタンの中身が初期HTMLにあるか確認。無ければ**開いた状態のHTMLを出力してCSSで畳む**方式に変更。
  3. 目次・関連記事・内部リンクブロックがJS生成なら**サーバー側出力に変える**（内部リンク設計がAIに伝わらないのは致命的）。
  4. 遅延読み込み画像の `alt` は初期HTMLに残す。
  5. 計算機／無料ツール（noe-matchの施策）は**JSで動くが、その説明文と計算ロジックの解説は静的HTMLで併記**する。ツール自体はAIに読めないが、解説文は読める。
- **日本での言及度**: **低〜中（推定・未検証）**。実行すべき日本語クエリ:「AIクローラー JavaScript 実行しない SSR」「GPTBot JS レンダリング」。【推測】Vercelの調査は日本語でも一部紹介されているが、**「アコーディオンFAQの中身がAIに見えない」という具体的な当てはめは日本語圏でほぼ語られていない**と推定。noe-matchはFAQPageスキーマ全記事実装済みなので、**スキーマだけあって本文がJS内、という最悪パターン**になっていないか確認する価値が高い。要検証。
- **noe-match適用度**: **A**。WordPressテーマ次第だが、確認は1h、修正は3〜8h。**FAQをアコーディオンで畳んでいる場合、本文チャンクが丸ごと消えている可能性がある**ので優先度は最高クラス。
- **リスク・反証**: 【事実】Googlebot経由のインデックス（＝AI Overviews/AI Modeの供給元）はJSをレンダリングするため、**Google系だけを見ていると問題が顕在化しない**。ChatGPT/Perplexity/Claudeでのみ消えるので、GSCでは検知できない。逆に言えば「SSR化しても順位は変わらない」ため効果測定が難しい。

---

## 1-08. AIエージェント向けMarkdown配信 / コンテンツネゴシエーション（Serving Markdown to Agents）

- **一言で**: 同じURLに対し、`Accept: text/markdown` を送ってきたAIエージェントにはHTMLではなくクリーンなMarkdownを返す。または `記事URL + .md` で素のMarkdownを配信する。llms.txtより現実的な「AI可読化」の本命とされ始めている。
- **海外での出典**:
  - Sanity「How to serve content to agents (a field guide)」 https://www.sanity.io/blog/how-to-serve-content-to-agents-a-field-guide
  - Pronovix「How to Serve Markdown to AI Agents Without Breaking Your SEO」 https://pronovix.com/articles/how-serve-markdown-ai-agents-without-breaking-your-seo
  - isagentready「Content Negotiation for AI Agents: Why Sentry Serves Markdown Over HTML」 https://isagentready.com/en/blog/content-negotiation-for-ai-agents-why-sentry-serves-markdown-over-html
  - modpagespeed「Serving markdown to AI crawlers, and synthesizing /llms.txt」 https://modpagespeed.com/blog/serve-markdown-to-ai-crawlers-llms-txt/
  - DeployHQ https://www.deployhq.com/blog/making-your-documentation-ai-friendly-serving-markdown-to-ai-coding-assistants
  - 実装例: Ably docs の PR https://github.com/ably/docs/pull/2862
- **仕組み／なぜ効くか**: 【事実】コンテンツネゴシエーションはHTTPの27年来の標準機能（Acceptヘッダで形式を出し分ける）。ブラウザには `text/html`、エージェントには `text/markdown` を返す。【事実】HTMLの代わりにMarkdownを配信するとトークン消費が60〜80%削減されるという主張がある（※抜粋経由 https://www.ekamoira.com/blog/how-to-serve-markdown-to-ai-crawlers-content-negotiation-token-economics-guide 、**ベンダー主張であり査読なし**）。SentryやAblyなど実運用例がある点がllms.txtとの決定的な違い。
- **具体手順**:
  1. まず `/{slug}.md` 形式の静的Markdown版を生成する（WordPressならREST APIの本文からビルド、またはプラグイン）。
  2. HTML側の `<head>` に `<link rel="alternate" type="text/markdown" href="/{slug}.md">` を置く（発見可能性）。
  3. 余裕があればサーバー／エッジで `Accept: text/markdown` を見て出し分ける。
  4. **`.md` 版には `X-Robots-Tag: noindex` を付ける**（HTML版との重複コンテンツ扱いを避ける）。canonicalはHTML版に向ける。
  5. Markdown版でも「統計＋出典＋日付」（1-03）と自己完結チャンク（1-02）が保たれているか確認。
- **日本での言及度**: **ほぼ無（推定・未検証）**。実行すべき日本語クエリ:「コンテンツネゴシエーション AIエージェント Markdown 配信」「Accept: text/markdown SEO」。【推測】これは**日本語圏でほぼゼロ**の領域と推定。llms.txtの記事は山ほどあるのに、その代替案として海外で議論されているMarkdown配信はほぼ紹介されていない。要検証。
- **noe-match適用度**: **B（条件付き）**。WordPressだと実装がやや重い（プラグイン or テーマfunctions.php）。ただし「重複コンテンツ扱いを避けつつAI可読版を出す」という設計は、258記事の資産を二重活用できる。工数8〜16h。効果は未実証。
- **リスク・反証**: 【事実】**効果を示す実測データが存在しない**。llms.txtと同様「受け手が読みに来るか不明」。Pronovixの記事タイトルが "Without Breaking Your SEO" である通り、**重複コンテンツ／クロールバジェット浪費のリスク**が明示的に議論されている。noindex + canonical を誤ると本体の順位を毀損する。

---

## 1-09. Entity SEO / Wikidata・sameAs・ナレッジパネル掌握

- **一言で**: ブランド名を「文字列」ではなく「エンティティ（Q番号を持つ実体）」としてGoogleのKnowledge GraphとLLMに認識させる。sameAsで外部プロフィールを束ね、Wikidataを正準ターゲットにする。
- **海外での出典**:
  - SEO Strategy Ltd「Wikidata for SEO: Wikipedia's Smarter Sibling That Powers Google, ChatGPT & AI Search」 https://www.seostrategy.co.uk/wikidata-seo/
  - Stackmatix「Organization Schema Markup: Complete Guide to Knowledge Graph & Entity SEO (2026)」 https://www.stackmatix.com/blog/organization-schema-knowledge-graph
  - OrganiKPI「Schema sameAs: How Entity Disambiguation Works」 https://organikpi.com/blog/technical-seo/schema-sameas-entity-disambiguation-ai-citations/
  - Search Engine Land「Entity-first SEO: How to align content with Google's Knowledge Graph」 https://searchengineland.com/guide/entity-first-content-optimization
  - Search Engine Land「How to use entities in schema to improve Google's understanding of your content」 https://searchengineland.com/entities-seo-schema-google-content-428602
- **仕組み／なぜ効くか**: 【事実】WikidataはQ番号（アイテム）とP番号（プロパティ）で事実を保持する機械可読なナレッジベースで、GoogleのKnowledge Graphが強く依拠しているため、Knowledge PanelとAI回答への直接入力になる（※抜粋経由、上記各URL）。**sameAsは「このサイトのエンティティは、Wikidata／LinkedIn／X／Crunchbaseのこれと同一である」と明示する宣言**であり、AIが複数ソースを三角測量してブランドを同定できるようにする。
- **具体手順**:
  1. `Organization` スキーマをトップページに設置し、`name` / `url` / `logo` / `description` / `foundingDate` / `sameAs[]` を埋める。
  2. `sameAs` に**実在するプロフィールだけ**を列挙（X、note、YouTube、Instagram、必要ならGoogleビジネスプロフィール）。存在しないURLを書くと逆効果。
  3. サイト内に**「エンティティホーム」＝会社／運営者情報ページ**を1枚作り、そこを `Organization` の `url` にする。
  4. Wikidata登録は**特筆性（notability）の基準がある**ため、個人メディアではまず外部の言及（メディア掲載、著書、公的な引用）を積んでから検討する。
  5. `WebSite` スキーマの `publisher` から `Organization` を `@id` 参照でリンクし、**全ページのスキーマを1つのエンティティグラフに接続**する。
- **日本での言及度**: **中（推定・未検証）**。実行すべき日本語クエリ:「Wikidata SEO 登録 ナレッジパネル」「sameAs エンティティ 名寄せ」。【推測】「エンティティSEO」「sameAs」という語は日本語のSEO記事にも出るが、**Wikidataへの能動的登録／編集を実務手順として書いた日本語記事は少なく、特に「AI引用のための名寄せ」という文脈はほぼ無い**と推定。要検証。
- **noe-match適用度**: **B（条件付き）**。Organization + sameAs + エンティティホームは即実行可（工数3h、A相当）。**Wikidata登録は特筆性基準に引っかかる可能性が高くC**。ドメイン開設2026年6月で外部言及がまだ薄いため、先に1-11（ブランド言及）を積むのが順序。
- **リスク・反証**: 【事実】Wikidataは**特筆性のないエンティティは削除される**（自己宣伝目的の登録は荒らし扱い）。個人アフィリエイトメディアの登録は削除リスクが高く、コミュニティとの摩擦を生む。また sameAs を書いてもGoogleがKnowledge Panelを出す保証は一切ない。

---

## 1-10. ProfilePage / Person スキーマによる著者エンティティ構築

- **一言で**: 著者を「文字列の名前」ではなく sameAs で外部に接続された Person エンティティとして構造化し、ProfilePage で著者ページ自体をマークアップする。AIが「誰が書いたか」を機械的に同定できるようにする。
- **海外での出典**:
  - Schema Engine AI「ProfilePage Schema for Author, Creator, and Team Pages」 https://schemaengineai.com/blog/profilepage-schema-markup/
  - LeadsuiteNow「Person Schema and Author Authority: Signal Expertise to AI Systems」 https://leadsuitenow.com/blog/person-schema-author-authority-ai
  - Aubrey Yung「ProfilePage Schema Markup」 https://aubreyyung.com/profilepage-schema/
  - Customer Impact「Author schema for E-E-A-T in AI」 https://www.customerimpact.be/en/blog/author-schema-markup/
- **仕組み／なぜ効くか**: 【事実】ProfilePage は schema.org で定義された、著者バイオ／クリエイタープロフィール専用のページ型。**エンティティ曖昧性解消（同名人物の識別）**が主目的で、sameAs付きのPersonと組み合わせることでAIが正しく帰属できる（※抜粋経由、上記各URL）。GoogleのQuality Rater GuidelinesがE-E-A-Tを「識別可能で資格のある著者」に紐づけているのと同じ信号を、AIエンジンも人物同定に使っている、という論建て。
- **具体手順**:
  1. `/author/{name}/` に著者ページを作り、`@type: ProfilePage` + `mainEntity: {@type: Person}` でマークアップ。
  2. Person に `name` / `jobTitle` / `description` / `knowsAbout[]`（婚活、結婚相談所、結婚式費用…）/ `sameAs[]`（X、note、LinkedIn）/ `image` を入れる。
  3. **各記事の `author` を文字列ではなく `{"@id": "https://noe-match.com/author/xxx/#person"}` の参照にする**（ここが日本で最も抜けている点）。
  4. `knowsAbout` に扱うトピックのエンティティを列挙し、トピカルオーソリティと接続する。
  5. 著者名で検索したときに自サイトの著者ページが1位に来る状態を作る（ブランドSERP掌握の人物版）。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「ProfilePage スキーマ 著者 構造化データ」「Person schema knowsAbout 著者」。【推測】「著者情報を書こう（E-E-A-T）」という記事は日本語に大量にあるが、**ProfilePage型・`@id` 参照によるエンティティ結合・knowsAbout の実装まで書いた日本語記事はほぼ無い**と推定。要検証。
- **noe-match適用度**: **A**。個人運営なので著者は1人＝実装がシンプル。**noteでの活動（既に実施中の寄生SEO）を sameAs で本体サイトに接続できる**のが大きい。工数4〜6h。
- **リスク・反証**: 【事実】著者スキーマは**リッチリザルトを生まない**（表示上の見返りゼロ）。効果測定が事実上不可能で、「やって損はない」レベルの施策。匿名運営を続けたい場合はプライバシーとのトレードオフ。また虚偽の経歴・資格を書くとYMYL領域で重大なリスク。

---

## 1-11. ブランド言及（Unlinked Mentions）優先の外部施策

- **一言で**: AI可視性との相関はバックリンクではなく**ブランドのウェブ言及**が圧倒的に強い、というAhrefsの75,000ブランド調査。リンクを取りに行くのではなく「名前を出してもらう」ことを目標にする。
- **海外での出典**:
  - Ahrefs「An Analysis of AI Overview Brand Visibility Factors (75K Brands Studied)」 https://ahrefs.com/blog/ai-overview-brand-correlation/
  - Ahrefs「AI Brand Visibility Correlations」 https://ahrefs.com/blog/ai-brand-visibility-correlations
  - Chris Long（LinkedIn）による解説 https://www.linkedin.com/posts/chris-long-marketing_seo-data-study-an-analysis-from-ahrefs-found-activity-7334185782213033986-NI0k
  - Blck Alpaca「Brand Mentions vs. Backlinks: The Ahrefs 75K Brand Study」 https://blckalpaca.at/en/knowledge-base/seo-geo/geo-generative-engine-optimization/brand-mentions-vs-backlinks-the-ahrefs-75k-brand-study
- **仕組み／なぜ効くか**: 【事実】Ahrefsの調査で、AI Overviewsでのブランド可視性との相関はブランドのウェブ言及が **0.664**、ブランドアンカー **0.527**、ブランド検索ボリューム **0.392** に対し、**バックリンクは 0.218**、コンテンツ量は **0.194**（Spearman相関、※抜粋経由 https://ahrefs.com/blog/ai-overview-brand-correlation/ ）。【事実】後続の分析ではYouTube上の言及（動画タイトル・字幕・説明文にブランド名が出る）が **0.737** で単独最強とされる（※抜粋経由 https://ahrefs.com/blog/ai-brand-visibility-correlations ）。
- **具体手順**:
  1. **リンクなしでいいので媒体名を出してもらう**PR設計にする（プレスリリース、調査レポートの配布、取材協力）。
  2. noe-matchの一次データ（自治体データ43件）を**「Noe結婚設計室調べ」という表記込みで引用させる**フォーマットで配布する。引用ルールをデータページに明記。
  3. YouTube上の言及を増やす（自チャンネル運営、または婚活系YouTuberへのデータ提供）。**字幕・概要欄にサイト名が入るだけで信号になる**。
  4. 指名検索（ブランド検索ボリューム）を増やす施策をセットにする＝SNS・noteでのブランド名の反復露出。
  5. Google アラート／Ahrefs Brand Radar 等で**未リンク言及をモニタし、リンク化交渉はしない**（言及自体が目的）。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「ブランド言及 AI可視性 相関 バックリンク Ahrefs」「サイテーション LLMO 相関係数」。【推測】日本語LLMO記事の多くが「サイテーションが重要」とは書くが、**0.664 vs 0.218 という具体的な相関係数と、YouTube言及0.737という順位づけを引いている日本語記事はほぼ無い**と推定。要検証。
- **noe-match適用度**: **A（ただし中長期）**。データバンク施策と完全に噛み合う。**「引用してもらう用のデータページ＋引用表記ルール」を作るのは工数4h**で、以降はストック資産。ドメイン開設3ヶ月で外部言及が薄いのでリターンまで時間がかかる。
- **リスク・反証**: 【事実】**これは相関であって因果ではない**。「有名なブランドは言及も多いしAIにも出る」という交絡を排除できていない。Ahrefs自身が相関研究として提示している。ブランド言及を人工的に増やす施策（スパム的な言及ばら撒き）は効かない可能性が高く、むしろリスク。

---

## 1-12. サードパーティ・リスティクル掲載（Listicle Placement / Off-site GEO）

- **一言で**: ChatGPTの引用元の約半分が「best of / おすすめ◯選」型のリスティクル。自社サイトを磨くより**他人のリスティクルに載る**ほうが引用への近道、という戦術。
- **海外での出典**:
  - Ahrefs「Do Self-Promotional "Best" Lists Boost ChatGPT Visibility? Study of 26,283 Source URLs」 https://ahrefs.com/blog/best-lists-research/
  - Link Building Journal「Listicle Placements: The New Most Powerful AI Citation Tactic in 2026」 https://linkbuildingjournal.co.uk/listicle-placements-ai-citation-tactic/
  - Alhena「GEO Citation Strategy: 7 Off-Site Sources for AI Recommendations」 https://alhena.ai/blog/geo-citation-strategy-off-site-sources-ai-recommendations/
  - Stradiji「Off-Page GEO: Win Citations, Not Backlinks」 https://www.stradiji.com/off-page-geo-win-citations-not-backlinks/
- **仕組み／なぜ効くか**: 【事実】Ahrefsは750検索語にわたる26,283件のソースURLを分析し、「best X」型リスティクル（自社を1位に置いた自作リストを含む）がChatGPTのソースとして最も目立つページタイプだったと報告（ https://ahrefs.com/blog/best-lists-research/ ）。**引用の43.8%〜44%がリスティクルだった**という数字が二次ソースで広く流通している（※抜粋経由 https://linkbuildingjournal.co.uk/listicle-placements-ai-citation-tactic/ 、**原典で必ず確認すること**）。AIは「複数ソースの合意（consensus）」を作るため、比較表形式の第三者評価を好む。
- **具体手順**:
  1. ChatGPT/Perplexityに「◯◯のおすすめは？」と実際に聞き、**回答に出てくる引用元リスティクルをリスト化**する（それが既に引用パイプラインに乗っている媒体）。
  2. そのリスティクル運営者に、掲載理由になる材料（独自データ、他にない切り口、アフィリ提携）を添えて打診する。
  3. 同時に、**自サイト側でも「◯◯ 比較 2026年版」型のリスティクルを作る**。更新日を明示し、実際に更新する（放置リストは引用率が低いとされる）。
  4. 比較表は `<table>` で、各行に固有名詞・価格・条件を入れる（チャンク単体で意味が通る）。
  5. Bingにインデックスされているか確認（1-15）。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「ChatGPT 引用 リスティクル おすすめ◯選 43%」「AI引用 比較記事 掲載 戦略」。【推測】「比較記事が強い」は日本のアフィリ界隈でも常識だが、**「他人のリスティクルに載りに行く（＝掲載営業）」を AI 引用獲得の主戦術として位置づける議論は日本語圏でほぼ無い**と推定。要検証。
- **noe-match適用度**: **A（自作リスティクル）／B（他媒体への掲載営業）**。婚活・結婚相談所領域は比較記事の激戦区で大手が強いが、**「空白理論」と組み合わせて大手が作らない粒度（例: 地方自治体別の結婚支援制度の比較）でリスティクルを作る**のが噛み合う。工数: 1本8〜12h。
- **リスク・反証**: 【事実】Ahrefsの記事タイトル自体が「自己宣伝的なbestリストは効くのか？」という問いであり、**自作リストで自社を1位にする行為が実際に効くのか、それとも短命なのかは結論が出ていない**。【事実】水増しリスティクル・合成レビューは「GEOスパム」としてGoogle/Microsoft双方が対処対象にしていると複数ソースが指摘（※抜粋経由 https://alhena.ai/blog/geo-citation-strategy-off-site-sources-ai-recommendations/ ）。

---

## 1-13. エンジン別の引用元プロファイルに合わせた出し分け

- **一言で**: ChatGPT・Perplexity・Google AI Overviews は**引用するドメインの傾向がまったく違う**。「AI対策」を一本化せず、狙うエンジンごとに置き場所を変える。
- **海外での出典**:
  - Semrush「The Most-Cited Domains in AI: A 3-Month Study」 https://www.semrush.com/blog/most-cited-domains-ai/
  - Semrush「AI Mode Comparison Study」 https://semrush.com/blog/ai-mode-comparison-study
  - Frase「Which AI Engines Cite Which Sources? (2026 Data)」 https://www.frase.io/blog/which-ai-engines-cite-which-sources
  - Contently「Top 10 Sources LLMs Cite Most in 2026」 https://contently.com/2026/04/29/top-sources-llms-cite/
  - Everything PR「The 50 Websites AI Engines Cite Most in 2026」 https://everything-pr.com/ai-platform-citation-source-index-2026
- **仕組み／なぜ効くか**: 【事実】Semrushの325,000プロンプト調査で、LinkedInはChatGPT Search回答の14.3%、Google AI Modeの13.5%、Perplexityの5.3%で引用され、全体ではRedditに次ぐ2位（※抜粋経由 https://www.semrush.com/blog/most-cited-domains-ai/ ）。【事実】ChatGPTはWikipedia/百科事典系が上位引用の47.9%、PerplexityはRedditが46.7%、Google AI OverviewsはYouTube等マルチモーダルが23.3%（※抜粋経由 https://www.frase.io/blog/which-ai-engines-cite-which-sources ）。【事実】ChatGPTとPerplexityで**共通して引用されるドメインはわずか11%**（※抜粋経由 https://authoritytech.io/curated/ai-citation-11-percent-platform-overlap-per-engine-audit-2026 ）。【事実】Google AI OverviewsとAI Modeですら、同じURLを引用するのは13.7%しかない（※抜粋経由 https://semrush.com/blog/ai-mode-comparison-study ）。
- **具体手順**:
  1. **どのエンジンからの流入を取りたいかを先に決める**（日本の婚活領域なら実質 ChatGPT >> Gemini/AI Overviews > Perplexity）。
  2. ChatGPT狙い → Bingインデックス（1-15）＋Wikipedia的な定義記事＋リスティクル掲載。
  3. Google AI Overviews狙い → 従来SEOの順位＋YouTube／画像などマルチモーダル。
  4. Perplexity狙い → UGC（海外はReddit、**日本語ではYahoo!知恵袋・はてな・note・X**が対応物になり得る／【推測】未検証）。
  5. 自分のブランド名・主要キーワードで**3エンジン全部を手で叩き、引用元ドメインを台帳化**する（noe-matchは既にAI Overviews出現の実測台帳を持っているので、そこにエンジン列を追加するだけ）。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「ChatGPT Perplexity AI Overviews 引用元 ドメイン 違い」「エンジン別 引用 傾向 Reddit Wikipedia」。【推測】「AIによって引用元が違う」という総論は日本語にもあるが、**11%オーバーラップ・13.7%といった具体データを引いて出し分けを設計する議論はほぼ無い**と推定。要検証。
- **noe-match適用度**: **A**。既存のAI Overviews台帳を拡張するだけ。工数: 台帳拡張3h＋月次運用2h。
- **リスク・反証**: 【事実】これらの調査は**英語圏のプロンプトが中心**で、日本語プロンプトでの引用元分布はまったく別の可能性が高い（日本語ではRedditがほぼ出ない）。海外データをそのまま日本語市場に当てはめるのは危険。**noe-match自身の実測台帳のほうが信頼できる**。

---

## 1-14. 「取得されるが引用されない」問題への対処（Retrieval ≠ Citation）

- **一言で**: ChatGPTは取得したURLの約半分しか引用しない。**取得プールに入ること**と**引用されること**は別の最適化問題として分けて考える。
- **海外での出典**:
  - Ahrefs「Why ChatGPT Cites One Page Over Another (Study of 1.4M Prompts)」 https://ahrefs.com/blog/why-chatgpt-cites-pages/
  - Search Engine Journal「ChatGPT Often Retrieves But Rarely Cites Reddit Pages, Data Shows」 https://www.searchenginejournal.com/chatgpt-often-retrieves-but-rarely-cites-reddit-pages-data-shows/572243/
  - The Visibility Report「Ahrefs Studied 1.4M ChatGPT Prompts」 https://thevisibilityreport.com/posts/visibility-13-ahrefs-studied-1-4m-chatgpt-prompts-here-s-why-some-pages-get-cited-and-others-don-t
  - CXL「Why your pages aren't surfacing in ChatGPT citations」 https://cxl.com/blog/chatgpt-citations-ai-search-optimization/
- **仕組み／なぜ効くか**: 【事実】Ahrefsの1.4Mプロンプト調査によると、**取得されたアイテムのうち引用に至るのは49.98%**。**引用されたURLの88%は検索経由**で入ってきている（＝検索順位が取得プールへの入場券）。Redditは独自の取得チャネルを持ち1,600万件超取得されているが、**引用率はわずか1.93%**で、非引用URLの67.8%がReddit（※抜粋経由 https://ahrefs.com/blog/why-chatgpt-cites-pages/ ）。つまりRedditは「文脈理解の材料」として使われ、クレジットは与えられていない。【事実】引用可否の最大要因は**タイトル／URLとfan-outクエリのコサイン類似度**、記述的スラッグの引用率は89.78%（非記述的は81.11%）。
- **具体手順**:
  1. **取得プール入場のためのSEO**（従来の順位取り）を捨てない。88%が検索経由という事実がある以上、GEOは従来SEOの上に乗る。
  2. **タイトルを「広い語」ではなく「狭い派生クエリ」に寄せる**（例:「結婚相談所とは」→「結婚相談所の成婚料は平均いくらか【2026年】」）。
  3. **URLスラッグを記述的にする**（`/p=1234` や `/blog/post-1` は捨てる。`/konkatsu/seikon-ryo-heikin/` のように内容が読める形に）。
  4. 「取得されているのに引用されない」ページを特定するため、**サーバーログでOAI-SearchBot/ChatGPT-Userが来ているURL** と **実際にChatGPTが引用したURL** を突き合わせる。
  5. 引用されないページには「引用に足る具体（数値・出典・日付）」（1-03）が欠けている可能性が高い。
- **日本での言及度**: **ほぼ無（推定・未検証）**。実行すべき日本語クエリ:「retrieval citation 取得 引用 ChatGPT 半分」「Ahrefs 1.4M プロンプト 調査 日本語」。【推測】この「取得と引用の分離」という枠組み自体が日本語圏でほぼ語られていないと推定。noteに英語記事の翻訳紹介が1本ある程度（ https://note.com/trex_ai/n/nfc70a07149bc?hl=en ）。要検証。
- **noe-match適用度**: **A**。特に**URLスラッグの記述性チェック**は既存258記事に対して機械的に監査可能。工数: 監査2h＋リダイレクト付きスラッグ変更（危険なので新規記事のみ適用を推奨）。
- **リスク・反証**: 【事実】スラッグ変更はリダイレクト事故で順位を失うリスクが大きい。既存記事は触らず新規記事のルールにするのが安全。またコサイン類似度の話は**Ahrefsが自社データで観測した相関**であり、OpenAIの内部仕様の開示ではない。

---

## 1-15. Bing インデックス確保 / IndexNow（ChatGPT引用の前提条件）

- **一言で**: ChatGPTの検索はBingインデックスを土台にしているため、**Bingに入っていないページはChatGPTに引用されない**。日本のSEOはGoogle一辺倒でBing Webmaster Toolsを放置しがち。
- **海外での出典**:
  - Conbersa「Bing Indexing Optimization: Why 87% of ChatGPT Citations Come From Bing」 https://www.conbersa.ai/learn/bing-indexing-optimization-for-chatgpt （Seer Interactive の分析: SearchGPT引用の87%がBing上位結果と一致）
  - Stackmatix「Bing Webmaster Tools for ChatGPT Optimization: Complete Guide (2026)」 https://www.stackmatix.com/blog/bing-webmaster-tools-chatgpt
  - Brand Cited「Why ChatGPT Citations Come From Bing, Not Google」 https://www.brandcited.ai/blog/chatgpt-citations-bing-not-google
  - Lemniscate Growth「How ChatGPT Search Works: Sources, Bing, and Citations」 https://lemniscategrowth.com/blogs/how-chatgpt-search-works.html
  - Pressonify「Does Google Support IndexNow in 2026? No — Here's Who Does」 https://pressonify.ai/blog/indexnow-instant-indexing-press-releases-2026
- **仕組み／なぜ効くか**: 【事実】ChatGPTのweb検索はBingのインデックスを使い、Googleでは順位が付いてもBing未インデックスならChatGPT引用に出ない（※抜粋経由）。【事実】ただし2026年時点では**Bingが唯一のソースではなくなっており**、OpenAIは自前クローラと自前インデックスを構築し、サードパーティ検索プロバイダも併用している（※抜粋経由 https://lemniscategrowth.com/blogs/how-chatgpt-search-works.html ）。【事実】IndexNow は Bing / Yandex / Naver 等が対応、**Googleは非対応**。BingインデックスがChatGPT・Copilot・DuckDuckGoを支えるため、IndexNowは間接的にAI引用を早める。
- **具体手順**:
  1. **Bing Webmaster Tools に登録**する（GSCからインポート可能）。noe-matchが未登録なら最優先。
  2. サイトマップを送信し、**インデックス済みページ数がGSCと乖離していないか**確認する。
  3. IndexNow を有効化（WordPressなら Yoast / Rank Math / Bing公式プラグインでワンクリック）。新規・更新記事を即通知。
  4. Bing側の「Site Explorer」「URL Inspection」で主要記事の実インデックス状況を個別確認。
  5. Bing上での順位を主要キーワードで手動チェック（Bingの上位＝ChatGPT引用候補プール）。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「Bing インデックス ChatGPT 引用 条件」「IndexNow 設定 WordPress AI」。【推測】「Bingも登録しよう」という記事は日本語にもあるが、**「ChatGPT引用の前提条件としてのBing」という因果でBing Webmaster Toolsを優先施策に置く議論は薄い**と推定。要検証。
- **noe-match適用度**: **A（最優先クラス）**。工数1〜2h、コストゼロ、リスクゼロ、効果の理屈が最も明快。**ドメイン開設2026年6月＝Bingのインデックスが遅れている可能性が高い**ので効果が出やすい。
- **リスク・反証**: 【事実】OpenAIが自前インデックスへ移行しつつあるため、**「Bing＝ChatGPTの唯一の門」という前提は2026年時点で崩れ始めている**。87%という数字も Seer Interactive の一調査（時期・サンプル未確認）。ただし施策コストがほぼゼロなので、前提が崩れても損失はない。

---

## 1-16. utm_source=chatgpt.com とAIリファラのGA4計測

- **一言で**: ChatGPTは引用リンクに `utm_source=chatgpt.com` を自動付与する。GA4でカスタムチャネルグループを作り、AI流入を独立チャネルとして可視化する。ただし**取りこぼしの構造**を理解しないと過小評価する。
- **海外での出典**:
  - Swydo「The Agency Guide to Tracking AI Traffic in GA4 — Setup, Regex Patterns, and More」 https://www.swydo.com/blog/track-ai-traffic-in-ga4/
  - Authority Tech「Track ChatGPT, Perplexity & Gemini Traffic in GA4 (2026)」 https://authoritytech.io/blog/ai-traffic-attribution-how-to-track-chatgpt-perplexity-gemini
  - Nadia Mohamed「Track AI Referral Traffic in GA4: Setup, Benchmarks & What It Means」 https://nadiamohamed.me/insights/track-ai-referral-traffic/
  - Conversios https://www.conversios.io/blog/track-ai-referral-traffic-from-chatgpt-in-ga4/
- **仕組み／なぜ効くか**: 【事実】ChatGPTは2025年から引用リンクに `utm_source=chatgpt.com` を付けており、GA4は追加設定なしでも取得できる（※抜粋経由）。【事実】AIリファラ全体に占める比率はChatGPTが約87%、Perplexity約4%、Claude約2%、Copilot約2%（※抜粋経由 https://authoritytech.io/blog/ai-traffic-attribution-how-to-track-chatgpt-perplexity-gemini 、**調査主体と期間は原典で要確認**）。【事実】取りこぼしの構造は2つ:(a) ChatGPTが `utm_source` だけ送って `utm_medium` を送らないため GA4 で "Unassigned" に落ちる、(b) **ChatGPTモバイルアプリやPerplexityのアプリ内ブラウザは referrer を送らない**ためダイレクト扱いになる。
- **具体手順**:
  1. GA4の管理 → チャネルグループ → カスタムチャネルグループを作成し、`AI Referrals` チャネルを追加。
  2. 条件: セッションのソースが次の正規表現に一致 — `chatgpt\.com|chat\.openai\.com|openai\.com|perplexity\.ai|claude\.ai|gemini\.google\.com|copilot\.microsoft\.com|bing\.com/chat|deepseek\.com|grok\.com|meta\.ai|you\.com`
  3. **このチャネルを Referral より優先順位で上に置く**（順序が重要）。
  4. "Unassigned" セッションを別途モニタし、AI由来の取りこぼしを推定する。
  5. **ダイレクト流入の急増**をAI由来の代理指標として見る（アプリ内ブラウザ分）。
  6. 1-17（GSCの生成AIレポート）とクロスチェックする。
- **日本での言及度**: **中（推定・未検証）**。実行すべき日本語クエリ:「utm_source=chatgpt.com GA4 計測」「AI流入 チャネルグループ 正規表現」。【推測】設定手順の日本語記事はそこそこ存在すると推定。ただし**「Unassignedへの落下」「アプリ内ブラウザのreferrer欠落でダイレクトに紛れる」という取りこぼし構造まで書いた日本語記事は少ない**と推定。要検証。
- **noe-match適用度**: **A**。工数1h。**AI流入がどれだけあるかを知らないまま施策を打つのが最大の無駄**なので、全施策の前提として最初にやる。
- **リスク・反証**: 【事実】上記の取りこぼしにより、**GA4のAIチャネルは実際のAI流入を系統的に過小評価する**。この数字を根拠に「AIからの流入は少ないから対策不要」と判断するのが典型的な失敗。また `utm_source` の付与仕様はOpenAI側の都合でいつでも変わる。

---

## 1-17. Search Console 生成AIパフォーマンスレポートの読み方

- **一言で**: AI Modeのデータは2025年6月16日から通常のパフォーマンスレポート合計に**混ぜ込まれ**、2026年6月3日に生成AI専用ビューが追加された（ただしインプレッションのみでクリックは含まれない）。この構造を知らないとデータを誤読する。
- **海外での出典**:
  - Search Engine Land「Google AI Mode traffic data comes to Search Console」 https://searchengineland.com/google-ai-mode-traffic-data-search-console-457076
  - Brodie Clark「AI Mode Tracking in Google Search Console Confirmed [SEO Experiment]」 https://brodieclark.com/ai-mode-google-search-console/
  - WebFX「What Marketers Need to Know About the New Google Search Console AI Performance Report (+ Opt-Out Control)」 https://www.webfx.com/blog/ai/google-search-console-ai-performance-report/
  - Smart Team「Search Console: New Generative AI Report」 https://smart-team.io/en/search-console-performance-report-generative-ia/
- **仕組み／なぜ効くか**: 【事実】2025年6月16日以降、AI Modeのクリック・インプレッション・掲載順位はSearch Consoleのパフォーマンス合計に**含まれる**が、独立セグメントとしては分離されていなかった（※抜粋経由）。【事実】2026年6月3日、GoogleはSearch Consoleに生成AIパフォーマンスレポートを追加し、AI Overviews / AI Mode / Discover のインプレッションデータを提供開始。**クリックは含まれない**（※抜粋経由 https://www.webfx.com/blog/ai/google-search-console-ai-performance-report/ ）。表示されるのは「AI Mode/AI Overviewsに自サイトURLが何回出たか」「どのURLが出たか」「国」「デバイス」。
- **具体手順**:
  1. Search Consoleの生成AIレポートを開き、**AI Overviews/AI Modeに出ているURLの一覧を取得**する。
  2. これを**noe-matchの既存「AI Overviews出現実測台帳」と突合**する（手動観測とGoogle公式データの誤差を測る）。
  3. **インプレッションはあるがクリックが伸びていないURL**を特定 → 引用はされているが流入に繋がっていない＝タイトル/スニペット改善の対象。
  4. 通常のパフォーマンスレポートの数字は「AI Mode込み」であることを前提に、前年比較・順位変動を解釈する。
  5. オプトアウト設定の有無を確認する（レポートにはオプトアウト制御が付随する旨の記載あり ※要原典確認）。
- **日本での言及度**: **中（推定・未検証）**。実行すべき日本語クエリ:「Search Console 生成AI パフォーマンスレポート AI Mode」「AIモード サーチコンソール 含まれる」。【推測】ニュースとしては日本語でも報じられるが、**「合計に混ざっている」ことによる前年比較の誤読リスクを指摘した日本語記事は少ない**と推定。要検証。
- **noe-match適用度**: **A**。無料・工数1h。既存台帳との突合は noe-match の独自資産を強化する。
- **リスク・反証**: 【事実】**クリックデータがない**ため、AI Overviews掲載が実流入にどれだけ寄与しているかはGSCだけでは分からない。また、データが通常レポートに混入している期間があるため、**2025年6月以前との時系列比較は不正確になる**。

---

## 1-18. AIボットのサーバーログ解析（Log File Analysis for AI Crawlers）

- **一言で**: AIクローラはJSを実行しないためGA4に一切現れない。**サーバーログだけが唯一のグラウンドトゥルース**。どのAIボットがどのURLを何回取りに来たかをKPI化する。
- **海外での出典**:
  - Screaming Frog「How to Monitor AI Bots in the Log File Analyser」 https://www.screamingfrog.co.uk/log-file-analyser/tutorials/monitor-ai-bots-in-the-log-file-analyser/
  - Similarweb「Log File Analysis: Track AI Bots & Fix Crawl Gaps」 https://www.similarweb.com/blog/marketing/geo/log-file-analysis/
  - Passion Digital「Tracking LLMs Bots on Your Site using Log File Analysis」 https://passion.digital/blog/tracking-llms-bots-on-your-site-using-log-file-analysis/
  - Wislr「48 Days of Server Logs Expose What GPTBot, ChatGPT, ClaudeBot, and 16 Others Are Doing」 https://www.wislr.com/articles/ai-bot-behavior-log-analysis/
  - CiteFlow「Monitor AI Crawler Server Logs: GPTBot, ClaudeBot, More」 https://www.citeflow.io/blog/monitor-ai-crawler-server-logs
- **仕組み／なぜ効くか**: 【事実】AIクローラは従来型アナリティクスのJSを実行しないため、**ログ以外にAIの注意量を測る手段がない**（※抜粋経由 https://www.menra.ai/glossary/log-file-analysis ）。【事実】GPTBotは2024年5月→2025年5月で**+305%**、ChatGPT-Userは同期間で**+2,825%**のリクエスト増（※抜粋経由 https://www.similarweb.com/blog/marketing/geo/log-file-analysis/ 、原典要確認）。【事実】UA偽装があるため、**逆引きDNSで公表IPレンジと照合**しないと数字が水増しされる。
- **具体手順**:
  1. レンタルサーバ／Cloudflareのアクセスログを月次で取得できる状態にする（多くの共用サーバは生ログをDL可能）。
  2. UAトークンで分類: `GPTBot` / `OAI-SearchBot` / `ChatGPT-User` / `ClaudeBot` / `Claude-SearchBot` / `PerplexityBot` / `Google-Extended` / `CCBot` / `Bytespider` / `Meta-ExternalAgent`。
  3. **逆引きDNS検証**（GPTBot → `*.openai.com` に解決するか）でスプーフィングを除外。
  4. KPI化する指標: (a) ボット別ヒット数、(b) ユニークURL数（深いページまで到達しているか、トップで跳ね返っていないか）、(c) ステータスコード分布、(d) **crawl-to-refer 比**（1-06）。
  5. ツール: Screaming Frog Log File Analyser（有料・単発監査向き）、GoAccess（リアルタイム・無料）、BigQuery/Athena（CDNログの大量処理）。
  6. **robots.txt を変更したら1ヶ月後にログで実際に変化したか確認**する（宣言と実挙動の乖離チェック）。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「GPTBot ログ解析 アクセスログ AIボット」「AIクローラー 生ログ 分析 逆引き」。【推測】ログ解析自体は日本のテクニカルSEOで語られるが、**AIボット別のKPI化・逆引き検証・crawl-to-refer比という運用まで書いた日本語記事はほぼ無い**と推定。要検証。
- **noe-match適用度**: **B（条件付き）**。共用サーバでログが取れるかに依存。取れるなら**GA4に映らないAIの動きを唯一見られる手段**として価値が高い。GoAccessなら無料。工数: 初期4h＋月次1h。
- **リスク・反証**: 【事実】ログにボットが来ていても、**引用されるかは別問題**（1-14の retrieval ≠ citation）。「GPTBotが月1万ヒット」は成果指標ではなく先行指標にすぎない。またログのボリュームが大きく、個人運営には運用負荷が重い。

---

## 1-19. プロンプトリサーチ（Prompt Research / Conversational Query Research）

- **一言で**: キーワードではなく「実際に人がAIに打ち込む長い自然文プロンプト」を収集・分類する調査手法。検索ボリュームの代わりに、Reddit・Q&A・問い合わせ・営業トークの生データから拾う。
- **海外での出典**:
  - Search Engine Land「Prompt research: The next layer of SEO and GEO strategy」 https://searchengineland.com/prompt-research-seo-geo-strategy-471399
  - Similarweb「How to do prompt research for AI SEO」 https://aisearch.similarweb.com/blog/prompt-research/
  - WordStream「How to Do Prompt-Based Keyword Research to Show Up Better in AI Results」 https://www.wordstream.com/blog/prompt-based-keyword-research
  - Backlinko「Prompt Tracking: How to Find (and Fix) Your AI Visibility Gaps」 https://backlinko.com/llm-prompt-tracking
  - Pi Datametrics「AI Prompt and Keyword Research」 https://pi-datametrics.com/platform/ai-prompt-keyword-research-tool/
- **仕組み／なぜ効くか**: 【事実】プロンプトリサーチは短いキーワードから外に広げるのではなく、**会話的な質問文から始めてAIが生成するサブクエリに分解し、自コンテンツが引用され得る場所をマッピングする**手法（※抜粋経由 https://www.relevantaudience.com/ai/seo-and-geo-guide-to-prompt-research-for-ai-search/ ）。【事実】データソースはキーワードツールの検索ボリュームではなく、**AIチャットログ、Reddit/Quoraなどのコミュニティ、カスタマーサポートのチケット、営業通話の書き起こし、SNS**。オートコンプリートに整形される前の「生の言い回し」が取れる点が肝。【事実】さらにマルチターン（追加質問で絞り込む流れ）をモデル化する。
- **具体手順**:
  1. 婚活領域の**生の言い回し**を収集する: Yahoo!知恵袋、X、note のコメント、掲示板、自分への問い合わせ。「35歳 女性 婚活 何から始めれば」のような文をそのまま集める。
  2. プロンプトを**タイプ分類**する: 状況説明型／比較型／可否判断型／手順型／不安相談型。
  3. 各プロンプトを実際に ChatGPT / Gemini に投げ、**回答に自サイトが出るか、出ないなら誰が出ているか**を記録（台帳化）。
  4. **マルチターン**を想定する: 第1問「結婚相談所ってどう？」→第2問「20代でも意味ある？」→第3問「安いところは？」。この連鎖の各段に答えるブロックを1記事内に置く。
  5. 検索ボリュームがゼロの長文でも捨てない（AIプロンプトはロングテールが本体）。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「プロンプトリサーチ キーワード調査 AI検索」「会話型クエリ 調査 LLMO」。【推測】「AI時代は会話型クエリが増える」という総論はあるが、**プロンプト収集の具体的データソース（サポートチケット・営業通話・コミュニティ）とタイプ分類の手法まで落ちた日本語記事はほぼ無い**と推定。要検証。
- **noe-match適用度**: **A**。婚活は「相談」型のプロンプトが極めて多い領域で相性が良い。**Yahoo!知恵袋の婚活カテゴリは事実上の日本語版Reddit**であり、生の言い回しの宝庫。工数: 初期収集8h＋台帳運用月2h。
- **リスク・反証**: 【推測・要検証】プロンプトには**公開された検索ボリュームデータが存在しない**ため、優先順位づけが主観になる。ツール各社が出す「プロンプトボリューム」は推定値であり、算出根拠が非公開のものが多い。投資判断の根拠としては弱い。

---

## 1-20. AI可視性計測ツール（Profound / Peec AI / Otterly / Scrunch / Semrush AI Toolkit / Ahrefs Brand Radar）と自作計測

- **一言で**: プロンプト群を定期的に各AIに投げ、自ブランドの出現率（share of model / share of voice）を測るSaaS群。個人メディアは**APIでの自作計測**で十分代替できる。
- **海外での出典**:
  - Surmado「Best AI Visibility Tools 2026: Profound vs Peec vs Otterly vs the Rest」 https://www.surmado.com/blog/best-ai-visibility-tools-2026
  - Sanbi「AI Visibility Platform Comparison 2026」 https://sanbi.ai/blog/ai-visibility-platform-comparison-peec-profound-scrunch
  - HubSpot「Peec AI alternatives for AI visibility monitoring in 2026」 https://blog.hubspot.com/marketing/peec-ai-alternatives
  - Bright Data「Open-Source AI Visibility Tracker」 https://brightdata.com/blog/ai/ai-visibility-tracker
  - Am I Cited「Building Your Own AI Visibility Tracking: DIY Methods」 https://www.amicited.com/blog/diy-ai-visibility-tracking/
  - Ritner Digital「How a marketer would actually build their own AI visibility tracker (and why it's harder than it sounds)」 https://www.ritnerdigital.com/blog/how-a-marketer-would-actually-build-their-own-ai-visibility-tracker-and-why-its-harder-than-it-sounds
- **仕組み／なぜ効くか**: 【事実】価格帯は Otterly.AI が月$29（15プロンプト）、Peec AI が月€89〜199、Profound が月$499前後から、Semrush のアドオンが$99、Ahrefs Brand Radar が$699+（※抜粋経由 https://www.surmado.com/blog/best-ai-visibility-tools-2026 、 https://sanbi.ai/blog/ai-visibility-platform-comparison-peec-profound-scrunch 、**価格は週単位で変動するため必ず現行の価格ページを確認**）。【事実】エンジンカバレッジは Scrunch が全プランで7エンジン（Claude・Metaを含む）、Profoundは最大10だが多くがEnterprise限定（※抜粋経由）。【事実】自作は OpenAI / Anthropic 等のAPIにプロンプト群を投げ、正規表現やNLPでブランド言及を検出する方式で、**API費用は月$5〜50程度**（※抜粋経由 https://www.amicited.com/blog/diy-ai-visibility-tracking/ ）。
- **具体手順**:
  1. 計測対象プロンプトを30〜50本決める（1-19のプロンプトリサーチの成果物）。
  2. Python/Node で「プロンプト一覧を読み込み → 各APIを順に叩く → 回答テキストを保存 → 自ブランド名/ドメインの出現を正規表現で検出 → スプレッドシートに追記」を書く。
  3. **週次または隔週**で回す（毎日は自動化必須、個人では過剰）。
  4. 記録項目: 出現有無、出現位置（何番目の推薦か）、引用URLの有無、競合として誰が出たか。
  5. **同じプロンプトを複数回叩いて分散を見る**（LLMは確率的なので1回計測は無意味）。
  6. web検索を使うモード（ChatGPT Search / Perplexity）と、使わない素のモデルを分けて計測する（前者はGEO施策が効き、後者は学習データ由来なので短期施策では動かない）。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「Profound Peec AI Otterly 比較 AI可視性」「AI可視性 計測 自作 API」。【推測】ツール名の紹介記事は日本語にも出始めているが、**自作計測のコード設計・複数回試行による分散測定・web検索モードの分離という方法論は日本語圏でほぼ無い**と推定。要検証。
- **noe-match適用度**: **A（自作）／C（SaaS）**。個人運営でProfound $499/月は非現実的。**自作で月$10程度**が正解。工数: スクリプト作成6〜10h＋週次運用0.5h。
- **リスク・反証**: 【事実】arXiv論文「Don't Measure Once: Measuring Visibility in AI Search (GEO)」 https://arxiv.org/pdf/2604.07585 が、**AI検索の可視性は1回の計測では不安定**であることを指摘している。単発の順位表を見て一喜一憂するのは無意味。【事実】Ritner Digitalの記事タイトル自体が「自作は思ったより難しい」であり、パーソナライズ・地域・ログイン状態で結果が変わる問題がある。またAPI経由の回答と実際のUI上の回答は同一ではない。

---

## 1-21. リーセンシーバイアスの利用（Recency Bias / dateModified の機械可読化）

- **一言で**: LLMリランカーには**新しいコンテンツを優遇する統計的バイアス**があることが査読論文で確認されている。更新日を構造化データで明示し、実際に更新することで取得順位を上げる。
- **海外での出典**:
  - 「Do Large Language Models Favor Recent Content? A Study on Recency Bias in LLM-Based Reranking」arXiv:2509.11353 https://arxiv.org/abs/2509.11353 / PDF https://arxiv.org/pdf/2509.11353
  - ACM SIGIR-AP 2025 収録 https://dl.acm.org/doi/10.1145/3767695.3769493
  - Seer Interactive「Study: AI Brand Visibility and Content Recency」 https://www.seerinteractive.com/insights/study-ai-brand-visibility-and-content-recency
  - Single Grain「How LLMs Interpret Historical Content vs Fresh Updates」 https://www.singlegrain.com/content-marketing-strategy-2/how-llms-interpret-historical-content-vs-fresh-updates/
- **仕組み／なぜ効くか**: 【事実】GPT-3.5-turbo / GPT-4o / GPT-4 / LLaMA-3 8B・70B / Qwen-2.5 7B・72B の7モデルで検証したところ、**「新しい」パッセージが一貫して押し上げられ、Top-10の平均公開年が最大4.78年ぶん前倒しになり、listwise reranking では個別アイテムが最大95順位動いた**。モデルが大きいほど緩和されるが、**どのモデルもバイアスを消せていない**（arXiv:2509.11353）。【事実】ログ分析ベースでは、ヒットの約65%が過去1年以内、79%が過去2年以内の公開コンテンツというデータもある（※抜粋経由 https://www.mattakumar.com/blog/how-to-rank-in-chatgpt-using-recency-bias/ 、原典要確認）。
- **具体手順**:
  1. `Article` スキーマの `datePublished` と `dateModified` を**正確に**出力する（WordPressのデフォルトが `dateModified` を出していないテーマがある）。
  2. 本文中に**可視の「最終更新日: 2026年8月」を表示**する（AIは本文テキストからも日付を読む）。
  3. タイトル／H1に年号を入れる（「2026年版」）。**ただし中身を更新せず年号だけ変えるのは虚偽**。
  4. 更新は「日付だけ変える」のではなく、**数値・料金・制度の実際の変更を反映**する（1-03の統計と連動）。
  5. 258記事を「更新価値の高い順」に並べ、四半期ごとに上位30本をローテーション更新する運用にする。
  6. 記事内の統計に**「2026年3月時点」のような時点表記を文中に入れる**（チャンク単体で鮮度が伝わる）。
- **日本での言及度**: **低〜中（推定・未検証）**。実行すべき日本語クエリ:「LLM リーセンシーバイアス 新しいコンテンツ 優遇 論文」「dateModified AI検索 鮮度」。【推測】「リライトが大事」は日本語SEOの常識だが、**「LLMリランカーに定量的な鮮度バイアスがある」という査読論文を根拠にした議論はほぼ無い**と推定。要検証。
- **noe-match適用度**: **A**。既存258記事の更新運用に直結。工数: スキーマ確認2h＋更新運用は継続。**婚活・結婚費用・自治体の補助金は毎年変わる領域なので、鮮度更新の実質的な価値が高い**（形だけの日付更新にならない）。
- **リスク・反証**: 【事実】論文が示しているのは**LLMリランカーのバイアス**であり、「日付を書き換えれば上がる」という意味ではない（論文は passage の実publication year を操作した実験）。【事実】Googleは日付だけ変えて中身を更新しない行為をスパムとして扱う。また鮮度バイアスは「古いが正確な情報」を不当に下げるという**モデル側の欠陥**であり、これに乗るのは長期的には脆い。

---

## 1-22. セマンティック・トリプル文体（Subject-Predicate-Object / Koray Framework）

- **一言で**: 全文を「主語＋述語＋目的語」の明確な三つ組で書き、曖昧な修辞を排する。H2をユーザーの質問文にし、その直下に40語前後の抽出可能な答えを置く。
- **海外での出典**:
  - Holistic SEO（Koray Tuğberk Gübür）「Semantic Search for Semantic SEO」 https://www.holisticseo.digital/seo-research-study/semantic-search
  - Holistic SEO「Importance of Entity, Attribute, Value (EAV) Architecture for SEO」 https://www.holisticseo.digital/seo-research-study/entity-attribute-value
  - Topical Authority and Semantic SEO Course https://www.topicalauthority.digital/
  - Claire Broadley「WTF is Subject-Predicate-Object? Semantic SEO Guide」 https://www.clairebroadley.com/wtf-is-subject-predicate-object/
  - FatRank「Semantic Triples - Subject Predicate Object RDF Triple」 https://www.fatrank.com/semantic-triples/
- **仕組み／なぜ効くか**: 【事実】セマンティック・トリプルは主語（エンティティ）＋述語（関係）＋目的語（値または関連エンティティ）のデータ構造で、知識グラフの基本単位（※抜粋経由）。【事実】Koray Framework は41のコンテンツルールから成り、**1ページ1マクロコンテキスト、H2はユーザーの質問文、40語の抽出型回答、EAV（エンティティ・属性・値）の網羅**を柱とする（※抜粋経由 https://pos1.ar/seo/koray-framework/ ）。「Koraynese」と呼ばれる文体は、全文がSPOトリプルを含み、全エンティティが属性で修飾され、全主張が検証可能という制約を課す。
- **具体手順**:
  1. H2を必ず**疑問文**にする（「結婚相談所の成婚料はいくらか？」）。
  2. H2直下に**40語前後（日本語なら80〜120字）の完結した答え**を置く。修飾・前置きなし。
  3. 文型を「Aは、Bである」「AはBをCする」に揃える。「〜と言えるでしょう」「〜かもしれません」を削る。
  4. **エンティティ＋属性＋値**を明示する（「結婚相談所（エンティティ）の成婚料（属性）は平均5〜20万円（値）」）。
  5. 1記事1マクロコンテキストを守る（婚活アプリの記事に結婚式の話を混ぜない）。
  6. 全主張に検証可能な出典を付ける（1-03と統合）。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「セマンティックトリプル SEO 主語 述語 目的語」「Koray フレームワーク トピカルオーソリティ 日本語」。【推測】「トピカルオーソリティ」は日本語でもかなり流通したが（noe-match も認知済み）、**その提唱者Korayの41ルール／SPO文体／EAV／40語回答という実装レイヤーは日本語圏でほぼ流通していない**と推定。要検証。
- **noe-match適用度**: **A（新規記事）／B（既存記事）**。noe-match は既にトピカルオーソリティを認知しているので、その**下位レイヤーの実装ルール**として導入価値が高い。1-02（チャンク最適化）と1-03（citation engineering）と合わせて**1本のライティング規約**にまとめられる。工数: 規約策定4h。
- **リスク・反証**: 【事実】Koray Framework は**個人の提唱するメソドロジーであり、査読研究や公式ドキュメントの裏付けはない**。「41のルール」という数字も本人由来。【推測】SPO文体を徹底すると日本語として不自然に硬くなり、読了率・回遊率が落ちるリスクがある。婚活という感情的な領域で機械的な文体は逆効果になり得る（アフィリエイト転換率とのトレードオフ）。

---

## 1-23. エンティティ・サリエンス測定（Entity Salience / Google Cloud NLP API）

- **一言で**: Google Cloud Natural Language API に自記事を投げ、**「このページは何についての記事だと機械が判定しているか」を0.0〜1.0のsalienceスコアで確認**する。狙ったエンティティが1位でないなら書き方を直す。
- **海外での出典**:
  - Google Cloud Natural Language API — Entity リファレンス https://docs.cloud.google.com/natural-language/docs/reference/rest/v1/Entity
  - Dan Taylor「Understanding salience for better keyword classification」 https://dantaylor.online/blog/understanding-salience-better-keyword-classification/
  - Search Engine Land「Entity-first SEO: How to align content with Google's Knowledge Graph」 https://searchengineland.com/guide/entity-first-content-optimization
  - Squin「Google NLP API for SEO: Complete Implementation Guide」 https://squin.org/semantic-seo/google-nlp-api-seo/
  - ClickRank「What is entity salience?」 https://www.clickrank.ai/seo-glossary/e/what-is-entity-salience/
- **仕組み／なぜ効くか**: 【事実】Cloud Natural Language API はテキスト中のフレーズを既知のエンティティ（人物・組織・場所など）として表現し、各エンティティに **salience（0.0〜1.0の中心性推定）** と mentions を返す（Google公式リファレンス）。【事実】salienceは「その文書にとってそのエンティティがどれだけ中心的か」の推定値。狙ったトピックのsalienceが低い＝機械にとってその記事は別の話に見えている。
- **具体手順**:
  1. Google Cloud の Natural Language API を有効化（少量なら無料枠内）。デモUIでも試せる。
  2. 主要記事の本文をAPIに投げ、**エンティティのsalience降順リスト**を出す。
  3. 狙ったエンティティ（例:「結婚相談所」）が1位でない、またはsalienceが極端に低いなら、**冒頭段落・H2・最初の100語にそのエンティティを配置**し直す。
  4. **意図しないエンティティが上位に来ていないか**確認（広告文言、運営者名、無関係な地名がトップになる事故がよくある）。
  5. 記事群全体でsalienceを集計し、**サイト全体のトピック分布**を可視化する（トピカルオーソリティの定量チェック）。
  6. schema.org の `about`（記事の主題）と `mentions`（言及）を、salience上位を `about`、下位を `mentions` に対応させて記述する。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「エンティティサリエンス Google NLP API SEO」「salience 記事 判定 構造化」。【推測】Google NLP APIをSEOに使う話は数年前に日本語でも一部紹介されたが、**AI検索/GEOの文脈で復権させ、`about`/`mentions` スキーマと接続する議論は日本語圏でほぼ無い**と推定。要検証。
- **noe-match適用度**: **B（条件付き）**。GCPアカウントとAPIキーが必要でやや技術寄り。ただし**258記事の「機械から見たトピック分布」を一度可視化する価値は大きい**（トピカルオーソリティの自己診断）。工数: セットアップ3h＋一括分析スクリプト4h。
- **リスク・反証**: 【事実】Cloud NLP API は**Google検索のランキングシステムそのものではない**。salienceが検索順位やAI引用に直結する証拠はなく、あくまで「機械可読性の代理指標」。【推測】日本語のエンティティ抽出精度は英語より低い可能性があり、スコアの解釈には注意が必要。

---

## 1-24. Dataset スキーマ＋Google Dataset Search（一次データの機械可読化）

- **一言で**: 独自に集めたデータ（noe-matchの自治体データ43件など）を `Dataset` 構造化データでマークアップし、Google Dataset Search に登録可能な形にする。日本のアフィリエイトSEOではまず語られない構造化データ。
- **海外での出典**:
  - Google Search Central「Dataset Structured Data」 https://developers.google.com/search/docs/appearance/structured-data/dataset
  - Hill Web Creations「How to Use Google Dataset Search with Dataset Schema」 https://www.hillwebcreations.com/google-dataset-search-adds-dataset-schema/
  - SE Ranking「Structured Data for SEO and LLMs」 https://seranking.com/blog/structured-data/
  - Opace「Schema Markup for SEO: The Complete Structured Data Guide for Google, AI Search and LLMs (2026)」 https://opace.agency/blog/structured-data-schema-for-seo/
- **仕組み／なぜ効くか**: 【事実】Datasetマークアップの目的は、ライフサイエンス・社会科学・機械学習・**行政/市民データ**などのデータセットの発見性を高めること。名称・説明・作成者・配布形式を構造化データで提供すると Dataset Search で見つかりやすくなる（Google公式）。【事実】Googleは schema.org の Dataset に加え、W3C の **DCAT** 形式も理解し、**CSVW** の実験的サポートも行っている（Google公式）。【推測】AIが「一次データの出所」を探すとき、Dataset としてマークアップされたページは「オリジナルのデータ源」として識別されやすく、引用の帰属先になりやすい。
- **具体手順**:
  1. 自治体データ43件を**1つのデータセットページ**にまとめる（一覧＋定義＋収集方法＋更新日）。
  2. `@type: Dataset` で `name` / `description`（50字以上推奨）/ `creator`（Organization、1-09と接続）/ `datePublished` / `dateModified` / `license` / `keywords` / `spatialCoverage`（日本／都道府県）/ `temporalCoverage` をマークアップ。
  3. `distribution` に `@type: DataDownload` で **CSV / JSON の実ファイルURL** を指定する（実際にDL可能にする）。
  4. 収集方法（methodology）を明記する — これがAI引用時の信頼シグナルになる。
  5. 引用時の表記ルール（「Noe結婚設計室調べ」）をページ内に明記（1-11と接続）。
  6. Rich Results Test / Schema Markup Validator で検証。
- **日本での言及度**: **ほぼ無（推定・未検証）**。実行すべき日本語クエリ:「Dataset 構造化データ Google Dataset Search 実装」「DataDownload スキーマ CSV 配布」。【推測】**Datasetスキーマは日本語SEO記事でほぼ完全に無視されている**領域と推定（学術リポジトリ文脈で少しあるかもしれないが、メディア運営の文脈ではほぼゼロ）。要検証。
- **noe-match適用度**: **A（最も噛み合う施策のひとつ）**。noe-matchは既に一次データバンク（自治体データ43件）を持っており、**それを機械可読にするだけ**で「大手が持っていない独自データ源」として認識され得る。工数: データセットページ制作6h＋スキーマ実装3h＋CSV整備3h。
- **リスク・反証**: 【事実】Dataset リッチリザルトは**通常のウェブ検索には表示されず、Google Dataset Search という別サービス上での発見性向上が主**。直接的な検索流入増は期待しにくい。【事実】GoogleはFAQ等の構造化データ機能を次々に廃止しており（1-25参照）、Datasetも将来の廃止対象になる可能性は否定できない。【推測】CSVを配布すると競合にデータを丸ごとコピーされるリスクがある（一方でそれが引用と言及を生むというトレードオフ）。

---

## 1-25. 廃止済み／表示なしスキーマの「AI向け信号」としての残存利用（Speakable / ClaimReview / FAQ）

- **一言で**: リッチリザルト表示が廃止されたスキーマ（FAQ、ClaimReview）や、そもそも表示を持たないスキーマ（Speakable）は、**SERP上の見返りはないがAIへの意味論的シグナルとしては残る**という考え方。
- **海外での出典**:
  - Google Search Central「Speakable (BETA) Structured Data」 https://developers.google.com/search/docs/appearance/structured-data/speakable
  - Google Search Central「Fact Check (ClaimReview) Markup」 https://developers.google.com/search/docs/appearance/structured-data/factcheck
  - schema.org ClaimReview https://schema.org/ClaimReview
  - Relevant Audience「Google Dropped These Schema Types — 2026 Fix List」 https://www.relevantaudience.com/seo/google-removes-structured-data-2025-guide-for-websites/
  - Digital Applied「Schema Markup After March 2026: Structured Data Update」 https://www.digitalapplied.com/blog/schema-markup-after-march-2026-structured-data-strategies
  - Passionfruit「FAQ Rich Results Deprecated: Google's May 2026 Change」 https://www.getpassionfruit.com/blog/what-changed-with-google-drops-faq-rich-results-and-what-to-do-now
  - Stan Ventures「John Mueller Clarifies Schema Changes Coming in 2026」 https://www.stanventures.com/news/google-john-mueller-schema-update-2026-5719/
- **仕組み／なぜ効くか**: 【事実】Speakable は記事内の音声読み上げに適した箇所を指定するプロパティで、**Googleでは今もBETA扱いだが廃止されていない**。SERP表示は持たず、Assistant／AI回答レイヤーに供給されるとされる（※抜粋経由 https://www.levyonline.com/blog/speakable-structured-data/ ）。【事実】ClaimReview は2025年6月にGoogleがリッチリザルトのサポートを廃止したが、**schema.orgの語彙としては存続しており、他のプラットフォームや検索エンジンは今も読む**（※抜粋経由 https://www.relevantaudience.com/seo/google-removes-structured-data-2025-guide-for-websites/ ）。【事実】FAQリッチリザルトも2026年に廃止された（※抜粋経由 https://www.getpassionfruit.com/blog/what-changed-with-google-drops-faq-rich-results-and-what-to-do-now ）。**noe-matchはFAQPageを全記事に実装済みだが、表示上のメリットはもう無い**という前提を持つ必要がある。
- **具体手順**:
  1. **FAQPageスキーマを外さない**（AI向けの意味論シグナルとして残す）。ただし**「リッチリザルトが出る」という前提の運用は改める**。
  2. FAQの本文が**アコーディオン内のJS生成になっていないか確認**（1-07。スキーマだけあって本文が読めないのが最悪パターン）。
  3. Speakable を主要記事の「結論1文」に付ける: `speakable: {"@type":"SpeakableSpecification","cssSelector":[".answer-lead"]}`。
  4. ClaimReview は「◯◯という説は本当か」型の検証記事にのみ付ける。**訂正方針ページ（corrections policy）が要件だったため、それも用意する**。政治関連は対象外。
  5. すべて Schema Markup Validator（schema.org側）で検証する（Googleのリッチリザルトテストは廃止済み機能を検証しない）。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「Speakable スキーマ 実装 2026」「ClaimReview 構造化データ 廃止 意味」「FAQPage 廃止 スキーマ 残すべきか」。【推測】FAQリッチリザルト廃止のニュースは日本語でも流通したが、**「表示は消えたがAI向け信号として残す」という判断軸や、Speakable/ClaimReviewの残存利用の議論はほぼ無い**と推定。要検証。
- **noe-match適用度**: **B**。FAQPage維持の判断は即実行（工数0）。Speakable追加は工数2h。ClaimReviewは婚活領域で「◯◯は本当か」型の記事を作るなら価値があるが、訂正方針ページの整備が必要（工数4h）。
- **リスク・反証**: 【事実】**「廃止されたスキーマがAIに効く」という主張には実証データがない**。上記の「AI Modeが ClaimReview ページを高信頼ソースとして扱う」という記述は二次ソースのベンダー主張であり、Googleの公式言明ではない。維持コストがほぼゼロだから残す、という以上の根拠はない。【事実】Googleは構造化データ機能を継続的に削減しており、投資対象としては縮小トレンド。

---

## 1-26. コサイン類似度によるコンテンツ自己監査（Embedding-based Content Audit）

- **一言で**: 自記事とターゲットクエリをそれぞれ埋め込みベクトル化し、コサイン類似度を計算して「機械から見た関連度」を数値で測る。内部リンク候補・カニバリ・剪定対象も同じ手法で洗い出す。
- **海外での出典**:
  - Search Engine Land「How to leverage cosine similarity for ecommerce SEO」 https://searchengineland.com/how-to-leverage-cosine-similarity-for-ecommerce-seo-448027
  - Tinuiti「Using Cosine Similarity for AI SEO: The Quick Start Guide」 https://tinuiti.com/blog/search/cosine-similarity/
  - Lumar「Semantic Search Explained: Vector Models' Impact on SEO Today」 https://www.lumar.io/blog/best-practice/semantic-search-explained-vector-models-impact-on-seo/
  - Wix Studio「Vector Embedding: Enhance Your GEO Strategy with Semantic Search」 https://www.wix.com/studio/ai-search-lab/vector-embedding
- **仕組み／なぜ効くか**: 【事実】検索エンジンとLLMは、文書ベクトルとクエリベクトルの距離で関連性を判定する。近いほど関連性が高い（※抜粋経由）。【事実】SEO用途では**キーワードクラスタリング、コンテンツ分析、重複検出**に使われ、コンテンツクラスタの特定・内部リンク機会の発見・剪定対象ページの特定に応用される（※抜粋経由 https://searchengineland.com/how-to-leverage-cosine-similarity-for-ecommerce-seo-448027 ）。1-04（fan-out）と1-14（Ahrefsの発見）を踏まえると、**fan-outクエリと自記事タイトル/URLの類似度**こそが引用の鍵。
- **具体手順**:
  1. OpenAI の embeddings API（`text-embedding-3-small` 等、極めて安価）で258記事のタイトル＋H2＋冒頭200字をベクトル化。
  2. 1-04で得た fan-out クエリ群もベクトル化。
  3. **各fan-outクエリ × 各記事のコサイン類似度行列**を作る。
  4. 類似度が最も高い記事が「その派生クエリに答えるべき記事」。**どの記事も低いクエリ＝コンテンツギャップ**。
  5. **記事同士の類似度が0.9超のペア＝カニバリ候補**として統合または差別化する。
  6. 中程度の類似度（0.7〜0.85）のペア＝**内部リンクの自然な候補**（noe-matchの内部リンク設計を機械的に強化できる）。
- **日本での言及度**: **低（推定・未検証）**。実行すべき日本語クエリ:「コサイン類似度 SEO コンテンツ監査 埋め込み」「embedding 内部リンク 提案 カニバリ」。【推測】キーワードクラスタリングにembeddingを使う話は日本語でも一部あるが、**「fan-outクエリ×記事の類似度行列でギャップを見つける」という設計は日本語圏でほぼ無い**と推定。要検証。
- **noe-match適用度**: **A**。258記事という規模はスクリプト処理に最適。**内部リンク設計（既に取り組み中）とトピカルオーソリティの定量化を同時に達成できる**。API費用は数百円レベル。工数: スクリプト8h。
- **リスク・反証**: 【推測】OpenAIのembeddingは、Googleや各AI検索が内部で使う埋め込みモデルとは**別物**。得られる類似度は「代理指標」であり、実際の検索システムの挙動を再現するものではない。【推測】日本語の短文（タイトル）の埋め込みは意味を十分に捉えないことがあり、閾値の設定には試行錯誤が要る。

---

## 領域1の未解決事項（結論が割れている論点）

1. **llms.txt は「無意味」で確定なのか、「早すぎる」だけなのか**
   Google（Mueller / Illyes）は明確に否定し、ログ分析でもクローラが読みに来ていない。一方で採用率は上位1,000サイトの8.7%まで伸びており（ https://www.rankability.com/data/llms-txt-adoption/ ）、エージェント（コーディングアシスタント等）用途では実際に使われているという主張もある（ https://www.untype.jp/blog/llms-txt-agent-readability/ ）。「検索用途では死んでいるがエージェント用途では生きている」という分裂した評価が並立しており、決着していない。

2. **Markdown配信（コンテンツネゴシエーション）は llms.txt の後継か、同じ轍か**
   Sentry / Ably の実運用例はあるが、**AI引用が増えたという実測はどこにも存在しない**。重複コンテンツとクロールバジェットのコストは確実に発生する。llms.txtと同じ「送り手だけが熱心」構造に見えるという批判と、「HTTPの標準機能なので受け手が対応しやすい」という擁護が対立。

3. **ブランド言及とAI可視性の相関0.664は因果か交絡か**
   Ahrefsの75Kブランド調査（ https://ahrefs.com/blog/ai-overview-brand-correlation/ ）はバックリンク0.218に対し言及0.664を示すが、**「有名だから両方多い」という交絡を排除していない**。「言及を増やせばAI可視性が上がる」という施策論に転換できるかは未証明。特に「YouTube言及0.737」は、YouTubeがGoogle所有であることによる構造的優遇の可能性がある。

4. **自作リスティクル（自分を1位に置く比較記事）は効くのか**
   Ahrefsは「自己宣伝的なbestリストがChatGPTソースとして目立つ」と観測しているが（ https://ahrefs.com/blog/best-lists-research/ ）、それが**持続するのか、GEOスパムとして対処されるのか**は結論なし。「引用は買うものではなく獲得するもの」という規範論と、「実際に効いている」という観測が対立。

5. **リーセンシーバイアスに乗るべきか、乗ると脆いか**
   arXiv:2509.11353 は7モデルすべてで鮮度バイアスを確認し、著者らはこれを**情報検索の欠陥・バイアスとして問題視**している。バイアスは将来的に修正され得る。「今の穴を突く」戦術と「修正されたら無駄になる」懸念のどちらを取るかは未解決。

6. **ChatGPTはまだBing依存なのか**
   「87%がBing上位と一致」（Seer Interactive、※抜粋経由）という数字がある一方、OpenAIは自前クローラ・自前インデックスを構築中で第三者検索プロバイダも併用しているという記述もある（ https://lemniscategrowth.com/blogs/how-chatgpt-search-works.html ）。**Bing Webmaster Tools への投資の価値がいつまで続くかは不明**（ただしコストが低いので実務上は問題にならない）。

7. **英語圏の引用元分布データを日本語市場に外挿できるか**
   「PerplexityはRedditが46.7%」「ChatGPTはWikipediaが47.9%」といったデータはすべて英語圏プロンプト中心。**日本語プロンプトでのRedditはほぼゼロ**であり、対応するUGC（Yahoo!知恵袋・はてな・note・X）が同じ役割を果たすかは誰も検証していない。noe-match自身の実測が唯一の根拠になる。

8. **AI可視性の計測方法論そのものが未確立**
   arXiv:2604.07585「Don't Measure Once」は、AI検索の可視性は単発計測では不安定だと指摘。ツール各社の「Share of Model」「Visibility Score」は算出方法が非公開かつ相互に非互換で、**同じブランドでもツールによって結果が大きく違う**。KPIとして経営判断に使える段階にない。

9. **FAQPage を残すべきか外すべきか**
   リッチリザルトは廃止された。「AI向けの意味論シグナルとして残す」派と「無駄なマークアップはページ肥大とメンテコストだけを生む」派が対立し、Google側から「残す価値がある」という言明は出ていない。noe-matchは全記事実装済みなので、**外すコストのほうが高い**というのが現実的な回答だが、根拠は薄い。

10. **GEO論文（KDD 2024）の効果量は2026年のエンジンにも当てはまるか**
    Statistics Addition / Quotation Addition の+41%/+28%は2023年当時の生成エンジン模擬環境での測定。**AI Mode の query fan-out アーキテクチャは当時と別物**であり、後続研究（arXiv:2604.19113 / 2604.25707）が別の特徴量セットを提案している。どの特徴量が現行エンジンで有効かは収束していない。

---

## 補遺: 未実行の日本語検証クエリ一覧（次回セッションで実行すべき）

セッションの検索クォータ枯渇により未実行。手法番号とクエリの対応:

| 手法 | 実行すべき日本語クエリ |
|---|---|
| 1-03 | `GEO 論文 Princeton 統計追加 引用追加 可視性` / `生成エンジン最適化 論文 KDD 2024` |
| 1-04 | `クエリファンアウト AI Mode 対策` / `query fan-out 日本語 SEO Qforia` |
| 1-05 | `GPTBot OAI-SearchBot 使い分け robots.txt` / `Google-Extended ブロック 検索順位 影響` |
| 1-06 | `Cloudflare Pay Per Crawl 日本語` / `crawl to refer ratio クロール 流入 比率` |
| 1-07 | `AIクローラー JavaScript 実行しない SSR` / `GPTBot JS レンダリング Vercel` |
| 1-08 | `コンテンツネゴシエーション AIエージェント Markdown 配信` / `Accept: text/markdown SEO` |
| 1-09 | `Wikidata SEO 登録 ナレッジパネル` / `sameAs エンティティ 名寄せ` |
| 1-10 | `ProfilePage スキーマ 著者 構造化データ` / `Person schema knowsAbout 著者` |
| 1-11 | `ブランド言及 AI可視性 相関 バックリンク Ahrefs` |
| 1-12 | `ChatGPT 引用 リスティクル おすすめ選 43%` |
| 1-13 | `ChatGPT Perplexity AI Overviews 引用元 ドメイン 違い` |
| 1-14 | `retrieval citation 取得 引用 ChatGPT 半分` |
| 1-15 | `Bing インデックス ChatGPT 引用 条件` / `IndexNow WordPress 設定` |
| 1-16 | `utm_source=chatgpt.com GA4 計測` |
| 1-17 | `Search Console 生成AI パフォーマンスレポート AI Mode` |
| 1-18 | `GPTBot ログ解析 アクセスログ AIボット` |
| 1-19 | `プロンプトリサーチ キーワード調査 AI検索` |
| 1-20 | `Profound Peec AI Otterly 比較 AI可視性` / `AI可視性 計測 自作 API` |
| 1-21 | `LLM リーセンシーバイアス 論文 鮮度` |
| 1-22 | `セマンティックトリプル SEO 主語 述語 目的語` / `Koray フレームワーク 日本語` |
| 1-23 | `エンティティサリエンス Google NLP API SEO` |
| 1-24 | `Dataset 構造化データ Google Dataset Search 実装` |
| 1-25 | `Speakable スキーマ 実装 2026` / `ClaimReview 構造化データ 廃止` |
| 1-26 | `コサイン類似度 SEO コンテンツ監査 埋め込み` |

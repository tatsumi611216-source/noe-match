# 領域8: 2026年の最前線と日英情報ギャップ

- **調査日**: 2026-08-27
- **参照ソース数**: 実際に検索結果として取得できたURL = 47件（うち本文まで読めたもの = 0件）
- **調査完了度**: **部分完了（約35%）**

---

## ⚠️ 最初に読むこと（本レポートの信頼性の限界）

このレポートは**依頼された調査の一部しか実行できていない**。理由を先に書く。

1. **WebSearch の回数上限をセッション全体で使い切った。** 本セッションは200回の検索枠を他エージェントと共有しており、私が着手した時点で残枠がほぼ無かった。私が実行できた検索は **8回のみ**（依頼は最低25回）。
2. **WebFetch / curl による外部サイト取得が、ネットワークポリシーで全面的に遮断されている。** `developers.google.com` / `ahrefs.com` / `techcrunch.com` / `searchengineland.com` / `searchenginejournal.com` / `seroundtable.com` / `blog.cloudflare.com` / `en.wikipedia.org` / `example.com` すべて `CONNECT tunnel failed, response 403`。つまり**英語一次ソースの本文を1本も読めていない**。
3. 結果として、以下が**実行できていない**:
   - 一次ソース（Google公式・OpenAI公式・Cloudflare公式）本文の確認 → **すべて検索スニペット経由の間接情報**
   - **日本語での対応検索（手順2）が1回も実行できていない** → 「日本語圏での言及」欄は全論点で**未検証**
   - 論点8-08〜8-18（Perplexity/Claude/Copilot引用傾向、AP2/NLWeb、ゼロクリック収益モデル、Google 2026更新履歴、検索の分散、日本語SEO情報源の実態）は**未着手**

### この文書の読み方
- **【確認済】** = 2026年8月27日に実際に検索を実行し、複数の検索結果スニペットで一致した内容。ただし一次ソース本文は未読。
- **【要検証】** = 検索結果に出たが、出典が営業目的のブログで、裏取りできていない数値。
- **【未調査】** = 検索すら実行できていない。中身は書いていない。
- **【推論】** = 私の分析であり、事実ではない。

**この文書を根拠に施策を決める前に、検索枠を回復して再実行すること。** 特に数値は【要検証】が多く、そのまま記事に引用してはいけない。

---

# 第1部: 論点

## 8-01. Search Console の生成AIパフォーマンスレポート（Generative AI Performance Reports in Search Console）

- **一言で**: Googleが2026年6月3日、Search Console に AI Overviews / AI Mode / Discover の生成AI面での**表示回数**を見るレポートを追加した。ただし**クリック数は含まれない**。
- **海外での出典**:
  - Google Search Central Blog「Introducing Search Generative AI performance reports in Search Console」 https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports （2026年6月）※本文取得は遮断され未読
  - Neil Patel「Google Search Console Now Tracks AI Search: What to Do」 https://neilpatel.com/blog/gsc-ai-search-data-generative-ai-report/ （2026年、日付未確認）
  - Pragma-Code「Google Search Console: Generative AI Performance Reports 2026」 https://www.pragma-code.de/en/blog-search-console-generative-ai-performance
- **何が起きているか** 【確認済（ただし一次ソース未読）】:
  1. 公開日は2026年6月3日とされる。
  2. 対象は Search 上の生成AI機能（AI Overviews および AI Mode）と、Discover 上の生成AI機能。
  3. 提供されるディメンションは5つ: impressions（表示回数）、pages（引用されたURL）、countries、devices、dates（時間単位〜月単位）。
  4. **クリック数（CTR）、ユーザーの実際のプロンプト文字列、掲載順位は開示されない。**
  5. ロールアウトは2026年6月時点で**英国拠点のサイト所有者の一部**に限定。全世界展開は「予定」とされるが時期未発表。
  6. Google は追加指標を検討中としている。
- **サイト運営者にとっての含意**: これまで「AI経由の露出は測れない」が前提だったが、**表示回数だけは公式に測れるようになる**。ただしクリックが出ないため「AI Modeで何回引用されたか」は分かっても「それが何の役に立ったか」は依然分からない。日本のサイトはまだ対象外の可能性が高い。
- **日本語圏での言及**: **未検証**（日本語検索を実行できていない）。ただし検索結果の英語圏ブログの量から見て、英語圏では2026年6月〜7月に一斉に記事化されている。
- **noe-match適用度**: **A** — 今すぐの実務アクションは「Search Console を毎月開いて、生成AIレポートのタブが自分のアカウントに出現したかを確認する」だけ。出現した時点で、婚活系クエリでどのページがAIに拾われているかが初めて可視化される。ロールアウト待ちなので先回りの実装作業は不要。
- **不確実性**: (a) 日本への展開時期が完全に不明。(b)「クリック数を含まない」は複数の二次ソースで一致するが、一次ソース未読のため断定できない。(c) 既存の Performance レポートに AI Mode のクリックが**合算されている**のか**別枠**なのかが、この調査では確定できなかった。これは実務上かなり重要な論点なので再調査必須。

---

## 8-02. Query fan-out（クエリ・ファンアウト）

- **一言で**: AI Mode は1つの質問を**9〜11本の下位クエリに分解**して並列検索し、その結果を統合して答えを作る。つまり「1キーワードで上位を取る」設計が構造的に効かなくなる。
- **海外での出典**:
  - upGrowth「Query Fan-Out Explained: AI Mode + ChatGPT [2026]」 https://upgrowth.in/query-fan-out-google-ai-mode-chatgpt-explained/
  - nobori.ai「Query Fan-Out Optimization: The 2026 B2B Playbook」 https://nobori.ai/blog/query-fan-out-optimization-hidden-sub-queries-ai-citations-2026
  - Link Building Journal「Query Fan-Out: How AI Mode Splits One Question Into Many」 https://linkbuildingjournal.co.uk/query-fan-out/
  - ※いずれも**SEO事業者の営業ブログ**であり一次ソースではない。Google自身のAI Mode発表文言（「subtopicsに分解し、多数のクエリを同時に発行する」）が元ネタ。
- **何が起きているか**:
  1. 【確認済】Google は AI Mode 発表時に、質問をサブトピックに分解して同時に多数のクエリを発行する仕組みを自ら説明している。
  2. 【要検証】ekamoira の調査として「59%のプロンプトが5〜11本の同時サブクエリを発火」「複雑なクエリの平均は9〜11本」。
  3. 【要検証】Google AI Mode は9〜11本、ChatGPT は2.3〜2.8本という比較値。
  4. 【要検証】ALM Corp が173,000 URLを対象にした2025〜2026年の調査で、**上位10位のページがAI Overviewsに引用される率が76%→38%に低下**。
  5. 【要検証】FAQスキーマのあるページはAI回答に出る確率が60%高い。
- **サイト運営者にとっての含意**: 「検索順位1位 ≒ AI回答に引用される」という前提が崩れつつある（4の数値が正しければ半減している）。対策の方向は、単一キーワード最適化ではなく、**1テーマについて想定される派生質問を1ページ内で網羅的に、抽出しやすい形（見出し＋短い断定文）で書く**こと。
- **日本語圏での言及**: **未検証**。ただし検索結果に `linksurge.jp/blog/en/query-fan-out-guide-2026/` という**日本ドメインが英語ページで**この話題を書いているものが混ざっていた。日本の事業者が英語圏向けに発信している例であり、日本語圏内での流通量とは別問題。
- **noe-match適用度**: **A** — 「婚活アプリ おすすめ」のような単発キーワード狙いの記事より、「30代女性が婚活アプリを選ぶときに出てくる疑問」を1本の中に見出し単位で10〜15個並べる構成のほうが、fan-out に拾われやすい。既存記事のリライト方針として直接使える。
- **不確実性**: サブクエリ本数の具体的数値はすべて営業ブログ由来で、**測定方法が公開されていない**。「9〜11本」を事実として記事に書くのは危険。fan-out という仕組みの存在はGoogle自身が認めているので、そこまでは書いてよい。

---

## 8-03. llms.txt はほぼ決着した（2026年時点）

- **一言で**: **llms.txt は誰も読んでいない。** 97%のファイルが2026年5月に一度もアクセスされていないという大規模調査があり、Google も公式に非推奨の立場。日本語圏でまだ「やるべき施策」として語られているなら、それは周回遅れ。
- **海外での出典**:
  - Ahrefs「We Analyzed 137K Sites: 97% of llms.txt Files Never Get Read」 https://ahrefs.com/blog/llmstxt-study/ （2026年、5月のデータ）
  - Search Engine Journal「Google's Mueller Says llms.txt Can't Help LLMs Differentiate Sites」 https://www.searchenginejournal.com/googles-mueller-says-llms-txt-cant-help-llms-differentiate-sites/579304/
  - Search Engine Roundtable「Google Search Team Does Not Endorse LLMs.txt Files」 https://www.seroundtable.com/google-does-not-endorse-llms-txt-40789.html
  - The SEO Community「The Current Consensus on llms.txt: Where Are We Now? (Still No)」 https://theseocommunity.com/resources/blog/llms-txt-should-we-or-not
- **何が起きているか** 【確認済（複数ソース一致）】:
  1. Ahrefs が137,000サイトを調査し、**llms.txt ファイルの97%が2026年5月に一切のトラフィックを受けていない**と報告。
  2. The SEO Framework の検証では、**Googlebot も GPTBot も ClaudeBot も llms.txt を取りに来なかった**。
  3. Google の John Mueller は、llms.txt では LLM がサイトを識別・差別化できないと述べ、エージェントが既にサイト上にいる場合の限定的な役割しか認めていない。
  4. Google のドキュメントサイトに llms.txt が存在したのは、**社内CMSが自動生成しただけで、消し忘れ**だったと説明されている。
  5. OpenAI / Google / Anthropic / Meta のいずれも、本番システムでこのファイルを読む・利用すると公式に表明していない（2026年Q1時点）。
  6. Mueller の実務的な回答:「あなたに顧客を連れてきているAIプラットフォームが『このファイルが必要だ』と文句を言ってきたら、そのとき作ればいい」。
- **サイト運営者にとっての含意**: **llms.txt に工数を割く必要はない。** 設置しても害は無いが、効果の根拠が現時点で存在しない。「AI時代のSEOとして llms.txt を設置しましょう」という日本語記事や有料note・コンサルがあれば、2026年時点では**根拠が薄い**と判断してよい。
- **日本語圏での言及**: **未検証**。【推論】ただし llms.txt は2024〜2025年に日本語圏でもそれなりに話題になった経緯があり、「否定側の決着（2026年のAhrefs調査・Mueller発言）」のほうが日本語に降りてくるのは遅れやすい構造がある。**肯定的な新施策の情報は速く伝播し、否定的な決着は遅く伝播する**（第2部参照）。これは検証すべき仮説であって、確認された事実ではない。
- **noe-match適用度**: **B** — 「やらない」という判断のために使う。加えて、**逆張りコンテンツのネタとして価値がある**（後述の情報ギャップ活用）。
- **不確実性**: 「97%が読まれていない」の測定方法（サーバーログか、Ahrefs自身のクロールデータか）を一次ソースで確認できていない。また llms.txt を**推している側**（Answer.AI の Jeremy Howard ら提唱者）の2026年時点の反論を私は確認していない。片側だけ見て決着と書くのは本来危険。

---

## 8-04. Cloudflare の AIクローラー既定ブロックと Pay Per Crawl → Pay Per Use

- **一言で**: Cloudflare が **2026年9月15日から**、広告を掲載しているページに対する「mixed-use」クローラーを**既定でブロック**する。さらに Pay Per Crawl（クロールごとに課金）は **Pay Per Use（AI回答に自社コンテンツが登場したら課金）** に進化しつつある。
- **海外での出典**:
  - TechCrunch「Cloudflare's new policy pushes AI companies to pay for publishers' content」 https://techcrunch.com/2026/07/01/cloudflares-new-policy-pushes-ai-companies-to-pay-for-publishers-content/ （2026年7月1日）
  - Cloudflare Blog「Introducing pay per crawl」 https://blog.cloudflare.com/introducing-pay-per-crawl/ （一次ソース・本文未読）
  - Technology.org「Cloudflare Sets Deadline for Mixed AI Crawlers」 https://www.technology.org/2026/07/03/cloudflare-blocks-mixed-use-ai-crawlers/ （2026年7月3日）
  - fastCRW「Cloudflare's September 15 AI Crawler Wall」 https://fastcrw.com/blog/cloudflare-ai-crawler-block-september-2026
- **何が起きているか** 【確認済（複数ソース一致）】:
  1. **AI関連クローラーが全クローラーリクエストの52%を占める（2026年6月）**。2025年春は22%だった。1年強で倍以上。
  2. 主要AIボットの**クロール対リファラル比は 118:1 から約50,000:1**。つまり「1回の送客のために数百〜数万回クロールされている」。
  3. **AIクローラーのトラフィックの50%超が、変更のないページの再取得に費やされている。**
  4. 2026年9月15日から、Cloudflare の既定設定が「mixed-use」クローラー（学習と回答生成の両方に使うボット）を、**広告を掲載しているページから**ブロックする。
  5. この既定変更が適用されるのは、**新規Cloudflare顧客・既存顧客の新規サイト・すべての既存無料プラン顧客**。既存の有料顧客の既存サイトは自動適用されない（＝自分で設定する必要がある）。
  6. Pay Per Crawl は **Pay Per Use** に移行しつつあり、**クロールされた時ではなくAI回答に登場した時に支払われる**モデル。初期パートナーは **Ceramic.ai と You.com**。
- **サイト運営者にとっての含意**: ここが**判断が割れる最重要論点**。ブロックすれば「タダで学習される」のは減るが、**AI検索経由の露出と送客も消える**。noe-match のような個人アフィリエイトメディアにとって、AI経由の送客はまだ小さいが伸びている段階であり、いま遮断するのは早い可能性が高い。一方、**Cloudflare無料プランを使っていると2026年9月15日以降「意図せず既定でブロックされる」** リスクがある。これは能動的に確認すべき。
- **日本語圏での言及**: **未検証**。【推論】Cloudflareの既定変更は日本語圏でもニュースとしては報じられやすいが、「**自分の無料プランのサイトが9月15日から既定でブロック側に入る**」という運用者目線の具体的アクションまで書いた日本語記事は少ないと推測。要検証。
- **noe-match適用度**: **A（緊急度あり）** — 具体アクション: (1) noe-match.com が Cloudflare を使っているか確認。(2) 使っていて無料プランなら、2026年9月15日前に AI crawler 設定画面を開き、**GPTBot / ClaudeBot / PerplexityBot / Google-Extended を「許可」に明示的に倒すか、ブロックを受け入れるかを意図的に決める**。放置＝ブロック側に倒れる。(3) 広告/アフィリエイトリンクを貼っているページは「広告を掲載しているページ」に該当する可能性が高く、この既定変更の直撃範囲。
- **不確実性**: (a)「広告を掲載しているページ」の判定基準（アフィリエイトリンクだけの記事が該当するか）が不明。これは noe-match にとって決定的なのに確認できていない。(b) Pay Per Use が個人サイトでも利用可能なのか、大手パブリッシャー限定かが不明。(c) 9月15日という日付は複数ソースで一致するが一次ソース未読。

---

## 8-05. OpenAI が Instant Checkout を撤回した（2026年3月）

- **一言で**: **2026年3月、OpenAI は ChatGPT内での購入完結（Instant Checkout）を約6か月で撤退**し、「チャットで発見し、購入は加盟店サイトで」に方針転換した。エージェント購買の物語が最初の現実チェックを受けた。
- **海外での出典**:
  - CNBC「OpenAI revamps shopping experience in ChatGPT after struggling with Instant Checkout offering」 https://www.cnbc.com/2026/03/24/openai-revamps-shopping-experience-in-chatgpt-after-instant-checkout.html （**2026年3月24日**）
  - Search Engine Land「OpenAI's big ChatGPT Instant Checkout plan just changed」 https://searchengineland.com/chatgpt-instant-checkout-plan-change-471033
  - Forrester「What It Means That The Leader In "Agentic Commerce" Just Pulled Back」 https://www.forrester.com/blogs/what-it-means-that-the-leader-in-agentic-commerce-just-pulled-back/
- **何が起きているか** 【確認済（複数ソース一致）】:
  1. Instant Checkout は2025年9月ローンチ、**2026年3月に撤回**。約6か月。
  2. OpenAI広報は、Instant Checkout は「Apps」へ移行し、購入は接続されたサービス内で起きる、と説明。ChatGPT本体は**商品の検索と発見**を優先する。
  3. 失敗要因として報じられているもの: 加盟店のオンボーディングが困難、商品データの正確性、複数商品カートの未対応、ロイヤルティ会員との接続不可。
  4. **根本的な問題として、ChatGPTユーザーは商品に関する質問は大量にするが、アプリ内で購入を完了しなかった**。「意図は高いが、コンバージョンしない閲覧者」だった。
- **サイト運営者にとっての含意**: これは**アフィリエイトにとって、むしろ良いニュース**。「AIがチャット内で買ってしまうから比較サイトは死ぬ」という2025年の悲観論が、少なくとも一度は現実に否定された。**発見はAI、意思決定と申込は自サイト**という構造が当面続く可能性が上がった。ただし「発見の入口をAIに握られる」構造自体は変わっていない。
- **日本語圏での言及**: **未検証**。【推論】これは**日本語圏でほぼ確実に情報が薄い典型例**。理由: (a) ローンチ（華々しい）は報じられ、撤回（地味）は報じられにくい。(b) 日本ではそもそも Instant Checkout が使えなかったため当事者意識が低い。(c) 「エージェント購買が来る」という前提で商売しているコンサルにとって、撤回は都合の悪いニュース。**要検証だが、依頼主が探している「日本に降りていない論点」の最有力候補**。
- **noe-match適用度**: **A** — (1) 記事の企画方針として、「AIに全部持っていかれる」前提の恐怖を煽る構成をやめ、「AIで見つけて、自分で比べて、自分で申し込む」導線を前提に設計する。(2) コンテンツのネタとして、この撤回自体が日本語で書かれていなければ強い。ただし婚活メディアの読者層と噛み合わないので、記事化するならメディア本体ではなく別枠。
- **不確実性**: 「撤退」が恒久的な方針転換なのか、技術的な作り直しのための一時撤退なのかは、この調査では判断できない。Forrester の分析本文を読めていないため、業界がこれをどう総括したかも未確認。

---

## 8-06. エージェント購買プロトコルが乱立している（ACP / UCP / AP2 / MCP / A2A / Visa TAP）

- **一言で**: 2026年4月時点で**6つのプロトコルが並立**しており、標準が1つに決まっていない。本番導入では2〜3個を組み合わせて使われている。
- **海外での出典**:
  - Stripe Newsroom「Stripe powers Instant Checkout in ChatGPT and releases Agentic Commerce Protocol codeveloped with OpenAI」 https://stripe.com/newsroom/news/stripe-openai-instant-checkout
  - Stripe Blog「Developing an open standard for agentic commerce」 https://stripe.com/blog/developing-an-open-standard-for-agentic-commerce
  - agenticplug.ai「State of Agentic Commerce | Protocol Tracker」 https://agenticplug.ai/current-state-of-agentic-commerce
  - Seeking Alpha「Salesforce Announces Support for Agentic Commerce Protocol in Collaboration with Stripe」 https://seekingalpha.com/pr/20264485-salesforce-announces-support-for-agentic-commerce-protocol-in-collaboration-with-stripe
- **何が起きているか**:
  1. 【確認済】ACP は Stripe と OpenAI が共同開発したオープン標準。加盟店は1回の統合でAIエージェント経由の販売を開始できる。
  2. 【要検証】**2026年4月時点で6つのプロトコル**: ACP（OpenAI/Stripe）、UCP（Google）、AP2（Google＋決済ネットワーク）、MCP（Anthropic）、A2A（Google）、Visa TAP。本番導入の多くは2〜3個を組み合わせている。
  3. 【要検証】Etsy, Glossier, SKIMS, Spanx, Vuori と100万超の Shopify 加盟店が ChatGPT Shopping で稼働。Walmart と Target が予定として発表。
  4. 【要検証】OpenAI は Instant Checkout の完了購入1件あたり**加盟店に4%の手数料**（購入者の追加負担なし）。2026年1月下旬、Shopify加盟店のオンボーディング開始時に確認された。
  5. ※ただし 8-05 の通り、Instant Checkout 自体が2026年3月に撤回されているため、3と4の状態は**既に過去のもの**である可能性が高い。**この論点は情報が急速に陳腐化している。**
- **サイト運営者にとっての含意**: **個人アフィリエイトメディアが今この標準戦争に対応する必要はない。** これらは「商品を売る事業者」向けのプロトコルであり、noe-match のような**紹介する側**は対象外。ただし「AIエージェントが読みに来る構造化された商品データ」を持つ事業者が優遇される流れは、比較メディアの中間マージンを削る方向に働く。
- **日本語圏での言及**: **未検証**。【推論】ACP と MCP は日本語圏でも話題になっているが、**「6つ並立していて決着していない」という混乱の実態**より「ACPが標準になる」という単純化された話が流通しやすい。
- **noe-match適用度**: **C** — 今すぐの作業は不要。年1回の定点観測でよい。婚活サービス（結婚相談所・アプリ）は物販ではないため、エージェント購買の直接の射程外。
- **不確実性**: 非常に高い。8-05 の撤回により、この領域の2026年前半の情報の多くが既に古い。**再調査時はこの論点を最優先で更新すべき。**

---

## 8-07. 「AI経由トラフィックは高コンバージョン」説の実際（数値が1.2倍〜23倍までばらついている）

- **一言で**: 「AI経由の訪問者はよく成約する」は**ほぼ全ての調査で方向性は一致**するが、**倍率が1.2倍から23倍までばらつく**。そしてAI経由は**全セッションの0.18%**に過ぎない。
- **海外での出典**:
  - WebFX「Study: AI Traffic Grew 796% & Out-Converts Organic Search」 https://www.webfx.com/blog/seo/gen-ai-search-trends/ （23億セッション、2024年1月〜2025年12月）
  - AirOps「AI Referral Traffic vs Organic Search: Conversion Rates and Performance Compared」 https://www.airops.com/blog/ai-referral-traffic-conversion-rates
  - kozec.ai「AI Traffic vs Organic Search Conversion Rates: 2026 Data」 https://kozec.ai/ai-sourced-traffic-conversion-rates-vs-organic-search/
  - Averi「AI Search Visitors Convert 23x Higher」 https://www.averi.ai/blog/ai-search-visitors-convert-23x-higher.-everyone-s-ignoring-it.
- **何が起きているか**:
  1. 【要検証】WebFX が**23億セッション**（2024年1月〜2025年12月）を分析: 生成AI経由トラフィックは2年で**796%成長**、コンバージョンは**約1.2倍**。
  2. 【要検証】Ahrefs: AI検索経由の訪問者は**23倍**成約（トラフィックの0.5%がサインアップの12.1%を生んだ）。
  3. 【要検証】Semrush 2026年データ: 業界横断平均で**4.4倍**。
  4. 【要検証】Opollo 2026 AI Search Benchmark Report、B2B IT・テック312社: 2026年Q1で AI検索経由**14.2%** vs Google自然検索**2.8%**。
  5. 【要検証】Adobe Digital Insights: 2026年3月、米国小売でAI経由は非AI比**42%高い**コンバージョン。
  6. 【確認済に近い】**母数が小さい**: 自然検索＋ダイレクトが全セッションの63%を占めるのに対し、**AIは0.18%**。
  7. 【要検証】**AI検索を独立したチャネルとして計測しているマーケターは14%のみ**。多くはGA4で「direct」または「referral」に誤分類している。
- **サイト運営者にとっての含意**: **倍率のばらつき自体が最も重要な情報。** 1.2倍（最大サンプル・23億セッション）と23倍（Ahrefs・自社SaaS）の差は、おそらく**測定対象の違い**（B2B SaaSのサインアップ vs 一般的なEC/メディアのコンバージョン）と**アトリビューションの誤り**（AI経由の一部がdirectに混ざり、残った分だけが高品質に見える生存バイアス）による。**「AI経由は23倍成約する」を根拠に投資判断をしてはいけない。** 最も信頼できるのは最大サンプルの1.2倍。
- **日本語圏での言及**: **未検証**。【推論】この手の「◯倍」という景気のいい数字は日本語圏でも輸入されやすいが、**ばらつきの理由や母数0.18%という冷や水**は一緒に翻訳されにくい。数字だけが独り歩きする典型パターン。
- **noe-match適用度**: **A** — 具体アクション: (1) GA4 で **AI経由を独立チャネルとして分離する設定を行う**（chatgpt.com, perplexity.ai, claude.ai, copilot.microsoft.com, gemini.google.com からの参照をカスタムチャネルグループ化）。これは今日できて、やっている日本の個人サイトは少ない。(2) 分離した上で**自分のサイトの実数**を見る。他人の倍率を信じない。
- **不確実性**: 全ての数値が二次ソース経由で、調査方法を確認できていない。特に Ahrefs の23倍は自社プロダクトのサインアップという特殊な指標。**婚活アフィリエイト（=成約まで長く、比較検討が重い）に外挿できる根拠は無い。**

---

## 8-08〜8-18. 【未調査】検索枠が尽きて着手できなかった論点

以下は依頼に含まれていたが、**検索を1回も実行できていない**。中身を書くと憶測になるため、**調べるべき問いと検索クエリのみ**を残す。再実行時はここから始めること。

### 8-08. ChatGPT Search / Atlas ブラウザ / shopping research の現況 【未調査】
- 調べる問い: Atlas ブラウザは2026年8月時点でどうなっているか。ChatGPT の引用（citation）はどう選ばれているか。OpenAI のパブリッシャー向け仕様（OAI-SearchBot と GPTBot の違い、robots.txt での制御単位）は。
- 推奨クエリ: `OpenAI Atlas browser 2026 status`, `OAI-SearchBot vs GPTBot robots.txt publisher control`, `ChatGPT search citation selection how it works 2026`

### 8-09. Perplexity / Claude / Copilot の引用ソース傾向の比較 【未調査】
- 調べる問い: 各AIがどのドメインを引用しがちか（Reddit偏重は続いているか、Wikipedia比率、一次ソース vs アフィリエイト比較サイト）。婚活のような「体験談が効く」領域でどこが引用されるか。
- 推奨クエリ: `AI citation source study 2026 Perplexity Claude ChatGPT domain overlap`, `Reddit citations AI search 2026 share`

### 8-10. Microsoft NLWeb と、サイト側がMCPを公開する動き 【未調査】
- 調べる問い: NLWeb は2026年に実際に採用されているか。「自サイトをMCPサーバーとして公開する」は個人サイトで意味があるか。
- 推奨クエリ: `NLWeb adoption 2026`, `website publish MCP server for AI agents 2026`

### 8-11. AIクローラーをブロックすべきか許可すべきかの実測データ 【未調査】
- 調べる問い: 実際にブロックしたパブリッシャーのトラフィック変化の実データ。8-04 と対になる論点。
- 推奨クエリ: `publishers blocked AI crawlers traffic impact data 2026`

### 8-12. Google の2026年アップデート履歴 【未調査】
- 調べる問い: 2026年に入ってからのコアアップデート・スパムアップデートの一覧と、その中で日本語圏で報じられていないもの。特に**アフィリエイト/レビュー系に効いたもの**。
- 推奨クエリ: `Google core update 2026 list`, `Google spam update 2026 affiliate sites impact`

### 8-13. ゼロクリック後の収益モデル 【未調査】
- 調べる問い: メールリスト・コミュニティ・ツール・有料化への移行事例と実数値。**アフィリエイトの生存条件**は何か。noe-match に最も直結する論点。
- 推奨クエリ: `zero click era publisher revenue model 2026 newsletter community`, `affiliate site survival AI search 2026`

### 8-14. 検索の分散（TikTok / Instagram / Amazon / 若年層） 【未調査】
- 調べる問い: 若年層の検索行動データの2026年版。婚活層（20代後半〜30代）がどこで情報を探しているか。
- 推奨クエリ: `Gen Z search behavior 2026 TikTok Instagram vs Google data`

### 8-15. AI Mode の2026年8月時点の展開状況と日本での提供状況 【未調査】
- 調べる問い: AI Mode は日本語・日本市場でどこまで出ているか。日本語クエリでの挙動の違い。**依頼主にとって最重要の1つ**。
- 推奨クエリ: `Google AI Mode Japan rollout 2026`, `AI Mode Japanese language availability`

### 8-16. 日本語コーパスの薄さがLLMの引用に与える影響 【未調査】
- 調べる問い: 日本語で書かれたコンテンツはAIに引用されやすいのか、されにくいのか。**「日本語圏は競合が薄い＝チャンス」が本当かの核心。**
- 推奨クエリ: `LLM citation non-English languages bias 2026`, `Japanese content AI search citation study`

### 8-17. 日本語圏SEO情報源の実態調査 【未調査】
- 調べる問い: 誰が発信していて何を扱っていないか。海外一次ソースを直接読んでいる日本語発信者は誰か。
- 注: **これは日本語検索が必須**であり、本セッションでは1回も実行できていない。

### 8-18. AI Mode における引用元の選定ロジック 【未調査】
- 調べる問い: 8-02 の fan-out の先で、**どのページが引用元に選ばれるか**。順位との相関、ドメイン権威との相関、コンテンツ形式との相関。
- 推奨クエリ: `AI Mode citation selection ranking correlation study 2026`

---

# 第2部: 日英情報ギャップの構造

⚠️ **この節は【推論】である。** 日本語圏の実態調査（8-17）を実行できていないため、以下は私の分析仮説であり、検証されたものではない。**検証方法も併記する。**

## なぜ日本のSEO情報は遅れる/歪むのか（仮説）

### 1. 翻訳のタイムラグは、実はもう主因ではない【仮説】
- 機械翻訳とLLMの普及で、英語記事を読むコストは2026年時点でほぼゼロ。**「読めない」から遅れるという説明は古い。**
- にもかかわらずギャップが残るなら、原因は言語ではなく**インセンティブ**にある。
- 検証方法: 主要な英語ニュース（例: Instant Checkout撤回、2026年3月24日）が日本語で最初に書かれた日付を調べ、タイムラグの実測値を出す。

### 2. 「肯定的な新施策」は速く伝わり、「否定的な決着」は遅く伝わる【仮説・最重要】
- 新しい施策（llms.txt を置こう、GEO対策をしよう）は**売り物になる**ので、コンサル・情報商材・SEO会社が積極的に翻訳・紹介する。
- 逆に「llms.txt は無意味だった」「Instant Checkout は撤回された」は**誰の商売にもならない**ので、紹介する動機がない。
- 結果、日本語圏には**「登り」の情報だけが蓄積し、「降り」の情報が欠落する**。日本語圏のSEO言説が実態より楽観的・施策過多に歪む主因はこれだと考える。
- 検証方法: llms.txt について、日本語記事の「推奨」記事数と「不要」記事数の比を数える。英語圏の同じ比と比較する。

### 3. 日本のSEO業界の商流【仮説】
- 日本のSEO情報の主要な発信者は**SEOツールベンダーと制作会社/代理店**であり、発信は実質的にリード獲得手段。
- そのため、(a) 自社ツールで測れることが過大に語られ、(b) 測れないこと（AI引用など）は「未知」として曖昧にされ、(c) 施策の否定は避けられる。
- 個人ブロガーによる発信は、代理店発信を二次的に要約したものが多く、**一次ソースまで遡る層が薄い**。
- 検証方法: 「AI Mode 最適化」で日本語検索し、上位20件の発信主体を分類（ベンダー/代理店/個人/メディア）し、英語一次ソースへのリンクがあるか数える。

### 4. Google日本語検索固有の事情【仮説】
- 新機能（AI Mode、Search Console の生成AIレポート等）の**日本展開が英語圏より遅い**ため、日本語圏では議論が「まだ来ていないもの」の伝聞になりがち。
- 8-01 の例: 生成AIレポートは2026年6月時点で**英国の一部**のみ。日本の実務者は手元で検証できないので、記事は英語記事の要約にしかならず、精度が落ちる。
- 検証方法: AI Mode / 生成AIレポートの日本提供状況を確認（8-15）。

### 5. 日本語コーパスの薄さ【仮説・未検証・慎重に扱うこと】
- LLMの学習・引用において日本語コンテンツの比重が小さいなら、日本語で書いても引用されにくい可能性がある。
- **だがこれは逆方向にも働きうる**: 日本語で書かれた良質なコンテンツが少ないなら、少数の良質な日本語ページが引用を独占する可能性もある。
- **どちらが正しいか、私は確認していない。** これは 8-16 で必ず検証すべき。

## 「日本語圏に情報が薄い＝チャンス」はどこまで本当か

依頼主の仮説を、私が確認できた範囲で採点する。

**本当だと考えられる部分:**
- **「否定的な決着」の情報ギャップは実在する可能性が高い**（仮説2）。llms.txt が無意味だったこと、Instant Checkout が撤回されたことは、日本語圏で薄い可能性が高く、かつ**知っていると無駄な工数を払わずに済む**という実利がある。これは本物のアドバンテージ。
- **一次ソースを直接読む習慣そのもの**がアドバンテージ。競合が二次情報を読んでいる間に一次情報で判断できる。

**本当ではない、または危険な部分:**
- **「情報が薄い＝そのテーマで記事を書けば勝てる」は成立しない。** 情報が薄い理由が「日本の読者に需要がないから」である可能性が高い。婚活メディアの読者は Agentic Commerce Protocol を検索しない。**情報ギャップは「自分の意思決定の質」には効くが、「集客できる記事ネタ」としては効かない場合が多い。**
- **翻訳して先出しするだけの戦略は寿命が短い。** 2026年時点では誰でもLLMで翻訳できるため、先行できるのは数日〜数週間。
- **依頼主の例に挙がった「観光庁のデータをまとめてデータバンクにする」は、情報ギャップの話ではなく「一次データの独自加工」の話。** これは別の（そしてより強い）戦略であり、混同しないほうがよい。一次データ加工は**翻訳より遥かに模倣されにくい**。

**結論【推論】**: 情報ギャップは **noe-match の運営判断（何をやらないか）を良くする** 効果はかなり大きい。一方 **集客コンテンツのネタとしての価値は限定的**。依頼主は前者を目的にすべきで、後者を期待すると外す。

---

# 第3部: 海外一次ソースの定点観測リスト

⚠️ **本セッションでは外部サイトへの接続が全面遮断されていたため、以下のURL・更新頻度・RSS有無は到達確認できていない。** 広く知られた媒体を記載しているが、**初回アクセス時にURLとRSSを各自で確認すること。**

| # | 媒体名 | URL | 更新頻度 | 何が得られるか | RSS |
|---|---|---|---|---|---|
| 1 | Google Search Central Blog | https://developers.google.com/search/blog | 月数回 | **一次ソース最重要**。アップデート、Search Console新機能、公式ガイダンス | あり |
| 2 | Google Search Status Dashboard | https://status.search.google.com/ | 随時 | ランキング更新・障害の公式記録。**日付の裏取りに使える** | 要確認 |
| 3 | Search Engine Roundtable (Barry Schwartz) | https://www.seroundtable.com/ | 毎日複数 | 業界の一次情報を最速で拾う。Google社員の発言を逐一記録 | あり |
| 4 | Search Engine Land | https://searchengineland.com/ | 毎日 | ニュースの標準。速報性と網羅性 | あり |
| 5 | Search Engine Journal | https://www.searchenginejournal.com/ | 毎日 | 同上。解説寄り | あり |
| 6 | Cloudflare Blog | https://blog.cloudflare.com/ | 週数回 | **AIクローラー・pay per crawl の一次ソース**。8-04の震源地 | あり |
| 7 | Cloudflare Radar | https://radar.cloudflare.com/ | 随時 | AIボットのクロール量の実データ | 要確認 |
| 8 | OpenAI Blog / News | https://openai.com/news/ | 週数回 | ChatGPT検索・ショッピング・Atlas の一次発表 | 要確認 |
| 9 | OpenAI Platform Docs (bots) | https://platform.openai.com/docs/bots | 随時 | **GPTBot / OAI-SearchBot / ChatGPT-User の公式仕様**。robots.txt設計の根拠 | なし |
| 10 | Anthropic News | https://www.anthropic.com/news | 週数回 | Claude / MCP の一次発表 | 要確認 |
| 11 | Stripe Blog | https://stripe.com/blog | 月数回 | ACP・エージェント決済の一次ソース | 要確認 |
| 12 | Ahrefs Blog | https://ahrefs.com/blog/ | 週数回 | **大規模実データ調査**。llms.txt 137Kサイト調査等。数字の信頼度が高い | あり |
| 13 | Semrush Blog / Research | https://www.semrush.com/blog/ | 週数回 | 大規模データ。AI検索トラフィック調査 | あり |
| 14 | Kevin Indig (Growth Memo) | https://www.kevin-indig.com/ | 週1 | **一次データ分析＋戦略**。翻訳されにくい深さ | あり |
| 15 | Aleyda Solis (SEOFOMO) | https://www.aleydasolis.com/en/seofomo/ | 週1 | 週次まとめニュースレター。**これ1本で英語圏の週次動向を追える。最優先** | メール |
| 16 | iPullRank (Mike King) | https://ipullrank.com/blog | 月数回 | 技術的に最も深い。AI検索の内部構造の推論 | あり |
| 17 | Search Engine Land - SEO newsletter | https://searchengineland.com/newsletter | 平日毎日 | メールで漏らさず追う用 | メール |
| 18 | The Verge (AI) | https://www.theverge.com/ai-artificial-intelligence | 毎日 | AI業界の大きな方向転換（Instant Checkout撤回等）はここが速い | あり |
| 19 | CNBC Technology | https://www.cnbc.com/technology/ | 毎日 | 事業側の一次報道。8-05の出典 | あり |
| 20 | TechCrunch | https://techcrunch.com/ | 毎日 | 同上。8-04の出典 | あり |
| 21 | Forrester Blogs | https://www.forrester.com/blogs/ | 週数回 | アナリストの総括。「で、結局どうなったのか」の答え合わせ | 要確認 |
| 22 | Adobe Digital Insights | https://business.adobe.com/resources/digital-insights.html | 月次 | **実購買データに基づくAI経由トラフィック分析**。小売寄りだが数字が固い | 要確認 |
| 23 | Similarweb Insights | https://www.similarweb.com/blog/insights/ | 月数回 | AI検索の利用実態・トラフィックシェアの実測 | 要確認 |
| 24 | Google Search Central (YouTube) | https://www.youtube.com/@GoogleSearchCentral | 月数回 | Office Hours。Mueller等の発言の一次ソース | あり |
| 25 | Pew Research Center - Internet & Tech | https://www.pewresearch.org/topic/internet-technology/ | 月次 | **検索行動・若年層の情報接触の中立的な調査**。ベンダー調査のバイアス補正に使う | あり |

**運用の推奨【推論】**: 個人運営で25本は現実的でない。**#15 (SEOFOMO) と #3 (Search Engine Roundtable) の2本を週次で読み、月1回 #1 (Search Central) と #6 (Cloudflare Blog) を確認する**だけで、日本語圏の大半より先行できる。

---

## 領域8の未解決事項

### A. 本調査の実行上の欠落（最優先で再実行すべき）
1. **WebSearch枠の枯渇により、依頼された25回中8回しか検索できていない。** 論点8-08〜8-18は完全に未着手。
2. **外部サイトへのHTTP接続が全面遮断されており、英語一次ソースの本文を1本も読めていない。** 全ての記述が検索スニペット経由の間接情報。
3. **日本語での対応検索を1回も実行できていない。** これは依頼の中核（手順2）であり、「日本語圏での言及」欄は全て未検証。**第2部の情報ギャップ分析も、この検証なしには仮説の域を出ない。**
4. → **再実行時は、日本語検索を先に確保すること。** 英語側の情報は本レポートで7論点ぶん確保できているので、次は日本語側の実態調査（8-17）から始めるのが効率的。

### B. 内容上の未解決事項
5. **Cloudflare の「広告を掲載しているページ」にアフィリエイトリンクのみの記事が含まれるか。** noe-match への影響を決める分岐点だが未確認。2026年9月15日が迫っており、**時間的余裕がない**。
6. **Search Console 生成AIレポートの日本展開時期。** および AI Mode のクリックが既存Performanceレポートに合算されているか別枠か。
7. **AI Mode の日本語・日本市場での提供状況**（8-15）。依頼主にとって最も実務的な問いだが未調査。
8. **日本語コンテンツがLLMに引用されやすいのか、されにくいのか**（8-16）。「日本語圏は競合が薄い＝チャンス」仮説の成否を分ける核心だが、私は**どちらの方向かすら確認していない**。
9. **llms.txt の提唱者側（Answer.AI / Jeremy Howard）の2026年時点の反論を確認していない。** 8-03は否定側のソースのみで構成されており、片側からしか見ていない。
10. **AI経由コンバージョン倍率のばらつき（1.2倍〜23倍）の原因**が特定できていない。測定方法の違いか、生存バイアスか、業種差か。**婚活領域に外挿できる根拠は現時点で無い。**
11. **エージェント購買プロトコル領域（8-06）は、Instant Checkout撤回により2026年前半の情報が既に陳腐化している。** 現状の再確認が必要。

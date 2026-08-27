# 領域4: テクニカルSEO/情報設計

- 調査日: 2026-08-27
- 参照ソース数: 英語一次・準一次ソース 約70件（26回のWeb検索経由）／日本語検証検索 2件＋既知の日本語SEOメディア知見
- 担当領域: 「海外では常識だが日本語圏のSEO情報でほとんど流通していない」テクニカル/情報設計手法の羅列

## 調査上の制約（先に明記）

1. **WebFetchが本セッションのegressプロキシで全ドメイン遮断された**ため、一次ソース（Google Patents本文、developers.google.com、QRG PDF本体、iPullRank記事本文）の直接精読はできていない。URLは検索インデックス上で実在を確認したものだが、**本文の逐語引用ではなく検索結果サマリ経由の要約**である。数値を実務判断に使う前に、記載URLを直接開いて原文確認すること。
2. **Web検索クォータ（セッション200回）を消費しきった**ため、後半の数手法（EXIF/オリジナル画像、地域シグナル/NAP、HTMLテーブルとAI引用率）は専用検索を打てておらず、既存ソース＋当方の知識ベースでの記述となる。該当箇所には「※専用検索未実施」と明記した。
3. **日本語言及度**は、実検索したのは「情報利得/インフォメーションゲイン」「コンテンツプルーニング」の2クエリのみ（クォータ制約）。残りは日本語SEOメディア（Web担当者Forum、LANY、ナイル、ミエルカ、SEO Japan、バズ部、Faber Company系）の流通状況に関する当方の知識に基づく推定であり、**「実検索で検証済」と「推定」を各項目で区別して書いた**。
4. Google公式見解と実務家の実測は必ず分けて書いた。両者が食い違う論点（プルーニング、CWV、日付更新、クリック信号）は「反証」欄に対立を残してある。

## noe-match側の実測（本ドキュメントの適用度判定の前提）

リポジトリを実査した結果（2026-08-27時点）:

| 項目 | 実測値 |
|---|---|
| `articles/` 配下の記事ディレクトリ | 256 |
| sitemap-all.xml の `<loc>` 数 | 230（=**約26記事がサイトマップ未収録**） |
| Article schema を持つ記事 | 132 |
| BlogPosting schema を持つ記事 | 77（=**同一サイト内で型が混在**） |
| Article/BlogPosting どちらも無い記事 | 48 |
| `dateModified`/`datePublished`/`author` を持つ記事 | 各208 |
| `author` の @type | **全件 `Organization`（"Noe編集部"）。`Person` は サイト全体で0件** |
| 他記事から被リンク0の記事（内部オーファン） | **59件（256中23.0%）** |
| 被リンク最多 | matching-app-ranking（99本）／2位 kekkon-okane-data（44本） |
| `<table>` を使う記事 | 206 |
| `<dl>`（定義リスト）を使う記事 | **0** |
| 記事あたり平均 `<h2>` 数 | 10.8 |
| FAQPage schema | 226記事（実装済み） |

この実測値が、以下の各手法の「noe-match適用度」の根拠になっている。

---

## 4-01. インフォメーションゲイン・スコア（Information Gain Score）

- **一言で**: 「すでにユーザーが読んだ他のページに**載っていない情報**をどれだけ足しているか」を機械学習で採点するGoogle特許。スカイスクレイパー（上位記事の焼き直しで長くする）の真逆の設計思想。
- **海外での出典**:
  - Google Patents US11354342B2 "Contextual estimation of link information gain"（発明者 Victor Carbune / Pedro Gonnet、2018-10-18出願、2022-06-07付与）https://patents.google.com/patent/US11354342B2/en
  - 同ファミリー US20200349181A1 https://patents.google.com/patent/US20200349181A1/en
  - Search Engine Journal「Google's Information Gain Patent For Ranking Web Pages」https://www.searchenginejournal.com/googles-information-gain-patent-for-ranking-web-pages/524464/
  - Semrush「What Is Information Gain in SEO & Does Google Measure It?」https://www.semrush.com/blog/information-gain/
- **仕組み／なぜ効くか**: 特許の記載では、「ユーザーが既に閲覧した文書群」と「まだ提示していない新規文書」の両方を学習済みモデルに入力し、**新規文書が追加でもたらす情報量**をスコアとして出力する。つまり絶対評価ではなく**SERP上の他ページとの差分の相対評価**。SEJの解説によれば、同一発明が7年間で4回再付与されており、Googleが放棄していない証拠とされる。特許の文脈の多くは自動アシスタント／チャットボット向けであり、**AI OverviewsやAI Modeの引用選定ロジックへの示唆**として読むのが妥当。
- **具体手順**:
  1. 対象クエリのSERP上位10件を取得し、各記事の`<h2>/<h3>`をすべて書き出して「共通見出し集合」を作る（Pythonで十分）。
  2. 共通見出し＝コモディティ情報。ここは**最短で正確に**書き、差別化には使わない。
  3. 「どこにも無い要素」を最低3つ入れる。順に実効性が高いのは (a) 一次データ（自分で取った数値）、(b) 一次体験（実際にやった記録・スクショ）、(c) 独自の切り口の分類・比較表、(d) 反証・例外条件。
  4. 各記事の冒頭200字以内に「この記事にしかない情報」を明示する（AI要約器が拾う位置に置く）。
  5. 記事メタに「独自要素タグ」を持たせ、Python生成時に独自要素0の記事を検出してフラグを立てる。
- **日本での言及度**: **低**（※実検索で検証済）。日本語クエリ「"情報利得" SEO インフォメーションゲイン Google特許」で、SEO GEEKS（https://seogeeks.jp/blog/information-gain-seo/ ）、assisty（https://assisty.jp/column/20251202/ ）、集客ジョーズ（https://seo-adshark.com/blog/information-gain/ ）等が2025年末〜のヒット。**用語自体は日本にも入り始めているが、記事は「独自情報を書こう」という精神論に収束しており、SERP見出し差分の定量化・実装手順まで書いた日本語記事は見当たらない**。大手SEOメディア（Web担、ナイル、LANY）の主要記事に定着した用語ではない。
- **noe-match適用度**: **A**。婚活ジャンルは他社記事の焼き直しが極めて多く、差分を作れば効きやすい。しかも既にサイト内にツール（結婚率計算、恋愛費用シミュレータ等の`WebApplication` schema 17件）と`data_bank.md`があるので、「自前の数値」という最強の情報利得ソースを持っている。想定工数: SERP見出し差分スクリプト（`scripts/`に1本、半日）＋記事あたり30分の独自要素追加。
- **リスク・反証**: **特許＝実装の証明ではない**。Googleは「Information Gain Scoreというランキング要素がある」と公式に述べたことは一度もない。Semrushも「Googleが測定しているかは未確認」というトーンで書いている。また特許本文の主眼は会話型アシスタントであり、通常のWeb検索ランキングに直輸入できる保証はない。**「独自情報を足す」という行動自体は helpful content ガイドラインとも整合するのでノーリスク**だが、「情報利得スコアが上がったから順位が上がる」という因果の言い切りは避けること。

---

## 4-02. コンテンツ・プルーニング／統合（Content Pruning / Consolidation）

- **一言で**: 低品質・低トラフィックのページを削除または統合すると、**残ったページの評価が上がる**という海外の定説。ただしGoogle公式はこれを明確に否定しており、SEO界で最も大きな「公式 vs 実測」の対立点のひとつ。
- **海外での出典**:
  - Search Engine Land「Google warns against content pruning as CNET deletes thousands of pages」https://searchengineland.com/google-warns-against-content-pruning-as-cnet-deletes-thousands-of-pages-430509
  - Search Engine Roundtable「Google Says Removing Content Doesn't Make The Other Content Rank Higher In Search」https://www.seroundtable.com/google-removing-content-36097.html
  - Google公式「Creating Helpful, Reliable, People-First Content」https://developers.google.com/search/docs/fundamentals/creating-helpful-content
  - Search Engine Journal「Google Explains Which Pages Should be Removed」https://www.searchenginejournal.com/google-explains-content-pruning/371252/
  - Inflow（Home Science Tools事例、戦略コンテンツ収益+64%）https://www.goinflow.com/blog/content-pruning-case-study/
  - SEO.ai（CNETの削除後データ分析）https://seo.ai/blog/content-pruning-case-study-cnet
- **仕組み／なぜ効くか（実務家側の理屈）**: (1) サイト全体の品質期待値（leakで言うところの site-level 信号）を押し上げる、(2) インデックス肥大（index bloat）を解消しクロール予算を有効ページに寄せる、(3) 統合により内部リンクと被リンクの評価を1URLに集約する、(4) カニバリを同時に解消する。Inflowはコンテンツ監査＋プルーニングで戦略コンテンツ収益+64%を報告。他に「index bloat修正でオーガニック+28%」「統合でクリック+92%」といった事例が集積している（https://www.goinflow.com/blog/content-pruning-case-study/ ）。
- **Google公式の見解（必ず区別）**: John Muellerは X で「**removing content doesn't make the rest rank higher**（コンテンツを削除しても残りの順位は上がらない）」と明言（https://www.seroundtable.com/google-removing-content-36097.html ）。またhelpful contentガイドラインの自己評価質問に「サイトを『新鮮』に見せて順位を上げようとして大量のコンテンツを追加/削除しているか？（No, it won't）」という項目が明記されている（https://developers.google.com/search/docs/fundamentals/creating-helpful-content ）。Mueller/Illyesはいずれも「可能な限り削除ではなく改善を」と述べている。またMuellerは「アクセスが無い＝低品質ではない」「Aboutページのように独自価値のあるページは低トラフィックでも消すな」とも述べている。
- **具体手順**:
  1. GSCの16ヶ月データを全URLでエクスポートし、`clicks`・`impressions`・`position`・被リンク（内部/外部）・最終更新日をURL単位で1テーブルに結合。
  2. 分類を4値に固定する: **維持 / リライト（refresh） / 統合（consolidate） / 削除（prune）**。判定は単一指標にしない（Mueller警告に従う）。
  3. 統合を最優先にする。統合先を決め、統合元は**301リダイレクト**（noindexや404ではなく）で評価を渡す。
  4. 削除は「独自価値ゼロ＆被リンクゼロ＆12ヶ月クリック0＆改善見込みなし」の4条件AND、かつ全体の数%以内に留める。
  5. 実行前後の**日付とURLリストを記録**し、90日後にサイト全体のインプレッションで前後比較する（削除の効果は個別ページではなくサイト全体でしか観測できない）。
- **日本での言及度**: **中**（※実検索で検証済）。「コンテンツプルーニング 記事削除 SEO 低品質ページ 統合 効果」で、Web担当者Forumの「低品質コンテンツは削除すべき？改善すべき？ ゲイリーの正論vsランドの現実」（https://webtan.impress.co.jp/e/2017/10/20/27173 ）、LANY（https://www.lany.co.jp/blog/low-quality-content ）などが上位。**「低品質コンテンツ削除」という文脈では日本にも十分流通している**。ただし (a) `content pruning`という英語術語、(b) refresh/consolidate/pruneの4分類フレーム、(c) サイト全体インプレッションでの前後測定という**方法論としての厳密さ**は日本語圏で手薄。日本語記事の多くは「削除すべきか改善すべきか」の二択論に留まっている。
- **noe-match適用度**: **B**。ドメイン開設2026年6月で**まだ2ヶ月半**。この段階でのプルーニングは時期尚早（そもそも評価が定まっていないページを消しても測れない）。ただし**統合（consolidate）は今すぐ価値がある**：256記事中`article-3`/`article-7`/`article-17`/`article-33`のような汎用スラッグ記事が複数あり、これらは高確率でテーマ重複している。想定工数: 統合候補の抽出スクリプト半日＋統合作業1本30分。`redirects.json`が既に存在するのでリダイレクト機構は流用できる。**削除は最低でもドメイン12ヶ月経過まで凍結を推奨**。
- **リスク・反証**: 上記の通りGoogle公式は効果を明確に否定している。CNETの大量削除は海外でも「Googleが警告した」事例として報じられており、成功事例として引用するのは危険。さらに削除は**不可逆**で、当時トラフィックが無くても後から伸びる記事はある。GitHub Pagesの静的サイトでは404が即座に発生するため、必ず301（`redirects.json`経由）を挟むこと。

---

## 4-03. トピカルオーソリティの定量設計（Topical Map / Koray Framework）

- **一言で**: 「関連記事を増やす」ではなく、**中心エンティティ→中心検索意図→コアセクション／アウターセクション**という階層でトピック網羅率を設計図として先に確定させ、その順序で公開していく手法。
- **海外での出典**:
  - Koray Tuğberk Gübür / Holistic SEO「What is Topical Authority?」https://www.holisticseo.digital/theoretical-seo/topical-authority/
  - 「How to Expand a Topical Map for Higher Topical Authority?」https://www.holisticseo.digital/seo-research-study/topical-map
  - Semantic SEO Glossary（Koray用語集）https://rokonz.com/resources/semantic-seo-glossary
  - The Koray Framework Explained https://topicalmap.services/koray-framework/
  - Koray本人のMedium https://medium.com/@ktgubur/korays-agents-generative-ai-agents-for-semantic-seo-and-topical-authority-d4b247fac72a
- **仕組み／なぜ効くか**: フレームワークは5要素で構成される。**Source Context**（サイトの収益方法・アイデンティティ）、**Central Entity**（サイト全体を貫く中心実体）、**Central Search Intent**、**Core Section**（Source Context × Central Search Intent の交差＝収益直結領域）、**Outer Section**（収益に直結しないが、トピック網羅と履歴データ・文脈統合のために必要な領域）。「関連語を全部書く」のではなく、**Core を先に完成させてからOuterに広げる順序**が要点とされる。見出し（headings）は"contextual vector"として設計され、クエリ長分布から想定される文脈の幅に合わせる。
- **具体手順**:
  1. Source Context を1文で確定（noe-matchなら「婚活サービス比較アフィリエイト」）。
  2. Central Entity を1つに絞る（「結婚」なのか「婚活」なのかで地図が全く変わる）。
  3. Core Section: 中心意図 × 収益ポイントの交差だけを列挙し、抜けをゼロにする。
  4. Outer Section: 収益に直結しない周辺（統計、制度、法律、費用の背景知識）を列挙。
  5. 各ノードに「代表クエリ／見出し構成（contextual vector）／内部リンク先」を書いた設計表を作り、**この表をPython生成の入力データにする**。
  6. Core完成率を%で管理し、Coreが100%になるまでOuterに手を出さない。
- **日本での言及度**: **ほぼ無**（※推定。「トピッククラスター」「ピラーページ」は日本語で流通しているが、**Koray Tuğberk Gübür の名前と Source Context / Central Entity / Core Section / Outer Section という語彙は日本語SEO記事でほぼ見ない**）。日本語で流通しているのはHubSpot由来の「ピラー＋クラスター」までで、**Core/Outerの順序制約や「歴史データ（historical data）」という概念は紹介されていない**。日本語圏で最も手薄な領域のひとつ。
- **noe-match適用度**: **A**。すでに`cluster_map.md`・`cluster_candidates_2026-08-16.md`・`garugaru_cluster_plan.md`があり、クラスタ設計の下地は存在する。それをKoray式に**Core/Outer二層で再ラベリング**し、Core完成率を出すだけで、次に書く記事の優先順位が機械的に決まる。Python生成サイトなのでトピカルマップをJSONにしてビルドの入力にでき、相性は極めて良い。想定工数: 既存クラスタ資料の再構成に1〜2日。
- **リスク・反証**: **Koray式は本人の提唱であってGoogleの公式概念ではない**。Google自身は「topical authority」という語をランキングシステム名として公式には使っていない（John Muellerは「トピカルオーソリティという特別なスコアは無い」という趣旨の発言を繰り返している）。またOuter Sectionの大量生産は、helpful contentガイドラインの「順位のためにコンテンツを大量追加していないか」に抵触しうる。**Coreの完成を優先し、Outerは実際に読者価値がある範囲に留める**のが安全側。

---

## 4-04. クエリ・カニバリゼーションの機械的検出（GSC API × page-query 1:1マッピング）

- **一言で**: GSC APIで `dimensions=['page','query']` を取り、**同一クエリで2URL以上が露出している組**を機械的に抽出して、1クエリ1URLに正規化する。
- **海外での出典**:
  - JC Chouinard「Find Keyword Cannibalization Using Google Search Console and Python」https://www.jcchouinard.com/keyword-cannibalization-tool-with-python/
  - GitHub: allanreda/SEO-Keyword-Cannibalization-Detector https://github.com/allanreda/SEO-Keyword-Cannibalization-Detector
  - Advanced GSC「How to Find Keyword Cannibalization in Google Search Console」https://www.advancedgsc.com/blog/keyword-cannibalization-google-search-console
- **仕組み／なぜ効くか**: GSC APIは`page`と`query`を同時ディメンションで返せるため、**{query, URL}ペアごとのclicks/impressions/position/CTRが全件取れる**（1リクエストあたり最大25,000行）。同一クエリが複数URL行に現れる＝カニバリ候補。深刻度の判定基準として海外で使われている閾値は「**順位差 < 3 かつ インプレッション比 > 0.5 なら High**」（https://www.advancedgsc.com/blog/keyword-cannibalization-google-search-console ）。カニバリは内部リンクの評価分散とGoogleの正規URL判断の揺れを生むため、解消するとクリックが1URLに集約される。
- **具体手順**:
  1. GSC API（`searchanalytics.query`）で過去90日、`dimensions=['query','page']`、`rowLimit=25000`、ページングして全件取得。
  2. pandasで `groupby('query')` → `nunique('page') >= 2` を抽出。
  3. 各クエリについて順位差とインプレッション比を計算し、High/Mid/Low に3分類。
  4. Highのみ手当て：**勝たせるURLを1つ決め**、負けURLからそのクエリの見出し・本文言及を薄め、負けURL→勝ちURLへ内部リンク（アンカーテキストは当該クエリ）を張る。
  5. 統合すべきレベル（内容がほぼ同一）なら4-02の統合フローへ回す。
  6. 「クエリ→正URL」の対応表をリポジトリにJSONで保持し、次回以降の記事生成時に**新記事が既存の正URLのクエリを侵食していないか**をビルド時にチェックする。
- **日本での言及度**: **中**（※推定）。「キーワードカニバリゼーション」という語は日本語SEO記事に十分あり、GSCのフィルタでの手動確認手順も紹介されている。しかし**「GSC APIでpage×query全件を取ってpandasで自動判定し、順位差<3・インプレッション比>0.5という定量閾値で深刻度を切る」というレベルの実装記事は日本語でほぼ見ない**。さらに「クエリ→正URLの1:1マッピングをリポジトリに永続化してビルド時に検証する」という運用は日本語圏で紹介例を知らない。
- **noe-match適用度**: **A**。すでに`gsc_data.json`があり、GSCデータの取得パイプラインが存在する。256記事・婚活という語彙の狭いジャンルは**構造的にカニバリが起きやすい**（「婚活アプリ おすすめ」系が複数記事に散っている可能性が高い）。想定工数: 検出スクリプト半日、対応表の運用組み込み半日。Python生成サイトなのでビルド時チェックまで実装できるのが強み。
- **リスク・反証**: GSCの`page`×`query`同時取得は**行数制限とデータの間引き（anonymized queries）**があり、ロングテールは取りこぼす。またGoogle公式は「カニバリゼーション」という概念自体をランキングシステムとして認めておらず、Muellerは「複数ページが同じクエリで出るのは普通のこと」という趣旨の発言をしている。**同一クエリで2URLが出る＝必ず悪、ではない**（ナビゲーショナルな指名クエリでは正常）。閾値でHighに絞ること。

---

## 4-05. ストライキングディスタンス分析（Striking Distance / 11〜20位の刈り取り）

- **一言で**: 11〜20位（2ページ目）のクエリだけを抽出し、**そのクエリの語が本文に実際に含まれているかを機械的に照合**して、欠落している語を埋めて1ページ目に押し上げる。
- **海外での出典**:
  - Search Engine Journal「Using Python + Streamlit To Find Striking Distance Keyword Opportunities」https://www.searchenginejournal.com/python-seo-striking-distance/423009/
  - RicketyRoo「Striking Distance Keywords: How to Find Them—and What to Do with Them」https://ricketyroo.com/blog/striking-distance-keywords/
  - Content Raptor「Striking Distance Keywords: How to Find and Optimize Them with GSC」https://contentraptor.com/blog/striking-distance-keywords-gsc/
- **仕組み／なぜ効くか**: 11〜20位は「Googleが既にそのページを当該クエリで関連ありと判断しているが、あと一歩」という状態。ゼロから作るより圧倒的に安い。SEJの手法の肝は、**GSCのクエリと本文テキストを突き合わせ「タイトルに含むか/H1に含むか/本文に含むか」の3列の真偽表を出す**こと。含まれていない語＝Googleが文脈から推測して露出させているだけの語であり、明示するだけで順位が動きやすい。優先度は `impressions ×（順位3のCTR − 現在のCTR）` の機会損失スコアで並べる（https://contentraptor.com/blog/striking-distance-keywords-gsc/ ）。
- **具体手順**:
  1. GSC APIまたはCSVエクスポートで過去3ヶ月の `query, page, clicks, impressions, position` を取得。
  2. `10 < position <= 20` かつ `impressions >= N`（サイト規模に応じ10〜50）でフィルタ。
  3. URLごとにクエリをグルーピング（1ページに対して複数の striking クエリが付く）。
  4. 各URLの静的HTMLを読み、クエリを形態素分割して **title / h1 / h2群 / 本文** それぞれに出現するかの真偽表を作る（日本語なので`janome`か`sudachipy`で分割。単純な部分文字列一致でも実用上は機能する）。
  5. 「本文にすら無い」語を優先的に、既存の文脈に自然に組み込む（新見出しを1つ足すのが最も安全）。
  6. 30〜60日後に同じクエリの position を再取得して差分を記録。
- **日本での言及度**: **低**（※推定）。「あと少しで1ページ目のキーワード」「順位11〜20位を狙う」という概念は日本語記事にもある。しかし**"striking distance" という術語と、SEJのPython実装（クエリ×本文の真偽表を自動生成する部分）は日本語圏でほぼ紹介されていない**。日本語記事は「2ページ目のキーワードをリライトしよう」という粒度で止まり、「どの語が欠けているか」を機械的に出す部分が欠落している。
- **noe-match適用度**: **A（最優先候補）**。ドメイン2ヶ月でまだ11〜20位の母数が小さい可能性はあるが、インデックス申請運用で90-100%インデックス済とのことなので、露出は既にあるはず。**静的HTMLなので本文テキストの機械照合が異常にやりやすい**（DBもレンダリングも不要、`articles/*/index.html`を読むだけ）。想定工数: 1日。既存の`scripts/`にもう1本足すだけ。
- **リスク・反証**: 「順位12→6で流入5〜10倍」といった倍率はソースにより幅があり、クエリのCTRカーブ次第で大きく変わる。また**キーワードを機械的に本文に足すのはキーワードスタッフィングに退化しやすい**。「欠落語リスト」はあくまで**書くべき内容の欠落を示すシグナル**として使い、語を挿入するのではなく**その語について書くべき段落・見出しを1つ足す**という運用にすること。AI検索時代には、そもそも「語が入っているか」より「その意図に答える段落があるか」が効くという指摘もある（4-16 query fan-out 参照）。

---

## 4-06. 内部リンクスカルプティングとPageRankフロー（Internal Link Sculpting）

- **一言で**: 内部リンクを「関連記事を貼る」ではなく**評価の配管**として設計し、どのページにどれだけ流すかを意図的に配分する。
- **海外での出典**:
  - Digital Applied「Internal Linking Strategy & Topical Authority Playbook」https://www.digitalapplied.com/blog/internal-linking-strategy-topical-authority-playbook-2026
  - Uprankd「How Google Really Interprets Internal Links (Beyond PageRank)」https://uprankd.com/news/guides/how-google-interprets-internal-links-beyond-simple-page-rank-flow
  - ClickRank「PageRank Sculpting: 2026 Guide to Internal Link Equity」https://www.clickrank.ai/pagerank-sculpting/
  - mean.ceo「The Startup Guide to Internal Link Sculpting」https://blog.mean.ceo/startup-internal-link-sculpting/
- **仕組み／なぜ効くか**: 3つのサブ手法が海外では標準扱い。
  - **First-link priority**: 同一ページから同一URLへ2回リンクした場合、Googleは歴史的に**最初のアンカーテキストを重く見る**とされる。よって「本文最初の1回に最良のアンカーを置く」（https://www.clickrank.ai/pagerank-sculpting/ ）。
  - **アンカーテキスト分布**: 完全一致5〜10%、部分一致25〜35%、残りをブランド／汎用にする配分が推奨されている（同上）。同一アンカーの過剰は共起の不自然さを生む。
  - **クリック深度**: ホームから3クリック以内のページが優先的にクロールされ、インデックスが速いとされる。4クリック以上に埋もれたページは「重要でない」と解釈されやすい。
- **具体手順**:
  1. 全記事HTMLをパースして**内部リンクの有向グラフ**を作り、各URLの被リンク数（indegree）とホームからの最短クリック距離を計算する。
  2. indegreeの分布を見て、**上位1%に集中しすぎ／下位に0が多い**という偏りを可視化する。
  3. 収益ページ（比較・ランキング）をハブに指定し、そこへ流すノードを明示的に増やす。
  4. 各ページの本文で、同一URLへの複数リンクがある場合は**最良アンカーを最初のリンクに移動**する。
  5. アンカーテキストの全件集計を取り、完全一致比率が高すぎるURLを是正。
  6. これらを**Python生成テンプレートのルールとして固定**し、手作業ではなくビルドで担保する。
- **日本での言及度**: **低〜中**（※推定）。「内部リンク最適化」は日本語で頻出だが、**"first link priority"（同一ページ内の最初のリンクが優先される）という具体則、アンカーテキスト分布の数値レンジ、内部リンクを有向グラフとして解析するアプローチ**は日本語記事でほぼ扱われていない。日本語記事は「関連記事を貼りましょう」「パンくずを設置しましょう」の粒度が中心。
- **noe-match適用度**: **A**。実測で **被リンク上位は matching-app-ranking が99本、次点44本と極端な冪分布**で、収益ページへの集中自体は設計されている。一方で下位側が問題（4-07参照）。**Python生成なので、リンク配置ルールをテンプレートに書けば256記事に一括適用できる**のが最大の利点。想定工数: グラフ解析スクリプト半日、テンプレート改修1日。
- **リスク・反証**: **`nofollow` によるPageRankスカルプティングは2009年にGoogleが無効化済み**（nofollowリンク分のPageRankは蒸発するだけで他リンクに再分配されない）。ClickRank等が「link sculpting」と呼んでいるのは**リンクを張る/張らないという構造設計**であって、nofollow操作ではない。**nofollowを使ったスカルプティングは絶対にやらないこと**。またfirst-link priorityは古い実験に基づく通説で、Googleが現在も同じ挙動である公式確認はない。

---

## 4-07. オーファンページ検出（Orphan Page Detection）

- **一言で**: 「サイトマップには載っているが、**どのページからも内部リンクされていない**」ページを機械検出して救出する。
- **海外での出典**:
  - Digital Applied（オーファン検出を四半期監査項目として明記）https://www.digitalapplied.com/blog/internal-linking-strategy-topical-authority-playbook-2026
  - Uprankd「A page buried four clicks from the homepage with no internal links pointing to it is a page Google is likely to crawl rarely and rank poorly, no matter how good the content is.」https://uprankd.com/news/guides/how-google-interprets-internal-links-beyond-simple-page-rank-flow
  - Search Engine Land Website Structure Guide https://searchengineland.com/guide/website-structure
- **仕組み／なぜ効くか**: 内部リンクゼロのページはPageRankを一切受け取らず、サイトマップ経由でクロールはされてもトピック的文脈（どのクラスタに属するか）をGoogleに伝えられない。オーファンは**サイトマップとクローラの差分**でしか見つからないため、多くの運営者が存在に気づかない。
- **具体手順**:
  1. サイトマップの全URL集合 A を取得。
  2. 全HTMLをパースして「他ページからリンクされているURL」集合 B を作る。
  3. **A − B がオーファン**。さらに B − A（サイトマップ未収録だがリンクはある）も同時に出す。
  4. オーファン1件ごとに、トピカルマップ上の親クラスタを決め、**親から子への本文中リンクを最低2本**張る。
  5. これをビルド時のアサーションにする（オーファンが1件でもあればビルド警告）。
- **日本での言及度**: **低**（※推定）。「孤立ページ」という語は一部のツール系記事にあるが、**日常的な監査項目として日本語SEO記事で強調されているのは見たことがない**。ScreamingFrog/Ahrefsの機能紹介の一部として触れられる程度。
- **noe-match適用度**: **A（即着手推奨・工数最小）**。実測で **256記事中59件（23.0%）が他記事からの被リンク0**。具体例: `article-17`, `article-33`, `women-23`, `profilephoto-32`, `bridal-inner-guide`, `matching-josei-cost-data`, `fraudfake-15`, `pairs-kaiin-data`, `futari-sumaho-minaoshi`, `identity-exposure-38`, `article-3`, `article-7`, `withwomen-8`, `pairsmen-6`, `profile-27` ほか。さらに **sitemap-all.xml の`<loc>`は230件で、記事ディレクトリ256件との差23件がサイトマップ未収録**の可能性がある。この2つは今日中に潰せる。想定工数: 検出スクリプト30分＋リンク付与のバッチ生成半日。
- **リスク・反証**: ナビ／フッタからリンクされているページを「オーファン」と誤判定しないよう、パースは本文領域とグローバルナビを区別すること（上記59件は記事本文HTML全体を対象にした集計なので、テンプレート由来のリンクも含めてなお0本＝真のオーファンの可能性が高い）。また「オーファン解消＝順位上昇」を保証する公式見解はない。

---

## 4-08. AI抽出を前提とした情報設計（Content Chunking / Passage-level 最適化）

- **一言で**: AI検索と パッセージランキングは**ページ単位ではなくチャンク（見出しと段落で区切られた自己完結ブロック）単位**で取り出すので、1チャンク=1論点に整形する。
- **海外での出典**:
  - Promptwatch「Content Chunking」（AI systems process content in chunks bounded by heading elements, paragraph breaks, list structures, and semantic markers）https://promptwatch.com/glossary/content-chunking
  - Chroma Research「Evaluating Chunking Strategies for Retrieval」https://www.trychroma.com/research/evaluating-chunking
  - arXiv「Passage Segmentation of Documents for Extractive Question Answering」https://arxiv.org/pdf/2501.09940
  - iPullRank（パッセージ最適化の実務側）https://ipullrank.com/query-fanout-how-to
- **仕組み／なぜ効くか**: RAG／AI検索は文書を分割して埋め込み、クエリに近いチャンクだけを取り出して回答を組む。よって**チャンク境界がどこに落ちるか**が引用可否を決める。Chromaの研究は、チャンク戦略が検索精度に実測で効くことを示している。実務側では Mike King が「段落を分割して、各段落が1つの明確なトピックだけを扱うようにする」と明言している（https://ipullrank.com/query-fanout-how-to ）。「atomization（各チャンクが具体的で引用可能な情報を単体で持つ）」「structured content（セマンティックマークアップがチャンク境界の識別を助ける）」が対になる（https://promptwatch.com/glossary/content-chunking ）。
- **具体手順**:
  1. **1段落＝1論点**に統一する。1段落3〜5文、複数論点を含む段落を機械検出（文数・接続詞数で閾値）。
  2. 各`<h2>`直下の**最初の段落で、その見出しの問いに完結した答えを出す**（前置きを置かない）。
  3. 主語を省略しない。「これは」「その場合」といった**前チャンク依存の指示語を、チャンク先頭では使わない**（チャンク単体で読めなくなる）。
  4. 数値・条件・比較は必ず`<table>`か`<ul>`にする（構造マーカーがチャンク境界として機能する）。
  5. 用語定義は`<dl>/<dt>/<dd>`（定義リスト）で書く。HTMLの意味論上「これは定義である」と明示できる唯一のタグ。
  6. `<h2>` → `<h3>` を飛ばさない（`<h4>`をいきなり使わない）。階層がチャンクの入れ子構造として解釈される。
- **日本での言及度**: **ほぼ無**（※推定）。日本語SEO記事で「チャンク」という語はほぼ登場しない。「見出し構造を整えましょう」「PREP法で書きましょう」はあるが、**「AIが取り出す単位はチャンクであり、チャンクは単体で意味が通らなければならない」という設計原理として説明した日本語記事は極めて少ない**。指示語をチャンク先頭で使わないという具体則は特に流通していない。
- **noe-match適用度**: **A**。実測で **`<table>`使用は206記事（80%）と良好だが、`<dl>`（定義リスト）は0件**。婚活ジャンルは「成婚料」「お見合い料」「IBJ」「連盟」など定義が必要な用語が多く、定義リストの導入余地が大きい。平均`<h2>`数10.8は十分な粒度。**Python生成なので、`<dl>`への一括変換と「見出し直下段落の完結性」チェックをスクリプト化できる**。想定工数: チェッカ半日、テンプレート改修＋既存記事バッチ変換2〜3日。
- **リスク・反証**: **Googleがチャンク単位で処理していることの公式確認はない**。Googleが公表しているのは「passage ranking（パッセージに基づくランキング）」の存在までで、その内部粒度は非公開。またチャンク最適化を過剰にやると「同じことを各見出しで繰り返す冗長な文章」になり、helpful content的にはマイナス。**「単体で読める」と「重複」の境界に注意**。

---

## 4-09. Article と BlogPosting の使い分け／構造化データ型の一貫性

- **一言で**: Article / BlogPosting / NewsArticle は**継承関係（BlogPostingはArticleのサブタイプ）**で必須プロパティは同一。しかし**サイト内で型が混在していると、エンティティとしての一貫性が崩れる**。
- **海外での出典**:
  - schema.org BlogPosting https://schema.org/BlogPosting
  - Schema Validator「Article vs BlogPosting Schema: Which One Should You Use? (2026)」https://schemavalidator.org/guides/article-vs-blogposting-schema
  - recited「Article, BlogPosting, and NewsArticle Schema」https://recited.io/kb/schema-markup-and-structured-data/schema-types-and-applications/article-blogposting-and-newsarticle-schema/
- **仕組み／なぜ効くか**: リッチリザルト適格性はArticle/BlogPosting/NewsArticleでほぼ同一で、**唯一の実質的差はTop Stories（NewsArticleのみ適格）**（https://schemavalidator.org/guides/article-vs-blogposting-schema ）。したがってArticleかBlogPostingかは**リッチリザルトではなくコンテンツ分類のシグナル**であり、海外の推奨は「エバーグリーンなガイド・リファレンスは`Article`、個人的意見・時事性のある記事は`BlogPosting`」。重要なのは**サイト内で恣意的に混ざっていないこと**。
- **具体手順**:
  1. 全記事の`@type`を集計し、混在の実態を把握。
  2. 記事を「エバーグリーン解説／比較・ランキング／体験談・意見」に3分類。
  3. 前2者を`Article`、体験談を`BlogPosting`に**ルールとして固定**し、Python生成時にメタから自動決定する。
  4. `@type`が無い記事をゼロにする。
  5. Rich Results Test / Schema Markup Validator で全件バリデーション（GitHub Actionsで回せる）。
- **日本での言及度**: **低**（※推定）。日本語では「記事構造化データを入れましょう」までは頻出だが、**ArticleとBlogPostingの使い分け基準、およびTop Storiesだけが実質的差であるという結論は日本語記事でほとんど説明されていない**。プラグイン任せで型が混在したまま放置されるのが日本の一般的状況。
- **noe-match適用度**: **A（工数極小・実測で問題が確定している）**。実測: **Article 132記事 / BlogPosting 77記事 / どちらも無し 48記事**。これは典型的な「生成スクリプトが世代ごとに違う型を吐いている」状態。Python生成なので**1回のバッチで256記事すべて統一できる**。想定工数: 半日。
- **リスク・反証**: 型を揃えても順位が上がるという実証はない。効果は「リッチリザルト適格性の担保」と「エンティティの一貫性」という間接的なもの。**過剰な期待は禁物だが、コストがほぼゼロなので費用対効果は高い**。

---

## 4-10. 著者エンティティの構築（Author Entity Building / Person schema + sameAs）

- **一言で**: `author` を組織名の文字列や`Organization`ではなく、**`Person` エンティティ**にして、`sameAs`で外部プロフィール（LinkedIn / X / ORCID / Wikidata）に接続し、機械可読な人物実体として解決可能にする。
- **海外での出典**:
  - Schema Validator「Person Schema for Authors: Bylines, sameAs & E-E-A-T Signals (2026)」https://schemavalidator.org/guides/person-schema-authors
  - OrganiKPI「Schema sameAs: How Entity Disambiguation Works」https://organikpi.com/blog/technical-seo/schema-sameas-entity-disambiguation-ai-citations/
  - Aubrey Yung「How to use Author schema for E-E-A-T?」https://aubreyyung.com/author-schema/
  - iPullRank「Google's Search Quality Rater Guidelines and YMYL in the Age of AI Search」https://ipullrank.com/eeat-ymyl-ai-search
- **仕組み／なぜ効くか**: `sameAs`はエンティティの**曖昧性解消（disambiguation）**の仕組み。同名人物が複数いる世界で「この著者はこのLinkedInのこの人だ」と機械的に確定させる。実務側の観測として「名前付きでスキーマ属性が付き、エンティティレコードが解決できる著者のページは、汎用バイラインのページよりAI検索での取得（retrieval）成績が良い」という報告がある（https://organikpi.com/blog/technical-seo/schema-sameas-entity-disambiguation-ai-citations/ ）。ORCIDは学術・医療系著者に、LinkedInは最も汎用性の高い高権威プロフィールとして推奨されている。
- **具体手順**:
  1. `/author/{slug}/` の著者ページを作り、`@type: Person`、`name`、`description`、`jobTitle`、`knowsAbout`（担当トピック配列）、`sameAs`（外部URL配列）、`url`、`image` を持たせる。
  2. 各記事の`author`を、その著者ページの`@id`への参照にする（`{"@id": "https://.../author/xxx/#person"}`）。
  3. 外部プロフィール側からも著者ページへリンクを張る（**双方向でないとsameAsは検証されにくい**）。
  4. 記事ページ内に**可視の著者バイオ**（顔写真＋経歴2〜3行＋担当分野）を置く。構造化データだけでなく人間可読な実体が必要。
  5. `Organization`側に`founder`（Personへの参照）と`knowsAbout`を持たせ、組織⇄人物のエンティティグラフを閉じる（4-11参照）。
- **日本での言及度**: **低**（※推定）。「E-E-A-Tのために著者情報を書きましょう」「監修者を置きましょう」は日本語で**非常に多い**。しかし**`sameAs`によるエンティティ曖昧性解消という仕組みの説明、`knowsAbout`の使用、`@id`による参照でエンティティグラフを閉じる実装**は日本語圏で圧倒的に手薄。日本では「著者ページを作る」＝「プロフィールページを作る」で止まり、機械可読性の議論に進まない。
- **noe-match適用度**: **A（最も差分が大きい未実装項目）**。実測: **サイト全体で`@type: Person` が0件。`author`は208記事すべてが `{"@type":"Organization","name":"Noe編集部"}`**。婚活・結婚・お金はYMYL隣接領域であり、E-E-A-Tの実装がそのまま効きやすい。個人運営なので**運営者本人をPersonエンティティ化するのが最速**（X／noteのアカウントを`sameAs`に）。想定工数: 著者ページ作成＋テンプレート改修で1〜2日。既に`about.html`と`policy/editorial.html`があるので土台はある。
- **リスク・反証**: **Googleは「author schemaがランキング要素である」と公式に述べていない**。Google公式ドキュメントで`author`が必須なのはNewsArticle系のリッチリザルト文脈が中心。E-E-A-Tも「ランキング要素そのものではなく、品質評価者が使う概念」というのがGoogleの公式説明。したがって効果は**間接的（AI引用時の実体解決、人間の信頼獲得）**と考えるべき。また**実在しない著者や誇張した経歴を書くのは最悪手**（YMYL隣接領域では特に危険）。個人運営なら「個人が運営していること」を正直に書く方が強い。

---

## 4-11. Organization エンティティの強化（knowsAbout / founder / publisher の連結）

- **一言で**: サイト運営組織を`Organization`として宣言し、`knowsAbout`で専門領域を明示、`founder`でPersonに接続、`WebSite`の`publisher`から`@id`参照させて、**エンティティグラフを1つのJSON-LDブロックで閉じる**。
- **海外での出典**:
  - Stackmatix「Organization Schema Markup: Complete Guide to Knowledge Graph & Entity SEO (2026)」https://www.stackmatix.com/blog/organization-schema-knowledge-graph
  - Schema Validator「Entity SEO & Schema Markup: Build Your Knowledge Graph Presence (2026)」https://schemavalidator.org/guides/entity-seo-schema-markup
  - Schema Engine AI「Organization Schema Markup Guide」https://schemaengineai.com/blog/organization-schema-markup-guide/
- **仕組み／なぜ効くか**: 推奨実装は「**Organization と WebSite を1つのJSON-LDブロックにまとめ、WebSiteの`publisher`がOrganizationの`@id`を指す**」形（https://www.stackmatix.com/blog/organization-schema-knowledge-graph ）。`knowsAbout`は「この組織はこのトピックの専門である」という明示的シグナルとして機能する（https://www.leadgen-economy.com/blog/entity-graph-schema-ai-visibility-guide/ 系の実務記事が主張）。監査記事では**Organization schemaは最も使われていないスキーマ型**とされている。
- **具体手順**:
  1. サイト共通で`@id`付きのOrganizationブロックを1つ定義（`https://www.noe-match.com/#organization`）。
  2. `knowsAbout` に主要トピックを配列で列挙（「婚活」「結婚式費用」「マッチングアプリ」「結婚相談所」「新生活の家計」など、トピカルマップのCore Sectionと一致させる）。
  3. `founder` に運営者Personの`@id`を入れる。
  4. `WebSite`（`@id: #website`）を定義し、`publisher: {"@id": "#organization"}`。
  5. 各記事の`publisher`も文字列ではなく`@id`参照に統一。
  6. 全ページ共通ブロックはPython生成のテンプレート1箇所に置く。
- **日本での言及度**: **ほぼ無**（※推定）。`Organization` schema自体は日本語でも紹介されるが、**`knowsAbout`、`founder`、`@id`によるエンティティ参照、Organization×WebSiteの単一ブロック統合**は日本語SEO記事でほぼ扱われていない。日本語では「パンくずとFAQを入れましょう」で構造化データの話が終わることが多い。
- **noe-match適用度**: **A**。実測で`Organization` は363箇所に出現するが、`WebSite`は1件のみ、`@id`参照による連結は行われていない（各記事に文字列レベルのOrganizationが重複して埋め込まれている状態）。**Python生成なので共通ブロック化は1回の改修で済む**。想定工数: 半日〜1日。
- **リスク・反証**: `knowsAbout`がGoogleに使われている公式確認はない。Googleが公式にサポートするOrganizationプロパティは限定的（`name`, `url`, `logo`, `sameAs`, `contactPoint`等）で、`knowsAbout`はschema.org語彙としては正しいがGoogleの公式リッチリザルト要件には含まれない。**AI検索（LLM）向けの機械可読性向上として位置づけるのが妥当**。ナレッジパネル取得を約束するものではない。

---

## 4-12. 一次体験の証明（Proof of Experience / オリジナル画像）

- **一言で**: E-E-A-Tの最初のE（Experience）を「言葉で主張する」のではなく、**オリジナル写真・自前のスクリーンショット・自分で取った数値・日付入りの結果**という物証で示す。
- **海外での出典**:
  - iPullRank「Google's Search Quality Rater Guidelines and YMYL in the Age of AI Search」https://ipullrank.com/eeat-ymyl-ai-search
  - SEOZoom「Google quality rater guidelines: comprehensive and updated guide」https://www.seozoom.com/google-search-quality-rater-guidelines/
  - The Rez Ali「Page 6 tells the raters their ratings do not move rankings」https://therezaali.com/writing/eeat-quality-rater-guidelines/
  - Google「Creating Helpful, Reliable, People-First Content」（"original information, reporting, research"）https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- **仕組み／なぜ効くか**: QRGはExperienceを「コンテンツ制作者がそのトピックについて必要な**一次的あるいは実生活上の経験**をどの程度持っているか」と定義している。実務家の読み方は「**評価者は実際にやった証拠を求めている：オリジナル写真、自分のテストデータ、日付入りの具体的な結果**」（https://theguidex.com/google-quality-rater-guidelines-summary/ ほか）。またQRGは「**Effort（労力）の証拠**」として、オリジナル画像・独自データセット・ケーススタディを挙げている。
- **具体手順**:
  1. 記事ごとに「この記事で自分が実際にやったこと」を1つ決める（アプリの登録画面のスクショ、料金ページの実キャプチャ、自分で集計した統計）。
  2. **ストック写真をヒーロー画像に使わない**。最低1枚は自前の画像を入れる。
  3. スクリーンショットには**取得日を画像内またはキャプションに明記**する。
  4. 画像に`ImageObject` schema（`contentUrl`, `caption`, `datePublished`, `creator`）を付ける。
  5. 独自集計は表にし、算出方法・母数・取得日を注記する。
  6. 記事末尾に「調査方法」セクション（いつ・何を・どうやって確認したか）を置く。
- **日本での言及度**: **低**（※推定。専用検索は未実施）。「E-E-A-T」「一次情報が大事」は日本語で頻出。しかし**「QRGのどの節がそれを求めているか」「Effortの証拠として何が列挙されているか」という原典ベースの議論、および画像に取得日を入れる／`ImageObject`で作成者を宣言するといった実装レベルの具体**は日本語圏で手薄。EXIF情報については**Googleは画像のEXIFを直接ランキングに使うとは公式に述べておらず、EXIFがSEOに効くという主張は根拠が弱い**ので、この項目からは意図的に外した（EXIFよりキャプション・周辺テキスト・ファイル名・alt・`ImageObject`の方が根拠がある）。
- **noe-match適用度**: **B〜A**。実測で`ImageObject` schema は6件のみ、`images/`ディレクトリは存在。婚活サービスの管理画面スクショや料金表キャプチャは**アフィリエイト規約上の制約**があるので要確認だが、料金・条件の一次確認（公式サイトを見た日付）は書ける。想定工数: 運用ルール化＋テンプレート改修1日、既存記事への遡及適用は記事あたり15分。**まず「調査方法」セクションと取得日明記から始めるのが低コスト**。
- **リスク・反証**: **QRG 6ページ目に「評価者の評価は直接順位を動かさない」と明記されている**（https://therezaali.com/writing/eeat-quality-rater-guidelines/ ）。QRGはアルゴリズムの仕様書ではなく、Googleが「良いとみなしたい方向」の説明資料。したがって「QRGに書いてある＝ランキング要素」ではない。ただし**方向性の指針としては最も信頼できる公開文書**である。またアフィリエイト先のスクリーンショット掲載は各ASP/広告主の規約違反になりうるので、掲載前に必ず確認すること。

---

## 4-13. Core Web Vitals の実際の重み（過大評価への反証を含む）

- **一言で**: CWVは公式のランキング要素だが、**重みは小さく、コンテンツ関連性が同等の場合のタイブレーカー**というのが海外の到達点。日本語圏で語られるほどの投資対効果はない場合が多い。
- **海外での出典**:
  - The Stacc「Core Web Vitals Statistics: 43% Fail INP in 2026」https://thestacc.com/blog/core-web-vitals-statistics/
  - Digital Applied「Core Web Vitals Benchmarks 2026: What Good Looks Like」https://www.digitalapplied.com/blog/core-web-vitals-benchmarks-2026-pass-rate-reference
  - corewebvitals.io「What Are the Core Web Vitals? LCP, INP & CLS Explained (2026)」https://www.corewebvitals.io/core-web-vitals
  - White Label Coders「How important are Core Web Vitals for SEO in 2026?」https://whitelabelcoders.com/blog/how-important-are-core-web-vitals-for-seo-in-2026/
- **仕組み／なぜ効くか（と、効かない理由）**:
  - 実測相関: **1位のサイトが9位のサイトよりCWVを通過する確率は10%高いだけ**（https://thestacc.com/blog/core-web-vitals-statistics/ ）。相関はあるが因果の向きは議論中とされている。
  - 業種差が極大: **米国の金融系上位URLの24%はCWV通過でランキングブーストを得るが、教育系は5%未満**（同上）。つまり**「どの業種か」で投資判断が変わる**。
  - 2024年3月にFIDがINPに置換され、**2026年時点でINPを落としているサイトが43%**（同上）＝INPが最大のボトルネック。
  - 海外の共通見解は「重みは小さいが実在する。競合が拮抗しているニッチではタイブレーカーになる」。
- **具体手順**:
  1. まずCrUX（フィールドデータ）で自サイトの実測値を確認する。Lighthouse（ラボデータ）だけで判断しない。
  2. INPを最優先で見る（2026年時点で最も落ちやすい指標）。原因はほぼJavaScriptのメインスレッド占有。
  3. LCP要素を特定し、その画像だけ`fetchpriority="high"`＋プリロード。
  4. CLSは画像・広告・埋め込みに`width`/`height`または`aspect-ratio`を必ず指定して潰す（最も安く効く）。
  5. **通過（Good）に達したらそれ以上投資しない**。CWVは閾値型であり、Goodの中でさらに速くしても検索上の追加利得はないとされる。
- **日本での言及度**: **高（ただし方向が逆）**（※推定）。日本語SEO記事はCWVを**過大に**扱う傾向がある（「CWVを改善しないと順位が下がる」）。**「重みは小さい」「業種で影響が5%〜24%と大きく違う」「Good到達後の追加投資は無意味」という反証側の情報こそが日本語圏で流通していない**。この項目は「日本で言及が薄い手法」ではなく「**日本で誤って重視されている論点の是正**」として価値がある。
- **noe-match適用度**: **C（低優先）**。GitHub Pagesの静的HTMLサイトで、JSフレームワークを使っていない。**構造上、INPもLCPも最初から良好である可能性が高い**。CrUXで一度確認して、Goodならこの領域には一切投資しないでよい。想定工数: 確認のみ30分。CLSだけ画像のwidth/height指定を全記事でチェック（スクリプト30分）。
- **リスク・反証**: Google公式は「Core Web Vitals はページエクスペリエンスシグナルの一部で、優れたコンテンツを上回るものではない」と一貫して述べている。一方で「LCPが3秒超のページは2025年12月コアアップデートで23%多くトラフィックを失った」という実務観測もある（https://thestacc.com/blog/core-web-vitals-statistics/ ）が、**これは相関であり、遅いサイト＝リソースの乏しいサイト＝コンテンツも弱い、という交絡の可能性が高い**。

---

## 4-14. ログファイル解析の個人向け代替（GSC Crawl Stats / Cloudflare / GA4）

- **一言で**: サーバログが取れない環境（GitHub Pages等）でも、**GSCのクロール統計レポート**とCDNのボット解析でクロール挙動を近似できる。
- **海外での出典**:
  - Oncrawl「Google Crawl Stats Report vs Log File Analysis: Which is the winner?」https://www.oncrawl.com/general-seo/google-crawl-stats-report-log-file-analysis/
  - GSQI（Glenn Gabe）「How To Use GSC's Crawl Stats Reporting To Analyze and Troubleshoot Site Moves」https://www.gsqi.com/marketing-blog/how-to-use-gsc-crawl-stats-report-site-migrations/
  - Similarweb「Log File Analysis: Track AI Bots & Fix Crawl Gaps」https://aisearch.similarweb.com/blog/log-file-analysis/
- **仕組み／なぜ効くか**: ログは全リクエストをURL単位で記録するのに対し、**GSC Crawl Statsは集計トレンドしか出さず、一部リクエストは計上されず、データ反映に最大1週間かかる**（https://www.oncrawl.com/general-seo/google-crawl-stats-report-log-file-analysis/ ）。それでも「ホストのステータス」「レスポンス別内訳（200/301/404/5xx）」「ファイル種別内訳」「Googlebot種別（スマートフォン/デスクトップ/画像）」「目的別（Discovery/Refresh）」は取れる。CloudflareのBot Analyticsはプロキシ配下のサイトで部分的な像を与える（Enterprise以外ではWorkerでエッジログを取る必要がある、https://aisearch.similarweb.com/blog/log-file-analysis/ ）。
- **具体手順**:
  1. GSC設定 → クロールの統計情報 で、①1日あたりのクロールリクエスト数の推移、②レスポンス内訳、③目的（検出 vs 更新）の比率を月次で記録する。
  2. **「検出（Discovery）」の比率**が低いまま新規記事を出し続けているなら、新URLの発見経路（内部リンク・サイトマップ）に問題がある。
  3. 404/301の比率が上がっていないか監視（リンク切れの早期検出）。
  4. GitHub Pagesではサーバログが取れないので、**Cloudflareを前段に置けばボット解析が使える**（noe-matchはCNAMEありなのでDNS切替で可能）。
  5. GA4はJSベースなのでボットは基本計上されない。**GA4はクローラ解析には使えない**（人間のトラフィックのみ）。この誤解は多い。
  6. 補助として、`sitemap.xml`の各URLがGSCのURL検査で「クロール済み」になっているかを定期サンプリングする。
- **日本での言及度**: **低**（※推定）。「ログファイル解析」は日本語では大規模サイト向けの話題として少数の記事があるが、**「サーバログが無い個人サイトで何をどう代替するか」「GSC Crawl Statsの目的別内訳をどう読むか」という実践的な代替手順の記事は日本語圏でほぼ見ない**。Glenn Gabe系のGSC深掘りコンテンツは日本語に翻訳されていない。
- **noe-match適用度**: **B**。GitHub Pagesなのでサーバログは取得不可。**GSC Crawl Statsの月次記録は今日から無料でできる**（工数ゼロ）。Cloudflare導入は判断が必要（GitHub Pagesの前段にCloudflareを置く構成は一般的だが、Pages側のHTTPS設定と衝突しないよう注意）。想定工数: GSC記録の運用化1時間。Cloudflare導入は半日＋リスク検討。
- **リスク・反証**: GSC Crawl Statsは**サンプリングされている可能性があり、AI系クローラ（GPTBot, ClaudeBot, PerplexityBot）は一切見えない**。AI検索での可視性を追うならCloudflare等のエッジ解析が必要。またCloudflare導入はGitHub Pagesとの二重CDNになり、キャッシュ制御を誤ると更新が反映されない事故が起きる。

---

## 4-15. dateModified と「空更新」問題

- **一言で**: 日付だけ更新して中身を変えないのは**効かないどころか、サイト全体の日付シグナルの信頼を失う**。日付は「schema・可視日付・sitemap lastmod・Google自身のクロール記録」の4系統が一致している必要がある。
- **海外での出典**:
  - Search Engine Journal「Google's John Mueller: Updating XML Sitemap Dates Doesn't Help SEO」https://www.searchenginejournal.com/googles-john-mueller-updating-xml-sitemap-dates-doesnt-help-seo/545547/
  - Search Engine Land「Byline Dates in SEO: What They Mean, What Google Actually Uses」https://searchengineland.com/guide/byline-dates
  - WhitePress「Publication date update – exploring freshness algorithm with an SEO experiment」https://www.whitepress.com/en/knowledge-base/1665/publication-date-update-exploring-freshness-algorithm-with-an-seo-experiment
- **仕組み／なぜ効くか**:
  - **Google公式**: Muellerは「sitemapの日付を自動で更新してもSEOには効かず、**むしろGoogleが本当の更新を見つけにくくなる**」と述べている（https://www.searchenginejournal.com/googles-john-mueller-updating-xml-sitemap-dates-doesnt-help-seo/545547/ ）。また日付を人為的に新しくする手法について「**古い手口で、Googleは既に対処済み。順位は上がらない**」、2023年には「**可視日付だけを変えてもランキングには何もしない**」と発言している（https://searchengineland.com/guide/byline-dates ）。
  - **仕組み側**: Googleはschema、可視日付、sitemapのlastmod、そして自身のクロール履歴という複数の日付シグナルを突き合わせる。**全部が食い違う場合、Googleは意図的に最も古いものを採用する**とされる（https://searchengineland.com/guide/byline-dates ）。
  - **実務家の観測**: dateModifiedが進んでいるのに本文差分がほぼゼロだと不一致が検出可能で、**そのURLだけでなくサイト全体の日付シグナルの信用が落ちる**という主張がある（未検証の仮説として扱うべき）。
- **具体手順**:
  1. `dateModified` を**実際に本文が変わったときだけ**更新する。Python生成なら、前回ビルドとの**本文ハッシュ差分**を取り、差分がある記事だけ日付を進める。
  2. sitemapの`lastmod`も同じ判定を使う（noe-matchは既に230件全件にlastmodがある＝要確認：全件が同一日になっていないか）。
  3. 可視日付（本文中の「最終更新日」表記）とJSON-LDの`dateModified`を**必ず同一の値**にする。片方だけ更新しない。
  4. `datePublished`は絶対に書き換えない（初出日は履歴として価値がある）。
  5. 更新時は本文中に「2026年8月時点の情報に更新しました」等、**何を更新したかを明示**する（人間にもGoogleにも実質的更新であることが伝わる）。
- **日本での言及度**: **低〜中**（※推定）。「更新日を新しくすると順位が上がる」という俗説は日本語圏に根強く、**「日付だけ更新は効かない」というMuellerの明言を紹介した日本語記事は少数**。特に「**4系統の日付が食い違うと最も古い日付が採用される**」「**sitemap lastmodの自動更新は逆効果**」という具体は日本語圏でほぼ流通していない。
- **noe-match適用度**: **A（工数極小・事故防止価値が高い）**。実測: 208記事に`dateModified`あり、sitemapは230件全件にlastmodあり。**Python生成サイトで最も起こりやすい事故が「ビルドのたびに全記事のlastmod/dateModifiedが今日になる」**。まずこれが起きていないかを確認し、起きていれば本文ハッシュ差分方式に変更する。想定工数: 確認30分＋改修半日。
- **リスク・反証**: 「空更新でサイト全体の信頼が落ちる」という主張はGoogle公式の裏付けがない実務家仮説。Googleが公式に言っているのは「効かない」までで、「ペナルティがある」とは言っていない。ただし**効かない上に本当の更新の検出を妨げる**ので、やる理由が一切ない。

---

## 4-16. クエリ・ファンアウト対応（Query Fan-Out / AI Mode 最適化）

- **一言で**: AI Modeは1つの質問を**内部で数十〜数百の合成クエリ（synthetic queries）に分解して並列検索**するので、「1キーワードに最適化」ではなく「**サブ意図の網羅**」で設計する。
- **海外での出典**:
  - iPullRank（Mike King）「Query Fan-Out in Practice: Turning One Search into an Omnimedia Content Plan」https://ipullrank.com/query-fanout-how-to
  - iPullRank「How AI Search Platforms Expand Queries with Fan-Out and Why It Skews Intent」https://ipullrank.com/expanding-queries-with-fanout
  - Digiday「WTF is 'query fan-out' in Google's AI mode?」https://digiday.com/media/wtf-is-query-fan-out-in-googles-ai-mode/
  - Semrush「We Tested Query Fan-Out Optimization (Here's What We Learned)」https://www.semrush.com/blog/query-fan-out-experiment/
- **仕組み／なぜ効くか**: Googleは Gemini 系LLMで、**意図の多様性・語彙の変化・エンティティに基づく言い換え**を強調した構造化プロンプトで合成クエリを生成しているとされる。合成クエリの類型は **Related（意味的に隣接）/ Implicit（言わなかったが意図している）/ Comparative（比較・意思決定用）/ Personalized（履歴・位置に基づく）**（https://logikdigital.com/blog/query-fan-out-ai-search/ ほか）。King の実務提言は「**狙うキーワードでの順位を見て、Googleが使いそうなパッセージを最適化する。それは段落を分割して各段落が1つの明確なトピックだけを扱うようにすること**」（https://ipullrank.com/query-fanout-how-to ）。Kingは`Qforia`というファンアウトシミュレータを公開している（Gemini APIキーが必要）。
- **具体手順**:
  1. 主要記事の対象クエリについて、LLMに「このクエリからAI検索が生成しそうなサブクエリを30個」出させる（Qforia相当の処理は手元のLLMで代替可能）。
  2. サブクエリを Related / Implicit / Comparative / Personalized の4類型に分類。
  3. **Comparative（比較）と Implicit（暗黙）が最も抜けやすい**ので優先的に潰す。
  4. サブクエリ1つにつき、記事内に**そのサブクエリに単体で答える段落またはFAQ項目**を1つ用意する。
  5. 既存のFAQPage schema（noe-matchは226記事に実装済み）を、このサブクエリリストで**内容ベースに置き換える**。
  6. カバー率（30サブクエリ中いくつに答えているか）を記事ごとの指標として管理。
- **日本での言及度**: **ほぼ無**（※推定）。「AI Overviews対策」「LLMO/GEO」という語は2025年後半から日本語でも増えたが、**"query fan-out"という具体的な機構名と、その4類型、そして「段落を1トピックに分割する」という実装指示は日本語圏でほとんど紹介されていない**。iPullRankのコンテンツは日本語に翻訳されていない。**本領域で最も差分の大きい手法のひとつ**。
- **noe-match適用度**: **A**。**FAQPage schemaが全記事に既実装という資産がそのまま活きる**。現状のFAQが「よくある質問を思いつきで書いた」ものなら、ファンアウト由来のサブクエリに差し替えるだけで質が跳ね上がる。婚活は Comparative（「AとBどっちが」）と Implicit（「30代女性が今から始めて何ヶ月で成婚できるか」）が非常に多いジャンル。想定工数: サブクエリ生成の自動化半日＋記事あたり30分。
- **リスク・反証**: **query fan-outの内部仕様はGoogleが詳細を公表していない**。合成クエリの類型も実務家の推定。Semrushの実験記事（https://www.semrush.com/blog/query-fan-out-experiment/ ）も「試した」レベルであり、確立した因果関係ではない。またサブクエリを網羅しようとして記事が肥大化すると本来のUXを壊す。**FAQ枠に押し込むのが最も副作用が少ない**。

---

## 4-17. Speakable / ItemList / 高度な構造化データ型の取捨選択

- **一言で**: 「入れられるスキーマを全部入れる」は間違い。**Googleが実際にサポートしている型・非推奨になった型を把握して選ぶ**。
- **海外での出典**:
  - Google公式「Speakable (BETA) Schema Markup」https://developers.google.com/search/docs/appearance/structured-data/speakable
  - Search Engine Land「Structured data and SEO: What you need to know in 2025」https://searchengineland.com/structured-data-seo-what-you-need-to-know-447304
  - Yoast「Structured data with schema for search and AI」https://yoast.com/structured-data-schema-ultimate-guide/
- **仕組み／なぜ効くか（型ごとの実態）**:
  - **Speakable**: Google公式ドキュメント上も**BETA扱いで、対象は「英語設定の米国Google Homeデバイス所有者」に限定**（https://developers.google.com/search/docs/appearance/structured-data/speakable ）。**日本語サイトにとっては現時点で完全に無価値**。日本語のSEO記事で「音声検索対策にSpeakableを」と書いてあるものは無視してよい。
  - **ItemList**: カテゴリページ、コレクションページ、キュレーションリスト、比較ガイドで有用（https://yoast.com/structured-data-schema-ultimate-guide/ ）。ランキング記事と相性が良い。
  - **Dataset**: 検索結果表示としては**2026年1月に非推奨化された**とする記述がある（https://www.gwcontent.com/blogs/news/structured-data-for-seo ）ため、リッチリザルト目的では使わない。
  - **Organization**: 監査上「最も使われていないスキーマ型」（4-11参照）。
  - **Table**: schema.orgの`Table`型はGoogleのリッチリザルト対象外。**HTMLの`<table>`をセマンティックに正しく書く方が価値が高い**（`<thead>/<th scope>/<caption>`）。
- **具体手順**:
  1. Speakableは**実装しない**（日本語サイトでは効果ゼロ）。
  2. ランキング・比較記事に`ItemList` + `ListItem`（`position`, `name`, `url`）を入れる。noe-matchは既に`ListItem`が688箇所あるので、パンくず用途か比較用途かを確認する。
  3. `BreadcrumbList`は全記事で維持（189/256記事に実装済み → **残り約67記事に未実装**）。
  4. `Dataset`は使わない。
  5. `<table>`は`<caption>`と`<th scope="col|row">`を必ず付ける（AI抽出とアクセシビリティ両方に効く）。
  6. 実装後はRich Results TestとSchema Markup Validatorの両方でバリデート（前者はGoogle対応型のみ、後者は語彙の正しさ）。
- **日本での言及度**: **中〜低**（※推定）。「構造化データの種類一覧」記事は日本語に多いが、**「Speakableは英語圏の米国限定BETAなので日本語サイトでは無意味」「Datasetは非推奨化」という取捨選択の情報が更新されていない古い日本語記事が大量に残っている**。この「やらなくていいことの特定」こそが日本語圏で最も欠けている。
- **noe-match適用度**: **B**。BreadcrumbList未実装の約67記事を埋めるのが最優先（工数小）。ItemListは比較・ランキング記事に限定して追加。想定工数: 半日。
- **リスク・反証**: 構造化データは**リッチリザルト適格性を与えるだけで、ランキングを直接上げるものではない**とGoogleは一貫して述べている。過剰なマークアップ（本文に無い内容をスキーマに書く等）は手動対策の対象になる。

---

## 4-18. コンテンツ・ディケイ（Content Decay）の定量監視とリフレッシュ

- **一言で**: 公開直後にピークを打ってから**じわじわ減衰する記事**を、減衰率で機械検出してリフレッシュ順に並べる。
- **海外での出典**:
  - Ahrefs「What Is Content Decay? (And How to Fix It Before It Tanks Your Traffic)」https://ahrefs.com/blog/content-decay/
  - Animalz「Content Refresh Strategy: How to Update Old Content for SEO and AI Search」https://www.animalz.co/blog/content-refresh
  - Fractl「Content Decay and Revival: Identifying and Updating Underperforming Content」https://www.frac.tl/content-decay-updating-underperforming-content/
  - Kevin Indig https://www.kevin-indig.com/
- **仕組み／なぜ効くか**: Animalzは AdEspresso のデータ分析で**週あたり平均 −1.21% の減衰率**を記録している（https://www.animalz.co/blog/content-refresh ）。同社の報告では1回のリフレッシュで**30,000+ 追加PVと週次トラフィック+55%**の事例がある（同上）。実務フレームは「12〜24ヶ月のオーガニックトラフィック・順位・エンゲージメント・CVをURL単位で集め、**maintain / refresh / consolidate / prune の4値に分類**する」（4-02と同じ4値）。「新記事を1本も書かずに、失ったオーガニックの30〜60%を約90日で取り戻せる」という主張もある（https://prometixai.com/blog/content-decay/ ）。
- **具体手順**:
  1. URLごとに月次クリック数の時系列を作り、**「ピーク月からの下落率」と「直近3ヶ月の傾き」**を計算。
  2. 下落率 > 30% かつ ピーク時クリックが一定以上 の記事を decay 候補に。
  3. decay の原因を3分類：(a) 情報の陳腐化、(b) 競合の新規参入、(c) 検索意図の変化（SERP構成が変わった）。
  4. (a)なら数値・料金・制度の更新、(b)なら情報利得の追加（4-01）、(c)なら記事の構成そのものを作り直す。
  5. リフレッシュ後は`dateModified`を実差分ベースで更新（4-15）。
  6. リフレッシュ日をリポジトリに記録し、90日後に効果測定。
- **日本での言及度**: **低**（※推定）。「リライト」は日本語SEOの主要テーマで記事は非常に多い。しかし**「content decay」という現象名、週次減衰率という定量化、ピークからの下落率で機械的に候補を出すアプローチ**は日本語圏でほぼ扱われていない。日本語の「リライト」記事は「順位が落ちた記事を直そう」という属人的判断に留まる。
- **noe-match適用度**: **C（現時点）→ 6ヶ月後にA**。**ドメイン開設2026年6月で、まだ減衰を語れるだけの時系列が無い**。ただし**今から月次スナップショットを取り始めないと、半年後にこの手法が使えない**。`kpi_history.json`と`index_history.json`が既にあるので、GSCの月次クリックをURL単位でアーカイブする処理を今すぐ足すべき。想定工数: スナップショット処理1〜2時間（**今やる価値が最も高い項目**）。
- **リスク・反証**: 減衰の多くは**季節性**（婚活は年始・春・秋にピークがある）で説明でき、真の decay と区別しないと誤ってリライトしてしまう。最低12ヶ月の時系列が無いと季節性を除去できない。またリフレッシュ自体が順位を下げるケースもある（うまくいっていた構成を壊す）。**リフレッシュ前のHTMLを必ずgitに残す**こと（noe-matchはgitリポジトリなので自動的に満たされる）。

---

## 4-19. レンダリング戦略：静的HTMLの構造的優位

- **一言で**: Googleは「第1波でHTMLを処理し、JS実行は第2波として別キューに回す」ため、**JS依存サイトは数日〜1週間以上インデックスが遅れる**。静的HTMLはこの遅延がゼロ。
- **海外での出典**:
  - Rewati Khare「JavaScript SEO in 2026: What Google actually handles vs what still bites you」https://www.rewatikhare.com/post/javascript-seo-in-2026-what-google-actually-handles-vs-what-still-bites-you
  - SEO Kreativ「JavaScript SEO & Rendering: How Google Handles JS [2026]」https://www.seo-kreativ.de/en/blog/javascript-seo-rendering/
  - SEOLinkScan「JavaScript SEO in 2026: How Google Renders JS and What You Are Missing」https://seolinkscan.com/blog/javascript-seo-guide-2026
- **仕組み／なぜ効くか**: 第1波でGooglebotは初期HTMLを即時処理する。JS実行とレンダリングは別キューに入り、**サイトのクロール優先度とサーバ速度により数秒〜数日の遅延**が生じる。DeepCrawlの調査として**初回クロールとJS実行の間に5〜7日の遅延**が引用されている（https://seolinkscan.com/blog/javascript-seo-guide-2026 ）。優先度の低いサイトでは1週間以上になることもある。逆に**静的HTMLは数時間でクロール・インデックスされ、第1波の時点でコンテンツ・リンク・メタ・構造化データがすべて見える**。
- **具体手順**:
  1. **主要コンテンツ・内部リンク・JSON-LDを、JSなしのHTMLソースに必ず含める**（`curl`して`grep`で確認できる状態）。
  2. 「もっと見る」「タブ切替」でコンテンツをJSで後から挿入しない。HTMLに全部入れてCSSで折りたたむ。
  3. 内部リンクは必ず`<a href>`。`onclick`によるナビゲーションは使わない。
  4. 遅延読み込みは画像に限定し、`loading="lazy"`（ネイティブ）を使う。JSベースのlazy loadでコンテンツを隠さない。
  5. GSCのURL検査「レンダリング済みHTML」と、生の`curl`結果を比較して差分がないことを確認。
- **日本での言及度**: **中**（※推定）。「JavaScript SEO」は日本語記事もそれなりにある。ただし**「2波レンダリングの遅延が具体的に5〜7日」「静的サイトはこの遅延がゼロという構造的優位」という定量的な優位性の説明**は日本語圏で強調されていない。日本では「SSRにしましょう」というフレームワーク側の議論に偏る。
- **noe-match適用度**: **A（既に達成済み。守るべき資産として認識すること）**。**GitHub Pages上のPython生成静的HTMLという構成は、この観点では最適解**。ドメイン2ヶ月で「インデックス申請ありで90-100%」という実測が出ているのも、静的HTMLで第1波完結していることが寄与している可能性が高い。**今後の施策でJS依存を持ち込まないことが最大の価値**（例: 比較表をJSでレンダリングする、記事一覧をJSでページングする、といった改修は絶対にしない）。想定工数: ゼロ（維持のみ）。ただしビルド時のアサーションとして「JSなしHTMLにJSON-LDと本文が含まれる」を検証するテストを入れておくとよい（1時間）。
- **リスク・反証**: Googleは「現代のGooglebotはJSをレンダリングできる」と公式に述べており、JSサイトがインデックスされないわけではない。遅延の日数は調査により幅があり、サイトの権威度に依存する。**「JSはSEOに悪い」ではなく「JSは遅延と失敗の確率を持ち込む」が正確**。

---

## 4-20. llms.txt は入れなくてよい（やらないことの特定）

- **一言で**: 2026年時点で **llms.txt は Google が公式に「Search に一切影響しない」と明言し、実測でもAIクローラがほぼ読んでいない**。実装コストをかける根拠がない。
- **海外での出典**:
  - 1ClickReport「llms.txt in 2026: The Evidence Says It Does Nothing」https://www.1clickreport.com/blog/llms-txt-evidence-2026
  - Digital Applied「llms.txt in Practice: Adoption Data, Evidence, and Setup」https://www.digitalapplied.com/blog/llms-txt-in-practice-adoption-evidence-2026
  - Tobira「Does llms.txt Actually Work? An Honest Read of the 2026 Evidence」https://blog.tobira.ai/does-llms-txt-actually-work/
- **仕組み／なぜ効くか（効かない根拠）**:
  - **Google公式**: 2025年7月に Gary Illyes が「Googleは llms.txt をサポートしておらず、する予定もない」と確認。John Mueller は「廃れた keywords メタタグと同じ」と評した。**2026年6月のGoogleドキュメント更新で「llms.txt は Search のランキングにもAI Overviewsにも、良い影響も悪い影響も一切与えない。Searchは単に無視する」と明記**（https://www.1clickreport.com/blog/llms-txt-evidence-2026 ）。
  - **実測**: Ahrefs の137,000サイト調査で、**2026年5月にllms.txtファイルの97%がトラフィックゼロ**。5億件超のAIボット訪問を90日間監視して、**llms.txtを直接叩いたのは408件のみ**。AIボットは llms.txt が存在しないドメインに対してそれを要求すらしていない（探しに来てもいない）（同上）。
  - SE Ranking の約300,000ドメイン調査で、**llms.txt の有無とAI引用頻度に相関なし**（同上）。導入率は 10.13%。
  - OpenAI / Anthropic / Perplexity はいずれも robots.txt とユーザーエージェントについてのガイダンスは出しているが、**llms.txt が必要・推奨・引用判断に使用される、とは一切述べていない**（同上）。
- **具体手順（代わりにやること）**:
  1. llms.txt は作らない。
  2. 代わりに **robots.txt でAIクローラのポリシーを明示**する（GPTBot, ClaudeBot, PerplexityBot, Google-Extended などを許可するか拒否するかを意図的に決める）。
  3. 引用されたいなら**HTMLそのものを機械可読にする**（4-08のチャンク設計、4-09〜4-11の構造化データ）。
  4. AI検索での可視性は llms.txt ではなく**エッジログでのボット到達確認**で測る（4-14）。
- **日本での言及度**: **中（ただし方向が逆）**（※推定）。2025年に日本語圏でも「llms.txtを設置しよう」というLLMO/GEO系記事が急増した。**「効果がないという2026年の実証データ」と「Google公式が明確に無視すると言明した事実」は日本語圏でほとんど更新されていない**。この項目は「やらなくてよいことの特定」として価値がある。
- **noe-match適用度**: **A（＝実装しない、という判断）**。工数ゼロ。既に作ってあるなら残しておいても害はないが、更新の手間をかける必要はない。`robots.txt`は既にあるので、AIクローラの方針だけ明示的に書くのを推奨（30分）。
- **リスク・反証**: 将来的にどこかのAIプロバイダが採用する可能性はゼロではない。ただし**採用されてから作っても遅くない**（静的ファイル1枚）。

---

## 4-21. Google公式の否認 vs リーク／訴訟で判明した実態

- **一言で**: 2024年5月の Content Warehouse API ドキュメント流出と反トラスト訴訟により、**Googleが長年否定していた複数の要素（クリック信号、サイト全体の権威スコア、新規ドメインの扱い）が内部的に存在することが示された**。公式発言を額面通りに受け取らない読み方の基準。
- **海外での出典**:
  - SparkToro / Rand Fishkin「An Anonymous Source Shared Thousands of Leaked Google Search API Documents with Me」https://sparktoro.com/blog/an-anonymous-source-shared-thousands-of-leaked-google-search-api-documents-with-me-everyone-in-seo-should-see-them/
  - Hobo Web「The Google Content Warehouse API Leak of 2024」https://www.hobo-web.co.uk/the-google-content-warehouse-leak-2024/
  - Search Engine Journal「Rand Fishkin At MozCon: Rethinking Strategies Amid Google API 'Leak'」https://www.searchenginejournal.com/rand-fishkin-at-mozcon-rethinking-strategies-amid-google-api-leak/518504/
  - Growth Marketing「5 Google Ranking Claims the DOJ Trial Contradicted」https://growthmarketing.ai/ranking-lies-google-told
- **仕組み／なぜ効くか（何が判明したか）**:
  - 2024年3月13日、`yoshi-code-bot` が公開GitHubリポジトリに **2,500超のドキュメント・14,014の属性**を含む内部APIドキュメントを誤って公開。5月5日に Erfan Azimi が発見し Rand Fishkin と Mike King に共有、5月27日に公表（https://www.hobo-web.co.uk/the-google-content-warehouse-leak-2024/ ）。
  - **NavBoost**: クリックに基づく再ランキングシステム。`goodClicks` / `badClicks` / `lastLongestClicks` などのクリック分類が存在。Gary Illyes が長年「クリックはランキングに使っていない」と述べてきたことと矛盾する（同上）。
  - **siteAuthority**: サイト単位の権威指標。Googleは「ドメインオーソリティのようなものは無い」と何十年も否定してきた。
  - **hostAge**: 新規サイトを「サンドボックス」する目的で使われている様子が見られる。Googleは「サンドボックスは無い」と否定してきた。
  - 反トラスト訴訟（United States v. Google, 2023-2024）でも、Googleがツイートで否定してきた事柄が法廷で真実と判明したものがある（https://growthmarketing.ai/ranking-lies-google-told ）。
- **具体手順（実務への落とし込み）**:
  1. **Google公式の否定発言を「その要素が存在しない証拠」として扱わない**。「Googleがそう言った」は一次情報だが、それは「事実である」ことを意味しない。
  2. `siteAuthority` の存在を前提に、**サイト全体の品質の底上げ（オーファン解消、低品質記事の統合、著者エンティティ）にリソースを割く**判断は合理的。
  3. `hostAge`（サンドボックス）を前提に、**ドメイン2ヶ月の noe-match は「すぐには効かない」ことを織り込んだ期待値管理**をする。焦って施策を乱発しない。
  4. NavBoostを前提に、**CTRとエンゲージメント（タイトル・ディスクリプション・ファーストビュー）**を軽視しない。
  5. ただし**リークの数字を「現在の重み」として扱わない**（下記リスク参照）。
- **日本での言及度**: **中**（※推定）。2024年のリークは日本語でも報道された。しかし**「だから公式発言をどう読み替えるか」という運用原則にまで落とした日本語記事は少ない**。日本語圏はGoogle公式発言を規範として扱う傾向が強く、リークとの矛盾を実務判断に組み込む議論が薄い。
- **noe-match適用度**: **B（判断基準として）**。具体的な実装ではなく**意思決定のフレーム**として使う。特に `hostAge`／サンドボックスの前提は、開設2ヶ月のサイトの期待値管理に直結する。想定工数: ゼロ（読み物）。
- **リスク・反証**: **リークされたのは属性名と説明であって、重みやアルゴリズムそのものではない**。データは少なくとも5年前のものである可能性が指摘されており、また公開Document AI Warehouse APIに関連するもので検索ランキングの内部を露出したものではない、という反論もある（https://www.hobo-web.co.uk/the-google-content-warehouse-leak-2024/ ）。**「属性が存在する＝現在ランキングで使われている」ではない**。リークを根拠に極端な施策（クリック操作等）に走るのは論外。

---

## 4-22. サイト構造：フラット vs サイロ（クリック深度の実務結論）

- **一言で**: 海外の到達点は「**論理的な階層は保ちつつ、重要ページはホームから3クリック以内**」。純粋なフラットも純粋なサイロも推奨されていない。
- **海外での出典**:
  - Search Engine Land「Site architecture: Creating a website structure that ranks」https://searchengineland.com/guide/website-structure
  - onwardSEO「Flat vs. Deep Site Architecture: What's Better for SEO?」https://onwardseo.com/flat-vs-deep-site-architecture-whats-better-for-seo-in-2025/
  - EcomSEO「Site Architecture for Ecommerce」https://ecomseo.co/academy/site-architecture-for-ecommerce
- **仕組み／なぜ効くか**: **Googleはクリック深度が直接のランキング信号だとは述べていない**が、クロール優先度と内部リンク評価の流れに相関する（https://onwardseo.com/flat-vs-deep-site-architecture-whats-better-for-seo-in-2025/ ）。引用されている実測として「2024年の40のECサイトの調査で、**3クリック以内で到達できる商品ページは5クリック以上のページより2.4倍速くインデックスされた**」、「19サイトで、クロール深度とリンクエクイティの流れを優先した結果、**90日以内に非ブランドクリックが中央値18〜34%増加**」（https://ecomseo.co/academy/site-architecture-for-ecommerce ）。到達点は「重要テンプレートのクロール深度を制約し、権威ある内部リンクを張り、論理的に剪定された階層を持つ」こと。
- **具体手順**:
  1. 全記事のホームからの最短クリック距離を計算（4-06のグラフ解析で同時に出る）。
  2. **4クリック以上の記事をリストアップ**し、ハブページ（クラスタトップ）経由で3クリック以内に収める。
  3. URL構造はフラットに保つ（`/articles/{slug}/`）が、**リンク構造は階層的**にする。URLの階層とリンクの階層は別物。
  4. クラスタトップ（ハブ）ページを明示的に作り、そこから配下記事へリンク、配下記事からハブへ戻すリンクを張る。
  5. サイトマップは階層別に分割（noe-matchは既に分割運用済み）。
- **日本での言及度**: **低〜中**（※推定）。「サイト構造」「パンくず」「カテゴリ設計」は日本語にもある。しかし**「URL階層とリンク階層を分けて考える」「クリック深度3以内という定量基準」「Googleはクリック深度を直接のランキング信号とは言っていない、という前提の明示」**は日本語圏で明確に説明されない。日本語記事は「URLは浅くしましょう」でURL階層の話に矮小化されがち。
- **noe-match適用度**: **B**。URL構造は既に`/articles/{slug}/`のフラット型で問題なし。**問題はリンク階層側**（4-07のオーファン59件がまさにこれ）。クリック深度の実測がまだ無いので、まずグラフ解析で測る。想定工数: 4-06/4-07と同一スクリプトで済むので追加工数はほぼゼロ。
- **リスク・反証**: 引用した「2.4倍」「18〜34%」といった数値は**個別ベンダーのブログ記事に載ったもので、査読された調査ではない**。数値を鵜呑みにせず「方向性は正しい、倍率は当てにしない」という扱いが妥当。またクリック深度を下げるためにナビゲーションに大量のリンクを詰め込むと、1リンクあたりの評価が薄まる。

---

## 4-23. サイトマップと「差分」の整合（lastmod・分割・網羅率）

- **一言で**: サイトマップは「全URLが載っていること」と「lastmodが実際の更新を反映していること」の2点で価値が決まる。**惰性の自動更新は逆効果**。
- **海外での出典**:
  - Search Engine Journal「Google's John Mueller: Updating XML Sitemap Dates Doesn't Help SEO」https://www.searchenginejournal.com/googles-john-mueller-updating-xml-sitemap-dates-doesnt-help-seo/545547/
  - Search Engine Land Byline Dates Guide https://searchengineland.com/guide/byline-dates
  - Oncrawl（Crawl Statsとサイトマップの突合）https://www.oncrawl.com/general-seo/google-crawl-stats-report-log-file-analysis/
- **仕組み／なぜ効くか**: Muellerは「サイトマップの日付を自動で新しくしてもSEOには効かず、**むしろGoogleが実際の更新を見つけにくくする**」と明言している。つまりlastmodは「Googleに再クロールしてほしいURLを教える差分シグナル」であり、**全件が毎日更新されているとシグナルとして無価値になる**。
- **具体手順**:
  1. サイトマップの`<loc>`集合と、実際に存在する記事URL集合を突合し、**未収録URLをゼロにする**。
  2. `lastmod`は本文ハッシュ差分がある記事だけ更新（4-15と同じ判定を共有）。
  3. サイトマップを種別で分割（記事／ツール／固定ページ）し、GSCで**種別ごとのインデックス率**を見られるようにする。
  4. GSCのサイトマップレポートで「検出されたURL数」と「インデックス済み」の乖離を月次記録。
  5. `robots.txt`にサイトマップのURLを明記。
- **日本での言及度**: **中**（※推定）。サイトマップの基本は日本語でも十分説明されている。**「lastmodの自動更新は逆効果」というMuellerの明言、およびサイトマップ分割をインデックス率の診断装置として使う発想**は日本語圏で薄い。
- **noe-match適用度**: **A（実測で問題が見つかっている）**。**`sitemap-all.xml` の`<loc>`は230件、記事ディレクトリは256件 → 最大26件が未収録の可能性**。lastmodは230件全件に付与されているが、**それが実差分に基づくのか一括更新なのかを確認する必要がある**。既にサイトマップ分割は運用済み。想定工数: 突合スクリプト1時間、lastmod判定の改修半日。
- **リスク・反証**: サイトマップに載せてもインデックスされる保証はない（noe-matchの実測「申請なし1.7%」がそれを裏付けている）。サイトマップは発見の補助であり、インデックスの決定要因ではない。

---

## 4-24. 国内単一言語サイトの地域・実体シグナル（hreflang不要ケース）

- **一言で**: 単一言語・単一国のサイトに hreflang は不要。代わりに効くのは**運営者の実在性と所在の明示**であって、Googleビジネスプロフィールではない。
- **海外での出典**: ※専用検索未実施（検索クォータ枯渇）。以下は既存ソースからの導出。
  - Google「Creating Helpful, Reliable, People-First Content」（"Who, How, Why" の3観点で運営主体を明示せよ）https://developers.google.com/search/docs/fundamentals/creating-helpful-content
  - iPullRank「E-E-A-T and YMYL in the Age of AI Search」（Trust が E-E-A-T の中心であること）https://ipullrank.com/eeat-ymyl-ai-search
  - Schema Validator「Entity SEO & Schema Markup」https://schemavalidator.org/guides/entity-seo-schema-markup
- **仕組み／なぜ効くか**: hreflangは**同一コンテンツの言語/地域別バリアントが複数存在する場合のみ**の仕組みで、日本語単一サイトには適用対象がない（実装しても無害だが無意味）。一方でGoogleが helpful content の自己評価で明示的に求めているのは「**誰が（Who）作ったか、どうやって（How）作ったか、なぜ（Why）作ったか**」。ローカルビジネスでないアフィリエイトメディアには**LocalBusiness schema も NAP も GBP も不要**（むしろ実店舗が無いのにLocalBusinessを名乗るのは不適切）。必要なのは `Organization` + `Person`（4-10, 4-11）と、運営者情報・編集方針・お問い合わせ導線という**Trust の可視化**。
- **具体手順**:
  1. hreflang は実装しない。`<html lang="ja">` だけ正しく設定する。
  2. LocalBusiness / NAP / GBP は実装しない（実店舗が無いため不適切）。
  3. 代わりに `Organization`（`name`, `url`, `logo`, `sameAs`, `founder`, `knowsAbout`）を全ページ共通で持つ。
  4. 「運営者情報」「編集方針」「情報の更新方針」「お問い合わせ」の4ページを整備し、フッタから全ページからリンク。
  5. アフィリエイト表記（広告を含む旨）を明示する。これは景表法対応であると同時に、Googleが求める透明性（Why）に直結する。
  6. 日本固有の制度（結婚相談所連盟、婚姻届、児童手当等）を扱う際は**出典を政府・自治体の一次ソースにリンク**する。これが日本国内向けサイトにおける最も強い地域シグナル。
- **日本での言及度**: **低**（※推定。専用検索未実施）。日本語SEO記事は「E-E-A-Tのために運営者情報を書きましょう」までは言うが、**「hreflangは不要」「LocalBusinessを名乗ってはいけない」という"やらないことの明確化"**は説明されない。またWho/How/Whyという helpful content の3観点フレームも日本語圏で定着していない。
- **noe-match適用度**: **A（大半が既実装、残りは仕上げ）**。実測で `about.html`, `policy/editorial.html`, `policy/rating.html`, `policy/update.html`, `policy/research.html`, `privacy-policy.html`, `disclaimer.html` が既に存在し、**日本語アフィリエイトメディアとしてはかなり整っている**。残るギャップは 4-10（Personエンティティ）と 4-11（Organizationの`@id`統合）。想定工数: 4-10/4-11に含まれる。
- **リスク・反証**: Trust関連の整備がランキングを上げるという直接的な実証はない。**ASP審査の通過率やユーザーの信頼という副次効果の方が確実性が高い**。この項目は「SEOのため」より「メディアとして当然のため」と位置づけるのが健全。

---

## 4-25. `<table>` と定義リストのセマンティック実装（抽出しやすさ）

- **一言で**: 比較データは`<table>`、用語定義は`<dl>`。**見た目で表現するのではなく、タグの意味で表現する**とAI・検索双方の抽出精度が上がる。
- **海外での出典**: ※専用検索未実施（検索クォータ枯渇）。以下は既存ソースからの導出。
  - Promptwatch「Content Chunking」（AI systems process content in chunks bounded by heading elements, paragraph breaks, **list structures**, and semantic markers）https://promptwatch.com/glossary/content-chunking
  - Yoast Structured Data Guide https://yoast.com/structured-data-schema-ultimate-guide/
  - Search Engine Land Structured Data Guide https://searchengineland.com/structured-data-seo-what-you-need-to-know-447304
- **仕組み／なぜ効くか**: Promptwatchの記述にある通り、AIシステムは**リスト構造とセマンティックマーカーをチャンク境界として使う**。`<div>`で作った擬似テーブルは、行と列の対応関係が機械には復元できない。正しい`<table>`は `<caption>`（表が何を表すか）、`<th scope="col">`（列見出し）、`<th scope="row">`（行見出し）によって**セルの意味が一意に決まる**。定義リスト`<dl>/<dt>/<dd>`はHTMLで「これは用語とその定義である」を表現できる唯一のタグで、用語集・FAQ的な定義に最適。
- **具体手順**:
  1. すべての`<table>`に`<caption>`を付ける（「表1: 主要マッチングアプリの月額料金比較（2026年8月時点）」のように**対象と時点**を含める）。
  2. `<thead>`と`<tbody>`を分け、見出しセルは`<td>`ではなく`<th scope="col">`にする。
  3. 行見出し（サービス名など）も`<th scope="row">`にする。
  4. 用語定義を`<dl><dt>用語</dt><dd>定義</dd></dl>`に置き換える。
  5. 表の直前または直後に、**表の要点を1文のテキストで書く**（表を読めない抽出器のためのフォールバック）。
  6. 数値セルには単位を含める（「3,980円」であって「3980」ではない）。
- **日本での言及度**: **ほぼ無**（※推定。専用検索未実施）。日本語SEO記事で「`<th scope>`を付けよう」「`<caption>`を付けよう」と書いてあるものは**アクセシビリティ文脈以外ではほぼ皆無**。「AIに抽出されるためのHTMLセマンティクス」という切り口は日本語圏でまだ立ち上がっていない。**本領域で最も日本語情報が薄い項目のひとつ**。
- **noe-match適用度**: **A（実測で伸びしろが確定）**。実測: **`<table>` は206記事（80%）で使用中と良好。一方 `<dl>` は0件**。婚活ジャンルは「成婚料」「お見合い料」「IBJ/BIU/NNR」「活動初期費用」など定義が必要な用語が大量にあり、定義リスト化の余地が大きい。**Python生成なので既存テーブルへの`<caption>`/`<th scope>`一括付与はスクリプトで可能**。想定工数: テーブル改修スクリプト1日、定義リスト導入（テンプレート＋主要記事）1日。
- **リスク・反証**: **`<th scope>`や`<caption>`がランキングに影響するという実証はない**。効果はAI抽出の精度とアクセシビリティ。ただし**コストが低く、副作用がゼロ**なので実施しない理由もない。既存HTMLの一括書き換えは表崩れのリスクがあるので、変更後の目視確認を数記事分は必ず行うこと。

---

## 4-26. インデックス制御の測定基盤（IndexNow／申請運用の位置づけ）

- **一言で**: **GoogleはIndexNowをサポートしていない**（2026年2月時点）。Google向けにはGSCのURL検査からの申請しか手段がなく、noe-matchの実測（申請なし1.7%→申請あり90-100%）は極めて価値の高い一次データ。Bing系にはIndexNowが有効。
- **海外での出典**:
  - Pressonify「Does Google Support IndexNow in 2026? No — Here's Who Does」https://pressonify.ai/blog/indexnow-instant-indexing-press-releases-2026
  - CrawlWP「IndexNow vs Google Indexing API vs Sitemaps: What Actually Works in 2026」https://crawlwp.com/indexnow-vs-google-indexing-api-vs-sitemaps/
- **仕組み／なぜ効くか**:
  - **Googleは2021年10月からIndexNowをテストしてきたが、2026年時点で採用していない**。Google Indexing APIは求人情報とライブ配信に用途が限定されている（https://pressonify.ai/blog/indexnow-instant-indexing-press-releases-2026 ）。
  - **Bing / Yandex / Naver / Seznam / Yep が IndexNow をサポート**し、日次50億超のURL送信がある。**2026年2月時点でBingのクリックされたURLの22%がIndexNow経由の送信由来**（同上）。多くのサイトが数分でBingにインデックスされると報告している。
  - つまり**Google向けとBing向けで打ち手が完全に別**であり、日本語圏ではBing対策自体がほぼ議論されていない。
- **具体手順**:
  1. Google向け: 現行のGSC URL検査申請運用を継続。**申請あり/なしの対照実験データは資産なので、記録形式を維持する**（noe-matchは既に`index_experiment.md`, `index_baseline_20260801.json`, `index_history.json`, `index_requests_done.json` を保有）。
  2. Bing向け: IndexNowのAPIキーをサイトルートに置き、**新記事公開時に自動でping**するステップをビルドに追加（静的サイトなので `curl` 1本）。
  3. Bing Webmaster Toolsを導入して、Googleとは別系統でインデックス率を測る。
  4. 「インデックスされているのに露出しない」と「そもそもインデックスされていない」を切り分けて記録する（対処が全く違う）。
  5. IndexNowの効果は**Bingのインデックス速度**でのみ測る。Googleの数字と混ぜない。
- **日本での言及度**: **低**（※推定）。IndexNowは日本語でも紹介記事はあるが、**「Googleは非対応であり、これはBing系専用の施策である」という事実が曖昧なまま「インデックス高速化」として語られている**日本語記事が多い。また「Bingのクリック済みURLの22%がIndexNow由来」という定量データは日本語圏に無い。
- **noe-match適用度**: **B**。Google向けには追加価値なし（既に最良の運用をしている）。**Bing向けIndexNowは工数が極小（curl 1本）なので、やらない理由がない**。ただしBingからの流入は日本では小さいので優先度は中。想定工数: 1〜2時間。
- **リスク・反証**: IndexNowを送っても**インデックスされる保証はない**（クロールが早まるだけ）。またサイト健全性とエンジン側のクロールスケジュール次第で数時間〜数日の幅がある。Googleに対しては**一切効果がない**ので、Googleのインデックス改善を期待して導入しないこと。

---

## 領域4の未解決事項

1. **一次ソースの直接確認ができていない。** 本セッションではWebFetchが全ドメインでegress遮断され、Google Patents US11354342B2 本文、Search Quality Rater Guidelines PDF本体、developers.google.com の該当節、iPullRankの記事本文を**逐語で確認できていない**。特に以下は原文確認が必要:
   - Information Gain特許の請求項が「ランキング」に言及しているか、それとも「アシスタント応答の文書選択」に限定されているか（4-01の適用範囲の根拠が変わる）
   - QRGのExperience節と「Effortの証拠」節の正確な文言（4-12）
   - helpful contentガイドラインの日付・コンテンツ量に関する自己評価質問の原文（4-02, 4-15）
2. **日本語言及度を実検索で検証できたのは2手法のみ**（情報利得、コンテンツプルーニング）。残り24手法の「日本での言及度」は当方の知識に基づく推定であり、**実検索での再検証が必要**。特に 4-03（Koray）、4-16（query fan-out）、4-25（テーブル/定義リストのセマンティクス）は「ほぼ無」と判定したが、これは実検証すべき。
3. **Information Gain を実際に定量化する方法が未確定。** SERP見出しの差分を取る手法は提案したが、「情報利得スコアが実際にどう計算されるか」は特許を読まないと決められない。埋め込みベクトルの距離で近似する方法もあるが、それがGoogleの実装と一致する保証はない。
4. **content pruning の効果測定方法が確立していない。** Google公式が「効かない」と言い、実務家が「効いた」と言う状態で、**個人サイト規模で有意差を検出できる実験設計が存在しない**。noe-matchでやるなら「統合のみ実施、削除は保留、90日後にサイト全体インプレッションで前後比較」が現実的な妥協点だが、季節性と自然成長を除去できない。
5. **AI検索（AI Overviews / AI Mode）での可視性の測定手段が無い。** query fan-out（4-16）やチャンク設計（4-08）を実施しても、**効果を測る手段がGSCに存在しない**（GSCはAI Overviews由来のクリックを分離して報告しない）。エッジログでのAIボット到達確認（4-14）が唯一の間接指標だが、これは「クロールされた」であって「引用された」ではない。
6. **`knowsAbout` / `founder` / `@id` エンティティグラフの効果が未実証。** schema.org語彙としては正しいが、Googleの公式サポート対象外。**AI検索向けに効くという主張はすべて実務家の観測**であり、対照実験が存在しない。低コストなので実施は推奨できるが、効果の期待値は不明。
7. **noe-matchのクリック深度が未計測。** 4-06/4-07/4-22 のためにグラフ解析スクリプトが必要だが、本調査では被リンク数（indegree）までしか算出していない。ホームからの最短距離とアンカーテキスト分布は未計測。
8. **サイトマップ未収録の26URLの正体が未確認。** `sitemap-all.xml` 230件 vs 記事ディレクトリ256件の差分が、意図的な除外（noindex記事）なのか漏れなのかを確認していない。
9. **EXIF・オリジナル画像の効果について専用調査ができていない。** 4-12ではEXIFを意図的に扱わなかったが、「Googleが画像のEXIF（撮影日時・GPS）をExperienceの検証に使っている」という主張の真偽は未検証。**現時点ではGoogle公式の言及がないため根拠薄と判断した**が、Google Images側のドキュメントを確認する価値はある。
10. **日本の婚活ジャンル特有のYMYL判定が不明。** 婚活・結婚は QRG の YMYL カテゴリに明示的には含まれないが、「お金」「人生の重要な決定」に隣接する。**どの程度E-E-A-Tの基準が厳しく適用されるジャンルなのかが未確定**で、4-10（著者エンティティ）への投資量の判断根拠が弱い。

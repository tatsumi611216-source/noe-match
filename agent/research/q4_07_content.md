# 領域7: コンテンツ戦略・編集設計

- 調査日: 2026-08-27
- 担当領域: コンテンツ戦略・編集設計（英語圏では定番だが日本語SEO情報でほぼ流通していない型）
- 収録手法数: 30
- 参照ソース数: 一次ソースURL 62件（うちGoogle公式ドキュメント/公式ブログ 9件、Google Patents 2件）

---

## ⚠️ 調査条件の開示（重要・先に読むこと）

本レポートは以下の制約下で作成された。依頼主が結果を運用判断に使う前に、この節を必ず読むこと。

1. **ライブ検索は8回で打ち止めになった。** セッション全体のWebSearch予算（200回）が本エージェント起動前に他タスクで消費済みで、9回目以降は `web search budget (200 of 200)` で拒否された。依頼の「最低20回」は満たせていない。
2. **WebFetchは全ドメインでegress proxyにブロックされている。** `developers.google.com` `ahrefs.com` `detailed.com` `growandconvert.com` `animalz.co` すべて `EGRESS_BLOCKED`。curl経由も `CONNECT tunnel failed, response 403`。つまり**一次ソースの原文を直接開いて読むことは今回一切できていない**。
3. したがって本文中の記述は「**8回のライブ検索で確認できた事実**」＋「**学習知識（2026年5月カットオフ）に基づく記述**」の混成である。両者を以下のラベルで区別した。
   - `[検証済]` … 今回のライブ検索で文言・事実を確認した
   - `[知識ベース]` … 学習知識から記述。URLは実在するが原文の再確認はできていない
   - `[要原文確認]` … 引用文言の一字一句の正確性に自信が持てない箇所
4. **「日本での言及度」は実検索していない。** 日本語クエリを叩く予算が残らなかった。各項目に記載した言及度は学習知識ベースの**推定**であり、`【未検証・推定】` と明示した上で「検証すべき日本語クエリ」を併記してある。**依頼主側で必ず実検索して上書きすること。** ここが本レポート最大の弱点。
5. 数字にはURLを付したが、上記3の理由で数字も再確認できていないものがある。`[知識ベース]` の数字は発注前に必ず原典で確認すること。

---

## 目次

| # | 手法 | 日本での言及度(推定) | noe-match適用度 |
|---|---|---|---|
| 7-01 | Topical Map / Semantic Content Network | ほぼ無 | A |
| 7-02 | Source Context（情報源としての立ち位置固定） | ほぼ無 | A |
| 7-03 | Central Entity と Attribute 起点の見出し設計 | ほぼ無 | A |
| 7-04 | Core Section / Outer Section と公開順序 | ほぼ無 | B |
| 7-05 | Information Gain（10x contentからの移行） | 低 | A |
| 7-06 | Content-Market Fit | ほぼ無 | B |
| 7-07 | Know Simple / Do / Website / Visit-in-person 分類 | 低 | A |
| 7-08 | SERPからのintent逆算・mixed intent SERPの扱い | 低 | A |
| 7-09 | Intent Shift の検出 | ほぼ無 | B |
| 7-10 | Pain Point SEO / Bottom-of-Funnel First | ほぼ無 | A |
| 7-11 | Product-Led Content | 低 | A |
| 7-12 | Second-Order Pain Points | ほぼ無 | A |
| 7-13 | "Best X for Y" のmodifier粒度設計 | 低 | A |
| 7-14 | "X Alternatives" ページ | ほぼ無 | A |
| 7-15 | "X vs Y" Comparison ページ | 中 | A |
| 7-16 | Original Research Flywheel | 低 | A |
| 7-17 | "How We Test" / Testing Methodology ページ | ほぼ無 | A |
| 7-18 | First-Hand Testing Protocol（Experienceの証明） | ほぼ無 | A |
| 7-19 | Reviews System 要求要素チェックリスト | 低 | A |
| 7-20 | Helpful Content 自己評価質問群と Who/How/Why | 中 | B |
| 7-21 | Editorial Standards / Corrections Policy | ほぼ無 | B |
| 7-22 | Author Byline と "Who is behind this site" | 中 | A |
| 7-23 | Content Refresh の型と "significant update" | 中 | A |
| 7-24 | Content Pruning / Consolidation | 中 | B |
| 7-25 | Glossary / Definition Pages の資産化 | 低 | B |
| 7-26 | Calculator / Interactive Tool コンテンツ | 低 | A |
| 7-27 | Programmatic FAQ の罠（scaled content abuse） | 低 | A(回避) |
| 7-28 | アフィリ壊滅事例分析（HouseFresh / Retro Dodo） | ほぼ無 | B |
| 7-29 | 小サイトが大手に勝つ実例分析（Detailed / r/juststart） | ほぼ無 | B |
| 7-30 | Site Reputation Abuse を逆手に取る | 低 | B |

---

## 7-01. トピカルマップ／セマンティック・コンテンツ・ネットワーク（Topical Map / Semantic Content Network）

- **一言で**: キーワードのリストではなく「エンティティとその属性の網羅表」としてサイト全体の記事構成を先に設計しきり、その順序どおりに公開していく方法論。日本の「トピッククラスター／ピラーページ」とは別物で、粒度も網羅要求も一段深い。

- **海外での出典**:
  - Koray Tuğberk Gübür 本人の解説（Topical Authorityの提唱は2022-05-18とされる）: https://www.topicalauthority.digital/koray-tugberk-gubur `[検証済：ライブ検索で提唱日・肩書き・フレームワーク5要素を確認]`
  - The Koray Framework 解説（Source Context / Central Entity / Central Search Intent / Core Section / Outer Section の5本柱）: https://topicalmap.services/koray-framework/ `[検証済]`
  - Murat Ulusoy「Topical Maps — the end of keyword research」: https://www.muratulusoy.de/en/blog/topical-maps-content.html `[検証済：検索結果に出現]`
  - Koray「Topical Authority: 15 Semantically Optimized Topical Maps for SEO」: https://me.linkedin.com/posts/koray-tugberk-gubur_topical-authority-15-semantically-optimized-activity-7016024092373889024-vsMc `[検証済]`
  - SOP形式のトピカルマップ作成手順: https://rokonz.com/resources/topical-map-sop `[検証済]`

- **仕組み／なぜ効くか**:
  検索エンジンは「このサイトはこの話題について、聞かれうる問いの何％に答えているか」を近似的に評価する（Korayの主張は "topical coverage" と "historical data" の掛け算）。1記事1キーワードで穴だらけに書くと、どの記事も「その話題の一部しか持たないページ」になる。逆に、ある話題に属する問いの集合を先に列挙し尽くしてから埋めると、後発記事ほど既存記事の内部リンク文脈を継承して立ち上がりが速くなる。日本で流行した「ピラー＋クラスター」は階層図止まりで、**属性レベルの網羅表を作る工程がない**点が決定的に違う。 `[知識ベース]`

- **具体手順**:
  1. サイトの Central Entity（中心となる実体）を1つに決める。noe-matchなら「結婚相談所」ではなく「結婚を目的とした出会いの手段」レベルまで抽象度を上げるか下げるかをここで決めきる。
  2. そのエンティティの **属性（attribute）** を列挙する。価格、期間、成婚率、年齢層、契約形態、解約条件、地域、併用可否、失敗理由…。属性は「比較表の列になるもの」と考えると出しやすい。
  3. 属性 × エンティティのバリエーション（個別サービス名、年齢、地域、状況）で問いを機械的に展開し、数百〜千行のマップにする。
  4. 各行に「Core（収益に直結し、中心エンティティを直接説明する）」か「Outer（周辺文脈。信頼と網羅性を作る）」のラベルを付ける。
  5. **Core を先に、かつ短期間に集中して公開する。** Korayの主張の肝は「順序と密度」で、断続的に出すと効かない。
  6. 公開後、マップの行を消し込みながら内部リンクを属性名アンカーで張る。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「トピカルオーソリティ Koray」「トピカルマップ 作り方 SEO」「セマンティックSEO 中心エンティティ」。推定根拠は、日本語圏のSEO言説が「トピッククラスター」「網羅性」までで止まり、Korayの用語体系（source context / central entity / core section）を日本語で解説した記事をほぼ見た記憶がないこと。翻訳された書籍・記事も確認できていない。

- **noe-match適用度**: **A**。258本という規模は「マップを作らずに書き溜めた結果、どこに穴があるか分からない」状態になっている可能性が最も高いフェーズ。既存258本をマップ上にマッピングし直すだけで、書くべき残りが可視化される。想定工数: マップ初版 12〜20時間（属性列挙が本体）、既存記事のマッピング 8〜12時間。

- **婚活/結婚領域での具体化**:
  - Central Entity を「結婚相談所」に置いた場合の属性展開例: 料金体系（入会金／月会費／お見合い料／成婚料）、会員データベース（連盟：IBJ・BIU・日本結婚相談所連盟…）、カウンセラー、活動期間、成婚定義、休会・退会条件、乗り換え。→「結婚相談所 成婚料 相場」「結婚相談所 休会 できる」「結婚相談所 乗り換え 費用」…が機械的に出る。
  - 特に**「成婚の定義が相談所ごとに違う」**は属性起点でないと絶対に出てこない行。タイトル案:「『成婚』の定義は相談所ごとに違う——IBJ・BIU・独立系の成婚規定を原文で並べた」
  - Outer Section 側の例:「結婚相談所を辞めたあとの人間関係」「親に婚活を報告するタイミング」——収益に直結しないが、Central Entity の周辺文脈を埋める。

- **リスク・反証**: Koray の方法論は本人以外による再現検証が乏しく、「網羅すれば勝てる」の部分は Helpful Content 以降の環境では**薄い記事の量産と紙一重**。属性展開で出た問いのうち、実際に一次データや実測を載せられないものは書かない、という足切りを必ず入れること。網羅を目的化した瞬間に7-27（scaled content abuse）に落ちる。

---

## 7-02. ソース・コンテキスト（Source Context）

- **一言で**: 「このサイトは何で食っているか／どういう立場から語るか」を先に確定させ、全記事の切り口をその立場に一貫させる設計。Korayフレームワークの5本柱の第1。

- **海外での出典**:
  - The Koray Framework: https://topicalmap.services/koray-framework/ `[検証済：Source Context が5 fundamentals の筆頭であることを確認]`
  - Koray's Agents（Medium）: https://medium.com/@ktgubur/korays-agents-generative-ai-agents-for-semantic-seo-and-topical-authority-d4b247fac72a `[検証済]`

- **仕組み／なぜ効くか**:
  同じ「結婚相談所の選び方」でも、**紹介料で食う比較メディア**と**元カウンセラーの個人サイト**と**婚姻統計を扱う研究機関**では、書くべき見出しも、書けない見出しも違う。Source Context を明示すると (a) 記事間の主張がぶれない、(b) 「その立場だから書ける／その立場では書けない」が明確になり、依頼主の言う「空白理論」と直結する。Google側の対応概念は Helpful Content の "Why"（なぜこのコンテンツを作ったか）。 `[知識ベース]`

- **具体手順**:
  1. 「収益がどこから来るか」を1文で書く（例: 結婚相談所・婚活アプリのアフィリエイト）。
  2. 「その収益源ゆえに書けないこと」をリスト化する（例: 提携先の解約トラブルの実数）。
  3. 「その収益源と無関係だから書けること」をリスト化する（＝空白）。
  4. 「語り手の立場」を1文で固定（例: 自分で全部契約して自腹で試した個人）。
  5. 全記事テンプレの冒頭に、この立場が読者に伝わる1〜2文を定型で入れる。
  6. About / 運営者情報ページに 1〜4 をそのまま書く（7-22 と接続）。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「ソースコンテキスト SEO」「SEO 情報源としての立ち位置」。日本語では「サイトコンセプト」「ペルソナ」に吸収されてしまっており、**収益構造と語れる範囲を接続する**という核心が抜けている、というのが推定。

- **noe-match適用度**: **A**。依頼主の「空白理論」は事実上 Source Context の逆算であり、既に思想としては持っている。**明文化して全記事テンプレに落とす**のが未実施なら、そこが差分。想定工数: 4〜6時間＋既存記事への定型文差し込み。

- **婚活/結婚領域での具体化**:
  - 運営者情報に置く1文の案:「本サイトは結婚相談所・婚活アプリの紹介料で運営しています。したがって『どこにも入会しない方が良いケース』も、そう判断した根拠つきで書きます。逆に、提携先から提供されたデータは提供元を明記し、自分で検証できたものだけを数字として扱います。」
  - 記事タイトル案:「私が結婚相談所のアフィリエイトをやりながら、それでも『いま入会するな』と書く3つのケース」

- **リスク・反証**: 立場の明示は諸刃で、「アフィリ収益がある」と明記した瞬間に読者の一部は離脱する。ただし英語圏レビューメディアでは affiliate disclosure は法規制（米FTC）由来でほぼ必須であり、隠す方が長期的リスクが高い。日本の景表法・ステマ規制（2023年10月〜）とも整合する方向。

---

## 7-03. Central Entity と Attribute 起点の見出し設計

- **一言で**: 記事の見出しを「読者が検索しそうな言葉」から作るのではなく、「中心エンティティが持つ属性」から作る。属性の抜けが順位の抜けになる。

- **海外での出典**:
  - The Koray Framework（Central Entity の定義）: https://topicalmap.services/koray-framework/ `[検証済]`
  - Koray「Topical Authority and Topical Maps in 5 Minutes」: https://www.youtube.com/watch?v=bWjlnI4gXxo `[検証済]`
  - Advanced Strategies for Topical Maps: https://www.rankinghacks.com/koray-tugberk-guburs-topical-maps-in-seo/ `[検証済]`

- **仕組み／なぜ効くか**:
  検索エンジンがページを理解する単位は語ではなくエンティティ＋属性。「結婚相談所A」というエンティティに対し、SERPで競合が触れている属性（料金／会員数／成婚率／年齢層／エリア）を全部持っていないページは、その属性を含むクエリの束を取り逃す。見出しを属性名にすると、属性の抜けが目視できる。 `[知識ベース]`

- **具体手順**:
  1. 記事の中心エンティティを1つに固定（複数中心は分割する）。
  2. 属性リスト（7-01 の 2）から、この記事で扱う属性を選ぶ。
  3. H2 を属性名そのものにする（「料金」「会員数」ではなく「入会金・月会費・成婚料の内訳」のように属性＋粒度）。
  4. 各 H2 の直下1文目に**その属性の答えを断定で置く**（結論先出し）。
  5. 競合上位5件の H2 を属性に正規化して差分を取り、自分にない属性を追加候補にする。
  6. 属性ごとに「一次データ or 実測 or 体験」のどれで裏を取るか列を持つ。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「エンティティ 属性 見出し SEO」「セマンティックSEO 属性」。日本語では「共起語」「関連キーワード」で語られ、**属性という構造的な単位**では語られていないと推定。

- **noe-match適用度**: **A**。既存258本の見出しリライトに直接使える。想定工数: 主要50本の見出し監査で 15〜25時間。

- **婚活/結婚領域での具体化**:
  - 「結婚相談所A」記事の属性H2案:「入会金・月会費・お見合い料・成婚料の総額（12か月モデル）」「加盟連盟と検索できる会員数」「成婚の定義（規約原文）」「休会・中途解約時の返金規定（特定商取引法の適用有無）」「担当カウンセラーの変更可否」
  - 特に「解約時の返金規定」は属性起点でないと出ない。タイトル案:「結婚相談所10社の解約規定を契約書ベースで比較した——中途解約で返ってくる金額の実額」

- **リスク・反証**: 属性を全部H2にすると記事が長大化し、Know Simple クエリ（7-07）には過剰。属性網羅は Do/比較系ページ限定にすべき。

---

## 7-04. Core Section / Outer Section と公開順序

- **一言で**: トピカルマップを「収益と中心性に直結する Core」と「文脈を支える Outer」に二分し、Core を先に高密度で出しきってから Outer に移る、という公開スケジューリング。

- **海外での出典**:
  - The Koray Framework（Core Section / Outer Section）: https://topicalmap.services/koray-framework/ `[検証済]`
  - SOP: Topical Map Creation: https://rokonz.com/resources/topical-map-sop `[検証済]`

- **仕組み／なぜ効くか**:
  サイトの「何のサイトか」の学習は初期の公開群に強く引っ張られる。Outer から書き始めると（例: 結婚式の豆知識から始める）、収益ページが後から来ても中心性を取り戻すのに時間がかかる。Core を先に厚く出す＝サイトのトピック重心を最初から収益領域に置く。 `[知識ベース]`

- **具体手順**:
  1. マップ各行に Core / Outer をラベリング。
  2. Core の定義を「中心エンティティを直接説明し、かつ商用意図がある」に固定。
  3. Core を全部出しきるまで Outer に手を出さない（例外: Core の理解に前提が要る場合のみ）。
  4. Core 内でも、内部リンクの受け手になる「ハブ」を先に出す。
  5. Outer は Core への内部リンクを必ず1本以上持たせる。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「コアセクション アウターセクション SEO」「記事 公開順序 SEO」。日本語では「まずは書きやすい記事から」「集客記事→収益記事」という逆順の指導が主流で、Core 先行は少数派と推定。

- **noe-match適用度**: **B**。既に258本ある＝順序の設計はもう効かない。ただし**今後の新規追加を Core 優先に切り替える**、および既存の Outer 記事から Core への内部リンクを張り直す形で部分適用できる。想定工数: 内部リンク再設計 10〜15時間。

- **婚活/結婚領域での具体化**:
  - Core: 「結婚相談所 比較」「婚活アプリ 比較」「結婚相談所 料金」「婚活 費用 総額」
  - Outer: 「両家顔合わせ 服装」「結婚式 費用 分担」「新婚 家計 分け方」
  - Outer → Core リンク例:「両家顔合わせ 服装」記事の末尾から「そもそも顔合わせに至る出会い方別の期間比較」へ。

- **リスク・反証**: Core（商用意図）ばかり先に出すと、被リンクとブランド検索が育たないまま商用ページだけが並び、Helpful Content 的には「検索エンジン向けに作られたサイト」に見えるリスク。Core 先行は Original Research（7-16）とセットでないと危険。

---

## 7-05. インフォメーション・ゲイン（Information Gain）—— "10x content" 以降

- **一言で**: 「上位10件より10倍良いものを作る」（Rand Fishkin の 10x content）から、「**上位10件に**まだ**無い情報を1つでも足す**」への評価軸の移行。Googleの特許に "information gain score" が明示されている。

- **海外での出典**:
  - Google Patent US11354342B2「Contextual estimation of link information gain」: https://patents.google.com/patent/US11354342B2/en `[検証済：出願2018-10、公開2020-11、登録2022を確認]`
  - 同ファミリー US11720613B2: https://patents.google.com/patent/US11720613B2/en `[検証済]`
  - 同ファミリー US12013887B2: https://patents.google.com/patent/US12013887B2/en `[検証済]`
  - Search Engine Journal「Google's Information Gain Patent」: https://www.searchenginejournal.com/googles-information-gain-patent-for-ranking-web-pages/524464/ `[検証済]`
  - Semrush「What Is Information Gain in SEO & Does Google Measure It?」: https://www.semrush.com/blog/information-gain/ `[検証済]`
  - Moz / Rand Fishkin の 10x content 原典（Whiteboard Friday）: https://moz.com/blog/how-to-create-10x-content `[知識ベース]`

- **仕組み／なぜ効くか**:
  特許の記述は「an information gain score for a given document is indicative of additional information that is included in the document beyond information contained in documents that were previously viewed by the user」（ユーザーが既に見た文書に含まれる情報を**超えて**含まれている追加情報を示すスコア）`[検証済：この趣旨の記述をライブ検索で確認。ただし一字一句の原文照合は未実施＝要原文確認]`。
  つまり評価は「網羅度」ではなく「**差分**」。上位が全員書いていることを丁寧に書き直しても差分はゼロ。Google自身は information gain を使っているか明言していない（Semrush記事も "It's unclear whether Google uses information gain as described in its patent"）`[検証済]` が、AI Overviews / AI Mode 時代には「既出情報の再編集」はそもそも要約に吸収されるため、実務的な帰結は同じ。

- **具体手順**:
  1. 対象クエリの上位10件を開き、**各ページが提示している事実（数字・条件・手順）を1行ずつ抽出**して1枚の表にする。
  2. 表の行を重複排除する。残った行が「そのSERPの既知情報の全体集合」。
  3. その集合に**無い**行を最低3本作れるか自問する。作れないなら書かない。
  4. 差分行の作り方は3系統: (a) 一次データ（自分で取った数字）、(b) 一次ソースの原文（規約・法令・統計の原典を当たる）、(c) 体験の一意化（自分にしか無い条件下の記録）。
  5. 差分行を記事の**冒頭近く**に置く（末尾に埋めない）。
  6. タイトル・見出しに差分行を露出させる。

- **日本での言及度**: `【未検証・推定】低`
  検証用クエリ: 「インフォメーションゲイン SEO」「情報利得 SEO 特許」「10xコンテンツ 限界」。「情報の独自性」としては語られるが、**特許名・スコアという枠組み**で語る日本語記事は少数と推定。

- **noe-match適用度**: **A**。依頼主の「一次データ主義／実測主義／体験談の一意化」は information gain の実装そのもの。**手順1〜2の「既知情報の全体集合を表にする」工程を明文化してテンプレ化する**のが差分。想定工数: テンプレ作成 3時間、1記事あたり +40〜60分。

- **婚活/結婚領域での具体化**:
  - 「結婚相談所 成婚率」SERPの既知集合はおそらく「連盟公表値」「分母の定義が各社バラバラ」まで。差分候補:「各社IR・公式PDFの成婚率の**分母の定義を原文で並べた表**」「同一人物が3社に同時期に入会して受け取った紹介件数の実数」
  - タイトル案:「『成婚率60%』の分母は何人か——12社の公表資料の原文を並べて計算し直した」
  - タイトル案:「婚活アプリ5つに同じプロフィールで登録して30日放置した結果のいいね数（スクショ全掲載）」

- **リスク・反証**: 特許＝実装ではない。Googleは未確認。また差分作りにコストが掛かるため、記事あたり単価が上がり本数が落ちる。258本のサイトで全記事に適用するのは非現実的で、Core（7-04）に絞るべき。

---

## 7-06. コンテンツ・マーケット・フィット（Content-Market Fit）

- **一言で**: プロダクトの PMF に倣い、「そのコンテンツが、その読者層に対して、代替不可能な形でハマっているか」を指標化して測る考え方。トラフィック量ではなく「再訪・指名・引用」で測る。

- **海外での出典**:
  - Animalz のコンテンツ戦略解説（同社自身のコンテンツがトラフィックでなく評判で機能している構造）: https://www.animalz.co/blog/ `[知識ベース]` / 二次解説: https://seo.thefxck.com/articles/animalz-content-strategy/ `[検証済：検索結果に出現]`
  - Animalz vs Grow and Convert の戦略対比（editorial brand building vs bottom-funnel conversion）: https://discoveredlabs.com/blog/animalz-vs-grow-and-convert-editorial-brand-building-vs-bottom-funnel-conversion `[検証済]`
  - Superpath / Tracey Wallace 系の content-market fit 議論: https://www.superpath.co/blog `[知識ベース・要原文確認]`

- **仕組み／なぜ効くか**:
  検索流入だけを指標にすると、「検索需要はあるが自分が書く必然性がないページ」を量産してしまう。Content-Market Fit は逆に「自分が書く必然性が最大化する読者セグメント」を先に決め、そこに刺さるかで測る。指標例: 直帰でなく**回遊率**、指名検索（サイト名・著者名）の伸び、SNS/掲示板での自然言及、メール登録率。 `[知識ベース]`

- **具体手順**:
  1. 読者を「状況」で切る（属性でなく状況。例:「40代・地方在住・結婚相談所に2社入って辞めた人」）。
  2. その状況の人にしか価値がない記事を3本出す。
  3. 指標を検索流入から「指名検索数／回遊率／保存・共有」に切り替えて測る。
  4. 反応があったセグメントに寄せて縦に掘る。
  5. 反応がないセグメント向け記事は増やさない（トラフィックが出ていても）。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「コンテンツマーケットフィット」「content market fit 日本語」。PMF は流通しているが Content-Market Fit は未流通と推定。

- **noe-match適用度**: **B**。個人運営で258本という規模なら、まず7-10（BOFU優先）の方が金銭的リターンが早い。ただし**「どの状況の読者に刺さっているか」を測る仕組みが無いと7-01のマップも当てずっぽうになる**ため、測定基盤としては先に要る。想定工数: 指標設計とGA4/Search Console側の設定 6〜10時間。

- **婚活/結婚領域での具体化**:
  - セグメント案:「結婚相談所を退会したが婚活は続けたい人」——大手は入会を売るので退会後を書く動機が無い（＝空白）。
  - タイトル案:「結婚相談所を辞めた後の3か月にやることリスト——退会証明・データ削除・次の手段の選び直し」
  - 指標:「noe-match 退会」等のサイト名込み指名検索の発生を見る。

- **リスク・反証**: 指名検索が伸びるまで数か月〜年単位。個人運営のモチベーション設計として辛い。また状況セグメントを狭めすぎると絶対数が足りずアフィリ収益が立たない。

---

## 7-07. 検索意図の細分化（Know Simple / Know / Do / Website / Visit-in-person）

- **一言で**: 日本で流通している「Know / Do / Go / Buy」ではなく、Googleの品質評価ガイドライン（QRG）が実際に使っている4分類＋Know Simple という下位区分で意図を判定する。

- **海外での出典**:
  - Google Search Quality Rater Guidelines（原典PDF）: https://static.googleusercontent.com/media/guidelines.raterhub.com/en//searchqualityevaluatorguidelines.pdf `[知識ベース：URLは実在するが今回開けていない]`
  - Onely「Google's Quality Rater Guidelines」: https://www.onely.com/blog/googles-quality-rater-guidelines/ `[検証済]`
  - Portent「Overview of Google's Search Quality Rater Guidelines」: https://portent.com/blog/seo/googles-search-quality-evaluator-guidelines-for-seo.htm `[検証済]`
  - MarketMuse 解説: https://blog.marketmuse.com/google-search-quality-rater-guidelines-how-google-evaluates-your-site/ `[検証済]`

- **仕組み／なぜ効くか**:
  ライブ検索で確認できた分類は次のとおり `[検証済]`:
  - **Know** … 調べもの。うち **Know Simple** は「短く簡潔な答えが1つに定まる」もの（QRG上、モバイル画面に収まる程度の短答で満たされる問い）。
  - **Do** … 何かを実行したい。**購入（transactional）はここに入る**。日本語圏で言う「Buyクエリ」は独立カテゴリではなく Do の下位。
  - **Website** … 特定サイトへ行きたい（＝指名）。
  - **Visit-in-person** … 実店舗・場所へ行きたい（ローカル）。
  この分類の実務的価値は **Know Simple の識別**にある。Know Simple クエリに長文記事を当てるのは構造的な誤りで、AI Overviews に吸われて終わる。

- **具体手順**:
  1. 対象クエリを4分類＋Know Simple でラベリングする。
  2. Know Simple → 記事を作らない、または既存記事内のH2として吸収し、冒頭40字以内で答える。
  3. Know（非Simple）→ 長文可。ただし7-05の差分が必須。
  4. Do → 比較表・申込導線・条件分岐を主構造にする（散文にしない）。
  5. Website → 自サイトの指名を取りに行く施策（7-22, 7-16）に接続。
  6. Visit-in-person → 地域ページ。noe-match では「地域 × 結婚相談所」が該当。

- **日本での言及度**: `【未検証・推定】低`
  検証用クエリ: 「Know Simple クエリ」「品質評価ガイドライン 検索意図 4分類」「Visit-in-person 検索意図」。日本語SEOは「Know / Do / Go / Buy」の4分類が定着しており、これは**QRG準拠ではない独自流通版**。Know Simple と Visit-in-person という語の日本語解説は薄いと推定。

- **noe-match適用度**: **A**。既存258本の中に「Know Simple に長文を当てている記事」が相当数あるはず。それを見つけて統合・短縮するだけで7-24（pruning）にも効く。想定工数: 全記事のラベリング 8〜12時間。

- **婚活/結婚領域での具体化**:
  - Know Simple 例:「婚姻届 証人 何人」（答え: 2人）、「結納金 相場」（数字1つ）。→ 単独記事にせず「婚姻届の書き方」記事内のH2に吸収。
  - Know 例:「結婚相談所 仕組み」→ 長文可。
  - Do 例:「結婚相談所 無料相談 予約」→ 比較表と導線。
  - Visit-in-person 例:「札幌 結婚相談所」→ 地域ページ。実際に行ける店舗の実地情報（7-18）が差分になる。
  - タイトル案（Know Simple吸収型）:「婚姻届のよくある短答25問——証人の人数・訂正印・提出先を一覧で」

- **リスク・反証**: QRG は「ランキングの仕様書」ではなく評価者向けの手引きであり、分類がそのままアルゴリズムに実装されている保証はない。あくまで**意図判定の共通言語**として使うべき。

---

## 7-08. SERPからの意図逆算と mixed intent SERP の扱い

- **一言で**: キーワードツールの分類を信じず、実際のSERPの構成（ページタイプの内訳、リッチリザルト、上位の発行年月）から意図を読み取り、mixed intent（意図が割れている）SERPでは**分割ではなく1ページで両方を満たす**設計を取る。

- **海外での出典**:
  - Ahrefs「Search Intent」ガイド（3C: Content type / Content format / Content angle）: https://ahrefs.com/blog/search-intent/ `[知識ベース]`
  - Google QRG の Needs Met 評価（raters が query から intent を推定し result との適合を判定する構造）: https://www.onely.com/blog/googles-quality-rater-guidelines/ `[検証済]`
  - LinkBuildingHQ「User Intent in Search: Understanding the Nuances」: https://www.linkbuildinghq.com/blog/understanding-user-intent-in-search/ `[検証済]`

- **仕組み／なぜ効くか**:
  Googleは意図が割れているクエリでは**わざと異なるタイプのページを混在させる**（例: 上位に「定義解説」「比較記事」「公式サービス」「知恵袋」が混在）。ここで単一タイプに寄せると、混在枠のどれか1つとしか競合できない。逆に、混在の内訳比率を数え、多数派タイプの型を骨格にしつつ少数派の要素をセクションとして内包すると、複数の枠に対して適格になる。 `[知識ベース]`

- **具体手順**:
  1. 上位10件を「ページタイプ」で分類する（定義解説／比較リスト／個別レビュー/公式ページ／フォーラム・知恵袋／動画）。
  2. 内訳を数える。5:5 に近ければ mixed intent。
  3. 多数派タイプの**フォーマット**（リストか散文か、表の有無、文字数帯）を骨格に採用。
  4. 少数派タイプが提供している要素を、記事内の独立セクションとして必ず入れる。
  5. **知恵袋・Reddit が上位にいる場合は最優先の空白シグナル**（依頼主の空白理論と一致）。その質問文をそのままH2にする。
  6. 上位の発行/更新年月を記録する。全部直近1年なら鮮度要求が高いクエリ＝7-23のリフレッシュ対象。

- **日本での言及度**: `【未検証・推定】低`
  検証用クエリ: 「mixed intent SERP」「検索意図 SERP 逆算」「複合検索意図」。「上位を見て型を合わせる」は日本語でも語られるが、**内訳比率を数える／混在時に内包する**という具体手順は薄いと推定。

- **noe-match適用度**: **A**。ツール不要、既存記事のリライト判断に直結。想定工数: 1クエリ 15分、主要100クエリで 25時間。

- **婚活/結婚領域での具体化**:
  - 「婚活疲れ」のSERPは体験談ブログ／カウンセラー記事／知恵袋が混ざる典型的 mixed intent。→ 骨格は体験談、内部に「専門家の見解」「同じ悩みの実際の質問文と回答」を内包。
  - タイトル案:「婚活疲れで辞めた人の記録と、辞めずに続いた人との違い——知恵袋の質問120件を分類した」
  - 「結婚相談所 やめとけ」のSERPに掲示板が多いなら、そこは大手が触れない空白。

- **リスク・反証**: SERPは個人化・地域化・時期変動があり、1回の観測で決めるのは危険。同一クエリを時期を変えて2〜3回観測すること。

---

## 7-09. インテント・シフトの検出（Intent Shift Detection）

- **一言で**: 同じクエリのSERPの構成が時期をまたいで変わること（例: 情報記事中心 → EC/公式中心）を定点観測し、順位下落の原因が「自分の記事の劣化」か「意図の移動」かを切り分ける。

- **海外での出典**:
  - Ahrefs / Semrush の SERP 変動追跡機能に関する解説: https://ahrefs.com/blog/search-intent/ `[知識ベース]`
  - Google の「更新されたSERPは意図の再解釈を反映する」旨のコア更新解説: https://developers.google.com/search/updates/core-updates `[知識ベース：URL実在、今回開けず]`

- **仕組み／なぜ効くか**:
  順位が落ちたとき、多くの運営者は自記事を書き足す。しかし原因が intent shift（Googleがそのクエリに求めるページタイプを変えた）なら、書き足しは無意味で、**ページタイプごと作り替える**か**そのクエリを捨てる**のが正解。切り分けができないと工数が空転する。 `[知識ベース]`

- **具体手順**:
  1. 主要クエリのSERP上位10件のURL＋ページタイプを月次でスナップショット保存（スプレッドシート1枚で足りる）。
  2. 前月比でページタイプ内訳が30%以上入れ替わったクエリをフラグ。
  3. フラグ立ったクエリで自分の順位が落ちていたら intent shift と判定。
  4. 新しい多数派タイプに自記事の型が合うか判定。合わないなら別ページを新設し、旧記事は正規化 or 統合。
  5. 合わせられない（例: 公式サイトしか上がらなくなった）なら撤退し、そのクエリの内部リンクを他へ振り替える。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「インテントシフト SEO」「検索意図の変化 順位下落 切り分け」。日本語では順位下落→「リライト」一択の指導が支配的で、意図移動という原因仮説がほぼ提示されないと推定。

- **noe-match適用度**: **B**。仕組み化すれば強いが、個人運営で月次スナップショットを続ける運用負荷が現実的な障壁。上位20クエリに絞れば実行可能。想定工数: 初期構築 4時間＋月2時間。

- **婚活/結婚領域での具体化**:
  - 「婚活アプリ おすすめ」は各アプリ公式・ストアページが上がってくる方向にシフトしやすいクエリ。ここが公式中心に変わったら比較記事は撤退判断。
  - 逆に「結婚 手続き 一覧」のような手続き系は自治体公式にシフトしやすい。
  - 撤退後の受け皿タイトル案:「婚活アプリ公式が絶対に書かない『退会後にデータがどうなるか』を各社規約で確認した」

- **リスク・反証**: SERPスナップショットの取得を自動化するとスクレイピング規約の問題が出る。手動 or 正規のAPI/ツール利用に留めること。

---

## 7-10. ペインポイントSEO／ボトム・オブ・ファネル優先（Pain Point SEO / BOFU-First）

- **一言で**: トラフィックの大きい情報系記事を先に作るのではなく、**検索ボリュームが小さくても購入直前の読者しか打たないクエリ**を先に全部押さえる戦略。英語圏SaaSアフィリの標準手順。提唱は Grow and Convert（Benji Hyam / Devesh Khanal）。

- **海外での出典**:
  - Grow and Convert「Pain Point SEO」原典: https://www.growandconvert.com/content-marketing/pain-point-seo/ `[知識ベース：今回 EGRESS_BLOCKED で開けず。URLは実在]`
  - Animalz vs Grow and Convert 戦略対比（"bottom-funnel conversion" として Grow and Convert を位置づけ）: https://discoveredlabs.com/blog/animalz-vs-grow-and-convert-editorial-brand-building-vs-bottom-funnel-conversion `[検証済]`
  - Grow and Convert のケーススタディ群: https://www.growandconvert.com/case-studies/ `[知識ベース]`

- **仕組み／なぜ効くか**:
  Pain Point SEO が定義するBOFUキーワードのカテゴリは概ね次の5系統 `[知識ベース・要原文確認]`:
  1. **Category keywords**（"best X" / "X software" / "X tools"）
  2. **Comparison keywords**（"X vs Y"）
  3. **Alternatives keywords**（"X alternatives"）
  4. **Jobs-to-be-done keywords**（"how to 〈製品が解決する行為〉"）
  5. **Use case keywords**（"X for 〈特定用途/職種〉"）
  これらは検索ボリュームが小さいが、**打つ人の全員が既に購入検討に入っている**。CVRが桁違いに高く、少ない記事数で収益が立つ。日本の「まず集客記事を100本、そこから収益記事へ内部リンク」という定石とは順序が逆。

- **具体手順**:
  1. 提携している／したい商材を全部リストアップ。
  2. 各商材について上記5系統のクエリを機械的に生成（商材名 × vs × 他社名、商材名 + 代替、など）。
  3. 検索ボリュームが0〜10でも**消さない**。ボリュームで足切りしないのがこの手法の要点。
  4. 生成したクエリを全部書ききる。ここまでは情報系記事に一切手を出さない。
  5. 各BOFUページに、実測・一次データ（7-18）を必ず1つ以上入れる（これが無いと7-28の壊滅組と同じになる）。
  6. BOFUが埋まってから、そこへ内部リンクを流すための情報系記事を作る。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「ペインポイントSEO」「Grow and Convert 日本語」「BOFU SEO 順序」。日本語アフィリ論は「集客記事→収益記事」の順序がほぼ唯一の定石として語られており、**逆順を主張する体系だった日本語記事**は見た記憶がない。本レポート中で最も差分が大きい候補の1つ。

- **noe-match適用度**: **A**。258本ある中で BOFU 系がどれだけ埋まっているかを数えるだけで、即座に穴が見つかる。想定工数: クエリ生成 4時間、記事化は1本3〜5時間 × 本数。

- **婚活/結婚領域での具体化**:
  - Comparison:「ツヴァイ vs パートナーエージェント」「IBJメンバーズ vs サンマリエ」——実名比較は大手メディアが利益相反で書きにくい（＝空白）。
  - Alternatives:「結婚相談所の代わりになるもの5つ——アプリ・婚活パーティー・親戚紹介・地域の婚活支援・マッチングサービスの費用対効果」
  - Jobs-to-be-done:「1年以内に結婚したい人がやること」「38歳から婚活を始めるときの手順」
  - Use case:「地方在住者向けの結婚相談所」「バツイチ再婚向けの婚活サービス」「シングルマザー向け婚活」「転勤族の婚活」
  - Category:「オンライン完結型 結婚相談所」
  - タイトル案:「【実費公開】ツヴァイとパートナーエージェントに同時入会して6か月——支払総額とお見合い成立数を全部出す」

- **リスク・反証**: BOFU クエリは競合のアフィリエイターが最も密集する領域でもあり、被リンクゼロの個人サイトが即座に取れる保証はない。また実名比較は**薬機法ではないが景表法・名誉毀損のリスク**があり、根拠（規約原文・実費領収書）を必ず保存すること。BOFU 先行はドメイン評価がゼロだと空振りしやすく、noe-match のように既に258本ある中堅サイトの方が向いている。

---

## 7-11. プロダクト・レッド・コンテンツ（Product-Led Content）

- **一言で**: 記事の中で自然に商材を「解決手段の一部として」登場させ、記事の価値と商材の説明を分離しない書き方。Animalz が体系化。

- **海外での出典**:
  - Animalz「Product-Led Content」解説: https://www.animalz.co/blog/product-led-content/ `[知識ベース：EGRESS_BLOCKED で開けず。URL実在]`
  - Animalz Podcast Ep.59「Product-Led Content & Thinking Like a Strategist with Dr. Fio Dossetto」: https://www.animalz.co/blog/episode-59 `[検証済]`
  - Animalz「Don't Build It, Yet: How Content Can Validate Your Next Product Idea」（content-led product 側）: https://www.animalz.co/blog/content-led-product `[検証済]`

- **仕組み／なぜ効くか**:
  ライブ検索で確認できた定義は「content should always mention your product in a relevant way, directly benefit the reader, and help solve their questions」`[検証済]`——**(a) 関連性のある形で商材に触れる、(b) 読者に直接利益を与える、(c) 読者の問いを解決する** の3条件を同時に満たす。
  日本のアフィリ記事は「解説パート」と「商材紹介パート」が接ぎ木になっており、後者が広告として認識されて読み飛ばされる。Product-Led Content はこの接ぎ木を無くす。

- **具体手順**:
  1. 記事の問い（読者が解決したいこと）を1つに絞る。
  2. その問いの解決手順を**商材抜きで**書ききる。
  3. その手順の中で「商材を使うと具体的にどのステップが省けるか／変わるか」を特定する。
  4. そのステップの説明の**中に**商材を置く（末尾のバナーではなく）。
  5. 商材が不要なケースを明記する（これが無いと (b) を満たさない）。
  6. 商材紹介セクションを独立させない。

- **日本での言及度**: `【未検証・推定】低`
  検証用クエリ: 「プロダクトレッドコンテンツ」「product-led content 日本語」。「自然な訴求」としては語られるが、Animalz の3条件という形での体系は未流通と推定。

- **noe-match適用度**: **A**。既存記事の「まとめ：おすすめはこちら」型の接ぎ木を解体するリライトに直結。想定工数: 1本あたり 1〜2時間。

- **婚活/結婚領域での具体化**:
  - Before:「婚活の進め方（解説5000字）→ おすすめ結婚相談所3選（バナー）」
  - After:「婚活の進め方」の中の「STEP3: 相手の条件を絞り込む」で「自力で条件を絞ると◯◯の情報が取れない。連盟の検索システムを使うと年収証明の提出有無で絞り込めるので、ここが変わる。ただし条件を絞りすぎると母数が◯人まで落ちるので、その場合は相談所は不要」
  - タイトル案:「婚活の条件の絞り方——自力でできる範囲と、相談所の検索システムでしかできない範囲の境目」

- **リスク・反証**: ステマ規制（景表法、2023年10月施行）下では、商材を自然に埋め込むほど**広告であることの明示が必要**になる。埋め込みと明示は両立させること（記事冒頭にPR表記＋本文内で自然に配置、が安全側）。

---

## 7-12. セカンドオーダー・ペインポイント（Second-Order Pain Points）

- **一言で**: 商材が直接解決する痛み（一次）を書き尽くしたあと、「その痛みを持つ人が**同時に抱えている別の痛み**」に展開してトピックを拡張する方法。「もう書くことがない」の解決策。

- **海外での出典**:
  - Animalz「The Power of Second-Order Pain Points」: https://www.animalz.co/blog/second-order-pain-points `[検証済：ライブ検索で記事の存在と趣旨を確認]`

- **仕組み／なぜ効くか**:
  ライブ検索で確認できた趣旨は「every product has access to an entire constellation of second-order pain points, which can provide access to a far larger audience and a natural route of progression for companies that feel like they have 'run out' of topics to cover」`[検証済・要原文確認]`。
  一次ペインの検索需要は有限で、しかも競合が最も密集する。二次ペインは競合密度が低く、かつ読者層は同じなので内部リンクで一次ページへ流せる。**空白理論と最も相性が良い手法**。

- **具体手順**:
  1. 一次ペインを1文で書く（例: 「結婚相手が見つからない」）。
  2. そのペインを持つ人の**生活上の周辺状況**を10個挙げる（お金、親、仕事、住居、健康、時間、人間関係…）。
  3. 各状況で発生している別のペインを列挙（例: 親からの催促、周囲の結婚報告、貯金の使い道、転職と婚活の両立）。
  4. その二次ペインについて、一次ペインの文脈から書く（他サイトは一次ペインの文脈を持たない）。
  5. 二次ペインページから一次ペインページへ内部リンク。
  6. 二次ペインで反応が出たら、そこを新しい一次として3階層目に展開。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「セカンドオーダーペインポイント」「二次的ペインポイント コンテンツ」。日本語では「関連キーワード展開」に矮小化されており、**読者の同一性を保ったまま痛みを横に展開する**という発想は未流通と推定。

- **noe-match適用度**: **A**。「婚活・結婚・新生活」という時系列的に隣接する3領域を既に持っているサイトなので、構造的に相性が良い。想定工数: 展開表作成 4時間。

- **婚活/結婚領域での具体化**:
  - 一次:「結婚相手が見つからない」
  - 二次:「親からの結婚の催促にどう答えるか」「友人の結婚式に呼ばれ続ける時期の心理と出費」「婚活と転職を同時期にやるときの順序」「婚活費用を親に借りるべきか」「同僚に婚活していることを知られたくない」
  - タイトル案:「婚活中に友人の結婚式が重なる年の出費を実額で記録した——ご祝儀・交通費・衣装の年間合計」
  - タイトル案:「親の『まだ結婚しないの』に3年間どう答えてきたか——実際に使った返し方と、使って失敗した返し方」

- **リスク・反証**: 二次ペインは商材接続が弱く、収益にならないページが増える。Core/Outer（7-04）でいう Outer なので、Core が埋まる前にやると重心がずれる。

---

## 7-13. "Best X for Y" のモディファイア粒度設計

- **一言で**: 「best 〈カテゴリ〉」という大きい1ページで戦わず、「best 〈カテゴリ〉 for 〈状況/属性/用途〉」を**状況の数だけ**個別ページ化する。粒度をどこで切るかの設計が本体。

- **海外での出典**:
  - HouseFresh の「best air purifier for pets」分析（このクエリの構造とSERP独占状況の実例）: https://housefresh.com/david-vs-digital-goliaths/ `[検証済：クエリ名と上位サイト名まで確認]`
  - Google「Write high quality reviews」の "Cover comparable products to consider, or explain which products might be best for certain uses or circumstances" `[検証済：この趣旨をライブ検索で確認／要原文確認]`: https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews
  - Grow and Convert の Category / Use case キーワード分類: https://www.growandconvert.com/content-marketing/pain-point-seo/ `[知識ベース]`

- **仕組み／なぜ効くか**:
  "best X" 単体は大手メディアが被リンクで独占している（HouseFresh の事例がまさにそれ）。一方 "for Y" 付きは (a) 検索者の状況が確定しているので**答えが一意化でき**、(b) 大手は状況ごとの実測をしていないので差分を作りやすい、(c) CVRが高い。粒度は「答えが変わる境目」で切る——状況が変わっても推奨が変わらないなら、そのモディファイアはページを分ける価値がない。 `[知識ベース]`

- **具体手順**:
  1. 「best 〈カテゴリ〉」の推奨が**変わる要因**を列挙する（予算、年齢、地域、期間、前提条件）。
  2. 各要因で推奨が実際に変わるかを検証する。変わらない要因は捨てる。
  3. 変わる要因の組み合わせでページを起こす。
  4. 各ページの結論を**必ず別々にする**（同じ1位を並べるならページを分けない）。
  5. 親ページ（best 〈カテゴリ〉）から全子ページへリンク、子から親へ戻す。
  6. 子ページには、その状況固有の実測（7-18）を必ず1つ入れる。

- **日本での言及度**: `【未検証・推定】低`
  検証用クエリ: 「おすすめ ◯◯向け 記事 分け方」「best for モディファイア SEO」。「◯◯向けおすすめ」記事自体は日本にも大量にあるが、**「推奨が変わる境目でのみ分割する」という設計原則**として語られておらず、結果として中身が同じ量産ページになっているのが実情と推定。

- **noe-match適用度**: **A**。想定工数: 要因洗い出し 3時間、1ページ 4〜6時間。

- **婚活/結婚領域での具体化**:
  - 推奨が実際に変わる要因:「年齢帯（20代/30代前半/30代後半/40代以上）」「居住地（都市部/地方）」「予算上限」「再婚か初婚か」「子どもの有無」「活動可能な曜日」
  - 推奨が変わらない要因（分けない）: 血液型、趣味、身長 など
  - タイトル案:「地方在住者向けの結婚相談所——オンライン面談のみで完結できる社と、支店に行かないと動けない社を実際に問い合わせて分けた」
  - タイトル案:「40代の再婚に向く結婚相談所——年齢上限と再婚者比率を各社に問い合わせた実数」

- **リスク・反証**: 状況の掛け算でページを増やすと7-27（scaled content abuse）に直行する。「推奨が変わらないなら分けない」の足切りを厳守すること。実測を伴わない for Y ページは作らない。

---

## 7-14. "X Alternatives" ページ

- **一言で**: 「〈特定サービス名〉の代わり／代替」を狙う独立ページ。英語圏SaaSアフィリでは最重要ページ種の1つだが、日本ではほぼ体系的に作られていない。

- **海外での出典**:
  - Grow and Convert の Pain Point SEO における Alternatives カテゴリ: https://www.growandconvert.com/content-marketing/pain-point-seo/ `[知識ベース]`
  - Ahrefs 自身が "Ahrefs alternatives" 等の自社比較ページを持つ運用: https://ahrefs.com/blog/ `[知識ベース]`

- **仕組み／なぜ効くか**:
  「X alternatives」を検索する人は **(a) X を既に知っており、(b) X に不満があるか予算が合わず、(c) 今すぐ別を探している**。BOFUの中でも最も購買に近い。かつ **X の運営会社自身は絶対にこのページを作らない**（利益相反）ため、構造的な空白。 `[知識ベース]`

- **具体手順**:
  1. 領域内の主要サービス名を全部リスト化。
  2. 各サービスについて「なぜ人が離れるか」を実際の口コミ・掲示板から抽出（推測しない）。
  3. 離脱理由ごとに代替候補を割り当てる（理由が違えば代替も違う）。
  4. 「Xで満足している人はそのままでいい」ケースを明記する（信頼の担保）。
  5. 比較表は必ず「Xの何が不満か」を行にする（機能一覧にしない）。
  6. X自体の解約手順・違約金も書く（他が書かない実務）。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「◯◯ 代わり」「◯◯ 代替 サービス」「alternatives ページ SEO」。日本語では「◯◯ 解約」「◯◯ 評判」は作られるが、**「代替」を独立ページ種として設計する**発想は未流通と推定。ここも差分が大きい候補。

- **noe-match適用度**: **A**。実装が軽く（1ページ4〜6時間）、CVRが高い。想定工数: 主要10サービス分で 50時間程度。

- **婚活/結婚領域での具体化**:
  - タイトル案:「ペアーズの代わりを探している人へ——『マッチしない』『真剣度が低い』『既婚者が混じる』の3つの不満別に代替を分けた」
  - タイトル案:「結婚相談所が高すぎると感じたときの代替5つ——月2万円未満で続けられる選択肢を費用実額で比較」
  - タイトル案:「ゼクシィ縁結びエージェントの代わり——同じIBJ加盟で店舗数が多い社／料金が安い社／担当固定の社」
  - 表の行の例:「担当が変わりすぎる」「紹介人数が少ない」「オンライン対応が弱い」「解約金が高い」

- **リスク・反証**: 特定サービスの不満を列挙する構造なので、**事実に基づかない記述は名誉毀損・信用毀損のリスク**。口コミ引用は出典URLと取得日を必ず残す。また提携先の代替を書くと提携解除される可能性がある（Source Context の問題）。

---

## 7-15. "X vs Y" コンパリゾン・ページ

- **一言で**: 2社（2製品）の直接比較だけで1ページを構成する型。3社以上の「まとめ比較」とは別物として設計する。

- **海外での出典**:
  - Grow and Convert の Comparison キーワード分類: https://www.growandconvert.com/content-marketing/pain-point-seo/ `[知識ベース]`
  - Google「Write high quality reviews」の "Explain what sets a product apart from its competitors" `[検証済：趣旨確認／要原文確認]`: https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews
  - Discovered Labs による bottom-funnel 戦略の整理: https://discoveredlabs.com/blog/animalz-vs-grow-and-convert-editorial-brand-building-vs-bottom-funnel-conversion `[検証済]`

- **仕組み／なぜ効くか**:
  「A vs B」を打つ人は候補を**2つまで絞りきっている**。まとめ比較記事は「まだ絞れていない人」向けで、必要な情報の粒度が違う。vs ページで必要なのは網羅ではなく**決定打**——「この1点で分かれる」を示すこと。 `[知識ベース]`

- **具体手順**:
  1. 実際に併記検索されている組み合わせを特定する（サジェスト・関連検索から）。
  2. 2社の差が**実際に出る項目**を3つに絞る（全項目を並べない）。
  3. 「Aを選ぶべき人／Bを選ぶべき人」を冒頭200字以内に置く。
  4. 差が出ない項目は「同じ」と明記する（差を捏造しない）。
  5. 両方に実際に接触した記録（問い合わせ・見学・入会）を証拠付きで載せる。
  6. まとめ比較ページから vs ページへ、vs ページからまとめへ相互リンク。

- **日本での言及度**: `【未検証・推定】中`
  検証用クエリ: 「◯◯ 比較 どっち」「A vs B 記事 SEO」。「どっちがいい」系記事は日本にも多いが、**BOFUページ種として体系的に全組み合わせを埋める**運用は少ないと推定。手法自体の認知は中程度。

- **noe-match適用度**: **A**。想定工数: 1ページ 4〜8時間（実接触を伴うと増える）。

- **婚活/結婚領域での具体化**:
  - タイトル案:「IBJメンバーズとパートナーエージェントはどっちか——両方に無料相談に行って比較した、料金以外の3つの分かれ目」
  - タイトル案:「ペアーズとwith、30代後半が使うならどっちか——同一プロフィールで30日運用したマッチ数の実数」
  - 冒頭200字の型:「結論: 担当に伴走してほしいならA、自分で検索して動きたいならB。料金総額は12か月でAが約◯万円、Bが約◯万円で、差は◯万円。」

- **リスク・反証**: 実接触の記録がないと、7-28で告発された「テストしていない比較記事」と同じものになる。また片方の提携報酬が高い場合に結論が歪むので、**報酬額を結論に影響させていないことを明記する**か、報酬構造そのものを開示するのが英語圏の作法。

---

## 7-16. オリジナル・リサーチ・フライホイール（Original Research Flywheel）

- **一言で**: 自分で調査データを作り→それが引用・被リンクされ→ドメイン評価が上がり→他の商用ページが上がる、という循環を意図的に回す。単発の「独自調査」ではなく**回す仕組み**として設計するのが要点。

- **海外での出典**:
  - Google Helpful Content の "Does the content provide original information, reporting, research, or analysis?" `[検証済：この設問がGoogle公式の自己評価質問に含まれることを確認]`: https://developers.google.com/search/docs/fundamentals/creating-helpful-content
  - Google Patent「Contextual estimation of link information gain」（新規情報の評価）: https://patents.google.com/patent/US11354342B2/en `[検証済]`
  - Animalz「Don't Build It, Yet: How Content Can Validate Your Next Product Idea」（コンテンツが先行して検証になる構造）: https://www.animalz.co/blog/content-led-product `[検証済]`
  - SparkToro / Amanda Natividad の zero-click content 論（調査結果を要約ごと外部プラットフォームに出す）: https://sparktoro.com/blog/ `[知識ベース：Amanda Natividad の "zero-click content" 概念。今回原文未確認]`

- **仕組み／なぜ効くか**:
  被リンクは「事実として引用できる数字」に最も集まる。感想・意見にはリンクされない。統計・調査は**一度作れば何年も引用され続ける**ストック資産で、しかも競合が真似するには同じコストが要る。個人サイトが大手に勝てる数少ない構造的優位。 `[知識ベース]`

- **具体手順**:
  1. 「この領域で誰も数えていない数字」を10個書き出す。
  2. うち、自分1人で1〜3日で取れるものを選ぶ（大規模調査でなくてよい）。
  3. 方法（サンプル数、期間、取得方法、限界）を先に決め、記事に明記する。
  4. 数字を**引用しやすい形**にする: 図表を1枚、要約1文、引用用の一文（「〈サイト名〉の調査によると◯◯は◯%」）をページ内に置く。
  5. 数字を出したあと、関連する既存記事から全部リンクを張る。
  6. 定点化する（同じ調査を毎年やる＝「◯年版」として再引用される）。

- **日本での言及度**: `【未検証・推定】低`
  検証用クエリ: 「独自調査 被リンク SEO」「オリジナルリサーチ コンテンツ」。「独自調査は良い」までは言われるが、**フライホイール（循環）として設計し定点化する**運用は薄いと推定。

- **noe-match適用度**: **A**。依頼主が既に「一次データ主義」を掲げているなら、あとは**定点化と引用されやすい形の整備**だけ。想定工数: 1調査あたり 15〜30時間、年2〜3本。

- **婚活/結婚領域での具体化**:
  - 調査案1:「結婚相談所50社の料金表を全部集計した——入会金・月会費・成婚料の中央値と分布（2026年版）」（公式サイトの公表価格を集めるだけで成立、著作権リスクも低い）
  - 調査案2:「主要結婚相談所20社の『成婚』の定義を規約原文から分類した——交際期間◯か月で成婚とみなす社が◯社」
  - 調査案3:「婚活アプリ10本の退会後データ削除ポリシーを利用規約から抽出した」
  - 引用用一文の例:「Noe結婚設計室の2026年調査によると、結婚相談所50社の成婚料の中央値は◯万円だった。」
  - 定点化:「2027年版」「2028年版」と毎年更新（7-23と接続）。

- **リスク・反証**: 料金表の集計は公表情報の再構成なので比較的安全だが、**表全体の転載**は著作権上グレー。自分で数値を抽出して統計量にする形にすること。また調査の方法論が甘いと数字が誤りとなり、7-20の "Does the content have any easily-verified factual errors?" に直撃する。

---

## 7-17. "How We Test" / テスト方法論ページ（Testing Methodology Page）

- **一言で**: レビューの結論ページとは別に、**「どうやって試験したか」だけを説明する独立ページ**を持つ。英語圏レビューメディアの必須装備で、日本のアフィリサイトにはほぼ存在しない。

- **海外での出典**:
  - RTINGS のテスト方法論公開（テスト方法・写真・動画を公開し、機材を自費購入、生データも公開）: https://www.rtings.com/ `[検証済：ライブ検索で「publishes their testing methods, photos, and videos」「purchases their own products rather than accepting cherry-picked units」「publishes the original data from its tests」を確認]`
  - Wirecutter の "What, Why, How" 構造（何を推すか／なぜか／どう試験したか）: https://www.nytimes.com/wirecutter/ `[検証済：構造の記述をライブ検索で確認]`
  - Google「Write high quality reviews」の "Provide evidence such as visuals, audio, or other links of your own experience" `[検証済]`: https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews
  - Wikipedia「RTINGS」（透明性メーター等の記述）: https://en.wikipedia.org/wiki/RTINGS `[検証済]`

- **仕組み／なぜ効くか**:
  レビュー記事の中に方法論を書くと毎回長くなり、かつ読者は読まない。独立ページにすると (a) 全レビューからリンクできる、(b) そのページ自体が被リンクを集める、(c) Google側の「Who/How/Why」の **How** に対する直接的な回答になる。RTINGS が実際にやっているのは「機材を自費購入」の明記——これは提供品レビューとの決定的な差別化で、日本のサイトはここを書かない。 `[検証済＋知識ベース]`

- **具体手順**:
  1. `/how-we-test/`（または `/testing-methodology/`）という固定URLを作る。
  2. 書く項目: ①誰が試すか ②どうやって入手したか（自費/提供/貸与）③試験の期間と条件 ④測る項目とその定義 ⑤スコアの付け方 ⑥利益相反の扱い ⑦間違いがあったときの訂正手順（7-21へリンク）
  3. 全レビュー記事の冒頭または方法論セクションからこのページへリンク。
  4. 「今回のレビューではこの方法論のうち◯と◯を実施」と記事ごとに明記（全部やったフリをしない）。
  5. 方法論を変えたら改訂履歴を残す。
  6. About / 運営者情報からもリンク。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「検証方法 ページ アフィリエイト」「どうやって比較したか ページ」「レビュー 方法論 開示」。日本の比較サイトで「比較基準」を書くところはあるが、**独立URLの方法論ページ**を持つ例はほぼ記憶にない。本レポート中で最も実装が軽く、かつ差分が大きい候補。

- **noe-match適用度**: **A**。1ページ作るだけ。想定工数: 6〜10時間（方法論を実際に決める時間が本体）。

- **婚活/結婚領域での具体化**:
  - ページタイトル案:「Noe結婚設計室が結婚相談所・婚活サービスをどう調べているか（調査方法とお金の出どころ）」
  - 見出し案:
    - 「誰が調べているか（運営者1名／自身の婚活歴／相談所に入会した実績）」
    - 「費用は誰が払っているか——入会金・月会費は全額自費。提供・無償提供を受けた場合は該当記事に必ず明記します」
    - 「何を測るか——①契約前に開示される情報の量 ②初回面談から初お見合いまでの日数 ③30日あたりの紹介件数 ④解約時の返金額 ⑤担当者の変更可否」
    - 「測っていないこと——成婚率は各社の定義が異なるため、当サイトでは横並び比較の指標にしません」
    - 「訂正について」
  - 「測っていないこと」を書くのが英語圏流で、これが日本には無い。

- **リスク・反証**: 方法論を公開すると、**やっていないことが露見する**。逆に言えば、実測が伴わないサイトはこのページを作れない。作った以上は守る必要があり、記事ごとの実施状況の管理コストが発生する。

---

## 7-18. ファーストハンド・テスティング・プロトコル（First-Hand Testing Protocol）

- **一言で**: 「体験しました」と書くのではなく、**体験したことが第三者に検証可能な形で残る手順**を事前にプロトコル化しておく。E-E-A-T の Experience を「証明」に変える。

- **海外での出典**:
  - Google「Write high quality reviews」: "Provide evidence such as visuals, audio, or other links of your own experience with the product, to support your expertise and reinforce the authenticity of your review." `[検証済：ライブ検索でこの文言の趣旨を確認／一字一句は要原文確認]` https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews
  - 同「Share quantitative measurements about how a product measures up in various categories of performance.」`[検証済・要原文確認]`
  - Google の April 2023 Reviews Update が experience を強く要求した経緯: https://www.amsive.com/insights/seo/googles-newest-reviews-update-elevates-real-life-experience/ `[検証済]`
  - RTINGS の自費購入＋生データ公開: https://www.rtings.com/ `[検証済]`

- **仕組み／なぜ効くか**:
  Experience は主張ではなく**痕跡**で示す。痕跡の型は3つ: ①タイムスタンプのある記録（領収書、メール、予約確認、アプリのスクショ）②定量値（回数、日数、金額、件数）③失敗の記録（成功談だけの体験談は疑われる）。事前にプロトコル化しておかないと、体験した後では痕跡が取れない。 `[知識ベース＋検証済（Google文言）]`

- **具体手順**:
  1. 体験を始める**前に**、記録する項目を決める（日付、金額、担当者名の有無、やり取りの回数）。
  2. スクリーンショットの命名規則を決める（`YYYYMMDD_サービス名_画面名`）。
  3. 領収書・契約書・メールをPDFで保存（記事に載せる際は個人情報をマスク）。
  4. 定量値を毎回同じ単位で取る（他サービスと並べられるように）。
  5. 「うまくいかなかったこと」を必ず1つ以上記録する。
  6. 記事化時に、①いつ ②いくら払って ③何回やって ④結果どうだったか を冒頭ブロックに定型で置く。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「実体験 証明 SEO」「E-E-A-T 経験 証明方法」「レビュー 一次体験 記録」。「体験談を書こう」は大量にあるが、**記録プロトコルを事前に設計する**という運用論は未流通と推定。

- **noe-match適用度**: **A**。依頼主の「体験談の一意化」を実装レベルに落とすもの。想定工数: プロトコル策定 4時間、以後は体験ごとに +20〜30%の手間。

- **婚活/結婚領域での具体化**:
  - 記事冒頭の定型ブロック案:
    ```
    このレビューの前提
    ・調査期間: 2026年3月1日〜5月31日（92日）
    ・支払総額: 231,000円（入会金 33,000円／月会費 16,000円×3／お見合い料 11,000円×15）※領収書あり
    ・お見合い成立: 15件／申込 87件／受諾率 17.2%
    ・費用は全額自費。当サイトは同社のアフィリエイトプログラムに参加しています。
    ・うまくいかなかった点: 担当者が期間中に1回交代し、引き継ぎで2週間動きが止まった
    ```
  - タイトル案:「結婚相談所に92日間・231,000円払って何が起きたか——申込87件・成立15件の全記録」
  - マスク済みスクショ:「会員検索画面の絞り込み条件」「担当者からのメール（氏名マスク）」

- **リスク・反証**: 相談所の会員情報・他会員の写真は**絶対に載せられない**（個人情報・肖像権）。掲載できるのは自分の契約情報と自分の画面のみ。また規約でスクリーンショット禁止のサービスがあるため、事前に規約を確認すること。「自費」を貫くとコストが重い。

---

## 7-19. Reviews System 要求要素チェックリスト（Google公式の逐条リスト化）

- **一言で**: Googleの「高品質なレビューの書き方」ドキュメントの箇条書きを**そのままチェックリスト化して編集フローに埋め込む**。日本語では要約されて紹介されるため、逐条での運用が行われていない。

- **海外での出典**:
  - Google Search Central「How To Write Reviews / Write high quality reviews」: https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews `[検証済：ページの存在と主要文言の趣旨を確認。EGRESS_BLOCKEDのため全文照合は未実施＝要原文確認]`
  - Reviews Update の履歴: https://developers.google.com/search/updates/ranking `[知識ベース]`
  - 2023年4月 Reviews Update の解説: https://www.amsive.com/insights/seo/googles-newest-reviews-update-elevates-real-life-experience/ `[検証済]`
  - 2021-2022 Product Reviews Updates の整理: https://www.amsive.com/insights/seo/googles-2021-2022-product-reviews-updates-what-happened/ `[検証済]`

- **仕組み／なぜ効くか**:
  Googleが公開している要求は**具体的な行為リスト**であり、抽象的な品質論ではない。以下は当該ドキュメントの主要項目（趣旨。`[要原文確認]`）:
  - 「Evaluate from a user's perspective.」（ユーザー視点で評価する）
  - 「Demonstrate that you are knowledgeable about what you are reviewing」（レビュー対象について精通していることを示す）
  - 「**Provide evidence such as visuals, audio, or other links of your own experience** with the product, to support your expertise and reinforce the authenticity of your review.」`[検証済：この文言をライブ検索で確認]`
  - 「**Share quantitative measurements** about how a product measures up in various categories of performance.」`[検証済]`
  - 「**Explain what sets a product apart from its competitors.**」
  - 「Cover comparable products to consider, or explain which products might be best for certain uses or circumstances.」
  - 「Discuss the benefits and drawbacks of a particular product, based on your own original research.」
  - 「Describe how a product has evolved from previous models or releases」（前モデルからの変化）
  - 「Identify key decision-making factors for the product's category and how the product performs in those areas.」
  - 「Describe key choices in how a product has been designed and their effect on the users beyond what the manufacturer says.」
  - ランキング形式について: 十分な独自コンテンツを持たせること、および **複数の販売者へのリンクを提供して読者が購入先を選べるようにすること**。
  この最後の「複数の販売者へのリンク」は日本のアフィリでは真逆（単一ASPリンクのみ）が普通で、最も無視されている項目。

- **具体手順**:
  1. 上記の各項目をチェックボックスにしたテンプレをレビュー記事の下書きに埋め込む。
  2. 記事公開前に、各項目が本文のどこで満たされているかを行番号で記入する（満たしていない項目は空欄のまま残す）。
  3. 空欄が3つ以上ある記事は公開しない、というルールを決める。
  4. 特に「quantitative measurements」「evidence（画像・音声）」「competitors との差」は必須項目に格上げする。
  5. ランキング記事には各項目の**独自コンテンツ量**を確保する（1位だけ厚い記事にしない）。
  6. 可能なら複数の申込経路を示す（公式サイト直＋比較サイト経由 等）。

- **日本での言及度**: `【未検証・推定】低`
  検証用クエリ: 「レビューアップデート 要件 一覧」「Google 高品質なレビュー 書き方 公式」。要約紹介はあるが、**逐条チェックリストとして編集フローに組み込む**実務は薄いと推定。

- **noe-match適用度**: **A**。テンプレ1枚で導入でき、効果の因果が明確。想定工数: 4時間。

- **婚活/結婚領域での具体化**:
  - 「quantitative measurements」の婚活版:「30日あたりの申込可能数」「お見合い成立率」「初回面談から初お見合いまでの日数」「1お見合いあたりの実費」
  - 「what sets it apart from competitors」の婚活版:「この社だけが◯◯（例: 面談を土日夜間に設定できる／担当が変わらない契約になっている）」
  - 「evidence」の婚活版: 契約書の該当条項の写真、会員検索画面のスクショ、支払明細
  - 「complementary products / best for certain circumstances」の婚活版:「相談所を使わずアプリで足りるケース」
  - タイトル案:「結婚相談所レビューで当サイトが必ず出す6つの数字——申込可能数・成立率・所要日数・実費・担当継続率・解約返金額」

- **リスク・反証**: このドキュメントは主に「product reviews」を想定しており、サービス（結婚相談所）への適用は類推。ただし2023年4月以降Googleは対象を product に限定しない方向に広げているため、実務上は適用してよい。`[知識ベース]`

---

## 7-20. Helpful Content 自己評価質問群と "Who / How / Why"

- **一言で**: Googleが公式に列挙している自己評価質問を**そのまま逐条で監査に使う**。特に "Who, How, and Why" の3問はサイト単位の設計に効く。

- **海外での出典**:
  - Google Search Central「Creating Helpful, Reliable, People-First Content」: https://developers.google.com/search/docs/fundamentals/creating-helpful-content `[検証済：ページ存在と主要設問を確認]`
  - Search Engine Land「What is helpful content, according to Google?」: https://searchengineland.com/what-is-helpful-content-google-387360 `[検証済]`
  - 自己評価チェックリスト整理: https://knowagency.com/website-content-quality-checklists/ `[検証済]`

- **仕組み／なぜ効くか**:
  ライブ検索で確認できた設問（趣旨・`[要原文確認]`）:
  - 「Does the content provide original information, reporting, research, or analysis?」`[検証済]`
  - 「Does the content provide a substantial, complete, or comprehensive description of the topic?」`[検証済]`
  - 「Does the content provide insightful analysis or interesting information that is beyond the obvious?」`[検証済]`
  - 「If the content draws on other sources, does it avoid simply copying or rewriting those sources, and instead provide substantial additional value and originality?」`[検証済]`
  - 「If someone researched the site producing the content, would they come away with an impression that it is well-trusted or widely recognized as an authority on its topic?」`[検証済]`
  - 「Is this content written or reviewed by an expert or enthusiast who demonstrably knows the topic well?」`[検証済]`
  - 「Does the content have any easily-verified factual errors?」`[検証済]`
  - 「Is this the sort of page you'd want to bookmark, share with a friend, or recommend?」`[検証済（趣旨）]`
  そして Google は「**ask someone who is not affiliated with your website for an honest assessment**」（サイトと無関係の第三者に正直な評価を頼め）と明記している `[検証済]`。日本語紹介ではこの一文がほぼ落ちる。
  **Who / How / Why**: 「誰が作ったか」「どうやって作ったか」「なぜ作ったか」。Why の正解は「まず人の役に立つため」であり、「検索から来てもらうため」が主目的なら people-first ではない、という判定基準。

- **具体手順**:
  1. 全設問をスプレッドシートの列にする。
  2. 主要記事50本を行にし、各セルを◯/×で埋める。
  3. ×が多い記事を「削除／統合／改稿」に振り分ける（7-24）。
  4. Who: 全記事に著者情報を（7-22）。
  5. How: 方法論ページを（7-17）。AI/自動生成を使った場合はその旨を書く。
  6. Why: サイト全体の Source Context を明文化（7-02）。
  7. 「第三者に評価を頼め」を実行する——婚活当事者1人に読んでもらいフィードバックを取る。

- **日本での言及度**: `【未検証・推定】中`
  検証用クエリ: 「ヘルプフルコンテンツ 自己評価 質問」「Who How Why Google コンテンツ」。設問リストの翻訳紹介は日本語にも複数ある（＝言及度は中）が、**逐条の監査シートとして運用する**実務と「第三者に頼め」の実行は薄いと推定。

- **noe-match適用度**: **B**。設問リスト自体は日本語でも入手可能なので差分は小さい。ただし監査シート化は未実施なら価値がある。想定工数: シート作成2時間＋50本監査 10時間。

- **婚活/結婚領域での具体化**:
  - 「Is this content written or reviewed by an expert or enthusiast who demonstrably knows the topic well?」に対する婚活版の答え:「運営者自身が2020〜2023年に結婚相談所2社・婚活アプリ4本を利用し、2024年に成婚した」——これを著者ページに書く。
  - 「beyond the obvious」の婚活版:「お見合い料が発生するタイミングが社ごとに違い、『申込時』か『成立時』かで3か月の総額が◯万円変わる」

- **リスク・反証**: Helpful Content System は2024年3月のコアアップデートでコアランキングシステムに統合され、独立した「HCU」としては存在しない `[知識ベース]`。設問はガイドとしては有効だが、これに全部◯を付けても順位は保証されない。

---

## 7-21. エディトリアル・スタンダード／訂正ポリシー／ファクトチェックページ

- **一言で**: 「編集方針」「訂正方針」「事実確認の手順」を独立ページとして公開する。英語圏の報道系・レビュー系メディアでは標準装備、日本の個人アフィリではほぼゼロ。

- **海外での出典**:
  - Google Helpful Content の "How" に対応（コンテンツがどう作られたかの説明）: https://developers.google.com/search/docs/fundamentals/creating-helpful-content `[検証済]`
  - Wirecutter / NYT の editorial standards 開示: https://www.nytimes.com/wirecutter/ `[知識ベース]`
  - RTINGS の透明性開示（機材の自費購入、生データ公開）: https://www.rtings.com/ `[検証済]`
  - Nieman Lab による HouseFresh 事例の報道（メディアの編集体制の劣化が争点になった経緯）: https://www.niemanlab.org/2024/02/google-promotes-sketchy-product-reviews-from-big-publishers-at-the-expense-of-small-indie-sites-a-small-indie-site-argues/ `[検証済]`

- **仕組み／なぜ効くか**:
  訂正ポリシーの本質は「**間違えることを前提にしている**」と宣言することで、逆説的に信頼を上げること。加えて実務上、訂正履歴を残すと (a) 更新日の正当性が担保され（7-23）、(b) 読者からの誤り指摘の窓口になり、(c) 事実誤りが見つかったときの被害を限定できる。 `[知識ベース]`

- **具体手順**:
  1. `/editorial-policy/`（編集方針）を作る。書く項目: 情報源の優先順位（一次ソース＞公式発表＞二次報道＞口コミ）、匿名口コミの扱い、提供品の扱い、AI利用の有無と範囲。
  2. `/corrections/`（訂正）を作る。訂正の一覧（日付・記事・何をどう直したか）を時系列で。
  3. 各記事末尾に「この記事の誤りを報告する」導線（フォーム or メール）。
  4. 訂正したら記事内にも訂正注記を残す（黙って直さない）。
  5. AI利用について明記する（使っていないなら「使っていない」と書く方が強い）。
  6. 数字を扱う記事には「出典と取得日」を必ず表記するルールを編集方針に書く。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「編集方針 ページ 個人ブログ」「訂正ポリシー アフィリエイト」「ファクトチェック方針」。新聞社・大手Webメディアには存在するが、**アフィリメディアの信頼シグナルとして推奨する日本語SEO記事**は見た記憶がない。

- **noe-match適用度**: **B**。実装は軽い（2ページ）が、単体での順位効果は間接的。7-17・7-22とセットで「運営体制3点セット」として一気に作るのが効率的。想定工数: 6〜8時間。

- **婚活/結婚領域での具体化**:
  - 編集方針の項目案:
    - 「料金は各社公式サイトの表示価格を基準とし、取得日を明記します。キャンペーン価格は本文の比較表に入れません」
    - 「口コミサイト・SNSの投稿は、投稿日とURLを明記した上で『検証していない情報』として扱い、結論の根拠にはしません」
    - 「無償提供・体験取材を受けた場合は記事冒頭に明記し、その記事の評価は総合ランキングに反映しません」
    - 「生成AIは下書きの構成案に使うことがありますが、数字・体験・結論はすべて人が確認しています」
  - 訂正ページのエントリ例:「2026-06-12 『結婚相談所50社料金調査』でA社の月会費を16,500円と記載していましたが、正しくは17,600円でした（2026-05-01時点の公式表示を再確認）。集計表と中央値を修正しました。」

- **リスク・反証**: 訂正を公開すると誤りの多さが可視化される。ただし訂正ゼロで数字を出し続けているサイトの方が実際には疑わしい。運用を続けられないなら作らない方がよい（放置された訂正ページは逆効果）。

---

## 7-22. 著者バイライン と "Who is behind this site"

- **一言で**: 記事に著者名・経歴・顔・連絡先を出し、独立した著者ページを持つ。Google の自己評価質問の "Who" と、サイト評判の判定に直結する。

- **海外での出典**:
  - Google Helpful Content: 「Does the content present information in a way that makes you want to trust it, such as clear sourcing, evidence of the expertise involved, background about the author or the site that publishes it, such as through links to an author page or a site's About page?」`[検証済（趣旨）／要原文確認]` https://developers.google.com/search/docs/fundamentals/creating-helpful-content
  - Google「Site reputation abuse」ポリシー（第三者コンテンツをホストの評価で押し上げる行為の禁止）: https://developers.google.com/search/blog/2024/11/site-reputation-abuse `[検証済：2024-11-19発効、定義文言を確認]`
  - Google Spam Policies: https://developers.google.com/search/docs/essentials/spam-policies `[検証済]`
  - Search Engine Journal による Google の反応（HouseFresh の告発に対する）: https://www.searchenginejournal.com/google-responds-to-evidence-of-reviews-algorithm-bias/508775/ `[検証済]`

- **仕組み／なぜ効くか**:
  Site reputation abuse ポリシーの定義は「the practice of publishing third-party pages on a site in an attempt to abuse search rankings by taking advantage of the host site's ranking signals」`[検証済：この文言をライブ検索で確認]`。かつ Google は「**no amount of first-party involvement alters the fundamental third-party nature of the content**」（第一者がどれだけ関与しても、第三者コンテンツの本質は変わらない）と明言している `[検証済]`。
  この裏返しとして、**個人運営で著者が明確なサイトは構造的に有利**になった。大手メディアの「無署名のアフィリ記事」「外注ライター記事」が減点される方向に環境が動いており、実名・実体験を出せる個人はここで勝てる。

- **具体手順**:
  1. `/author/〈name〉/` を作る。書く項目: 本名またはハンドル（一貫させる）、写真、この領域での実体験（年月・具体）、資格があれば資格、SNS、連絡先。
  2. 全記事に著者バイライン（名前＋一行の実績）を表示。
  3. 記事ごとに「この記事で著者が実際にやったこと」を1文入れる。
  4. 外部（SNS、noteなど）でも同じ名前・同じプロフィールを使い、実在性の裏を取れるようにする。
  5. About ページで「なぜこのサイトを作ったか」（Why）と「収益源」（7-02）を書く。
  6. 外注ライターを使う場合は、その人の名前でバイラインを出す（無署名にしない）。

- **日本での言及度**: `【未検証・推定】中`
  検証用クエリ: 「著者情報 E-E-A-T」「運営者情報 SEO」「サイト評判の不正使用」。運営者情報の重要性は日本語でも語られている（＝中）が、**site reputation abuse ポリシーが個人サイトに与える追い風**という角度での解説は薄いと推定。

- **noe-match適用度**: **A**。個人運営で実体験があるなら最大の武器。想定工数: 4〜6時間。

- **婚活/結婚領域での具体化**:
  - 著者ページの見出し案:「私が婚活に使った期間と金額の全記録」「利用した結婚相談所・アプリの一覧（利用時期つき）」「このサイトの収益源」「連絡先」
  - バイライン案:「〈名前〉｜結婚相談所2社・婚活アプリ4本を計3年8か月利用し2024年に成婚。支払総額◯◯万円。すべて自費。」
  - 記事内の1文:「この記事の料金は、私が2026年3月にA社と交わした契約書の実額に基づいています。」

- **リスク・反証**: 婚活領域は極めてプライベートで、実名・顔出しは配偶者や親族への影響がある。**実名でなくとも「一貫した固有のペルソナ＋検証可能な実績」で代替可能**（英語圏でもハンドル運営のレビューサイトは多い）。ただし匿名にするほど 7-20 の "well-trusted or widely recognized authority" は満たしにくくなるトレードオフがある。

---

## 7-23. コンテンツ・リフレッシュの型と "Significant Update" の定義

- **一言で**: 「更新日だけ書き換える」を排し、**何を書き換えると順位が戻るか**の優先順位を型にする。Googleは日付の扱いについて明示的な指針を持っている。

- **海外での出典**:
  - Google「Search results date guidelines」（日付表示の指針。実質的な更新がないのに日付を変えるべきでない旨）: https://developers.google.com/search/docs/appearance/publication-dates `[知識ベース：URL実在、今回開けず＝要原文確認]`
  - Google Core Updates ガイダンス: https://developers.google.com/search/updates/core-updates `[知識ベース]`
  - Google Helpful Content の "Does the content have any easily-verified factual errors?": https://developers.google.com/search/docs/fundamentals/creating-helpful-content `[検証済]`
  - Kevin Indig の content decay / refresh 論: https://www.kevin-indig.com/ `[知識ベース：今回検索予算切れで未確認]`

- **仕組み／なぜ効くか**:
  順位が落ちた記事に対して効く更新は順序がある `[知識ベース]`:
  1. **事実の誤り・古い数字の修正**（最優先。7-20の設問に直撃）
  2. **意図の再適合**（SERPのページタイプが変わっていないか＝7-09）
  3. **information gain の追加**（差分を足す＝7-05）
  4. 構造の再編（見出しを属性に＝7-03）
  5. 内部リンクの張り直し
  6. タイトル・ディスクリプション
  逆に効かないのは「文字数を増やす」「言い回しを変える」「更新日だけ変える」。Googleは日付について、**実質的な更新がある場合のみ日付を更新すべき**という趣旨の指針を出している。「significant update」の実務的な定義は「**その記事を読んで読者が取る行動が変わる程度の変更**」——数字が変わった、推奨が変わった、手順が変わった。誤字修正や言い換えは該当しない。

- **具体手順**:
  1. Search Console で「クリック数が前年同期比で30%以上落ちた記事」を抽出。
  2. 各記事について上記1〜6を上から順にチェック。
  3. 1（事実誤り）が見つかった記事を最優先で直す。
  4. 2（意図移動）が原因なら、リライトでなく作り直し or 撤退（7-09）。
  5. 更新した場合、**何を更新したかを記事内に明記**する（「2026年8月更新: A社の月会費改定に伴い比較表を更新」）。
  6. 実質的更新がない場合は更新日を触らない。

- **日本での言及度**: `【未検証・推定】中`
  検証用クエリ: 「リライト 優先順位 SEO」「更新日 SEO 変更」「コンテンツリフレッシュ」。「リライト」は日本語SEOの主要テーマ（＝中）だが、**「効く順序」と「日付を触ってよい条件」**の明文化は薄く、「更新日だけ変える」を推奨する記事すら日本語には存在すると推定。

- **noe-match適用度**: **A**。258本の運用フェーズでは最も費用対効果が高い作業。想定工数: 抽出とトリアージ 6時間、1本の実更新 2〜4時間。

- **婚活/結婚領域での具体化**:
  - 婚活領域で最も腐りやすい事実:「料金（改定が頻繁）」「加盟連盟と会員数」「キャンペーン」「アプリの機能・料金プラン」「法制度（婚姻届の様式、戸籍法改正、選択的夫婦別姓の議論状況）」
  - 更新注記の型:「【2026年8月更新】A社が2026年7月1日に月会費を16,000円→17,600円に改定したため、12か月総額と比較表の順位を更新しました。旧料金での記述はこちら（差分）」
  - 定点調査（7-16）を毎年更新することで、リフレッシュが自動的に「significant」になる構造を作れる。

- **リスク・反証**: 「順位が戻る」保証はない。コアアップデートによる下落は個別記事の修正では戻らないことが多く、サイト全体の評価の問題である場合がある（HouseFresh 事例がまさにそれ）。

---

## 7-24. コンテンツ・プルーニング／統合（Content Pruning / Consolidation）

- **一言で**: 弱い記事を消す・統合する。増やすのではなく減らすことで、サイト全体の平均品質とトピック重心を上げる。

- **海外での出典**:
  - Google Helpful Content の「removing unhelpful content」に関する記述: https://developers.google.com/search/docs/fundamentals/creating-helpful-content `[知識ベース：Googleは「不要なコンテンツの削除」に言及している／要原文確認]`
  - Google Search Central の「site-wide signals」に関する説明（サイト内に有用でないコンテンツが多いと全体に影響しうる）: https://developers.google.com/search/updates/core-updates `[知識ベース]`
  - Ahrefs / Semrush の content pruning ガイド: https://ahrefs.com/blog/content-pruning/ `[知識ベース]`

- **仕組み／なぜ効くか**:
  Helpful Content の考え方では、サイト内の「役に立たないコンテンツ」がサイト全体の評価に影響しうるとされる。258本のうち、流入ゼロ・被リンクゼロ・CVゼロの記事が仮に80本あれば、それは資産ではなく負債。統合すると (a) 個別に弱かったページの情報が1つの強いページになり、(b) 内部リンクが集中し、(c) 7-07 の Know Simple 記事を親記事のH2に吸収できる。 `[知識ベース]`

- **具体手順**:
  1. 全記事について、直近12か月のクリック数／被リンク数／CV数の3列を作る。
  2. 3つとも下位の記事を抽出。
  3. 各記事を4分類: **改稿**（テーマは有効／中身が弱い）／**統合**（他記事のH2にできる）／**削除**（テーマ自体が不要）／**保持**（CVは無いが導線として必要）
  4. 統合先を決め、内容を移し、301リダイレクト。
  5. 削除は410（Gone）または301。**内部リンクを必ず張り替える**。
  6. 削除・統合の記録を残し、3か月後に効果を測る。

- **日本での言及度**: `【未検証・推定】中`
  検証用クエリ: 「記事 削除 SEO 効果」「コンテンツプルーニング」「リライト 統合 301」。日本語でも「低品質記事の削除」は語られる（＝中）が、**4分類のトリアージ手順**と「削除の判断基準を数値で決める」実務は薄いと推定。

- **noe-match適用度**: **B**。効果はあるが、収益機会を潰すリスクもあり、7-23（リフレッシュ）を先にやってからの方が安全。想定工数: 全記事棚卸し 10〜15時間＋実作業。

- **婚活/結婚領域での具体化**:
  - 統合候補の典型:「婚姻届 証人 誰でもいい？」「婚姻届 証人 いない」「婚姻届 証人 friends」→ 1本の「婚姻届の証人の決め方」に統合し、それぞれをH2に。
  - 削除候補:「◯◯（サービス終了した婚活アプリ）の使い方」
  - 保持候補: CVゼロだが被リンクがある調査記事。

- **リスク・反証**: 削除は不可逆。まずnoindexで様子を見るか、統合（301）を優先すること。また「流入ゼロ」の中に、まだインデックスされて間もない記事や、AI Overviews に吸われているだけの良記事が混ざる。

---

## 7-25. グロッサリー／定義ページの資産化（Glossary / "What is X" Pages）

- **一言で**: 領域の用語を1語1ページで定義する用語集を作り、全記事から用語の初出時にリンクする。地味だが被リンクと内部リンクのハブになる。

- **海外での出典**:
  - Grow and Convert / Animalz 系のB2B SaaS戦略で glossary は定番の内部リンク資産: https://www.animalz.co/blog/ `[知識ベース]`
  - Google の「beyond the obvious」要求（定義だけのページは差分がない）: https://developers.google.com/search/docs/fundamentals/creating-helpful-content `[検証済]`
  - Ahrefs の SEO glossary 運用例: https://ahrefs.com/seo/glossary `[知識ベース]`

- **仕組み／なぜ効くか**:
  用語集は (a)「◯◯とは」クエリ（Know / Know Simple）を面で押さえ、(b) 全記事から自然に内部リンクできるハブになり、(c) 他サイトが用語説明の代わりにリンクしてくれる（被リンク獲得）。ただし**定義だけのページは information gain がゼロ**なので、必ず「その用語が実務でどう効くか」を足すこと。 `[知識ベース]`

- **具体手順**:
  1. 領域の専門用語を50〜150語リストアップ。
  2. 各語について「定義」「なぜこの語が重要か」「実務での落とし穴」「関連する自サイト記事へのリンク」の4ブロックで書く。
  3. 定義は1文で、ページ冒頭に置く（引用されやすくする）。
  4. 「落とし穴」に一次情報を入れる（ここが差分）。
  5. 全記事の初出時に用語集へリンク。
  6. 用語集の親ページ（索引）を作り、五十音／カテゴリで引けるようにする。

- **日本での言及度**: `【未検証・推定】低`
  検証用クエリ: 「用語集 SEO 効果」「グロッサリー 内部リンク」。「◯◯とは」記事は日本にも多いが、**用語集として体系化し全記事からリンクする資産設計**は薄いと推定。

- **noe-match適用度**: **B**。効果はストック型で遅効性。ただし婚活領域は業界用語が多く、しかも**業界用語の定義が社ごとに違う**（＝差分を作りやすい）。想定工数: 50語で 25〜40時間。

- **婚活/結婚領域での具体化**:
  - 用語候補:「お見合い料」「仮交際／真剣交際」「成婚退会」「プレ交際」「連盟」「IBJ」「BIU」「日本結婚相談所連盟」「見合い申込」「AI マッチング」「ハンドメイド紹介」「休会制度」「活動休止」「独身証明書」「収入証明」「両家顔合わせ」「結納」「入籍」「婚姻届」「証人」「戸籍謄本」「新姓」「マイナンバー 氏名変更」
  - 「落とし穴」ブロックの例（「仮交際」）:「仮交際の期間上限は連盟ごとに規定が異なり、IBJでは原則◯か月。上限を過ぎると自動的に終了扱いになる社があるため、契約前に規約の該当条項を確認すること。」
  - タイトル案:「婚活用語集——相談所によって意味が変わる23語を規約の原文つきで整理した」

- **リスク・反証**: 用語集は「薄いページの束」になりやすく、7-27 の scaled content abuse と紙一重。1語1ページにするなら各ページに実質的内容が要る。分量が確保できないなら1ページにまとめる方が安全。

---

## 7-26. カリキュレーター／インタラクティブ・ツール

- **一言で**: 計算ツール・診断・シミュレーターを自作して公開する。記事では取れない被リンクと再訪を取る。

- **海外での出典**:
  - Google Helpful Content の "original information" 要求（ツールは原理的にオリジナル）: https://developers.google.com/search/docs/fundamentals/creating-helpful-content `[検証済]`
  - "linkable asset" としての calculator の位置づけ（Ahrefs / Backlinko 系のリンクビルディング論）: https://ahrefs.com/blog/link-bait/ `[知識ベース]`
  - Google の Reviews 要求「Share quantitative measurements」との整合: https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews `[検証済]`

- **仕組み／なぜ効くか**:
  計算ツールは (a) 記事と違って**代替が効かない**（同じ計算をするページが複数あっても、使いやすい1つに集約される）、(b) 被リンクされやすい、(c) ブックマークされ再訪を生む（7-20 の "bookmark" 設問に直接答える）、(d) 入力データが自分のリサーチ資産になる。 `[知識ベース]`

- **具体手順**:
  1. 読者が実際に紙とペンで計算していることを見つける。
  2. 入力項目を3つ以下に絞る（多いと使われない）。
  3. 出力に「他の人と比べてどうか」を必ず入れる（比較があると共有される）。
  4. 計算式と出典を同一ページに明記する（ブラックボックスにしない）。
  5. 結果をURLで共有できるようにする（クエリパラメータ、ただしnoindex or canonical管理）。
  6. 関連記事から全部リンクする。

- **日本での言及度**: `【未検証・推定】低`
  検証用クエリ: 「計算ツール SEO 被リンク」「シミュレーター コンテンツ 効果」。金融・保険領域では日本にもシミュレーターがあるが、**個人メディアのコンテンツ戦略としてのツール自作**はほぼ語られていないと推定。

- **noe-match適用度**: **A**。婚活・結婚領域は「お金の計算が複雑で、しかもどこにも一覧がない」典型領域。想定工数: 1ツール 20〜40時間（実装込み）。静的HTML+JSで完結するものを選べば運用コストはゼロ。

- **婚活/結婚領域での具体化**:
  - ツール案1:「結婚相談所の総額シミュレーター」——入力: 活動予定月数／お見合い予定回数／候補社。出力: 各社の総額と内訳、最安社。式の根拠として各社公式料金表の取得日を明記。
  - ツール案2:「婚活の年間費用計算機」——相談所／アプリ/パーティー/交通費/被服費を合算。
  - ツール案3:「結婚式の費用分担シミュレーター」——両家負担・ご祝儀・自己負担の3分割計算。
  - ツール案4:「入籍後の手続きチェックリスト生成」——入力: 姓が変わるか／引っ越すか／勤務形態。出力: やること一覧と期限。
  - タイトル案:「結婚相談所の総額シミュレーター——12社の料金表から、あなたの活動計画での実額を計算します」

- **リスク・反証**: 料金データのメンテナンスが必要で、放置すると誤った数字を配り続ける（7-21の訂正ポリシー案件）。**データの取得日を必ず表示**し、更新できないなら公開しない。またJSツールはクロール・インデックスされにくいので、ページ内に説明テキストと計算式を必ずHTMLで持たせること。

---

## 7-27. プログラマティックFAQ生成の罠（Scaled Content Abuse）

- **一言で**: 「よくある質問」を自動/AI生成で量産すると、Google の scaled content abuse ポリシーに触れる。**回避すべき手法として**リスト化する。

- **海外での出典**:
  - Google Spam Policies「Scaled content abuse」: https://developers.google.com/search/docs/essentials/spam-policies `[検証済：ページ存在を確認／文言は要原文確認]`
  - Google「Updating our site reputation abuse policy」（2024-11-19）: https://developers.google.com/search/blog/2024/11/site-reputation-abuse `[検証済]`
  - Google Search Central「FAQ rich results の表示縮小」（2023年8月にFAQリッチリザルトを政府・医療系サイト中心に限定した変更）: https://developers.google.com/search/blog/2023/08/howto-faq-changes `[知識ベース：URL・時期とも要確認]`
  - Google Helpful Content の "avoid simply copying or rewriting those sources": https://developers.google.com/search/docs/fundamentals/creating-helpful-content `[検証済]`

- **仕組み／なぜ効くか（＝なぜ罠か）**:
  Google の scaled content abuse の定義は「many pages are generated for the primary purpose of manipulating search rankings and not helping users... creating large amounts of unoriginal content that provides little to no value to users, **no matter how it's created**」`[知識ベース・要原文確認]`。最後の「どう作られたかに関わらず」が重要で、**人力かAIかは問われない**。
  さらに 2023年8月に FAQ リッチリザルトの表示が大幅に縮小されたため、**FAQ を大量に付ける実務的インセンティブ（リッチリザルト獲得）自体が消滅している**。日本語圏では今もFAQスキーマ推奨が残っており、ここは明確なズレ。

- **具体手順（回避のための）**:
  1. FAQ を「リッチリザルト目当て」で付けているなら全部外す。
  2. 残すFAQは「実際に読者から来た質問」または「掲示板・知恵袋で実在が確認できた質問」のみ。
  3. FAQ の回答に**本文に無い情報**を入れる（本文の要約なら不要）。
  4. テンプレートから機械生成した Q&A は作らない。
  5. 「〈地域〉の〈サービス〉のよくある質問」のような掛け算生成は特に危険。やるなら地域固有の実データが必須。
  6. AI を使った場合、7-21 の編集方針でその範囲を明示する。

- **日本での言及度**: `【未検証・推定】低`
  検証用クエリ: 「FAQスキーマ 廃止」「よくある質問 SEO 効果 なくなった」「scaled content abuse 日本語」。FAQリッチリザルト縮小は日本語でもニュースにはなったが、**「だからFAQを量産する理由が消えた」**という実務結論まで踏み込んだ記事は薄く、今もFAQ追加を推奨する日本語記事が多数残っていると推定。

- **noe-match適用度**: **A（回避策として）**。既存258本にテンプレFAQが入っているなら、監査して外すだけで負債が減る。想定工数: 監査 4〜6時間。

- **婚活/結婚領域での具体化**:
  - 外すべきFAQ例:「Q. 結婚相談所は本当に結婚できますか？ A. 多くの方が成婚されています。」（無情報）
  - 残すべきFAQ例:「Q. 休会中も月会費はかかりますか？ A. 社によって異なります。A社は休会中も3,300円/月、B社は0円、C社は休会制度自体がありません（2026年8月時点の各社規約より）。」
  - タイトル案:「結婚相談所の『よくある質問』に公式が書かない答えを付けた——休会費・返金・担当変更の実際」
  - 特に「地域 × サービス」の掛け算ページは、実際に問い合わせた記録がない限り作らない。

- **リスク・反証**: FAQスキーマ自体はまだ有効なマークアップであり、政府・医療系では表示される。全面否定ではなく「リッチリザルト目的の量産をやめる」が正しい結論。

---

## 7-28. アフィリサイト壊滅事例の逆算分析（HouseFresh / Retro Dodo 型）

- **一言で**: 2023〜2024年に大量の独立系レビューサイトが検索流入を失った事例を、**何を持っていた／持っていなかったか**の観点で分解し、自サイトの生存条件に翻訳する。

- **海外での出典**:
  - HouseFresh「How Google is killing independent sites like ours」（2024年2月）: https://housefresh.com/david-vs-digital-goliaths/ `[検証済：記事タイトル・主張・対象クエリ「best air purifier for pets」・名指しされた上位サイト（Better Homes & Gardens, Real Simple, BuzzFeed, Popular Science）を確認]`
  - Nieman Lab による報道: https://www.niemanlab.org/2024/02/google-promotes-sketchy-product-reviews-from-big-publishers-at-the-expense-of-small-indie-sites-a-small-indie-site-argues/ `[検証済]`
  - Search Engine Journal「Google Responds To Evidence Of Reviews Algorithm Bias」: https://www.searchenginejournal.com/google-responds-to-evidence-of-reviews-algorithm-bias/508775/ `[検証済]`
  - MetaFilter スレッド（読者側の反応）: https://www.metafilter.com/202609/How-Google-is-killing-independent-sites-like-ours `[検証済]`
  - Retro Dodo の同種の告発（レトロゲームメディア）: https://retrododo.com/ `[知識ベース：今回未確認]`
  - Detailed.com（Glen Allsopp）による大手パブリッシャーの検索支配の分析: https://detailed.com/ `[知識ベース：EGRESS_BLOCKEDで未確認]`

- **仕組み／なぜ効くか**:
  HouseFresh の告発の骨子 `[検証済]`:
  - 対象クエリ「best air purifier for pets」の上位を大手メディアが占拠。
  - それらは**実際にテストしていない**「best of」リストで、アフィリエイト報酬に基づいて推奨している疑い。
  - 例として、**倒産・集団訴訟・第三者テストで低評価**という状態の Molekule Air Mini+ を多数のメディアが推していた。
  - 大手の一部（BuzzFeed, Huffington Post 等）は同一親会社の傘下で、**プライベート・エクイティが老舗メディアを買収し、記者を削減してアフィリエイト事業に転換**している構造がある。
  逆算すると、生き残った／勝てる条件は: ①実測データを持っていること ②方法論を公開していること ③著者が特定できること ④ブランド検索が存在すること ⑤検索以外の流入路（ニュースレター、コミュニティ、YouTube）を持っていること。HouseFresh 自身は①②を持っていたのに落ちたので、**①②だけでは足りない**というのが最も重い教訓。

- **具体手順**:
  1. 自サイトの記事を「実測あり／なし」で分類する。なしが過半なら構造的に危険。
  2. 上記5条件を自サイトで◯×評価する。
  3. ×の条件のうち、最も安く埋まるものから埋める（通常は②方法論ページ＝7-17、③著者＝7-22）。
  4. ⑤の検索外流入を必ず1本作る（メール or SNS or コミュニティ）。
  5. 大手が占拠しているクエリは正面から狙わず、7-13 の for Y 粒度と 7-14 の alternatives へ逃がす。
  6. 定期的に自領域のSERPを観測し、大手比率が上がっているクエリを撤退候補にする（7-09）。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「HouseFresh 日本語」「独立系サイト Google 壊滅」「レビューサイト 大手 独占」。この告発は英語圏では大きなニュースになり Google が公式に反応したが、**日本語で構造分析として紹介された記事はほぼ見た記憶がない**。差分の大きい候補。

- **noe-match適用度**: **B**。直接の施策ではなく、施策の優先順位を決めるための分析。ただし「実測すれば勝てる」という素朴な前提を修正する意味で重要。想定工数: 自己診断 3時間。

- **婚活/結婚領域での具体化**:
  - 日本の婚活領域の対応構造:「結婚相談所 おすすめ」の上位は、大手比較メディア（運営会社が広告代理店・人材系）と、相談所連盟自体が運営するメディアが占める。これらは**利益相反で「入会しない方がいい」を書けない**。
  - 検証記事の案:「『結婚相談所おすすめ』上位20記事のうち、実際に入会した記録があるのは何本か——全記事の記述を分類した」（メタ分析型。HouseFresh と同型の記事）
  - タイトル案:「『結婚相談所ランキング』を作っている会社を全部調べた——運営元・提携先・報酬構造の一覧」

- **リスク・反証**: 他社批判型の記事は法的リスク（名誉毀損・信用毀損）と、業界からの反発を招く。HouseFresh は結果的に流入を回復していない可能性がある（＝この告発は戦術としては成功していない）。実行するなら事実の記述に徹し、意見と事実を明確に分離すること。また日本では大手メディアの構造が英語圏とは異なるため、単純な当てはめは誤り。

---

## 7-29. 小サイトが大手に勝つ実例の逆算（Detailed.com / r/juststart 型）

- **一言で**: 個別の成功事例を「何が効いたか」で分解して型を抽出する。英語圏には事例の一次記録（掲示板の連投スレッド、公開監査）が大量にあるが、日本語圏には同等の記録がほぼ無い。

- **海外での出典**:
  - Detailed.com（Glen Allsopp）— 大手パブリッシャーのSEO支配とニッチサイトの実態の定量分析: https://detailed.com/ `[知識ベース：EGRESS_BLOCKEDで未確認]`
  - Reddit r/juststart — 個人サイト運営者の月次収益・施策の公開ログ: https://www.reddit.com/r/juststart/ `[知識ベース]`
  - Ahrefs のケーススタディ群: https://ahrefs.com/blog/category/case-studies/ `[知識ベース]`
  - Nieman Lab の HouseFresh 報道（小サイト側の視点の一次記録として）: https://www.niemanlab.org/2024/02/google-promotes-sketchy-product-reviews-from-big-publishers-at-the-expense-of-small-indie-sites-a-small-indie-site-argues/ `[検証済]`

- **仕組み／なぜ効くか**:
  英語圏では「income report」「site audit」を公開する文化があり、**施策と結果の対応関係を第三者が検証できる**。日本語圏の「月◯万円達成しました」は結果だけで施策が非公開のことが多く、学習材料にならない。r/juststart 型のログを読む価値は、成功例より**失敗例と、成功例の「実際にかかった期間」**にある（多くが18〜36か月）。 `[知識ベース]`

- **具体手順**:
  1. 自領域に近い英語圏サイトを5つ特定する（婚活は英語圏だとdating/relationship領域）。
  2. 各サイトについて、初期20記事のタイプを調べる（BOFUか情報系か）。
  3. 各サイトの独自装備を調べる（ツール、調査、方法論ページ、著者）。
  4. 共通項を抽出する。
  5. 日本語圏で同じ装備を持つサイトが自領域にいるかを確認する。いなければそれが空白。
  6. 装備を1つずつ導入し、導入日と順位変化を記録する（自分の income report を内部的に作る）。

- **日本での言及度**: `【未検証・推定】ほぼ無`
  検証用クエリ: 「Detailed.com 日本語」「r/juststart 日本語」「海外 アフィリ 事例 分析」。英語圏の一次記録を日本語で分析した記事はほぼ無いと推定。

- **noe-match適用度**: **B**。学習コストが高く、直接の施策ではない。ただし「日本語SEO情報にない型」を探す目的そのものなので、依頼主の意図には最も合致する。想定工数: 継続的（週2時間程度）。

- **婚活/結婚領域での具体化**:
  - 英語圏の参照候補: 婚活領域そのものは英語圏では検索市場が小さいが、「wedding planning」「wedding budget」領域には実測型メディアがある。
  - 移植候補:「結婚式費用の実額データベース」（英語圏の wedding cost report の日本版）
  - タイトル案:「結婚式の実費を100組から集めた——地域別・人数別の実額分布（2026年版）」（＝7-16 のフライホイールと接続）

- **リスク・反証**: 英語圏の成功例は英語のSERP環境・被リンク文化・アフィリ報酬体系に依存しており、そのまま日本に移植できない。特に日本は「ASPの単価構造」「比較メディアの運営主体」が違う。

---

## 7-30. Site Reputation Abuse を逆手に取る（大手の弱点の構造的利用）

- **一言で**: 2024年11月に強化された Google の site reputation abuse ポリシーが大手メディアの「アフィリ部門」を直撃する構造を理解し、そこで空いた枠を取りにいく。

- **海外での出典**:
  - Google「Updating our site reputation abuse policy」（2024-11-19発効）: https://developers.google.com/search/blog/2024/11/site-reputation-abuse `[検証済：発効日と定義文言を確認]`
  - Google Spam Policies: https://developers.google.com/search/docs/essentials/spam-policies `[検証済]`
  - Siteimprove による解説: https://www.siteimprove.com/blog/understand-googles-site-reputation-abuse-policy/ `[検証済]`
  - Digital Position「Google's Site Reputation Abuse Policy: What You Need to Know」: https://www.digitalposition.com/resources/blog/seo/googles-site-reputation-abuse-policy-what-you-need-to-know/ `[検証済]`
  - Medianama による報道: https://www.medianama.com/2024/11/223-googles-new-spam-policy-language-clamps-down-on-site-reputation-abuse/ `[検証済]`

- **仕組み／なぜ効くか**:
  ポリシー定義 `[検証済]`:「Site reputation abuse is the practice of publishing third-party pages on a site in an attempt to abuse search rankings by taking advantage of the host site's ranking signals.」
  重要な追加解釈 `[検証済]`:「no amount of first-party involvement alters the fundamental third-party nature of the content or the unfair, exploitative nature of attempting to take advantage of the host site's ranking signals」——**第一者がどれだけ監督しても、第三者コンテンツの本質は変わらない**。
  ただし「Having third-party content alone isn't a violation... it's only a violation if the third-party content is published on a host site mainly because of that host site's already-established ranking signals」`[検証済]`。
  日本での該当例: 新聞社・テレビ局・大手ポータルの「PR/比較コーナー」「◯◯ラボ」など、本体の権威を借りたアフィリコーナー。婚活領域にもこの型は多い。これらが減点されると、その枠が空く。

- **具体手順**:
  1. 自領域の主要クエリ上位を調べ、大手ドメイン配下の「別ディレクトリのアフィリコーナー」を特定する。
  2. そのコーナーの記事に (a) 著者名があるか (b) 実測があるか (c) 本体メディアのテーマと関連しているか を評価。
  3. 3つとも×なら、そのURLは site reputation abuse の候補。
  4. そのクエリを自分の重点候補にする（枠が空く可能性がある）。
  5. 同時に、**自分が逆側に立たない**ようにする——外注記事を無署名で出す、他人のサブディレクトリを貸す、等をしない。
  6. 経過を記録する（実際に落ちるかは分からないため、賭けずに監視する）。

- **日本での言及度**: `【未検証・推定】低`
  検証用クエリ: 「サイトの評判の不正使用」「パラサイトSEO 対策」「site reputation abuse 日本」。ポリシー自体はニュースとして日本語でも流通した（＝低〜中）が、**個人サイト側の機会として読み替える分析**は薄いと推定。

- **noe-match適用度**: **B**。攻めの施策ではなく機会観測。ただし「大手が落ちる可能性のあるクエリ」を先に押さえる判断材料になる。想定工数: 領域スキャン 4時間＋月1時間の監視。

- **婚活/結婚領域での具体化**:
  - 観測対象例: 大手ポータル・メディア配下の婚活比較コーナー、人材系企業が運営する婚活メディア、保険・金融メディアの「結婚」カテゴリ。
  - 記事案:「『結婚相談所おすすめ』を出しているドメインの内訳——本体メディアと運営会社の関係を全部調べた」（7-28と接続）
  - 自衛:「当サイトの記事はすべて運営者本人が執筆しています。外部への記事枠の貸出は行いません」を編集方針（7-21）に明記。

- **リスク・反証**: Google が実際にどのサイトに適用しているかは非公開で、「落ちるはず」の予測に賭けると外れる。またこのポリシーは主にホスト側への処分であり、そのクエリの枠が個人サイトに回ってくる保証はない（AI Overviews に吸われる可能性の方が高い）。

---

## 領域7の未解決事項

### A. 本調査の欠損（最優先で埋めるべき）

1. **日本語での言及度が一切実検証されていない。** 全30項目の「日本での言及度」は推定であり、検証用クエリだけを記載した。依頼主側で以下を実検索して上書きする必要がある。特に「ほぼ無」と推定した11項目（7-01, 7-02, 7-03, 7-04, 7-06, 7-10, 7-12, 7-14, 7-17, 7-18, 7-21, 7-28, 7-29）は、実際には日本語記事が存在する可能性がある。
2. **Google公式ドキュメントの原文照合ができていない。** `developers.google.com` が EGRESS_BLOCKED のため、引用文言はライブ検索のスニペット経由と学習知識に依存している。`[要原文確認]` を付した引用は、以下のURLを直接開いて一字一句を確認すること。
   - https://developers.google.com/search/docs/fundamentals/creating-helpful-content
   - https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews
   - https://developers.google.com/search/docs/essentials/spam-policies
   - https://developers.google.com/search/blog/2024/11/site-reputation-abuse
   - https://developers.google.com/search/docs/appearance/publication-dates
3. **Grow and Convert の Pain Point SEO 原典（7-10）が読めていない。** 5つのキーワードカテゴリの分類名と定義は学習知識ベース。この手法は本レポートで最も差分が大きい候補の1つなので、原典の確認は必須。 https://www.growandconvert.com/content-marketing/pain-point-seo/
4. **Detailed.com（Glen Allsopp）の分析（7-29, 7-28）が全く読めていない。** 大手パブリッシャーの検索支配に関する定量データは彼のレポートが最も精度が高いが、今回は1ページも開けていない。
5. **Kevin Indig / Amanda Natividad / SparkToro の一次ソースに到達していない。** 7-16 の zero-click content、7-23 の content decay は検索予算切れで確認できなかった。
6. **Retro Dodo の告発記事（7-28）が未確認。** HouseFresh と同型の事例として言及したが、内容の確認はできていない。

### B. 手法そのものに残る論点

7. **Koray フレームワーク（7-01〜7-04）の再現性が検証されていない。** 本人と受講者以外による独立した成功事例・失敗事例の記録が乏しい。特に「Core を短期間に高密度で出す」は、Helpful Content 以降の環境では「大量公開」として逆に減点されるリスクがあり、この矛盾は未解決。
8. **7-10（BOFU優先）と 7-04（Core先行）と 7-16（Original Research先行）は、どれを最初にやるかで衝突する。** 258本を既に持つサイトでの正しい順序は本レポートでは決めきれていない。仮説としては「7-23リフレッシュ → 7-17/7-21/7-22の運営体制3点セット → 7-10 BOFU補完 → 7-16 調査」だが、根拠は弱い。
9. **AI Overviews / AI Mode 下で、これらの手法のうちどれが無効化されるか**が全く検証できていない。特に 7-07 の Know Simple、7-25 の用語集、7-26 の計算ツールは、AIが直接答えることで流入がゼロになる可能性が高い。2026年時点の日本語SERPでのAI Overviews表示率の実測が要る。
10. **婚活領域固有の法的制約**（景表法・ステマ規制、結婚相手紹介サービス業の特定商取引法上の扱い、個人情報保護）が、7-14（alternatives＝他社批判）と 7-18（実体験の証拠公開）にどこまで制約をかけるかを法務的に詰めていない。特に**結婚相手紹介サービスは特定商取引法の「特定継続的役務提供」に該当**するため、契約・解約に関する記述は正確性の要求水準が高い。ここは専門家確認が必要。
11. **「実測すれば勝てる」の反証（7-28）に対する答えが無い。** HouseFresh は実測も方法論公開も著者明示も持っていたが落ちた。個人サイトが実測で勝てる条件は「実測＋α」であり、その α が何かは本レポートでは特定できていない。候補は「検索外の流入路」「ブランド検索」「被リンク」だが、優先順位は不明。
12. **7-13（for Y の粒度分割）と 7-27（scaled content abuse）の境界線が定量的に引けていない。** 「推奨が変わるなら分ける」という定性基準しか示せていない。実務では何ページまでなら安全かの目安が要る。

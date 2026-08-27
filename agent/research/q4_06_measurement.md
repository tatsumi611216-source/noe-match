# 領域6: 計測・分析・実験設計

- 調査日: 2026-08-27
- 担当領域: SEO Analytics / Experimentation（計測・分析・実験設計）
- 参照ソース数: 121 URL（重複除外・実在確認済。うち WebSearch 14セッション経由で発見、直接 WebFetch で本文確認できたのは GitHub 上の4リポジトリのみ — 下記「事前開示」参照）
- 手法数: 23

## 本レポートの信頼度に関する事前開示（重要）

正直に書く。以下の2点は読む前に知っておいてほしい。

1. **egress制限**: 本セッションのネットワークポリシーにより `searchpilot.com` / `developers.google.com` / `support.google.com` / `searchengineland.com` / `arxiv.org` / `jcchouinard.com` など主要ドメインへの直接フェッチがブロックされた。実際に本文を取得して確認できたのは GitHub 上の4リポジトリのみ。それ以外は **検索エンジン経由で取得したタイトル・URL・抜粋** に基づく。URLは実在が確認できたものだけを載せているが、**引用した数値は原典で再確認すること**を推奨する。特に「70.6%」「250-500プロンプト」など具体数値には `【要再検証】` を付した。
2. **日本語言及度の検証範囲**: 「実検索で検証」できたのは **2クエリのみ**（`SEO A/Bテスト CausalImpact 因果推論 日本語` と `CUPED 分散削減 A/Bテスト 日本語 解説`）。この時点でセッション共有のWeb検索予算（200/200）が枯渇した。残りの手法の「日本での言及度」は、**打つ予定だった日本語クエリを明記した上で、英語圏の流通状況と日本語SEO業界の既知の情報分布からの推定**である。各項目に `[実検索済]` / `[推定]` を明記した。推定はあくまで仮説であり、実行前に自分で検索して確かめてほしい。

---

## noe-match のデータ規模に関する事前計算（全手法の判定根拠）

現状: 月間表示 278 / クリック 4（CTR 約1.4%）。ドメイン2026年6月開設。

以下は本レポート全体で「必要なデータ規模」を判定するために先に計算した閾値。**手法ごとの A/B/C 判定はすべてこの表を根拠にしている。**

### (a) クリック数ベースの検定（ポアソン近似）

分散安定化変換 √ を使った近似式: 必要な対照群期待イベント数 `m0 ≈ (1.4 / (√R − 1))²`（両側α=0.05, 検出力80%, 曝露量が両群同じ場合）

| 検出したい効果（クリック比 R） | 必要な対照群クリック数 m0 | noe-match現状での到達期間 |
|---|---|---|
| R = 2.0（倍増） | 約 11 クリック | 約 3ヶ月 |
| R = 1.5（+50%） | 約 39 クリック | 約 10ヶ月 |
| R = 1.2（+20%） | 約 215 クリック | 約 4.5年 |
| R = 1.1（+10%） | 約 823 クリック | 約 17年 |

**結論: noe-matchで統計的に検出できるのは「倍増レベル」の効果のみ。** +20%の改善は現在の規模では原理的に検出不可能。

### (b) 表示数ベースのCTR検定（2標本比率検定）

ベースラインCTR 1.5% → 1.8%（相対+20%）を検出する場合:

```
n = (1.96·√(2p̄(1−p̄)) + 0.84·√(p₁(1−p₁)+p₂(1−p₂)))² / (p₂−p₁)²
  = (0.35311 + 0.15161)² / (0.003)²
  ≈ 28,300 表示 / 群（合計 約56,600表示）
```

**noe-match現状（月278表示）では約17年分。** タイトルタグA/Bテストは現時点では純粋に無意味。相対+50%（1.5%→2.25%）でも約4,700表示/群 ≈ 合計9,400表示 ≈ 34ヶ月分。

### (c) n=4クリックで何が言えるか（ベイズ）

Jeffreys事前分布 Beta(0.5, 0.5) + 4クリック/278表示 → 事後分布 Beta(4.5, 274.5)

- 事後平均 CTR = 4.5/279 = **1.61%**
- 事後標準偏差 = √(0.0161×0.9839/280) = **0.75pp**
- 95%信用区間 ≈ **[0.5%, 3.3%]**

**言えること: 「このサイトのCTRは0.5%〜3.3%のどこかにある」。それ以上は何も言えない。** 上限と下限で6.6倍の開きがある。「先週CTR1.0%、今週2.0%だから改善した」は、n=4では純粋なノイズと区別できない。この事実を KPI 台帳の注記に入れるべき。

### (d) Share of Model のn数

引用率 p を ±10pp 精度（95%信頼）で推定するのに必要なプロンプト実行数:
`n = 1.96² × p(1−p) / 0.1²` → 最悪ケース p=0.5 で **n ≈ 96**。±5pp なら **n ≈ 384**。

---

## 6-01. SEOスプリットテスト（SEO A/B Test / SearchPilot型ページ分割テスト）

- **一言で**: ユーザーではなく **URLをランダムに2群に割り当て**、片方だけにテンプレート変更を適用し、時系列モデルで「変更しなかった場合の対照群予測値」との差分を因果効果として推定する手法。
- **海外での出典**:
  - https://www.searchpilot.com/resources/blog/what-is-seo-split-testing （[Updated 2026] What is SEO A/B testing? A guide to setting up, designing and running SEO split tests）
  - https://www.searchpilot.com/resources/blog/the-math-behind-searchpilot-how-seo-a/b-testing-actually-works （The Math Behind SearchPilot）
  - https://www.searchpilot.com/resources/blog/how-searchpilot-analyses-test-data
  - https://www.searchpilot.com/data-analysts （外れ値検出・クラスタリング・フィルタリングで対照群と変異群を統計的に等質化するアルゴリズムの説明）
- **仕組み／なぜ効くか**: 通常のCROのA/Bテストは「ユーザー」を分割するが、SEOでは検索エンジンのクローラーが見るのは1つのURLにつき1バージョンでなければならない（クローキング回避）。そこで **分割の単位をページにする**。同一テンプレートの数百〜数千ページがあれば、それを対照群/変異群にランダム割り当てし、群ごとのオーガニッククリック合計の時系列を比較する。対照群が「もし変更しなかったら」の反事実を提供するため、季節変動・アルゴリズム更新・全体トレンドが自動的にキャンセルされる。SearchPilotは結果を p値ではなく **credible interval（信用区間）** で報告し、Causal Impact より強い research-backed prior を使うと明言している。
- **具体手順**:
  1. 同一テンプレートの類似ページを50件以上集める（noe-matchなら記事ページ258件が候補）。
  2. 過去8〜12週の日次クリック時系列でページをクラスタリングし、トラフィック水準が似たペアを作る。ペアの片方ずつを対照/変異に振る（層化ランダム化）。
  3. 変異群にのみ変更を適用。適用日を明確に記録。
  4. 4〜8週後、`pandas` で群別日次クリックを集計。
  5. `tfcausalimpact`（`pip install tfcausalimpact`）で `CausalImpact(df[['variant','control']], pre_period, post_period)` を実行。`ci.summary()` の相対効果と95%信用区間を読む。
  6. 信用区間が0を跨いだら「効果なし」ではなく「この規模では検出不能」と記録する。
- **必要なデータ規模**: SearchPilot型が成立する最低ラインは、**各群が期間中に最低200〜500クリック**（上記(a)の計算より、R=1.2を検出するには群あたり215クリック必要）。実務的には **同一テンプレートのページが最低50件、群あたり月間1,000クリック以上** が推奨される。表示数ベースでCTR効果を見る場合は群あたり28,000表示。
- **日本での言及度**: **ほぼ無** `[推定]`。打つ予定だった日本語クエリ: `SEOスプリットテスト`, `SEO A/Bテスト ページ分割`, `SearchPilot 日本語`。日本語圏では「SEOのA/Bテスト」は Google Optimize 的なユーザー分割（=SEO効果は測れない）と混同されて語られることが圧倒的に多く、ページ分割型の因果推論設計が体系的に紹介されている日本語記事はほぼ見かけない。SearchPilot（旧 Distilled ODN）の名前自体が日本語圏でほぼ流通していない。
- **noe-match適用度**: **C**。理由: 258記事あるがテンプレートが均質でなく、かつ全サイト月間4クリックでは群あたりのクリック数が0〜2件になり、どんな統計手法でも情報が取り出せない。**再評価の閾値: 月間クリック2,000件（群あたり1,000件）に到達したら着手価値が出る。** 現状の278表示/4クリックから見て、最短でも1〜2年先。ただし **今のうちに「テンプレート群のラベリング」だけはやっておく価値がある**（記事メタに `template_group` を持たせる、工数2〜3時間）。将来テストする時に遡ってランダム化できる。
- **リスク・反証**: (1) ページ分割は「クローキング」ではないが、変異群と対照群の差が大きすぎるとGoogleに不自然と見なされるリスクがゼロではない。Googleは公式にサイトテスト自体は許容している（https://developers.google.com/search/blog/2012/08/website-testing-google-search ）。(2) 群間でリンク構造やクロール頻度が不均等だと交絡する。(3) **最大の反証: SearchPilotは1サイトあたり月間数百万セッション規模の顧客を前提にしている。** 個人規模での成立可能性については彼ら自身が語っていない。個人サイトで「有意でした」と出た場合、それはほぼ確実に偽陽性。

---

## 6-02. CausalImpact（ベイズ構造時系列による介入効果推定）

- **一言で**: 対照群がなくても、**相関する共変量系列**（別ページ群、別クエリ群、Google Trends等）から「介入がなかった場合の反事実」をベイズ構造時系列モデル（BSTS）で予測し、実測との差分を因果効果とする。
- **海外での出典**:
  - https://github.com/google/tfp-causalimpact （Google公式のPython実装。**直接確認済**: `pip install tfp-causalimpact` / `import causalimpact`。前提条件として「介入の影響を受けない対照時系列で結果を説明できること」「処置系列と対照系列の関係が介入後も安定していること」の2条件を明記）
  - https://github.com/WillianFuks/tfcausalimpact （**直接確認済**: `pip install tfcausalimpact`、`CausalImpact(data, pre_period, post_period)`、`model_args={'fit_method':'hmc'}` でHMC、デフォルトは変分推論で2〜3分）
  - https://www.jcchouinard.com/causalimpact-for-seo/ （SEO split-testing実験へのCausalImpact適用）
  - https://www.womenintechseo.com/knowledge/measure-the-impact-of-your-seo-changes-with-causal-impact/
  - Brodersen et al. (2015), Annals of Applied Statistics — 原論文
- **仕組み／なぜ効くか**: SEOでは「変更前後の比較」しかできないことが多いが、単純な前後比較は季節性・アルゴリズム更新・全体トレンドと交絡する。BSTSは事前期間で「目的系列 y と共変量 X の関係」を学習し、介入後は X から y の予測分布を出す。実測 y との差の累積が「増分」。**p値ではなく事後分布が出るので、「効果がプラスである確率85%」といった意思決定に直結する言い方ができる**のが小規模サイトで効く理由。
- **具体手順**:
  1. 週次（日次だとノイズ過多）のGSCデータで、目的系列 `y` = 施策対象ページ群のクリック、共変量 `X` = 施策対象外ページ群のクリック、を作る。`scripts/fetch_gsc.py` の出力を `pandas` で pivot。
  2. 事前期間は **最低でも介入後期間の3倍**（例: 介入後4週なら事前12週以上）。GSCは16ヶ月保持なので最大でも約70週。
  3. `pip install tfp-causalimpact` → `ci = causalimpact.fit_causalimpact(data, pre_period, post_period)`。
  4. `ci.summary()` の `Relative effect` と `Posterior tail-area probability p` を読む。
  5. **共変量が介入の影響を受けていないことを必ず確認**（内部リンクを張り替えた場合、対照ページ群も影響を受けるのでこの前提が崩れる）。
  6. プレースボテスト: 介入日を偽って過去の任意の日に設定して同じ分析を回し、「効果あり」が出ないことを確認する。これをやらない CausalImpact 分析は信用できない。
- **必要なデータ規模**: 週次系列で **事前期間12点以上、各点のクリック数が最低5〜10**（ポアソンノイズが信号を飲まないため）。つまり **週間クリック50〜100件（月間200〜400件）** が実用下限。それ未満だと信用区間が「−80%〜+300%」のように無意味に広がる。
- **日本での言及度**: **中（ただしSEO文脈では低）** `[実検索済]`。検索クエリ: `SEO A/Bテスト CausalImpact 因果推論 日本語`。結果として **CausalImpact 自体の日本語解説は豊富**（レバレジーズ データAIブログ、株式会社Crosstab、株式会社JADEのブログ、Qiita複数本、和から株式会社の講座）。特に JADE のブログ記事「素人でも1ヶ月 Causal Impact で遊んだら、統計的有意差が見えるようになった話」（https://blog.ja.dev/entry/blog/2024/09/04/causal-impact-beginners-guide ）は SEO 会社が書いた稀な例。**ただし「SEO施策の効果測定に日常的に使う運用手法として」紹介している日本語記事は極めて少なく、マーケ全般・広告効果測定の文脈が主。** ここが穴。
- **noe-match適用度**: **B**。理由: 現状の月4クリックでは信用区間が広すぎて使えないが、**「表示数（impressions）」を目的変数にすれば月278と桁が1つ大きくなり、成立の芽がある**。表示数ベースなら週間70表示程度で、粗い効果（±50%以上）の検出は可能。想定工数: Python環境が既にあるので **初回セットアップ4〜6時間、以降は1施策あたり30分**。プレースボテストの実装を含めて8時間見ておけば十分。
- **リスク・反証**: (1) 共変量が施策の影響を受けていると効果を過小評価する（最頻出の誤用）。(2) 事前期間にドメイン全体が急成長中だとBSTSのトレンド外挿が暴走する。**noe-matchは2026年6月開設で成長初期なので、これは実害のあるリスク。** 対策は共変量を必ず入れて「相対」で見ること。(3) 「有意でない」を「効果がない」と誤読する。検出力不足と効果ゼロは別物。

---

## 6-03. CUPED（事前実験データによる分散削減）

- **一言で**: 実験前の同じ指標を共変量として回帰的に差し引くことで、**サンプル数を増やさずに分散を減らし検出力を上げる**。Microsoft が2013年に提唱し、現在の実験プラットフォームの標準装備。
- **海外での出典**:
  - https://medium.com/@VectorWorksAcademy/cuped-a-practical-and-theoretical-guide-to-variance-reduction-in-online-experiments-b2a3e804c8fc
  - https://arxiv.org/pdf/2110.13406 （Towards Optimal Variance Reduction in Online Controlled Experiments）
  - https://arxiv.org/pdf/2401.04062 （Variance Reduction in Ratio Metrics for Efficient Online Experiments — CTRのような比率指標へのCUPED適用）
  - https://arxiv.org/pdf/2112.13299 （Zero to Hero: Exploiting Null Effects to Achieve Variance Reduction）
  - https://towardsai.net/p/l/variance-reduction-in-causal-inference
- **仕組み／なぜ効くか**: 調整後指標 `Y_cuped = Y − θ(X − E[X])`、`θ = Cov(Y,X)/Var(X)`。X は実験前期間の同一指標。分散削減率は **相関係数の2乗 ρ²** に等しい。SEOのページ単位実験ではページ間のトラフィック分散が桁違いに大きい（べき分布）ため、事前トラフィックとの相関 ρ は 0.8〜0.95 になることが多く、**分散を64〜90%削減できる = 必要サンプル数が1/3〜1/10になる**。これが小規模サイトにとって決定的に重要。
- **具体手順**:
  1. 実験対象ページ群について、実験前4〜8週の週平均クリック（または表示数）を `X` として記録。
  2. 実験期間の同指標を `Y` とする。
  3. `numpy` で `theta = np.cov(Y, X)[0,1] / np.var(X)`。
  4. `Y_cuped = Y - theta * (X - X.mean())` を計算。
  5. 通常のt検定/ブートストラップを `Y_cuped` に対して行う。`scipy.stats.ttest_ind` または `scipy.stats.bootstrap`。
  6. `np.corrcoef(Y, X)[0,1]**2` を報告し、実際に何%分散が減ったかを記録する。
- **必要なデータ規模**: CUPED自体は **単位（ページ）が30以上あれば θ の推定が安定する**。ただし CUPED は分散を減らすだけで **平均ゼロのデータから情報を生み出すわけではない**。上記(a)(b)の必要サンプル数を ρ² 分だけ緩和する道具。ρ=0.9 なら CTR実験の必要表示数 28,300 → **約5,400表示/群** まで下がる。それでもnoe-matchの月278表示では届かない。
- **日本での言及度**: **低〜中（データサイエンス文脈のみ）** `[実検索済]`。検索クエリ: `CUPED 分散削減 A/Bテスト 日本語 解説`。日本語記事は存在する（Qiita「A/BテストでCUPEDを使って分散を小さくする」https://qiita.com/tetsuro731/items/ac84ee32a8a001541631 、note「ABテストにおける分散削減手法①」https://note.com/dapper_bobcat204/n/nb2293ca4ccdb 、Speaker Deck「A/BテストにおけるVariance reduction」https://speakerdeck.com/shyaginuma/btesutoniokeruvariance-reduction 、Amplitude公式日本語ドキュメント）。**ただしすべてプロダクト開発・データサイエンス文脈で、SEO/コンテンツ計測への応用を書いた日本語記事は見つからなかった。** 「SEO × CUPED」は完全な空白。
- **noe-match適用度**: **C（現時点）／将来はA**。理由: 手法として最も「小規模サイト向き」だが、それでも土台となるサンプルサイズが足りない。**再評価の閾値: 月間表示数10,000（≒現在の36倍）。** 想定工数: 実装自体は `numpy` で20行、**2時間**。分散削減率のログを KPI台帳に組み込むのが本体。
- **リスク・反証**: (1) 実験前期間と実験期間で母集団が変わっている（新規記事の追加）と θ がバイアスを持つ。(2) ρ が低い（<0.3）場合、CUPEDはほぼ無効。適用前に必ず ρ を確認する。(3) CUPED は**ランダム化されている前提**の手法。観察データに使うと擬似相関を「調整済み」に見せかける危険がある。

---

## 6-04. 時系列対照群デザイン / Difference-in-Differences / スイッチバック

- **一言で**: ページ分割ができないほど小規模な場合に、**「施策を打ったクエリ群」と「打っていないクエリ群」の前後差の差（DiD）** を取る、あるいは **同一ページで期間をON/OFF交互に切り替える（スイッチバック）**。
- **海外での出典**:
  - https://www.searchpilot.com/data-analysts （SearchPilotが対照群の統計的等質化について述べている箇所）
  - https://www.jcchouinard.com/pycausalimpact/ （pyCausalImpactでの実装例）
  - https://developers.google.com/search/blog/2012/08/website-testing-google-search （Google公式: サイトテストと検索の関係。クローキング判定を避ける条件）
  - https://www.womenintechseo.com/knowledge/measure-the-impact-of-your-seo-changes-with-causal-impact/
- **仕組み／なぜ効くか**: DiDは「対照群も処置群も、施策がなければ同じトレンドを辿ったはず（parallel trends assumption）」を仮定して、両群の前後差の差を効果とする。SEOでは**クエリクラスタ単位**で処置/対照を切ることができる（例: 「婚活」系記事だけリライト、「産後ケア」系は据え置き）。スイッチバックは同一ユニット内で時間を分割するため、ページ間の異質性を完全に消せるが、**SEOではインデックス反映に数日〜数週かかるためキャリーオーバー効果が致命的**で、実務ではほぼ使えない。
- **具体手順**:
  1. 記事を意味クラスタ（6-11参照）で分割し、処置クラスタ/対照クラスタを決める。**クラスタ間で事前トレンドが平行であることをグラフで確認**（これが最重要かつ最も省略されがちな手順）。
  2. 処置クラスタのみに施策を適用、日付を記録。
  3. `pandas` で `週 × クラスタ × 指標` の long-format を作る。
  4. `statsmodels.formula.api.ols('clicks ~ treated * post', data=df).fit()` で交互作用項 `treated:post` の係数がDiD推定量。
  5. 標準誤差はクラスタ頑健にする（`.fit(cov_type='cluster', cov_kwds={'groups': df['cluster']})`）。小クラスタ数だとこれでも過小になるので `scipy.stats.bootstrap` でのブロックブートストラップを併用。
  6. プレースボ期間でのDiDを回して0が出ることを確認。
- **必要なデータ規模**: DiD は **処置群・対照群それぞれ週次で最低12点、各点のクリックが最低5件**。noe-match換算で **月間クリック200件以上**。表示数ベースなら **月間表示3,000件以上**。スイッチバックはSEOでは推奨しない（下記リスク）。
- **日本での言及度**: **低** `[推定]`。打つ予定だったクエリ: `SEO 差分の差分法`, `SEO DiD 効果測定`, `SEO スイッチバックテスト`。DiD自体は計量経済学・EBPM文脈で日本語資料が豊富だが、**SEOのクエリクラスタ単位でDiDを組む発想を書いた日本語記事は見当たらない見込み**。CausalImpactが日本語で普及した分、より単純で小規模向きのDiDが逆に語られていない、という逆転現象がありそう。
- **noe-match適用度**: **B**。理由: CausalImpactより仮定が少なく実装も軽い。表示数ベースなら現状規模でも「粗い効果（±50%以上）」の推定に手が届く。**PDCA凍結の考え方と相性が良い**——凍結期間を「事前期間」として明示的に使える。想定工数: **3〜4時間**（statsmodels + プロット）。
- **リスク・反証**: (1) parallel trends が成立しない場合、DiD推定量は完全にバイアスを持つ。特に成長初期のサイトでは新規記事の追加がトレンドを歪める。**対策: 分析対象を「施策前から存在していた記事」に限定する（コホート固定）。** (2) スイッチバックはインデックス反映遅延（数日〜数週）でキャリーオーバーが起き、SEOではほぼ確実に効果を希釈する。加えて頻繁なコンテンツ変更自体がランキングに影響する可能性がある。**個人サイトでのスイッチバックは非推奨。** (3) クラスタ数が2つだけだと標準誤差の推定が原理的に不可能（2クラスタDiDは推論できない）。最低6クラスタ以上に分けること。

---

## 6-05. Incrementality測定（ホールドアウト／地理的ホールドアウト／アフィリエイト増分）

- **一言で**: 「そのチャネル/施策がなかったら、そのコンバージョンは起きなかったのか」を実験的に検証する。ラストクリック帰属が過大評価する分を剥がす。
- **海外での出典**:
  - https://irev.com/blog/how-to-measure-incrementality-in-affiliate-marketing-holdout-tests-geo-tests-and-mmm-for-real-growth/
  - https://prismique.com/blog/a-practical-guide-to-incrementality-testing （アフィリエイト・パフォーマンスマーケでの実践ガイド）
  - https://commonthreadco.com/pages/incrementality （Geo Holdout Incrementality Testing）
  - https://supermetrics.com/blog/incrementality-testing
  - https://segmentstream.com/measurement-engine/incrementality
  - https://www.metricuno.com/incrementality-testing
  - https://lyxelandflamingo.com/blogs/full-funnel-marketing/incrementality-at-scale-designing-geo-experiments-for-enterprise-marketing/
- **仕組み／なぜ効くか**: incrementality = 「その施策が原因で起きた分だけ」。アフィリエイト業界での定番の発見は、**クーポン・キャッシュバック系パートナーの多くは需要を"創出"していない（capture であって create ではない）** というもの。出典 (irev / prismique) によれば、特定パートナー種別のコミッションを4〜6週間停止し、全体のコンバージョン率と売上が有意に変化しないなら、そのパートナーは既存需要を刈り取っていただけと推論する。地理的ホールドアウトは国/州/市/DMA/郵便番号で分割し、対照地域では通常配信、ホールドアウト地域では停止する。**クロスコンタミネーションもオーディエンス重複も起きない綺麗な境界**が作れるのが利点。
- **具体手順（noe-match=送客側での翻案）**:
  1. 記事内CTA（アフィリエイトリンク）を持つ記事を、コホートAとBに分ける。
  2. コホートBのみ4週間、CTAの位置/文言/数を意図的に「据え置き」にする（＝ホールドアウト）。
  3. コホートAには施策を打つ。
  4. 期間終了後、`クリック率（記事PV→アフィリンククリック）` と `記事あたりオーガニッククリック` の両方を比較。**後者を見るのが重要**（CTA増加がUXを損ねてSEOを下げていないかの検出）。
  5. 差分は 6-04 のDiDで推定。
- **必要なデータ規模**: incrementality測定は **コンバージョンイベントが対照群で最低30〜50件** ないと検出力が出ない（上記(a)の R=1.5 で m0=39 に対応）。noe-matchのアフィリエイト成果件数がまだ0〜数件なら **原理的に不可能**。ホールドアウトは 2〜4週が標準だが、出典（commonthreadco）は「ブランド効果を測るなら短期ホールドアウトは方法論として誤り、効果は数ヶ月かけて複利的に効く」と明言している。
- **日本での言及度**: **低** `[推定]`。打つ予定だったクエリ: `インクリメンタリティ 計測 アフィリエイト`, `ホールドアウトテスト 増分`, `ジオリフト テスト 日本語`。日本語では広告運用（特にMeta/Google広告）文脈で「インクリメンタリティ」が語られ始めているが、**アフィリエイト・メディア側が自分の施策の増分を測る文脈での日本語記事はほぼ皆無**と見込む。
- **noe-match適用度**: **C**。理由: 成果（コンバージョン）件数がホールドアウト設計の下限（対照群30件）に全く届かない。**再評価の閾値: 月間アフィリエイト成果30件。** ただし **「クリック（アフィリリンククリック）を代理指標にする」なら閾値が下がる**——月間アフィリリンククリック30件なら実施可能。想定工数: コホート管理の仕組みを記事メタに入れるのに **4時間**、分析は6-04と共通。
- **リスク・反証**: (1) 代理指標（リンククリック）と最終成果（成約）の相関が保証されない。クリックは増えたが成約は減る、はアフィリで頻繁に起きる。(2) ホールドアウト期間中の機会損失。noe-matchの規模では損失は小さいが、逆に言えば得られる情報も小さい。(3) **最大の反証: incrementality の議論は「複数チャネルを併用している広告主」の文脈で発達したもので、単一チャネル（オーガニック検索のみ）のメディアには構造的に当てはまりにくい。** noe-matchに本当に必要なのは incrementality ではなく単純な検出力の確保。

---

## 6-06. Page × Query マトリクスによるカニバリゼーション検出

- **一言で**: GSC APIの `page` と `query` の2次元を同時に取り、**1クエリに複数URLが表示されている状態**を機械的に検出して統合/差別化の判断材料にする。
- **海外での出典**:
  - https://github.com/allanreda/SEO-Keyword-Cannibalization-Detector （**直接確認済**: GSC APIから clicks/impressions/CTR/average position を取得し、pandas で「どのキーワードが複数のランキングURLを持つか」を評価。Google API Client Library + pandas + requests + BeautifulSoup + concurrent.futures/multiprocessing、Excel出力）
  - https://www.jcchouinard.com/seo-cannibalization-analysis-python-example-tutorial/
  - https://www.jcchouinard.com/keyword-cannibalization-tool-with-python/
  - https://practicaldatascience.co.uk/data-science/how-to-identify-keyword-cannibalisation-using-python
  - https://github.com/topics/keyword-canibalization （**直接確認済**: allanreda（Python）, zatkoma（R）, Robaie98（Python）の3リポジトリ）
- **仕組み／なぜ効くか**: Googleは基本的に1クエリ1サイト1〜2枠しか出さないため、同一クエリに自サイトの複数URLが割り当てられると、リンク評価とクリックが分散する。GSCの `query + page` 次元を取ると **「同一クエリで表示された各URL」がそのまま観測できる**——これは外部ツールでは絶対に見えない、GSCだけが持つ情報。判定の実用的な閾値として、出典（practicaldatascience）は **「そのキーワードの総クリックの10%以上が、2つ以上の異なるページに分散している」** キーワードを抽出する方法を挙げている。
- **具体手順**:
  1. `scripts/fetch_gsc.py` の `by_query_page` を使う（既に実装済み。ただし `rowLimit: 500` は将来的に25,000まで引き上げ、`startRow` でページネーションが必要）。
  2. `df.groupby('query')['page'].nunique()` で複数URL持ちクエリを抽出。
  3. 各クエリ内で `clicks` シェアを計算し、`2位のページのクリックシェア >= 10%` かつ `総表示数 >= 20` でフィルタ。
  4. さらに `position` の差を見る。両ページとも20位圏外なら「カニバリではなく単に弱い」。**片方が10位以内、もう片方が11〜30位のケースが最も是正価値が高い**。
  5. 是正: 弱い方から強い方へ内部リンク、または title/h1 の意図を明確に分離、または統合301。
  6. 是正後は 6-04 のDiDで効果を測る。
- **必要なデータ規模**: **クエリあたり表示数20件以上**が最低ライン（それ未満は表示のゆらぎと区別できない）。サイト全体では **月間表示200件以上** あればいくつかの候補は出る。**noe-matchの278表示/月でも、上位数クエリについては検出可能。** ただし該当クエリは1〜3件程度と予想。
- **日本での言及度**: **中（概念）／低（GSC APIによる機械検出）** `[推定]`。打つ予定だったクエリ: `キーワードカニバリゼーション 検出 Python`, `GSC API カニバリ 自動検出`。「カニバリゼーション」という言葉自体は日本語SEO記事で頻出だが、**「GSCのquery×page次元を取ってクリックシェア10%閾値で機械抽出する」という具体的な実装レシピを書いた日本語記事はほぼない**と見込む。日本語記事の大半は「タイトルが似ていないか目視で確認しましょう」レベル。
- **noe-match適用度**: **A**。理由: **既存の `scripts/fetch_gsc.py` がすでに `by_query_page` を取得している**ので、追加のAPI実装が不要。データ規模も現状で成立する（絶対数は少ないが偽陽性が出にくい方向の少なさ）。258記事あるサイトで婚活/産後ケア/育休など近接テーマが多いため、カニバリの実在確率が高い。想定工数: **2〜3時間**（pandas 30行 + 判定ロジック + 週次レポートへの組み込み）。
- **リスク・反証**: (1) GSCの `query + page` 集計では、**同一クエリの異なる検索セッションで別ページが出ただけ**（デバイス差・地域差・時間差）のケースが「カニバリ」に見える。真のカニバリは同一SERPに2つ出ること。GSCではこれを厳密に区別できない。(2) 意図的に複数ページで面を取る戦略（ロングテール網羅）を誤って潰す危険。(3) 統合301は不可逆。**表示数20件未満のクエリでは絶対に統合判断をしないこと。**

---

## 6-07. CTRカーブからの期待値差分（Expected CTR Gap / Opportunity Score）

- **一言で**: 「この順位ならCTRはこのくらいのはず」という基準カーブと実測CTRの差を取り、**順位を上げるべきページ**と**タイトル/説明文を直すべきページ**を分離する。
- **海外での出典**:
  - https://navboost.com/ctr-by-position/ （CTR by Google Search Position: 2026 Benchmarks from 5+ Studies。**10位以降でCTRは0.5%未満に崩壊する**と記載。また **20位のCTRが約1.47%で11位の1.0%より高い**という反直感的なアノマリーを報告 `【要再検証】`）
  - https://metricstab.com/docs/ctr-curve/
  - https://supermetrics.com/connect/google-search-console-to-claude （**opportunity score = impressions × (3位時の期待CTR − 現在のCTR)** という定式を明示）
  - https://www.intrepidonline.com/blog/seo/the-importance-of-striking-distance-keywords/
- **仕組み／なぜ効くか**: SEOの意思決定は本来2軸ある——「順位を上げる（コンテンツ/リンク）」と「同じ順位でクリックを増やす（タイトル/説明文/構造化データ）」。この2つは打ち手が全く違うのに、日本語のSEO運用では区別されずに語られる。CTRカーブとの乖離を計算すると、**「4位なのにCTR 2%（期待10%）→ タイトル問題」** と **「4位でCTR 11%（期待10%）→ 順位を上げる以外に伸びしろなし」** を機械的に分離できる。さらに `期待値差分 × 表示数` で優先順位が付く。
  - **決定的に重要な点: 汎用CTRカーブ（外部調査の平均値）ではなく、自サイトのGSCデータから自分のカーブを推定すべき。** 業種・クエリタイプ・SERP機能の有無でカーブは大きく違う。
- **具体手順**:
  1. GSCの `query + page` データを取り、`position` を1刻みでビニング。
  2. ビンごとに `sum(clicks)/sum(impressions)` を計算（行ごとのCTR平均ではない。これを間違えるとロングテールに引っ張られる）。
  3. 表示数の少ないビンは信頼できないので、**ビンあたり表示数200件未満は汎用カーブで代替**。汎用カーブは navboost.com の公開ベンチマークを使う。
  4. 各行について `expected_ctr = curve(position)`、`gap = ctr - expected_ctr`、`opportunity = impressions * max(0, -gap)`。
  5. `opportunity` 降順でソート → タイトル改善候補リスト。
  6. 別途 `impressions * (curve(3) - ctr)` を計算 → 順位改善候補リスト（6-08 と統合）。
- **必要なデータ規模**: **自前カーブの推定には各順位ビンで最低200表示、全体で最低5,000表示**が必要。noe-matchの278表示/月では **自前カーブは推定不可能 → 汎用カーブで代替する**。個別行の `gap` 判定には **行あたり表示数30件以上** が欲しい（表示30/クリック0でも「CTR 0% < 期待10%」は偶然で起こりうるため。表示30でCTR期待10%なら、クリック0の確率は 0.9^30 = 4.2%）。
- **日本での言及度**: **低** `[推定]`。打つ予定だったクエリ: `CTRカーブ 順位別 期待CTR 差分`, `期待CTR 実測CTR 乖離 SEO`。日本語では「順位別CTR一覧」の紹介記事はあるが、**「期待値との差分をopportunity scoreとして計算して優先順位を付ける」という運用手法として書かれたものは見かけない**と見込む。ここは明確な空白。
- **noe-match適用度**: **A**。理由: 汎用カーブを使えば現データ規模でも即実行可能で、**「次にどの記事のタイトルを直すか」という最も具体的な意思決定に直結する**。278表示のうち上位数クエリだけでも、期待CTRとの乖離が見えれば行動が決まる。想定工数: **2時間**（カーブ定数のハードコード + pandas 20行）。既存KPI台帳に列を1つ足すだけ。
- **リスク・反証**: (1) **GSCの `position` は表示数加重平均**（6-09参照）なので、「平均4位」のページは実際には1位と10位の混合かもしれない。この場合、期待CTRの計算が根本的に狂う。**対策: 単一クエリ×単一ページの行に限定して分析する。** (2) 汎用CTRカーブは英語圏の調査が大半で、日本語検索（特にモバイル、婚活のようなYMYL近接領域）に当てはまる保証がない。(3) AI Overviews が出るクエリではCTRカーブ自体が別物になる。(4) navboost の「20位のCTRが11位より高い」というアノマリーは、**ページ2の最下部に到達するユーザーは意図が強い**という選択バイアスの可能性が高く、そのまま行動指針にしてはいけない。

---

## 6-08. Striking Distance分析（11〜20位帯の狙い撃ち）

- **一言で**: 順位11〜20位（＝検索結果2ページ目）かつ表示数が多いクエリを抽出する。**1位分の順位上昇あたりのクリック増分が最大になる帯**を機械的に見つける。
- **海外での出典**:
  - https://www.clearscope.io/blog/what-are-striking-distance-keywords
  - https://support.seotesting.com/en/article/striking-distance-keywords-report-rnafa2/
  - https://seogets.com/features/striking-distance-report
  - https://www.seoforjournalism.com/p/what-are-striking-distance-keywords （WTF is SEO?）
  - https://llmfy.ai/blog/striking-distance-keywords （AI検索時代のstriking distance）
  - https://www.intrepidonline.com/blog/seo/the-importance-of-striking-distance-keywords/
- **仕組み／なぜ効くか**: CTRカーブは10位と11位の間で崖がある（10位以降で0.5%未満に崩壊）。11位のページを9位に上げると、CTRは約1%→約2.5%と2.5倍になる。一方1位のページを更に上げることはできず、30位を29位にしてもCTRはほぼ変わらない。**限界クリック増分が最大化される帯が11〜20位**。既にインデックスされ、被リンクと履歴を持っているページなので、新規記事を書くよりROIが高い。出典（digitalapplied）は **5〜20位帯** をROI最高としている。
- **具体手順**:
  1. GSCの `query + page` データを取得（期間28日以上）。
  2. `df[(df.position >= 8) & (df.position <= 25) & (df.impressions >= 10)]` でフィルタ。**noe-matchの規模では 11-20 に限定せず 8-25 に広げるべき**（position が加重平均でブレるため）。
  3. `potential_clicks = impressions * (ctr_curve(5) - ctr)` で優先度スコアを計算。
  4. 上位20行について、実際のURLとクエリを目視確認。**「そのページがそのクエリを本当に狙っているか」を確認する**（狙っていないなら別ページを作るべき、というシグナル）。
  5. 打ち手を分類: (a) 内部リンク追加 (b) 見出し/本文にクエリ意図を追加 (c) 6-06のカニバリ是正 (d) 何もしない（意図が合っていない）。
  6. 施策後4〜8週で position の変化を 6-16 の手順で検定する。
- **必要なデータ規模**: **クエリあたり表示数10件以上**（それ未満は position の推定誤差が大きすぎる）。サイト全体では **月間表示100件以上** で数件は抽出できる。**noe-matchの278表示/月で成立する数少ない手法。**
- **日本での言及度**: **低〜中** `[推定]`。打つ予定だったクエリ: `striking distance キーワード SEO`, `11位から20位 キーワード 狙う`。日本語では「あと一歩キーワード」「2ページ目キーワード」といった表現で断片的に語られるが、**"striking distance" という定着した英語の術語と、opportunity score による定量的な優先順位付けはセットで語られていない**と見込む。
- **noe-match適用度**: **A**。理由: 現データ規模で実行可能な数少ない手法。既存記事の改善に直結し、新規執筆より工数が小さい。**6-07 と同じスクリプトで実装できる。** 想定工数: **6-07と合わせて3時間**。
- **リスク・反証**: (1) 11〜20位にいる理由が「そのページが本来そのクエリ向けでない」場合、いくら改善しても上がらない。**打ち手を決める前に必ずSERPを目視で見ること。** (2) 表示数10件レベルのクエリの position は、実際には ±5位くらいの推定誤差がある。「12位だった」が実際は「7位と20位が混ざった平均」の可能性がある。(3) AI Overviews が出るクエリでは、11位→5位に上げてもクリックが増えない（AIOに吸われる）ケースがある。llmfy の記事はこの点を扱っている。

---

## 6-09. GSCデータの既知の罠の体系的理解（Anonymized queries / Position定義 / 16ヶ月 / サンプリング）

- **一言で**: GSCの数字が「何を数えているか」を正確に知らないと、上記すべての分析が土台から崩れる。**特に小規模サイトでは罠の影響が相対的に巨大になる。**
- **海外での出典**:
  - https://support.google.com/webmasters/answer/7042828?hl=en （Google公式: What are impressions, position, and clicks?）
  - https://seotesting.com/google-search-console/average-position/
  - https://www.incremys.com/en/resources/blog/google-search-console-position
  - https://nikki-pilkington.com/why-your-average-position-in-google-search-console-is-absolute-rubbish/
  - https://theoceanmarketing.com/blog/why-google-search-console-average-position-isnt-always-reliable/
  - https://www.ritnerdigital.com/blog/my-impressions-dropped-but-my-average-position-went-up-in-google-search-console-what-does-that-mean
  - https://getdadseo.com/blog/export-google-search-console-data-csv-api （Export GSC Data Without Losing Half of It）
- **仕組み／罠のリスト**:
  1. **平均順位は表示数加重平均であり、かつ「そのページの最高順位」で計算される**。同一SERPに2つ出た場合、上位の方だけがカウントされる。→ カニバリの影響が順位に現れない。
  2. **平均順位はクエリを跨いで平均される**。「対策キーワードで1位」でもロングテールで50位が多ければ平均は悪化する。→ **ページ単位の平均順位を KPI にしてはいけない。** query×page 単位で見ること。
  3. **デバイス・地域で順位が違い、表示数の多い方に引っ張られる**。出典（seotesting）の例: PCで4位・モバイルで12位、モバイルが表示の70%なら平均は12位寄りになる。
  4. **Anonymized queries（匿名化クエリ）**: 検索者を特定しうるとGoogleが判断した稀少クエリはクエリ名が伏せられる。**UIとAPIではこの行が「消える」ため、クエリ次元の合計とページ次元の合計が一致しない。** 小規模サイトほど稀少クエリの比率が高く、影響が大きい。BigQuery bulk export では `is_anonymized_query` フラグで見える（6-10）。
  5. **データ保持は16ヶ月**。それ以前は取得不能。→ **前年同月比（YoY）が取れるのは実質1回きり**。noe-matchは2026年6月開設なので、初のYoYは2027年6月。
  6. **APIの `rowLimit` は最大25,000、`startRow` でページネーションが必要**。デフォルト実装（現在の `fetch_gsc.py` は `rowLimit: 500`）ではロングテールが切り捨てられる。
  7. **直近2〜3日のデータは未確定で後から増える**（現 `fetch_gsc.py` は `today - 2` で正しく回避している）。
  8. **UIのエクスポートは1,000行上限**。APIかBigQueryでしか全量は取れない。
- **具体手順（noe-matchでやるべき是正）**:
  1. `scripts/fetch_gsc.py` の `rowLimit` を 25000 に変更し、`startRow` ループを実装する（返却行数が rowLimit 未満になるまで繰り返す）。
  2. `dimensions=["query"]` の合計クリックと `dimensions=["page"]` の合計クリックを毎回比較し、**差分を「匿名化クエリ由来の欠損」として台帳に記録する**。この差分比率は小規模サイトの重要な健康指標。
  3. KPIから「サイト全体の平均順位」を外し、「query×page 単位の順位（表示数10件以上のもののみ）」に置き換える。
  4. デバイス次元（`device`）を追加取得し、PC/モバイルを分けて見る。
  5. 16ヶ月ローリングでGSCデータをローカルに永続保存する（`agent/gsc_history/` に週次スナップショット）。**これをやらないと2027年以降にYoY分析ができない。**
- **必要なデータ規模**: 罠の理解自体に規模は不要。**むしろ規模が小さいほど罠の影響が大きいので、noe-matchでは最優先事項。**
- **日本での言及度**: **中（断片的）／低（体系的理解として）** `[推定]`。打つ予定だったクエリ: `GSC 平均掲載順位 加重平均 罠`, `サーチコンソール 匿名化クエリ`, `GSC クエリ合計 一致しない`。日本語でも「平均順位はあてにならない」という話は流通しているが、**「表示数加重かつ最高順位」という正確な定義、匿名化クエリによる合計不一致、rowLimit/startRowによる欠損を一つのチェックリストにまとめた日本語資料は見当たらない**と見込む。特に匿名化クエリの話は日本語でほぼ流通していない。
- **noe-match適用度**: **A（最優先）**。理由: 他のすべての手法の前提条件。かつ既存の `scripts/fetch_gsc.py` に3箇所の実バグ（rowLimit=500、startRowなし、履歴保存なし）がある。想定工数: **3〜4時間**。特に **履歴の永続保存は今日始めないと取り返しがつかない**（16ヶ月で消える）。
- **リスク・反証**: (1) 匿名化クエリの欠損比率はGoogle側の閾値変更で変動するため、時系列で比較すると偽のトレンドを生む。(2) `rowLimit` を上げるとAPIクォータを消費する（デフォルト1日1,200クエリ/プロジェクト、1分あたり600）。週次実行なら問題ない。(3) 「position の定義を正しく理解した」ことが「position を信用してよい」を意味しない。**AI Overviews下では position という概念自体が壊れつつある（6-21）。**

---

## 6-10. GSC Bulk Data Export → BigQuery（匿名化フラグとパーティション設計）

- **一言で**: GSCの日次生データを **無制限行数・匿名化フラグ付き・16ヶ月制限なし** でBigQueryに自動エクスポートする公式機能。APIの制約をすべて回避できる唯一の手段。
- **海外での出典**:
  - https://developers.google.com/search/blog/2023/06/bigquery-efficiency-tips （Google Search Central 公式: BigQuery efficiency tips for Search Console bulk data exports）
  - https://trevorfox.com/2023/03/google-search-console-bulk-export-for-bigquery/ （The Complete Guide to GSC Bulk Export）
  - https://www.advancedwebranking.com/blog/gsc-bulk-data-export-bigquery-basics-for-better-data （See Ya, Sampling!）
  - https://www.aeripret.com/gsc-data-in-bigquery/ （Antoine Eripret）
  - https://theseocommunity.com/resources/best-of/optimize-bigquery-gsc-integration-costs-with-table-partitioning
  - https://www.seozoom.com/guide-to-the-bulk-data-export-from-google-search-console/
  - https://www.searchenginejournal.com/google-search-console-data-bigquery-enhanced-analytics/496535/
- **仕組み／なぜ効くか**: 出力されるのは `searchconsole` データセット配下の3テーブル: **`searchdata_url_impression`**（URL×クエリ×日×デバイス等の粒度）、**`searchdata_site_impression`**（サイト全体粒度）、**`ExportLog`**。設定は BigQuery プロジェクトで `search-console-data-export@system.gserviceaccount.com` に **BigQuery Data Editor** を付与し、GSC側で「一括データエクスポート」を有効にするだけ。**48時間以内に日次テーブルが降り始める。**
  - **匿名化クエリが `is_anonymized_query` フラグ付きで見える**（クエリ文字列は長さ0の文字列になるが、表示数は取れる）。UIやAPIでは行ごと消えていた情報が、少なくとも量としては見える。
  - **テーブルは日付パーティション**。出典（theseocommunity）によれば、パーティションなしで10日分をクエリすると100GBスキャンされるところ、パーティションありなら10GBで済む。**WHERE句で `data_date` を必ず絞る**のが鉄則。
- **具体手順**:
  1. Google Cloud プロジェクトを作成（既存の GSC サービスアカウントとは別でよい）。
  2. BigQuery API を有効化。IAM で `search-console-data-export@system.gserviceaccount.com` に **BigQuery ジョブユーザー + BigQuery データ編集者** を付与。
  3. GSC → 設定 → 一括データエクスポート → プロジェクトID とデータセット名（`searchconsole`）を指定。
  4. 48時間待つ。`ExportLog` テーブルで到着を確認。
  5. クエリは必ず `WHERE data_date BETWEEN '...' AND '...'` を付ける。匿名化除外は `WHERE is_anonymized_query = false`。
  6. `google-cloud-bigquery` Python クライアントで `client.query(sql).to_dataframe()` → 既存の pandas 分析基盤にそのまま繋ぐ。
- **費用**: BigQuery の **無料枠は月1TBのクエリスキャンと10GBのストレージ**。noe-match規模（月278表示 = 日次数十行）では **年間データ量が数MB〜数十MBに収まり、実質完全無料**。むしろ大規模サイトでコストが問題になる話であって、小規模サイトには純粋な利得しかない。
- **必要なデータ規模**: **下限なし。むしろ小規模サイトほど得**（匿名化クエリの比率が高く、APIの行制限より匿名化の方が痛いため）。ただし **エクスポート開始日以前のデータは遡れない**ので、始めるのが早いほど価値が出る。
- **日本での言及度**: **低** `[推定]`。打つ予定だったクエリ: `Search Console 一括データエクスポート BigQuery 設定`, `is_anonymized_query`, `GSC BigQuery 費用`。日本語でも設定手順の紹介記事は数本あると思われるが、**`is_anonymized_query` フラグの意味、パーティションによるコスト差（10GB vs 100GB）、「小規模サイトなら無料枠内で完全無料」という実務的結論をセットで書いた日本語記事はほぼない**と見込む。日本語SEO界隈での BigQuery 利用は「大規模サイト向けの高度な話」として扱われ、個人サイトが今日始めるべき話として語られていない。
- **noe-match適用度**: **A（最優先レベル）**。理由: (1) 費用が実質ゼロ。(2) 16ヶ月制限を今日から回避できる——**設定が1日遅れるごとに永久に失われるデータがある**。(3) 既にPython分析基盤とGCPサービスアカウントがあるので追加学習コストが小さい。想定工数: **初回設定1〜2時間、待ち48時間、pandas接続に1時間。** 6-09 の「履歴の永続保存」への最良解でもある（自前スナップショットより堅牢）。
- **リスク・反証**: (1) GCPの請求先アカウント（クレジットカード）登録が必須。無料枠内でも登録は要る。うっかり巨大クエリを打つと課金される（`--maximum_bytes_billed` を設定して防御すること）。(2) データの整理方法をこちらでコントロールできない（テーブル構造は固定）。(3) **エクスポート開始以前のデータは入らない。** 過去分はAPIで取って別テーブルにUNIONする必要がある。(4) GSC UI の数字と BigQuery の数字は完全一致しない（集計タイミングの差）。

---

## 6-11. クエリの意味クラスタリング（Embedding + SERP Overlap Clustering）

- **一言で**: GSCで取れた全クエリを **意味ベクトルで機械的にグループ化**し、「記事単位」ではなく「意図クラスタ単位」でパフォーマンスを見る。実験の割り当て単位にもなる。
- **海外での出典**:
  - https://contentgecko.io/blog/semantic-vs-serp-clustering/ （**SERP-overlap clustering が最高精度**: 2つのキーワードが上位15URLの40%以上を共有していればGoogleが同一意図と見なしている、と定式化）
  - https://lumkamishi.com/blog/semantic-keyword-clustering-python/
  - https://seotistics.com/keyword-clustering/
  - https://www.keyclusters.com/blog/semantic-keyword-clustering
  - https://help.seoutils.app/guide/semantic-keyword-clustering
- **仕組み／なぜ効くか**: 2種類ある。
  - **Semantic clustering**: `sentence-transformers`（SBERT）でクエリを密ベクトル化し、`scikit-learn` の `AgglomerativeClustering` や `HDBSCAN` でクラスタリング。**スケールと発見に強い**が、意味が近くてもGoogleが別意図と扱うケースを取り違える。
  - **SERP-overlap clustering**: 実際に検索して上位URLの重なりを見る。**Googleの実際の判断を直接観測するので精度が最高**だが、SERP取得のコストがかかる。
  - 出典（contentgecko）の実務的な使い分けが優れている: **「セマンティッククラスタリングは発見とスケールの道具、SERPクラスタリングは最終的なコンテンツ設計とカニバリ防止の道具」**。
  - なぜ小規模サイトで効くか: **クエリ単位では表示数が1〜3件しかなくても、クラスタに集約すれば表示数が20〜50件になり、統計的に意味のある単位になる。** これが検出力問題への最も現実的な回答。
- **具体手順**:
  1. GSC（またはBigQuery）から16ヶ月分の全クエリを取得。
  2. `pip install sentence-transformers scikit-learn`。日本語なので `intfloat/multilingual-e5-large` または `pkshatech/GLuCoSE-base-ja` などの日本語対応モデルを使う（**英語モデルをそのまま使うのは典型的な失敗**）。
  3. `model.encode(queries, normalize_embeddings=True)` でベクトル化。
  4. `sklearn.cluster.AgglomerativeClustering(n_clusters=None, distance_threshold=0.25, metric='cosine', linkage='average')` でクラスタリング。閾値は目視で調整。
  5. クラスタごとに `clicks`, `impressions`, `weighted position` を集計。**これを週次KPIの基本単位にする。**
  6. クラスタと記事の対応表を作り、1クラスタに複数記事が対応していたら 6-06 のカニバリ候補として突合。
- **必要なデータ規模**: **クエリのユニーク数が最低100件**あればクラスタリングの意味が出る。noe-matchは258記事あるので、16ヶ月分のロングテールを集めればユニーククエリ数百件は取れる可能性が高い（月278表示でも、ユニーククエリは100件超のはず）。**クラスタ単位での分析には、クラスタあたり表示数20件以上**が欲しい。
- **日本での言及度**: **低〜中** `[推定]`。打つ予定だったクエリ: `キーワードクラスタリング Python 日本語 embedding`, `SERP重複 クラスタリング`。日本語でも「キーワードグルーピング」は語られるが、**(a) SERP-overlap 40%閾値というGoogleの判断を代理する定量基準、(b) 日本語対応embeddingモデルの選択、(c) クラスタを「統計単位」として使って小規模サイトの検出力問題を解く発想** — この3点セットは日本語圏でほぼ語られていないと見込む。特に (c) が本命。
- **noe-match適用度**: **A**。理由: **小規模サイトの検出力不足に対する最も現実的な緩和策。** クエリ単位（表示1〜3）では何も言えないが、クラスタ単位（表示20〜50）なら 6-04 のDiDや 6-16 の順位検定が成立し始める。既にPython基盤があるので実装障壁が低い。想定工数: **初回6〜8時間**（モデル選定と閾値チューニングが大半）、以降は週次で自動実行。
- **リスク・反証**: (1) 日本語embeddingモデルの品質はモデル依存。「婚活」と「結婚相談所」を同クラスタにすべきかは事業判断であってモデルの判断ではない。**必ず目視でクラスタを検品すること。** (2) クラスタ境界を後から変えると時系列の比較ができなくなる。**一度決めたクラスタ定義を凍結し、バージョン管理する**（PDCA凍結の思想と同じ）。(3) SERP-overlap clustering は SERP スクレイピングを伴い、Googleの利用規約とレート制限の問題がある。個人規模では SerpAPI 等の有料APIか、手作業サンプリングに留めるべき。(4) クラスタに集約すると、クラスタ内の個別クエリの動きが見えなくなる（Simpsonのパラドックス）。

---

## 6-12. Content Decay検出と更新ROIの優先順位付け

- **一言で**: 記事のトラフィックが「ピークからどれだけ落ちたか」を減衰カーブとして定量化し、**リライト / 統合 / リダイレクト / 削除** のどれをやるかを機械的に決める。
- **海外での出典**:
  - https://searchengineland.com/guide/content-decay
  - https://seojuice.com/blog/content-decay-guide/ （Detect Decay Before It Becomes a Cliff。5フェーズモデル）
  - https://www.animalz.co/blog/content-refresh
  - https://www.digitalapplied.com/blog/content-refresh-prioritization-2026-seo-decision-matrix （**5〜20位帯が最高ROI**、加重スコアリングモデル）
  - https://www.growth-rocket.com/blog/content-decay-detection-systems-for-seo-performance-recovery/
  - https://slatehq.com/blog/content-decay-detection-tools
  - https://trydecoding.com/blog/content-decay-how-to-identify-fix/
- **仕組み／なぜ効くか**: 記事のトラフィックは典型的に「立ち上がり → ピーク → プラトー → 減衰 → 崖」の5フェーズを辿る。**プラトーと減衰の境目で介入するのが最もROIが高い**（崖まで落ちてからでは復旧コストが跳ね上がる）。原因は検索意図の変化、新しい競合記事、AI Overviewsによるクリック吸収、内部リンクの断裂、情報の陳腐化。
  - 出典（digitalapplied）の重要な指摘: **5〜20位のページが最高ROI**。既に権威・被リンク・インデックス履歴を持っているが、1ページ目のクリックボリュームをまだ取れていないから。
  - 出典（seojuice）の重要な指摘: **AI可視性における減衰は、通常検索での減衰より先に起きる**。Googleで順位を保ったまま、AI回答から静かに消えることがある。
- **具体手順**:
  1. GSCの16ヶ月ページ別クリックを週次で時系列化（6-10のBigQueryが理想）。
  2. 各ページについて `peak = rolling_4w_max()`、`current = 直近4週平均`、`decay_ratio = current / peak`。
  3. `decay_ratio < 0.7` かつ `peak >= 一定閾値` を減衰候補とする。
  4. **打ち手の分岐**: `position 5-20` → リライト優先 / `position > 30 かつ peak が小さい` → 統合または削除 / `position 保持しているのに CTR が落ちた` → AI Overviews によるクリック吸収を疑う（6-17/6-21）。
  5. ROI計算: `期待回復クリック = peak - current`、`工数 = リライト時間`、`優先度 = 期待回復クリック / 工数`。
  6. リライト後は 6-04 のDiDで効果検証（未リライト記事を対照群に）。
- **必要なデータ規模**: **ページのピーク週次クリックが最低10件**ないと減衰と偶然の区別がつかない（(a)の R=2.0 検出に m0≈11 が必要）。表示数ベースなら **ピーク週次表示50件**。**noe-matchは開設2ヶ月強でまだ「ピーク→減衰」のライフサイクルを一周していないため、現時点では検出対象が存在しない。**
- **日本での言及度**: **低** `[推定]`。打つ予定だったクエリ: `コンテンツディケイ 検出`, `記事 リライト 優先順位 スコアリング`, `content decay 日本語`。日本語では「リライトが大事」という定性的な話は氾濫しているが、**decay_ratio という定量指標、5フェーズモデル、「5-20位帯が最高ROI」という具体的な優先順位基準、リライト後のDiD検証**をセットで書いた日本語記事はほぼないと見込む。「リライト」は日本語SEOの最頻出トピックなのに、その優先順位付けが定量化されていないのは大きな空白。
- **noe-match適用度**: **B（今は仕込み、6〜12ヶ月後にA）**。理由: 手法は正しいが、サイトが若すぎて減衰事例がない。**ただし「週次のページ別クリック時系列を今から蓄積する」ことが前提条件なので、6-10と併せて今日始める必要がある。** 想定工数: 蓄積の仕組みは 6-10 に含まれる。検出ロジック自体は **3時間**、ただし実行は半年後。
- **リスク・反証**: (1) 若いサイトでは「減衰」と「そもそも上がりきっていない」の区別がつかない。**最低6ヶ月の履歴がないページには適用しないこと。** (2) 季節性のある記事（「結婚式 6月」等）は毎年減衰して見える。**6-13 の季節調整が前提。** noe-matchのテーマ（婚活・結婚・新生活）は季節性が強い領域なので、これは実害のあるリスク。(3) リライトは既存の良い部分を壊すリスクがある。リライト前のHTMLを必ずgitで保全すること（既にgitリポジトリなので自動的に満たされている）。

---

## 6-13. 季節調整済みYoY / STL・MSTL分解 / Prophetによる予測

- **一言で**: 「先月より減った」を **トレンド・季節性・残差** に分解し、施策の効果だけを取り出す。および将来トラフィックの予測区間を出す。
- **海外での出典**:
  - https://searchengineland.com/non-linear-seo-seasonality-prophet-477570 （How to model non-linear SEO seasonality with Prophet）
  - https://www.searchenginejournal.com/python-seo-forecasting/420237/ （How to Use Python to Forecast Demand, Traffic & More for SEO）
  - https://www.blog.trainindata.com/multi-seasonal-time-series-decomposition-using-mstl-in-python/ （MSTL: 複数季節性、時間変化する季節性、外れ値に頑健）
  - https://towardsdatascience.com/multi-seasonal-time-series-decomposition-using-mstl-in-python-136630e67530/
  - https://www.datacamp.com/tutorial/facebook-prophet （トレンド・季節性・祝日・誤差の4成分分解）
  - https://hex.tech/templates/time-series/time-series-forecasting-prophet/
- **仕組み／なぜ効くか**: SEOのレポーティングで最も多い誤りは「前月比」を見ること。検索需要には週次周期（平日/休日）と年次周期があり、**前月比は季節成分をそのまま施策効果と誤読する**。
  - **STL** (`statsmodels.tsa.seasonal.STL`): 単一季節性の頑健な分解。
  - **MSTL** (`statsmodels.tsa.seasonal.MSTL`): 週次+年次のような複数季節性に対応。外れ値に頑健で、季節性が時間変化する場合も扱える。
  - **Prophet**: 予測が主目的。祝日効果を明示的に入れられる（日本の祝日は `add_country_holidays(country_name='JP')`）。
  - **"seasonality-adjusted YoY"** の実務的な意味: 単純YoYは「去年の同月」と比べるが、去年と今年で祝日配置・曜日配置・イースター的な移動祝日がずれる。STL/MSTLで季節成分を除いた **trend成分同士** を比較するのが正しい。
- **具体手順**:
  1. 日次または週次のGSCクリック/表示数を `pandas.Series` に（DatetimeIndex必須）。
  2. `from statsmodels.tsa.seasonal import MSTL` → `MSTL(series, periods=(7, 365)).fit()`。日次データで最低2周期分（=2年）ないと年次季節性は推定できない。**データが1年未満なら週次季節性（period=7）のみ。**
  3. `res.trend` を取り出し、これをKPIの主指標にする。`res.resid` の分散が「ノイズの大きさ」＝ 6-16 の検定の基準になる。
  4. 予測: `pip install prophet` → `m = Prophet(); m.add_country_holidays('JP'); m.fit(df)` → `m.predict(future)`。`yhat_lower`/`yhat_upper` の予測区間を必ず併記する。
  5. 実測が予測区間の外に出た週だけを「異常」としてアラートする（**これが最も実用的な使い方**）。
  6. Google Trends の該当カテゴリ指数を `Prophet` の `add_regressor` に入れると、外部需要変動を分離できる。
- **必要なデータ規模**: **週次季節性には最低8週、年次季節性には最低2年（=104週）の履歴が必要。** noe-matchは2026年6月開設なので、**年次季節性は2028年まで推定不可能**。週次季節性は現時点でも可能だが、日次クリックが0〜1件なので週次分解の意味は薄い。表示数（日次約9件）なら週次分解に僅かに手が届く。
- **日本での言及度**: **中（時系列分析一般）／低（SEO文脈）** `[推定]`。打つ予定だったクエリ: `Prophet SEO トラフィック 予測`, `季節調整 前年同月比 SEO`, `MSTL 複数季節性 Python`。Prophet/STL の日本語解説は豊富だが、**「SEOのKPIレポートで前月比を使うのをやめて trend成分を使う」という運用への落とし込みを書いた日本語記事は稀**と見込む。特に MSTL（複数季節性）は日本語資料が少ない。
- **noe-match適用度**: **C（現時点）／2027年後半からB**。理由: 履歴が2ヶ月しかなく、季節分解の前提を満たさない。**婚活・結婚領域は季節性が極めて強い**（春の出会い期、6月ジューンブライド、年末年始の帰省後の婚活開始）ため、履歴が貯まれば価値は非常に高い。**再評価の閾値: 週次データ104点（2年）= 2028年6月。** ただし **Google Trends を使えば「業界全体の季節性」は今日から取れる**——自サイトの履歴がなくても、`婚活` `結婚相談所` のTrends指数を2004年から取れば季節パターンが分かる。**これは今すぐやる価値がある（工数2時間）。**
- **リスク・反証**: (1) 若いサイトのトレンド成分は成長カーブに支配され、季節性の推定が不安定。(2) Prophetは変化点（changepoint）を自動検出するが、SEOではアルゴリズム更新が変化点になる。**Google Core Update の日付を `changepoints` に明示的に渡す**べき。(3) 予測区間を「予測が当たる範囲」と誤読しやすい。Prophetの区間はモデルの不確実性であって、未知のアルゴリズム更新は含まない。(4) **2年分のデータを貯めても、その間にサイトの記事構成が変わっていれば季節性の推定対象が別物になっている。**

---

## 6-14. ベイズによる小標本意思決定（Beta-Binomial、「n=4クリックで何が言えるか」）

- **一言で**: 頻度論の有意性検定が使えない極小データで、**「効果がプラスである確率」** という形で不確実性を明示したまま意思決定する。
- **海外での出典**:
  - https://www.pymc.io/projects/examples/en/latest/causal_inference/bayesian_ab_testing_introduction.html （PyMC公式のBayesian A/B testing例）
  - https://www.dynamicyield.com/lesson/bayesian-approach-to-ab-testing/
  - https://uxdesign.cc/bayesian-a-b-testing-a-practical-primer-c0d4ab1c689e
  - https://www.convert.com/blog/a-b-testing/frequentist-vs-bayesian-ab-testing/
  - https://www.personizely.net/glossary/bayesian-ab-testing
  - https://alldaystech.com/guides/data-science/ab-testing-small-traffic-experiment-design （A/B Testing with Small Traffic）
- **仕組み／なぜ効くか**: 二値イベント（表示→クリック）に対して Beta事前分布は共役なので、事後分布が解析的に `Beta(α₀ + clicks, β₀ + impressions − clicks)` で出る。**MCMCすら不要、`scipy.stats.beta` の1行で済む。**
  - 決定的に重要な点: **無情報事前分布 Beta(1,1) を使うとベイズの利点が消える**。出典（craftup/alldaystech）が明確に述べている通り、**小データでこそ情報のある事前分布（過去のCTR実績、業界ベンチマーク）を入れるべき**。
  - noe-matchでの実装: サイト全体のCTR実績（1.4%）を事前分布にして、個別ページのCTRを **縮小推定（shrinkage）** する。表示3件でクリック1件のページを「CTR 33%の当たりページ」と誤認する事故が防げる。これが階層ベイズの本質。
- **具体手順**:
  1. サイト全体のCTR分布から事前分布を推定。`scipy.stats.beta.fit()` または モーメント法で `α₀, β₀` を求める（`α₀+β₀` が「事前の仮想サンプル数」= 縮小の強さ）。
  2. 各ページ/クエリについて `posterior = beta(α₀ + clicks, β₀ + impressions - clicks)`。
  3. `posterior.mean()` を「縮小推定CTR」として使う。**KPI台帳の「CTR」列をこれに差し替える。**
  4. 比較: 施策前後で `p_better = np.mean(post_after.rvs(100000) > post_before.rvs(100000))` をモンテカルロで計算。
  5. 意思決定ルールを事前に決める: 例「`p_better > 0.85` なら採用、`< 0.5` なら棄却、間なら継続観測」。**このルールをPDCA凍結の宣言に含める。**
  6. `expected_loss`（誤って採用した場合の期待損失）も計算し、`< 0.5%` を採用条件に加えると更に堅い。
- **必要なデータ規模**: **下限なし。これが最大の利点。** ただし「データが少なければ事後分布が事前分布に近いまま」= 何も学べない、という事実が数字で出るだけ。上記(c)の計算通り、**n=4クリック/278表示 では CTR の95%信用区間が [0.5%, 3.3%] と6.6倍の幅**。つまり **「n=4で言えるのは『CTRは概ね1%台のどこか』だけ」** が定量的な結論。
- **日本での言及度**: **中（ベイズA/Bテスト一般）／ほぼ無（SEOの小標本への応用）** `[推定]`。打つ予定だったクエリ: `ベイズ A/Bテスト 事前分布 少ないサンプル`, `縮小推定 CTR SEO`, `階層ベイズ CTR 推定`。ベイズA/Bテストの日本語解説は存在するが、**「GSCの表示数が2桁しかない個人サイトで、事前分布による縮小推定を使ってCTRを評価する」** という具体的応用は日本語圏で見たことがない。**この領域で最も日本語での空白が大きい手法の一つ。**
- **noe-match適用度**: **A（最優先）**。理由: **noe-matchのデータ規模で「正しく機能する」数少ない統計手法。** 他のすべての手法が「データが足りない」で終わるのに対し、ベイズは「足りないことを正しく表現する」ことができる。特に **縮小推定CTR は今日から KPI台帳に入れるべき**（表示3件クリック1件を33%と表示している限り、あらゆる意思決定が壊れる）。想定工数: **3〜4時間**（`scipy.stats` のみ、依存追加なし）。
- **リスク・反証**: (1) 事前分布の選択が結論を左右する。**事前分布を後から変えて結論を変えるのは最悪の不正。** 事前分布をコードにコミットして凍結すること。(2) `p_better > 0.85` のような閾値は恣意的。頻度論の p<0.05 と同じ問題を持つ。(3) **ベイズは検出力不足を解決しない。** 事後分布が広いことを正直に示すだけ。「ベイズなら少ないデータで判断できる」は誤解。(4) 独立性の仮定: 同じユーザーの複数表示は独立でない。GSCでは区別できない。

---

## 6-15. 統計的検出力の事前計算（Power Analysis / MDE）— 「そもそもこの実験は可能か」の判定

- **一言で**: 実験を始める **前に**「現在のデータ規模で検出できる最小効果量（MDE）」を計算し、**検出不可能な実験を始めないようにする**。
- **海外での出典**:
  - https://alldaystech.com/guides/data-science/ab-testing-small-traffic-experiment-design
  - https://craftuplearn.com/blog/ab-testing-low-traffic-sequential-testing-smart-baselines （A/B Testing Low Traffic: Sequential Testing Guide）
  - https://www.searchpilot.com/data-analysts （SearchPilotが低トラフィック・変動の大きいページのフィルタリングを事前に行うと明言）
  - https://www.convert.com/blog/a-b-testing/frequentist-vs-bayesian-ab-testing/
- **仕組み／なぜ効くか**: SEO業界で最も多く浪費されているのは「有意にならなかったテスト」ではなく **「最初から有意になりようがなかったテスト」** に費やした時間。MDEを事前に計算すれば、その時間をゼロにできる。
  - MDE = 与えられたサンプル数・α・検出力で、統計的に検出できる最小の効果。
  - **逆算して使うのが本質**: 「私は4週間で結論を出したい。4週間で得られる表示数は1,112件。その規模でのMDEは？」→ 答えが「+180%」なら、その実験はやってはいけない。
  - noe-matchでの実際のMDE（月278表示、2群に分割 → 群あたり139表示/月、4週間実験）:
    - ベースラインCTR 1.5%、群あたり139表示 → 検出可能な最小効果は **相対 +700%以上**（CTR 1.5% → 12%）。**つまり事実上どんな実験も不可能。**
- **具体手順**:
  1. `pip install statsmodels`。
  2. `from statsmodels.stats.power import NormalIndPower; from statsmodels.stats.proportion import proportion_effectsize`
  3. 逆算: `NormalIndPower().solve_power(effect_size=None, nobs1=139, alpha=0.05, power=0.8)` で検出可能な effect_size（Cohen's h）を得る。
  4. `proportion_effectsize` の逆変換で、それを相対CTR改善率に直す。
  5. **この数字をKPI台帳の固定ヘッダに書く**: 「現在のMDE: 相対+700%（=実験不能）」。データが増えるたびに更新する。
  6. クリック数ベースは上記(a)の `m0 ≈ (1.4/(√R−1))²` の表を使う。
- **必要なデータ規模**: **なし。これは「規模を判定する」ためのメタ手法。**
- **日本での言及度**: **低** `[推定]`。打つ予定だったクエリ: `検出力分析 サンプルサイズ設計 A/Bテスト`, `MDE 最小検出効果 計算`, `SEO テスト サンプルサイズ`。検出力分析自体は統計・臨床試験文脈で日本語資料が豊富だが、**「SEO施策を始める前にMDEを計算して"やらない"判断をする」という運用は日本語SEO圏でほぼ語られていない**と見込む。日本語SEO記事の圧倒的多数は「施策を試しましょう」で終わり、「その施策の効果は原理的に測れません」を最初に言う文化がない。
- **noe-match適用度**: **A（最優先／防御的価値が最大）**。理由: **noe-matchにとって最も価値があるのは「新しい分析手法」ではなく「無駄な分析をやらない根拠」。** MDE計算はそれを1時間で提供する。PDCA凍結の考え方とも完全に整合する——凍結期間の長さをMDEから逆算して決められる。想定工数: **1〜2時間**。本レポート冒頭の(a)(b)表がそのまま使える。
- **リスク・反証**: (1) MDEが大きい=実験不能、を「だから何もするな」と誤読する危険。**正しい解釈は「効果測定を諦めて、外部知見に基づくベストプラクティスを適用しろ」。** 小規模フェーズは実験フェーズではなく実装フェーズ。(2) 正規近似はクリック数が5未満だと崩れる。その場合は `scipy.stats.poisson` による厳密計算か、シミュレーション（10,000回のブートストラップ）を使う。(3) MDEの計算はα=0.05, power=0.8 という慣習値に依存する。個人サイトなら α=0.2, power=0.6 くらいに緩めて「粗い意思決定」に使う選択肢もある（ただし偽陽性が増えることを明示的に受け入れる場合のみ）。

---

## 6-16. 週次の順位変動の統計的有意性判定

- **一言で**: 「先週12.3位、今週9.8位。改善した？」に **統計的に答える**。GSCの平均順位は表示数加重平均なので、素朴な差分は無意味。
- **海外での出典**:
  - https://seotesting.com/google-search-console/average-position/
  - https://www.incremys.com/en/resources/blog/google-search-console-position
  - https://www.ritnerdigital.com/blog/my-impressions-dropped-but-my-average-position-went-up-in-google-search-console-what-does-that-mean （表示数が減って平均順位が上がる = 順位改善ではなくクエリ構成の変化、というSimpsonのパラドックスの典型例）
  - https://nikki-pilkington.com/why-your-average-position-in-google-search-console-is-absolute-rubbish/
- **仕組み／なぜ効くか**: GSCの平均順位が動く原因は3つあり、素朴な比較ではこれらが混ざる。
  1. **本当に順位が動いた**
  2. **クエリ構成が変わった**（新しい低順位クエリで表示が増えた → 平均が悪化。順位は何も変わっていない）
  3. **デバイス/地域構成が変わった**
  - **解決策の核心: クエリコホートを固定する。** 両週に共通して存在するクエリだけを取り出し、その集合の中でだけ順位を比較する。これで原因2をほぼ消せる。
  - 検定は **対応のあるノンパラメトリック検定**（順位データは正規分布しないため）: `scipy.stats.wilcoxon`（対応あり）。あるいは表示数で重み付けたブートストラップ。
- **具体手順**:
  1. 週W1とW2の `query × page × position × impressions` を取得。
  2. 両週に共通する `(query, page)` ペアのみに絞る（内部結合）。**この時点で行数が半分以下に減るのが普通。それが正常。**
  3. `delta = position_W2 - position_W1` を計算（負が改善）。
  4. `scipy.stats.wilcoxon(pos_w1, pos_w2)` で対応のある検定。
  5. 表示数の少ない行はノイズが大きいので、`impressions >= 5` でフィルタするか、`scipy.stats.bootstrap` で表示数加重の中央値差の信頼区間を出す。
  6. **共通クエリ集合が20ペア未満なら「判定不能」と記録する。** 無理に検定しない。
- **必要なデータ規模**: **両週に共通する (query, page) ペアが最低20〜30組**。各ペアの表示数が5件以上。noe-match換算で **週間表示数150件以上（月600件）**。現状の月278表示（週約65表示）では、共通ペアが10組を切ると予想され、**判定不能になる可能性が高い。**
  - **緩和策: 週次ではなく4週次で比較する**（月278表示 → 共通ペア数が実用域に届く可能性）。あるいは 6-11 のクラスタ単位で見る。
- **日本での言及度**: **ほぼ無** `[推定]`。打つ予定だったクエリ: `GSC 順位変動 有意差 検定`, `平均掲載順位 比較 クエリ固定`, `サーチコンソール 順位 統計`。日本語SEO記事は「順位が上がった/下がった」を無検定で語るのが標準。**「クエリコホートを固定してWilcoxon検定する」という発想の日本語記事は皆無に近い**と確信度高く見込む。**本レポート中、日本語での空白が最も大きい手法の候補。**
- **noe-match適用度**: **B**。理由: 手法は正しく、実装も軽い（scipy 5行）。ただし現データ規模では共通ペア数が足りず「判定不能」を返す可能性が高い。**しかし「判定不能と正しく返すこと」自体に大きな価値がある**——無根拠な「順位が改善しました」レポートを防げる。4週次比較 + クラスタ集約で成立域に持ち込める。想定工数: **2〜3時間**。
- **リスク・反証**: (1) 共通クエリだけに絞ると、**新規に上がってきたクエリ（=最も重要な成長シグナル）が分析から消える**。共通クエリの順位検定とは別に、「新規クエリ数」「消失クエリ数」を独立したKPIとして記録すること。(2) GSCのpositionは既に週内で加重平均されているので、週内の変動情報は失われている。日次で取ればマシだがクリック0の日が多く実用性が落ちる。(3) Wilcoxon検定は「順位の差の分布が対称」を仮定する。SEOでは急落は起きやすく急騰は起きにくいので非対称。**符号検定（`scipy.stats.binomtest`）の方が仮定が少なく堅い場合がある。**

---

## 6-17. AI流入の計測（utm_source=chatgpt.com / GA4カスタムチャネルグループ / dark traffic）

- **一言で**: ChatGPT/Perplexity/Gemini等からの流入を可視化する。ただし **参照元が付かない「dark traffic」が大半**であることを前提に設計する。
- **海外での出典**:
  - https://www.growthunhinged.com/p/how-to-measure-the-impact-of-ai-search-the-right-way
  - https://www.swydo.com/blog/track-ai-traffic-in-ga4/ （The Agency Guide to Tracking AI Traffic in GA4 — Setup, Regex Patterns）
  - https://digital-power.com/en/inspiration/measuring-ai-referral-traffic-in-web-analytics/
  - https://www.digitalapplied.com/blog/ga4-ai-assistant-channel-2026-measure-ai-traffic-playbook （GA4の新しい "AI Assistant" チャネル）
  - https://authoritytech.io/blog/llm-referral-traffic-tracking`
  - https://www.tryhikoo.com/en/blog/guides/measure-ai-traffic-ga4/
  - https://fatjoe.com/blog/track-ai-traffic/
  - Kevin Indig: https://www.growth-memo.com/p/growth-intelligence-brief-15 / https://substack.com/@kevinindig/p-152850238
- **仕組み／なぜ効くか（および罠）**:
  1. **ChatGPTは `utm_source=chatgpt.com` を自動付与するが、`utm_medium` も `utm_campaign` も付けない。** GA4のデフォルトチャネルグループは source+medium の組で判定するため、**mediumがないと "Unassigned" に落ちる**。これがGA4でAI流入が見えない最大の技術的原因。
  2. **AI由来トラフィックの 70.6% は referrer が剥がれて "Direct" に着地する** `【要再検証】`（出典: 上記AI流入検索クラスタ）。ベストエフォートのカスタムチャネルグループでも **回収できるのは50〜70%** とされる。
  3. **"Dark AI traffic"** = referrer なしで来る、AI経由の直接流入・ブランド検索経由の流入。**原理的にGA4では捕捉不能。**
  4. Kevin Indig の重要な指摘: **クライアントサイド計測（GA4）ではなくサーバーログを見るべき**。かつ **`GPTBot`（学習用インジェスト）と `ChatGPT-User`（リアルタイム取得）を区別する**こと。前者は「将来引用される可能性」、後者は「今まさに誰かの質問に答えるために読まれている」を意味し、価値が全く違う。
- **具体手順**:
  1. GA4 → 管理 → チャネルグループ → カスタムチャネルグループを作成。
  2. 条件: `Session source` が正規表現 `chatgpt\.com|openai\.com|perplexity\.ai|gemini\.google\.com|claude\.ai|copilot\.microsoft\.com|you\.com|bing\.com/chat` にマッチ → チャネル名 "AI Assistant"。
  3. **`Session medium` の条件は入れない**（ChatGPTがmediumを付けないため）。ここを間違えると全部漏れる。
  4. 併せて **Looker Studio でAIチャネルのランディングページ別レポート** を作る（どの記事がAIに引用されているかが分かる）。
  5. サーバーログ側: noe-matchはGitHub Pages（CNAMEあり）のため生ログが取れない。→ **Cloudflareを前段に入れれば Bot Analytics で `GPTBot` / `ChatGPT-User` / `PerplexityBot` / `ClaudeBot` の到達を確認できる。** これが個人規模での現実解。
  6. **Dark traffic の間接推定**: 「Direct流入の週次推移」と「6-19のブランド検索量」を並べて監視する。AI経由の影響はこの2つに先に現れる。
- **必要なデータ規模**: **チャネル設定自体に下限なし。今日やるべき。** ただし noe-match の現在の流入規模（月クリック4）では、AI流入が月0〜1件で統計的な議論はできない。**「今設定して、データが来た時に取り逃さない」ことに価値がある。**
- **日本での言及度**: **中（設定手順）／低（dark trafficと計測不能性の議論）** `[推定]`。打つ予定だったクエリ: `GA4 AI流入 チャネルグループ 設定`, `utm_source=chatgpt.com 計測`, `ダークトラフィック AI 参照元なし`。設定手順の日本語記事は2025年以降増えていると思われるが、**「medium が付かないから Unassigned に落ちる」という具体的な失敗モード、「70%は原理的に捕捉不能」という限界の直視、GPTBot と ChatGPT-User の区別** — これらは日本語圏でほぼ流通していないと見込む。
- **noe-match適用度**: **A（設定は今日／分析は将来）**。理由: 設定工数が小さく（**1時間**）、逃した流入は永久に取り戻せない。婚活・結婚領域は「結婚相談所 選び方」のような比較検討クエリが多く、**AIアシスタントで質問されやすいテーマ**。Cloudflare導入は別途 **2〜3時間**（GitHub Pages前段に置く構成）。
- **リスク・反証**: (1) カスタムチャネルグループは **過去データに遡及適用される**（GA4の仕様）ので、過去のUnassignedも再分類される。ただし referrer が元々なかった分は永久に戻らない。(2) LLM各社のUTM付与方針は予告なく変わる。正規表現の定期メンテが必要。(3) **「AI流入が少ない」ことと「AIに引用されていない」ことは別物。** 引用されてもクリックされない（zero-click）のがAIの標準的な挙動。→ 6-18 の直接計測が必要。(4) Cloudflare導入はサイト全体の配信経路を変えるので、設定ミスでサイトが落ちるリスクがある。

---

## 6-18. Share of Model / LLM引用率の自前モニタリング

- **一言で**: 同一のプロンプトセットを定期的に各LLMに投げ、**自ブランド/自サイトが言及・引用される率を時系列で記録する**。AI時代の「順位計測」の代替。
- **海外での出典**:
  - https://www.symphonicdigital.com/blog/understanding-share-of-model （Share of Model: The Essential Marketing Metric for the AI Era。**SoMは確率的**——「best organic skincare」で80%の回答に出るブランドもあれば20%のブランドもある）
  - https://nightwatch.io/blog/how-to-measure-llm-visibility/ （**選挙予測に着想を得たpolling型モデル。250〜500の高意図クエリの代表サンプル** `【要再検証】`）
  - https://searchatlas.com/blog/llm-visibility-tracking-plan/ （**プロンプトセットは30〜50クエリでファネル全段階をカバー** `【要再検証】`）
  - https://www.meltwater.com/en/blog/how-to-track-llm-prompts
  - https://www.optimizegeo.ai/blog/how-to-track-brand-visibility-in-llms
  - https://trackmyvisibility.com/blogs/llm-behavior/what-is-llm-visibility/
  - https://aiclicks.io/blog/best-tools-for-tracking-llm-visibility
- **仕組み／なぜ効くか**: LLMの出力は確率的であり、**同じ質問を2回すると違うブランドが返る**。したがって「1回投げて出たか出ないか」は測定ではなくサンプリング。出典（aiclicks経由のAllmond事例）は **1プロンプトあたり4〜5回スキャンして平均を取る** と述べている。
  - 指標: `AI SOV = 自ブランド言及数 ÷ 追跡全ブランド言及数 × 100`。
  - **各実行で「日付」だけでなく「モデルバージョン」を必ず記録する**（出典 nightwatch が明記）。LLMの挙動はモデル更新で不連続に変わるため、バージョンを記録していない時系列は解釈不能になる。
  - 記録項目: 言及の有無 / 言及順位（回答内の何番目か）/ センチメント / 引用リンクの有無。
- **具体手順**:
  1. **プロンプトセットの設計**: noe-match のテーマで、ファネル段階別に30〜50問。例:
     - 認知期: 「婚活を始めるにはまず何をすべきか」
     - 比較期: 「結婚相談所とマッチングアプリの違いは」「30代女性におすすめの婚活方法」
     - 決定期: 「結婚相談所の費用相場は」「入籍時の手続きチェックリスト」
     - 周辺: 「産後ケア 費用」「育休給付金 いくら」
     - **noe-matchはブランドが無名なので、SoM（ブランド言及率）ではなく "citation rate"（自サイトURLが引用元として出る率）を主指標にすべき。**
  2. **実行設計**: 各プロンプト × 各LLM（ChatGPT, Gemini, Claude, Perplexity）× **反復3〜5回** × 週1回。50問 × 4モデル × 3反復 = 週600リクエスト。
  3. **実装**: 各社APIを使う（Web検索機能を有効にすること。無効だと引用が出ない）。`anthropic` / `openai` / `google-genai` の各SDK。Perplexityは `sonar` API。レスポンスから引用URLを正規表現で抽出し、`noe-match.com` を含むかを判定。
  4. **統計処理**: プロンプト `i`、反復 `j` について `y_ij ∈ {0,1}`。プロンプト単位の引用率 `p_i = mean_j(y_ij)`。全体指標は `mean_i(p_i)`。**信頼区間はプロンプト単位のブートストラップ**（反復間の相関があるため単純二項CIは狭すぎる）: `scipy.stats.bootstrap((p_array,), np.mean)`。
  5. **n数の根拠**: ±10pp精度なら実質n≈96（プロンプト数×反復数ではなく **独立なプロンプト数が効く**ので、50問×3反復では有効n≈50〜80）。**±10ppより細かい変化は50問セットでは検出できない**ことを明記する。
  6. 週次でCSVに追記し、モデルバージョン列を必ず入れる。
- **必要なデータ規模**: **自サイトのトラフィック規模とは無関係。** noe-matchの278表示でも実行できる。**これがこの手法の最大の利点**——他のすべての手法がデータ不足で詰まる中、Share of Model計測だけは「自分でデータを作る」ため規模の制約を受けない。
  - コスト概算: 週600リクエスト × 平均1,500出力トークン。各社の低価格モデルを使えば **月額数百円〜2,000円程度**。
- **日本での言及度**: **低（ツール紹介はある）／ほぼ無（自前実装の統計設計）** `[推定]`。打つ予定だったクエリ: `LLM 引用率 計測 自前`, `Share of Model 計測`, `AI可視性 トラッキング 日本語`。日本語では「LLMO」「GEO」という言葉と共に有料ツールの紹介記事が増えているが、**「プロンプトセットを何問にするか」「反復何回で確率的変動を均すか」「有効n数からどこまでの精度が出るか」「モデルバージョンの記録が必須である理由」という測定設計論を書いた日本語記事はほぼ存在しない**と見込む。**本レポート中、日本語での空白が最大の手法。**
- **noe-match適用度**: **A**。理由: (1) データ規模の制約を受けない唯一の手法。(2) 婚活・結婚・新生活は「AIに相談されやすい」領域。(3) 既にPython基盤があり、API呼び出しの実装障壁が低い。(4) **順位計測が壊れつつある（6-21）中で、代替となる先行指標を今から持てる。** 想定工数: **初回8〜12時間**（プロンプトセット設計に半分、実装に半分）、以降は週次自動実行で0時間。月額コスト数百〜2,000円。
- **リスク・反証**: (1) **各社の利用規約**: 自動化された大量クエリはAPI経由なら問題ないが、Webスクレイピングは規約違反になりうる。**必ず公式APIを使うこと。** (2) パーソナライゼーション: LLMの回答はユーザー履歴・地域で変わる。API経由の「素の」回答は実ユーザーが見る回答と違う。(3) **引用されてもトラフィックにならない**（zero-click）。SoMとクリックの相関は保証されていない。この手法は「先行指標」であって成果指標ではない。(4) モデル更新で数値が不連続にジャンプする。バージョンを記録していないとトレンドとして誤読する。(5) プロンプトセットを後から変えると時系列が切れる。**凍結してバージョン管理すること**（PDCA凍結の思想を適用）。

---

## 6-19. Share of Search / ブランド需要を先行指標にする

- **一言で**: Google Trends上での「自ブランド検索数 ÷ カテゴリ内全ブランド検索数」を測る。Les Binet の研究により **市場シェアを6〜12ヶ月先行する** ことが示された指標。
- **海外での出典**:
  - https://ipa.co.uk/news/binet-presents-fast-cheap-predictive-share-of-search-metric （IPA公式: EffWorks Global 2020 での Les Binet の発表）
  - https://ipa.co.uk/effworks/effworksglobal-2020/share-of-search-as-a-predictive-measure
  - https://www.warc.com/en/article/les-binet-outlines-why-%22share-of-search%22-is-a-powerful%2C-predictive-marketing-metric-07db5c40f18642ca9d93d1e84a42d668
  - https://lbbonline.com/news/les-binet-unveils-share-of-search-metric-with-10-key-findings
  - https://www.26pmx.com/insights/les-binet-share-of-search-metric-taken-further
  - https://prooflytics.io/blog/branded-search-volume-leading-indicator-pipeline
  - https://www.junoschool.org/article/branded-search-volume-kpi/
  - https://lseo.com/answer-engine-optimization-services/branded-search-volume-measuring-the-ripple-effect-of-aeo/
- **仕組み／なぜ効くか**: Binet は自動車・エネルギー・携帯電話の3カテゴリで検証し、**Share of Search が Share of Market と相関し、かつ先行する**ことを示した `【要再検証: 具体的な相関係数と先行月数は原典で確認すること】`。Google Trends は無料、2004年まで遡れ、週次粒度。Binet の表現では **Googleは「人間の意図に関する世界最大のデータベース」**。
  - **AI時代における新しい意味**: 出典（lseo）が指摘する通り、AI検索で記事が引用されクリックされなくても、**ブランド名を覚えたユーザーが後でブランド名を検索する**。したがってブランド検索量は「AI経由の見えない影響」を捕捉する数少ない指標になる。6-17 の dark traffic 問題への部分的な回答。
  - GSCでの測り方: クエリを「ブランド名を含む」でフィルタし、**クリックではなく表示数を読む**（出典 wpseoai）。誤字バリエーション、ブランド+製品名も含める。
- **具体手順**:
  1. `pip install pytrends`（または `trendspy`）。Google Trends から `noe-match`, `Noe結婚設計室` + 競合メディア名の週次指数を取得（`geo='JP'`）。
  2. `SoS = own / (own + competitors)` を週次で計算。
  3. GSC側: `dimensionFilterGroups` でクエリ正規表現 `noe|ノエ|結婚設計室` にマッチする行を抽出し、週次表示数を集計。**ブランド/非ブランドの分離を全KPIレポートの標準にする。**
  4. 「非ブランド表示数」と「ブランド表示数」を別系列でプロットし、**前者の増加が後者の増加に何週先行するか** を相互相関（`scipy.signal.correlate` / `statsmodels.tsa.stattools.ccf`）で見る。
  5. AI流入施策（6-18）の効果は、まずブランド検索に現れる仮説で監視する。
- **必要なデータ規模**: **Google Trends は検索量が閾値未満だと「データ不足」で0を返す。** 無名ブランドでは完全に使えない。**noe-match の現状（開設2ヶ月、月278表示）では Google Trends に一切データが出ない可能性が極めて高い。**
  - GSC側のブランドクエリ表示数なら **月10表示から記録開始できる**。ゼロでも「ゼロである」ことを記録する価値がある（0→1 の変化が最初の重要シグナル）。
  - Google Trends が使えるようになる目安: **月間ブランド検索が数百〜数千**。noe-matchには当面来ない。
- **日本での言及度**: **低** `[推定]`。打つ予定だったクエリ: `Share of Search レス・ビネット`, `ブランド検索数 先行指標`, `シェアオブサーチ 市場シェア 予測`。「指名検索を増やそう」という話は日本語SEO記事にあるが、**Les Binet の Share of Search 研究そのもの（IPA/EffWorks 2020、6〜12ヶ月の先行性、Google Trendsでのカテゴリ内シェア計算）が日本語で紹介されている例は少ない**と見込む。マーケティング効果測定の日本語圏では Binet & Field の「The Long and the Short of It」は知られているが、Share of Search は続編にあたり普及が遅れている。
- **noe-match適用度**: **B（ブランド/非ブランド分離はA、Trends部分はC）**。理由:
  - **今すぐやるべき（A相当）: GSCのクエリをブランド/非ブランドに分離して別々にトラッキングする。** これは規模を問わず有効で、**「ブランド検索が0から1になった週」を検出できる体制を作ることに価値がある**。工数 **1〜2時間**。
  - **今はできない（C相当）: Google Trends での SoS 計算。** 検索量不足でデータが返らない。**再評価の閾値: 月間ブランド検索数 数百件。**
- **リスク・反証**: (1) Google Trends は相対指数であって絶対値ではない。**サンプリングされており、同じクエリでも取得タイミングで値が変わる。** 複数回取得して平均を取ること。(2) 「Noe」のような短い語は無関係な検索と混ざる。**ブランド名の一意性が低いと使えない。** noe-match の場合これは実害のあるリスク。(3) **Binet の研究は消費財のマスブランドが対象。** 個人運営のニッチメディアに外挿できる保証はない。**むしろできないと考えるべき。** (4) 先行性6〜12ヶ月は、個人サイトの意思決定サイクル（週次）と時間スケールが合わない。

---

## 6-20. ログファイル / クロールバジェットの実測と個人規模での代替

- **一言で**: サーバーの生ログでGooglebot（およびAIクローラー）の実際の挙動を見る。生ログが取れない個人サイトでの現実的な代替手段を持つ。
- **海外での出典**:
  - https://www.oncrawl.com/general-seo/google-crawl-stats-report-log-file-analysis/ （**GSCのCrawl Statsは日次集計でURL単位が見えない**。「火曜に12,000ページクロールされた」は分かるが「どの12,000ページか」は分からない）
  - https://searchengineland.com/guides/log-file-analysis
  - https://firstplaceseo.co.uk/technical-seo/free-tools-to-analyse-log-files-and-fix-crawl-waste/ （Screaming Frog Log File Analyzer、GoAccess）
  - https://www.wix.com/seo/learn/resource/crawl-budget-optimization
  - https://autopagerank.com/log-file-analysis-vs-google-search-console-crawl-stats/ （**小規模サイトならGSC単独で十分、20,000ページ超なら両方使え**）
  - https://gautamkhorana.com/blog/log-file-analysis-crawl-budget-large-sites/
  - https://authoritytech.io/blog/llm-referral-traffic-tracking
- **仕組み／なぜ効くか**: ログには「誰が、いつ、どのURLを、どのステータスコードで」が全件記録される。クロールシミュレーションでは見えない実際の404連発、リダイレクトチェーン、5xx、遅延が分かる。
  - **ただし出典（autopagerank）が明言する通り、小規模サイト（<20,000ページ）ではGSC単独で十分。** noe-matchは258記事なので、**クロールバジェットは構造的に問題にならない**。
  - **むしろ2026年時点で価値があるのは「AIクローラーの分離観測」**: `GPTBot`（OpenAI学習用）、`ChatGPT-User`（リアルタイム取得）、`OAI-SearchBot`、`PerplexityBot`、`ClaudeBot`、`Google-Extended`。**ChatGPT-User の到達は「今まさに誰かの質問に答えるために読まれた」を意味し、6-18のSoM計測と突き合わせられる。**
- **具体手順（noe-matchでの現実解）**:
  1. **noe-matchはGitHub Pages配信のため生アクセスログが取得不能。** これが最大の制約。
  2. **代替1: Cloudflareを前段に置く。** 無料プランでも Bot Analytics で主要ボットのリクエスト数が見える。設定は DNS を Cloudflare に向けるだけ（工数2〜3時間、ダウンタイムリスクあり）。
  3. **代替2: GSCの「クロールの統計情報」レポート**（設定 → クロールの統計情報）。日次のクロールリクエスト数、レスポンス別内訳、ファイルタイプ別、Googlebotタイプ別が見える。**URL単位は見えないが、異常検知には十分。**
  4. **代替3: Cloudflare Workers または軽量な計測エンドポイント**でUser-Agentをログする。ただしGitHub Pagesでは静的配信なのでサーバーサイド実行ができない。
  5. **代替4: `robots.txt` へのアクセスログ。** これも静的配信では取れない。
  6. **結論として現実解は Cloudflare 導入一択**。導入すれば 6-17 のAI流入計測と共通の基盤になる。
- **必要なデータ規模**: **ページ数が20,000未満ならクロールバジェット分析の価値はほぼゼロ。** noe-match（258ページ）は完全にこの範囲。**ただしAIクローラー観測は規模を問わず価値がある**（1回の `ChatGPT-User` アクセスでも情報）。
- **日本での言及度**: **中（ログ分析一般）／低（AIクローラーの区別、GitHub Pages等での代替手段）** `[推定]`。打つ予定だったクエリ: `ログファイル分析 SEO クロールバジェット`, `GPTBot ChatGPT-User 違い`, `Cloudflare ボット分析 SEO`。日本語でもログ分析の紹介はあるが、**「GPTBot は学習用、ChatGPT-User はリアルタイム取得で意味が違う」という区別と、静的ホスティング環境での代替手段の具体的な議論はほぼない**と見込む。
- **noe-match適用度**: **C（クロールバジェット）／B（AIクローラー観測）**。理由: 258ページではクロールバジェットは問題にならない（Googleは容易に全ページを回る）。一方AIクローラーの到達観測は、Cloudflare導入という副作用の大きい前提を伴うが、6-17 と共通基盤になるのでセットで検討する価値がある。想定工数: Cloudflare導入 **2〜3時間 + 検証**。**急がなくてよい。**
- **リスク・反証**: (1) Cloudflare導入はDNS切り替えを伴い、設定ミスでサイトが数時間落ちる可能性がある。**GitHub Pages + カスタムドメイン + Cloudflare の組み合わせはSSL設定（Full/Full Strict）で躓きやすい。** (2) Cloudflareの無料Bot Analyticsは粒度が粗く、URL単位のボットアクセスは見えない（有料プランが必要）。(3) User-Agent は偽装できるので、`GPTBot` を名乗るアクセスが本物とは限らない。OpenAIは公式IPレンジを公開しているので照合が必要。(4) **クロールバジェット最適化は大規模サイトの問題であり、個人サイトで時間を使うのは典型的な最適化の誤配分。**

---

## 6-21. Rank Trackingの限界とSERP Feature / Pixel Position トラッキングへの移行

- **一言で**: 「順位」という単一のスカラー値が、パーソナライズ・ローカライズ・AI Overviews によって **意味を失いつつある**。代わりに「SERP上のどの面に、どの高さで出ているか」を測る。
- **海外での出典**:
  - https://serpapi.com/blog/rank-tracking-in-the-age-of-ai-overviews-whats-changed/
  - https://mygomseo.com/blog/rank-tracking-software-is-broken-why-position-1-doesn-t-mean-what-it-used-to
  - https://www.riffanalytics.ai/blog/track-serp-features （How To Track SERP Features Effectively In 2026）
  - https://www.goodfirms.co/resources/serp-visibility-why-rankings-no-longer-drive-organic-traffic
  - https://www.yotpo.com/blog/rank-tracking-ai-first-era/ （Rank Tracking In 2026: 10 Tips For The AI-First Era）
  - https://aysa.ai/ai-driven-personalized-search-2026-win-visibility/
  - https://agencydashboard.io/blog/rank-tracking-ai-search-visibility
  - https://www.tryvizup.com/blog/enterprise-rank-tracking-2026
- **仕組み／なぜ順位が壊れるか**:
  1. **単一の"真のSERP"が存在しない**（出典 yotpo/aysa）。パーソナライゼーションで結果が断片化し、「順位は動いていないのに新しいAI Overviewsに押し下げられて折り返し線の下に行く」が起きる。
  2. **順位1位でも注目・クリック・売上を保証しない**（出典 mygomseo）。AI Overviews、パーソナライゼーション、ゼロクリック結果が、青いリンクが問題になる前に需要を横取りする。
  3. **新しい可視性の定義は3層**（出典 riffanalytics/agencydashboard）: (a) 従来の順位 (b) **実際の可視性 = ピクセル位置** (c) AI生成コンテンツ内での存在。
  4. **citation share（引用シェア）がコアのSEO指標になりつつある**。多くの既存ツールは自社ブランドがAI Overviews内に出ているか、引用元になっているかを表示できない。
  5. 出典（yotpo）の重要な指摘: SEO実務者が疲弊しているのは、**Googleが機能を導入 → SEOが最適化 → Googleが機能を引っ込める、というサイクルが加速している**こと。SERP機能への過剰最適化はそれ自体がリスク。
- **具体手順（noe-matchでの現実解）**:
  1. **順位トラッキングツールを買わない。** 個人規模では費用対効果が合わず、かつ上記の理由で得られる情報の信頼性が低い。
  2. 代わりに **GSCの `query × page` の position を「参考値」として記録し、KPIの主指標にはしない**（6-09、6-16）。
  3. 主指標を **クリック数・表示数・6-18のcitation rate** に置く。
  4. **主要20クエリについて、月1回手動でSERPをスクリーンショット保存する**（AI Overviewsの有無、上位に何が出ているか）。工数月30分。**これが個人規模で最も費用対効果の高いSERP機能トラッキング。**
  5. AI Overviews が出るクエリで **「順位が良いのにCTRが期待値を大きく下回る」** パターンを 6-07 の期待CTR差分で検出する。**これがAIOによるクリック吸収の間接的な計測になる。**
  6. スクリーンショットを日付付きでリポジトリに保存し、時系列でSERPの構造変化を追う。
- **必要なデータ規模**: **手動SERP観察に下限なし。** 期待CTR差分によるAIO検出には **クエリあたり表示数30件以上**が必要（6-07参照）。noe-matchでは上位数クエリのみ対象になる。
- **日本での言及度**: **低〜中** `[推定]`。打つ予定だったクエリ: `AI Overviews 順位 意味 崩壊`, `ピクセル順位 SERP機能 トラッキング`, `順位計測 限界 2026`。日本語でも「AI Overviewsで検索順位の意味が変わる」という論調の記事はあるが、**「ピクセル位置」「citation share」という具体的な代替指標、および「順位トラッキングツールを買わずに期待CTR差分でAIO影響を間接検出する」という個人規模の現実解**は日本語圏でほぼ語られていないと見込む。日本語SEO界隈は依然として「順位計測ツール」が中心。
- **noe-match適用度**: **B**。理由: 「やらない判断」としての価値が高い（順位ツールに課金しない、順位をKPIにしない）。手動SERP観察は工数が小さく（月30分）情報価値が高い。期待CTR差分によるAIO検出は 6-07 の実装に含まれる。想定工数: **運用ルールの策定に1時間、以降は月30分。**
- **リスク・反証**: (1) 手動観察はサンプル数が少なく、自分の検索履歴でパーソナライズされる。**シークレットモード + 位置情報を明示した検索**を使うこと。(2) 「順位を追わない」は「順位が無意味」ではない。**順位は依然としてクリックの最大の説明変数**。追い方を変えるだけ。(3) 期待CTR差分でAIOを検出する方法は、他の原因（タイトルが悪い、SERP機能が別にある）と区別できない。**必ずSERPを目視で確認して裏取りすること。** (4) SERP機能への最適化サイクルの短さ（出典yotpo）を考えると、SERP機能トラッキングに投資すること自体が次に無駄になるリスクを持つ。

---

## 6-22. Attribution: アフィリエイトのラストクリック問題と assisted conversion

- **一言で**: アフィリエイトの成果は **最後にクリックされたリンクにのみ帰属**するため、意思決定を形成した記事（比較記事、悩み解決記事）の貢献がゼロと記録される。
- **海外での出典**:
  - https://prismique.com/blog/a-practical-guide-to-incrementality-testing （アフィリエイトの帰属とincrementalityの関係）
  - https://irev.com/blog/how-to-measure-incrementality-in-affiliate-marketing-holdout-tests-geo-tests-and-mmm-for-real-growth/ （**"capture であって create ではない"** パートナーの識別）
  - https://www.metricuno.com/incrementality-testing
  - https://supermetrics.com/blog/incrementality-testing
  - https://www.searchinfluence.com/blog/ai-search-kpis-traffic/ （assisted conversion を含むAI検索KPI）
  - https://prooflytics.io/blog/branded-search-volume-leading-indicator-pipeline
- **仕組み／なぜ効くか**: ASPの管理画面はラストクリックしか見せない。ユーザーが「結婚相談所 費用」記事で知識を得て、後日「〇〇相談所」と指名検索して別サイトのリンクから申し込んだ場合、**noe-matchの貢献は完全に記録から消える**。
  - **個人メディアで実行可能な近似手段**:
    1. **サイト内の assisted path 計測**: GA4のイベントで「記事A閲覧 → 記事B閲覧 → アフィリリンククリック」の経路を追う。GA4の探索レポート「経路データ探索」で可能。**これで「成約直前の記事」だけでなく「その手前で読まれた記事」が分かる。**
    2. **ラストクリック記事と assisted 記事のクリック貢献を分けて台帳に記録する**。単純なルールベース帰属（例: 直前クリック記事に50%、同セッション内の他記事に50%を均等配分）で十分。厳密なMTAは個人規模では過剰。
    3. **6-05のホールドアウト**で、assisted記事を一時的に内部リンクから外して全体成果が下がるかを見る（真の増分測定）。
- **具体手順**:
  1. GA4でアフィリエイトリンククリックをイベント化（`outbound_click` の自動収集 + カスタムディメンションでリンク先ドメイン）。
  2. GA4探索 → 経路データ探索で `page_view` → `page_view` → `click` の経路を出す。
  3. BigQuery（GA4 export、無料枠内）で `session_id` ごとの `page_location` 配列を作り、**クリック直前N件のページを "assisted" として記録**。SQLで `ARRAY_AGG(page_location ORDER BY event_timestamp)`。
  4. 記事ごとに `last_click_count` と `assisted_count` の2列を持つ台帳を作る。
  5. **「assisted_count は高いが last_click_count が0の記事」を特定する** → その記事にCTAを追加するか、last-click記事への内部リンクを強化するかを判断。
  6. 施策後は 6-04 のDiDで検証。
- **必要なデータ規模**: **アフィリエイトリンククリックが月30件以上**ないと経路分析の意味が出ない（1経路あたり1件では分布が見えない）。**noe-matchの現状（月クリック4）では完全に不足。**
  - **再評価の閾値: 月間セッション500、アフィリリンククリック30件。**
  - ただし **GA4のイベント設定とBigQuery exportの有効化は今日やるべき**（データは遡及取得できない）。
- **日本での言及度**: **低** `[推定]`。打つ予定だったクエリ: `アフィリエイト ラストクリック 問題 アシストコンバージョン`, `間接効果 記事 貢献度 計測`。日本語のアフィリエイト情報は「どの記事が成果を出したか」をASP管理画面ベースで語るのが標準で、**アシスト記事の貢献を測る方法論はほぼ流通していない**と見込む。GA4の「アシストコンバージョン」という言葉自体はEC文脈で知られているが、アフィリエイトメディアの記事評価に適用する話は稀。
- **noe-match適用度**: **C（分析）／A（データ収集の仕込み）**。理由: 分析に必要なイベント数が全く足りない。しかし **GA4のイベント設定とBigQuery export有効化（無料）は今日やらないと、将来の分析対象データが永久に失われる**。想定工数: GA4イベント設定 **2時間**、BigQuery export有効化 **30分**、分析実装は将来 **4時間**。
- **リスク・反証**: (1) **クロスデバイス・クロスセッションの経路は原理的に追えない。** ユーザーがスマホで読んでPCで申し込むケースはすべて失われる。婚活領域は検討期間が長いのでこの影響が大きい。(2) ITP/クッキー規制により、GA4の `user_pseudo_id` はSafariで7日で切れる。(3) **ルールベース帰属（50/50配分等）は恣意的で、それ自体は因果推論ではない。** 「どの記事を増やすべきか」の意思決定には 6-05 のホールドアウトが必要。(4) BigQuery GA4 export は日次で無料枠内だが、イベント数が増えると課金対象になる。

---

## 6-23. 海外で使われている無料/低額の計測ツールスタック

- **一言で**: 海外の個人〜小規模SEOが実際に使っている、**合計月額ほぼ0円** の計測スタックの構成。
- **海外での出典**:
  - https://www.advancedwebranking.com/blog/gsc-bulk-data-export-bigquery-basics-for-better-data
  - https://trevorfox.com/2023/03/google-search-console-bulk-export-for-bigquery/
  - https://getdadseo.com/blog/export-google-search-console-data-csv-api
  - https://github.com/joshcarty/google-searchconsole （**直接確認済**: `pip install git+https://github.com/joshcarty/google-searchconsole`。クエリビルダ、正規表現フィルタ、searchType（web/news/video/image/**discover**/googleNews）、pandas出力、認証の永続化）
  - https://firstplaceseo.co.uk/technical-seo/free-tools-to-analyse-log-files-and-fix-crawl-waste/
  - https://www.aeripret.com/gsc-data-in-bigquery/
  - https://www.searchenginejournal.com/google-search-console-data-bigquery-enhanced-analytics/496535/
- **スタック構成と費用**:

| ツール | 費用 | 用途 | noe-matchでの位置づけ |
|---|---|---|---|
| **GSC API** | 無料（1日1,200クエリ、1分600） | クエリ×ページ×日次の生データ | 既に稼働中（要改修: 6-09） |
| **GSC Bulk Data Export → BigQuery** | 実質無料（月1TBスキャン/10GBストレージが無料枠） | 匿名化フラグ付き全量、16ヶ月制限突破 | **最優先で導入（6-10）** |
| **`google-searchconsole` (joshcarty)** | 無料（OSS） | GSC APIのPythonラッパー。正規表現フィルタ、Discover次元 | 現在の自前実装から乗り換え候補 |
| **`tfcausalimpact` / `tfp-causalimpact`** | 無料（OSS） | ベイズ構造時系列による効果推定 | 6-02 |
| **`statsmodels` / `scipy` / `prophet`** | 無料（OSS） | 検定・分解・予測 | 6-13, 6-15, 6-16 |
| **`sentence-transformers`** | 無料（OSS） | クエリの意味クラスタリング | 6-11 |
| **Screaming Frog SEO Spider 無料版** | 無料（**500URL上限**） | クロール、内部リンク、メタ情報の一括取得。GSC/GA4 API連携は有料版のみ | **noe-matchは258記事なので500URL上限内に完全に収まる** |
| **Screaming Frog Log File Analyser 無料版** | 無料（**1,000行上限**） | ログ解析 | GitHub Pagesでは生ログが取れないため使えない |
| **GoAccess** | 無料（OSS） | ターミナルでのリアルタイムログ解析 | 同上 |
| **Looker Studio** | 無料 | GSC/GA4/BigQueryを繋いだダッシュボード | **週次KPIの可視化に有効** |
| **GA4 + Data API** | 無料 | 行動データ、AI流入チャネル | 6-17, 6-22 |
| **GA4 → BigQuery export** | 無料枠内 | セッション経路の生データ | 6-22 |
| **Google Trends / `pytrends`** | 無料 | カテゴリ季節性、Share of Search | 6-13（季節性）は今すぐ有効、6-19は将来 |
| **Cloudflare 無料プラン** | 無料 | Bot Analytics（AIクローラー到達） | 6-17, 6-20（導入コストあり） |
| **各LLMのAPI** | 月数百〜2,000円 | Share of Model 計測 | 6-18 |

- **具体手順（導入順序の推奨）**:
  1. **今日**: GSC Bulk Data Export → BigQuery を有効化（6-10）。**1日遅れるごとにデータが永久に失われる。**
  2. **今日**: GA4のAIチャネルグループ設定（6-17）+ アフィリンククリックのイベント化（6-22）。
  3. **今週**: `scripts/fetch_gsc.py` の rowLimit/startRow 修正（6-09）。
  4. **今週**: Screaming Frog 無料版で全258記事をクロールし、内部リンク構造・重複タイトル・メタ情報のベースラインを取る。
  5. **今月**: ベイズ縮小推定CTR（6-14）と MDE 計算（6-15）をKPI台帳に組み込む。
  6. **今月**: Share of Model のプロンプトセット設計と週次実行（6-18）。
- **必要なデータ規模**: **下限なし。全てが小規模サイトで動く。** むしろ「有料ツールを買わない」判断の根拠になる。
- **日本での言及度**: **中（個別ツール）／低（このスタック構成として）** `[推定]`。打つ予定だったクエリ: `無料 SEO 計測ツール BigQuery Looker Studio 構成`, `Screaming Frog 無料版 500URL`。個別ツールの日本語紹介はあるが、**「GSC Bulk Export + BigQuery + Python + Looker Studio で月額ほぼ0円の分析基盤を組む」という構成論を書いた日本語記事は少ない**と見込む。日本語圏では有料SEOツール（ahrefs、Semrush、GRC等）の紹介記事が圧倒的に多く、無料スタックの体系的な提示が薄い。
- **noe-match適用度**: **A**。理由: 既にPython分析基盤とGSC API連携があるため、追加コストがほぼゼロで拡張できる。想定工数: 上記1〜6で合計 **20〜25時間**（うち待ち時間48時間）。**月額コストは LLM API の数百〜2,000円のみ。**
- **リスク・反証**: (1) 無料枠には上限がある。BigQueryは `--maximum_bytes_billed` を設定して事故を防ぐこと。(2) **ツールを増やすこと自体がコスト。** 個人運営で管理できるのは3〜4ツールまで。優先順位を守ること。(3) Screaming Frog無料版はGSC/GA4のAPI連携が有料版限定なので、クロールデータとGSCデータの突合はPythonで自前実装が必要。(4) Looker Studio は BigQuery を直接繋ぐと表示のたびにスキャンが走る。**BIエンジンまたは集計済みテーブルを間に挟むこと。**

---

## 領域6の未解決事項

1. **本レポートの一次ソース確認率が低い。** egress制限により `searchpilot.com`、`developers.google.com`（Search Central公式）、`support.google.com`（GSCヘルプ公式）、`searchengineland.com`、`arxiv.org`、Kevin Indig の Growth Memo に直接アクセスできなかった。**特に SearchPilot の統計手法の詳細（priorの具体的な形、最低必要ページ数）と、Google公式のGSC指標定義の正確な文言は、原典で再確認する必要がある。** 数値に `【要再検証】` を付した箇所は特に。

2. **日本語言及度の検証が2クエリで打ち切られた。** セッション共有のWeb検索予算（200/200）が枯渇。実検索で確認できたのは CausalImpact と CUPED のみ。**残り21手法の「日本での言及度」はすべて推定であり、依頼主自身による検証が必要。** 各項目に「打つ予定だったクエリ」を明記したので、それをそのまま使えば検証できる。

3. **「小規模サイトで統計的にSEO施策を評価する」ことの原理的な可能性が未解決。** 本レポートの計算が示す通り、月278表示・4クリックでは、+20%の効果を検出するのに4.5年、+10%なら17年かかる。**これは手法の選択で解決できる問題ではない。** 残された選択肢は (a) ベイズで不確実性を正直に表示する（6-14）、(b) クラスタ集約で単位あたりのnを稼ぐ（6-11）、(c) 自分でデータを作る手法（6-18のShare of Model）に賭ける、(d) 効果測定を諦めて外部知見のベストプラクティスを実装する期間と割り切る、の4つ。**(d)が現時点で最も合理的である可能性を、依頼主と議論すべき。**

4. **AI流入の "dark traffic" 比率が原理的に測れない。** 「70.6%がDirectに落ちる」という数値の出所と測定方法が確認できていない。この数値が正しければ、**AI経由の影響は事実上ブランド検索（6-19）とShare of Model（6-18）でしか捕捉できない**が、noe-matchはブランドが無名でGoogle Trendsにデータが出ないため、6-19が使えない。**「無名ブランドのAI経由影響をどう測るか」は本レポートで解けなかった。**

5. **Share of Model 計測の統計的妥当性が学術的に未確立。** 「250〜500プロンプト」「30〜50プロンプト」と出典によって10倍の開きがあり、どちらも根拠が示されていない。**LLM出力の分散構造（プロンプト間分散 vs 反復間分散の比率）が分からないと、必要n数を正しく計算できない。** 依頼主が実装する場合、**最初の4週間は「分散構造の推定期間」として、少数プロンプトを高反復（例: 10問×20反復）で回してICC（級内相関）を測ることを推奨する。** これは本レポートの範囲を超える追加調査項目。

6. **婚活・結婚領域の季節性の実データが未収集。** 6-13の季節調整は2年分の履歴を要するが、Google Trends で `婚活` `結婚相談所` `結婚式` の2004年以降の週次指数を取れば、**業界全体の季節パターンは今日から入手できる**。これを取得して noe-match の KPI に季節ベースラインとして組み込む作業が未着手。工数2時間で完了する割に価値が高い。

7. **`scripts/fetch_gsc.py` の実装上の3つの欠損が未修正。** (a) `rowLimit: 500`（最大25,000）、(b) `startRow` によるページネーションなし、(c) 履歴の永続保存なし。**(c)は16ヶ月で取り返しがつかなくなる。** 本レポートの分析手法の大半がこの3点に依存しているが、修正は本レポートの担当範囲外として実施していない。

8. **PDCA凍結の期間長を統計的に決める方法が未定式化。** 6-15のMDE計算を使えば「この効果量を検出するには最低N週の凍結が必要」と逆算できるはずだが、SEOの効果発現遅延（インデックス反映、ランキング再評価）を織り込んだ凍結期間の決め方について、英語圏でも定式化された議論を見つけられなかった。**SearchPilotが「テスト期間は最低2週間、推奨4週間」としているという断片情報はあるが、原典未確認。**

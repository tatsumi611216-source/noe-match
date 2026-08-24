# ツール中心クラスタ設計（2026-08-15 CEO策定）

## 戦略（正本）

**ツールを中心にクラスタを組み、4つの脚で上位表示を取りに行く。**

```
            ┌─ ① 集客記事（検索の入口・需要のある語で取る）
            │
   【ツール】┼─ ② 高単価アフィリ誘導記事（収益の脚）
   （クラスタの核）
            ├─ ③ ツール本体（体験型・滞在と再訪を作る）
            │
            └─ ④ note（外部からの流入・指名検索の種）
```

なぜツールが核か：静的な解説記事は大手と同じ土俵になるが、**体験型ツールは大手が
作らない**（記事量産のラインに乗らないため）。空白はここに開く。

なぜ4本足か：`scripts/article_audit.py` の3観点（①流入 × ②実効単価 × ③接続）に
noteの外部流入を足したもの。**どれか1つがゼロならクラスタ全体がゼロになる。**

---

## クラスタ現況（2026-08-15）

### クラスタA｜ガルガル期・産後 ＝ **集客メイン＋キャッシュ回収**（CEO明示・2026-08-15）

**主目的は集客（到達とLINE@登録）。ただしキャッシュポイントでの回収も行う。**

高単価の婚活系案件を産後文脈に持ち込むのは筋が悪い（読者の目的が違う）。
一方で、産後の生活文脈に自然に合う低単価案件（食材宅配・保険相談・引っ越し）は
すでに置いてあり、これは続ける。**主従を間違えないことだけが条件**——
集客が主、キャッシュが従。逆にすると産後の不安に付け込む導線になる。

| 脚 | 状態 | 実体 |
|---|---|---|
| ① 集客記事 | △ | `garugaru-ki-guide` / `garugaru-ki-itsumade` / `sango-crisis-guide`。**`義母・実母` `ない人` の独立ページが無い**（いずれもサジェスト上位） |
| ② キャッシュ回収 | ○ | ツール3件（Oisix／保険ランドリー／引越し侍）、記事に1〜2件ずつ設置済み |
| ③ ツール | ○ | `tools/garugaru-check`（53問／簡易15問）＋LINE@導線 |
| ④ note | × | 未着手（予定5本） |

**穴は2つ。**

1. ~~LINE導線がツールページにしか無い~~ → **2026-08-15に記事側へ設置済み（add_line_cta.py）。8/23時点でA記事22本すべてにLINE@導線あり**（産後美容2本は8/23に追加）
2. **①のサジェスト上位2語が独立ページになっていない**（`義母・実母` `ない人`）

**KPIの主従：主＝到達・LINE@登録／従＝キャッシュポイント成果。**
収益だけで評価すると誤判定するが、ゼロでよいわけでもない。

### クラスタB｜夫源病・妻源病

| 脚 | 状態 | 実体 |
|---|---|---|
| ① 集客記事 | **×** | 解説記事がゼロ。ツール単独で浮いている |
| ② 高単価誘導 | × | なし |
| ③ ツール | ○ | `tools/fugenbyo-check` / `tools/saigenbyo-check` |
| ④ note | × | 未着手（予定3本） |

**穴：①が完全に空。** サジェストは厚い（`夫源病チェックシート` `妻源病 10の禁句`
がいずれもサジェスト2位）のに、受け皿の記事が無い。
→ **次アクション：①を最優先で埋める。** ツールだけでは指名検索しか拾えない。

### クラスタC｜結婚費用・資金

| 脚 | 状態 | 実体 |
|---|---|---|
| ① 集客記事 | ○ | `kekkon-okane-data` / `kekkon-hiyou-futan`（8/15新規） / `nashikon-data` |
| ② 高単価誘導 | **○** | **ハナユメ（式場見学予約・推定10,000円／1〜2万円帯トップ）** |
| ③ ツール | ○ | `tools/kekkon-shikin-keisanki` / `tools/soudanjo-simulator` |
| ④ note | × | 未着手（予定4本） |

**4本足が最初に揃うクラスタ。** ①③②が既にあり、残りは④のみ。
→ **次アクション：ここを最優先で完成させ、他クラスタの型にする。**

---

## 判断の順序

1. **4本足が揃うクラスタから完成させる**（現状はC）。揃っていないクラスタに
   記事を足しても、収益の脚が無ければ流入は素通りする
2. **①が空のクラスタは①から**（現状はB）。ツール単独は指名検索しか拾えない
3. **②が無いクラスタは、無理に案件を足さない。** 文脈の合わない案件を置くと
   読者の目的とずれ、クラスタ全体の信頼を削る（`agent/affiliate_gaps.md` の原則）
4. **クラスタには役割の違いがある。** 集客装置クラスタ（現状はA）と回収クラスタ
   （現状はC）を同じ物差しで測らない。集客装置を収益で評価すると誤判定する。
   **測るのは、集客装置＝到達とLINE@登録／回収クラスタ＝成果件数。**

## 単価の実測値（`agent/AGENT.md` 台帳より）

| 案件 | 単価 | 使える文脈 |
|---|---|---|
| 白衣コン | 40,000円（提携中最高） | 看護師×婚活のみ（`nurse-guide`） |
| ハナユメ | 推定10,000円 | 式場探し・結婚費用 |
| 引越し侍 | 667円・確定率100% | 同棲・新生活の引っ越し |

案件の優先順位は単価だけで決めない：**期待値＝単価 × 承認率 × 成約しやすさ**
（無料登録＞資料請求＞有料契約）。


---

# 全記事のクラスタ割付（2026-08-16・全185本を棚卸し）

`articles/` の281エントリのうち、**リダイレクト残骸と canonical が他を指す重複を除いた実記事は185本**。
その全部を、**漏れなく・重複なく**クラスタへ割り付けた（1本は1クラスタ。
重複所属を作ると、どのツールへ送るかが記事ごとに決まらなくなる）。

## 割付の原則

**テーマの見た目ではなく「読者が同じ判断をしている段階」で切る。**
たとえば `dousei-kekkon-hikaku`（同棲か結婚か）は同棲の記事だが、
読者がしているのは**生活の立ち上げの判断**なのでBに入る。
逆に `tokyo-guide` はマッチングアプリの記事だが、
読者がしているのは**どの手段で動くかの判断**なのでC系に入る。

## 一覧

| クラスタ | 本数 | 核となるツール | KPI | 備考 |
|---|---|---|---|---|
| **A｜ガルガル期・産後** | 21 | tools/garugaru-check ✅稼働 | 集客（到達・LINE@） | 9月中旬に判定（index≥10/19・表示≥200/月・LINE@≥5/月） |
| **B｜新生活・生活費** | 28 | tools/seikatsuhi-simulator ✅稼働 | 回収（成果件数） | K（同棲か結婚か 3本）を統合。判断段階が同じ |
| **C｜婚活の手段選び** | 24 | tools/konkatsu-type-shindan ✅本日公開 | 回収（成果件数） | ④noteが婚活記録1語のみ＝要検証 |
| **C-sub｜地域** | 10 | Cの診断に地域入力で接続 | 回収 | 新規ツール不要。Cのサテライト |
| **D｜アプリの選定** | 23 | tools/app-kekkonritsu-data（E核を共用・8/23に23本接続。新規ツールは案件が薄いため作らない） | 回収（成果件数） | 最大の未整理帯。個別ガイド6＋比較5＋料金/会員データ |
| **E｜アプリの実績データ** | 22 | tools/app-kekkonritsu-data ✅2026-08-22公開 | 回収（成果件数） | 公表値と非公表を並べる＝大手がやらない切り口 |
| **F｜アプリ運用（プロフィール〜デート〜安全）** | 26 | 【新規】プロフィール自己診断 | 集客（到達・LINE@） | 旧F/G/Hを統合。26本 |
| **J｜結婚式・結婚準備** | 19 | tools/kekkon-shikin-keisanki（既存・8/23にハナユメ結果連動を追加） | 回収（成果件数） | noteの反応が最良帯（花嫁120.5・新婚78.5） |
| **L｜離婚・別居** | 6 | 【要検討】別居中の生活費計算機 | 回収 | ★台帳のYMYL上限8本。25本にはできない |
| **M｜キャリア・働き方** | 3 | 未定 | 回収 | 転職アフィリ5サイトとの接続を検討 |
| **N｜妊活** | 4 | なし（凍結） | — | 台帳でインデックス率0%・A8該当案件なしと実測済 |

**合計185本 — 未割付ゼロ・重複所属ゼロ（検算済み）。**

## 稼働状況

- **稼働中は3クラスタ（A・B・C）＝73本。** 残る112本は、まだツールに接続されていない
- **ツールが必要なのは4つ**（D・E・F・J）。C-subとKは既存ツールに接続するだけで足りる
- **L（離婚・別居）は25本にできない。** 台帳 `AGENT.md` のYMYL上限（5〜8記事）に既に達しているため、
  拡張するなら上限ルールの改定がCEO承認事項になる
- **N（妊活）は凍結。** 台帳でインデックス率0パーセント・A8に該当案件なしと実測済み

## 統合した小クラスタ

| 元 | 統合先 | 理由 |
|---|---|---|
| K｜同棲・結婚のタイミング（3本） | **B** | 判断の段階が同じ（生活の立ち上げ） |
| G｜デート（9本）・H｜安全（6本） | **F** | いずれも「アプリを使い始めたあとの運用」。単体では25本に届かない |

## 詳細

### A｜ガルガル期・産後（21本）

`garugaru-ki-guide` `garugaru-ki-itsumade` `garugaru-otto-taiou` `garugaru-nai-hito` `garugaru-gibo-jitsubo` `garugaru-doukyo` `garugaru-ueno-ko` `garugaru-otto-genkai` `garugaru-sangoutsu-chigai` `sango-crisis-guide` `sango-iraira` `sango-kaji-buntan` `sango-otto-kirai` `sango-rikon` `sango-satogaeri` `satogaeri-shinai` `shinseiji-menkai` `maternity-blue-chigai` `futarime-sango` `gijikka-ikitakunai` `ikukyu-fuufu-doji`

### B｜新生活・生活費（28本）

`dousei-hajimekata` `shinkon-seikatsu-guide` `shinkon-koteihi-minaoshi` `shinkon-net-kaisen-dandori` `futari-hikari-kaisen` `futari-sumaho-minaoshi` `kazoku-simhikaku` `kekkon-hoken-minaoshi` `futari-kouza-kanri` `kekkon-chokin-mokuhyou` `shinkyo-kagu-yosan` `kaden-rental-vs-kounyu` `tomobataraki-shokuji-data` `kekkon-hiyou-futan` `futari-kounetsuhi` `kakeibo-app-fuufu` `sengyoshufu-seikatsuhi` `shinkon-hojokin` `tokyo-futari-seikatsuhi` `dousei-nimotsu-trunkroom` `keiyaku-jisshitsu-wana` `kekkon-jutaku-loan` `yachin-credit-shiharai` `fuufu-credit-kanri` `shinkon-osechi` `dousei-kekkon-hikaku` `dousei-kekkon-timing` `dousei-kaisho`

### C｜婚活の手段選び（24本）

`soudanjo-hikaku` `agency-vs-app` `app-plus-agency` `app-tsukare-guide` `konkatsu-roadmap` `konkatsu-soudan-saki` `konkatsu-party-guide` `nurse-guide` `nurse-konkatsu-soudanjo` `civil-servant-guide` `engineer-guide` `otaku-konkatsu` `pet-konkatsu` `pocchari-konkatsu` `seishain-igai-guide` `hitomishiri-guide` `usuge-konkatsu-eikyou` `over50-guide` `batsuichi-guide` `40s-men` `35s-strategy` `tokyo-guide` `osaka-guide` `kyoto-guide`

### C-sub｜地域（10本）

`nagoya-guide` `fukuoka-guide` `sapporo-guide` `kobe-yokohama-guide` `saitama-chiba-guide` `sendai-hiroshima-guide` `shizuoka-niigata-guide` `okinawa-guide` `inaka-guide` `kokusai-kekkon-guide`

### D｜アプリの選定（23本）

`matching-app-ranking` `price-comparison` `compare-price` `compare-popular` `compare-konkatsu` `compare-20s` `omiai-vs-pairs` `tapple-vs-pairs` `with-vs-pairs` `youbride-marrish-hikaku` `pairs-guide` `omiai-guide` `with-guide` `tapple-guide` `youbride-guide` `marrish-guide` `bachelor-date-guide` `free-vs-paid` `matching-dansei-cost-data` `matching-josei-cost-data` `members-data` `age-data` `kaiin-age-cross-data`

### E｜アプリの実績データ（21本）

`success-rate-data` `success-stories` `appkon-wariai-data` `pairs-marriage-data` `pairs-kaiin-data` `omiai-30s-women-data` `tapple-seriousness-data` `with-seriousness-data` `youbride-seikon-data` `zexy-enmusubi-data` `marrish-saikon-data` `kekkon-madeno-kikan-data` `hatsushon-nenmei-data` `renkatsu-vs-konkatsu` `20s-guide` `student-guide` `late-20s-strategy` `30s-konkatsu` `40s-guide` `time-management` `faq-troubleshooting`

### F｜アプリ運用（プロフィール〜デート〜安全）（26本）

`photo-tips` `profile-photo` `profile-text` `konkatsu-photo-guide` `mens-make-konkatsu` `message-strategy` `line-exchange` `pairs-men` `pairs-women` `with-women` `women-strategy` `first-date-guide` `first-date-spot` `date-plan-2kaime` `ouchi-date-guide` `ouchi-date-sakuhin` `amenohi-date-guide` `date-sakuhin-ng` `sakuhin-kachikan` `enkyori-renai-guide` `anti-fraud` `fraud-detection` `fraud-statistics` `safety-guide` `privacy-protection` `kekkon-sokou-chousa`

### J｜結婚式・結婚準備（19本）

`shikijo-erabi-guide` `kekkon-okane-data` `nashikon-data` `propose-guide` `konyaku-yubiwa-data` `pair-ring-guide` `christmas-propose-gyakusan` `yokohama-propose-spot` `maedori-photo-guide` `bridal-esthe-guide` `bridal-inner-guide` `kekkonshiki-isho-rental` `gosyugi-shiharai-houhou` `kekkon-uchiiwai-guide` `kekkon-houkoku-nengajou` `nyuseki-2027-guide` `kisei-kekkon-aisatsu` `shinkon-ryokou-credit` `kinsen-kachikan-check`

### L｜離婚・別居（6本）

`rikon-junbi-jyunban` `rikon-okane-genjitsu` `koninhiyou-guide` `tantei-erabikata` `uwaki-chousa-kiso` `tanshin-uwaki-mikiwame`

### M｜キャリア・働き方（3本）

`kekkon-tenshoku-guide` `tenshoku-riyu-honne` `kosodate-zaitaku-guide`

### N｜妊活（4本）

`dansei-ninkatsu-guide` `mitas-formen-kuchikomi` `mitocore-kuchikomi` `myseed-kuchikomi`



---

## D・Fはクラスタを作らない（2026-08-16 CEO判断・GSC実測にもとづく）

### 決定

- **E（アプリの実績データ）を軸のクラスタにする**
- **D（アプリの選定）・F（アプリ運用）は、Eのサブクラスタとして扱う**（2026-08-16 CEO指示）。
  独立したクラスタにはせず、ツールもnoteの入口ワードも持たせない
- D・Fの49本は**削除も改稿もしない**。既存の案件設置もそのまま

### サブクラスタの定義（この扱いを他クラスタにも適用する）

**サブクラスタ＝4本足のうち①（集客記事）だけを担い、②③④を親に委ねる記事群。**

| | 親クラスタ | サブクラスタ |
|---|---|---|
| ① 集客記事 | 持つ | **持つ（これだけ）** |
| ② キャッシュ回収 | 持つ | 既存の設置は残すが、新規は親の判断に従う |
| ③ ツール | **持つ（核）** | 持たない。親のツールへ送る |
| ④ note入口ワード | 持つ | 持たない |

これにより「25本＝1クラスタ」の原則は保たれる。
**親Eが25本、サブD・Fが49本で、ツールに接続する記事は合計70本**になる。
サブを別クラスタとして数えないのは、ツールとnoteを持たないため
クラスタとしての成立条件（4本足）を満たさないから。

| | 本数 | 役割 |
|---|---|---|
| **E（親）** | 21（→25へ） | 検証系の主戦場。ツールとnoteを持つ |
| **D-sub（選定）** | 23 | 比較・ランキング・個別ガイド。Eへ送る |
| **F-sub（運用）** | 26 | プロフィール・デート・安全。Eへ送る |
| 合計 | **70** | ツール1本に接続する |

C-sub（地域10本）も同じ扱い。既に「Cの診断に接続」としており、定義が揃った。

### 根拠：経過日数をそろえて比べると差が決定的

| クラスタ | 本数 | 公開からの中央値 | 12位以内 | クリック |
|---|---|---|---|---|
| J 結婚式 | 19 | 21日 | 6本 | 0 |
| B 新生活 | 28 | 21日 | 6本 | 1 |
| E 実績データ | 21 | 43日 | 6本 | **11** |
| **D アプリの選定** | 23 | **68日** | **1本** | 1 |
| **F アプリ運用** | 26 | **68日** | 3本 | 2 |

**D・FはJ・Bの3倍の時間があって、結果は下**。時間の問題ではない。
`compare-price` `compare-popular` `compare-konkatsu` `pairs-guide` `with-guide`
`tapple-guide` `price-comparison` `members-data` は**68日経って表示ゼロ**。

### なぜEだけ勝てるのか

勝っているクエリの形が違う。

| クエリ | 記事 | 順位 |
|---|---|---|
| with 結婚率 | `with-seriousness-data` | **5.9位・5クリック** |
| タップル 真剣度 | `tapple-seriousness-data` | **7.2位・2クリック** |
| ユーブライド 成婚 | `youbride-seikon-data` | **7.0位・1クリック** |
| マリッシュ 再婚 | `marrish-saikon-data` | 8.5位 |
| アプリ婚 割合 | `appkon-wariai-data` | 18.2位・1クリック |

**固有名詞 × 公表数値の検証**。
「どのアプリがおすすめか」では勝てないが、「そのアプリの成婚率は公表されているのか」では勝てる。
理由は `blank-spot-theory` の中核の問いそのもの——
**アプリを紹介して稼ぐ媒体は、そのアプリの数値を批判的に検証する動機を持たない。**
比較・ランキング・プロフィール・デートは、その媒体群が最も金をかけている場所なので勝てない。

### 判定を誤らせかけた点（記録）

1. **本数で優先順位を付けかけた。** D=23本と最大だったため「Dが最優先」と一度判断したが、
   GSCを見ると最下位だった。**本数は資産の大きさであって、勝てる見込みではない**
2. **Jを「取れていない」と誤判定した。** 145表示0クリックだけを見た結果で、
   経過21日を考慮していなかった。Eの主力が5.9位に育つのに41日かかっている。
   **クラスタの評価は、公開からの日数をそろえてから行う**


## Eのツール：競合実査（2026-08-16）

**前提の訂正。** 「紹介して稼ぐ媒体は数字を検証できない」と一度書いたが、**誤り**。
実査したところ、記事レベルでは既に競合が存在する。彼らはむしろ差別化のために書く。

| 確認したこと | 結果 |
|---|---|
| 累計会員数と稼働の違いに踏み込んでいるか | **踏み込んでいる**（出会いコンパス：タップル2,300万人／月間37万人、with 1,500万人／月間54万人と明記） |
| 成婚率の定義問題（分母・成婚退会の不在） | 複数媒体が扱っている |
| **出典URLと取得日の明記** | **なし**（ペアーズ「2,700万人以上(2026年4月時点)」＝時点のみ、タップル「2,300万人以上」＝日付すらない） |
| **ツール化・インタラクティブ機能** | **なし** |
| **中立性** | **なし**（招待コード・アフィリリンクあり。数字の批判は他社を落として自社の推しを上げる用途） |
| 非公表数値の扱い | 「非公開」と書く程度。**数字の定義（分母・集計期間・自己申告か）には踏み込まない** |

### 結論：空白は残っているが、当初想定より狭い

差別化の軸は「誰も書いていない」ではなく **「検証の作法」**。

- 出典URLと**取得日**を全件明記する
- 全社を**同じ条件**で並べる（一部だけ厳しく見ない）
- **推奨しない**（どれが良いかを言わない。これが中立性の担保）
- 数字の**定義**まで書く（分母・集計期間・自己申告か）

**制約：取得日が古くなると価値が落ちる。継続更新が前提のツールであり、作って放置できない。**
更新頻度を維持できないなら、このツールは作らないほうがよい。

### 勝機の裏付け

E記事は既にこの大手比較サイト群に勝っている
（「with 結婚率」5.9位・「タップル 真剣度」7.2位・「ユーブライド 成婚」7.0位）。
**個別アプリ名×数値という粒度では、比較サイトのカテゴリページより具体的**だから取れている。
ツールはこの粒度を集約する形になる。

参照：出会いコンパス https://deai.app-liv.jp/archive/134185/ ／
マッチングアプリ比較ナビ https://matching-navi.jp/columns/matching-app-statistics-2026/


---

## バックログ（着手は後日・2026-08-16 CEO指示）

### M｜キャリア・働き方 ＝ **ツール複数・職種別展開**

現状3本（`kekkon-tenshoku-guide` `tenshoku-riyu-honne` `kosodate-zaitaku-guide`）。
**1クラスタ1ツールではなく、職種別に複数のツールを載せる**構成で展開できる（CEO着想）。

なぜこの型が有望か：台帳「新規記事はこの2型に限る」（2026-08-02制定・上位ルール）で
**属性型のインデックス率は100%**（地域型91%）と実測されている。**職種別＝属性型そのもの**。
Cクラスタの属性群（看護師・公務員・エンジニア）が既にGSCで表示を取っているのも同じ理由。

想定されるツールの例（いずれも未実測・着手時にサジェストを測ってから決める）:
- 職種別の「結婚を機に転職すべきか」判断ツール（勤務地・夜勤・転勤の有無から）
- 職種別の年収と生活費の突合（Bの生活費シミュレーターと接続）
- 育休・時短が取りやすい職種の条件整理

**接続先の検討事項**：別ドメインで転職アフィリ5サイト（看護・薬剤師・介護・エンジニア・保育士）を
運用中。**noe-matchから外部の自社サイトへ送るかは別途判断**（ドメインをまたぐ導線は
被リンクの扱いと読者体験の両面で影響があるため、送る前に設計する）。

**着手時期：未定（CEO「おいおいでいい」）。他クラスタを優先する。**

※ 2026-08-22 追記：`with-nenreiso-data`（8/17公開）が未割付だった。**E** に割り付ける（withの公表年齢層データ＝型A）。

## ツールの命名原則（2026-08-23・実測）

表示が立っているツールは nyuseki-calendar（「入籍日 カレンダー」サジェスト10件）と garugaru-check だけで、
「〜計算機」「〜シミュレーター」と機能名で命名した6本は、その語のサジェストが0〜1件＝誰も検索していなかった。
**ツール名は機能ではなく、検索される問い（〜はいくら？／平均／相場／成婚料）で付ける。** 6本を改名済み。効果は9/7の週次GSCで見る。


## 保活ツール（2026-08-24新設）
- /tools/hoikuen-tensu-nerima/ 練馬区 保育園点数計算＆ボーダー逆引き。区公式R8指数表＋令和8年4月1次の園別最低指数204園収録。産後クラスタ（sango-recovery-check／sango-kaji-buntan）と相互導線。横展開候補＝川崎市（ランク制・要ロジック分岐）。データ正本はscratchpad/nerima/{kijun,border}.json→再取得時は区公式PDF。

## 子育て制度クラスタ（2026-08-25新設）｜こども誰でも通園制度

- `/tools/daredemo-tsuen-jichitai/` **こども誰でも通園制度 自治体別ナビ**（**東京23区 全区＋国基準の24区分**・8/25に6区→23区へ拡張）。
  自治体を選ぶと上限時間・利用料・予約の経路・申込の入口が出る。使いたい回数から枠に収まるかも判定。
- **選定の根拠（実測 2026-08-25）**：サジェストは自治体名が8語（渋谷/江戸川/品川/世田谷/足立…）＝地域展開でクラスタが組める。
  SERP1ページ目は自治体公式・localgov・noteのみで**器具（比較ツール）ゼロ**。制度は2026年度から本格実施＝これから検索が伸びる。
  勝ち筋の3条件（送客に繋がらない／年度更新が要って量産ラインに乗らない／器具が空いている）を全て満たす。
- **決定的な差**：上限が月10時間〜**大田区160時間（条件つき・国10＋区150、同一施設で継続利用する場合）**と最大16倍開いており、横断で比較できる場所が存在しない。無条件の最大は渋谷64時間。上乗せ確認は11区（大田/渋谷/世田谷/練馬/江東/品川/港/江戸川/中央/豊島/葛飾）。
- **未確認2区**：中野区・荒川区は令和8年度の公表を確認できず（ページに明示）。再確認の宿題。葛飾・新宿・文京は上限時間そのものが非公表（葛飾は月48,000円という金額上限で運用）。
- 導線：産後・育休クラスタ5本（ikukyu-fuufu-doji / sango-kaji-buntan / satogaeri-shinai / sango-crisis-guide / futarime-sango）から設置済み。
  アンカーは検索語入り（8/24の実測でツール名アンカーはクエリ信号を渡さないと判明したため）。
- 横展開：23区は完了（8/25）。次は政令市（横浜・川崎・さいたま・千葉・大阪・名古屋・福岡・札幌）。データの正本は各区公式ページ（build_daretsu_navi.py の CITIES に出典URLと確認日を保持）。
  **年度替わりに再確認が必要**（上乗せ枠は年度予算で動く）。
- 未着手の脚：①集客記事0本 ②note 0本 ③高単価アフィリなし（この領域は集客の脚と割り切る）。

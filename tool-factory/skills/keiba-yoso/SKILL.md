---
name: keiba-yoso
description: >
  競馬予想エージェントスキル。中央競馬（JRA）と地方競馬（NAR）の両方に対応。
  netkeiba.comからブラウザ経由で出馬表・オッズ・過去成績データを取得し、
  各馬の期待値（EV = 推定勝率 × オッズ - 1）を計算してレースを選定・予想する。
  「競馬予想」「レース予想」「出馬表」「馬券」「今日の競馬」「明日のレース」
  「大阪杯」「地方競馬」「期待値」など、競馬に関するあらゆるリクエストで必ずこのスキルを使うこと。
  結果の突合・振り返り分析もこのスキルの範囲。
---

# 競馬予想エージェント（EV計算対応版）

JRA中央競馬・地方競馬（NAR）の予想を、netkeiba.comからリアルタイムデータを取得して行う。
各馬の過去成績から期待値（EV）を計算し、根拠のある予想とレース選定を実現する。

## 期待値（EV）の考え方

```
EV = 推定勝率 × 単勝オッズ - 1

例）勝率30%・オッズ3.0倍 → EV = 0.30 × 3.0 - 1 = -0.10  （テイクレートより良い）
例）勝率40%・オッズ3.0倍 → EV = 0.40 × 3.0 - 1 = +0.20  （理論的プラス期待値）
```

- 日本の馬券はテイクレート約25%なので、ランダム購入のEV ≈ -0.25 がベースライン
- **EV > -0.10** → 妙味あり（平均より有利な賭け）
- **EV > 0.00** → 理論的プラス期待値
- 「期待値の高いレース」= 複数頭にEV妙味がある＝レースEVスコアが高いレース

**推定勝率の求め方**: 各馬のnetkeiba過去成績ページから直近N走の着順を取得し、
同馬場・近似距離（±300m）に絞って勝率・複勝率を算出する。

---

## ブラウザデータ取得のルール

netkeibaからデータを取得する際のツール使い分け:

| サイト | `javascript_tool` | `find` + `read_page` | 推奨 |
|---|---|---|---|
| race.netkeiba.com（レース一覧・出馬表） | 動作する | 動作する | `javascript_tool` |
| nar.netkeiba.com（レース一覧・出馬表） | 動作する | 動作する | `javascript_tool` |
| db.netkeiba.com（馬の過去成績） | **動作しない** | 動作する | `find` + `read_page` |

`db.netkeiba.com` は `javascript_tool` でスクリプトを実行してもundefinedや空が返る。
理由は不明だがサイトのCSP等の制約と思われる。このサイトでは必ず以下の手順を使う:

### db.netkeiba.comでの過去成績取得手順

```
1. navigate で https://db.netkeiba.com/horse/{horse_id} を開く
2. find で "db_h_race_results" を検索 → ref_id を取得
   （テーブルのIDが "db_h_race_results_tb" の場合もある）
3. read_page で ref_id を指定して読み取る（depth=2, max_chars=70000）
4. 出力をファイル保存（1馬1ファイル: {horse_id}.txt）
5. parse_horse_results.py でパース → JSON化
```

`get_page_text` はHTMLのゴミデータが大量に含まれるため使わない。
`read_page` のAccessibility Tree出力は構造が3パターンあり、
バンドル済みの `scripts/parse_horse_results.py` が自動判定してパースする（後述）。

---

## 開催モード（平日 vs 土日）

| 曜日 | 対象 | 予算 | 出力ファイル |
|---|---|---|---|
| **月〜金（平日）** | NARのみ | ¥10,000 | `{日付}_nar_report.html` |
| **土・日（週末）** | NAR + JRA 両方 | NAR ¥10,000 + JRA ¥10,000 | `{日付}_nar_report.html` + `{日付}_jra_report.html` |

- 月曜はJRA開催なし。必ずNARを確認する。
- 週末はStep 1〜6をNAR・JRA**それぞれ独立して**実行し、最終的に2本のHTMLレポートを生成する。
- 予算は各サイト独立（混ぜない）。NAR 1万 + JRA 1万 = 合計2万。

---

## データ取得ワークフロー（全体像）

```
[平日モード: NAR]  /  [週末モード: NAR → JRA の順に実施]

Step 1: 全開催場のレース一覧を取得（JRA + NAR全場）
  ↓ 候補スコアリング（定量基準）→ 上位8本を候補に
Step 2: 候補8レースのshutubaを取得 + horse ID抽出
  ↓ Stage 1: オッズ分布スコアで3〜5レースに絞り込み
  ↓ Stage 2: 馬フィルタ（EV計算不能な馬を除外して取得対象を絞る）
Step 3: 絞ったレースの対象馬・過去成績ページを取得
  ↓ 差分キャッシュ活用（前日データがあれば再利用）
  ↓ parse_horse_results.py でパース → JSON化
Step 4: calc_ev.py で期待値計算 → レース最終選定（上位5レース）
  ↓
Step 5: 予想出力 + portfolio.py でHalf-Kelly馬券ポートフォリオ構築
  ↓
Step 6: generate_report.py で美麗HTMLレポート生成 → outputs/に保存
```

**「全レース表は必要か？」の答え**:
- 全レースのshutubaは不要。Step 1のスコアリングで上位8本に絞れる。
- Step 3で必要なのは「各馬のhorse page（個別成績ページ）」であり、追加のレース表ではない。
- 馬フィルタ後の取得数 = 絞ったレース × フィルタ後頭数（例: 4レース×8頭 = 32ページ）が現実的な上限。

---

## Step 1: 全開催場のレース一覧を取得

### 1-A: JRAとNARを両方取得する

その日の全開催場を必ず確認する。**JRAとNARは別サイトのため両方を開くこと。**

| 種別 | URL |
|---|---|
| JRA | `https://race.netkeiba.com/top/race_list.html?kaisai_date=YYYYMMDD` |
| NAR（地方全場） | `https://nar.netkeiba.com/top/race_list.html?kaisai_date=YYYYMMDD` |

NARの1ページには**その日の全地方競馬場**（水沢・川崎・船橋・大井・浦和・名古屋・笠松・園田・姫路・高知・佐賀など）が一覧表示される。JRAが開催なし（月曜など）でもNARを必ず確認する。

**抽出用JavaScript（レース一覧 + 開催場名）:**
```javascript
const allAnchors = document.querySelectorAll('a[href*="race_id="]');
const seen = new Set();
const races = [];
allAnchors.forEach(a => {
  const href = a.getAttribute('href') || '';
  const match = href.match(/race_id=(\d+)/);
  if (match && !seen.has(match[1])) {
    seen.add(match[1]);
    const text = a.textContent.trim().replace(/\s+/g, ' ').substring(0, 80);
    if (text.length > 2) races.push(match[1] + '|' + text);
  }
});
const headers = document.querySelectorAll('.RaceList_DataHeader');
const venues = [];
headers.forEach(h => venues.push(h.textContent.trim().replace(/\s+/g, ' ')));
'VENUES:\n' + venues.join('\n') + '\nRACES:\n' + races.join('\n');
```

結果をファイル `{日付}_jra_races.txt` / `{日付}_nar_races.txt` に保存する。

### 1-B: 候補スコアリング（定量基準）

JRA・NAR合わせて**全レースに以下のスコアを計算**し、上位8本を候補とする。感覚や印象での選定は禁止。

| 基準 | 点数 | 判断方法（レース一覧の表示から） |
|---|---|---|
| 重賞（GⅠ〜GⅢ・地方重賞） | +5 | レース名に「GⅠ/GⅡ/GⅢ」「重賞」「グランプリ」 |
| 特別競走（固有名詞あり） | +3 | レース名に「賞」「杯」「特別」「ステークス」「トロフィー」 |
| クラス A以上・OP | +2 | レース名・条件欄に「A」「OP」「オープン」 |
| クラス B | +1 | 〃「B」 |
| クラス C以下 | +0 | 〃「C」 |
| 頭数 9〜14頭 | +2 | レース一覧の頭数 |
| 頭数 7〜8 または 15〜16頭 | +1 | 〃 |
| 頭数 6頭以下 または 17頭以上 | +0 | 〃 |
| 距離 1400m〜2000m | +1 | レース一覧の距離表示 |
| 発走が現在時刻より後（未発走） | +1 | 発走時刻を確認 |

スコアを計算してファイル `{日付}_race_scores.txt` に保存する形式:
```
race_id|スコア|レース名|頭数|距離|発走時刻|競馬場
202645040611|9|疾風迅雷賞(A2)|9頭|ダ900|20:15|川崎
202636040612|7|桜並木賞(B1)|10頭|ダ1400|18:15|水沢
...
```

**上位8本のrace_idをStep 2に渡す。**

---

## Step 2: 出馬表の取得 + 馬フィルタ

**URL:**
```
https://race.netkeiba.com/race/shutuba.html?race_id={RACE_ID}
```
地方の場合: `https://nar.netkeiba.com/race/shutuba.html?race_id={RACE_ID}`

**抽出用JavaScript（出馬表 + Horse ID）:**
```javascript
const rows = document.querySelectorAll('.HorseList');
const horses = [];
rows.forEach(row => {
  const tds = row.querySelectorAll('td');
  if (tds.length < 5) return;
  const waku = tds[0]?.textContent?.trim() || '';
  const umaban = tds[1]?.textContent?.trim() || '';
  const horseLink = row.querySelector('.HorseName a');
  const name = horseLink?.textContent?.trim() || '';
  const horseHref = horseLink?.getAttribute('href') || '';
  const horseIdMatch = horseHref.match(/horse\/(\d+)/);
  const horseId = horseIdMatch ? horseIdMatch[1] : '';
  const sexAge = tds[4]?.textContent?.trim() || '';
  const kinryo = tds[5]?.textContent?.trim() || '';
  const jockey = row.querySelector('.Jockey a')?.textContent?.trim() || '';
  const trainer = row.querySelector('.Trainer a')?.textContent?.trim() || '';
  const oddEl = row.querySelector('.Odds') || row.querySelector('[class*="Odds"]');
  const odds = oddEl?.textContent?.trim() || '';
  if (name) horses.push([waku, umaban, name, horseId, sexAge, kinryo, jockey, trainer, odds].join('|'));
});
const raceInfo = document.querySelector('.RaceList_Item02')?.textContent?.trim()?.replace(/\s+/g, ' ') || '';
const raceName = document.querySelector('.RaceName')?.textContent?.trim() || '';
raceName + '\n' + raceInfo + '\n' + horses.join('\n');
```

> 出力フォーマット: `枠|馬番|馬名|horseId|性齢|斤量|騎手|調教師|オッズ`
> ファイルに保存: `{race_id}_shutuba.txt`

### Stage 1: オッズ分布スコアで候補レースを絞る

5〜8レースのshutubaを取得したら、オッズ分布でスコアリングして3〜5レースに絞る:
- 1番人気が1.1〜1.5倍の断然人気 → **低スコア**（EV計算しても旨みが薄い）
- 2〜5倍台が複数頭いる接戦 → **高スコア**（複数頭にEV妙味が生まれやすい）
- 8倍以上の馬が多数で1強構図 → **中スコア**（1番人気EVが高ければ狙える）

### Stage 2: 馬フィルタ（過去成績取得の対象を絞る）

**取得対象は「1〜3番人気のみ」。4番人気以下は除外する。**

理由: EV計算で妙味が出るのは実力と市場評価が乖離している馬であり、
その大半は1〜3番人気の範囲に収まる。4番人気以下は過去成績データが少なく
勝率推定の精度も低いため、取得コストに見合わない。

出馬表から人気順（単勝オッズの低い順）を取得し、上位3頭のhorse_idのみ
過去成績ページを取得する。

| 条件 | 処理 |
|---|---|
| 1〜3番人気（単勝オッズ上位3頭） | 過去成績を取得してEV計算 |
| 4番人気以下 | スキップ（レポートに「データ除外」と表記） |
| オッズ未表示（「---」） | スキップ（EV計算不可） |

これにより1レースあたりの取得対象を最大3頭に固定でき、
データ取得時間を60〜70%削減できる。

---

## Step 3: 各馬の過去成績取得

### 差分キャッシュ（前日データの再利用）

過去成績データは馬固有のもので、日をまたいでも大きくは変わらない。
前日（または直近）のキャッシュファイル `{日付}_nar_cache.json` / `{日付}_jra_cache.json` が
outputs/ にあれば、同じhorse_idの馬のpast_resultsを再利用できる。

**再利用の手順:**
1. 前日のキャッシュJSONを読み込む
2. 今日の対象horse_id一覧と照合
3. 一致する馬は前日のpast_resultsをそのまま使用（ただし前日に出走していた場合は再取得）
4. 新しい馬だけブラウザで取得

キャッシュの鮮度は3日を目安とする。3日以上前のデータは再取得が望ましい。

### Horse page取得手順（db.netkeiba.com）

**URL:** `https://db.netkeiba.com/horse/{horse_id}`
（JRA・NARとも同じURL。地方馬も `db.netkeiba.com` で取得できる）

db.netkeiba.comでは `javascript_tool` が動作しないため、以下の手順で取得する:

```
1. navigate "https://db.netkeiba.com/horse/{horse_id}"
2. find "db_h_race_results"  →  ref_id を控える
3. read_page ref_id depth=2 max_chars=70000
4. 出力テキストをファイル保存: past_results/{horse_id}.txt
```

**注意点:**
- `find` で見つからない場合は "db_h_race_results_tb" や "レース成績" で再検索
- `read_page` の depth=2 で50000字を超える馬がいる（重賞馬など出走数が多い）ので max_chars=70000 を指定
- 出力がJSON overflow（ファイルに書き出された場合）は、そのファイルを `json.load` して `type=='text'` の要素からテキストを抽出
- ページ全体のATが返ってきた場合（先頭が `link "スマートフォン版へ"` など）は、`find` からやり直してテーブルのref_idを正確に指定する

### ATデータのパース

`read_page` の出力はAccessibility Tree（AT）形式で、3つのパターンがある:

1. **AT形式**（最も一般的）: `link "2024/03/15"`, `generic "ダ1200"` のようなタグ付き
2. **プレーンテキスト形式**: 各フィールドが1行ずつ並ぶ（日付が単独行）
3. **CSV形式**: カンマ区切りの1行1レース

バンドル済みの **`scripts/parse_horse_results.py`** が3形式を自動判定してパースする:

```bash
# 単一ファイル
python3 SKILL_DIR/scripts/parse_horse_results.py past_results/2022107209.txt

# ディレクトリ内の全ファイル一括パース → all_past_results.json 出力
python3 SKILL_DIR/scripts/parse_horse_results.py past_results/ --output all_past_results.json
```

出力JSON形式（1馬分）:
```json
{
  "horse_id": "2022107209",
  "results": [
    {
      "date": "2024-03-15",
      "venue": "川崎",
      "race_name": "疾風迅雷賞",
      "distance": 900,
      "track": "ダ",
      "finish": 1,
      "time": "0:54.2",
      "margin": "-0.3",
      "last_3f": "37.8",
      "odds": 2.3,
      "jockey": "笹川翼",
      "passing": "1-1",
      "weight": 480,
      "weight_diff": -2
    }
  ]
}
```

**勝敗の判定ルール（AT形式）:**
- `link "(馬名)"` のように括弧付きの馬名リンクがある → この馬が勝った（finish=1）
- margin（着差）が負の値 → この馬が勝った（finish=1）
- 括弧なし＋margin正値 → 敗戦

### 並行取得の安定化ルール

過去成績の取得を複数のサブエージェントで並行実行する場合:

1. **1馬 = 1ファイル**: `past_results/{horse_id}.txt` に個別保存。共有JSONへの同時書き込みは禁止
2. **最大5馬/エージェント**: 1つのエージェントに割り当てる馬は最大5頭
3. **統合は全完了後**: 全エージェント完了後に `parse_horse_results.py` で一括パース
4. **フェイクデータ検知**: パース結果が全レコード finish=0 かつ odds=null ばかりの場合はパース失敗を疑う。元ファイルの先頭10行を確認して形式を特定し直す

---

## Step 4: 期待値計算（calc_ev.py）

各レースの入力JSONを作成してスクリプトを実行する。

**スクリプトのパス:** `{このSKILL.mdのディレクトリ}/scripts/calc_ev.py`

**入力JSON形式（{race_id}.json として保存）:**
```json
{
  "race_id": "202645040611",
  "race_name": "疾風迅雷賞(A2)",
  "dist": "ダ900",
  "horses": [
    {
      "umaban": "4",
      "name": "ハーフブルー",
      "horse_id": "2022107209",
      "win_odds": 2.3,
      "results": [
        {"rank": "1", "dist": "ダ1200", "odds": "4.0", "pop": "2"},
        {"rank": "4", "dist": "ダ1200", "odds": "4.6", "pop": "3"}
      ]
    }
  ]
}
```

parse_horse_results.py の出力からJSONを生成する際:
- `finish` → `rank`（1なら"1"、0なら着順不明として"0"）
- `track` + `distance` → `dist`（例: "ダ1200"）
- `odds` → `odds`（文字列に変換）

**実行コマンド:**
```bash
# 単一レース分析
python3 SKILL_DIR/scripts/calc_ev.py race_202645040611.json

# 複数レース一括比較 → どのレースを予想するか決める
python3 SKILL_DIR/scripts/calc_ev.py race1.json race2.json race3.json race4.json race5.json
```

**出力の読み方:**
- **レースEVスコア**: 上位3頭のEV平均。高いほど「妙味のある馬が多いレース」
- **妙味あり馬数**: EV≥-0.10の馬の数。2頭以上なら馬券が組みやすい
- **EV(単)**: 単勝期待値。EV > 0 が理想だが -0.10 以上でも検討余地あり
- **EV(複)**: 複勝期待値（単勝オッズから推算）

**レース最終選定基準:**
1. レースEVスコアが高い順（上位5レースを予想対象に）
2. 妙味あり馬数が多い方を優先
3. データ不足（N走が少ない）のレースは注意書きを付ける

---

## Step 5: 予想出力 + ポートフォリオ構築

### オッズの最新化（リフレッシュ）

オッズは**発走30〜60分前に大きく動く**。Step 2で取得したオッズは予想開始時点のスナップショットに過ぎない。
以下の状況でshutubaページを再取得してオッズを更新する:

**リフレッシュすべきタイミング:**
- 予想完了後、発走まで30分以上ある場合
- 取得時にオッズが確定していなかった馬がいる（表示「---」）
- ユーザーから「最新オッズで見直して」と指示があった場合

`navigate` ツールで同じshutubaURLに再遷移して最新化する。
前回取得オッズと比較して大きく変動した馬（±1.0倍以上）は注記し、EV計算を再実行する。

### 予想出力フォーマット

各レースについて以下のフォーマットで出力する:

```
【1. レース確認】
・開催日：
・競馬場：
・レース番号・レース名：
・距離 / コース：
・条件：
・取消・除外馬：（確認できなければ「不明」）
・騎手変更：（確認できなければ「不明」）
・馬場状態：（予報ベースでもOK）
・天候予報：

確定枠順（全頭テーブル）:
| 枠 | 馬番 | 馬名 | 性齢 | 斤量 | 騎手 | 調教師 | 単勝オッズ | EV(単) |

【2. EV分析サマリー】
（calc_ev.py の出力結果を要約）
・レースEVスコア：
・EV上位馬：馬名(EV値), 馬名(EV値), ...
・妙味あり馬数：N頭
・使用データ：同条件Nレース分 / 全Nレース分

【3. 先に結論】
・◎ 本命：（EV最高または本命サイドで最高EV）
・○ 対抗：
・▲ 単穴：
・△ 連下：（複数可）
・☆ 穴：（EVが高い割にオッズが高い馬）
・危険な人気馬：（EV < -0.20 の人気馬 = 過大評価）

【4. 展開予測】
・逃げ候補：
・先行勢：
・差し勢：
・追い込み勢：
・想定ペース：（H/M/S + 根拠）

【5. 各馬評価（上位中心）】
良い点・不安点の両方を記載。EV値と過去成績データを根拠として使う。

【6. 印の理由】
なぜその印か。EV値と過去成績（勝率・複勝率・サンプル数）を明示。

【7. 馬券戦略（バランス型）】

【8. 買い目】10点以内厳守
馬番で明示。馬名併記。EV根拠を一行で添える。

【9. 最終判断】
強気に買える / 少額なら買える / 妙味はあるが難解 / 見送り推奨

【10. 不確実性と注意事項】
・使用データのサンプル数（N走）
・フィルタ適用の有無（同条件限定か全走か）
・EV計算不能馬の有無（データ不足）
```

### 買い目構成ルール（EV版）

**ルール1: EVに基づく軸設定**
- EV最高馬を◎に設定する（人気順位でなくEV順で本命を決める）
- EV > 0 の馬が複数いる場合はその馬でBOX or 流しを優先
- 断然人気馬のEVが低い（EV < -0.20）場合は「危険な人気馬」として外す

**ルール2: 軸の分散（EVが拮抗している場合）**
上位3頭のEV差が0.10未満の場合は複数軸またはBOX買い。特に:
- ハンデ戦、多頭数（14頭以上）、EV拮抗レースは軸分散

**ルール3: 穴馬の活用**
EV高・高オッズ馬（EVプラスで単勝5倍以上）を☆穴に指定し、買い目に最低2点は組み込む。

**ルール4: 危険な人気馬の徹底活用**
EV < -0.20 の人気馬は外した買い目を構成する（三連複で含まない組み合わせ優先）。

**ルール5: レースタイプ別戦略**
- **堅いレース**（EVスコア低・1強構図）: 1強軸の複勝・馬連で手堅く
- **中荒れレース**（EVスコア中・2〜3強）: 上位2頭軸の三連複流し
- **大荒れレース**（EVスコア高・複数頭にEV妙味）: BOX買い or EV高馬中心のワイド

### ポートフォリオ構築（portfolio.py）

EV計算が完了したレースについて、Half-Kelly基準で各買い目の投資額を算出する。

**スクリプトのパス:** `{このSKILL.mdのディレクトリ}/scripts/portfolio.py`

**入力JSON:**
calc_ev.py の出力をベースに、各レースに `bets` 配列を追加したJSONを作成する:

```json
[
  {
    "race_id": "202645040611",
    "race_name": "疾風迅雷賞(A2)",
    "venue": "川崎",
    "dist": "ダ900",
    "n_horses": 9,
    "race_ev_score": 0.05,
    "bets": [
      {
        "type": "馬連",
        "horses": ["4", "7"],
        "names": ["ハーフブルー", "スモークフレイバー"],
        "odds": 5.2,
        "win_prob": 0.25,
        "ev": 0.30,
        "label": "◎-○"
      }
    ]
  }
]
```

**win_prob の決め方:**
- calc_ev.py が計算した `win_rate_filtered`（同条件勝率）を優先
- サンプル不足なら `win_rate_all`（全成績勝率）を使用
- 馬連・三連複は「◎の単勝勝率 × ○の複勝率」などで推算
- EV と odds が分かれば逆算も可: `win_prob = (ev + 1) / odds`

**実行コマンド:**
```bash
SKILL_DIR="[SKILL.mdのあるディレクトリ]"

# 平日（NAR のみ） 予算1万円
python3 $SKILL_DIR/scripts/portfolio.py {日付}_nar_portfolio_input.json \
    --budget 10000 --mode nar

# 週末（JRA）
python3 $SKILL_DIR/scripts/portfolio.py {日付}_jra_portfolio_input.json \
    --budget 10000 --mode jra
```

出力: `portfolio_10000.json`（JSON）+ テキストサマリー（stdout）

---

## Step 6: HTMLレポート生成（generate_report.py）

**スクリプトのパス:** `{このSKILL.mdのディレクトリ}/scripts/generate_report.py`

portfolio.py の出力JSON を入力として、ダークテーマの美麗HTMLレポートを生成する。
馬のシルエットSVG・EVバー・印バッジ・ポートフォリオ表を含む完全版HTMLが生成される。

**実行コマンド:**
```bash
SKILL_DIR="[SKILL.mdのあるディレクトリ]"
DATE_STR="2026年4月10日（金）"
BUDGET=10000

# NARレポート
python3 $SKILL_DIR/scripts/generate_report.py portfolio_10000.json \
    --date "$DATE_STR" \
    --budget $BUDGET \
    --output {日付}_nar_report.html
```

**最後に必ず outputs/ ディレクトリにコピーする。**
ユーザーには `computer://` リンクでHTMLファイルを共有する。

---

## 結果の取得と突合

**URL:**
```
https://nar.netkeiba.com/race/result.html?race_id={RACE_ID}
```
JRAの場合: `https://race.netkeiba.com/race/result.html?race_id={RACE_ID}`

**抽出用JavaScript（結果）:**
```javascript
const rows = document.querySelectorAll('.ResultTableWrap table tbody tr');
const results = [];
rows.forEach(row => {
  const cells = row.querySelectorAll('td');
  if (cells.length > 10) {
    results.push([
      cells[0]?.textContent?.trim(),  // 着順
      cells[1]?.textContent?.trim(),  // 枠
      cells[2]?.textContent?.trim(),  // 馬番
      cells[3]?.textContent?.trim(),  // 馬名
      cells[9]?.textContent?.trim(),  // 人気
      cells[10]?.textContent?.trim(), // 単勝オッズ
      cells[11]?.textContent?.trim()  // 上がり3F
    ].join('|'));
  }
});
const payoutRows = document.querySelectorAll('.Payout_Detail_Table tr');
const payouts = [];
payoutRows.forEach(row => {
  const th = row.querySelector('th');
  const tds = row.querySelectorAll('td');
  if (th && tds.length >= 2) {
    payouts.push(th.textContent.trim() + ':' + tds[0]?.textContent?.trim()?.replace(/\s+/g,',') + ' ' + tds[1]?.textContent?.trim()?.replace(/\s+/g,','));
  }
});
'RESULTS:\n' + results.join('\n') + '\nPAYOUTS:\n' + payouts.join('\n');
```

### 結果突合フォーマット

```
【予想 vs 結果】
| 印 | 馬名 | 予測EV | 結果着順 | 評価 |

【買い目検証】
| # | 買い目 | 結果（的中/ハズレ） |

【EV精度検証】
- EV > 0 の馬は何頭中何頭が馬券内か
- EV < -0.20 の危険馬は実際に飛んだか
- 予測勝率 vs 実際の結果（ベイズ更新の参考に）

【反省点】
- 良かった点
- 改善すべき点
- EV計算の精度改善案
```

---

## 運用ルール

- netkeiba からの実データに基づくこと。推測・記憶での回答禁止。
- 「絶対」「確実」などの断定表現は使わない。
- 各レース買い目は10点以内を厳守。
- 情報不足は「不明」と明記。EV計算のサンプル数が少ない場合は必ず明示する。
- 指定されたレース数の予想を必ず全部出すこと。途中で止めない。
- `get_page_text` は使わない。データ抽出は `javascript_tool` または `find` + `read_page` で行う。
- 取得データはファイルに保存してからコンテキストに読み込む。
- calc_ev.py / portfolio.py / generate_report.py / parse_horse_results.py のパスは、このSKILL.mdと同階層の `scripts/` ディレクトリ。
- **最終成果物は必ずHTMLレポートを生成してユーザーに提示すること**（テキスト出力のみで終わらない）。
- 平日はNARのみ予算1万円、週末はNAR1万＋JRA1万（合計2万円）でそれぞれ独立してポートフォリオを構築する。
- **作業後は必ず課題・改善点をユーザーに報告する**。スキルの更新はユーザーの判断で行う。

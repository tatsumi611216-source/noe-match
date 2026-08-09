# インデックス申請リスト（2026-08-01 作成・note実験と切り分け済み）

## 未インデックス95本の割り振り

| 群 | 本数 | 施策 | 何が測れるか |
|----|------|------|------------|
| Day 0（2026-08-01 実施済み） | 10 | Google申請 | — |
| **note専用テスト群** | **5** | **noteのみ・Google申請しない** | **noteがクロールを動かすか** |
| Google申請の対象 | 80 | 申請のみ・noteなし | 申請がクロールを動かすか |

**この分離が重要。**同じ記事に両方やると、どちらが効いたか永久に分からない。

### note専用テスト群（**絶対にGoogle申請しないこと**）

noteの立ち上げ8本のうち、リンク先がまだ未クロールの5本。

```
kaden-rental-vs-kounyu
nurse-konkatsu-soudanjo
soudanjo-hikaku
tantei-erabikata
yachin-credit-shiharai
```

**この5本にGoogle申請をすると、noteの効果測定が壊れる。**
noteの予約投稿（8/4〜）でリンクが公開された後、この5本が先にクロールされれば
「noteはクロール需要を動かす」と実測で言える。動かなければnoteも効かないと分かる。

残り3本（success-rate-data / shikijo-erabi-guide / with-seriousness-data）は
既にインデックス済みなので判定には使えない。

## 申請の順番

無作為に申請すると、途中で上限に当たったり中断したときに何も分からなくなる。
**1日10本の中に4つのクエリ型を混ぜてあり、毎日が縮小版の実験になる。**
各日の内訳：固有修飾4／定番トピック3／指名2／ヘッドターム1。
`●`＝CTAあり（収益記事）／`○`＝CTAなし。同じ型の中ではCTAありを先に置いている。

## 手順

Search Console 上部の検索窓にURLを貼る → Enter → 「インデックス登録をリクエスト」。
**1日の上限に達したらその日は終了**（残りは翌日のDayへ繰り越す）。

## 判定（全部申請し終えてから7日後）

```
python scripts\index_check.py --refresh    # 最新の状態を取り直す
python scripts\index_diff.py               # 申請前(2026-08-01)と比べる
```

**`--report` だけでは判定できない。**全体のインデックス率が上がっていても、
申請していない群が同じだけ上がっていれば、それは時間の効果であって申請の効果ではない。
`index_diff.py` は申請済み群と申請待ち群の**伸びの差**を出す。そこを見る。

比較の基準は `agent/index_baseline_20260801.json`（申請前のスナップショット）に凍結してある。
どの Day を実際に申請したかは `agent/index_requests_done.json` に記録する。
**この2つが正しくないと群分けが壊れる。**

| 結果 | 読み取り |
|------|---------|
| 申請80本の大半が入った | **申請は効く**。行列の問題は順番待ちであって品質評価ではない |
| ヘッドタームだけ入らない | Googleがこの層を価値なしと判断。AGENT.mdのヘッドターム禁止は維持 |
| 全体的に入らない | 申請では動かない。需要側（外部評価）以外に手が無いことが確定 |
| **note群5本が入った** | **noteはクロール需要を動かす**。SNS投資の判断根拠になる |
| note群が入らず申請群が入った | noteは被リンクとしては効かない。役割は直接流入に限定される |

**申請中も新記事の公開は週2本を維持すること。**変えると何が効いたか分からなくなる。

## 記録欄

機械可読な正本は `agent/index_requests_done.json`。この表は人間用の控え。

| Day | 実施日 | 申請できた本数 | 備考（上限に当たった等） |
|-----|-------|--------------|----------------------|
| 0 | 2026-08-01 | 10 | index_experiment.md の10本 |
| 1 | 2026-08-02 | 10 | |
| 2 | 2026-08-08 | 10 | |
| 3 | 2026-08-09 | 10 | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |

**申請済み 40本 / 申請待ち 50本 / note専用テスト群 5本（申請禁止）**

### 中間判定（2026-08-09・`index_diff.py`）

| 群 | 申請前 | 08-09 | 経過日数 |
|----|-------|-------|---------|
| Day 0 | 0.0% | **100.0%** | 8日 |
| Day 1 | 0.0% | **90.0%** | 7日 |
| Day 2 | 0.0% | 10.0% | 1日（**まだ早い**） |
| **申請待ち60本（対照）** | 0.0% | **1.7%** | — |

**差 +65.0ポイント。申請は効く。** 反映までの目安は**7日**。
Day 2 が10%なのは失敗ではなく、単に申請の翌日だから。

**残り Day 3〜8（60本）を最後まで消化すること。**申請待ち群は8日で+1本しか
入っていない（自然クロール 0.125本/日）。**待っても入らない。**

---

### Day 1

```
https://www.noe-match.com/articles/dousei-nimotsu-trunkroom/
https://www.noe-match.com/articles/futari-hikari-kaisen/
https://www.noe-match.com/articles/kekkon-houkoku-nengajou/
https://www.noe-match.com/articles/kekkon-tenshoku-guide/
https://www.noe-match.com/articles/40s-guide/
https://www.noe-match.com/articles/40s-men/
https://www.noe-match.com/articles/date-sakuhin-ng/
https://www.noe-match.com/articles/omiai-30s-women-data/
https://www.noe-match.com/articles/omiai-vs-pairs/
https://www.noe-match.com/articles/compare-konkatsu/
```
<sub>dousei-nimotsu-trunkroom=サイト外の固● / futari-hikari-kaisen=サイト外の固● / kekkon-houkoku-nengajou=サイト外の固● / kekkon-tenshoku-guide=サイト外の固● / 40s-guide=ニッチ内の定● / 40s-men=ニッチ内の定● / date-sakuhin-ng=ニッチ内の定● / omiai-30s-women-data=指名（サービ● / omiai-vs-pairs=指名（サービ● / compare-konkatsu=無修飾ヘッド●</sub>

### Day 2

```
https://www.noe-match.com/articles/kekkon-uchiiwai-guide/
https://www.noe-match.com/articles/konkatsu-party-guide/
https://www.noe-match.com/articles/mens-make-konkatsu/
https://www.noe-match.com/articles/shinkon-osechi/
https://www.noe-match.com/articles/dousei-hajimekata/
https://www.noe-match.com/articles/dousei-kekkon-timing/
https://www.noe-match.com/articles/kazoku-simhikaku/
https://www.noe-match.com/articles/pairs-guide/
https://www.noe-match.com/articles/tapple-guide/
https://www.noe-match.com/articles/compare-popular/
```
<sub>kekkon-uchiiwai-guide=サイト外の固● / konkatsu-party-guide=サイト外の固● / mens-make-konkatsu=サイト外の固● / shinkon-osechi=サイト外の固● / dousei-hajimekata=ニッチ内の定● / dousei-kekkon-timing=ニッチ内の定● / kazoku-simhikaku=ニッチ内の定● / pairs-guide=指名（サービ● / tapple-guide=指名（サービ● / compare-popular=無修飾ヘッド●</sub>

### Day 3

```
https://www.noe-match.com/articles/tanshin-uwaki-mikiwame/
https://www.noe-match.com/articles/tenshoku-riyu-honne/
https://www.noe-match.com/articles/uwaki-chousa-kiso/
https://www.noe-match.com/articles/futari-kouza-kanri/
https://www.noe-match.com/articles/kekkon-chokin-mokuhyou/
https://www.noe-match.com/articles/kekkon-hoken-minaoshi/
https://www.noe-match.com/articles/kekkon-sokou-chousa/
https://www.noe-match.com/articles/tapple-seriousness-data/
https://www.noe-match.com/articles/youbride-marrish-hikaku/
https://www.noe-match.com/articles/konkatsu-roadmap/
```
<sub>tanshin-uwaki-mikiwame=サイト外の固● / tenshoku-riyu-honne=サイト外の固● / uwaki-chousa-kiso=サイト外の固● / futari-kouza-kanri=サイト外の固○ / kekkon-chokin-mokuhyou=ニッチ内の定● / kekkon-hoken-minaoshi=ニッチ内の定● / kekkon-sokou-chousa=ニッチ内の定● / tapple-seriousness-data=指名（サービ● / youbride-marrish-hikaku=指名（サービ● / konkatsu-roadmap=無修飾ヘッド●</sub>

### Day 4

```
https://www.noe-match.com/articles/fuufu-credit-kanri/
https://www.noe-match.com/articles/gosyugi-shiharai-houhou/
https://www.noe-match.com/articles/rikon-okane-genjitsu/
https://www.noe-match.com/articles/shinkon-ryokou-credit/
https://www.noe-match.com/articles/kisei-kekkon-aisatsu/
https://www.noe-match.com/articles/matching-dansei-cost-data/
https://www.noe-match.com/articles/ouchi-date-sakuhin/
https://www.noe-match.com/articles/mitas-formen-kuchikomi/
https://www.noe-match.com/articles/mitocore-kuchikomi/
https://www.noe-match.com/articles/matching-app-ranking/
```
<sub>fuufu-credit-kanri=サイト外の固○ / gosyugi-shiharai-houhou=サイト外の固○ / rikon-okane-genjitsu=サイト外の固○ / shinkon-ryokou-credit=サイト外の固○ / kisei-kekkon-aisatsu=ニッチ内の定● / matching-dansei-cost-data=ニッチ内の定● / ouchi-date-sakuhin=ニッチ内の定● / mitas-formen-kuchikomi=指名（サービ○ / mitocore-kuchikomi=指名（サービ○ / matching-app-ranking=無修飾ヘッド●</sub>

### Day 5

```
https://www.noe-match.com/articles/photo-tips/
https://www.noe-match.com/articles/shinkon-koteihi-minaoshi/
https://www.noe-match.com/articles/shinkyo-kagu-yosan/
https://www.noe-match.com/articles/myseed-kuchikomi/
https://www.noe-match.com/articles/pairs-marriage-data/
https://www.noe-match.com/articles/compare-price/
https://www.noe-match.com/articles/pairs-men/
https://www.noe-match.com/articles/pairs-women/
https://www.noe-match.com/articles/tapple-vs-pairs/
https://www.noe-match.com/articles/with-vs-pairs/
```
<sub>photo-tips=ニッチ内の定● / shinkon-koteihi-minaoshi=ニッチ内の定● / shinkyo-kagu-yosan=ニッチ内の定● / myseed-kuchikomi=指名（サービ○ / pairs-marriage-data=指名（サービ○ / compare-price=無修飾ヘッド○ / pairs-men=指名（サービ○ / pairs-women=指名（サービ○ / tapple-vs-pairs=指名（サービ○ / with-vs-pairs=指名（サービ○</sub>

### Day 6

```
https://www.noe-match.com/articles/shizuoka-niigata-guide/
https://www.noe-match.com/articles/time-management/
https://www.noe-match.com/articles/tomobataraki-shokuji-data/
https://www.noe-match.com/articles/faq-troubleshooting/
https://www.noe-match.com/articles/usuge-konkatsu-eikyou/
https://www.noe-match.com/articles/anti-fraud/
https://www.noe-match.com/articles/dousei-kaisho/
https://www.noe-match.com/articles/dousei-kekkon-hikaku/
https://www.noe-match.com/articles/first-date-guide/
https://www.noe-match.com/articles/fraud-statistics/
```
<sub>shizuoka-niigata-guide=ニッチ内の定● / time-management=ニッチ内の定● / tomobataraki-shokuji-data=ニッチ内の定● / faq-troubleshooting=無修飾ヘッド○ / usuge-konkatsu-eikyou=ニッチ内の定● / anti-fraud=ニッチ内の定○ / dousei-kaisho=ニッチ内の定○ / dousei-kekkon-hikaku=ニッチ内の定○ / first-date-guide=ニッチ内の定○ / fraud-statistics=ニッチ内の定○</sub>

### Day 7

```
https://www.noe-match.com/articles/kaiin-age-cross-data/
https://www.noe-match.com/articles/keiyaku-jisshitsu-wana/
https://www.noe-match.com/articles/kekkon-jutaku-loan/
https://www.noe-match.com/articles/free-vs-paid/
https://www.noe-match.com/articles/kinsen-kachikan-check/
https://www.noe-match.com/articles/koninhiyou-guide/
https://www.noe-match.com/articles/late-20s-strategy/
https://www.noe-match.com/articles/line-exchange/
https://www.noe-match.com/articles/nashikon-data/
https://www.noe-match.com/articles/profile-text/
```
<sub>kaiin-age-cross-data=ニッチ内の定○ / keiyaku-jisshitsu-wana=ニッチ内の定○ / kekkon-jutaku-loan=ニッチ内の定○ / free-vs-paid=無修飾ヘッド○ / kinsen-kachikan-check=ニッチ内の定○ / koninhiyou-guide=ニッチ内の定○ / late-20s-strategy=ニッチ内の定○ / line-exchange=ニッチ内の定○ / nashikon-data=ニッチ内の定○ / profile-text=ニッチ内の定○</sub>

### Day 8

```
https://www.noe-match.com/articles/sakuhin-kachikan/
https://www.noe-match.com/articles/with-guide/
https://www.noe-match.com/articles/with-women/
https://www.noe-match.com/articles/members-data/
https://www.noe-match.com/articles/women-strategy/
https://www.noe-match.com/articles/price-comparison/
https://www.noe-match.com/articles/privacy-protection/
https://www.noe-match.com/articles/renkatsu-vs-konkatsu/
https://www.noe-match.com/articles/safety-guide/
https://www.noe-match.com/articles/success-stories/
```
<sub>sakuhin-kachikan=ニッチ内の定○ / with-guide=ニッチ内の定○ / with-women=ニッチ内の定○ / members-data=無修飾ヘッド○ / women-strategy=ニッチ内の定○ / price-comparison=無修飾ヘッド○ / privacy-protection=無修飾ヘッド○ / renkatsu-vs-konkatsu=無修飾ヘッド○ / safety-guide=無修飾ヘッド○ / success-stories=無修飾ヘッド○</sub>
# インデックス申請リスト（2026-08-01 作成・9日で85本）

## 方針の変更

2026-08-01 に10本だけの切り分け実験を設計したが、**人間の判断で「95本すべてを
1日10本ずつ申請する」方針に変更した。こちらの方が優れている。**

- 10本の実験は「申請が効くか」を7日かけて調べるだけで、その間 行列は進まない
- **95本すべて申請すれば、同じ問いをn=95で確かめながら同時に問題も解ける**
- 効くなら約10日で行列が消える。効かないならそれも分かる（対照は過去の実績値
  ＝検出1.08回/日・インデックス率24〜31%を使う）

**2026-08-01に申請済みの10本**（`agent/index_experiment.md`）はDay 0扱い。
本リストはその残り85本。

## 申請の順番について

無作為に申請すると、途中で上限に当たったり中断したときに何も分からなくなる。
**1日10本の中に4つのクエリ型を混ぜてあり、毎日が縮小版の実験になる。**
どの日で止めても、型ごとの差は読み取れる。

各日の内訳：固有修飾4／定番トピック3／指名2／ヘッドターム1

`●`＝CTAあり（収益記事）／`○`＝CTAなし。同じ型の中ではCTAありを先に置いている。

## 未インデックス95本の内訳

| クエリ型 | 本数 | うちCTAあり |
|---------|------|-----------|
| サイト外の固有修飾 | 20 | 15 |
| 指名（サービス名） | 14 | 6 |
| ニッチ内の定番トピック | 38 | 20 |
| 無修飾ヘッドターム | 13 | 4 |

## 手順

Search Console 上部の検索窓にURLを貼る → Enter → 「インデックス登録をリクエスト」。
**1日の上限に達したらその日はそこで終了**（残りは翌日のDayに繰り越す）。

## 判定

**全部申請し終えてから7日後**に：

```
python scripts/index_check.py --refresh
```

| 結果 | 読み取り |
|------|---------|
| 大半がインデックスされた | 申請は効く。**行列の問題は「順番待ち」であって品質評価ではなかった**。今後も新記事は申請する運用にする |
| ヘッドタームだけ入らない | Googleがこの層を価値なしと判断している。AGENT.mdのヘッドターム禁止ルールは維持し、既存13本は寄せ直し対象 |
| 全体的に入らない | 申請では動かない。需要側（外部評価）以外に手が無いことが確定する |

**申請中も新記事の公開は週2本を維持すること。**変えると何が効いたか分からなくなる。

## 記録欄

| Day | 実施日 | 申請できた本数 | 備考（上限に当たった等） |
|-----|-------|--------------|----------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |

---

## Day 1
● https://www.noe-match.com/articles/dousei-nimotsu-trunkroom/    (サイト外の固有修)
● https://www.noe-match.com/articles/futari-hikari-kaisen/    (サイト外の固有修)
● https://www.noe-match.com/articles/kaden-rental-vs-kounyu/    (サイト外の固有修)
● https://www.noe-match.com/articles/kekkon-houkoku-nengajou/    (サイト外の固有修)
● https://www.noe-match.com/articles/40s-guide/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/40s-men/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/date-sakuhin-ng/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/omiai-30s-women-data/    (指名（サービス名)
● https://www.noe-match.com/articles/omiai-vs-pairs/    (指名（サービス名)
● https://www.noe-match.com/articles/compare-konkatsu/    (無修飾ヘッドター)

## Day 2
● https://www.noe-match.com/articles/kekkon-tenshoku-guide/    (サイト外の固有修)
● https://www.noe-match.com/articles/kekkon-uchiiwai-guide/    (サイト外の固有修)
● https://www.noe-match.com/articles/konkatsu-party-guide/    (サイト外の固有修)
● https://www.noe-match.com/articles/mens-make-konkatsu/    (サイト外の固有修)
● https://www.noe-match.com/articles/dousei-hajimekata/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/dousei-kekkon-timing/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/kazoku-simhikaku/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/pairs-guide/    (指名（サービス名)
● https://www.noe-match.com/articles/tapple-guide/    (指名（サービス名)
● https://www.noe-match.com/articles/compare-popular/    (無修飾ヘッドター)

## Day 3
● https://www.noe-match.com/articles/nurse-konkatsu-soudanjo/    (サイト外の固有修)
● https://www.noe-match.com/articles/shinkon-osechi/    (サイト外の固有修)
● https://www.noe-match.com/articles/tanshin-uwaki-mikiwame/    (サイト外の固有修)
● https://www.noe-match.com/articles/tantei-erabikata/    (サイト外の固有修)
● https://www.noe-match.com/articles/kekkon-chokin-mokuhyou/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/kekkon-hoken-minaoshi/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/kekkon-sokou-chousa/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/tapple-seriousness-data/    (指名（サービス名)
● https://www.noe-match.com/articles/youbride-marrish-hikaku/    (指名（サービス名)
● https://www.noe-match.com/articles/konkatsu-roadmap/    (無修飾ヘッドター)

## Day 4
● https://www.noe-match.com/articles/tenshoku-riyu-honne/    (サイト外の固有修)
● https://www.noe-match.com/articles/uwaki-chousa-kiso/    (サイト外の固有修)
● https://www.noe-match.com/articles/yachin-credit-shiharai/    (サイト外の固有修)
○ https://www.noe-match.com/articles/futari-kouza-kanri/    (サイト外の固有修)
● https://www.noe-match.com/articles/kisei-kekkon-aisatsu/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/matching-dansei-cost-data/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/ouchi-date-sakuhin/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/mitas-formen-kuchikomi/    (指名（サービス名)
○ https://www.noe-match.com/articles/mitocore-kuchikomi/    (指名（サービス名)
● https://www.noe-match.com/articles/matching-app-ranking/    (無修飾ヘッドター)

## Day 5
○ https://www.noe-match.com/articles/fuufu-credit-kanri/    (サイト外の固有修)
○ https://www.noe-match.com/articles/gosyugi-shiharai-houhou/    (サイト外の固有修)
○ https://www.noe-match.com/articles/rikon-okane-genjitsu/    (サイト外の固有修)
○ https://www.noe-match.com/articles/shinkon-ryokou-credit/    (サイト外の固有修)
● https://www.noe-match.com/articles/photo-tips/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/shinkon-koteihi-minaoshi/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/shinkyo-kagu-yosan/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/myseed-kuchikomi/    (指名（サービス名)
○ https://www.noe-match.com/articles/pairs-marriage-data/    (指名（サービス名)
○ https://www.noe-match.com/articles/compare-price/    (無修飾ヘッドター)

## Day 6
● https://www.noe-match.com/articles/shizuoka-niigata-guide/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/soudanjo-hikaku/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/time-management/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/pairs-men/    (指名（サービス名)
○ https://www.noe-match.com/articles/pairs-women/    (指名（サービス名)
○ https://www.noe-match.com/articles/faq-troubleshooting/    (無修飾ヘッドター)
○ https://www.noe-match.com/articles/tapple-vs-pairs/    (指名（サービス名)
○ https://www.noe-match.com/articles/with-vs-pairs/    (指名（サービス名)
● https://www.noe-match.com/articles/tomobataraki-shokuji-data/    (ニッチ内の定番ト)
● https://www.noe-match.com/articles/usuge-konkatsu-eikyou/    (ニッチ内の定番ト)

## Day 7
○ https://www.noe-match.com/articles/anti-fraud/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/dousei-kaisho/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/dousei-kekkon-hikaku/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/free-vs-paid/    (無修飾ヘッドター)
○ https://www.noe-match.com/articles/first-date-guide/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/fraud-statistics/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/kaiin-age-cross-data/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/keiyaku-jisshitsu-wana/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/kekkon-jutaku-loan/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/kinsen-kachikan-check/    (ニッチ内の定番ト)

## Day 8
○ https://www.noe-match.com/articles/koninhiyou-guide/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/late-20s-strategy/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/line-exchange/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/members-data/    (無修飾ヘッドター)
○ https://www.noe-match.com/articles/nashikon-data/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/profile-text/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/sakuhin-kachikan/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/with-guide/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/with-women/    (ニッチ内の定番ト)
○ https://www.noe-match.com/articles/women-strategy/    (ニッチ内の定番ト)

## Day 9
○ https://www.noe-match.com/articles/price-comparison/    (無修飾ヘッドター)
○ https://www.noe-match.com/articles/privacy-protection/    (無修飾ヘッドター)
○ https://www.noe-match.com/articles/renkatsu-vs-konkatsu/    (無修飾ヘッドター)
○ https://www.noe-match.com/articles/safety-guide/    (無修飾ヘッドター)
○ https://www.noe-match.com/articles/success-stories/    (無修飾ヘッドター)
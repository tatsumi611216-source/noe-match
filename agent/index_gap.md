# インデックス欠落リスト（sitemap掲載URLのうち未インデックスのもの）

**自動生成: `scripts/index_gap.py`。手で編集しない。**

index_status 取得: 2026-08-20 / GSC期間: 2026-07-21〜2026-08-18

sitemap 206 URL のうち **未インデックス 71本（34%）**。

実測則「申請すれば7日で90〜100%／放置は8日で1.7%」より、この71本は**順位が悪いのではなく、まだ試合をしていない**。

## ⛔ 申請してはいけない（note対照実験）

noteがクロール需要を動かすかの対照群。**申請すると実験が壊れる。**

- `/articles/yachin-credit-shiharai/` — Discovered - currently not indexed（確認 2026-08-15）

（対照群5本のうち、他4本は既にインデックス済み。未インデックスで残っているのはこれだけなので、実験の観測点として保持する）

## A. Google がURLの存在を知らない（6本・最優先）

sitemapに載っていて内部リンクもあるのに未認識。申請で解消しない場合は、リンク先URLの綴り・実URLの200応答・sitemap再送信を順に確認する。

| URL | 確認日 | 優先理由 |
|---|---|---|
| `/tools/kekkon-shikin-keisanki/` | 2026-08-15 | ツール（AI要約に食われない防御資産） |
| `/articles/omiai-danjohi-data/` | 2026-08-20 | データ・統計（クリック/本 1.00＝サイト最良） |
| `/articles/zexy-enmusubi-data/` | 2026-08-15 | データ・統計（クリック/本 1.00＝サイト最良） |
| `/articles/compare-price/` | 2026-08-15 | その他記事 |
| `/articles/sakuhin-kachikan/` | 2026-08-15 | その他記事 |
| `/articles/women-strategy/` | 2026-08-15 | その他記事 |

## B. 申請キュー（1日10本・上から順に消化）

手順は `agent/index_request_queue.md` と同じ。Search Console にURLを貼って「インデックス登録をリクエスト」。


### Day 1

```
https://www.noe-match.com/tools/kekkon-shikin-keisanki/
https://www.noe-match.com/articles/omiai-danjohi-data/
https://www.noe-match.com/articles/zexy-enmusubi-data/
https://www.noe-match.com/articles/compare-price/
https://www.noe-match.com/articles/sakuhin-kachikan/
https://www.noe-match.com/articles/women-strategy/
https://www.noe-match.com/tools/saigenbyo-check/
https://www.noe-match.com/tools/seikatsuhi-simulator/
https://www.noe-match.com/articles/shizuoka-niigata-guide/
https://www.noe-match.com/articles/hatsushon-nenmei-data/
```

### Day 2

```
https://www.noe-match.com/articles/kaiin-age-cross-data/
https://www.noe-match.com/articles/matching-josei-cost-data/
https://www.noe-match.com/articles/members-data/
https://www.noe-match.com/articles/nashikon-data/
https://www.noe-match.com/articles/pairs-kaiin-data/
https://www.noe-match.com/articles/pairs-marriage-data/
https://www.noe-match.com/articles/tomobataraki-shokuji-data/
https://www.noe-match.com/articles/garugaru-doukyo/
https://www.noe-match.com/articles/garugaru-ki-itsumade/
https://www.noe-match.com/articles/garugaru-otto-genkai/
```

### Day 3

```
https://www.noe-match.com/articles/garugaru-sangoutsu-chigai/
https://www.noe-match.com/articles/garugaru-ueno-ko/
https://www.noe-match.com/articles/maternity-blue-chigai/
https://www.noe-match.com/articles/sango-iraira/
https://www.noe-match.com/articles/sango-rikon/
https://www.noe-match.com/articles/shinseiji-menkai/
https://www.noe-match.com/articles/anti-fraud/
https://www.noe-match.com/articles/compare-popular/
https://www.noe-match.com/articles/dousei-kaisho/
https://www.noe-match.com/articles/dousei-kekkon-hikaku/
```

### Day 4

```
https://www.noe-match.com/articles/faq-troubleshooting/
https://www.noe-match.com/articles/first-date-guide/
https://www.noe-match.com/articles/fraud-statistics/
https://www.noe-match.com/articles/free-vs-paid/
https://www.noe-match.com/articles/keiyaku-jisshitsu-wana/
https://www.noe-match.com/articles/kekkon-hiyou-futan/
https://www.noe-match.com/articles/kekkon-jutaku-loan/
https://www.noe-match.com/articles/kinsen-kachikan-check/
https://www.noe-match.com/articles/koninhiyou-guide/
https://www.noe-match.com/articles/konkatsu-party-guide/
```

### Day 5

```
https://www.noe-match.com/articles/late-20s-strategy/
https://www.noe-match.com/articles/line-exchange/
https://www.noe-match.com/articles/myseed-kuchikomi/
https://www.noe-match.com/articles/otaku-konkatsu/
https://www.noe-match.com/articles/pairs-guide/
https://www.noe-match.com/articles/pairs-men/
https://www.noe-match.com/articles/pairs-women/
https://www.noe-match.com/articles/pet-konkatsu/
https://www.noe-match.com/articles/photo-tips/
https://www.noe-match.com/articles/price-comparison/
```

### Day 6

```
https://www.noe-match.com/articles/privacy-protection/
https://www.noe-match.com/articles/profile-text/
https://www.noe-match.com/articles/renkatsu-vs-konkatsu/
https://www.noe-match.com/articles/safety-guide/
https://www.noe-match.com/articles/shinkon-osechi/
https://www.noe-match.com/articles/shinkyo-kagu-yosan/
https://www.noe-match.com/articles/success-stories/
https://www.noe-match.com/articles/tapple-guide/
https://www.noe-match.com/articles/tapple-vs-pairs/
https://www.noe-match.com/articles/tokyo-futari-seikatsuhi/
```

### Day 7

```
https://www.noe-match.com/articles/usuge-konkatsu-eikyou/
https://www.noe-match.com/articles/with-guide/
https://www.noe-match.com/articles/with-vs-pairs/
https://www.noe-match.com/articles/with-women/
https://www.noe-match.com/disclaimer.html
https://www.noe-match.com/policy/editorial.html
https://www.noe-match.com/policy/rating.html
https://www.noe-match.com/policy/research.html
https://www.noe-match.com/policy/update.html
https://www.noe-match.com/privacy-policy.html
```

## 優先順の内訳

| 順 | 区分 | 本数 |
|---|---|---|
| 1 | ツール（AI要約に食われない防御資産） | 3 |
| 2 | 地域ガイド（平均15.7位＝サイト最良） | 1 |
| 3 | データ・統計（クリック/本 1.00＝サイト最良） | 10 |
| 4 | 産後クラスタ（10位台の実績あり） | 9 |
| 5 | その他記事 | 41 |
| 6 | 規約・方針ページ（収益に直結しないが運営者情報のシグナル） | 6 |

## ⚠ 判定が古い可能性（未インデックスなのにGSCに表示がある）

index_status の確認日が古く、その後インデックスされた可能性がある。**申請前にGSCで実機確認してよい。**

| URL | 表示 | 確認日 |
|---|---|---|
| `/tools/saigenbyo-check/` | 2 | 2026-08-15 |
| `/policy/research.html` | 1 | 2026-08-15 |
| `/policy/update.html` | 1 | 2026-08-15 |


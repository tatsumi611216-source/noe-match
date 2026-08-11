# 記事監査：① 流入 × ② 実効単価 × ③ 接続

**自動生成: `scripts/article_audit.py`。手で編集しない。**

収益は3つの掛け算。どれか1つがゼロなら全体がゼロ。
希少なのは①だけで、②は提携182件あって余っている。**①のある場所に②を寄せるのが基本方針**。

実効単価 = 単価 × 確定率。確定率が台帳に無い案件は 0.6 で仮置きしている（要実測）。

## S. 10位以内（①が最大）（2本）

> **②を最大化する。**流入が既にあるので、より実効単価の高い案件に差し替えられないか検討する。単価不明なら真っ先に調べる

| 表示 | クリック | 順位 | 実効単価 | 記事 | 載っている案件 |
|---|---|---|---|---|---|
| 30 | 4 | 4.2 | 6,000円 | `with-seriousness-data` | ユーブライド |
| 2 | 0 | 5.0 | 6,000円 | `inaka-guide` | 田舎婚 |

## B. 射程内（①が生きている）（17本）

> **磨いて10位以内へ。**ターゲット語が本文にあるか、競合が持っていない節があるかを見る

| 表示 | クリック | 順位 | 実効単価 | 記事 | 載っている案件 |
|---|---|---|---|---|---|
| 25 | 0 | 20.7 | 600円 | `propose-guide` | THE KISS |
| 18 | 0 | 34.8 | 6,000円 | `success-rate-data` | ユーブライド |
| 17 | 0 | 46.0 | 1,800円 | `marrish-guide` | マリッシュ |
| 12 | 0 | 25.8 | 案件なし | `student-guide` | — |
| 11 | 0 | 25.0 | 6,000円 | `shikijo-erabi-guide` | ハナユメ |
| 10 | 0 | 37.0 | 300円 | `kekkon-houkoku-nengajou` | 挨拶状ドットコム |
| 9 | 0 | 42.0 | 3,000円 | `bachelor-date-guide` | バチェラーデート |
| 7 | 0 | 34.4 | 6,000円 | `kyoto-guide` | ユーブライド |
| 6 | 0 | 21.0 | 5,280円 | `shinkon-seikatsu-guide` | ハローストレージ |
| 4 | 0 | 17.0 | 6,000円 | `nagoya-guide` | ユーブライド |
| 4 | 0 | 48.8 | 6,000円 | `omiai-guide` | ユーブライド |
| 4 | 0 | 29.0 | 案件なし | `age-data` | — |
| 3 | 0 | 18.0 | 6,000円 | `kekkon-madeno-kikan-data` | ユーブライド |
| 2 | 0 | 29.5 | 10,452円 | `tokyo-guide` | エクセレンス青山 |
| 1 | 0 | 17.0 | 6,000円 | `appkon-wariai-data` | ユーブライド |
| 1 | 0 | 44.0 | 6,000円 | `fukuoka-guide` | ユーブライド |
| 1 | 0 | 28.0 | 6,000円 | `hitomishiri-guide` | ユーブライド |

## C. 51位以下（①が弱い）（21本）

> **看板を掛け替える。**本文は活かし、タイトル・h1・導入をサイト外の固有修飾へ寄せる（到達率23.5→68.8）

| 表示 | クリック | 順位 | 実効単価 | 記事 | 載っている案件 |
|---|---|---|---|---|---|
| 26 | 0 | 65.0 | 1,800円 | `over50-guide` | マリッシュ |
| 12 | 0 | 86.2 | 6,000円 | `batsuichi-guide` | ユーブライド |
| 11 | 0 | 74.0 | 1,800円 | `20s-guide` | Photojoy |
| 9 | 0 | 67.9 | 1,800円 | `first-date-spot` | Photojoy |
| 8 | 0 | 94.0 | 6,000円 | `30s-konkatsu` | ユーブライド |
| 6 | 0 | 87.0 | 24,000円 | `nurse-guide` | 白衣コン |
| 6 | 0 | 71.2 | 6,000円 | `bridal-esthe-guide` | ハナユメ |
| 5 | 0 | 57.5 | 6,000円 | `fraud-detection` | ユーブライド |
| 5 | 0 | 85.0 | 1,800円 | `profile-photo` | Photojoy |
| 4 | 0 | 90.0 | 6,000円 | `agency-vs-app` | ユーブライド |
| 3 | 0 | 92.0 | 6,000円 | `app-plus-agency` | ユーブライド |
| 2 | 0 | 84.0 | 6,000円 | `app-tsukare-guide` | ユーブライド |
| 2 | 0 | 55.0 | 6,000円 | `civil-servant-guide` | ユーブライド |
| 2 | 0 | 78.0 | 6,000円 | `kekkon-okane-data` | ハナユメ |
| 2 | 0 | 81.0 | 6,000円 | `omiai-vs-pairs` | ユーブライド |
| 2 | 0 | 55.0 | 6,000円 | `sapporo-guide` | ユーブライド |
| 2 | 0 | 85.0 | 6,000円 | `youbride-guide` | ユーブライド |
| 1 | 0 | 52.0 | 6,000円 | `35s-strategy` | ユーブライド |
| 1 | 0 | 100.0 | 6,000円 | `40s-men` | ユーブライド |
| 1 | 0 | 77.0 | 6,000円 | `okinawa-guide` | ユーブライド |
| 1 | 0 | 94.0 | 案件なし | `dansei-ninkatsu-guide` | — |

## D. 表示ゼロ（①がゼロ＝圏外）（35本）

> 同上。`silent_articles.md` の寄せ直し対象

| 表示 | クリック | 順位 | 実効単価 | 記事 | 載っている案件 |
|---|---|---|---|---|---|
| 0 | 0 | — | 12,450円 | `kekkon-tenshoku-guide` | レバウェル看護 |
| 0 | 0 | — | 9,000円 | `rikon-junbi-jyunban` | ALG探偵社 |
| 0 | 0 | — | 6,000円 | `40s-guide` | ユーブライド |
| 0 | 0 | — | 6,000円 | `compare-konkatsu` | ユーブライド |
| 0 | 0 | — | 6,000円 | `engineer-guide` | ユーブライド |
| 0 | 0 | — | 6,000円 | `kobe-yokohama-guide` | ユーブライド |
| 0 | 0 | — | 6,000円 | `maedori-photo-guide` | ハナユメ |
| 0 | 0 | — | 6,000円 | `omiai-30s-women-data` | ユーブライド |
| 0 | 0 | — | 6,000円 | `osaka-guide` | ユーブライド |
| 0 | 0 | — | 6,000円 | `saitama-chiba-guide` | ユーブライド |
| 0 | 0 | — | 6,000円 | `seishain-igai-guide` | ユーブライド |
| 0 | 0 | — | 6,000円 | `sendai-hiroshima-guide` | ユーブライド |
| 0 | 0 | — | 5,280円 | `dousei-nimotsu-trunkroom` | ハローストレージ |
| 0 | 0 | — | 3,000円 | `message-strategy` | バチェラーデート |
| 0 | 0 | — | 1,800円 | `konkatsu-photo-guide` | Photojoy |
| 0 | 0 | — | 797円 | `ouchi-date-guide` | Oisixおためしセット |
| 0 | 0 | — | 600円 | `pair-ring-guide` | THE KISS |
| 0 | 0 | — | **単価不明** | `amenohi-date-guide` | スカパー! |
| 0 | 0 | — | 案件なし | `bridal-inner-guide` | — |
| 0 | 0 | — | 案件なし | `christmas-propose-gyakusan` | — |
| 0 | 0 | — | 案件なし | `compare-20s` | — |
| 0 | 0 | — | 案件なし | `date-plan-2kaime` | — |
| 0 | 0 | — | **単価不明** | `date-sakuhin-ng` | WOWOWオンデマンド |
| 0 | 0 | — | 案件なし | `enkyori-renai-guide` | — |
| 0 | 0 | — | 案件なし | `futari-sumaho-minaoshi` | — |
| 0 | 0 | — | **単価不明** | `gosyugi-shiharai-houhou` | エポスカード |
| 0 | 0 | — | **単価不明** | `kekkon-uchiiwai-guide` | シャディギフトモール |
| 0 | 0 | — | 案件なし | `kekkonshiki-isho-rental` | — |
| 0 | 0 | — | 案件なし | `kokusai-kekkon-guide` | — |
| 0 | 0 | — | **単価不明** | `konyaku-yubiwa-data` | リファスタ |
| 0 | 0 | — | 案件なし | `kosodate-zaitaku-guide` | — |
| 0 | 0 | — | 案件なし | `marrish-saikon-data` | — |
| 0 | 0 | — | 案件なし | `nyuseki-2027-guide` | — |
| 0 | 0 | — | 案件なし | `yokohama-propose-spot` | — |
| 0 | 0 | — | 案件なし | `youbride-seikon-data` | — |

## A. 未インデックス（①が未測定）（83本）

> **GSCで申請する。**申請すれば7〜8日で100%、放置すると1.7%。判定はその後

| 表示 | クリック | 順位 | 実効単価 | 記事 | 載っている案件 |
|---|---|---|---|---|---|
| 0 | 0 | — | 30,000円 | `dousei-hajimekata` | ビジモ光 |
| 0 | 0 | — | 30,000円 | `futari-hikari-kaisen` | ビジモ光 |
| 0 | 0 | — | 30,000円 | `kazoku-simhikaku` | ビジモ光 |
| 0 | 0 | — | 30,000円 | `kekkon-chokin-mokuhyou` | ビジモ光 |
| 0 | 0 | — | 30,000円 | `shinkon-koteihi-minaoshi` | ビジモ光 |
| 0 | 0 | — | 30,000円 | `shinkon-net-kaisen-dandori` | ビジモ光 |
| 0 | 0 | — | 24,000円 | `nurse-konkatsu-soudanjo` | 白衣コン |
| 0 | 0 | — | 10,452円 | `soudanjo-hikaku` | エクセレンス青山 |
| 0 | 0 | — | 9,000円 | `kekkon-sokou-chousa` | ALG探偵社 |
| 0 | 0 | — | 9,000円 | `tanshin-uwaki-mikiwame` | ALG探偵社 |
| 0 | 0 | — | 9,000円 | `tantei-erabikata` | ALG探偵社 |
| 0 | 0 | — | 9,000円 | `uwaki-chousa-kiso` | ALG探偵社 |
| 0 | 0 | — | 6,000円 | `compare-popular` | ユーブライド |
| 0 | 0 | — | 6,000円 | `hatsushon-nenmei-data` | ユーブライド |
| 0 | 0 | — | 6,000円 | `konkatsu-roadmap` | ユーブライド |
| 0 | 0 | — | 6,000円 | `matching-app-ranking` | ユーブライド |
| 0 | 0 | — | 6,000円 | `matching-dansei-cost-data` | ユーブライド |
| 0 | 0 | — | 6,000円 | `matching-josei-cost-data` | ユーブライド |
| 0 | 0 | — | 6,000円 | `otaku-konkatsu` | ヲタ婚 |
| 0 | 0 | — | 6,000円 | `pairs-kaiin-data` | ユーブライド |
| 0 | 0 | — | 6,000円 | `pet-konkatsu` | ペット婚 |
| 0 | 0 | — | 6,000円 | `pocchari-konkatsu` | ぽちゃ婚 |
| 0 | 0 | — | 6,000円 | `tapple-seriousness-data` | ユーブライド |
| 0 | 0 | — | 6,000円 | `tenshoku-riyu-honne` | ユーブライド |
| 0 | 0 | — | 6,000円 | `usuge-konkatsu-eikyou` | ユーブライド |
| 0 | 0 | — | 6,000円 | `youbride-marrish-hikaku` | ユーブライド |
| 0 | 0 | — | 6,000円 | `zexy-enmusubi-data` | ユーブライド |
| 0 | 0 | — | 5,280円 | `dousei-kekkon-timing` | ハローストレージ |
| 0 | 0 | — | 3,000円 | `pairs-guide` | バチェラーデート |
| 0 | 0 | — | 3,000円 | `time-management` | バチェラーデート |
| 0 | 0 | — | 2,100円 | `kaden-rental-vs-kounyu` | 家電レンタルみんなのHappy |
| 0 | 0 | — | 1,800円 | `photo-tips` | Photojoy |
| 0 | 0 | — | 1,800円 | `tapple-guide` | Photojoy |
| 0 | 0 | — | 1,000円 | `mens-make-konkatsu` | NULL BBクリーム |
| 0 | 0 | — | 1,000円 | `yachin-credit-shiharai` | クレカリ賃貸 |
| 0 | 0 | — | 797円 | `tomobataraki-shokuji-data` | Oisixおためしセット |
| 0 | 0 | — | 735円 | `konkatsu-party-guide` | PARTY☆PARTY |
| 0 | 0 | — | 案件なし | `anti-fraud` | — |
| 0 | 0 | — | **単価不明** | `compare-price` | ウェルスマ |
| 0 | 0 | — | 案件なし | `dousei-kaisho` | — |

※他 43 本は省略

## ②が測れていない記事（17本）

CTAは貼られているが、台帳に単価の記載が無いため実効単価を計算できない。
**空欄は「案件なし」ではない。**この混同で判断を誤ったことがある（2026-08-09）。
afb / A8 の管理画面で単価と確定率を確認し、`AGENT.md` に追記すること。

`amenohi-date-guide`, `compare-price`, `date-sakuhin-ng`, `dousei-kekkon-hikaku`, `futari-kouza-kanri`, `fuufu-credit-kanri`, `gosyugi-shiharai-houhou`, `kekkon-hoken-minaoshi`, `kekkon-uchiiwai-guide`, `kisei-kekkon-aisatsu`, `konkatsu-soudan-saki`, `konyaku-yubiwa-data`, `ouchi-date-sakuhin`, `shinkon-osechi`, `shinkon-ryokou-credit`, `shinkyo-kagu-yosan`, `shizuoka-niigata-guide`


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
| 25 | 0 | 20.7 | 6,000円 | `propose-guide` | ハナユメ |
| 18 | 0 | 34.8 | 6,000円 | `success-rate-data` | ユーブライド |
| 17 | 0 | 46.0 | 1,800円 | `marrish-guide` | マリッシュ |
| 12 | 0 | 25.8 | 案件なし | `student-guide` | — |
| 11 | 0 | 25.0 | 6,000円 | `shikijo-erabi-guide` | ハナユメ |
| 10 | 0 | 37.0 | 300円 | `kekkon-houkoku-nengajou` | 挨拶状ドットコム |
| 9 | 0 | 42.0 | 3,000円 | `bachelor-date-guide` | バチェラーデート |
| 7 | 0 | 34.4 | 6,000円 | `kyoto-guide` | ユーブライド |
| 6 | 0 | 21.0 | 5,280円 | `shinkon-seikatsu-guide` | ハローストレージ |
| 4 | 0 | 29.0 | 6,000円 | `age-data` | ユーブライド |
| 4 | 0 | 17.0 | 6,000円 | `nagoya-guide` | ユーブライド |
| 4 | 0 | 48.8 | 6,000円 | `omiai-guide` | ユーブライド |
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

## 全記事一覧（テーマ × ①②③）

`③` はCTAの設置数。**①があるのに③が0なら、貼るだけで経路ができる。**

| 判定 | テーマ | ①順位 | ①表示 | ①クリック | ②実効単価 | ③CTA | 記事 |
|---|---|---|---|---|---|---|---|
| S | withの真剣度・結婚データ | 4.2 | 30 | 4 | 6,000円 | 2 | `with-seriousness-data` |
| S | 地方・田舎でマッチングアプリは使える？【人口10万人以下】出 | 5.0 | 2 | 0 | 6,000円 | 2 | `inaka-guide` |
| B | 名古屋でマッチングアプリを使うなら | 17.0 | 4 | 0 | 6,000円 | 2 | `nagoya-guide` |
| B | アプリ婚・マッチングアプリ経由の婚姻割合データ | 17.0 | 1 | 0 | 6,000円 | 2 | `appkon-wariai-data` |
| B | マッチングアプリから結婚までの期間データ | 18.0 | 3 | 0 | 6,000円 | 2 | `kekkon-madeno-kikan-data` |
| B | 結婚の段取り完全ガイド | 20.7 | 25 | 0 | 6,000円 | 3 | `propose-guide` |
| B | 新婚生活の準備ガイド | 21.0 | 6 | 0 | 5,280円 | 2 | `shinkon-seikatsu-guide` |
| B | 結婚式場探し完全ガイド | 25.0 | 11 | 0 | 6,000円 | 1 | `shikijo-erabi-guide` |
| B | 20代前半（学生・新社会人）向けマッチングアプリ完全ガイド | 25.8 | 12 | 0 | **なし** | 0 | `student-guide` |
| B | 人見知り・内向型のためのマッチングアプリ攻略 | 28.0 | 1 | 0 | 6,000円 | 2 | `hitomishiri-guide` |
| B | マッチングアプリの年齢層分布【各年代の利用率比較】 | 29.0 | 4 | 0 | 6,000円 | 1 | `age-data` |
| B | 東京のマッチングアプリ | 29.5 | 2 | 0 | 10,452円 | 3 | `tokyo-guide` |
| B | 京都でマッチングアプリを使うなら | 34.4 | 7 | 0 | 6,000円 | 2 | `kyoto-guide` |
| B | マッチングアプリの結婚率・成功率データ | 34.8 | 18 | 0 | 6,000円 | 2 | `success-rate-data` |
| B | 結婚報告はがき・年賀状の作り方 | 37.0 | 10 | 0 | 300円 | 1 | `kekkon-houkoku-nengajou` |
| B | バチェラーデート完全ガイド | 42.0 | 9 | 0 | 3,000円 | 2 | `bachelor-date-guide` |
| B | 福岡でマッチングアプリを使うなら | 44.0 | 1 | 0 | 6,000円 | 2 | `fukuoka-guide` |
| B | マリッシュの料金と評判 | 46.0 | 17 | 0 | 1,800円 | 2 | `marrish-guide` |
| B | Omiai(お見合い)完全ガイド【婚活向け30代必読・成功戦 | 48.8 | 4 | 0 | 6,000円 | 2 | `omiai-guide` |
| C | 35歳前後のマッチングアプリ戦略 | 52.0 | 1 | 0 | 6,000円 | 4 | `35s-strategy` |
| C | 公務員に出会いがないのはなぜか | 55.0 | 2 | 0 | 6,000円 | 2 | `civil-servant-guide` |
| C | 札幌でマッチングアプリを使うなら | 55.0 | 2 | 0 | 6,000円 | 2 | `sapporo-guide` |
| C | マッチングアプリの業者・サクラの見分け方 | 57.5 | 5 | 0 | 6,000円 | 2 | `fraud-detection` |
| C | 50代の婚活サイトはどれを選ぶ？アプリ・結婚相談所との違いと | 65.0 | 26 | 0 | 1,800円 | 3 | `over50-guide` |
| C | マッチングアプリの初デート場所 | 67.9 | 9 | 0 | 1,800円 | 1 | `first-date-spot` |
| C | ブライダルエステはいつから？費用・回数の相場データと選び方 | 71.2 | 6 | 0 | 6,000円 | 1 | `bridal-esthe-guide` |
| C | 20代向けマッチングアプリ完全ガイド【恋活・婚活別選び方】 | 74.0 | 11 | 0 | 1,800円 | 1 | `20s-guide` |
| C | 沖縄でマッチングアプリを使うなら | 77.0 | 1 | 0 | 6,000円 | 2 | `okinawa-guide` |
| C | 結婚にかかるお金の総額データ | 78.0 | 2 | 0 | 6,000円 | 1 | `kekkon-okane-data` |
| C | OmiaiとPairs比較 | 81.0 | 2 | 0 | 6,000円 | 2 | `omiai-vs-pairs` |
| C | マッチングアプリ疲れの原因と対処法 | 84.0 | 2 | 0 | 6,000円 | 3 | `app-tsukare-guide` |
| C | マッチングアプリのプロフィール写真 | 85.0 | 5 | 0 | 1,800円 | 1 | `profile-photo` |
| C | ユーブライド完全ガイド | 85.0 | 2 | 0 | 6,000円 | 2 | `youbride-guide` |
| C | バツイチの恋愛は難しい？恋愛対象外にされる理由と、そこを外し | 86.2 | 12 | 0 | 6,000円 | 4 | `batsuichi-guide` |
| C | 夜勤があると恋愛できない？看護師のシフト×デート調整の実務【 | 87.0 | 6 | 0 | 24,000円 | 4 | `nurse-guide` |
| C | 結婚相談所とマッチングアプリの違い | 90.0 | 4 | 0 | 6,000円 | 4 | `agency-vs-app` |
| C | 結婚相談所に入らなくていい人の条件 | 92.0 | 3 | 0 | 6,000円 | 3 | `app-plus-agency` |
| C | 30代向け婚活アプリ完全ガイド | 94.0 | 8 | 0 | 6,000円 | 2 | `30s-konkatsu` |
| C | 男性の妊活準備ガイド | 94.0 | 1 | 0 | **なし** | 0 | `dansei-ninkatsu-guide` |
| C | 40代男性向けマッチングアプリ攻略 | 100.0 | 1 | 0 | 6,000円 | 4 | `40s-men` |
| D | 40代のマッチングアプリ活用法 | 圏外 | 0 | 0 | 6,000円 | 3 | `40s-guide` |
| D | 雨の日デートプラン | 圏外 | 0 | 0 | 単価不明 | 1 | `amenohi-date-guide` |
| D | ブライダルインナーはどこで買う？必要性・選び方・専門店比較【 | 圏外 | 0 | 0 | **なし** | 0 | `bridal-inner-guide` |
| D | クリスマスプロポーズの逆算準備ガイド | 圏外 | 0 | 0 | **なし** | 0 | `christmas-propose-gyakusan` |
| D | Tapple vs with vs Pairs 20代向け比 | 圏外 | 0 | 0 | **なし** | 0 | `compare-20s` |
| D | 婚活アプリ比較 | 圏外 | 0 | 0 | 6,000円 | 3 | `compare-konkatsu` |
| D | 2回目・3回目のデートプラン | 圏外 | 0 | 0 | **なし** | 0 | `date-plan-2kaime` |
| D | デートで見ると気まずくなる作品の共通点 | 圏外 | 0 | 0 | 単価不明 | 1 | `date-sakuhin-ng` |
| D | 同棲・結婚で荷物が入らない問題 | 圏外 | 0 | 0 | 5,280円 | 2 | `dousei-nimotsu-trunkroom` |
| D | エンジニア・理系向けマッチングアプリガイド | 圏外 | 0 | 0 | 6,000円 | 2 | `engineer-guide` |
| D | 遠距離恋愛・遠距離婚活の続け方 | 圏外 | 0 | 0 | **なし** | 0 | `enkyori-renai-guide` |
| D | 夫婦・同棲カップルのスマホ代見直し手順 | 圏外 | 0 | 0 | **なし** | 0 | `futari-sumaho-minaoshi` |
| D | 結婚式のご祝儀・支払いはクレジットカードでできる？現金以外の | 圏外 | 0 | 0 | 単価不明 | 1 | `gosyugi-shiharai-houhou` |
| D | 結婚を機に転職すべきか | 圏外 | 0 | 0 | 12,450円 | 1 | `kekkon-tenshoku-guide` |
| D | 結婚内祝いのマナー完全ガイド | 圏外 | 0 | 0 | 単価不明 | 1 | `kekkon-uchiiwai-guide` |
| D | 結婚式の親族衣装・お呼ばれ服レンタルガイド | 圏外 | 0 | 0 | **なし** | 0 | `kekkonshiki-isho-rental` |
| D | 神戸・横浜でマッチングアプリを使うなら | 圏外 | 0 | 0 | 6,000円 | 2 | `kobe-yokohama-guide` |
| D | 国際結婚・外国人パートナーとの出会いと手続きガイド | 圏外 | 0 | 0 | **なし** | 0 | `kokusai-kekkon-guide` |
| D | 婚活・マッチングアプリのプロフィール写真戦略 | 圏外 | 0 | 0 | 1,800円 | 1 | `konkatsu-photo-guide` |
| D | 婚約指輪の相場データ | 圏外 | 0 | 0 | 単価不明 | 1 | `konyaku-yubiwa-data` |
| D | 子育てと両立できる働き方ガイド | 圏外 | 0 | 0 | **なし** | 0 | `kosodate-zaitaku-guide` |
| D | 前撮り・フォトウェディングの費用比較 | 圏外 | 0 | 0 | 6,000円 | 1 | `maedori-photo-guide` |
| D | マリッシュの再婚成婚データ | 圏外 | 0 | 0 | **なし** | 0 | `marrish-saikon-data` |
| D | マッチングアプリのメッセージ戦略 | 圏外 | 0 | 0 | 3,000円 | 1 | `message-strategy` |
| D | 2027年の入籍日はいつがいい？ | 圏外 | 0 | 0 | **なし** | 0 | `nyuseki-2027-guide` |
| D | Omiaiは30代女性に向いている？ | 圏外 | 0 | 0 | 6,000円 | 2 | `omiai-30s-women-data` |
| D | 大阪でマッチングアプリを使うなら | 圏外 | 0 | 0 | 6,000円 | 2 | `osaka-guide` |
| D | おうちデート完全ガイド | 圏外 | 0 | 0 | 797円 | 1 | `ouchi-date-guide` |
| D | ペアリングの選び方と相場データ | 圏外 | 0 | 0 | 600円 | 2 | `pair-ring-guide` |
| D | 離婚を考えたら最初にすること | 圏外 | 0 | 0 | 9,000円 | 1 | `rikon-junbi-jyunban` |
| D | 埼玉・千葉でマッチングアプリを使うなら | 圏外 | 0 | 0 | 6,000円 | 2 | `saitama-chiba-guide` |
| D | 非正規・フリーランスは結婚できない？雇用形態を聞かれたときの | 圏外 | 0 | 0 | 6,000円 | 2 | `seishain-igai-guide` |
| D | 仙台・広島でマッチングアプリを使うなら | 圏外 | 0 | 0 | 6,000円 | 2 | `sendai-hiroshima-guide` |
| D | 横浜プロポーズスポットガイド | 圏外 | 0 | 0 | **なし** | 0 | `yokohama-propose-spot` |
| D | ユーブライドの成婚率は公表されているか | 圏外 | 0 | 0 | **なし** | 0 | `youbride-seikon-data` |
| A | マッチングアプリの業者・詐欺を見分ける完全版 | 未計測 | — | — | **なし** | 0 | `anti-fraud` |
| A | 30代が婚活で使うPairs・with・Omiai比較 | 未計測 | — | — | 6,000円 | 2 | `compare-popular` |
| A | マッチングアプリ料金を男女・目的別に比較 | 未計測 | — | — | 単価不明 | 1 | `compare-price` |
| A | 同棲の始め方完全ガイド | 未計測 | — | — | 30,000円 | 2 | `dousei-hajimekata` |
| A | 同棲解消のリアル | 未計測 | — | — | **なし** | 0 | `dousei-kaisho` |
| A | 同棲か結婚か | 未計測 | — | — | 単価不明 | 1 | `dousei-kekkon-hikaku` |
| A | 同棲中の結婚のタイミング | 未計測 | — | — | 5,280円 | 1 | `dousei-kekkon-timing` |
| A | マッチングアプリがうまくいかない原因は5つに収束する | 未計測 | — | — | **なし** | 0 | `faq-troubleshooting` |
| A | マッチングアプリ初デート完全ガイド | 未計測 | — | — | **なし** | 0 | `first-date-guide` |
| A | マッチングアプリの業者・サクラ被害の実態 | 未計測 | — | — | **なし** | 0 | `fraud-statistics` |
| A | マッチングアプリの課金はいつ始めるべきか | 未計測 | — | — | **なし** | 0 | `free-vs-paid` |
| A | 2人暮らしの光回線選び | 未計測 | — | — | 30,000円 | 2 | `futari-hikari-kaisen` |
| A | 結婚後の口座・お金の管理方法 | 未計測 | — | — | 単価不明 | 1 | `futari-kouza-kanri` |
| A | 夫婦のクレジットカードは家族カードか別々か | 未計測 | — | — | 単価不明 | 1 | `fuufu-credit-kanri` |
| A | 初婚年齢の平均データ | 未計測 | — | — | 6,000円 | 2 | `hatsushon-nenmei-data` |
| A | 新婚の家電はレンタルと購入どちらが得か | 未計測 | — | — | 2,100円 | 2 | `kaden-rental-vs-kounyu` |
| A | マッチングアプリの年齢層×目的マップ | 未計測 | — | — | **なし** | 0 | `kaiin-age-cross-data` |
| A | 結婚後のスマホ代・格安SIM比較 | 未計測 | — | — | 30,000円 | 1 | `kazoku-simhikaku` |
| A | 新生活の契約で見落としがちな「実質」表記の罠 | 未計測 | — | — | **なし** | 0 | `keiyaku-jisshitsu-wana` |
| A | 結婚までにいくら貯めるべきか | 未計測 | — | — | 30,000円 | 1 | `kekkon-chokin-mokuhyou` |
| A | 結婚したら保険はどう見直す？加入タイミングと必要保障額の考え | 未計測 | — | — | 単価不明 | 1 | `kekkon-hoken-minaoshi` |
| A | 結婚後の住まい選び | 未計測 | — | — | **なし** | 0 | `kekkon-jutaku-loan` |
| A | 結婚前の身元・素行調査は必要か | 未計測 | — | — | 9,000円 | 2 | `kekkon-sokou-chousa` |
| A | 結婚前に確認すべき金銭感覚のすり合わせ | 未計測 | — | — | **なし** | 0 | `kinsen-kachikan-check` |
| A | 年末年始の帰省と結婚挨拶・手土産ガイド | 未計測 | — | — | 単価不明 | 1 | `kisei-kekkon-aisatsu` |
| A | 婚姻費用とは | 未計測 | — | — | **なし** | 0 | `koninhiyou-guide` |
| A | 婚活パーティーの選び方と料金相場 | 未計測 | — | — | 735円 | 2 | `konkatsu-party-guide` |
| A | 婚活アプリで結婚するには | 未計測 | — | — | 6,000円 | 3 | `konkatsu-roadmap` |
| A | 婚活の悩みは誰に相談すればいいか | 未計測 | — | — | 単価不明 | 2 | `konkatsu-soudan-saki` |
| A | 20代後半（25〜29歳）のマッチングアプリ戦略 | 未計測 | — | — | **なし** | 0 | `late-20s-strategy` |
| A | マッチングアプリのLINE交換タイミング | 未計測 | — | — | **なし** | 0 | `line-exchange` |
| A | 2026年最新マッチングアプリランキングTOP15 | 未計測 | — | — | 6,000円 | 1 | `matching-app-ranking` |
| A | マッチングアプリの男性費用データ | 未計測 | — | — | 6,000円 | 2 | `matching-dansei-cost-data` |
| A | マッチングアプリの女性費用 | 未計測 | — | — | 6,000円 | 2 | `matching-josei-cost-data` |
| A | マッチングアプリの男女比はどれくらい？会員数より先に見るべき | 未計測 | — | — | **なし** | 0 | `members-data` |
| A | 婚活・マッチングアプリ写真のためのメンズメイク入門 | 未計測 | — | — | 1,000円 | 1 | `mens-make-konkatsu` |
| A | mitas for men（ミタス男性用）の口コミ・成分検証 | 未計測 | — | — | **なし** | 0 | `mitas-formen-kuchikomi` |
| A | ミトコア300mgの口コミ・成分を検証 | 未計測 | — | — | **なし** | 0 | `mitocore-kuchikomi` |
| A | マイシード（男性妊活サプリ）の口コミ・成分を検証 | 未計測 | — | — | **なし** | 0 | `myseed-kuchikomi` |
| A | 結婚式をしない「ナシ婚」の割合データ | 未計測 | — | — | **なし** | 0 | `nashikon-data` |
| A | 看護師の婚活は結婚相談所が向いている？不規則勤務でも続く進め | 未計測 | — | — | 24,000円 | 2 | `nurse-konkatsu-soudanjo` |
| A | オタクの婚活はどう進めるか | 未計測 | — | — | 6,000円 | 1 | `otaku-konkatsu` |
| A | おうちデートで見る作品の選び方 | 未計測 | — | — | 単価不明 | 1 | `ouchi-date-sakuhin` |
| A | Pairs(ペアーズ)完全ガイド | 未計測 | — | — | 3,000円 | 1 | `pairs-guide` |
| A | Pairsの会員数はどこまで本当か | 未計測 | — | — | 6,000円 | 2 | `pairs-kaiin-data` |
| A | ペアーズの成婚率・結婚データ | 未計測 | — | — | **なし** | 0 | `pairs-marriage-data` |
| A | Pairs（ペアーズ）男性向け完全攻略 | 未計測 | — | — | **なし** | 0 | `pairs-men` |
| A | Pairs（ペアーズ）女性向け完全攻略 | 未計測 | — | — | **なし** | 0 | `pairs-women` |
| A | ペット好きの婚活はどう進めるか | 未計測 | — | — | 6,000円 | 1 | `pet-konkatsu` |
| A | マッチングアプリのプロフィール写真完全ガイド | 未計測 | — | — | 1,800円 | 1 | `photo-tips` |
| A | ぽっちゃり女性の婚活で体型はどう書くか | 未計測 | — | — | 6,000円 | 1 | `pocchari-konkatsu` |
| A | マッチングアプリ料金・会員数完全比較表【2026年版】 | 未計測 | — | — | **なし** | 0 | `price-comparison` |
| A | マッチングアプリで知り合いを見つけた・見つかった時の対処 | 未計測 | — | — | **なし** | 0 | `privacy-protection` |
| A | マッチングアプリのプロフィール文 | 未計測 | — | — | **なし** | 0 | `profile-text` |
| A | 恋活から婚活に切り替えるタイミング | 未計測 | — | — | **なし** | 0 | `renkatsu-vs-konkatsu` |
| A | 離婚した場合のお金の現実 | 未計測 | — | — | **なし** | 0 | `rikon-okane-genjitsu` |
| A | 安全なマッチングアプリの選び方 | 未計測 | — | — | **なし** | 0 | `safety-guide` |
| A | 作品の感想でわかる相手の結婚観 | 未計測 | — | — | **なし** | 0 | `sakuhin-kachikan` |
| A | 新婚生活の固定費見直し完全ガイド | 未計測 | — | — | 30,000円 | 1 | `shinkon-koteihi-minaoshi` |
| A | 新婚・同棲の引っ越しでネット回線はいつ手配する？ | 未計測 | — | — | 30,000円 | 2 | `shinkon-net-kaisen-dandori` |
| A | 新婚夫婦の初めてのおせち | 未計測 | — | — | 単価不明 | 2 | `shinkon-osechi` |
| A | 新婚旅行の支払いはどのクレジットカードが得か | 未計測 | — | — | 単価不明 | 1 | `shinkon-ryokou-credit` |
| A | 新居の家具・インテリア予算データ | 未計測 | — | — | 単価不明 | 2 | `shinkyo-kagu-yosan` |
| A | 静岡・新潟でマッチングアプリを使うなら | 未計測 | — | — | 単価不明 | 1 | `shizuoka-niigata-guide` |
| A | 結婚相談所の料金比較 | 未計測 | — | — | 10,452円 | 4 | `soudanjo-hikaku` |
| A | マッチングアプリで結婚した人の体験談 | 未計測 | — | — | **なし** | 0 | `success-stories` |
| A | 別居・単身赴任中の浮気の見抜き方 | 未計測 | — | — | 9,000円 | 2 | `tanshin-uwaki-mikiwame` |
| A | 探偵事務所の選び方・料金相場比較 | 未計測 | — | — | 9,000円 | 3 | `tantei-erabikata` |
| A | Tapple(タップル)完全ガイド【20代向け即デート実現戦 | 未計測 | — | — | 1,800円 | 1 | `tapple-guide` |
| A | タップルの真剣度は低い？ | 未計測 | — | — | 6,000円 | 2 | `tapple-seriousness-data` |
| A | TappleとPairs比較 | 未計測 | — | — | **なし** | 0 | `tapple-vs-pairs` |
| A | 転職理由ランキング | 未計測 | — | — | 6,000円 | 1 | `tenshoku-riyu-honne` |
| A | マッチングアプリの時間管理 | 未計測 | — | — | 3,000円 | 1 | `time-management` |
| A | 共働き夫婦の食事はどうしている？自炊・ミールキット・外食の費 | 未計測 | — | — | 797円 | 1 | `tomobataraki-shokuji-data` |
| A | 薄毛は婚活・マッチングアプリで本当に不利か | 未計測 | — | — | 6,000円 | 2 | `usuge-konkatsu-eikyou` |
| A | 浮気・不倫調査の基礎知識 | 未計測 | — | — | 9,000円 | 2 | `uwaki-chousa-kiso` |
| A | with（ウィズ）完全ガイド | 未計測 | — | — | **なし** | 0 | `with-guide` |
| A | withとPairs比較 | 未計測 | — | — | **なし** | 0 | `with-vs-pairs` |
| A | with（ウィズ）女性向けガイド | 未計測 | — | — | **なし** | 0 | `with-women` |
| A | マッチングアプリの女性向けガイド | 未計測 | — | — | **なし** | 0 | `women-strategy` |
| A | 家賃はクレジットカードで払える？手数料とポイント還元の損得を | 未計測 | — | — | 1,000円 | 1 | `yachin-credit-shiharai` |
| A | ユーブライドとマリッシュを徹底比較 | 未計測 | — | — | 6,000円 | 2 | `youbride-marrish-hikaku` |
| A | ゼクシィ縁結びの成婚率 | 未計測 | — | — | 6,000円 | 2 | `zexy-enmusubi-data` |

## ★クエリに答えていない記事

順位が付いているのに、そのクエリの語が本文にほとんど出てこない記事。
**開いても答えが見つからないので、順位があってもクリックされない。**

実例（2026-08-09に発見・修正済み）: `with-seriousness-data` は「with 結婚率」で4.2位・30表示だったが、
本文に「結婚率」が**1回しか無かった**。`over50-guide` は「婚活サイト 50代」で上位なのに
本文は「マッチングアプリ」16回に対し「婚活サイト」12回で主語が逆だった。

**答えが「その数字は公表されていない」でも構わない。**むしろ事業者は自社の不都合を書けないので空く。

| 順位 | 表示 | クエリ | 本文での出現 | 記事 |
|---|---|---|---|---|
| 17.0 | 1 | マッチングアプリ 結婚率 データ | **結婚率=2回** | `appkon-wariai-data` |
| 17.0 | 1 | 近く出会い | **近く出会い=0回** | `nagoya-guide` |
| 25.0 | 1 | 式場予約サイト | **式場予約サイト=0回** | `shikijo-erabi-guide` |
| 28.0 | 1 | マチアプ 大学生 社会人 | **マチアプ=0回** | `student-guide` |
| 29.0 | 1 | マッチングアプリ 平均年齢 | **平均年齢=0回** | `age-data` |
| 40.0 | 1 | マチアプ 結婚率 | **マチアプ=0回** | `success-rate-data` |
| 40.0 | 1 | マッチングアプリ 婚姻率 データ | **婚姻率=0回** | `success-rate-data` |
| 40.0 | 1 | 愛知/名古屋 マッチングアプリ | **愛知/名古屋=0回** | `nagoya-guide` |
| 43.5 | 2 | プロポーズ どうやって | **どうやって=0回** | `propose-guide` |
| 44.0 | 1 | 福岡 人気 マッチングアプリ | **人気=0回** | `fukuoka-guide` |
| 49.0 | 1 | 京都駅 出会い | **京都駅=2回** | `kyoto-guide` |
| 55.0 | 1 | ペアーズ 札幌 | **ペアーズ=1回** | `sapporo-guide` |
| 64.0 | 1 | 婚約期間 平均 | **婚約期間=0回** | `kekkon-madeno-kikan-data` |
| 67.0 | 1 | バチェラーデート サクラ | **サクラ=0回** | `bachelor-date-guide` |
| 74.0 | 1 | dine バチェラーデート | **dine=0回** | `bachelor-date-guide` |
| 74.0 | 2 | 婚活アプリ 20代 | **婚活アプリ=0回** | `20s-guide` |
| 75.0 | 1 | 新婚 年賀状 | **新婚=2回** | `kekkon-houkoku-nengajou` |
| 76.0 | 1 | マッチングアプリ成功率 | **マッチングアプリ成功率=0回** | `success-rate-data` |
| 78.0 | 1 | 結婚費用 平均 | **平均=2回** | `kekkon-okane-data` |
| 78.2 | 4 | 式場探し サイト おすすめ | **おすすめ=2回** | `shikijo-erabi-guide` |
| 80.0 | 1 | 結婚 費用 平均 | **平均=2回** | `kekkon-okane-data` |
| 81.0 | 1 | omiai ペアーズ | **omiai=0回** | `omiai-vs-pairs` |
| 81.5 | 2 | 婚活アプリ 50代 | **婚活アプリ=1回** | `over50-guide` |
| 82.0 | 1 | ペアーズ omiai | **ペアーズ=0回** | `omiai-vs-pairs` |
| 82.0 | 2 | 結婚式場 予約 方法 | **方法=0回** | `shikijo-erabi-guide` |
| 84.0 | 2 | デート 場所 決め方 | **決め方=0回** | `first-date-spot` |
| 84.0 | 2 | マッチングアプリ うまくいかない 疲れた 切り替え | **うまくいかない=1回** | `app-tsukare-guide` |
| 90.0 | 2 | マッチングアプリ うまくいかない 結婚相談所 費用 | **うまくいかない=2回** | `agency-vs-app` |
| 91.0 | 1 | 出会いアプリ 50代 | **出会いアプリ=0回** | `over50-guide` |
| 95.0 | 1 | 結婚相談所アプリ | **結婚相談所アプリ=0回** | `agency-vs-app` |

## ②が測れていない記事（17本）

CTAは貼られているが、台帳に単価の記載が無いため実効単価を計算できない。
**空欄は「案件なし」ではない。**この混同で判断を誤ったことがある（2026-08-09）。
afb / A8 の管理画面で単価と確定率を確認し、`AGENT.md` に追記すること。

`amenohi-date-guide`, `compare-price`, `date-sakuhin-ng`, `dousei-kekkon-hikaku`, `futari-kouza-kanri`, `fuufu-credit-kanri`, `gosyugi-shiharai-houhou`, `kekkon-hoken-minaoshi`, `kekkon-uchiiwai-guide`, `kisei-kekkon-aisatsu`, `konkatsu-soudan-saki`, `konyaku-yubiwa-data`, `ouchi-date-sakuhin`, `shinkon-osechi`, `shinkon-ryokou-credit`, `shinkyo-kagu-yosan`, `shizuoka-niigata-guide`


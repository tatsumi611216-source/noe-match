# GSC照合キュー（2026-08-19作成）

**「表示ゼロ×申請記録なし」のページ。** GSCで1件ずつ照合し、「リクエスト済み」なら台帳に記録、未申請なら申請する（1日10件）。

手順は index_request_queue.md と同じ。済んだら行頭に `[済]` を付ける。

**判定の自動化（2026-08-19 CEO承認）**: 1件ずつGSCで照合する代わりに、
実測則「申請済みなら7日で90〜100%インデックスされる」を使う。
**8/26 7:30に一回限りの定期タスク `affiliate-index-verify-20260826` が走り**、
インデックスされずに残ったものを「実質未申請」としてこのファイルに起票する。
それまでこのリストには手を付けなくてよい。

## 優先（63本）

```
[済] https://www.noe-match.com/articles/anti-fraud/
[済] https://www.noe-match.com/articles/compare-konkatsu/
[済] https://www.noe-match.com/articles/compare-popular/
https://www.noe-match.com/articles/compare-price/
[済] https://www.noe-match.com/articles/date-sakuhin-ng/
https://www.noe-match.com/articles/dousei-kaisho/
https://www.noe-match.com/articles/dousei-kekkon-hikaku/
[済] https://www.noe-match.com/articles/faq-troubleshooting/
https://www.noe-match.com/articles/first-date-guide/
https://www.noe-match.com/articles/fraud-statistics/
https://www.noe-match.com/articles/free-vs-paid/
[済] https://www.noe-match.com/articles/futari-hikari-kaisen/
https://www.noe-match.com/articles/hatsushon-nenmei-data/
https://www.noe-match.com/articles/kaiin-age-cross-data/
[済] https://www.noe-match.com/articles/keiyaku-jisshitsu-wana/
[済] https://www.noe-match.com/articles/kekkon-jutaku-loan/
[済] https://www.noe-match.com/articles/kekkon-sokou-chousa/
[済] https://www.noe-match.com/articles/kekkon-uchiiwai-guide/
https://www.noe-match.com/articles/kinsen-kachikan-check/
[済] https://www.noe-match.com/articles/kobe-yokohama-guide/
[済] https://www.noe-match.com/articles/kokusai-kekkon-guide/
https://www.noe-match.com/articles/koninhiyou-guide/
https://www.noe-match.com/articles/konkatsu-party-guide/
[済] https://www.noe-match.com/articles/konkatsu-photo-guide/
https://www.noe-match.com/articles/konkatsu-roadmap/
[済] https://www.noe-match.com/articles/konyaku-yubiwa-data/
[済] https://www.noe-match.com/articles/kosodate-zaitaku-guide/
https://www.noe-match.com/articles/late-20s-strategy/
https://www.noe-match.com/articles/line-exchange/
https://www.noe-match.com/articles/matching-josei-cost-data/
https://www.noe-match.com/articles/members-data/
https://www.noe-match.com/articles/myseed-kuchikomi/
https://www.noe-match.com/articles/nashikon-data/
[済] https://www.noe-match.com/articles/ouchi-date-sakuhin/
https://www.noe-match.com/articles/pairs-guide/
[済] https://www.noe-match.com/articles/pairs-marriage-data/
https://www.noe-match.com/articles/pairs-men/
https://www.noe-match.com/articles/pairs-women/
[済] https://www.noe-match.com/articles/pet-konkatsu/
https://www.noe-match.com/articles/price-comparison/
https://www.noe-match.com/articles/privacy-protection/
https://www.noe-match.com/articles/profile-text/
https://www.noe-match.com/articles/renkatsu-vs-konkatsu/
[済] https://www.noe-match.com/articles/rikon-junbi-jyunban/
[済] https://www.noe-match.com/articles/rikon-okane-genjitsu/
[済] https://www.noe-match.com/articles/sakuhin-kachikan/
[済] https://www.noe-match.com/articles/shinkon-osechi/
https://www.noe-match.com/articles/shinkyo-kagu-yosan/
[済] https://www.noe-match.com/articles/shizuoka-niigata-guide/
[済] https://www.noe-match.com/articles/success-stories/
https://www.noe-match.com/articles/tapple-guide/
https://www.noe-match.com/articles/tapple-vs-pairs/
https://www.noe-match.com/articles/tomobataraki-shokuji-data/
[済] https://www.noe-match.com/tools/fugenbyo-check/
[済] https://www.noe-match.com/tools/kekkon-shikin-keisanki/
[済] https://www.noe-match.com/tools/saigenbyo-check/
[済] https://www.noe-match.com/tools/soudanjo-simulator/
https://www.noe-match.com/articles/usuge-konkatsu-eikyou/
[済] https://www.noe-match.com/articles/uwaki-chousa-kiso/
https://www.noe-match.com/articles/with-guide/
https://www.noe-match.com/articles/with-vs-pairs/
[済] https://www.noe-match.com/articles/with-women/
[済] https://www.noe-match.com/articles/women-strategy/
```

## 後回し：ガルガル群（8/15-16に19本申請済みの記録があるため、重複の可能性が高い 20本）

```
[済] https://www.noe-match.com/articles/futarime-sango/
[済] https://www.noe-match.com/articles/garugaru-doukyo/
[済] https://www.noe-match.com/articles/garugaru-gibo-jitsubo/
https://www.noe-match.com/articles/garugaru-ki-itsumade/
[済] https://www.noe-match.com/articles/garugaru-nai-hito/
https://www.noe-match.com/articles/garugaru-otto-genkai/
[済] https://www.noe-match.com/articles/garugaru-otto-taiou/
https://www.noe-match.com/articles/garugaru-sangoutsu-chigai/
[済] https://www.noe-match.com/articles/garugaru-ueno-ko/
[済] https://www.noe-match.com/articles/gijikka-ikitakunai/
[済] https://www.noe-match.com/articles/ikukyu-fuufu-doji/
[済] https://www.noe-match.com/articles/maternity-blue-chigai/
[済] https://www.noe-match.com/articles/sango-crisis-guide/
https://www.noe-match.com/articles/sango-iraira/
[済] https://www.noe-match.com/articles/sango-kaji-buntan/
[済] https://www.noe-match.com/articles/sango-otto-kirai/
[済] https://www.noe-match.com/articles/sango-rikon/
[済] https://www.noe-match.com/articles/sango-satogaeri/
[済] https://www.noe-match.com/articles/satogaeri-shinai/
https://www.noe-match.com/articles/shinseiji-menkai/
```

---

## 判定結果（2026-08-26）

定期タスク `affiliate-index-verify-20260826` が 2026-08-27 07:31 に実行（8/26 7:30 予定分が翌朝に起動）。
`python scripts\index_check.py --refresh`（228URL・取得失敗0）→ `index_diff.py` の結果で突合した。

**判定則**：申請済みなら7日で90〜100%インデックスされる（実測）。
Day 8（8/09）から18日、8/22〜8/25の一括申請からも最短2日〜最長5日が経過した時点で**まだインデックスされていないものを「実質未申請」とみなす**。

### 優先（63本） → 済み 31本 / 要申請 32本

```
https://www.noe-match.com/articles/compare-price/                    → 要申請（Googleがこのページを認識していない）
https://www.noe-match.com/articles/matching-josei-cost-data/         → 要申請（Googleがこのページを認識していない）
https://www.noe-match.com/articles/myseed-kuchikomi/                 → 要申請（Googleがこのページを認識していない）
https://www.noe-match.com/articles/pairs-guide/                      → 要申請（Googleがこのページを認識していない）
https://www.noe-match.com/articles/tapple-guide/                     → 要申請（Googleがこのページを認識していない）
https://www.noe-match.com/articles/tapple-vs-pairs/                  → 要申請（Googleがこのページを認識していない）
https://www.noe-match.com/articles/tomobataraki-shokuji-data/        → 要申請（Googleがこのページを認識していない）
https://www.noe-match.com/articles/with-guide/                       → 要申請（Googleがこのページを認識していない）
https://www.noe-match.com/articles/free-vs-paid/                     → 要申請（クロール済み・インデックス未登録）
https://www.noe-match.com/articles/konkatsu-roadmap/                 → 要申請（クロール済み・インデックス未登録）
https://www.noe-match.com/articles/dousei-kaisho/                    → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/dousei-kekkon-hikaku/             → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/first-date-guide/                 → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/fraud-statistics/                 → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/hatsushon-nenmei-data/            → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/kaiin-age-cross-data/             → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/kinsen-kachikan-check/            → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/koninhiyou-guide/                 → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/konkatsu-party-guide/             → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/late-20s-strategy/                → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/line-exchange/                    → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/members-data/                     → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/nashikon-data/                    → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/pairs-men/                        → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/pairs-women/                      → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/price-comparison/                 → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/privacy-protection/               → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/profile-text/                     → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/renkatsu-vs-konkatsu/             → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/shinkyo-kagu-yosan/               → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/usuge-konkatsu-eikyou/            → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/with-vs-pairs/                    → 要申請（検出済み・未クロール）
```

### ガルガル群（20本） → 済み 15本 / 要申請 5本

```
https://www.noe-match.com/articles/garugaru-ki-itsumade/             → 要申請（Googleがこのページを認識していない）
https://www.noe-match.com/articles/garugaru-otto-genkai/             → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/garugaru-sangoutsu-chigai/        → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/sango-iraira/                     → 要申請（検出済み・未クロール）
https://www.noe-match.com/articles/shinseiji-menkai/                 → 要申請（検出済み・未クロール）
```

### 合計

| 群 | 本数 | 済み | 要申請 |
|---|---|---|---|
| 優先 | 63 | 31 | 32 |
| ガルガル群 | 20 | 15 | 5 |
| **合計** | **83** | **46** | **37** |

→ 要申請 37本を `index_request_queue.md` の B欄「2026-08-26 判定分」へ転記した（1日10件・上限が出るまで回す）。

**note対照群5本（kaden-rental-vs-kounyu / nurse-konkatsu-soudanjo / soudanjo-hikaku / tantei-erabikata / yachin-credit-shiharai）は今回のNG判定に1本も現れなかった**ため、申請禁止ルールに触れる転記は発生していない。

### 判定にあたって気づいた不整合（申請は行っていない）

- `garugaru-ki-itsumade` は台帳の「申請済み」表に **2026-08-13 申請** と記録されているが、14日たった今も `URL is unknown to Google`（＝Googleがこのページを一度も認識していない）。申請が実際には通っていなかったか、記録が誤っている可能性が高い。要申請として起票した。
- 8/25の自動タスクは `profile-text` の直前で割り当て上限に達しており、Fクラスタ残り（profile-text / privacy-protection / pairs-women / pairs-men / line-exchange / fraud-statistics / first-date-guide）が今回そのままNGで出た。**判定則と台帳の記録が一致している**＝この判定は信用してよい、という傍証になる。
- 逆に 8/22〜8/25 に申請した分（anti-fraud / success-stories / shizuoka-niigata-guide / women-strategy / with-women / sakuhin-kachikan / photo-tips / 各tools など）は**すべてインデックス済みに変わっていた**。

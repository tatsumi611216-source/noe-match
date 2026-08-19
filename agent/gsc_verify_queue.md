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
https://www.noe-match.com/articles/anti-fraud/
https://www.noe-match.com/articles/compare-konkatsu/
https://www.noe-match.com/articles/compare-popular/
https://www.noe-match.com/articles/compare-price/
https://www.noe-match.com/articles/date-sakuhin-ng/
https://www.noe-match.com/articles/dousei-kaisho/
https://www.noe-match.com/articles/dousei-kekkon-hikaku/
https://www.noe-match.com/articles/faq-troubleshooting/
https://www.noe-match.com/articles/first-date-guide/
https://www.noe-match.com/articles/fraud-statistics/
https://www.noe-match.com/articles/free-vs-paid/
https://www.noe-match.com/articles/futari-hikari-kaisen/
https://www.noe-match.com/articles/hatsushon-nenmei-data/
https://www.noe-match.com/articles/kaiin-age-cross-data/
https://www.noe-match.com/articles/keiyaku-jisshitsu-wana/
https://www.noe-match.com/articles/kekkon-jutaku-loan/
https://www.noe-match.com/articles/kekkon-sokou-chousa/
https://www.noe-match.com/articles/kekkon-uchiiwai-guide/
https://www.noe-match.com/articles/kinsen-kachikan-check/
https://www.noe-match.com/articles/kobe-yokohama-guide/
https://www.noe-match.com/articles/kokusai-kekkon-guide/
https://www.noe-match.com/articles/koninhiyou-guide/
https://www.noe-match.com/articles/konkatsu-party-guide/
https://www.noe-match.com/articles/konkatsu-photo-guide/
https://www.noe-match.com/articles/konkatsu-roadmap/
https://www.noe-match.com/articles/konyaku-yubiwa-data/
https://www.noe-match.com/articles/kosodate-zaitaku-guide/
https://www.noe-match.com/articles/late-20s-strategy/
https://www.noe-match.com/articles/line-exchange/
https://www.noe-match.com/articles/matching-josei-cost-data/
https://www.noe-match.com/articles/members-data/
https://www.noe-match.com/articles/myseed-kuchikomi/
https://www.noe-match.com/articles/nashikon-data/
https://www.noe-match.com/articles/ouchi-date-sakuhin/
https://www.noe-match.com/articles/pairs-guide/
https://www.noe-match.com/articles/pairs-marriage-data/
https://www.noe-match.com/articles/pairs-men/
https://www.noe-match.com/articles/pairs-women/
https://www.noe-match.com/articles/pet-konkatsu/
https://www.noe-match.com/articles/price-comparison/
https://www.noe-match.com/articles/privacy-protection/
https://www.noe-match.com/articles/profile-text/
https://www.noe-match.com/articles/renkatsu-vs-konkatsu/
https://www.noe-match.com/articles/rikon-junbi-jyunban/
https://www.noe-match.com/articles/rikon-okane-genjitsu/
https://www.noe-match.com/articles/sakuhin-kachikan/
https://www.noe-match.com/articles/shinkon-osechi/
https://www.noe-match.com/articles/shinkyo-kagu-yosan/
https://www.noe-match.com/articles/shizuoka-niigata-guide/
https://www.noe-match.com/articles/success-stories/
https://www.noe-match.com/articles/tapple-guide/
https://www.noe-match.com/articles/tapple-vs-pairs/
https://www.noe-match.com/articles/tomobataraki-shokuji-data/
https://www.noe-match.com/tools/fugenbyo-check/
https://www.noe-match.com/tools/kekkon-shikin-keisanki/
https://www.noe-match.com/tools/saigenbyo-check/
https://www.noe-match.com/tools/soudanjo-simulator/
https://www.noe-match.com/articles/usuge-konkatsu-eikyou/
https://www.noe-match.com/articles/uwaki-chousa-kiso/
https://www.noe-match.com/articles/with-guide/
https://www.noe-match.com/articles/with-vs-pairs/
https://www.noe-match.com/articles/with-women/
https://www.noe-match.com/articles/women-strategy/
```

## 後回し：ガルガル群（8/15-16に19本申請済みの記録があるため、重複の可能性が高い 20本）

```
https://www.noe-match.com/articles/futarime-sango/
https://www.noe-match.com/articles/garugaru-doukyo/
https://www.noe-match.com/articles/garugaru-gibo-jitsubo/
https://www.noe-match.com/articles/garugaru-ki-itsumade/
https://www.noe-match.com/articles/garugaru-nai-hito/
https://www.noe-match.com/articles/garugaru-otto-genkai/
https://www.noe-match.com/articles/garugaru-otto-taiou/
https://www.noe-match.com/articles/garugaru-sangoutsu-chigai/
https://www.noe-match.com/articles/garugaru-ueno-ko/
https://www.noe-match.com/articles/gijikka-ikitakunai/
https://www.noe-match.com/articles/ikukyu-fuufu-doji/
https://www.noe-match.com/articles/maternity-blue-chigai/
https://www.noe-match.com/articles/sango-crisis-guide/
https://www.noe-match.com/articles/sango-iraira/
https://www.noe-match.com/articles/sango-kaji-buntan/
https://www.noe-match.com/articles/sango-otto-kirai/
https://www.noe-match.com/articles/sango-rikon/
https://www.noe-match.com/articles/sango-satogaeri/
https://www.noe-match.com/articles/satogaeri-shinai/
https://www.noe-match.com/articles/shinseiji-menkai/
```

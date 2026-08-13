# 品質是正バックログ（2026-08-13 更新）

`scripts/factory_audit.py` が検出する、既存記事の品質基準未達分を積むファイル。
**削除もリライトもしない。加筆で基準まで持ち上げる**のが方針。

## 経緯

2026-08-13 の audit で 29本の FAIL を検出。前回（2026-08-09）の台帳には「バックログ完了」
と記録されていたが、実測では未達が残っていた。前回台帳が実態と乖離していた可能性が高い。
今回の実測値を正として、以下にバックログを登録する。

本記事生成ランでは age-data・first-date-spot の 2本のみ修正済み（.pr-notice 追加）。
残り 27本は次回以降のPhase 3 で対応。

## FAIL 欄（加筆待ち）

| スラッグ | 問題 | 実測 |
|---|---|---|
| amenohi-date-guide | 本文3,976字 | 4000字未満 |
| date-sakuhin-ng | 本文3,661字 | 4000字未満 |
| dousei-hajimekata | 本文3,923字 | 4000字未満 |
| dousei-kaisho | 本文3,290字 | 4000字未満 |
| dousei-kekkon-hikaku | 本文3,619字 / pr-notice欠落 | 複合 |
| dousei-kekkon-timing | 本文3,585字 | 4000字未満 |
| futari-kouza-kanri | 本文3,601字 | 4000字未満 |
| fuufu-credit-kanri | 本文3,397字 | 4000字未満 |
| gosyugi-shiharai-houhou | 本文3,241字 | 4000字未満 |
| kazoku-simhikaku | 本文3,334字 | 4000字未満 |
| keiyaku-jisshitsu-wana | 本文3,515字 | 4000字未満 |
| kekkon-jutaku-loan | 本文3,592字 | 4000字未満 |
| kekkon-okane-data | 本文3,055字 | 4000字未満 |
| kinsen-kachikan-check | 本文3,503字 | 4000字未満 |
| kokusai-kekkon-guide | 本文3,768字 | 4000字未満 |
| koninhiyou-guide | 本文3,962字 | 4000字未満 |
| konyaku-yubiwa-data | 本文3,167字 | 4000字未満 |
| kosodate-zaitaku-guide | 本文3,660字 | 4000字未満 |
| marrish-guide | 本文3,825字 | 4000字未満 |
| otaku-konkatsu | 本文3,997字 | 4000字未満 |
| rikon-okane-genjitsu | 本文3,601字 | 4000字未満 |
| sakuhin-kachikan | 本文3,497字 | 4000字未満 |
| shikijo-erabi-guide | 本文3,581字 | 4000字未満 |
| shinkon-koteihi-minaoshi | 本文3,846字 | 4000字未満 |
| shinkon-ryokou-credit | 本文3,371字 | 4000字未満 |
| soudanjo-hikaku | 本文3,267字 | 4000字未満 |
| youbride-guide | 本文3,984字 | 4000字未満 |

## 加筆の方針（次に未達が出たとき用に保持）

- **水増ししない**。文字数を満たすためだけの一般論の追加は、記事の主張を薄めるので禁止
- AGENT.mdの必須セクション（導入／比較表／本題／体験談2本／FAQ 5問／まとめ／著者情報）の
  うち、痩せている節を特定して深掘りする。多くは「本題（キーワード固有の深掘り）」が薄い
- 体験談は既存記事と名前・エピソードが重複しないこと（既存記事をgrepして確認）
- 「大手が書けない場所」の原則に沿った内容を足す。網羅性のための加筆ではない
- 1回の実行で最大2本まで。Phase 1の記事生成とは別枠で、Phase 3（月次メンテ）の時間を使う
- 加筆したら**本バックログから行を削除する**（実態と乖離しないよう）

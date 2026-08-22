# 品質是正バックログ（2026-08-23 実測で復元）

`scripts/factory_audit.py` が検出する、既存記事の品質基準未達分を積むファイル。
**削除もリライトもしない。加筆で基準まで持ち上げる**のが方針。
ここに載っているスラッグは検品で「既知バックログ」扱いになり、CIを赤にしない。
**加筆して4,000字を超えたら行を削除する。**

## 現在の状態（2026-08-23 実測・`python3 scripts/factory_audit.py --list`）

| 区分 | 本数 |
|---|---|
| 稼働記事 | 189 |
| FAIL（本文4,000字未満・最優先是正） | **38** |
| WARN（4,000〜6,000字） | 45 |

### FAIL 一覧（本文字数＝script/style/目次/広告表記/中盤CTAを除いた実文字数）

| slug | 本文字数 |
|---|---|
| shinkon-hojokin | 3,212 |
| kekkon-okane-data | 3,223 |
| tokyo-futari-seikatsuhi | 3,233 |
| konyaku-yubiwa-data | 3,240 |
| garugaru-sangoutsu-chigai | 3,255 |
| gosyugi-shiharai-houhou | 3,315 |
| maternity-blue-chigai | 3,363 |
| dousei-kaisho | 3,395 |
| kakeibo-app-fuufu | 3,415 |
| sengyoshufu-seikatsuhi | 3,416 |
| futarime-sango | 3,435 |
| shinkon-ryokou-credit | 3,441 |
| fuufu-credit-kanri | 3,462 |
| sango-rikon | 3,538 |
| dousei-kekkon-timing | 3,599 |
| date-sakuhin-ng | 3,600 |
| sakuhin-kachikan | 3,618 |
| kekkon-jutaku-loan | 3,623 |
| garugaru-doukyo | 3,626 |
| dousei-kekkon-hikaku | 3,633 |
| keiyaku-jisshitsu-wana | 3,652 |
| kosodate-zaitaku-guide | 3,663 |
| shinseiji-menkai | 3,663 |
| kinsen-kachikan-check | 3,674 |
| sango-kaji-buntan | 3,681 |
| kazoku-simhikaku | 3,708 |
| futari-kounetsuhi | 3,736 |
| rikon-okane-genjitsu | 3,739 |
| garugaru-ueno-ko | 3,750 |
| kokusai-kekkon-guide | 3,783 |
| ikukyu-fuufu-doji | 3,801 |
| marrish-guide | 3,826 |
| shikijo-erabi-guide | 3,870 |
| sango-iraira | 3,873 |
| gijikka-ikitakunai | 3,905 |
| sango-otto-kirai | 3,940 |
| satogaeri-shinai | 3,949 |
| futari-kouza-kanri | 3,958 |

## 経緯：2026-08-11 の「未達ゼロ」は誤計測だった

2026-08-11 にこのファイルを「55本すべて加筆済み（9,855〜13,678字）」として空にしたが、
その数値は**UTF-8のバイト数**だった（例：`gosyugi-shiharai-houhou` は当時「10,488字」と記録。
実測は git 履歴で 2026-07-26 作成時 2,995字 → 2026-08-23 現在 3,315字。一度も加筆されていない。
3,315字×3バイト≒10K）。

結果、バックログが空のまま FAIL 29〜38本が「新規違反」扱いになり、
2026-08-11 から 8/22 まで Factory Audit が**全コミットで赤**になっていた（失敗通知メール約90通）。

**文字数は必ず `scripts/factory_audit.py` の `body_text()` で測ること。**
`wc -c` やファイルサイズは文字数ではない。

## 加筆の方針

- **水増ししない**。文字数を満たすためだけの一般論の追加は、記事の主張を薄めるので禁止
- AGENT.mdの必須セクション（導入／比較表／本題／体験談2本／FAQ 5問／まとめ／著者情報）の
  うち、痩せている節を特定して深掘りする。多くは「本題（キーワード固有の深掘り）」が薄い
- 体験談は既存記事と名前・エピソードが重複しないこと（既存記事をgrepして確認）
- 「大手が書けない場所」の原則に沿った内容を足す。網羅性のための加筆ではない
- 1回の実行で最大2本まで。Phase 1の記事生成とは別枠で、Phase 3（月次メンテ）の時間を使う
- 加筆したら**本バックログから行を削除する**。削除前に `factory_audit.py` で実測する

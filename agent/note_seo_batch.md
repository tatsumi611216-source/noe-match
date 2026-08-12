# note SEO弾 バッチ台帳（クエリの使用記録・重複執筆の防止）

**新しいnote弾を書く前に、必ずこのファイルを確認する。**
「使用済み」「不合格」に載っているクエリ（および同義の言い換え）は書かない。
在庫は `note_query_inventory.md`、ルールの正本は `note_setup.md`。

## ゲート（2026-08-13にAIOゲートを追加）

1. **需要ゲート**: サジェストに実在するクエリのみ（`serp_screen.py`）
2. **UGCゲート**: SERPに知恵袋・note・アメブロ・小町等が1本以上
3. **AIOゲート（新設）**: 対象クエリでAI Overviewsが質問に直答している場合は不合格
   （0クリック化するため）。体験・個別事情系クエリを優先する。
   ※初回は自クエリ数件で「AIOが出る＝流入が来ない」を実測してから閾値を確定する
4. **カニバリゲート**: PDCA凍結クエリ・使用済みクエリと衝突しない
5. SERP実測時にPAA（他の人はこちらも検索）を必ず採取し `note_query_inventory.md` へ追記

## フェーズ1（2026-08-12執筆・7本）

**投稿2週間後に入率を判定**（対象クエリで100位以内に入った本数）。
判定: 3/7以上 → 朝晩2本へ増速 ／ 1/7以下 → 撤退して週3の現行運用のみ。

| # | ターゲットクエリ | タイトル | ファイル | note URL | 投稿日 | 送り先 | 2週間後 |
|---|---|---|---|---|---|---|---|
| 1 | 長男 結婚（家・苗字・同居） | 長男の結婚で揉めるのは3点だけ｜家を継ぐ・苗字・同居を決める順番 | 01-chonan-kekkon.html | https://note.com/hachimitsu88812/n/n7dc486fed0d2 | 2026-08-12（下書き） | propose-guide | |
| 2 | 非正規 結婚 反対 | 非正規だから結婚に反対される？親の不安を3つに翻訳して答える方法 | 02-hiseiki-kekkon-hantai.html | https://note.com/hachimitsu88812/n/n6466fe30c305 | 2026-08-12（下書き） | seishain-igai-guide | |
| 3 | 実家暮らし 婚活 不利 | 実家暮らしは婚活で不利？分かれ目は「理由の一言」と2つの答え方 | 03-jikkagurashi-konkatsu.html | https://note.com/hachimitsu88812/n/n6adcd52efb33 | 2026-08-12（下書き） | soudanjo-hikaku | |
| 4 | 持病 結婚 諦めた | 持病があると結婚は諦めるしかないのか｜伝える時期と場の選び方 | 04-jibyou-kekkon.html | https://note.com/hachimitsu88812/n/naa733257d3f3 | 2026-08-12（下書き） | soudanjo-hikaku | |
| 5 | 親の介護 結婚 諦める | 親の介護で結婚を諦める前に。「できない」を3つに分解して考える | 05-oyakaigo-kekkon.html | https://note.com/hachimitsu88812/n/nb998a29df1f3 | 2026-08-12（下書き） | soudanjo-hikaku | |
| 6 | マッチングアプリ 疲れた | マッチングアプリに疲れた——原因3分類でわかる休み方と次の選択肢 | 06-app-tsukareta.html | https://note.com/hachimitsu88812/n/nabb6ef6313ed | 2026-08-12（下書き） | app-tsukare-guide | |
| 7 | オタク 婚活（場の選び方） | オタクの婚活はどこでやる？アプリ・パーティー・専門相談所の使い分け | 07-otaku-konkatsu-basho.html | https://note.com/hachimitsu88812/n/n664e5eb62dcf | 2026-08-12（下書き） | otaku-konkatsu | |

**アイキャッチ**: 7本すべて設定済み（2026-08-12・みんなのフォトギャラリー経由・API `eyecatch` と実画像の目視で検品PASS）。
1=父と子の夕日 ／ 2=PC作業 ／ 3=住まいインテリア ／ 4=白い小花 ／ 5=手を取る手 ／ 6=スマホを見る女性イラスト ／ 7=ゲームコントローラー。
※ギャラリーのグリッドは座標クリックがズレる。**画像選択はJSでimg列挙→タイトル確認→dispatchクリック**が確実（6本目で1タイル隣を掴んだ実績）。

## フェーズ1追加バッチ（2026-08-12夜・7本）

CEO指示「追加で7本」。UGCゲート実測済み（全て知恵袋等1本以上をSERPで確認）。

| # | ターゲットクエリ | ファイル | note URL | 投稿日 | 送り先 | 状態 |
|---|---|---|---|---|---|---|
| 8 | 低収入 結婚 諦めた | 08-teishunyu-kekkon.html | https://note.com/hachimitsu88812/n/n80759a7db023 | 2026-08-12（下書き） | seishain-igai-guide＋kekkon-okane-data | 下書き完成 |
| 9 | 結婚 諦めた 男 | 09-kekkon-akirameta-otoko.html | https://note.com/hachimitsu88812/n/ncae22ddd9b59 | 2026-08-12（下書き） | soudanjo-hikaku＋agency-vs-app | 下書き完成 |
| 10 | 40代 独身 女性 婚活 | 10-40dai-dokushin-josei.html | https://note.com/hachimitsu88812/n/n9ced48eb07d4 | 2026-08-12（下書き） | soudanjo-hikaku＋agency-vs-app | 下書き完成 |
| 11 | 一人っ子 結婚 後悔 | 11-hitorikko-kekkon.html | https://note.com/hachimitsu88812/n/n72bd12e01cf3 | 2026-08-12（下書き） | propose-guide | 下書き完成 |
| 12 | ぽっちゃり 婚活 | 12-pocchari-konkatsu.html | https://note.com/hachimitsu88812/n/nbd1bb59a8109 | 2026-08-12（下書き） | soudanjo-hikaku＋profile-text | 下書き完成 |
| 13 | 顔合わせ 揉めた | 13-kaoawase-mometa.html | https://note.com/hachimitsu88812/n/nb3e0438ef05d | 2026-08-12（下書き） | propose-guide | 下書き完成 |
| 14 | 看護師 出会いがない | 14-kangoshi-deai.html | https://note.com/hachimitsu88812/n/n058847e621bf | 2026-08-12（下書き） | nurse-guide | 下書き完成 |

**アイキャッチ**: 8〜14の7本すべて設定済み（ギャラリー経由・API `eyecatch` 検証済み）。
8=窓辺の家計ノート ／ 9=北海道の一本道 ／ 10=コーヒーカップ ／ 11=紅葉の親子水彩 ／ 12=洋服を選ぶ女の子イラスト ／ 13=乾杯 ／ 14=看護師の写真。
※トリミング「保存」はJS click()が効かないことがある→**pointerover〜mouseupを撃ってからclick**。挿入後はcropperのdata:image読込完了を待ってから保存。

※14はタイトル・見出しに「夜勤 恋愛」の並びを使わない（PDCA凍結クエリ保護）。
※「マッチングアプリ やめたい」は#6（疲れた）とカニバるため見送り。

## ゲート不合格（再挑戦しない・理由つき）

| クエリ | 不合格の理由（実測日 2026-08-12） |
|---|---|
| 浮気 確かめる方法 | マイナビウーマン・Smartlog・ベンナビが占有。UGCゼロ＝大手メディアの本丸 |
| 婚約者 浮気 どうする | 弁護士事務所SERP。慰謝料系は士業占有＋YMYL |
| 一人っ子 結婚 親の介護 | 介護施設メディア＋厚労省。UGCゼロ（※「親の介護 結婚 諦める」は別SERPで合格） |
| 結婚相談所 料金（系全般） | ナレソメ・oricon・GMO等の完全占有。noteでも入れない層 |
| 結婚 転職 タイミング | 転職エージェント（Geekly・Re就活・type）の集客語 |

## 執筆禁止（カニバリ防止・PDCA凍結 2026-09-09まで）

バツイチ 恋愛 ／ 夜勤 恋愛 ／ 非正規 結婚できない ／ 東京 待ち合わせ ／
業者 見分け方 ／ 公務員 出会い ／ 婚活サイト 50代 ／ マリッシュ 料金・評判
（8/9〜12にnoe-match本体の看板を掛け替えたターゲットクエリ。noteで書くと判定を汚す）

## 運用メモ

- 既存noteの週3本（火金日・エッセイ型）とは別枠。**5週目のビュー判定の分母に入れない**
- 使用済みクエリの確認コマンド: `grep -i "クエリの語" agent/note_seo_batch.md agent/note_query_inventory.md`

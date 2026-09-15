# SEO Rank Watch 報告

手順は `.claude/skills/seo-rank-watch/SKILL.md`。新しい回を末尾に追記する。

## 2026-09-16（初期設定）
- データ: 28日窓 2026-08-15〜2026-09-11 / 7日窓 2026-09-05〜2026-09-11
- 監視語を13語登録（20位以内・表示ありのクエリから、同じ意図の表記ゆれは variants にまとめた）
- 初回計測を rank-history.json に記録（28日窓・7日窓 各13行）
- 効果判定: 対象なし（初回）
- 改善: この回は実施していない（仕組みの設置のみ）
- observing 中: なし

## 2026-09-16
- データ: 28日窓 2026-08-15〜2026-09-11 / 7日窓 2026-09-05〜2026-09-11（アーカイブは今日から5日遅れ・欠測なし）
- 大きく動いた語（28日窓・前回比±2以上）: なし（初期設定と同じ窓のため前回比なし。rank-history 追記0件）
- 効果判定: 対象なし（observing 項目なし）
- 今日選んだ語と選定理由: 「with 成婚率」→ /articles/with-seriousness-data/。28日窓 4.8位・表示62・クリック1で、2〜10位の中で最も1位に近い（7日窓は2.6位・表示12）。priority high。locks・observing・直近7日の他自動化の変更いずれにも該当しない
- 推測した検索ニーズ: withで婚活を考えている人が、withで実際に何%が結婚しているのか、公式の数字があるのかを知りたい
- ギャップ: title/H1 に主要語「成婚率」が無い（「結婚率」のみ）／with公式「結婚レポート」ページ（体験談のみ・数値なし）に触れていない／相談所の成婚率とアプリの違いの説明が無い／FAQに「成婚率は何％？」の直接の問いが無い
- 実際に行った改善（ファイル・公開確認の結果）: articles/with-seriousness-data/index.html — title・og・twitter・H1・JSON-LD headline を「withの成婚率・結婚率は公表されていない｜代わりに確認できる数字を整理した」に同期、成婚率の定義と公式結婚レポートの現状（9/16確認）を2段落追加、基本データ表の確認日更新、FAQ先頭にQ1「withの成婚率は何％ですか？」追加（FAQPage JSON-LDにも反映）、dateModified 2026-09-16・sitemap lastmod 同期。factory_audit exit 0。公開確認は次行
- 承認待ちの提案: なし
- observing 中: with 成婚率 — 2026-09-23（GSCが約5日遅れのため、この日はデータ待ちになる見込み）
- 公開確認: Deploy to Pages run 35006539284（headSha aca0efb）success。本番 https://www.noe-match.com/articles/with-seriousness-data/ で新title・「結婚レポート」段落・FAQ Q1・最終更新 2026年9月16日 の反映を確認

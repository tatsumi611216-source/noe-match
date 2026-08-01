# noe-match

noe-match.com（婚活・結婚のアフィリエイトサイト）のソース。GitHub Pages で
リポジトリのルートをそのまま配信している。記事は週次で自動実行される
「記事工場エージェント」が生成する。

## 作業前に読むファイル

| ファイル | 内容 |
|---------|------|
| `agent/AGENT.md` | 週次の実行手順・記事の品質基準・アフィリエイト台帳・Phase 2〜4 |
| `agent/PHILOSOPHY.md` | 運営方針と判断基準。**新しいテーマ・切り口・案件配置を決めるときは必ず読む** |
| `agent/run_log.md` | 過去の実行記録 |

記事の生成・強化を行う場合は `agent/AGENT.md` の手順に従うこと。
このファイルはその要約ではなく、入口の案内にすぎない。

## 守ること

- **`sitemap.xml` / `index.html` / `articles/` の記事集合は常に一致させる。**
  変更したら `python3 scripts/check_consistency.py` を実行して終了コード0を確認する
- **`_config.yml` の `exclude` を安易に削らない。** `agent/` にはアフィリエイト
  案件の単価・承認率、GSC実績、note下書きが入っている。除外を外すと
  noe-match.com 上から誰でも読める状態になる
- **`.nojekyll` を置かない。** `about.md` / `privacy-policy.md` / `disclaimer.md` は
  フロントマター付きで、Jekyllが変換した `/about.html` 等にサイト内からリンクしている
- `about.md` / `privacy-policy.md` / `disclaimer.md` / `CNAME` / `robots.txt` は
  エージェントの自動実行では変更しない
- 既存記事の削除・改名はしない（リダイレクトstubが残るため）

## ディレクトリ

```
articles/<slug>/index.html   記事本体（実記事142本 ＋ 旧slugのリダイレクトstub48本）
images/                      記事用の画像
agent/                       エージェントの運用ファイル（非公開・_config.ymlで除外）
scripts/                     GSC取得・整合性チェック（非公開）
docs/archive/                初期構築時の一回限りのレポート・スクリプト（非公開）
redirects.json               旧slug → 新slug。server.py のローカル確認で使う
server.py                    ローカル確認用のFlaskサーバー
```

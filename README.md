# noe-match

[noe-match.com](https://www.noe-match.com/) — 婚活・結婚のライフイベント
（出会い→婚約→結婚→新生活）を扱う情報サイトのソース。

GitHub Pages がこのリポジトリのルートを Jekyll でビルドして配信している。
記事は週次で自動実行される「記事工場エージェント」が生成する。

## 構成

| パス | 内容 | 公開 |
|------|------|------|
| `index.html` | トップページ（記事一覧） | ✅ |
| `articles/<slug>/index.html` | 記事本体。実記事142本＋旧slugのリダイレクトstub48本 | ✅ |
| `images/` | 記事用の画像 | ✅ |
| `about.md` `privacy-policy.md` `disclaimer.md` | Jekyllが `/about.html` 等に変換 | ✅ |
| `sitemap.xml` `sitemap-all.xml` `robots.txt` `CNAME` | サイト設定 | ✅ |
| `google4df9c44513d0200e.html` | Search Console の所有権確認ファイル | ✅ |
| `28fb2874520d40719aa81fc0618e863b.txt` | IndexNow のキーファイル（ルート配信が必須） | ✅ |
| `agent/` | エージェントの運用ファイル（手順書・案件台帳・GSC実績・note下書き） | ❌ |
| `scripts/` | GSCデータ取得・整合性チェック | ❌ |
| `docs/archive/` | 初期構築時の一回限りのレポート・スクリプト | ❌ |
| `redirects.json` `article_slugs.json` `server.py` | ローカル確認用 | ❌ |

「公開 ❌」は `_config.yml` の `exclude` で配信対象から外していることを意味する。
`agent/` にはアフィリエイト案件の単価・承認率が入っているため、除外を外さないこと。

## よく使うコマンド

```bash
# 記事集合・記事数表記・内部リンクの整合性チェック（記事を追加したら必ず実行）
python3 scripts/check_consistency.py

# ローカルで確認する
python3 server.py

# GSCデータの取得（通常は .github/workflows/fetch-gsc.yml が毎週日曜に実行）
python3 scripts/fetch_gsc.py
```

## エージェントの運用

手順は `agent/AGENT.md`、方針と判断基準は `agent/PHILOSOPHY.md` にある。
Claude Code で作業する場合の入口は `CLAUDE.md`。

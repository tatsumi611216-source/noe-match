# 採用HR営業ソーシングツール

企業の公開求人を毎日収集し、「採用に困っている企業」を営業リスト化するツール。
ターゲットは採用・HR関連サービスの営業（人材紹介／採用代行／ダイレクトリクルーティング）。

- 詳細な要件・販売性評価: [REQUIREMENTS.md](REQUIREMENTS.md)
- 全データ項目と取得元: [DATA_DICTIONARY.md](DATA_DICTIONARY.md)

## 収集ソース（規約クリーンに限定）

自社採用ページの schema.org JobPosting 構造化データを主軸に、資金調達リリース・
J-Startup・VCポートフォリオ・ハローワークを組み合わせる。企業マスタは gBizINFO
（経産省・無料API）／法人番号／EDINET で補完。**大手有料求人媒体・会員限定データは対象外。**

## セットアップ

```bash
cd sourcing
python3 init_db.py            # data/sourcing.db を作成＋カテゴリ初期投入
```

## 実行フロー（Phase 1b）

```bash
# 1. 起点リスト（採用ページURLの種）を投入  ※CSVはJPX一覧/調達リリース等から用意
python3 scripts/load_seed.py seed.csv

# 2. 採用ページを巡回して求人を取得・DB反映（robots遵守・条件付きGET・並列）
python3 scripts/crawl.py seed_careers.json --source careers --workers 8

# 3. gBizINFOで企業マスタを補完（資本金・従業員・業種など）※要APIトークン
export GBIZINFO_API_TOKEN=xxxx
python3 scripts/gbiz_client.py

# 4. 採用の困り度スコアを算出
python3 scripts/score.py

# 5. HTMLレポート生成 → outputs/report.html
python3 scripts/generate_report.py
```

## スクリプト構成

| ファイル | 役割 | 状態 |
|---|---|---|
| init_db.py | DB初期化＋カテゴリ初期投入 | ✅ |
| scripts/common.py | 名寄せ正規化・カテゴリ分類・DB接続 | ✅ |
| scripts/extract_jobposting.py | 採用ページ→JobPosting抽出 | ✅ |
| scripts/http_cache.py | 条件付きGET（差分取得） | ✅ |
| scripts/crawl.py | 採用ページ巡回クローラ（robots/並列/差分） | ✅ |
| scripts/load_seed.py | 起点リストCSV→企業マスタ | ✅ |
| scripts/update_db.py | 求人取り込み・名寄せ・差分掲載終了 | ✅ |
| scripts/gbiz_client.py | gBizINFOエンリッチ（パース済／実接続は要トークン） | ◐ |
| scripts/score.py | 採用の困り度スコア | ✅ |
| scripts/generate_report.py | HTMLレポート生成 | ✅ |

## テスト

```bash
python3 tests/test_pipeline.py   # 抽出→取込→名寄せ→差分→スコア→ビュー
python3 tests/test_crawl.py      # シード→クロール(file://)→取込→gBizパース
```

## 未実装（次工程）

- 起点リストの自動生成（JPX上場一覧の取得、資金調達リリースの収集・パース）
- EDINET有報からの子会社抽出（corporate_relations の自動構築）
- 採用ページに JobPosting が無いサイトの素HTMLフォールバック
- 定期実行（毎朝の差分巡回）・CSVエクスポート

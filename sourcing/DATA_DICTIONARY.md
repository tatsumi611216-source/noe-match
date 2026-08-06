# データ項目定義書（データディクショナリ）

営業ソーシングDBが保持する項目と、その主な取得元。
「販売可能な企業データベース」として網羅性を確保するための定義。schema.sql と対応。

## companies（企業マスタ）

| 項目 | 型 | 内容 | 主な取得元 |
|---|---|---|---|
| name / name_normalized | TEXT | 企業名 / 名寄せキー | 各ソース共通 |
| corporate_number | TEXT | 法人番号（13桁）。全ソース横断の結合キー | 国税庁法人番号 / gBizINFO |
| industry / industry_code | TEXT | 業種 / 日本標準産業分類 | gBizINFO |
| business_summary | TEXT | 事業概要 | gBizINFO / 採用ページ |
| website / careers_url | TEXT | 企業サイト / 採用ページ（クロール対象） | gBizINFO / 探索 |
| representative_name | TEXT | 代表者名 | gBizINFO / 法人番号 |
| established_date | TEXT | 設立年月 | gBizINFO |
| capital_yen | INTEGER | 資本金 | gBizINFO |
| revenue_yen | INTEGER | 売上高 | gBizINFO(財務) / EDINET |
| employee_count | INTEGER | 従業員数 | gBizINFO |
| postal_code / prefecture / city / address | TEXT | 本社所在地 | gBizINFO / 法人番号 |
| phone | TEXT | 代表電話 | 採用ページ / 公開情報 |
| **is_listed** | INT | 上場フラグ | JPX上場一覧 |
| listing_market / ticker | TEXT | 市場区分 / 証券コード | JPX / EDINET |
| **is_subsidiary** | INT | 子会社フラグ（上場子会社の判定含む） | EDINET(関係会社) |
| parent_name / parent_corporate_number | TEXT | 親会社 | EDINET |
| ultimate_parent_name | TEXT | 最終親会社（グループ最上位） | EDINET |
| **is_foreign_affiliated** | INT | 外資系フラグ | 東洋経済外資系総覧 / JETRO / 有報 / 商号ヒューリスティック |
| foreign_parent_country / foreign_ownership_pct | TEXT/REAL | 外国親会社の国籍 / 外資比率 | 同上 |
| **funding_stage** | TEXT | 調達ステージ | 資金調達リリース / VCポートフォリオ |
| first/last_funding_date, last/total_funding_yen | - | 調達履歴 | PR TIMES等の調達リリース |
| source_list | TEXT | 起点リスト識別子 | 収集メタ |
| gbiz_synced_at | TEXT | gBizINFO最終同期日 | 収集メタ |
| sales_status | TEXT | 営業ステータス | 手動 / 営業活動 |
| priority_score | REAL | 採用の困り度スコア | score.py 算出 |

## corporate_relations（企業グループ関係）

| 項目 | 内容 | 取得元 |
|---|---|---|
| parent_name / parent_corporate_number | 親会社 | EDINET 有報「関係会社の状況」 |
| child_name / child_corporate_number | 子会社・関連会社 | 同上 |
| relation_type | 子会社/関連会社/親会社/持分法適用 | 同上 |
| ownership_pct | 議決権所有割合 | 同上 |

## job_postings（求人案件）

| 項目 | 内容 | 取得元 |
|---|---|---|
| title / employment_type | 職種名 / 雇用形態 | 採用ページ JobPosting |
| category_id | 職種カテゴリ（自動分類） | classify() |
| salary_min / salary_max | 給与（月給換算・円） | JobPosting baseSalary |
| location | 勤務地 | JobPosting jobLocation |
| posted_at / first_seen_at / last_seen_at | 掲載日 / 初検知 / 最終検知 | 収集 |
| is_active | 掲載中フラグ（差分で自動更新） | 差分ロジック |

## 公開データソースの位置づけ

| ソース | 提供 | 費用 | 役割 |
|---|---|---|---|
| gBizINFO REST API | 経産省 | 無料（1日1万回） | 企業マスタの背骨（資本金/従業員/業種/設立/財務/所在地） |
| 法人番号公表サイト | 国税庁 | 無料 | 法人番号・商号・所在地の一次マスタ |
| EDINET API | 金融庁 | 無料（要APIキー） | 上場企業の有報→関係会社（子会社）構造・財務 |
| JPX 上場会社一覧 | 日本取引所 | 無料 | 上場企業の起点リスト・市場区分・証券コード |
| 資金調達リリース（PR TIMES等） | 各社 | 無料（公開情報） | スタートアップ抽出・調達シグナル |
| J-Startup / VCポートフォリオ | 経産省 / 各VC | 無料（公開） | 有力スタートアップの起点リスト |
| 東洋経済「外資系企業総覧」 | 東洋経済 | 有料 | 外資系の権威データ（ライセンス購入で精度確保） |

> 大手有料求人媒体（doda/リクルート/ビズリーチ/リクナビ/マイナビ等）および会員限定データは、
> 規約・法令の観点から収集対象に含めない。データを外部販売する場合、出所の適法性は必須要件。

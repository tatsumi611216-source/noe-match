-- 営業ソーシングツール データベーススキーマ (SQLite)
-- 正とするスキーマ定義。変更時は DATA_DICTIONARY.md / REQUIREMENTS.md も更新すること。
-- マスタ項目の主な取得元: gBizINFO(経産省/無料API)・法人番号公表サイト・EDINET(有報/関係会社)。

PRAGMA foreign_keys = ON;

-- 職種カテゴリマスタ
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    keywords    TEXT NOT NULL DEFAULT '',
    sort_order  INTEGER NOT NULL DEFAULT 100
);

-- 企業マスタ（営業リストの本体＋販売可能な網羅的プロフィール）
CREATE TABLE IF NOT EXISTS companies (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    -- 識別
    name            TEXT NOT NULL,
    name_normalized TEXT NOT NULL UNIQUE,       -- 名寄せキー
    corporate_number TEXT UNIQUE,               -- 法人番号13桁（gBizINFO/法人番号サイトの結合キー）
    -- 事業プロフィール（gBizINFO由来）
    industry        TEXT,                        -- 業種（営業品目）
    industry_code   TEXT,                        -- 日本標準産業分類コード
    business_summary TEXT,                       -- 事業概要
    website         TEXT,
    careers_url     TEXT,                        -- 採用ページURL（クロール対象）
    representative_name TEXT,                    -- 代表者名
    established_date TEXT,                        -- 設立年月
    capital_yen     INTEGER,                     -- 資本金（円）
    revenue_yen     INTEGER,                     -- 売上高（円）
    employee_count  INTEGER,                     -- 従業員数
    -- 所在地・連絡先
    postal_code     TEXT,
    prefecture      TEXT,
    city            TEXT,
    address         TEXT,
    phone           TEXT,
    -- 上場・グループ構造
    is_listed       INTEGER NOT NULL DEFAULT 0,  -- 1=上場
    listing_market  TEXT,                        -- プライム/スタンダード/グロース等
    ticker          TEXT,                        -- 証券コード
    is_subsidiary   INTEGER NOT NULL DEFAULT 0,  -- 1=いずれかの企業の子会社（上場子会社の判定含む）
    parent_name     TEXT,                        -- 親会社名
    parent_corporate_number TEXT,                -- 親会社の法人番号
    ultimate_parent_name TEXT,                   -- 最終親会社（グループ最上位）
    -- 外資
    is_foreign_affiliated INTEGER NOT NULL DEFAULT 0, -- 1=外資系（外国資本1/3超等）
    foreign_parent_country TEXT,                 -- 外国親会社の国籍
    foreign_ownership_pct REAL,                  -- 外資比率(%)
    -- 資金調達（スタートアップ判定）
    funding_stage   TEXT,                         -- シード/シリーズA/B/C/D以降/未公開
    first_funding_date TEXT,
    last_funding_date  TEXT,
    last_funding_yen   INTEGER,
    total_funding_yen  INTEGER,                   -- 累計調達額（円）
    -- 収集メタ・営業管理
    source_list     TEXT,                         -- 起点: 'jpx' / 'prtimes' / 'jstartup' / 'vc:XXX' / 'edinet' / 'gbiz'
    gbiz_synced_at  TEXT,                          -- gBizINFO最終同期日
    sales_status    TEXT NOT NULL DEFAULT '未接触'
                    CHECK (sales_status IN ('未接触','アプローチ中','商談','成約','見送り','対象外')),
    priority_score  REAL NOT NULL DEFAULT 0,
    memo            TEXT,
    first_seen_at   TEXT NOT NULL DEFAULT (date('now')),
    last_seen_at    TEXT NOT NULL DEFAULT (date('now')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_companies_status  ON companies (sales_status);
CREATE INDEX IF NOT EXISTS idx_companies_pref    ON companies (prefecture);
CREATE INDEX IF NOT EXISTS idx_companies_listed  ON companies (is_listed);
CREATE INDEX IF NOT EXISTS idx_companies_foreign ON companies (is_foreign_affiliated);
CREATE INDEX IF NOT EXISTS idx_companies_corpnum ON companies (corporate_number);

-- 企業グループ関係（EDINET 有報「関係会社の状況」等から構築。上場子会社の把握に使用）
CREATE TABLE IF NOT EXISTS corporate_relations (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_corporate_number TEXT,
    parent_name            TEXT NOT NULL,
    child_corporate_number  TEXT,
    child_name             TEXT NOT NULL,
    relation_type          TEXT NOT NULL DEFAULT '子会社'
                           CHECK (relation_type IN ('子会社','関連会社','親会社','持分法適用')),
    ownership_pct          REAL,
    source                 TEXT DEFAULT 'edinet',
    disclosed_date         TEXT,
    UNIQUE (parent_name, child_name, relation_type)
);

CREATE INDEX IF NOT EXISTS idx_relations_child  ON corporate_relations (child_name);
CREATE INDEX IF NOT EXISTS idx_relations_parent ON corporate_relations (parent_name);

-- 求人案件
CREATE TABLE IF NOT EXISTS job_postings (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id     INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    category_id    INTEGER REFERENCES categories(id),
    source_site    TEXT NOT NULL,
    source_job_id  TEXT NOT NULL,
    title          TEXT NOT NULL,
    employment_type TEXT,
    salary_min     INTEGER,
    salary_max     INTEGER,
    location       TEXT,
    url            TEXT,
    raw_file       TEXT,
    posted_at      TEXT,
    first_seen_at  TEXT NOT NULL DEFAULT (date('now')),
    last_seen_at   TEXT NOT NULL DEFAULT (date('now')),
    is_active      INTEGER NOT NULL DEFAULT 1,
    UNIQUE (source_site, source_job_id)
);

CREATE INDEX IF NOT EXISTS idx_postings_company  ON job_postings (company_id);
CREATE INDEX IF NOT EXISTS idx_postings_category ON job_postings (category_id, is_active);

-- 営業活動履歴
CREATE TABLE IF NOT EXISTS sales_activities (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id    INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    activity_date TEXT NOT NULL DEFAULT (date('now')),
    activity_type TEXT NOT NULL CHECK (activity_type IN ('架電','メール','訪問','オンライン商談','その他')),
    result        TEXT,
    next_action   TEXT,
    next_action_date TEXT,
    memo          TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_activities_company ON sales_activities (company_id, activity_date);

-- カテゴリ別日次統計
CREATE TABLE IF NOT EXISTS daily_category_stats (
    stat_date     TEXT NOT NULL,
    category_id   INTEGER NOT NULL REFERENCES categories(id),
    active_count  INTEGER NOT NULL DEFAULT 0,
    new_count     INTEGER NOT NULL DEFAULT 0,
    company_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (stat_date, category_id)
);

-- 収集実行ログ
CREATE TABLE IF NOT EXISTS crawl_runs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date      TEXT NOT NULL DEFAULT (date('now')),
    source_site   TEXT NOT NULL,
    pages_fetched INTEGER NOT NULL DEFAULT 0,
    jobs_found    INTEGER NOT NULL DEFAULT 0,
    jobs_new      INTEGER NOT NULL DEFAULT 0,
    jobs_closed   INTEGER NOT NULL DEFAULT 0,
    errors        INTEGER NOT NULL DEFAULT 0,
    note          TEXT,
    started_at    TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at   TEXT
);

-- 営業対象リスト（未上場のみ・採用の困り度順）
CREATE VIEW IF NOT EXISTS v_sales_targets AS
SELECT
    c.id, c.name, c.corporate_number, c.industry, c.prefecture, c.city,
    c.employee_count, c.capital_yen, c.funding_stage, c.is_foreign_affiliated,
    c.sales_status, c.priority_score,
    COUNT(jp.id)                    AS active_jobs,
    GROUP_CONCAT(DISTINCT cat.name) AS categories,
    MIN(jp.first_seen_at)           AS oldest_posting,
    MAX(jp.first_seen_at)           AS newest_posting,
    c.website, c.careers_url, c.phone
FROM companies c
JOIN job_postings jp ON jp.company_id = c.id AND jp.is_active = 1
LEFT JOIN categories cat ON cat.id = jp.category_id
WHERE c.sales_status IN ('未接触', 'アプローチ中')
  AND c.is_listed = 0
GROUP BY c.id
ORDER BY c.priority_score DESC, active_jobs DESC;

-- 成長スタートアップ営業リスト（直近調達×採用強化を優先）
CREATE VIEW IF NOT EXISTS v_startup_targets AS
SELECT
    c.id, c.name, c.prefecture, c.funding_stage, c.employee_count, c.capital_yen,
    c.last_funding_date, c.last_funding_yen, c.total_funding_yen,
    c.is_foreign_affiliated, c.priority_score, c.sales_status,
    COUNT(jp.id)                    AS active_jobs,
    GROUP_CONCAT(DISTINCT cat.name) AS categories,
    c.website, c.careers_url, c.source_list
FROM companies c
JOIN job_postings jp ON jp.company_id = c.id AND jp.is_active = 1
LEFT JOIN categories cat ON cat.id = jp.category_id
WHERE c.is_listed = 0
  AND c.sales_status IN ('未接触', 'アプローチ中')
GROUP BY c.id
ORDER BY
    (c.last_funding_date IS NOT NULL) DESC,
    c.priority_score DESC,
    active_jobs DESC;

-- 上場子会社・グループ会社の営業リスト（親会社の傘下で採用している企業＝規模＋余力あり）
CREATE VIEW IF NOT EXISTS v_group_targets AS
SELECT
    c.id, c.name, c.corporate_number, c.parent_name, c.ultimate_parent_name, c.is_listed,
    c.industry, c.prefecture, c.employee_count, c.capital_yen,
    c.priority_score, c.sales_status,
    COUNT(jp.id)                    AS active_jobs,
    GROUP_CONCAT(DISTINCT cat.name) AS categories,
    c.website, c.careers_url
FROM companies c
JOIN job_postings jp ON jp.company_id = c.id AND jp.is_active = 1
LEFT JOIN categories cat ON cat.id = jp.category_id
WHERE c.is_subsidiary = 1
  AND c.sales_status IN ('未接触', 'アプローチ中')
GROUP BY c.id
ORDER BY c.priority_score DESC, active_jobs DESC;

-- カテゴリ別サマリー
CREATE VIEW IF NOT EXISTS v_category_summary AS
SELECT
    cat.name                        AS category,
    COUNT(jp.id)                    AS active_jobs,
    COUNT(DISTINCT jp.company_id)   AS companies
FROM categories cat
LEFT JOIN job_postings jp ON jp.category_id = cat.id AND jp.is_active = 1
GROUP BY cat.id
ORDER BY cat.sort_order;

-- 営業ソーシングツール データベーススキーマ (SQLite)
-- 正とするスキーマ定義。変更時は REQUIREMENTS.md §6 も更新すること。

PRAGMA foreign_keys = ON;

-- 職種カテゴリマスタ
CREATE TABLE IF NOT EXISTS categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    keywords    TEXT NOT NULL DEFAULT '',  -- 分類用キーワード（カンマ区切り、求人タイトル/職種名と部分一致）
    sort_order  INTEGER NOT NULL DEFAULT 100
);

-- 企業マスタ（営業リストの本体）
CREATE TABLE IF NOT EXISTS companies (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,             -- 表示用企業名
    name_normalized TEXT NOT NULL UNIQUE,      -- 名寄せキー（株式会社表記・全半角を正規化）
    industry        TEXT,
    prefecture      TEXT,
    address         TEXT,
    url             TEXT,
    phone           TEXT,
    employee_count  INTEGER,
    sales_status    TEXT NOT NULL DEFAULT '未接触'
                    CHECK (sales_status IN ('未接触','アプローチ中','商談','成約','見送り','対象外')),
    priority_score  REAL NOT NULL DEFAULT 0,   -- F-11 営業優先度スコア
    memo            TEXT,
    first_seen_at   TEXT NOT NULL DEFAULT (date('now')),
    last_seen_at    TEXT NOT NULL DEFAULT (date('now')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_companies_status ON companies (sales_status);
CREATE INDEX IF NOT EXISTS idx_companies_pref   ON companies (prefecture);

-- 求人案件
CREATE TABLE IF NOT EXISTS job_postings (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id     INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    category_id    INTEGER REFERENCES categories(id),
    source_site    TEXT NOT NULL,              -- 掲載サイト識別子（例: 'hellowork'）
    source_job_id  TEXT NOT NULL,              -- サイト内の求人ID
    title          TEXT NOT NULL,
    employment_type TEXT,                      -- 正社員/契約/派遣/パート等
    salary_min     INTEGER,                    -- 月給換算・円
    salary_max     INTEGER,
    location       TEXT,
    url            TEXT,
    raw_file       TEXT,                       -- data/raw/ 配下の元ファイルパス
    posted_at      TEXT,                       -- サイト上の掲載開始日
    first_seen_at  TEXT NOT NULL DEFAULT (date('now')),
    last_seen_at   TEXT NOT NULL DEFAULT (date('now')),
    is_active      INTEGER NOT NULL DEFAULT 1, -- 1=掲載中 0=掲載終了
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
    active_count  INTEGER NOT NULL DEFAULT 0,  -- 当日時点の有効案件数
    new_count     INTEGER NOT NULL DEFAULT 0,  -- 当日新規検知数
    company_count INTEGER NOT NULL DEFAULT 0,  -- 掲載企業数
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

-- 営業対象リスト: 有効求人があり、未接触または再アプローチ対象の企業
CREATE VIEW IF NOT EXISTS v_sales_targets AS
SELECT
    c.id,
    c.name,
    c.prefecture,
    c.industry,
    c.sales_status,
    c.priority_score,
    COUNT(jp.id)                    AS active_jobs,
    GROUP_CONCAT(DISTINCT cat.name) AS categories,
    MIN(jp.first_seen_at)           AS oldest_posting,
    MAX(jp.first_seen_at)           AS newest_posting,
    c.url,
    c.phone
FROM companies c
JOIN job_postings jp ON jp.company_id = c.id AND jp.is_active = 1
LEFT JOIN categories cat ON cat.id = jp.category_id
WHERE c.sales_status IN ('未接触', 'アプローチ中')
GROUP BY c.id
ORDER BY c.priority_score DESC, active_jobs DESC;

-- カテゴリ別サマリー: 現在有効な案件数と企業数
CREATE VIEW IF NOT EXISTS v_category_summary AS
SELECT
    cat.name                        AS category,
    COUNT(jp.id)                    AS active_jobs,
    COUNT(DISTINCT jp.company_id)   AS companies
FROM categories cat
LEFT JOIN job_postings jp ON jp.category_id = cat.id AND jp.is_active = 1
GROUP BY cat.id
ORDER BY cat.sort_order;

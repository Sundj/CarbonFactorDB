-- ========================================================
-- 国家温室气体排放因子数据库 - DDL Schema
-- 导出时间: 2026-03-23 10:06:58
-- 数据库文件: carbon_factors.db
-- ========================================================

-- Table: crawl_progress
DROP TABLE IF EXISTS crawl_progress;
CREATE TABLE crawl_progress (
    id INTEGER PRIMARY KEY,
    total_categories INTEGER DEFAULT 0,
    crawled_categories INTEGER DEFAULT 0,
    total_factors INTEGER DEFAULT 0,
    current_category TEXT,
    status TEXT DEFAULT 'running',
    errors TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: emission_factor
DROP TABLE IF EXISTS emission_factor;
CREATE TABLE emission_factor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pkid TEXT NOT NULL,
    category_pkid TEXT NOT NULL,
    category_type TEXT,  -- 'source' 或 'industry'
    fuel_type TEXT,
    fuel_type_en TEXT,
    net_calorific_value TEXT,
    net_calorific_cv TEXT,
    emission_factor TEXT,
    emission_factor_cv TEXT,
    unit TEXT,
    unit_desc TEXT,
    factor_pkid TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pkid, category_pkid, fuel_type)
);

-- Table: emission_source_category
DROP TABLE IF EXISTS emission_source_category;
CREATE TABLE emission_source_category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pkid TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    code TEXT,
    parent_id TEXT,
    sort_num INTEGER DEFAULT 0,
    factor_library_id TEXT,
    year_id TEXT,
    full_name TEXT,
    name_en TEXT,
    type TEXT,  -- '1'表示排放源, '2'表示行业企业
    status TEXT,
    type_permission TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: industry_emission_source_rel
DROP TABLE IF EXISTS industry_emission_source_rel;
CREATE TABLE industry_emission_source_rel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    industry_pkid TEXT NOT NULL,
    category_pkid TEXT NOT NULL,
    UNIQUE(industry_pkid, category_pkid)
);

-- Table: industry_enterprise
DROP TABLE IF EXISTS industry_enterprise;
CREATE TABLE industry_enterprise (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pkid TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    code TEXT,
    parent_id TEXT,
    sort_num INTEGER DEFAULT 0,
    factor_library_id TEXT,
    year_id TEXT,
    full_name TEXT,
    name_en TEXT,
    type TEXT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================================-- 碳排放因子库 - 国家温室气体排放因子数据库（第二版）-- ========================================================

CREATE DATABASE IF NOT EXISTS carbon_factor_db     DEFAULT CHARACTER SET utf8mb4     DEFAULT COLLATE utf8mb4_unicode_ci;

USE carbon_factor_db;

-- ========================================================-- 1. 因子分类体系-- ========================================================

-- 一级分类表（领域）CREATE TABLE factor_category_level1 (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    category_code VARCHAR(20) NOT NULL COMMENT '分类编码',
    category_name VARCHAR(100) NOT NULL COMMENT '分类名称',
    description VARCHAR(500) COMMENT '分类描述',    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序号',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态(0禁用,1启用)',    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,    deleted TINYINT NOT NULL DEFAULT 0 COMMENT '删除标记',
    PRIMARY KEY (id),    UNIQUE KEY uk_category_code (category_code),
    KEY idx_status (status),
    KEY idx_deleted (deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='因子一级分类（领域）';

-- 二级分类表（类别）
CREATE TABLE factor_category_level2 (    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    parent_id BIGINT NOT NULL COMMENT '父分类ID（一级分类）',
    category_code VARCHAR(20) NOT NULL COMMENT '分类编码',    category_name VARCHAR(100) NOT NULL COMMENT '分类名称',
    description VARCHAR(500) COMMENT '分类描述',
    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序号',    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态(0禁用,1启用)',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,    deleted TINYINT NOT NULL DEFAULT 0 COMMENT '删除标记',
    PRIMARY KEY (id),
    KEY idx_parent_id (parent_id),    KEY idx_category_code (category_code),
    KEY idx_status (status),
    KEY idx_deleted (deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='因子二级分类（类别）';

-- 三级分类表（子类别）
CREATE TABLE factor_category_level3 (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    parent_id BIGINT NOT NULL COMMENT '父分类ID（二级分类）',    category_code VARCHAR(20) NOT NULL COMMENT '分类编码',
    category_name VARCHAR(100) NOT NULL COMMENT '分类名称',
    description VARCHAR(500) COMMENT '分类描述',    sort_order INT NOT NULL DEFAULT 0 COMMENT '排序号',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态(0禁用,1启用)',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT NOT NULL DEFAULT 0 COMMENT '删除标记',    PRIMARY KEY (id),
    KEY idx_parent_id (parent_id),
    KEY idx_category_code (category_code),
    KEY idx_status (status),    KEY idx_deleted (deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='因子三级分类（子类别）';

-- ========================================================-- 2. 排放因子主表-- ========================================================

CREATE TABLE emission_factor (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    factor_code VARCHAR(50) NOT NULL COMMENT '因子编码（唯一标识）',    factor_name VARCHAR(200) NOT NULL COMMENT '因子名称',
    factor_alias VARCHAR(200) COMMENT '因子别名/常用名',
    
    -- 分类关联
    category1_id BIGINT NOT NULL COMMENT '一级分类ID（领域）',    category2_id BIGINT COMMENT '二级分类ID（类别）',
    category3_id BIGINT COMMENT '三级分类ID（子类别）',
    
    -- IPCC分类
    ipcc_sector_code VARCHAR(20) COMMENT 'IPCC部门编码',
    ipcc_sector_name VARCHAR(100) COMMENT 'IPCC部门名称',    ipcc_category_code VARCHAR(20) COMMENT 'IPCC类别编码',
    ipcc_category_name VARCHAR(100) COMMENT 'IPCC类别名称',
    
    -- 排放范围
    scope_type VARCHAR(20) NOT NULL COMMENT '排放范围(SCOPE1/SCOPE2/SCOPE3)',
    scope_subcategory VARCHAR(50) COMMENT '排放子类别',    
    -- 因子数值
    factor_value DECIMAL(20,10) NOT NULL COMMENT '排放因子值',
    factor_unit VARCHAR(50) NOT NULL COMMENT '因子单位(如kgCO2e/t)',    factor_unit_cn VARCHAR(50) COMMENT '因子单位中文',
    
    -- 气体成分
    co2_factor DECIMAL(20,10) COMMENT 'CO2排放因子分量',
    ch4_factor DECIMAL(20,10) COMMENT 'CH4排放因子分量',
    n2o_factor DECIMAL(20,10) COMMENT 'N2O排放因子分量',    other_ghg_factor DECIMAL(20,10) COMMENT '其他温室气体分量',
    gwp_version VARCHAR(20) COMMENT 'GWP版本(如AR4/AR5/AR6)',
    
    -- 适用条件
    applicable_region VARCHAR(100) COMMENT '适用地区（全国/省份）',
    applicable_province VARCHAR(50) COMMENT '适用省份',
    applicable_city VARCHAR(50) COMMENT '适用城市',    applicable_industry VARCHAR(100) COMMENT '适用行业',
    applicable_scenario VARCHAR(200) COMMENT '适用场景描述',
    
    -- 数据来源
    data_source VARCHAR(200) COMMENT '数据来源（文献/标准/实测）',
    source_document VARCHAR(500) COMMENT '来源文献/标准名称',
    source_version VARCHAR(50) COMMENT '来源版本',
    source_year INT COMMENT '数据年份',
    
    -- 数据质量
    data_quality VARCHAR(20) COMMENT '数据质量等级(高/中/低)',
    confidence_level VARCHAR(20) COMMENT '置信度',
    uncertainty_range VARCHAR(100) COMMENT '不确定性范围',
    
    -- 计算说明
    calculation_method TEXT COMMENT '计算方法说明',
    calculation_boundary TEXT COMMENT '计算边界说明',
    technical_route TEXT COMMENT '技术路线',
    
    -- 元数据
    factor_version INT NOT NULL DEFAULT 1 COMMENT '因子版本号',
    is_latest_version TINYINT NOT NULL DEFAULT 1 COMMENT '是否最新版本(0否,1是)',
    is_official TINYINT NOT NULL DEFAULT 1 COMMENT '是否官方因子(0否,1是)',    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态(0禁用,1启用)',
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by BIGINT COMMENT '创建人ID',    updated_by BIGINT COMMENT '更新人ID',
    deleted TINYINT NOT NULL DEFAULT 0 COMMENT '删除标记',
    
    PRIMARY KEY (id),    UNIQUE KEY uk_factor_code (factor_code),
    KEY idx_category1_id (category1_id),
    KEY idx_category2_id (category2_id),    KEY idx_category3_id (category3_id),
    KEY idx_scope_type (scope_type),
    KEY idx_factor_value (factor_value),    KEY idx_applicable_region (applicable_region),
    KEY idx_data_source (data_source),
    KEY idx_source_year (source_year),    KEY idx_is_latest_version (is_latest_version),
    KEY idx_status (status),
    KEY idx_deleted (deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='排放因子主表';

-- ========================================================-- 3. 因子历史版本表-- ========================================================

CREATE TABLE emission_factor_history (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    factor_id BIGINT NOT NULL COMMENT '因子主表ID',
    factor_code VARCHAR(50) NOT NULL COMMENT '因子编码',
    factor_version INT NOT NULL COMMENT '版本号',    
    factor_value DECIMAL(20,10) NOT NULL COMMENT '排放因子值',
    factor_unit VARCHAR(50) NOT NULL COMMENT '因子单位',
    data_source VARCHAR(200) COMMENT '数据来源',
    source_year INT COMMENT '数据年份',    
    change_reason TEXT COMMENT '变更原因',
    change_type VARCHAR(20) COMMENT '变更类型(新增/修改/作废)',
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,    created_by BIGINT COMMENT '创建人ID',
    
    PRIMARY KEY (id),
    KEY idx_factor_id (factor_id),    KEY idx_factor_code (factor_code),
    KEY idx_version (factor_version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='排放因子历史版本';

-- ========================================================-- 4. 活动数据类型与因子关联表-- ========================================================

CREATE TABLE activity_type_factor (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    activity_type_code VARCHAR(50) NOT NULL COMMENT '活动数据类型编码',
    activity_type_name VARCHAR(100) NOT NULL COMMENT '活动数据类型名称',
    activity_unit VARCHAR(50) NOT NULL COMMENT '活动数据单位',    
    factor_id BIGINT NOT NULL COMMENT '关联因子ID',
    is_default TINYINT NOT NULL DEFAULT 0 COMMENT '是否默认因子(0否,1是)',
    priority INT NOT NULL DEFAULT 0 COMMENT '优先级',
    
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    PRIMARY KEY (id),
    UNIQUE KEY uk_activity_factor (activity_type_code, factor_id),
    KEY idx_factor_id (factor_id),    KEY idx_activity_type (activity_type_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='活动数据类型与因子关联';

-- ========================================================-- 5. 初始化分类数据-- ========================================================

-- 一级分类（领域）
INSERT INTO factor_category_level1 (category_code, category_name, description, sort_order) VALUES
('ENERGY', '能源活动', '化石燃料燃烧、能源生产与供应等能源相关活动', 1),
('INDUSTRIAL', '工业生产过程', '工业生产过程中的非能源排放', 2),
('AGRICULTURE', '农业', '农业活动产生的温室气体排放', 3),
('LULUCF', '土地利用变化与林业', '土地利用、土地利用变化和林业活动', 4),
('WASTE', '废弃物处理', '废弃物处理产生的温室气体排放', 5),
('TRANSPORT', '交通运输', '交通运输活动产生的温室气体排放', 6),
('BUILDING', '建筑', '建筑运行产生的温室气体排放', 7);

-- 能源活动二级分类
INSERT INTO factor_category_level2 (parent_id, category_code, category_name, description, sort_order) 
SELECT id, 'STATIONARY', '固定源燃烧', '固定燃烧设备的化石燃料燃烧', 1 FROM factor_category_level1 WHERE category_code = 'ENERGY';
INSERT INTO factor_category_level2 (parent_id, category_code, category_name, description, sort_order) 
SELECT id, 'MOBILE', '移动源燃烧', '移动源的化石燃料燃烧', 2 FROM factor_category_level1 WHERE category_code = 'ENERGY';INSERT INTO factor_category_level2 (parent_id, category_code, category_name, description, sort_order) 
SELECT id, 'ENERGY_INDUSTRY', '能源工业', '能源生产和供应活动', 3 FROM factor_category_level1 WHERE category_code = 'ENERGY';
INSERT INTO factor_category_level2 (parent_id, category_code, category_name, description, sort_order) SELECT id, 'FUGITIVE', ' fugitive排放', '煤炭和油气系统的逸散排放', 4 FROM factor_category_level1 WHERE category_code = 'ENERGY';
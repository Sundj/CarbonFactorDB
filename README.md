# 碳排放因子库项目

国家温室气体排放因子数据库（第二版）本地实现

---

## 项目结构

```
carbon-factor-db/
├── backend/                    # Java Spring Boot 后端
│   ├── src/main/java/
│   │   └── com/carbon/factor/
│   │       ├── entity/         # 实体类
│   │       ├── repository/     # 数据访问层
│   │       ├── service/        # 业务逻辑层
│   │       └── controller/     # 控制器层
│   ├── src/main/resources/
│   │   └── db/migration/       # Flyway 迁移脚本
│   └── pom.xml
├── database/                   # 数据库脚本
│   └── V1__init_factor_database.sql
├── scripts/                    # 数据抓取脚本
│   └── crawl_factors.py        # Python 数据抓取工具
├── data/                       # 数据文件
└── docs/                       # 文档
```

---

## 数据库设计

### 核心表

| 表名 | 说明 |
|------|------|
| `factor_category_level1` | 一级分类（领域） |
| `factor_category_level2` | 二级分类（类别） |
| `factor_category_level3` | 三级分类（子类别） |
| `emission_factor` | 排放因子主表 |
| `emission_factor_history` | 因子历史版本 |
| `activity_type_factor` | 活动类型与因子关联 |

### 排放因子字段

- **基础信息**: factor_code, factor_name, factor_alias
- **分类**: category1_id, category2_id, category3_id
- **IPCC分类**: ipcc_sector_code, ipcc_category_code
- **排放范围**: scope_type (SCOPE1/SCOPE2/SCOPE3)
- **因子数值**: factor_value, factor_unit
- **气体成分**: co2_factor, ch4_factor, n2o_factor
- **适用条件**: applicable_region, applicable_industry
- **数据来源**: data_source, source_document, source_year
- **数据质量**: data_quality, confidence_level

---

## 快速开始

### 1. 数据库初始化

```bash
# 创建数据库
mysql -u root -p < database/V1__init_factor_database.sql
```

### 2. 运行后端服务

```bash
cd backend
mvn spring-boot:run
```

### 3. 抓取/导入因子数据

```bash
cd scripts

# 安装依赖
pip install mysql-connector-python

# 运行抓取脚本
python crawl_factors.py
```

---

## API 接口

### 排放因子查询

```
GET /api/factors                    # 查询因子列表（支持分页和筛选）
GET /api/factors/{factorCode}       # 根据编码查询因子
GET /api/factors/latest             # 获取最新版本因子
GET /api/factors/by-category/{id}   # 按分类查询
GET /api/factors/by-scope/{type}    # 按排放范围查询
GET /api/factors/statistics         # 获取统计数据

POST /api/factors                   # 创建因子
PUT /api/factors/{id}               # 更新因子
DELETE /api/factors/{id}            # 删除因子
```

### 查询参数

```
GET /api/factors?keyword=煤炭&category1Id=1&scopeType=SCOPE1&region=全国&page=0&size=10
```

---

## 数据来源

1. **国家温室气体排放因子数据库（第二版）** - 主要数据源
2. **IPCC 排放因子数据库** - 国际参考
3. **各省份温室气体清单指南** - 区域数据
4. **行业排放标准** - 行业特定因子

---

## 预置数据

脚本已预置常用排放因子：

| 因子编码 | 名称 | 范围 | 数值 | 单位 |
|---------|------|------|------|------|
| EF-001 | 原煤 | SCOPE1 | 1.9003 | tCO2e/t |
| EF-002 | 洗精煤 | SCOPE1 | 2.5000 | tCO2e/t |
| EF-003 | 焦炭 | SCOPE1 | 2.8600 | tCO2e/t |
| EF-004 | 原油 | SCOPE1 | 3.0200 | tCO2e/t |
| EF-005 | 汽油 | SCOPE1 | 2.9250 | tCO2e/t |
| EF-006 | 柴油 | SCOPE1 | 3.0959 | tCO2e/t |
| EF-007 | 天然气 | SCOPE1 | 2.1620 | tCO2e/万Nm3 |
| EF-009 | 电网平均排放因子 | SCOPE2 | 0.5703 | tCO2e/MWh |

---

## 技术栈

- **后端**: Java 17, Spring Boot 3.2, Spring Data JPA
- **数据库**: MySQL 8.0, Flyway
- **脚本**: Python 3, requests, mysql-connector

---

## License

MIT

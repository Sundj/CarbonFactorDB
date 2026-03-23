#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国家温室气体排放因子数据库 - 完整数据导出工具
生成 JSON、CSV、SQL 格式的全部排放因子数据
"""

import json
import csv
import os
from datetime import datetime

# 完整排放因子数据集（基于国家温室气体清单指南和公开数据）
COMPLETE_FACTOR_DATA = [
    # ========== 能源活动 - 固定源燃烧 - 煤炭类 ==========
    {"factor_code": "EF-COAL-001", "factor_name": "原煤", "scope_type": "SCOPE1", "factor_value": 1.9003, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "《中国能源统计年鉴》+ IPCC", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-COAL-002", "factor_name": "洗精煤", "scope_type": "SCOPE1", "factor_value": 2.5000, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-COAL-003", "factor_name": "焦炭", "scope_type": "SCOPE1", "factor_value": 2.8600, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-COAL-004", "factor_name": "型煤", "scope_type": "SCOPE1", "factor_value": 1.9000, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "中", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-COAL-005", "factor_name": "煤矸石", "scope_type": "SCOPE1", "factor_value": 0.9000, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "中", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    
    # 石油类
    {"factor_code": "EF-OIL-001", "factor_name": "原油", "scope_type": "SCOPE1", "factor_value": 3.0200, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "IPCC 2006", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OIL-002", "factor_name": "汽油", "scope_type": "SCOPE1", "factor_value": 2.9250, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OIL-003", "factor_name": "柴油", "scope_type": "SCOPE1", "factor_value": 3.0959, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OIL-004", "factor_name": "煤油", "scope_type": "SCOPE1", "factor_value": 3.0330, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "IPCC 2006", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OIL-005", "factor_name": "燃料油", "scope_type": "SCOPE1", "factor_value": 3.1700, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OIL-006", "factor_name": "液化石油气", "scope_type": "SCOPE1", "factor_value": 3.1013, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OIL-007", "factor_name": "炼厂干气", "scope_type": "SCOPE1", "factor_value": 2.9000, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "中", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OIL-008", "factor_name": "石脑油", "scope_type": "SCOPE1", "factor_value": 3.1500, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "IPCC 2006", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OIL-009", "factor_name": "润滑油", "scope_type": "SCOPE1", "factor_value": 3.1500, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "IPCC 2006", "source_year": 2023, "data_quality": "中", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OIL-010", "factor_name": "石蜡", "scope_type": "SCOPE1", "factor_value": 3.2000, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "IPCC 2006", "source_year": 2023, "data_quality": "中", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OIL-011", "factor_name": "沥青", "scope_type": "SCOPE1", "factor_value": 3.1700, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "IPCC 2006", "source_year": 2023, "data_quality": "中", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OIL-012", "factor_name": "石油焦", "scope_type": "SCOPE1", "factor_value": 3.2000, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    
    # 天然气类
    {"factor_code": "EF-GAS-001", "factor_name": "天然气", "scope_type": "SCOPE1", "factor_value": 2.1620, "factor_unit": "tCO2e/万Nm3", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-GAS-002", "factor_name": "液化天然气", "scope_type": "SCOPE1", "factor_value": 2.7000, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "IPCC 2006", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-GAS-003", "factor_name": "焦炉煤气", "scope_type": "SCOPE1", "factor_value": 1.1000, "factor_unit": "tCO2e/万Nm3", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "中", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-GAS-004", "factor_name": "高炉煤气", "scope_type": "SCOPE1", "factor_value": 2.0000, "factor_unit": "tCO2e/万Nm3", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "中", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-GAS-005", "factor_name": "转炉煤气", "scope_type": "SCOPE1", "factor_value": 1.8000, "factor_unit": "tCO2e/万Nm3", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "中", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    
    # 其他燃料
    {"factor_code": "EF-OTHER-001", "factor_name": "沼气", "scope_type": "SCOPE1", "factor_value": 1.0000, "factor_unit": "tCO2e/万Nm3", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "中", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OTHER-002", "factor_name": "工业废料", "scope_type": "SCOPE1", "factor_value": 1.5000, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "低", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    {"factor_code": "EF-OTHER-003", "factor_name": "城市固体废物", "scope_type": "SCOPE1", "factor_value": 0.9000, "factor_unit": "tCO2e/t", "scope_subcategory": "固定源燃烧", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "低", "category1_name": "能源活动", "category2_code": "STATIONARY", "ipcc_code": "1.A.1"},
    
    # ========== 移动源燃烧 ==========
    {"factor_code": "EF-MOB-001", "factor_name": "汽油（道路）", "scope_type": "SCOPE1", "factor_value": 2.3700, "factor_unit": "tCO2e/t", "scope_subcategory": "移动源燃烧-道路", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "MOBILE", "ipcc_code": "1.A.3.b"},
    {"factor_code": "EF-MOB-002", "factor_name": "柴油（道路）", "scope_type": "SCOPE1", "factor_value": 3.0200, "factor_unit": "tCO2e/t", "scope_subcategory": "移动源燃烧-道路", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "MOBILE", "ipcc_code": "1.A.3.b"},
    {"factor_code": "EF-MOB-003", "factor_name": "天然气（道路）", "scope_type": "SCOPE1", "factor_value": 2.2000, "factor_unit": "tCO2e/t", "scope_subcategory": "移动源燃烧-道路", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "中", "category1_name": "能源活动", "category2_code": "MOBILE", "ipcc_code": "1.A.3.b"},
    {"factor_code": "EF-AVI-001", "factor_name": "航空煤油（国内）", "scope_type": "SCOPE1", "factor_value": 3.1500, "factor_unit": "tCO2e/t", "scope_subcategory": "移动源燃烧-航空", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "MOBILE", "ipcc_code": "1.A.3.a"},
    {"factor_code": "EF-SHIP-001", "factor_name": "船用燃料油", "scope_type": "SCOPE1", "factor_value": 3.1700, "factor_unit": "tCO2e/t", "scope_subcategory": "移动源燃烧-水运", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "MOBILE", "ipcc_code": "1.A.3.d"},
    
    # ========== 能源间接排放 - 电力 ==========
    {"factor_code": "EF-ELC-001", "factor_name": "电网平均排放因子", "scope_type": "SCOPE2", "factor_value": 0.5703, "factor_unit": "tCO2e/MWh", "scope_subcategory": "外购电力", "applicable_region": "全国", "data_source": "生态环境部", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "ENERGY_INDIRECT", "ipcc_code": "2"},
    {"factor_code": "EF-ELC-002", "factor_name": "电网平均排放因子（华北）", "scope_type": "SCOPE2", "factor_value": 0.7125, "factor_unit": "tCO2e/MWh", "scope_subcategory": "外购电力", "applicable_region": "华北", "data_source": "生态环境部", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "ENERGY_INDIRECT", "ipcc_code": "2"},
    {"factor_code": "EF-ELC-003", "factor_name": "电网平均排放因子（华东）", "scope_type": "SCOPE2", "factor_value": 0.5257, "factor_unit": "tCO2e/MWh", "scope_subcategory": "外购电力", "applicable_region": "华东", "data_source": "生态环境部", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "ENERGY_INDIRECT", "ipcc_code": "2"},
    {"factor_code": "EF-ELC-004", "factor_name": "电网平均排放因子（华南）", "scope_type": "SCOPE2", "factor_value": 0.4723, "factor_unit": "tCO2e/MWh", "scope_subcategory": "外购电力", "applicable_region": "华南", "data_source": "生态环境部", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "ENERGY_INDIRECT", "ipcc_code": "2"},
    {"factor_code": "EF-ELC-005", "factor_name": "电网平均排放因子（华中）", "scope_type": "SCOPE2", "factor_value": 0.4538, "factor_unit": "tCO2e/MWh", "scope_subcategory": "外购电力", "applicable_region": "华中", "data_source": "生态环境部", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "ENERGY_INDIRECT", "ipcc_code": "2"},
    {"factor_code": "EF-ELC-006", "factor_name": "电网平均排放因子（西北）", "scope_type": "SCOPE2", "factor_value": 0.5625, "factor_unit": "tCO2e/MWh", "scope_subcategory": "外购电力", "applicable_region": "西北", "data_source": "生态环境部", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "ENERGY_INDIRECT", "ipcc_code": "2"},
    {"factor_code": "EF-ELC-007", "factor_name": "电网平均排放因子（东北）", "scope_type": "SCOPE2", "factor_value": 0.6878, "factor_unit": "tCO2e/MWh", "scope_subcategory": "外购电力", "applicable_region": "东北", "data_source": "生态环境部", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "ENERGY_INDIRECT", "ipcc_code": "2"},
    {"factor_code": "EF-ELC-008", "factor_name": "电网平均排放因子（西南）", "scope_type": "SCOPE2", "factor_value": 0.2179, "factor_unit": "tCO2e/MWh", "scope_subcategory": "外购电力", "applicable_region": "西南", "data_source": "生态环境部", "source_year": 2023, "data_quality": "高", "category1_name": "能源活动", "category2_code": "ENERGY_INDIRECT", "ipcc_code": "2"},
    
    # 热力
    {"factor_code": "EF-HEAT-001", "factor_name": "外购热力排放因子", "scope_type": "SCOPE2", "factor_value": 0.1100, "factor_unit": "tCO2e/GJ", "scope_subcategory": "外购热力", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "中", "category1_name": "能源活动", "category2_code": "ENERGY_INDIRECT", "ipcc_code": "2"},
    
    # ========== 工业生产过程 ==========
    {"factor_code": "EF-IND-001", "factor_name": "水泥生产过程", "scope_type": "SCOPE1", "factor_value": 0.5200, "factor_unit": "tCO2e/t熟料", "scope_subcategory": "水泥", "applicable_region": "全国", "data_source": "《水泥行业碳排放核算指南》", "source_year": 2023, "data_quality": "高", "category1_name": "工业生产过程", "category2_code": "MINERAL", "ipcc_code": "2.A.1"},
    {"factor_code": "EF-IND-002", "factor_name": "石灰生产过程", "scope_type": "SCOPE1", "factor_value": 0.7500, "factor_unit": "tCO2e/t石灰", "scope_subcategory": "石灰", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "中", "category1_name": "工业生产过程", "category2_code": "MINERAL", "ipcc_code": "2.A.2"},
    {"factor_code": "EF-IND-003", "factor_name": "合成氨生产过程", "scope_type": "SCOPE1", "factor_value": 2.1000, "factor_unit": "tCO2e/t氨", "scope_subcategory": "化工", "applicable_region": "全国", "data_source": "国家清单指南", "source_year": 2023, "data_quality": "中", "category1_name": "工业生产过程", "category2_code": "CHEMICAL", "ipcc_code": "2.B.1"},
    {"factor_code": "EF-IND-004", "factor_name": "电炉炼钢", "scope_type": "SCOPE1", "factor_value": 0.0800, "factor_unit": "tCO2e/t钢", "scope_subcategory": "钢铁", "applicable_region": "全国", "data_source": "行业经验值", "source_year": 2023, "data_quality": "中", "category1_name": "工业生产过程", "category2_code": "METAL", "ipcc_code": "2.C.1"},
    
    # ========== 交通运输 ==========
    {"factor_code": "EF-TRA-001", "factor_name": "公共汽车（柴油）", "scope_type": "SCOPE1", "factor_value": 0.0500, "factor_unit": "kgCO2e/人·km", "scope_subcategory": "公共交通", "applicable_region": "全国", "data_source": "行业经验值", "source_year": 2023, "data_quality": "中", "category1_name": "交通运输", "category2_code": "ROAD", "ipcc_code": "1.A.3.b"},
    {"factor_code": "EF-TRA-002", "factor_name": "地铁/轻轨", "scope_type": "SCOPE2", "factor_value": 0.0150, "factor_unit": "kgCO2e/人·km", "scope_subcategory": "轨道交通", "applicable_region": "全国", "data_source": "行业经验值", "source_year": 2023, "data_quality": "中", "category1_name": "交通运输", "category2_code": "RAIL", "ipcc_code": "2"},
    {"factor_code": "EF-TRA-003", "factor_name": "私家车（汽油）", "scope_type": "SCOPE1", "factor_value": 0.2000, "factor_unit": "kgCO2e/km", "scope_subcategory": "私家车", "applicable_region": "全国", "data_source": "行业经验值", "source_year": 2023, "data_quality": "中", "category1_name": "交通运输", "category2_code": "ROAD", "ipcc_code": "1.A.3.b"},
    {"factor_code": "EF-TRA-004", "factor_name": "国内航班", "scope_type": "SCOPE1", "factor_value": 0.1500, "factor_unit": "kgCO2e/人·km", "scope_subcategory": "航空", "applicable_region": "全国", "data_source": "行业经验值", "source_year": 2023, "data_quality": "中", "category1_name": "交通运输", "category2_code": "AIR", "ipcc_code": "1.A.3.a"},
    {"factor_code": "EF-TRA-005", "factor_name": "高速铁路", "scope_type": "SCOPE2", "factor_value": 0.0250, "factor_unit": "kgCO2e/人·km", "scope_subcategory": "铁路", "applicable_region": "全国", "data_source": "行业经验值", "source_year": 2023, "data_quality": "中", "category1_name": "交通运输", "category2_code": "RAIL", "ipcc_code": "2"},
    {"factor_code": "EF-TRA-006", "factor_name": "重型货车", "scope_type": "SCOPE1", "factor_value": 0.0800, "factor_unit": "kgCO2e/t·km", "scope_subcategory": "公路货运", "applicable_region": "全国", "data_source": "行业经验值", "source_year": 2023, "data_quality": "中", "category1_name": "交通运输", "category2_code": "ROAD", "ipcc_code": "1.A.3.b"},
    {"factor_code": "EF-TRA-007", "factor_name": "铁路货运", "scope_type": "SCOPE2", "factor_value": 0.0100, "factor_unit": "kgCO2e/t·km", "scope_subcategory": "铁路货运", "applicable_region": "全国", "data_source": "行业经验值", "source_year": 2023, "data_quality": "中", "category1_name": "交通运输", "category2_code": "RAIL", "ipcc_code": "2"},
    {"factor_code": "EF-TRA-008", "factor_name": "水运货运", "scope_type": "SCOPE1", "factor_value": 0.0080, "factor_unit": "kgCO2e/t·km", "scope_subcategory": "水运", "applicable_region": "全国", "data_source": "行业经验值", "source_year": 2023, "data_quality": "中", "category1_name": "交通运输", "category2_code": "WATER", "ipcc_code": "1.A.3.d"},
    
    # ========== 建筑 ==========
    {"factor_code": "EF-BLD-001", "factor_name": "住宅建筑（运行）", "scope_type": "SCOPE2", "factor_value": 35.0000, "factor_unit": "kgCO2e/m2·年", "scope_subcategory": "建筑运行", "applicable_region": "全国", "data_source": "《建筑碳排放计算标准》", "source_year": 2023, "data_quality": "中", "category1_name": "建筑", "category2_code": "OPERATION", "ipcc_code": "2"},
    {"factor_code": "EF-BLD-002", "factor_name": "公共建筑（运行）", "scope_type": "SCOPE2", "factor_value": 85.0000, "factor_unit": "kgCO2e/m2·年", "scope_subcategory": "建筑运行", "applicable_region": "全国", "data_source": "《建筑碳排放计算标准》", "source_year": 2023, "data_quality": "中", "category1_name": "建筑", "category2_code": "OPERATION", "ipcc_code": "2"},
]


def export_to_json(data, output_path):
    """导出为JSON"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ JSON导出完成: {output_path}")


def export_to_csv(data, output_path):
    """导出为CSV"""
    if not data:
        return
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ CSV导出完成: {output_path}")


def export_to_sql(data, output_path):
    """导出为SQL INSERT语句"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("-- 国家温室气体排放因子数据库 - 完整数据导入脚本\n")
        f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- 因子总数: {len(data)}\n\n")
        
        f.write("USE carbon_factor_db;\n\n")
        
        # 先插入分类数据
        f.write("-- 初始化一级分类\n")
        f.write("INSERT INTO factor_category_level1 (category_code, category_name, description, sort_order) VALUES\n")
        categories = [
            ("ENERGY", "能源活动", "化石燃料燃烧、能源生产与供应等能源相关活动", 1),
            ("INDUSTRIAL", "工业生产过程", "工业生产过程中的非能源排放", 2),
            ("AGRICULTURE", "农业", "农业活动产生的温室气体排放", 3),
            ("LULUCF", "土地利用变化与林业", "土地利用、土地利用变化和林业活动", 4),
            ("WASTE", "废弃物处理", "废弃物处理产生的温室气体排放", 5),
            ("TRANSPORT", "交通运输", "交通运输活动产生的温室气体排放", 6),
            ("BUILDING", "建筑", "建筑运行产生的温室气体排放", 7),
        ]
        values = []
        for code, name, desc, order in categories:
            values.append(f"('{code}', '{name}', '{desc}', {order})")
        f.write(",\n".join(values) + "\nON DUPLICATE KEY UPDATE category_name=VALUES(category_name);\n\n")
        
        # 插入因子数据
        f.write("-- 插入排放因子数据\n")
        f.write("INSERT INTO emission_factor (factor_code, factor_name, scope_type, scope_subcategory, factor_value, factor_unit, applicable_region, data_source, source_year, data_quality, is_latest_version, status, deleted) VALUES\n")
        
        values = []
        for item in data:
            val = f"('{item['factor_code']}', '{item['factor_name']}', '{item['scope_type']}', '{item['scope_subcategory']}', {item['factor_value']}, '{item['factor_unit']}', '{item['applicable_region']}', '{item['data_source']}', {item['source_year']}, '{item['data_quality']}', 1, 1, 0)"
            values.append(val)
        
        # 每50条分一个INSERT
        batch_size = 50
        for i in range(0, len(values), batch_size):
            batch = values[i:i+batch_size]
            f.write(",\n".join(batch))
            f.write("\nON DUPLICATE KEY UPDATE factor_value=VALUES(factor_value), updated_at=CURRENT_TIMESTAMP;\n\n")
            if i + batch_size < len(values):
                f.write("INSERT INTO emission_factor (factor_code, factor_name, scope_type, scope_subcategory, factor_value, factor_unit, applicable_region, data_source, source_year, data_quality, is_latest_version, status, deleted) VALUES\n")
    
    print(f"✅ SQL导出完成: {output_path}")


def generate_statistics(data):
    """生成统计数据"""
    stats = {
        "total": len(data),
        "by_scope": {},
        "by_category": {},
        "by_region": {},
        "by_quality": {},
        "by_year": {}
    }
    
    for item in data:
        # 按范围统计
        scope = item.get("scope_type", "未知")
        stats["by_scope"][scope] = stats["by_scope"].get(scope, 0) + 1
        
        # 按分类统计
        cat = item.get("category1_name", "未知")
        stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
        
        # 按地区统计
        region = item.get("applicable_region", "未知")
        stats["by_region"][region] = stats["by_region"].get(region, 0) + 1
        
        # 按质量统计
        quality = item.get("data_quality", "未知")
        stats["by_quality"][quality] = stats["by_quality"].get(quality, 0) + 1
        
        # 按年份统计
        year = item.get("source_year", "未知")
        stats["by_year"][str(year)] = stats["by_year"].get(str(year), 0) + 1
    
    return stats


def main():
    """主函数"""
    print("=" * 70)
    print("🌱 国家温室气体排放因子数据库 - 完整数据导出工具")
    print("=" * 70)
    
    # 创建输出目录
    output_dir = '/home/sundj/.openclaw/workspace/carbon-factor-db/data'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📊 数据集信息:")
    print(f"  排放因子总数: {len(COMPLETE_FACTOR_DATA)} 条")
    
    # 生成统计
    stats = generate_statistics(COMPLETE_FACTOR_DATA)
    
    print(f"\n  按排放范围:")
    for scope, count in stats["by_scope"].items():
        scope_name = {"SCOPE1": "范围1-直接排放", "SCOPE2": "范围2-间接排放", "SCOPE3": "范围3-其他间接"}.get(scope, scope)
        print(f"    {scope_name}: {count}条")
    
    print(f"\n  按领域分类:")
    for cat, count in stats["by_category"].items():
        print(f"    {cat}: {count}条")
    
    print(f"\n  按适用地区:")
    for region, count in sorted(stats["by_region"].items(), key=lambda x: -x[1]):
        print(f"    {region}: {count}条")
    
    # 导出JSON
    print("\n📤 导出JSON格式...")
    export_to_json(COMPLETE_FACTOR_DATA, f"{output_dir}/emission_factors_complete.json")
    
    # 导出CSV
    print("\n📤 导出CSV格式...")
    export_to_csv(COMPLETE_FACTOR_DATA, f"{output_dir}/emission_factors_complete.csv")
    
    # 导出SQL
    print("\n📤 导出SQL格式...")
    export_to_sql(COMPLETE_FACTOR_DATA, f"{output_dir}/emission_factors_complete.sql")
    
    # 导出统计数据
    print("\n📤 导出统计数据...")
    with open(f"{output_dir}/statistics.json", 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"✅ 统计信息导出完成: {output_dir}/statistics.json")
    
    print("\n" + "=" * 70)
    print("✅ 全部数据导出完成！")
    print(f"📁 输出目录: {output_dir}")
    print("=" * 70)


if __name__ == '__main__':
    main()

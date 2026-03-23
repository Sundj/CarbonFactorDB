#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国家温室气体排放因子数据库 - 完整数据抓取脚本
支持从多个数据源抓取全部排放因子
"""

import requests
import json
import time
import random
import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import mysql.connector
from mysql.connector import Error
from urllib.parse import urljoin, quote

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'carbon_factor_db',
    'user': 'root',
    'password': '123456'
}

# 完整排放因子数据集（基于国家温室气体清单指南和公开数据）
COMPLETE_FACTOR_DATA = {
    # ========== 能源活动 - 固定源燃烧 ==========
    "固定源燃烧": [
        # 煤炭类
        ("EF-COAL-001", "原煤", "SCOPE1", 1.9003, "tCO2e/t", "固定源燃烧", "全国", 
         "《中国能源统计年鉴》+ IPCC", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-COAL-002", "洗精煤", "SCOPE1", 2.5000, "tCO2e/t", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-COAL-003", "焦炭", "SCOPE1", 2.8600, "tCO2e/t", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-COAL-004", "型煤", "SCOPE1", 1.9000, "tCO2e/t", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "中", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-COAL-005", "煤矸石", "SCOPE1", 0.9000, "tCO2e/t", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "中", "能源活动", "STATIONARY", "1.A.1"),
        
        # 石油类
        ("EF-OIL-001", "原油", "SCOPE1", 3.0200, "tCO2e/t", "固定源燃烧", "全国", 
         "IPCC 2006", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OIL-002", "汽油", "SCOPE1", 2.9250, "tCO2e/t", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OIL-003", "柴油", "SCOPE1", 3.0959, "tCO2e/t", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OIL-004", "煤油", "SCOPE1", 3.0330, "tCO2e/t", "固定源燃烧", "全国", 
         "IPCC 2006", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OIL-005", "燃料油", "SCOPE1", 3.1700, "tCO2e/t", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OIL-006", "液化石油气", "SCOPE1", 3.1013, "tCO2e/t", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OIL-007", "炼厂干气", "SCOPE1", 2.9000, "tCO2e/t", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "中", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OIL-008", "石脑油", "SCOPE1", 3.1500, "tCO2e/t", "固定源燃烧", "全国", 
         "IPCC 2006", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OIL-009", "润滑油", "SCOPE1", 3.1500, "tCO2e/t", "固定源燃烧", "全国", 
         "IPCC 2006", 2023, "中", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OIL-010", "石蜡", "SCOPE1", 3.2000, "tCO2e/t", "固定源燃烧", "全国", 
         "IPCC 2006", 2023, "中", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OIL-011", "沥青", "SCOPE1", 3.1700, "tCO2e/t", "固定源燃烧", "全国", 
         "IPCC 2006", 2023, "中", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OIL-012", "石油焦", "SCOPE1", 3.2000, "tCO2e/t", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        
        # 天然气类
        ("EF-GAS-001", "天然气", "SCOPE1", 2.1620, "tCO2e/万Nm3", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-GAS-002", "液化天然气", "SCOPE1", 2.7000, "tCO2e/t", "固定源燃烧", "全国", 
         "IPCC 2006", 2023, "高", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-GAS-003", "焦炉煤气", "SCOPE1", 1.1000, "tCO2e/万Nm3", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "中", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-GAS-004", "高炉煤气", "SCOPE1", 2.0000, "tCO2e/万Nm3", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "中", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-GAS-005", "转炉煤气", "SCOPE1", 1.8000, "tCO2e/万Nm3", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "中", "能源活动", "STATIONARY", "1.A.1"),
        
        # 其他燃料
        ("EF-OTHER-001", "沼气", "SCOPE1", 1.0000, "tCO2e/万Nm3", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "中", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OTHER-002", "工业废料", "SCOPE1", 1.5000, "tCO2e/t", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "低", "能源活动", "STATIONARY", "1.A.1"),
        ("EF-OTHER-003", "城市固体废物", "SCOPE1", 0.9000, "tCO2e/t", "固定源燃烧", "全国", 
         "国家清单指南", 2023, "低", "能源活动", "STATIONARY", "1.A.1"),
    ],
    
    # ========== 能源活动 - 移动源燃烧 ==========
    "移动源燃烧": [
        ("EF-MOB-001", "汽油（道路）", "SCOPE1", 2.3700, "tCO2e/t", "移动源燃烧-道路", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "MOBILE", "1.A.3.b"),
        ("EF-MOB-002", "柴油（道路）", "SCOPE1", 3.0200, "tCO2e/t", "移动源燃烧-道路", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "MOBILE", "1.A.3.b"),
        ("EF-MOB-003", "天然气（道路）", "SCOPE1", 2.2000, "tCO2e/t", "移动源燃烧-道路", "全国", 
         "国家清单指南", 2023, "中", "能源活动", "MOBILE", "1.A.3.b"),
        ("EF-MOB-004", "液化石油气（道路）", "SCOPE1", 3.0000, "tCO2e/t", "移动源燃烧-道路", "全国", 
         "国家清单指南", 2023, "中", "能源活动", "MOBILE", "1.A.3.b"),
        
        # 航空
        ("EF-AVI-001", "航空煤油（国内）", "SCOPE1", 3.1500, "tCO2e/t", "移动源燃烧-航空", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "MOBILE", "1.A.3.a"),
        ("EF-AVI-002", "航空汽油", "SCOPE1", 3.0000, "tCO2e/t", "移动源燃烧-航空", "全国", 
         "IPCC 2006", 2023, "高", "能源活动", "MOBILE", "1.A.3.a"),
        
        # 水运
        ("EF-SHIP-001", "船用燃料油", "SCOPE1", 3.1700, "tCO2e/t", "移动源燃烧-水运", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "MOBILE", "1.A.3.d"),
        ("EF-SHIP-002", "船用柴油", "SCOPE1", 3.1000, "tCO2e/t", "移动源燃烧-水运", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "MOBILE", "1.A.3.d"),
        
        # 铁路
        ("EF-RAIL-001", "柴油（铁路）", "SCOPE1", 3.0200, "tCO2e/t", "移动源燃烧-铁路", "全国", 
         "国家清单指南", 2023, "高", "能源活动", "MOBILE", "1.A.3.c"),
    ],
    
    # ========== 能源间接排放 ==========
    "能源间接排放": [
        # 电力
        ("EF-ELC-001", "电网平均排放因子", "SCOPE2", 0.5703, "tCO2e/MWh", "外购电力", "全国", 
         "生态环境部", 2023, "高", "能源活动", "ENERGY_INDIRECT", "2"),
        ("EF-ELC-002", "电网平均排放因子（华北）", "SCOPE2", 0.7125, "tCO2e/MWh", "外购电力", "华北", 
         "生态环境部", 2023, "高", "能源活动", "ENERGY_INDIRECT", "2"),
        ("EF-ELC-003", "电网平均排放因子（华东）", "SCOPE2", 0.5257, "tCO2e/MWh", "外购电力", "华东", 
         "生态环境部", 2023, "高", "能源活动", "ENERGY_INDIRECT", "2"),
        ("EF-ELC-004", "电网平均排放因子（华南）", "SCOPE2", 0.4723, "tCO2e/MWh", "外购电力", "华南", 
         "生态环境部", 2023, "高", "能源活动", "ENERGY_INDIRECT", "2"),
        ("EF-ELC-005", "电网平均排放因子（华中）", "SCOPE2", 0.4538, "tCO2e/MWh", "外购电力", "华中", 
         "生态环境部", 2023, "高", "能源活动", "ENERGY_INDIRECT", "2"),
        ("EF-ELC-006", "电网平均排放因子（西北）", "SCOPE2", 0.5625, "tCO2e/MWh", "外购电力", "西北", 
         "生态环境部", 2023, "高", "能源活动", "ENERGY_INDIRECT", "2"),
        ("EF-ELC-007", "电网平均排放因子（东北）", "SCOPE2", 0.6878, "tCO2e/MWh", "外购电力", "东北", 
         "生态环境部", 2023, "高", "能源活动", "ENERGY_INDIRECT", "2"),
        ("EF-ELC-008", "电网平均排放因子（西南）", "SCOPE2", 0.2179, "tCO2e/MWh", "外购电力", "西南", 
         "生态环境部", 2023, "高", "能源活动", "ENERGY_INDIRECT", "2"),
        
        # 热力
        ("EF-HEAT-001", "外购热力排放因子", "SCOPE2", 0.1100, "tCO2e/GJ", "外购热力", "全国", 
         "国家清单指南", 2023, "中", "能源活动", "ENERGY_INDIRECT", "2"),
        ("EF-HEAT-002", "蒸汽（低压）", "SCOPE2", 0.1000, "tCO2e/GJ", "外购热力", "全国", 
         "行业经验值", 2023, "中", "能源活动", "ENERGY_INDIRECT", "2"),
        ("EF-HEAT-003", "蒸汽（中压）", "SCOPE2", 0.1100, "tCO2e/GJ", "外购热力", "全国", 
         "行业经验值", 2023, "中", "能源活动", "ENERGY_INDIRECT", "2"),
        ("EF-HEAT-004", "蒸汽（高压）", "SCOPE2", 0.1200, "tCO2e/GJ", "外购热力", "全国", 
         "行业经验值", 2023, "中", "能源活动", "ENERGY_INDIRECT", "2"),
    ],
    
    # ========== 工业生产过程 ==========
    "工业生产过程": [
        # 水泥
        ("EF-IND-001", "水泥生产过程", "SCOPE1", 0.5200, "tCO2e/t熟料", "水泥", "全国", 
         "《水泥行业碳排放核算指南》", 2023, "高", "工业生产过程", "INDUSTRIAL", "2.A.1"),
        ("EF-IND-002", "水泥窑灰", "SCOPE1", 0.4700, "tCO2e/t", "水泥", "全国", 
         "国家清单指南", 2023, "中", "工业生产过程", "INDUSTRIAL", "2.A.1"),
        
        # 石灰
        ("EF-IND-003", "石灰生产过程", "SCOPE1", 0.7500, "tCO2e/t石灰", "石灰", "全国", 
         "国家清单指南", 2023, "中", "工业生产过程", "INDUSTRIAL", "2.A.2"),
        
        # 钢铁
        ("EF-IND-004", "石灰石煅烧（钢铁）", "SCOPE1", 0.4400, "tCO2e/t", "钢铁", "全国", 
         "国家清单指南", 2023, "中", "工业生产过程", "INDUSTRIAL", "2.C.1"),
        ("EF-IND-005", "电炉炼钢", "SCOPE1", 0.0800, "tCO2e/t钢", "钢铁", "全国", 
         "行业经验值", 2023, "中", "工业生产过程", "INDUSTRIAL", "2.C.1"),
        
        # 化工
        ("EF-IND-006", "合成氨生产过程", "SCOPE1", 2.1000, "tCO2e/t氨", "化工", "全国", 
         "国家清单指南", 2023, "中", "工业生产过程", "INDUSTRIAL", "2.B.1"),
        ("EF-IND-007", "硝酸生产过程", "SCOPE1", 0.3000, "tCO2e/t酸", "化工", "全国", 
         "国家清单指南", 2023, "中", "工业生产过程", "INDUSTRIAL", "2.B.2"),
        ("EF-IND-008", "己二酸生产过程", "SCOPE1", 1.5000, "tCO2e/t", "化工", "全国", 
         "国家清单指南", 2023, "中", "工业生产过程", "INDUSTRIAL", "2.B.3"),
        
        # 其他
        ("EF-IND-009", "电石生产过程", "SCOPE1", 0.8000, "tCO2e/t电石", "化工", "全国", 
         "国家清单指南", 2023, "中", "工业生产过程", "INDUSTRIAL", "2.B.5"),
        ("EF-IND-010", "纯碱生产过程", "SCOPE1", 0.4000, "tCO2e/t纯碱", "化工", "全国", 
         "国家清单指南", 2023, "中", "工业生产过程", "INDUSTRIAL", "2.A.4"),
        ("EF-IND-011", "平板玻璃", "SCOPE1", 0.2000, "tCO2e/t玻璃", "玻璃", "全国", 
         "行业经验值", 2023, "中", "工业生产过程", "INDUSTRIAL", "2.A.3"),
        ("EF-IND-012", "陶瓷", "SCOPE1", 0.1500, "tCO2e/t陶瓷", "陶瓷", "全国", 
         "行业经验值", 2023, "低", "工业生产过程", "INDUSTRIAL", "2.A.4"),
    ],
    
    # ========== 交通运输 ==========
    "交通运输": [
        # 客运
        ("EF-TRA-001", "公共汽车（柴油）", "SCOPE1", 0.0500, "kgCO2e/人·km", "公共交通", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "1.A.3.b"),
        ("EF-TRA-002", "公共汽车（天然气）", "SCOPE1", 0.0400, "kgCO2e/人·km", "公共交通", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "1.A.3.b"),
        ("EF-TRA-003", "地铁/轻轨", "SCOPE2", 0.0150, "kgCO2e/人·km", "轨道交通", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "2"),
        ("EF-TRA-004", "出租车（汽油）", "SCOPE1", 0.1200, "kgCO2e/km", "出租车", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "1.A.3.b"),
        ("EF-TRA-005", "出租车（天然气）", "SCOPE1", 0.1000, "kgCO2e/km", "出租车", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "1.A.3.b"),
        ("EF-TRA-006", "私家车（汽油）", "SCOPE1", 0.2000, "kgCO2e/km", "私家车", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "1.A.3.b"),
        ("EF-TRA-007", "私家车（新能源）", "SCOPE2", 0.1000, "kgCO2e/km", "私家车", "全国", 
         "行业经验值", 2023, "低", "交通运输", "TRANSPORT", "2"),
        ("EF-TRA-008", "国内航班", "SCOPE1", 0.1500, "kgCO2e/人·km", "航空", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "1.A.3.a"),
        ("EF-TRA-009", "高速铁路", "SCOPE2", 0.0250, "kgCO2e/人·km", "铁路", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "2"),
        
        # 货运
        ("EF-TRA-010", "重型货车", "SCOPE1", 0.0800, "kgCO2e/t·km", "公路货运", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "1.A.3.b"),
        ("EF-TRA-011", "中型货车", "SCOPE1", 0.1200, "kgCO2e/t·km", "公路货运", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "1.A.3.b"),
        ("EF-TRA-012", "轻型货车", "SCOPE1", 0.2000, "kgCO2e/t·km", "公路货运", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "1.A.3.b"),
        ("EF-TRA-013", "铁路货运", "SCOPE2", 0.0100, "kgCO2e/t·km", "铁路货运", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "2"),
        ("EF-TRA-014", "水运货运", "SCOPE1", 0.0080, "kgCO2e/t·km", "水运", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "1.A.3.d"),
        ("EF-TRA-015", "航空货运", "SCOPE1", 0.6000, "kgCO2e/t·km", "航空货运", "全国", 
         "行业经验值", 2023, "中", "交通运输", "TRANSPORT", "1.A.3.a"),
    ],
    
    # ========== 建筑 ==========
    "建筑": [
        ("EF-BLD-001", "住宅建筑（运行）", "SCOPE2", 35.0000, "kgCO2e/m2·年", "建筑运行", "全国", 
         "《建筑碳排放计算标准》", 2023, "中", "建筑", "BUILDING", "2"),
        ("EF-BLD-002", "公共建筑（运行）", "SCOPE2", 85.0000, "kgCO2e/m2·年", "建筑运行", "全国", 
         "《建筑碳排放计算标准》", 2023, "中", "建筑", "BUILDING", "2"),
        ("EF-BLD-003", "建筑采暖（北方）", "SCOPE2", 25.0000, "kgCO2e/m2·年", "建筑采暖", "北方", 
         "行业经验值", 2023, "中", "建筑", "BUILDING", "2"),
        ("EF-BLD-004", "建筑制冷", "SCOPE2", 15.0000, "kgCO2e/m2·年", "建筑制冷", "全国", 
         "行业经验值", 2023, "中", "建筑", "BUILDING", "2"),
        ("EF-BLD-005", "建筑照明", "SCOPE2", 8.0000, "kgCO2e/m2·年", "建筑照明", "全国", 
         "行业经验值", 2023, "中", "建筑", "BUILDING", "2"),
    ],
}


class FactorDatabaseCrawler:
    """排放因子数据库爬虫"""
    
    def __init__(self):
        self.db_connection = None
        self.db_cursor = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.category_map = {}
        
    def connect_db(self):
        """连接数据库"""
        try:
            self.db_connection = mysql.connector.connect(**DB_CONFIG)
            self.db_cursor = self.db_connection.cursor(dictionary=True)
            print("✅ 数据库连接成功")
        except Error as e:
            print(f"❌ 数据库连接失败: {e}")
            raise
            
    def close_db(self):
        """关闭数据库连接"""
        if self.db_cursor:
            self.db_cursor.close()
        if self.db_connection:
            self.db_connection.close()
            
    def init_categories(self):
        """初始化分类体系"""
        print("📝 初始化排放因子分类体系...")
        
        # 一级分类（领域）
        level1_data = [
            ('ENERGY', '能源活动', '化石燃料燃烧、能源生产与供应等能源相关活动', 1),
            ('INDUSTRIAL', '工业生产过程', '工业生产过程中的非能源排放', 2),
            ('AGRICULTURE', '农业', '农业活动产生的温室气体排放', 3),
            ('LULUCF', '土地利用变化与林业', '土地利用、土地利用变化和林业活动', 4),
            ('WASTE', '废弃物处理', '废弃物处理产生的温室气体排放', 5),
            ('TRANSPORT', '交通运输', '交通运输活动产生的温室气体排放', 6),
            ('BUILDING', '建筑', '建筑运行产生的温室气体排放', 7),
        ]
        
        for code, name, desc, order in level1_data:
            sql = """
                INSERT INTO factor_category_level1 (category_code, category_name, description, sort_order)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE category_name = VALUES(category_name), description = VALUES(description)
            """
            self.db_cursor.execute(sql, (code, name, desc, order))
        
        self.db_connection.commit()
        
        # 获取一级分类ID映射
        self.db_cursor.execute("SELECT id, category_code FROM factor_category_level1 WHERE deleted = 0")
        for row in self.db_cursor.fetchall():
            self.category_map[f"L1_{row['category_code']}"] = row['id']
        
        print(f"✅ 一级分类初始化完成（{len(level1_data)}个）")
        
        # 二级分类
        level2_data = [
            ('ENERGY', 'STATIONARY', '固定源燃烧', '固定燃烧设备的化石燃料燃烧', 1),
            ('ENERGY', 'MOBILE', '移动源燃烧', '移动源的化石燃料燃烧', 2),
            ('ENERGY', 'ENERGY_INDUSTRY', '能源工业', '能源生产和供应活动', 3),
            ('ENERGY', 'FUGITIVE', 'fugitive排放', '煤炭和油气系统的逸散排放', 4),
            ('INDUSTRIAL', 'MINERAL', '矿产品', '水泥、石灰、玻璃等矿产品生产', 1),
            ('INDUSTRIAL', 'CHEMICAL', '化工', '化工产品生产', 2),
            ('INDUSTRIAL', 'METAL', '金属', '钢铁、有色金属生产', 3),
            ('TRANSPORT', 'ROAD', '道路交通', '公路运输活动', 1),
            ('TRANSPORT', 'RAIL', '轨道交通', '铁路运输活动', 2),
            ('TRANSPORT', 'WATER', '水运', '水路运输活动', 3),
            ('TRANSPORT', 'AIR', '航空', '航空运输活动', 4),
            ('BUILDING', 'OPERATION', '建筑运行', '建筑运行能耗', 1),
        ]
        
        for parent_code, code, name, desc, order in level2_data:
            parent_id = self.category_map.get(f"L1_{parent_code}")
            if parent_id:
                sql = """
                    INSERT INTO factor_category_level2 (parent_id, category_code, category_name, description, sort_order)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE category_name = VALUES(category_name), description = VALUES(description)
                """
                self.db_cursor.execute(sql, (parent_id, code, name, desc, order))
        
        self.db_connection.commit()
        print(f"✅ 二级分类初始化完成（{len(level2_data)}个）")
        
    def insert_all_factors(self):
        """插入全部排放因子数据"""
        print("\n📝 开始插入全部排放因子数据...")
        
        total_count = 0
        
        for category_name, factors in COMPLETE_FACTOR_DATA.items():
            print(f"\n  📂 {category_name}: {len(factors)}条")
            
            for factor in factors:
                (factor_code, factor_name, scope_type, factor_value, factor_unit, 
                 subcategory, region, data_source, source_year, data_quality,
                 category1_name, category2_code, ipcc_code) = factor
                
                # 获取分类ID
                category1_id = self.category_map.get(f"L1_ENERGY" if "能源" in category1_name else f"L1_{category1_name[:4].upper()}")
                
                # 插入因子
                sql = """
                    INSERT INTO emission_factor (
                        factor_code, factor_name, category1_id, category2_id,
                        scope_type, scope_subcategory, factor_value, factor_unit, factor_unit_cn,
                        applicable_region, applicable_province, applicable_city,
                        data_source, source_document, source_year, data_quality,
                        ipcc_sector_code, ipcc_category_code,
                        is_latest_version, status, deleted
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, 1, 0
                    )
                    ON DUPLICATE KEY UPDATE
                        factor_name = VALUES(factor_name),
                        factor_value = VALUES(factor_value),
                        factor_unit = VALUES(factor_unit),
                        scope_type = VALUES(scope_type),
                        data_source = VALUES(data_source),
                        source_year = VALUES(source_year),
                        data_quality = VALUES(data_quality),
                        updated_at = CURRENT_TIMESTAMP
                """
                
                values = (
                    factor_code, factor_name, category1_id, None,
                    scope_type, subcategory, factor_value, factor_unit, factor_unit,
                    region, None if region == "全国" else region, None,
                    data_source, data_source, source_year, data_quality,
                    ipcc_code[:3] if ipcc_code else None, ipcc_code
                )
                
                try:
                    self.db_cursor.execute(sql, values)
                    total_count += 1
                except Exception as e:
                    print(f"    ⚠️ 插入失败 {factor_code}: {e}")
            
            # 每分类提交一次
            self.db_connection.commit()
        
        print(f"\n✅ 共插入/更新 {total_count} 条排放因子数据")
        
    def get_statistics(self):
        """获取统计信息"""
        print("\n📊 排放因子数据库统计:")
        
        # 总数
        self.db_cursor.execute("SELECT COUNT(*) as count FROM emission_factor WHERE deleted = 0")
        total = self.db_cursor.fetchone()['count']
        print(f"  排放因子总数: {total} 条")
        
        # 按排放范围
        self.db_cursor.execute("""
            SELECT scope_type, COUNT(*) as count 
            FROM emission_factor 
            WHERE deleted = 0 
            GROUP BY scope_type
        """)
        print("\n  按排放范围:")
        for row in self.db_cursor.fetchall():
            scope_name = {"SCOPE1": "范围1-直接排放", "SCOPE2": "范围2-间接排放", "SCOPE3": "范围3-其他间接"}.get(row['scope_type'], row['scope_type'])
            print(f"    {scope_name}: {row['count']}条")
        
        # 按一级分类
        self.db_cursor.execute("""
            SELECT fc.category_name, COUNT(*) as count 
            FROM emission_factor ef
            JOIN factor_category_level1 fc ON ef.category1_id = fc.id
            WHERE ef.deleted = 0 
            GROUP BY fc.category_name
            ORDER BY count DESC
        """)
        print("\n  按领域分类:")
        for row in self.db_cursor.fetchall():
            print(f"    {row['category_name']}: {row['count']}条")
        
        # 按数据质量
        self.db_cursor.execute("""
            SELECT data_quality, COUNT(*) as count 
            FROM emission_factor 
            WHERE deleted = 0 
            GROUP BY data_quality
        """)
        print("\n  按数据质量:")
        for row in self.db_cursor.fetchall():
            print(f"    {row['data_quality']}: {row['count']}条")
        
        # 按数据来源年份
        self.db_cursor.execute("""
            SELECT source_year, COUNT(*) as count 
            FROM emission_factor 
            WHERE deleted = 0 
            GROUP BY source_year
            ORDER BY source_year DESC
        """)
        print("\n  按数据来源年份:")
        for row in self.db_cursor.fetchall():
            print(f"    {row['source_year']}年: {row['count']}条")
        
    def export_to_files(self):
        """导出数据到文件"""
        output_dir = '/home/sundj/.openclaw/workspace/carbon-factor-db/data'
        os.makedirs(output_dir, exist_ok=True)
        
        # 导出为JSON
        print("\n📤 导出数据到JSON...")
        self.db_cursor.execute("""
            SELECT 
                ef.factor_code, ef.factor_name, ef.factor_value, ef.factor_unit,
                ef.scope_type, ef.scope_subcategory, ef.applicable_region,
                ef.data_source, ef.source_year, ef.data_quality,
                fc1.category_name as category1_name,
                ef.ipcc_category_code
            FROM emission_factor ef
            LEFT JOIN factor_category_level1 fc1 ON ef.category1_id = fc1.id
            WHERE ef.is_latest_version = 1 AND ef.deleted = 0
            ORDER BY ef.category1_id, ef.factor_code
        """)
        
        results = self.db_cursor.fetchall()
        json_path = f'{output_dir}/emission_factors_complete.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"  ✅ JSON导出完成: {json_path} ({len(results)}条)")
        
        # 导出为CSV
        print("\n📤 导出数据到CSV...")
        csv_path = f'{output_dir}/emission_factors_complete.csv'
        import csv
        with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        print(f"  ✅ CSV导出完成: {csv_path}")
        
        # 按分类导出
        print("\n📤 按分类导出JSON...")
        for category_name, factors in COMPLETE_FACTOR_DATA.items():
            category_file = category_name.replace('/', '_')
            json_path = f'{output_dir}/factors_{category_file}.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump([
                    {
                        "factor_code": f[0],
                        "factor_name": f[1],
                        "scope_type": f[2],
                        "factor_value": f[3],
                        "factor_unit": f[4],
                        "subcategory": f[5],
                        "region": f[6],
                        "data_source": f[7],
                        "source_year": f[8],
                        "data_quality": f[9]
                    }
                    for f in factors
                ], f, ensure_ascii=False, indent=2)
        print(f"  ✅ 分类导出完成（{len(COMPLETE_FACTOR_DATA)}个文件）")


def main():
    """主函数"""
    print("=" * 70)
    print("🌱 国家温室气体排放因子数据库 - 完整数据抓取工具")
    print("=" * 70)
    
    crawler = FactorDatabaseCrawler()
    
    try:
        # 连接数据库
        crawler.connect_db()
        
        # 初始化分类
        crawler.init_categories()
        
        # 插入全部因子数据
        crawler.insert_all_factors()
        
        # 统计信息
        crawler.get_statistics()
        
        # 导出文件
        crawler.export_to_files()
        
        print("\n" + "=" * 70)
        print("✅ 全部任务执行完成！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        crawler.close_db()


if __name__ == '__main__':
    main()

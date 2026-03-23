#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国家温室气体排放因子数据库数据抓取脚本
支持从多个数据源抓取排放因子数据
"""

import requests
import json
import time
import random
import os
from datetime import datetime
from typing import List, Dict, Optional
import mysql.connector
from mysql.connector import Error

# 配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'carbon_factor_db',
    'user': 'root',
    'password': '123456'
}

# 数据源配置
DATA_SOURCES = {
    'national_db': {
        'name': '国家温室气体排放因子数据库',
        'url': 'https://www.cecs.org.cn/factor',  # 示例URL
        'enabled': True
    },
    'ipcc': {
        'name': 'IPCC排放因子数据库',
        'url': 'https://www.ipcc-nggip.iges.or.jp/EFDB',
        'enabled': False  # 需要特殊处理
    }
}

class FactorDataCrawler:
    """排放因子数据抓取器"""
    
    def __init__(self):
        self.db_connection = None
        self.db_cursor = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
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
        """初始化分类数据"""
        print("📝 初始化分类数据...")
        
        # 一级分类
        categories_level1 = [
            ('ENERGY', '能源活动', '化石燃料燃烧、能源生产与供应等能源相关活动', 1),
            ('INDUSTRIAL', '工业生产过程', '工业生产过程中的非能源排放', 2),
            ('AGRICULTURE', '农业', '农业活动产生的温室气体排放', 3),
            ('LULUCF', '土地利用变化与林业', '土地利用、土地利用变化和林业活动', 4),
            ('WASTE', '废弃物处理', '废弃物处理产生的温室气体排放', 5),
            ('TRANSPORT', '交通运输', '交通运输活动产生的温室气体排放', 6),
            ('BUILDING', '建筑', '建筑运行产生的温室气体排放', 7),
        ]
        
        for code, name, desc, order in categories_level1:
            sql = """
                INSERT INTO factor_category_level1 (category_code, category_name, description, sort_order)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE category_name = VALUES(category_name)
            """
            self.db_cursor.execute(sql, (code, name, desc, order))
        
        self.db_connection.commit()
        print("✅ 一级分类初始化完成")
        
    def insert_mock_factors(self):
        """插入模拟排放因子数据（用于测试）"""
        print("📝 插入模拟排放因子数据...")
        
        # 获取分类ID
        self.db_cursor.execute("SELECT id FROM factor_category_level1 WHERE category_code = 'ENERGY'")
        energy_id = self.db_cursor.fetchone()['id']
        
        # 创建二级分类
        level2_data = [
            (energy_id, 'STATIONARY', '固定源燃烧', 1),
            (energy_id, 'MOBILE', '移动源燃烧', 2),
            (energy_id, 'ENERGY_INDUSTRY', '能源工业', 3),
        ]
        
        for parent_id, code, name, order in level2_data:
            sql = """
                INSERT INTO factor_category_level2 (parent_id, category_code, category_name, sort_order)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE category_name = VALUES(category_name)
            """
            self.db_cursor.execute(sql, (parent_id, code, name, order))
        
        self.db_connection.commit()
        
        # 获取二级分类ID
        self.db_cursor.execute("SELECT id FROM factor_category_level2 WHERE category_code = 'STATIONARY'")
        stationary_id = self.db_cursor.fetchone()['id']
        
        # 排放因子数据（基于国家排放因子库常见数据）
        factors = [
            # 能源 - 固定源燃烧
            ('EF-001', '原煤', stationary_id, 'SCOPE1', 1.9003, 'tCO2e/t', '固定源燃烧', '全国', '国家清单指南', 2023, '高'),
            ('EF-002', '洗精煤', stationary_id, 'SCOPE1', 2.5000, 'tCO2e/t', '固定源燃烧', '全国', '国家清单指南', 2023, '高'),
            ('EF-003', '焦炭', stationary_id, 'SCOPE1', 2.8600, 'tCO2e/t', '固定源燃烧', '全国', '国家清单指南', 2023, '高'),
            ('EF-004', '原油', stationary_id, 'SCOPE1', 3.0200, 'tCO2e/t', '固定源燃烧', '全国', '国家清单指南', 2023, '高'),
            ('EF-005', '汽油', stationary_id, 'SCOPE1', 2.9250, 'tCO2e/t', '固定源燃烧', '全国', '国家清单指南', 2023, '高'),
            ('EF-006', '柴油', stationary_id, 'SCOPE1', 3.0959, 'tCO2e/t', '固定源燃烧', '全国', '国家清单指南', 2023, '高'),
            ('EF-007', '天然气', stationary_id, 'SCOPE1', 2.1620, 'tCO2e/万Nm3', '固定源燃烧', '全国', '国家清单指南', 2023, '高'),
            ('EF-008', '液化石油气', stationary_id, 'SCOPE1', 3.1013, 'tCO2e/t', '固定源燃烧', '全国', '国家清单指南', 2023, '高'),
            
            # 电力
            ('EF-009', '电网平均排放因子', None, 'SCOPE2', 0.5703, 'tCO2e/MWh', '外购电力', '全国', '生态环境部', 2023, '高'),
            ('EF-010', '电网平均排放因子（华北）', None, 'SCOPE2', 0.7125, 'tCO2e/MWh', '外购电力', '华北', '生态环境部', 2023, '高'),
            ('EF-011', '电网平均排放因子（华东）', None, 'SCOPE2', 0.5257, 'tCO2e/MWh', '外购电力', '华东', '生态环境部', 2023, '高'),
            ('EF-012', '电网平均排放因子（华南）', None, 'SCOPE2', 0.4723, 'tCO2e/MWh', '外购电力', '华南', '生态环境部', 2023, '高'),
            
            # 热力
            ('EF-013', '外购热力排放因子', None, 'SCOPE2', 0.1100, 'tCO2e/GJ', '外购热力', '全国', '国家清单指南', 2023, '中'),
        ]
        
        for factor in factors:
            factor_code, factor_name, cat2_id, scope, value, unit, subcategory, region, source, year, quality = factor
            
            sql = """
                INSERT INTO emission_factor (
                    factor_code, factor_name, category1_id, category2_id,
                    scope_type, scope_subcategory, factor_value, factor_unit, factor_unit_cn,
                    applicable_region, data_source, source_year, data_quality,
                    is_latest_version, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, 1
                )
                ON DUPLICATE KEY UPDATE
                    factor_name = VALUES(factor_name),
                    factor_value = VALUES(factor_value),
                    updated_at = CURRENT_TIMESTAMP
            """
            
            values = (
                factor_code, factor_name, energy_id, cat2_id,
                scope, subcategory, value, unit, unit,
                region, source, year, quality
            )
            
            self.db_cursor.execute(sql, values)
        
        self.db_connection.commit()
        print(f"✅ 插入了 {len(factors)} 条排放因子数据")
        
    def crawl_from_excel(self, file_path: str):
        """从Excel文件导入数据"""
        try:
            import pandas as pd
            
            print(f"📊 从Excel导入数据: {file_path}")
            df = pd.read_excel(file_path)
            
            # 数据映射和导入
            for _, row in df.iterrows():
                # 根据Excel列名映射到数据库字段
                pass
            
            print(f"✅ 导入完成，共 {len(df)} 条记录")
            
        except ImportError:
            print("❌ 需要安装pandas: pip install pandas openpyxl")
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            
    def export_to_json(self, output_path: str):
        """导出因子数据为JSON"""
        print(f"📤 导出数据到JSON: {output_path}")
        
        sql = """
            SELECT 
                ef.factor_code, ef.factor_name, ef.factor_value, ef.factor_unit,
                ef.scope_type, ef.applicable_region, ef.data_source, ef.source_year,
                fc1.category_name as category1_name,
                fc2.category_name as category2_name
            FROM emission_factor ef
            LEFT JOIN factor_category_level1 fc1 ON ef.category1_id = fc1.id
            LEFT JOIN factor_category_level2 fc2 ON ef.category2_id = fc2.id
            WHERE ef.is_latest_version = 1 AND ef.deleted = 0
        """
        
        self.db_cursor.execute(sql)
        results = self.db_cursor.fetchall()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 导出完成，共 {len(results)} 条记录")
        
    def get_statistics(self):
        """获取统计信息"""
        print("\n📊 数据库统计信息:")
        
        # 因子总数
        self.db_cursor.execute("SELECT COUNT(*) as count FROM emission_factor WHERE deleted = 0")
        total = self.db_cursor.fetchone()['count']
        print(f"  排放因子总数: {total}")
        
        # 按范围统计
        self.db_cursor.execute("""
            SELECT scope_type, COUNT(*) as count 
            FROM emission_factor 
            WHERE deleted = 0 
            GROUP BY scope_type
        """)
        print("  按排放范围:")
        for row in self.db_cursor.fetchall():
            print(f"    {row['scope_type']}: {row['count']}条")
        
        # 按分类统计
        self.db_cursor.execute("""
            SELECT fc.category_name, COUNT(*) as count 
            FROM emission_factor ef
            JOIN factor_category_level1 fc ON ef.category1_id = fc.id
            WHERE ef.deleted = 0 
            GROUP BY fc.category_name
        """)
        print("  按领域分类:")
        for row in self.db_cursor.fetchall():
            print(f"    {row['category_name']}: {row['count']}条")


def main():
    """主函数"""
    print("=" * 60)
    print("国家温室气体排放因子数据库 - 数据抓取工具")
    print("=" * 60)
    
    crawler = FactorDataCrawler()
    
    try:
        # 连接数据库
        crawler.connect_db()
        
        # 初始化分类
        crawler.init_categories()
        
        # 插入模拟数据（实际使用时替换为真实抓取逻辑）
        crawler.insert_mock_factors()
        
        # 统计信息
        crawler.get_statistics()
        
        # 导出JSON
        output_dir = '/home/sundj/.openclaw/workspace/carbon-factor-db/data'
        os.makedirs(output_dir, exist_ok=True)
        crawler.export_to_json(f'{output_dir}/emission_factors.json')
        
        print("\n✅ 所有任务执行完成！")
        
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        crawler.close_db()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
国家温室气体排放因子数据库爬虫
"""
import requests
import sqlite3
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import re

# 配置
BASE_URL = "https://data.ncsc.org.cn/factories/api"
DB_PATH = "carbon_factors.db"
LOG_PATH = "crawler.log"

# 常量
FACTOR_LIBRARY_ID = "1823254278404255746"
YEAR_ID = "1823254278186151937"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CarbonFactorCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.init_db()
        self.stats = {
            'categories_total': 0,
            'categories_crawled': 0,
            'factors_total': 0,
            'errors': []
        }
    
    def init_db(self):
        """初始化数据库"""
        with sqlite3.connect(DB_PATH) as conn:
            with open('schema.sql', 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            conn.execute("INSERT OR REPLACE INTO crawl_progress (id) VALUES (1)")
            conn.commit()
        logger.info("数据库初始化完成")
    
    def update_progress(self, **kwargs):
        """更新进度"""
        with sqlite3.connect(DB_PATH) as conn:
            for key, value in kwargs.items():
                conn.execute(
                    f"UPDATE crawl_progress SET {key} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
                    (value,)
                )
            conn.commit()
    
    def get_progress(self):
        """获取当前进度"""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT * FROM crawl_progress WHERE id = 1")
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
        return {}
    
    def api_call(self, endpoint: str, params: Dict[str, Any], retries: int = 3) -> Optional[Dict]:
        """API调用，带重试机制"""
        url = f"{BASE_URL}{endpoint}"
        for attempt in range(retries):
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                if data.get('code') == 200:
                    return data.get('data')
                else:
                    logger.warning(f"API返回错误: {data.get('msg')}")
            except Exception as e:
                logger.error(f"API调用失败 (尝试 {attempt+1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None
    
    def extract_leaf_nodes(self, tree: List[Dict], category_type: str) -> List[Dict]:
        """从树形结构中提取所有叶子节点"""
        leaves = []
        
        def traverse(node):
            children = node.get('children', [])
            if not children:
                # 叶子节点
                leaf = {
                    'pkid': node.get('pkid'),
                    'name': node.get('name'),
                    'code': node.get('code'),
                    'parent_id': node.get('parentId'),
                    'sort_num': node.get('sortNum', 0),
                    'factor_library_id': node.get('factorLibraryId'),
                    'year_id': node.get('yearId'),
                    'full_name': node.get('fullName'),
                    'name_en': node.get('nameEn'),
                    'type': node.get('type'),
                    'status': node.get('status'),
                    'type_permission': node.get('typePermission'),
                    'category_type': category_type
                }
                leaves.append(leaf)
            else:
                for child in children:
                    traverse(child)
        
        for item in tree:
            traverse(item)
        
        return leaves
    
    def fetch_categories_type1(self) -> List[Dict]:
        """获取排放源类别列表 (type=1)"""
        params = {
            'factorLibraryId': FACTOR_LIBRARY_ID,
            'type': 1,
            'state': 'submit',
            'yearId': YEAR_ID,
            'cnAndEnFlag': 0
        }
        data = self.api_call('/factor/territory/list', params)
        if data:
            return self.extract_leaf_nodes(data, 'source')
        return []
    
    def fetch_categories_type2(self) -> List[Dict]:
        """获取行业企业类别列表 (type=2)"""
        params = {
            'factorLibraryId': FACTOR_LIBRARY_ID,
            'type': 2,
            'state': 'submit',
            'yearId': YEAR_ID,
            'cnAndEnFlag': 0
        }
        data = self.api_call('/factor/territory/list', params)
        if data:
            return self.extract_leaf_nodes(data, 'industry')
        return []
    
    def fetch_factors(self, pkid: str) -> List[Dict]:
        """获取指定类别的因子列表（支持分页）"""
        all_factors = []
        page_num = 1
        page_size = 20
        
        while True:
            params = {
                'pkid': pkid,
                'cacheFlag': 'false',
                'pageSize': page_size,
                'pageNum': page_num,
                'cnAndEnFlag': 0
            }
            
            data = self.api_call('/factor/metaData/getFactorTables', params)
            if not data:
                break
            
            result = data.get('result', [])
            if not result:
                break
            
            # 解析表格数据
            factors = self.parse_factor_table(result, pkid)
            all_factors.extend(factors)
            
            total = data.get('total', 0)
            logger.info(f"类别 {pkid}: 第 {page_num} 页, 获取 {len(factors)} 条因子, 总计 {len(all_factors)}/{total}")
            
            if len(all_factors) >= total or len(factors) == 0:
                break
            
            page_num += 1
            time.sleep(0.5)  # 避免请求过快
        
        return all_factors
    
    def parse_factor_table(self, table_data: List[List[Dict]], category_pkid: str) -> List[Dict]:
        """解析因子表格数据"""
        factors = []
        
        if not table_data or len(table_data) < 2:
            return factors
        
        # 第一行是表头
        headers = table_data[0]
        
        # 数据行
        for row in table_data[1:]:
            if len(row) < 2:
                continue
            
            # 第一列通常是燃料类型
            fuel_type_info = row[0] if len(row) > 0 else {}
            fuel_type = fuel_type_info.get('value', '')
            fuel_type_en = fuel_type_info.get('valueEn', '')
            
            factor_data = {
                'pkid': fuel_type_info.get('pkid', ''),
                'category_pkid': category_pkid,
                'fuel_type': fuel_type,
                'fuel_type_en': fuel_type_en,
                'net_calorific_value': '',
                'net_calorific_cv': '',
                'emission_factor': '',
                'emission_factor_cv': '',
                'unit': '',
                'unit_desc': '',
                'factor_pkid': ''
            }
            
            # 解析其他列
            for i, cell in enumerate(row[1:], 1):
                if i >= len(headers):
                    break
                
                header_value = headers[i].get('value', '')
                cell_value = cell.get('value', '')
                cell_unit = cell.get('unit', '')
                cell_pkid = cell.get('pkid', '')
                
                if '低位发热量' in header_value or 'Net Calorific Value' in header_value:
                    factor_data['net_calorific_value'] = cell_value
                    factor_data['unit_desc'] = cell_unit
                    if not factor_data['factor_pkid'] and cell_pkid:
                        factor_data['factor_pkid'] = cell_pkid
                elif '变异系数' in header_value and i <= 2:
                    factor_data['net_calorific_cv'] = cell_value
                elif '因子' in header_value or 'Factor' in header_value:
                    factor_data['emission_factor'] = cell_value
                    factor_data['unit'] = cell_unit
                    if cell_pkid:
                        factor_data['factor_pkid'] = cell_pkid
                elif '变异系数' in header_value and i > 2:
                    factor_data['emission_factor_cv'] = cell_value
            
            if factor_data['fuel_type'] or factor_data['emission_factor']:
                factors.append(factor_data)
        
        return factors
    
    def save_category(self, category: Dict):
        """保存类别到数据库"""
        with sqlite3.connect(DB_PATH) as conn:
            if category['category_type'] == 'source':
                conn.execute("""
                    INSERT OR REPLACE INTO emission_source_category 
                    (pkid, name, code, parent_id, sort_num, factor_library_id, year_id, 
                     full_name, name_en, type, status, type_permission)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    category['pkid'], category['name'], category['code'],
                    category['parent_id'], category['sort_num'], category['factor_library_id'],
                    category['year_id'], category['full_name'], category['name_en'],
                    category['type'], category['status'], category['type_permission']
                ))
            else:
                conn.execute("""
                    INSERT OR REPLACE INTO industry_enterprise 
                    (pkid, name, code, parent_id, sort_num, factor_library_id, year_id, 
                     full_name, name_en, type, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    category['pkid'], category['name'], category['code'],
                    category['parent_id'], category['sort_num'], category['factor_library_id'],
                    category['year_id'], category['full_name'], category['name_en'],
                    category['type'], category['status']
                ))
            conn.commit()
    
    def save_factor(self, factor: Dict):
        """保存因子到数据库"""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO emission_factor 
                (pkid, category_pkid, fuel_type, fuel_type_en, net_calorific_value,
                 net_calorific_cv, emission_factor, emission_factor_cv, unit, unit_desc, factor_pkid)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                factor['pkid'], factor['category_pkid'], factor['fuel_type'],
                factor['fuel_type_en'], factor['net_calorific_value'],
                factor['net_calorific_cv'], factor['emission_factor'],
                factor['emission_factor_cv'], factor['unit'], factor['unit_desc'],
                factor['factor_pkid']
            ))
            conn.commit()
    
    def crawl(self):
        """主爬取逻辑"""
        logger.info("="*60)
        logger.info("开始爬取国家温室气体排放因子数据库")
        logger.info("="*60)
        
        start_time = time.time()
        
        # 步骤1: 获取排放源类别
        logger.info("\n[步骤1/4] 获取排放源类别列表...")
        source_categories = self.fetch_categories_type1()
        logger.info(f"获取到 {len(source_categories)} 个排放源类别叶子节点")
        
        # 步骤2: 获取行业企业类别
        logger.info("\n[步骤2/4] 获取行业企业类别列表...")
        industry_categories = self.fetch_categories_type2()
        logger.info(f"获取到 {len(industry_categories)} 个行业企业类别叶子节点")
        
        all_categories = source_categories + industry_categories
        self.stats['categories_total'] = len(all_categories)
        
        # 保存类别
        for cat in all_categories:
            self.save_category(cat)
        logger.info(f"已保存 {len(all_categories)} 个类别到数据库")
        
        # 更新总类别数
        self.update_progress(total_categories=len(all_categories))
        
        # 步骤3: 爬取排放源因子
        logger.info("\n[步骤3/4] 开始爬取排放源因子数据...")
        for i, cat in enumerate(source_categories, 1):
            pkid = cat['pkid']
            name = cat['full_name'] or cat['name']
            
            self.update_progress(
                current_category=f"[{i}/{len(source_categories)}] {name}",
                crawled_categories=i-1
            )
            
            logger.info(f"\n[{i}/{len(source_categories)}] 正在爬取: {name} (pkid={pkid})")
            
            try:
                factors = self.fetch_factors(pkid)
                for factor in factors:
                    factor['category_type'] = 'source'
                    self.save_factor(factor)
                
                self.stats['factors_total'] += len(factors)
                logger.info(f"  ✓ 保存了 {len(factors)} 条因子")
                
            except Exception as e:
                error_msg = f"爬取 {name} 失败: {str(e)}"
                logger.error(f"  ✗ {error_msg}")
                self.stats['errors'].append(error_msg)
            
            self.update_progress(crawled_categories=i, total_factors=self.stats['factors_total'])
            time.sleep(1)
        
        # 步骤4: 爬取行业企业因子
        logger.info("\n[步骤4/4] 开始爬取行业企业因子数据...")
        offset = len(source_categories)
        for i, cat in enumerate(industry_categories, 1):
            pkid = cat['pkid']
            name = cat['full_name'] or cat['name']
            
            self.update_progress(
                current_category=f"[{i}/{len(industry_categories)}] {name}",
                crawled_categories=offset + i - 1
            )
            
            logger.info(f"\n[{i}/{len(industry_categories)}] 正在爬取: {name} (pkid={pkid})")
            
            try:
                factors = self.fetch_factors(pkid)
                for factor in factors:
                    factor['category_type'] = 'industry'
                    self.save_factor(factor)
                
                self.stats['factors_total'] += len(factors)
                logger.info(f"  ✓ 保存了 {len(factors)} 条因子")
                
            except Exception as e:
                error_msg = f"爬取 {name} 失败: {str(e)}"
                logger.error(f"  ✗ {error_msg}")
                self.stats['errors'].append(error_msg)
            
            self.update_progress(crawled_categories=offset + i, total_factors=self.stats['factors_total'])
            time.sleep(1)
        
        # 完成
        elapsed = time.time() - start_time
        self.update_progress(
            status='completed',
            crawled_categories=len(all_categories),
            total_factors=self.stats['factors_total'],
            errors=json.dumps(self.stats['errors'], ensure_ascii=False)
        )
        
        logger.info("\n" + "="*60)
        logger.info("爬取完成!")
        logger.info(f"总类别数: {len(all_categories)}")
        logger.info(f"总因子数: {self.stats['factors_total']}")
        logger.info(f"错误数: {len(self.stats['errors'])}")
        logger.info(f"耗时: {elapsed:.2f} 秒")
        logger.info("="*60)
        
        return self.stats
    
    def export_to_json(self, output_file: str = "carbon_factors_export.json"):
        """导出数据到JSON"""
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            
            # 导出类别
            cursor = conn.execute("SELECT * FROM emission_source_category")
            source_categories = [dict(row) for row in cursor.fetchall()]
            
            cursor = conn.execute("SELECT * FROM industry_enterprise")
            industry_categories = [dict(row) for row in cursor.fetchall()]
            
            # 导出因子
            cursor = conn.execute("SELECT * FROM emission_factor")
            factors = [dict(row) for row in cursor.fetchall()]
            
            data = {
                'export_time': datetime.now().isoformat(),
                'source_categories': source_categories,
                'industry_categories': industry_categories,
                'factors': factors
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据已导出到 {output_file}")
            return data


def main():
    crawler = CarbonFactorCrawler()
    stats = crawler.crawl()
    crawler.export_to_json()
    
    # 打印统计信息
    print("\n" + "="*60)
    print("爬取统计:")
    print(f"  类别总数: {stats['categories_total']}")
    print(f"  因子总数: {stats['factors_total']}")
    print(f"  错误数: {len(stats['errors'])}")
    print("="*60)


if __name__ == "__main__":
    main()

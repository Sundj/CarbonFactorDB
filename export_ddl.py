#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出SQLite数据库为DDL文件
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = '/home/sundj/.openclaw/workspace/carbon-factor-db/carbon_factors.db'
OUTPUT_DIR = '/home/sundj/.openclaw/workspace/carbon-factor-db'

def export_schema(conn):
    """导出表结构"""
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    schema_sql = []
    schema_sql.append("-- ========================================================")
    schema_sql.append("-- 国家温室气体排放因子数据库 - DDL Schema")
    schema_sql.append(f"-- 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    schema_sql.append(f"-- 数据库文件: carbon_factors.db")
    schema_sql.append("-- ========================================================")
    schema_sql.append("")
    
    for (table_name,) in tables:
        if table_name.startswith('sqlite_'):
            continue
            
        # 获取建表语句
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        create_sql = cursor.fetchone()[0]
        
        schema_sql.append(f"-- Table: {table_name}")
        schema_sql.append(f"DROP TABLE IF EXISTS {table_name};")
        schema_sql.append(create_sql + ";")
        schema_sql.append("")
        
        # 获取索引
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}' AND sql IS NOT NULL")
        indexes = cursor.fetchall()
        for (index_sql,) in indexes:
            schema_sql.append(index_sql + ";")
        
        if indexes:
            schema_sql.append("")
    
    return '\n'.join(schema_sql)

def export_data(conn):
    """导出数据为INSERT语句"""
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    data_sql = []
    data_sql.append("-- ========================================================")
    data_sql.append("-- 国家温室气体排放因子数据库 - 数据导入脚本")
    data_sql.append(f"-- 导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    data_sql.append(f"-- 数据库文件: carbon_factors.db")
    data_sql.append("-- ========================================================")
    data_sql.append("")
    data_sql.append("PRAGMA foreign_keys = OFF;")
    data_sql.append("")
    
    total_rows = 0
    
    for (table_name,) in tables:
        if table_name.startswith('sqlite_'):
            continue
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # 获取数据
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        if not rows:
            continue
        
        data_sql.append(f"-- Table: {table_name} ({len(rows)} rows)")
        data_sql.append(f"DELETE FROM {table_name};")
        
        # 批量生成INSERT语句
        for row in rows:
            values = []
            for val in row:
                if val is None:
                    values.append("NULL")
                elif isinstance(val, str):
                    # 转义单引号
                    escaped = val.replace("'", "''")
                    values.append(f"'{escaped}'")
                elif isinstance(val, int):
                    values.append(str(val))
                elif isinstance(val, float):
                    values.append(str(val))
                else:
                    values.append(f"'{str(val)}'")
            
            insert = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({', '.join(values)});"
            data_sql.append(insert)
        
        data_sql.append("")
        total_rows += len(rows)
    
    data_sql.append("PRAGMA foreign_keys = ON;")
    data_sql.append("")
    data_sql.append(f"-- Total rows exported: {total_rows}")
    
    return '\n'.join(data_sql), total_rows

def main():
    print("🔄 导出SQLite数据库为DDL文件...")
    print(f"数据库: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ 数据库文件不存在: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # 导出Schema
        print("\n📄 导出表结构...")
        schema = export_schema(conn)
        schema_path = os.path.join(OUTPUT_DIR, 'ddl_schema.sql')
        with open(schema_path, 'w', encoding='utf-8') as f:
            f.write(schema)
        print(f"✅ Schema导出完成: {schema_path}")
        
        # 导出数据
        print("\n📄 导出数据...")
        data, total_rows = export_data(conn)
        data_path = os.path.join(OUTPUT_DIR, 'ddl_data.sql')
        with open(data_path, 'w', encoding='utf-8') as f:
            f.write(data)
        print(f"✅ 数据导出完成: {data_path}")
        print(f"   总行数: {total_rows}")
        
        # 导出完整DDL（Schema + Data）
        print("\n📄 导出完整DDL...")
        full_ddl = schema + "\n\n" + "-- ========================================================\n" + data
        full_path = os.path.join(OUTPUT_DIR, 'ddl_full.sql')
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(full_ddl)
        print(f"✅ 完整DDL导出完成: {full_path}")
        
        # 显示文件大小
        print("\n📊 导出文件统计:")
        for filename in ['ddl_schema.sql', 'ddl_data.sql', 'ddl_full.sql']:
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"   {filename}: {size/1024:.1f} KB")
        
        print("\n✅ 全部导出完成！")
        
    finally:
        conn.close()

if __name__ == '__main__':
    main()

import sqlite3
import os
import asyncio

# 零安装的本地数据库引擎
DB_FILE = "mcn_local_data.db"

async def init_db():
    """
    初始化本地单机数据库。
    不需要 Docker，不需要 PostgreSQL 服务，直接在本地生成文件。
    """
    # SQLite 在初始化建表时极快，此处简单封装以兼容现有的 async 调用
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 建立本地数据保险箱
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weibo_mcn_radar (
            uid TEXT PRIMARY KEY,
            nickname TEXT,
            followers INTEGER,
            posts INTEGER,
            cpm REAL,
            original_price INTEGER,
            repost_price INTEGER,
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ 本地单机数据库引擎 (SQLite) 已就绪，零依赖模式启动。")

# 预留给爬虫存数据的同步接口 (方便后续迭代)
def save_data(data: dict):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO weibo_mcn_radar 
        (uid, nickname, followers, posts, cpm, original_price, repost_price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['uid'], data['nickname'], data['followers'], data['posts'],
        data['commercial']['cpm'], data['commercial']['original_price'], data['commercial']['repost_price']
    ))
    conn.commit()
    conn.close()
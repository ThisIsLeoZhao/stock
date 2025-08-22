"""
Data Provider - 数据提供器

专门负责数据访问和基础数据处理功能，使用组合模式而非继承
"""

import sqlite3
import pandas as pd
import numpy as np
import os
from typing import Optional, Dict, List
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class DataProvider:
    """数据提供器类 - 负责数据库操作和基础数据处理"""
    
    def __init__(self, db_path: str = "ticker_data/stock_cache.db"):
        """
        初始化数据提供器
        
        Args:
            db_path: SQLite数据库路径
        """
        self.db_path = db_path
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database not found: {db_path}")
    
    def get_stock_data_from_db(self, ticker: str, interval: str = '1d') -> Optional[pd.DataFrame]:
        """
        从数据库读取股票数据
        
        Args:
            ticker: 股票代码
            interval: 数据间隔 (1d, 1wk, 1mo)
            
        Returns:
            DataFrame containing stock data or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            # 查询数据库中的数据
            query = """
            SELECT date, open_price as "Open", high_price as "High", 
                   low_price as "Low", close_price as "Close", volume as "Volume"
            FROM stock_data 
            WHERE ticker = ? AND interval = ?
            ORDER BY date ASC
            """
            
            df = pd.read_sql_query(query, conn, params=(ticker, interval))
            conn.close()
            
            if df.empty:
                print(f"No data found for {ticker} with interval {interval}")
                return None
            
            # 设置日期为索引
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            
            # 确保数值列为float类型
            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            print(f"✓ Loaded {len(df)} rows of {ticker} data from database")
            print(f"  Date range: {df.index.min().date()} to {df.index.max().date()}")
            
            return df
            
        except Exception as e:
            print(f"Error reading data from database: {e}")
            return None
    
    def get_available_data(self) -> List[Dict]:
        """获取数据库中可用的数据列表"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT ticker, interval, 
                   MIN(date) as start_date, 
                   MAX(date) as end_date,
                   COUNT(*) as record_count,
                   MIN(cached_at) as first_cached,
                   MAX(cached_at) as last_cached
            FROM stock_data 
            GROUP BY ticker, interval
            ORDER BY ticker, interval
            """
            
            result = pd.read_sql_query(query, conn)
            conn.close()
            
            if result.empty:
                print("No data found in database")
                return []
            
            print("\n📦 数据库中可用的数据：")
            for _, row in result.iterrows():
                print(f"   {row['ticker']} ({row['interval']}): "
                      f"{row['start_date']} to {row['end_date']} "
                      f"({row['record_count']} records)")
            
            return result.to_dict('records')
            
        except Exception as e:
            print(f"Error reading database: {e}")
            return []


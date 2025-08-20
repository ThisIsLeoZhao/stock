"""
Cache Manager Module

This module provides a SQLite-based caching system for stock data
with intelligent expiration based on data coverage rather than file timestamps.
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import json


class CacheManager:
    """
    SQLite-based cache manager for stock data.
    
    This class handles all caching operations separately from data fetching,
    providing a clean separation of concerns.
    """
    
    def __init__(self, cache_db_path: str = "ticker_data/stock_cache.db"):
        """
        Initialize the cache manager.
        
        Args:
            cache_db_path (str): Path to SQLite database file
        """
        self.cache_db_path = Path(cache_db_path)
        self.cache_db_path.parent.mkdir(exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self._init_database()
        
        self.logger.info("CacheManager initialized with database: %s", self.cache_db_path)
    
    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    date DATE NOT NULL,
                    open_price REAL NOT NULL,
                    high_price REAL NOT NULL,
                    low_price REAL NOT NULL,
                    close_price REAL NOT NULL,
                    volume INTEGER,
                    cached_at DATETIME NOT NULL,
                    UNIQUE(ticker, interval, date)
                )
            """)
            
            # Create indexes for faster queries with proper date ordering
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ticker_interval_date 
                ON stock_data(ticker, interval, date DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ticker_interval 
                ON stock_data(ticker, interval)
            """)
            
            # Create index for date range queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_date_range 
                ON stock_data(date)
            """)
            
            conn.commit()
    
    def _dataframe_to_rows(self, df: pd.DataFrame) -> list:
        """
        Convert DataFrame to list of row tuples for database insertion.
        
        Args:
            df (pd.DataFrame): DataFrame to convert
            
        Returns:
            list: List of tuples for database insertion
        """
        rows = []
        cached_at = datetime.now().isoformat()
        
        for date_idx, row in df.iterrows():
            # Ensure proper ISO date format for SQLite DATE type
            date_str = date_idx.strftime('%Y-%m-%d')
            volume = int(row.get('Volume', 0)) if pd.notna(row.get('Volume', 0)) else None
            
            row_tuple = (
                date_str,              # DATE format: YYYY-MM-DD
                float(row['Open']),
                float(row['High']),
                float(row['Low']),
                float(row['Close']),
                volume,
                cached_at             # DATETIME format: ISO8601
            )
            rows.append(row_tuple)
        
        return rows
    
    def _rows_to_dataframe(self, rows: list) -> pd.DataFrame:
        """
        Convert database rows back to DataFrame.
        
        Args:
            rows (list): List of database row tuples
            
        Returns:
            pd.DataFrame: Reconstructed DataFrame
        """
        if not rows:
            return pd.DataFrame()
        
        data = []
        for row in rows:
            date_str, open_price, high_price, low_price, close_price, volume, cached_at = row
            
            row_dict = {
                'Open': open_price,
                'High': high_price,
                'Low': low_price,
                'Close': close_price
            }
            
            if volume is not None:
                row_dict['Volume'] = volume
            
            data.append(row_dict)
        
        df = pd.DataFrame(data)
        df.index = pd.to_datetime([row[0] for row in rows])
        
        return df
    
    def _get_cached_date_range(
        self, 
        ticker: str, 
        interval: str
    ) -> Optional[Tuple[date, date]]:
        """
        Get the date range of cached data for a ticker/interval.
        
        Args:
            ticker (str): Stock ticker
            interval (str): Data interval
            
        Returns:
            Optional[Tuple[date, date]]: Start and end dates of cached data, or None
        """
        with sqlite3.connect(self.cache_db_path) as conn:
            cursor = conn.execute("""
                SELECT MIN(date) as min_date, MAX(date) as max_date
                FROM stock_data 
                WHERE ticker = ? AND interval = ?
            """, (ticker, interval))
            
            row = cursor.fetchone()
            if row and row[0] and row[1]:
                # SQLite stores dates as text in ISO format, parse them properly
                start_date = datetime.strptime(row[0], '%Y-%m-%d').date()
                end_date = datetime.strptime(row[1], '%Y-%m-%d').date()
                return start_date, end_date
        
        return None
    
    def _check_data_coverage(
        self,
        ticker: str,
        interval: str,
        requested_start: date,
        requested_end: date
    ) -> bool:
        """
        Check if we have cached data covering the requested date range.
        
        Args:
            ticker (str): Stock ticker
            interval (str): Data interval
            requested_start (date): Start date requested
            requested_end (date): End date requested
            
        Returns:
            bool: True if cached data covers the requested range
        """
        cached_range = self._get_cached_date_range(ticker, interval)
        if not cached_range:
            return False
        
        cached_start, cached_end = cached_range
        
        # Check if cached range covers requested range
        covers_range = (cached_start <= requested_start and cached_end >= requested_end)
        
        if covers_range:
            self.logger.info("Cache covers requested range for %s %s: cached %s to %s, requested %s to %s", 
                           ticker, interval, cached_start, cached_end, requested_start, requested_end)
        else:
            self.logger.info("Cache does not cover requested range for %s %s: cached %s to %s, requested %s to %s", 
                           ticker, interval, cached_start, cached_end, requested_start, requested_end)
        
        return covers_range
    
    def get_cached_data(
        self, 
        ticker: str, 
        interval: str, 
        requested_start: date, 
        requested_end: date
    ) -> Optional[pd.DataFrame]:
        """
        Get cached data for the requested parameters.
        
        Args:
            ticker (str): Stock ticker
            interval (str): Data interval ('1d', '1wk', '1mo')
            requested_start (date): Start date requested
            requested_end (date): End date requested
            
        Returns:
            Optional[pd.DataFrame]: Cached data covering the requested range, or None
        """
        # Check if we have data covering the requested range
        if not self._check_data_coverage(ticker, interval, requested_start, requested_end):
            self.logger.info("No covering cache found for %s %s %s to %s", 
                           ticker, interval, requested_start, requested_end)
            return None
        
        # Query the specific date range from database using proper date comparison
        with sqlite3.connect(self.cache_db_path) as conn:
            cursor = conn.execute("""
                SELECT date, open_price, high_price, low_price, close_price, volume, cached_at
                FROM stock_data 
                WHERE ticker = ? AND interval = ?
                AND date >= DATE(?) AND date <= DATE(?)
                ORDER BY date ASC
            """, (ticker, interval, requested_start.isoformat(), requested_end.isoformat()))
            
            rows = cursor.fetchall()
        
        if not rows:
            self.logger.info("No cached data found for exact date range")
            return None
        
        # Convert rows to DataFrame
        df = self._rows_to_dataframe(rows)
        
        if len(df) > 0:
            self.logger.info("Returning %d rows of cached data for %s %s", 
                           len(df), ticker, interval)
            return df
        else:
            self.logger.info("Cached data exists but no rows match requested date range")
            return None
    
    def cache_data(
        self, 
        ticker: str, 
        interval: str, 
        df: pd.DataFrame
    ):
        """
        Cache the provided DataFrame.
        
        Args:
            ticker (str): Stock ticker
            interval (str): Data interval
            df (pd.DataFrame): Data to cache
        """
        if df.empty:
            self.logger.warning("Attempted to cache empty DataFrame for %s %s", ticker, interval)
            return
        
        start_date = df.index.min().date()
        end_date = df.index.max().date()
        
        try:
            # Convert DataFrame to rows for insertion
            rows = self._dataframe_to_rows(df)
            
            with sqlite3.connect(self.cache_db_path) as conn:
                # Use INSERT OR REPLACE to handle duplicates
                for row in rows:
                    conn.execute("""
                        INSERT OR REPLACE INTO stock_data 
                        (ticker, interval, date, open_price, high_price, low_price, close_price, volume, cached_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (ticker, interval) + row)
                
                conn.commit()
                
            self.logger.info("Cached %d rows for %s %s (%s to %s)", 
                           len(df), ticker, interval, start_date, end_date)
            
        except Exception as e:
            self.logger.error("Failed to cache data for %s %s: %s", ticker, interval, str(e))
    
    def clear_cache(self, ticker: Optional[str] = None, interval: Optional[str] = None):
        """
        Clear cached data.
        
        Args:
            ticker (Optional[str]): If provided, only clear cache for this ticker
            interval (Optional[str]): If provided, only clear cache for this interval
        """
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                if ticker and interval:
                    conn.execute("DELETE FROM stock_data WHERE ticker = ? AND interval = ?", 
                               (ticker, interval))
                    self.logger.info("Cleared cache for %s %s", ticker, interval)
                elif ticker:
                    conn.execute("DELETE FROM stock_data WHERE ticker = ?", (ticker,))
                    self.logger.info("Cleared all cache for ticker %s", ticker)
                elif interval:
                    conn.execute("DELETE FROM stock_data WHERE interval = ?", (interval,))
                    self.logger.info("Cleared all cache for interval %s", interval)
                else:
                    conn.execute("DELETE FROM stock_data")
                    self.logger.info("Cleared all cache data")
                
                conn.commit()
                
        except Exception as e:
            self.logger.error("Failed to clear cache: %s", str(e))
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about cached data.
        
        Returns:
            Dict[str, Any]: Cache statistics and information
        """
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                # Get total count
                total_count = conn.execute("SELECT COUNT(*) FROM stock_data").fetchone()[0]
                
                # Get cache summary by ticker and interval
                cursor = conn.execute("""
                    SELECT ticker, interval, 
                           MIN(date) as start_date, 
                           MAX(date) as end_date,
                           COUNT(*) as row_count,
                           MAX(cached_at) as last_cached
                    FROM stock_data 
                    GROUP BY ticker, interval
                    ORDER BY last_cached DESC
                """)
                
                entries = []
                
                for row in cursor.fetchall():
                    ticker, interval, start_date, end_date, row_count, last_cached = row
                    
                    entries.append({
                        'ticker': ticker,
                        'interval': interval,
                        'start_date': start_date,
                        'end_date': end_date,
                        'row_count': row_count,
                        'last_cached': last_cached
                    })
                
                # Get database file size
                db_size = self.cache_db_path.stat().st_size if self.cache_db_path.exists() else 0
                
                return {
                    'database_path': str(self.cache_db_path),
                    'database_size_mb': round(db_size / (1024 * 1024), 3),
                    'total_entries': total_count,
                    'unique_datasets': len(entries),
                    'entries': entries
                }
                
        except Exception as e:
            self.logger.error("Failed to get cache info: %s", str(e))
            return {
                'database_path': str(self.cache_db_path),
                'error': str(e),
                'total_entries': 0,
                'entries': []
            }
    
    def cleanup_old_cache(self, days_old: int = 30):
        """
        Remove cache entries older than specified days.
        
        Args:
            days_old (int): Remove entries older than this many days
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            with sqlite3.connect(self.cache_db_path) as conn:
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM stock_data 
                    WHERE DATETIME(cached_at) < DATETIME(?)
                """, (cutoff_date,))
                old_count = cursor.fetchone()[0]
                
                conn.execute("""
                    DELETE FROM stock_data 
                    WHERE DATETIME(cached_at) < DATETIME(?)
                """, (cutoff_date,))
                conn.commit()
                
                self.logger.info("Cleaned up %d old cache entries (older than %d days)", 
                               old_count, days_old)
                
        except Exception as e:
            self.logger.error("Failed to cleanup old cache: %s", str(e))

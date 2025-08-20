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
                CREATE TABLE IF NOT EXISTS stock_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    interval TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    cached_at TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    UNIQUE(ticker, interval, start_date, end_date)
                )
            """)
            
            # Create index for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ticker_interval 
                ON stock_cache(ticker, interval)
            """)
            
            conn.commit()
    
    def _serialize_dataframe(self, df: pd.DataFrame) -> str:
        """
        Convert DataFrame to JSON string for storage.
        
        Args:
            df (pd.DataFrame): DataFrame to serialize
            
        Returns:
            str: JSON string representation
        """
        # Convert DataFrame to dict with date index as strings
        data_dict = {
            'index': [d.strftime('%Y-%m-%d') for d in df.index],
            'data': df.to_dict('records')
        }
        return json.dumps(data_dict)
    
    def _deserialize_dataframe(self, data_json: str) -> pd.DataFrame:
        """
        Convert JSON string back to DataFrame.
        
        Args:
            data_json (str): JSON string representation
            
        Returns:
            pd.DataFrame: Reconstructed DataFrame
        """
        data_dict = json.loads(data_json)
        df = pd.DataFrame(data_dict['data'])
        df.index = pd.to_datetime(data_dict['index'])
        return df
    
    def _find_covering_cache(
        self, 
        ticker: str, 
        interval: str, 
        requested_start: date, 
        requested_end: date
    ) -> Optional[Tuple[pd.DataFrame, date, date]]:
        """
        Find cached data that covers the requested date range.
        
        Args:
            ticker (str): Stock ticker
            interval (str): Data interval
            requested_start (date): Start date requested
            requested_end (date): End date requested
            
        Returns:
            Optional[Tuple[pd.DataFrame, date, date]]: Cached data and its date range, or None
        """
        with sqlite3.connect(self.cache_db_path) as conn:
            cursor = conn.execute("""
                SELECT data_json, start_date, end_date, cached_at
                FROM stock_cache 
                WHERE ticker = ? AND interval = ?
                AND start_date <= ? AND end_date >= ?
                ORDER BY cached_at DESC
                LIMIT 1
            """, (ticker, interval, requested_start.isoformat(), requested_end.isoformat()))
            
            row = cursor.fetchone()
            if row:
                data_json, start_date_str, end_date_str, cached_at = row
                try:
                    df = self._deserialize_dataframe(data_json)
                    start_date = datetime.fromisoformat(start_date_str).date()
                    end_date = datetime.fromisoformat(end_date_str).date()
                    
                    self.logger.info("Found covering cache for %s %s: %s to %s", 
                                   ticker, interval, start_date, end_date)
                    return df, start_date, end_date
                    
                except Exception as e:
                    self.logger.error("Failed to deserialize cached data: %s", str(e))
                    return None
        
        return None
    
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
        cache_result = self._find_covering_cache(ticker, interval, requested_start, requested_end)
        
        if cache_result is None:
            self.logger.info("No covering cache found for %s %s %s to %s", 
                           ticker, interval, requested_start, requested_end)
            return None
        
        df, cached_start, cached_end = cache_result
        
        # Filter the cached data to the exact requested range
        filtered_df = df[
            (df.index.date >= requested_start) & 
            (df.index.date <= requested_end)
        ].copy()
        
        if len(filtered_df) > 0:
            self.logger.info("Returning %d rows of cached data for %s %s", 
                           len(filtered_df), ticker, interval)
            return filtered_df
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
        cached_at = datetime.now().isoformat()
        data_json = self._serialize_dataframe(df)
        
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                # Use INSERT OR REPLACE to handle duplicates
                conn.execute("""
                    INSERT OR REPLACE INTO stock_cache 
                    (ticker, interval, start_date, end_date, cached_at, data_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (ticker, interval, start_date.isoformat(), end_date.isoformat(), 
                      cached_at, data_json))
                
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
                    conn.execute("DELETE FROM stock_cache WHERE ticker = ? AND interval = ?", 
                               (ticker, interval))
                    self.logger.info("Cleared cache for %s %s", ticker, interval)
                elif ticker:
                    conn.execute("DELETE FROM stock_cache WHERE ticker = ?", (ticker,))
                    self.logger.info("Cleared all cache for ticker %s", ticker)
                elif interval:
                    conn.execute("DELETE FROM stock_cache WHERE interval = ?", (interval,))
                    self.logger.info("Cleared all cache for interval %s", interval)
                else:
                    conn.execute("DELETE FROM stock_cache")
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
                total_count = conn.execute("SELECT COUNT(*) FROM stock_cache").fetchone()[0]
                
                # Get cache entries with details
                cursor = conn.execute("""
                    SELECT ticker, interval, start_date, end_date, cached_at,
                           LENGTH(data_json) as size_bytes
                    FROM stock_cache 
                    ORDER BY cached_at DESC
                """)
                
                entries = []
                total_size = 0
                
                for row in cursor.fetchall():
                    ticker, interval, start_date, end_date, cached_at, size_bytes = row
                    total_size += size_bytes
                    
                    entries.append({
                        'ticker': ticker,
                        'interval': interval,
                        'start_date': start_date,
                        'end_date': end_date,
                        'cached_at': cached_at,
                        'size_bytes': size_bytes,
                        'size_mb': round(size_bytes / (1024 * 1024), 3)
                    })
                
                # Get database file size
                db_size = self.cache_db_path.stat().st_size if self.cache_db_path.exists() else 0
                
                return {
                    'database_path': str(self.cache_db_path),
                    'database_size_mb': round(db_size / (1024 * 1024), 3),
                    'total_entries': total_count,
                    'total_data_size_mb': round(total_size / (1024 * 1024), 3),
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
                cursor = conn.execute("SELECT COUNT(*) FROM stock_cache WHERE cached_at < ?", 
                                    (cutoff_date,))
                old_count = cursor.fetchone()[0]
                
                conn.execute("DELETE FROM stock_cache WHERE cached_at < ?", (cutoff_date,))
                conn.commit()
                
                self.logger.info("Cleaned up %d old cache entries (older than %d days)", 
                               old_count, days_old)
                
        except Exception as e:
            self.logger.error("Failed to cleanup old cache: %s", str(e))

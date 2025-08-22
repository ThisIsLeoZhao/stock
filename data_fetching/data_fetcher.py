"""
Stock Data Fetcher V2 - Improved Architecture

This module provides a clean separation between data fetching and caching,
with improved cache expiration logic based on data coverage.
"""

import yfinance as yf
import pandas as pd
import logging
from datetime import datetime, timedelta, date
from typing import Optional, Literal, Tuple
from .cache_manager import CacheManager


class DataFetcher:
    """
    Clean data fetcher focused solely on retrieving stock data from APIs.
    
    This class handles only the data fetching logic, delegating all 
    caching operations to the CacheManager.
    """
    
    def __init__(self):
        """Initialize the data fetcher."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("DataFetcher initialized")
    
    def _validate_parameters(self, ticker: str, period: str, interval: str) -> Tuple[str, str, str]:
        """
        Validate and normalize input parameters.
        
        Args:
            ticker (str): Stock ticker symbol
            period (str): Time period
            interval (str): Data interval
            
        Returns:
            Tuple[str, str, str]: Validated parameters
            
        Raises:
            ValueError: If parameters are invalid
        """
        if not ticker or not isinstance(ticker, str):
            raise ValueError("Ticker must be a non-empty string")
        
        ticker = ticker.upper().strip()
        
        # Validate interval
        valid_intervals = ['1d', '1wk', '1mo']
        if interval not in valid_intervals:
            raise ValueError(f"Interval must be one of {valid_intervals}")
        
        # Validate period format
        if not period or len(period) < 2:
            raise ValueError("Period must be in format like '10y', '5y', '2y'")
        
        return ticker, period, interval
    
    def _calculate_date_range(self, period: str) -> Tuple[date, date]:
        """
        Calculate the actual date range for a given period.
        
        Args:
            period (str): Period string like '10y', '5y', '1y', '6mo'
            
        Returns:
            Tuple[date, date]: Start and end dates
        """
        end_date = date.today()
        
        # Parse period string
        if period.endswith('y'):
            years = int(period[:-1])
            start_date = end_date - timedelta(days=years * 365)
        elif period.endswith('mo'):
            months = int(period[:-2])
            start_date = end_date - timedelta(days=months * 30)
        elif period.endswith('d'):
            days = int(period[:-1])
            start_date = end_date - timedelta(days=days)
        else:
            raise ValueError(f"Unsupported period format: {period}")
        
        return start_date, end_date
    
    def fetch_from_api(self, ticker: str, period: str, interval: str) -> pd.DataFrame:
        """
        Fetch data directly from Yahoo Finance API.
        
        Args:
            ticker (str): Stock ticker symbol
            period (str): Time period
            interval (str): Data interval
            
        Returns:
            pd.DataFrame: Stock data with OHLC columns
            
        Raises:
            Exception: If API call fails
        """
        ticker, period, interval = self._validate_parameters(ticker, period, interval)
        
        try:
            self.logger.info("Fetching data from API for %s with period=%s, interval=%s", 
                           ticker, period, interval)
            
            # Create yfinance Ticker object
            stock = yf.Ticker(ticker)
            
            # Fetch historical data
            data = stock.history(period=period, interval=interval, auto_adjust=True, prepost=True)
            
            if data.empty:
                raise ValueError(f"No data found for ticker {ticker}")
            
            # Ensure we have the required OHLC columns
            required_columns = ['Open', 'High', 'Low', 'Close']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Keep only OHLC columns and Volume if available
            columns_to_keep = ['Open', 'High', 'Low', 'Close']
            if 'Volume' in data.columns:
                columns_to_keep.append('Volume')
            
            data = data[columns_to_keep].copy()
            
            # Remove any rows with NaN values
            data = data.dropna()
            
            # Ensure numeric types
            for col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce')
            
            # Drop any rows that became NaN after conversion
            data = data.dropna()
            
            if data.empty:
                raise ValueError(f"No valid data found for ticker {ticker} after cleaning")
            
            self.logger.info("Successfully fetched %d rows of data for %s", len(data), ticker)
            return data
            
        except Exception as e:
            error_msg = f"Failed to fetch data for {ticker}: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)


class StockDataService:
    """
    High-level service that combines data fetching with intelligent caching.
    
    This class provides the main interface for getting stock data,
    using the DataFetcher for API calls and CacheManager for caching.
    """
    
    def __init__(self, cache_db_path: str = "ticker_data/stock_cache.db"):
        """
        Initialize the stock data service.
        
        Args:
            cache_db_path (str): Path to cache database
        """
        self.data_fetcher = DataFetcher()
        self.cache_manager = CacheManager(cache_db_path)
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("StockDataService initialized")
    
    def _calculate_date_range(self, period: str) -> Tuple[date, date]:
        """
        Calculate the actual date range for a given period.
        
        Args:
            period (str): Period string like '10y', '5y', '1y', '6mo'
            
        Returns:
            Tuple[date, date]: Start and end dates
        """
        end_date = date.today()
        
        # Parse period string
        if period.endswith('y'):
            years = int(period[:-1])
            start_date = end_date - timedelta(days=years * 365)
        elif period.endswith('mo'):
            months = int(period[:-2])
            start_date = end_date - timedelta(days=months * 30)
        elif period.endswith('d'):
            days = int(period[:-1])
            start_date = end_date - timedelta(days=days)
        else:
            raise ValueError(f"Unsupported period format: {period}")
        
        return start_date, end_date
    
    def get_stock_data(
        self, 
        ticker: str,
        period: str = "10y",
        interval: Literal['1d', '1wk', '1mo'] = '1d',
        force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Get stock data with intelligent caching based on data coverage.
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
            period (str): Time period to fetch (e.g., '10y', '5y', '2y', '1y', '6mo')
            interval (Literal['1d', '1wk', '1mo']): Data granularity
            force_refresh (bool): If True, ignore cache and fetch fresh data
            
        Returns:
            pd.DataFrame: Stock data with columns [Open, High, Low, Close, Volume (if available)]
            
        Raises:
            ValueError: If parameters are invalid
            Exception: If data fetching fails
        """
        # Validate parameters first
        ticker, period, interval = self.data_fetcher._validate_parameters(ticker, period, interval)
        
        # Calculate the actual date range we need
        start_date, end_date = self._calculate_date_range(period)
        
        self.logger.info("Requesting %s %s data from %s to %s", 
                        ticker, interval, start_date, end_date)
        
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_data = self.cache_manager.get_cached_data(ticker, interval, start_date, end_date)
            if cached_data is not None:
                self.logger.info("Returning cached data with %d rows", len(cached_data))
                return cached_data
        
        # Fetch fresh data from API
        try:
            fresh_data = self.data_fetcher.fetch_from_api(ticker, period, interval)
            
            # Cache the fresh data
            self.cache_manager.cache_data(ticker, interval, fresh_data)
            
            # Filter to exact requested range (in case API returned more data)
            filtered_data = fresh_data[
                (fresh_data.index.date >= start_date) & 
                (fresh_data.index.date <= end_date)
            ].copy()
            
            self.logger.info("Returning fresh data with %d rows", len(filtered_data))
            return filtered_data
            
        except Exception as e:
            # If fresh fetch fails, try to use any available cached data
            self.logger.warning("Fresh fetch failed: %s", str(e))
            cached_data = self.cache_manager.get_cached_data(ticker, interval, start_date, end_date)
            if cached_data is not None:
                self.logger.info("Using cached data as fallback")
                return cached_data
            
            # If all else fails, re-raise the exception
            raise e
    
    def clear_cache(self, ticker: Optional[str] = None, interval: Optional[str] = None):
        """
        Clear cached data.
        
        Args:
            ticker (Optional[str]): If provided, only clear cache for this ticker
            interval (Optional[str]): If provided, only clear cache for this interval
        """
        self.cache_manager.clear_cache(ticker, interval)
    
    def get_cache_info(self) -> dict:
        """
        Get information about cached data.
        
        Returns:
            dict: Cache information and statistics
        """
        return self.cache_manager.get_cache_info()
    
    def cleanup_old_cache(self, days_old: int = 30):
        """
        Remove cache entries older than specified days.
        
        Args:
            days_old (int): Remove entries older than this many days
        """
        self.cache_manager.cleanup_old_cache(days_old)


# Convenience function for quick usage
def get_stock_data(
    ticker: str,
    period: str = "10y", 
    interval: Literal['1d', '1wk', '1mo'] = '1d'
) -> pd.DataFrame:
    """
    Convenience function to quickly get stock data.
    
    Args:
        ticker (str): Stock ticker symbol
        period (str): Time period (default: '10y')
        interval (Literal['1d', '1wk', '1mo']): Data interval (default: '1d')
        
    Returns:
        pd.DataFrame: Stock data
    """
    service = StockDataService()
    return service.get_stock_data(ticker, period, interval)


if __name__ == "__main__":
    # Example usage
    service = StockDataService()
    
    print("Fetching Apple daily data for the last 1 year...")
    try:
        aapl_data = service.get_stock_data('AAPL', period='1y')
        print(f"Retrieved {len(aapl_data)} rows of data")
        print("Columns:", list(aapl_data.columns))
        print("\nFirst 5 rows:")
        print(aapl_data.head())
        print("\nLast 5 rows:")
        print(aapl_data.tail())
        
        print("\nCache info:")
        cache_info = service.get_cache_info()
        print(f"Total cache entries: {cache_info['total_entries']}")
        
    except Exception as e:
        print(f"Error: {e}")

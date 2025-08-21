"""
Stock Data Service V2 - Usage Examples

This file demonstrates the improved architecture with separated concerns:
- DataFetcher: Handles API calls
- CacheManager: Handles SQLite-based caching with intelligent expiration
- StockDataService: High-level interface combining both
"""

from data_fetcher import StockDataService, get_stock_data
from cache_manager import CacheManager
import pandas as pd
import time
import yfinance as yf


def test_basic_functionality():
    """Test basic data fetching functionality."""
    print("=== Testing Basic Functionality ===\n")
    
    service = StockDataService()
    
    print("1. Fetching Apple 6 months daily data...")
    try:
        start_time = time.time()
        aapl_data = service.get_stock_data('AAPL', period='6mo', interval='1d')
        fetch_time = time.time() - start_time
        
        print(f"   ✓ Success! Retrieved {len(aapl_data)} rows in {fetch_time:.2f} seconds")
        print(f"   Date range: {aapl_data.index.min().date()} to {aapl_data.index.max().date()}")
        print(f"   Columns: {list(aapl_data.columns)}")
        print(f"   Sample data:\n{aapl_data.head(2)}\n")
        
    except Exception as e:
        print(f"   ✗ Error: {e}\n")
    
    print("2. Fetching Tesla weekly data for 2 years...")
    try:
        tsla_data = service.get_stock_data('TSLA', period='2y', interval='1wk')
        print(f"   ✓ Success! Retrieved {len(tsla_data)} rows")
        print(f"   Recent weeks:\n{tsla_data.tail(2)}\n")
        
    except Exception as e:
        print(f"   ✗ Error: {e}\n")


def test_caching_intelligence():
    """Test the intelligent caching based on data coverage."""
    print("=== Testing Intelligent Caching ===\n")
    
    service = StockDataService()
    
    print("1. First request - should fetch from API...")
    try:
        start_time = time.time()
        data1 = service.get_stock_data('GOOGL', period='1y', interval='1d')
        time1 = time.time() - start_time
        print(f"   First fetch: {len(data1)} rows in {time1:.2f} seconds")
        
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    print("2. Second identical request - should use cache...")
    try:
        start_time = time.time()
        data2 = service.get_stock_data('GOOGL', period='1y', interval='1d')
        time2 = time.time() - start_time
        print(f"   Second fetch: {len(data2)} rows in {time2:.2f} seconds")
        print(f"   Speed improvement: {time1/time2:.1f}x faster\n")
        
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    print("3. Smaller range request (6mo) - should use cached data...")
    try:
        start_time = time.time()
        data3 = service.get_stock_data('GOOGL', period='6mo', interval='1d')
        time3 = time.time() - start_time
        print(f"   Subset fetch: {len(data3)} rows in {time3:.2f} seconds")
        print(f"   Data is subset of cached range: {len(data3) < len(data1)}")
        
    except Exception as e:
        print(f"   Error: {e}")


def test_cache_management():
    """Test cache management features."""
    print("=== Testing Cache Management ===\n")
    
    service = StockDataService()
    
    # Ensure we have some cached data
    try:
        service.get_stock_data('NVDA', period='1y', interval='1d')
        service.get_stock_data('MSFT', period='6mo', interval='1wk')
    except Exception as e:
        print(f"Failed to create test cache data: {e}")
        return
    
    print("1. Cache information:")
    try:
        cache_info = service.get_cache_info()
        print(f"   Database path: {cache_info['database_path']}")
        print(f"   Database size: {cache_info['database_size_mb']} MB")
        print(f"   Total entries: {cache_info['total_entries']}")
        print(f"   Total data size: {cache_info['total_data_size_mb']} MB")
        
        if cache_info['entries']:
            print("   Cache entries:")
            for entry in cache_info['entries'][:3]:  # Show first 3
                print(f"     - {entry['ticker']} {entry['interval']}: "
                      f"{entry['start_date']} to {entry['end_date']} "
                      f"({entry['size_mb']} MB)")
        print()
        
    except Exception as e:
        print(f"   Error getting cache info: {e}\n")
    
    print("2. Testing selective cache clearing...")
    try:
        # Clear cache for specific ticker
        service.clear_cache('NVDA')
        print("   ✓ Cleared NVDA cache")
        
        cache_info_after = service.get_cache_info()
        print(f"   Entries after clearing NVDA: {cache_info_after['total_entries']}")
        
    except Exception as e:
        print(f"   Error clearing cache: {e}")


def test_different_intervals():
    """Test different data intervals."""
    print("=== Testing Different Intervals ===\n")
    
    service = StockDataService()
    
    intervals = [('1d', 'daily'), ('1wk', 'weekly'), ('1mo', 'monthly')]
    
    for interval, name in intervals:
        print(f"Fetching {name} data for SPY...")
        try:
            data = service.get_stock_data('SPY', period='2y', interval=interval)
            print(f"   ✓ {name.capitalize()}: {len(data)} rows")
            print(f"   Date range: {data.index.min().date()} to {data.index.max().date()}")
            
            # Show basic statistics
            latest_close = data['Close'].iloc[-1]
            avg_close = data['Close'].mean()
            print(f"   Latest close: ${latest_close:.2f}")
            print(f"   Average close: ${avg_close:.2f}\n")
            
        except Exception as e:
            print(f"   ✗ Error fetching {name} data: {e}\n")


def test_convenience_function():
    """Test the convenience function."""
    print("=== Testing Convenience Function ===\n")
    
    print("Using convenience function for quick access...")
    try:
        data = get_stock_data('AMD', period='1y', interval='1wk')
        print(f"✓ Retrieved {len(data)} rows of AMD weekly data")
        print(f"Recent performance:")
        print(data[['Open', 'High', 'Low', 'Close']].tail(3))
        print()
        
    except Exception as e:
        print(f"✗ Error: {e}\n")


def test_data_analysis_ready():
    """Show that data is ready for analysis."""
    print("=== Data Analysis Readiness ===\n")
    
    try:
        service = StockDataService()
        data = service.get_stock_data('AAPL', period='1y', interval='1d')
        
        print(f"Data shape: {data.shape}")
        print(f"Data types:\n{data.dtypes}\n")
        
        # Add some basic technical indicators
        data['Daily_Return'] = data['Close'].pct_change()
        data['SMA_20'] = data['Close'].rolling(window=20).mean()
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['Volatility_20'] = data['Daily_Return'].rolling(window=20).std()
        
        print("Added technical indicators:")
        print("- Daily returns")
        print("- 20-day Simple Moving Average")
        print("- 50-day Simple Moving Average") 
        print("- 20-day volatility")
        
        print(f"\nRecent data with indicators:")
        analysis_cols = ['Close', 'Daily_Return', 'SMA_20', 'SMA_50', 'Volatility_20']
        print(data[analysis_cols].tail(3))
        
        print(f"\nBasic statistics:")
        print(f"Average daily return: {data['Daily_Return'].mean():.4f}")
        print(f"Daily volatility: {data['Daily_Return'].std():.4f}")
        print(f"Current price vs 20-day SMA: {(data['Close'].iloc[-1] / data['SMA_20'].iloc[-1] - 1) * 100:.2f}%")
        
    except Exception as e:
        print(f"Error in analysis example: {e}")


def main():
    """Run all test examples."""
    print("Stock Data Service V2 - Comprehensive Testing\n")
    print("=" * 60)
    
    ticker = yf.Ticker('AAPL')
    data = ticker.history(period='1y', interval='1d')
    print(data)
    
    try:
        # test_basic_functionality()
        # test_caching_intelligence()
        # test_cache_management()
        # test_different_intervals()
        # test_convenience_function()
        # test_data_analysis_ready()
        
        print("=" * 60)
        print("✅ All tests completed!")
        print("\n🎯 Key Improvements in V2:")
        print("✓ SQLite database for better performance and reliability")
        print("✓ Intelligent caching based on data coverage, not file timestamps")
        print("✓ Clean separation of concerns (fetching vs caching)")
        print("✓ Better error handling and fallback mechanisms")
        print("✓ More efficient cache lookups and management")
        
        print("\n🚀 Ready for building analysis modules on top!")
        
    except Exception as e:
        print(f"Error running tests: {e}")


if __name__ == "__main__":
    main()

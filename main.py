"""
Stock Analysis Platform - 股票分析平台主入口

这是整个股票分析平台的主入口文件，提供了数据获取和分析的完整工作流程。

Usage:
    python3 main.py --help  # 查看帮助
    python3 main.py fetch SPX  # 获取SPX数据
    python3 main.py analyze SPX  # 分析SPX收益率
    python3 main.py compare AAPL GOOGL MSFT  # 比较多个股票
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data_fetching import StockDataService
from data_analysis import ReturnsAnalyzer


def fetch_data(ticker: str, period: str = '10y', interval: str = '1d'):
    """获取股票数据"""
    print(f"🚀 开始获取 {ticker} 数据...")
    
    try:
        service = StockDataService()
        
        # 转换ticker格式
        if ticker.upper() == 'SPX':
            ticker = '^GSPC'
        
        data = service.get_stock_data(ticker, period=period, interval=interval)
        
        if data is not None:
            print(f"✅ 成功获取 {ticker} 数据：{len(data)} 条记录")
            print(f"   日期范围: {data.index.min().date()} 到 {data.index.max().date()}")
            return True
        else:
            print(f"❌ 获取 {ticker} 数据失败")
            return False
            
    except Exception as e:
        print(f"❌ 获取数据时出错: {e}")
        return False


def analyze_returns(ticker: str):
    """分析单个股票的收益率"""
    print(f"📊 开始分析 {ticker} 收益率...")
    
    try:
        analyzer = ReturnsAnalyzer()
        
        # 转换ticker格式
        if ticker.upper() == 'SPX':
            ticker = '^GSPC'
        
        # 分析日收益率
        daily_results = analyzer.analyze_daily_returns(ticker, create_plots=True)
        
        if daily_results:
            print(f"✅ {ticker} 日收益率分析完成")
            
            # 如果有周数据，也分析周收益率
            try:
                weekly_results = analyzer.analyze_weekly_returns(ticker, create_plots=True)
                if weekly_results:
                    print(f"✅ {ticker} 周收益率分析完成")
            except Exception as e:
                print(f"⚠️  周收益率分析失败（可能没有周数据）: {e}")
            
            return True
        else:
            print(f"❌ {ticker} 分析失败（可能没有数据）")
            return False
            
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        return False


def analyze_intraday_returns(ticker: str):
    """分析单个股票的日内涨跌幅（开盘到收盘）"""
    print(f"📊 开始分析 {ticker} 日内涨跌幅...")
    print(f"   分类方式: 高开(>0) | 低开(<0) | 平开(=0)")
    
    try:
        analyzer = ReturnsAnalyzer()
        
        # 转换ticker格式
        if ticker.upper() == 'SPX':
            ticker = '^GSPC'
        
        # 分析日内收益率
        intraday_results = analyzer.analyze_intraday_returns(ticker, create_plots=True)
        
        if intraday_results:
            print(f"✅ {ticker} 日内涨跌幅分析完成")
            return True
        else:
            print(f"❌ {ticker} 日内分析失败（可能没有数据）")
            return False
            
    except Exception as e:
        print(f"❌ 日内分析过程中出错: {e}")
        return False


def compare_stocks(tickers: list):
    """比较多个股票的收益率"""
    print(f"📈 开始比较股票收益率: {', '.join(tickers)}")
    
    try:
        analyzer = ReturnsAnalyzer()
        
        # 转换ticker格式
        converted_tickers = []
        for ticker in tickers:
            if ticker.upper() == 'SPX':
                converted_tickers.append('^GSPC')
            else:
                converted_tickers.append(ticker)
        
        results = analyzer.compare_returns(converted_tickers, create_plots=True)
        
        if results:
            print(f"✅ 股票对比分析完成")
            return True
        else:
            print(f"❌ 对比分析失败")
            return False
            
    except Exception as e:
        print(f"❌ 对比分析过程中出错: {e}")
        return False


def show_available_data():
    """显示数据库中可用的数据"""
    try:
        analyzer = ReturnsAnalyzer()
        analyzer.get_available_data()
    except Exception as e:
        print(f"❌ 查看可用数据时出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Stock Analysis Platform - 股票分析平台',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python3 main.py fetch SPX           # 获取SPX 10年数据
  python3 main.py fetch AAPL --period 5y  # 获取AAPL 5年数据
  python3 main.py analyze SPX         # 分析SPX收益率
  python3 main.py intraday SPX        # 分析SPX日内涨跌幅（高开/低开/平开）
  python3 main.py compare AAPL GOOGL MSFT  # 比较多个股票
  python3 main.py list               # 查看可用数据
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # fetch命令
    fetch_parser = subparsers.add_parser('fetch', help='获取股票数据')
    fetch_parser.add_argument('ticker', help='股票代码 (如: AAPL, SPX)')
    fetch_parser.add_argument('--period', default='10y', 
                             help='数据期间 (默认: 10y)')
    fetch_parser.add_argument('--interval', default='1d', 
                             help='数据间隔 (默认: 1d)')
    
    # analyze命令
    analyze_parser = subparsers.add_parser('analyze', help='分析股票收益率')
    analyze_parser.add_argument('ticker', help='股票代码 (如: AAPL, SPX)')
    
    # intraday命令
    intraday_parser = subparsers.add_parser('intraday', help='分析股票日内涨跌幅（开盘到收盘）')
    intraday_parser.add_argument('ticker', help='股票代码 (如: AAPL, SPX)')
    
    # compare命令
    compare_parser = subparsers.add_parser('compare', help='比较多个股票')
    compare_parser.add_argument('tickers', nargs='+', 
                               help='股票代码列表 (如: AAPL GOOGL MSFT)')
    
    # list命令
    list_parser = subparsers.add_parser('list', help='查看可用数据')
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    print("=" * 60)
    print("🏢 Stock Analysis Platform v2.0")
    print("=" * 60)
    
    if args.command == 'fetch':
        success = fetch_data(args.ticker, args.period, args.interval)
        if success:
            print(f"\n💡 提示: 现在可以运行分析命令:")
            print(f"   python3 main.py analyze {args.ticker}")
    
    elif args.command == 'analyze':
        success = analyze_returns(args.ticker)
        if not success:
            print(f"\n💡 提示: 可能需要先获取数据:")
            print(f"   python3 main.py fetch {args.ticker}")
    
    elif args.command == 'intraday':
        success = analyze_intraday_returns(args.ticker)
        if not success:
            print(f"\n💡 提示: 可能需要先获取数据:")
            print(f"   python3 main.py fetch {args.ticker}")
    
    elif args.command == 'compare':
        success = compare_stocks(args.tickers)
        if not success:
            print(f"\n💡 提示: 可能需要先获取数据:")
            for ticker in args.tickers:
                print(f"   python3 main.py fetch {ticker}")
    
    elif args.command == 'list':
        show_available_data()
    
    print("\n" + "=" * 60)
    print("✅ 操作完成")


if __name__ == "__main__":
    main()

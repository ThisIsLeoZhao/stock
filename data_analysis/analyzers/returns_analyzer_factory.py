"""
Returns Analyzer Factory - 收益率分析器工厂

使用工厂模式统一管理各种分析器，提供简洁的接口
"""

from typing import Dict, List, Optional
from .daily_returns_analyzer import DailyReturnsAnalyzer
from .intraday_returns_analyzer import IntradayReturnsAnalyzer
from .weekly_returns_analyzer import WeeklyReturnsAnalyzer
from .comparison_analyzer import ComparisonAnalyzer
from .daily_range_analyzer import DailyRangeAnalyzer
from ..modules.data_provider import DataProvider


class ReturnsAnalyzer:
    """收益率分析器工厂 - 统一管理各种分析器"""
    
    def __init__(self, db_path: str = "ticker_data/stock_cache.db"):
        """
        初始化分析器工厂
        
        Args:
            db_path: SQLite数据库路径
        """
        self.db_path = db_path
        self.data_provider = DataProvider(db_path)
        
        # 初始化各种分析器
        self._daily_analyzer = None
        self._intraday_analyzer = None
        self._weekly_analyzer = None
        self._comparison_analyzer = None
        self._daily_range_analyzer = None
    
    @property
    def daily_analyzer(self) -> DailyReturnsAnalyzer:
        """懒加载每日收益率分析器"""
        if self._daily_analyzer is None:
            self._daily_analyzer = DailyReturnsAnalyzer(self.db_path)
        return self._daily_analyzer
    
    @property
    def intraday_analyzer(self) -> IntradayReturnsAnalyzer:
        """懒加载日内收益率分析器"""
        if self._intraday_analyzer is None:
            self._intraday_analyzer = IntradayReturnsAnalyzer(self.db_path)
        return self._intraday_analyzer
    
    @property
    def weekly_analyzer(self) -> WeeklyReturnsAnalyzer:
        """懒加载周收益率分析器"""
        if self._weekly_analyzer is None:
            self._weekly_analyzer = WeeklyReturnsAnalyzer(self.db_path)
        return self._weekly_analyzer
    
    @property
    def comparison_analyzer(self) -> ComparisonAnalyzer:
        """懒加载对比分析器"""
        if self._comparison_analyzer is None:
            self._comparison_analyzer = ComparisonAnalyzer(self.db_path)
        return self._comparison_analyzer
    
    @property
    def daily_range_analyzer(self) -> DailyRangeAnalyzer:
        """懒加载日内波动范围分析器"""
        if self._daily_range_analyzer is None:
            self._daily_range_analyzer = DailyRangeAnalyzer(self.db_path)
        return self._daily_range_analyzer
    
    # 保持向后兼容的方法
    def analyze_daily_returns(self, ticker: str, create_plots: bool = True) -> Dict:
        """
        分析股票的每日涨跌幅度分布
        
        Args:
            ticker: 股票代码
            create_plots: 是否创建可视化图表
            
        Returns:
            分析结果字典
        """
        return self.daily_analyzer.analyze(ticker, create_plots)
    
    def analyze_intraday_returns(self, ticker: str, create_plots: bool = True) -> Dict:
        """
        分析股票的日内涨跌幅度分布（开盘到收盘）
        
        Args:
            ticker: 股票代码
            create_plots: 是否创建可视化图表
            
        Returns:
            分析结果字典
        """
        return self.intraday_analyzer.analyze(ticker, create_plots)
    
    def analyze_weekly_returns(self, ticker: str, create_plots: bool = True) -> Dict:
        """
        分析股票的周收益率分布
        
        Args:
            ticker: 股票代码
            create_plots: 是否创建可视化图表
            
        Returns:
            分析结果字典
        """
        return self.weekly_analyzer.analyze(ticker, create_plots)
    
    def compare_returns(self, tickers: List[str], create_plots: bool = True) -> Dict:
        """
        比较多个股票的收益率特征
        
        Args:
            tickers: 股票代码列表
            create_plots: 是否创建对比图表
            
        Returns:
            对比分析结果
        """
        return self.comparison_analyzer.analyze(tickers, create_plots)
    
    def analyze_daily_range(self, ticker: str, create_plots: bool = True) -> Dict:
        """
        分析股票的日内波动范围（双起点：昨收&今开）
        
        Args:
            ticker: 股票代码
            create_plots: 是否创建可视化图表
            
        Returns:
            分析结果字典
        """
        return self.daily_range_analyzer.analyze(ticker, create_plots)
    
    def get_available_data(self) -> List[Dict]:
        """获取数据库中可用的数据列表"""
        return self.data_provider.get_available_data()
    
    def get_available_analyzers(self) -> Dict[str, str]:
        """获取可用的分析器列表"""
        return {
            'daily': '每日收益率分析',
            'intraday': '日内收益率分析（开盘到收盘）',
            'weekly': '周收益率分析',
            'comparison': '多股票对比分析',
            'daily_range': '日内波动范围分析（双起点：昨收&今开）'
        }
    
    def run_analysis(self, analysis_type: str, ticker: Optional[str] = None, 
                    tickers: Optional[List[str]] = None, create_plots: bool = True) -> Dict:
        """
        统一的分析接口
        
        Args:
            analysis_type: 分析类型 ('daily', 'intraday', 'weekly', 'comparison')
            ticker: 单个股票代码（用于单股票分析）
            tickers: 股票代码列表（用于对比分析）
            create_plots: 是否创建可视化图表
            
        Returns:
            分析结果字典
        """
        if analysis_type == 'daily':
            if not ticker:
                raise ValueError("每日分析需要提供ticker参数")
            return self.analyze_daily_returns(ticker, create_plots)
        
        elif analysis_type == 'intraday':
            if not ticker:
                raise ValueError("日内分析需要提供ticker参数")
            return self.analyze_intraday_returns(ticker, create_plots)
        
        elif analysis_type == 'weekly':
            if not ticker:
                raise ValueError("周分析需要提供ticker参数")
            return self.analyze_weekly_returns(ticker, create_plots)
        
        elif analysis_type == 'comparison':
            if not tickers or len(tickers) < 2:
                raise ValueError("对比分析需要提供至少2个ticker")
            return self.compare_returns(tickers, create_plots)
        
        elif analysis_type == 'daily_range':
            if not ticker:
                raise ValueError("日内波动范围分析需要提供ticker参数")
            return self.analyze_daily_range(ticker, create_plots)
        
        else:
            available = list(self.get_available_analyzers().keys())
            raise ValueError(f"不支持的分析类型: {analysis_type}。可用类型: {available}")

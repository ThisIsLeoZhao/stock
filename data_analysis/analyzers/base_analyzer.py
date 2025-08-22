"""
Base Analyzer - 基础分析器抽象类

定义了所有分析器的通用接口和共同功能
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
from ..modules.data_provider import DataProvider
from ..modules.statistics_calculator import StatisticsCalculator
from ..modules.file_manager import FileManager
from ..visualizers.returns_visualizer import ReturnsVisualizer


class BaseAnalyzer(ABC):
    """基础分析器抽象类 - 定义所有分析器的通用接口"""
    
    def __init__(self, db_path: str = "ticker_data/stock_cache.db"):
        """
        初始化基础分析器
        
        Args:
            db_path: SQLite数据库路径
        """
        self.data_provider = DataProvider(db_path)
        self.stats_calculator = StatisticsCalculator()
        self.file_manager = FileManager()
        self.visualizer = ReturnsVisualizer()
    
    @abstractmethod
    def analyze(self, ticker: str, create_plots: bool = True, **kwargs) -> Dict:
        """
        执行分析的抽象方法
        
        Args:
            ticker: 股票代码
            create_plots: 是否创建可视化图表
            **kwargs: 其他分析参数
            
        Returns:
            分析结果字典
        """
        pass
    
    @abstractmethod
    def get_analysis_name(self) -> str:
        """返回分析类型名称"""
        pass
    
    def _convert_ticker(self, ticker: str) -> str:
        """统一的ticker格式转换"""
        if ticker.upper() == 'SPX':
            return '^GSPC'
        return ticker
    
    def _print_analysis_header(self, ticker: str, analysis_name: str):
        """打印分析标题"""
        print(f"\n=== 分析 {ticker} {analysis_name} ===")
    
    def _save_results(self, stats: Dict, ticker: str, suffix: str):
        """保存分析结果"""
        filename = f'{ticker}_{suffix}'
        self.file_manager.save_analysis_results(stats, filename)
        return filename

"""
Weekly Returns Analyzer - 周收益率分析器

专门负责分析股票的周收益率分布
"""

from typing import Dict
from .base_analyzer import BaseAnalyzer


class WeeklyReturnsAnalyzer(BaseAnalyzer):
    """周收益率分析器 - 分析股票的周收益率分布"""
    
    def get_analysis_name(self) -> str:
        """返回分析类型名称"""
        return "周收益率分布"
    
    def analyze(self, ticker: str, create_plots: bool = True, **kwargs) -> Dict:
        """
        分析股票的周收益率分布
        
        Args:
            ticker: 股票代码
            create_plots: 是否创建可视化图表
            
        Returns:
            分析结果字典
        """
        # 转换ticker格式并打印标题
        original_ticker = ticker
        ticker = self._convert_ticker(ticker)
        self._print_analysis_header(original_ticker, self.get_analysis_name())
        
        # 从数据库获取数据
        data = self.data_provider.get_stock_data_from_db(ticker, '1wk')
        if data is None:
            print(f"❌ 无法获取 {ticker} 的周数据")
            return {}
        
        # 计算周收益率
        weekly_returns = self.stats_calculator.calculate_returns(data, 'Close')
        
        # 计算统计指标
        stats = self.stats_calculator.calculate_basic_stats(weekly_returns)
        
        # 添加周收益率特定的统计
        stats.update({
            'analysis_type': 'weekly_returns',
            'description': '周收益率分析',
            'positive_weeks': (weekly_returns > 0).sum(),
            'negative_weeks': (weekly_returns < 0).sum(),
            'flat_weeks': (weekly_returns == 0).sum(),
            'positive_ratio': (weekly_returns > 0).sum() / len(weekly_returns),
            'ticker': ticker,
            'original_ticker': original_ticker
        })
        
        # 打印统计结果
        self._print_return_statistics(original_ticker, stats, period='Weekly')
        
        # 创建图表
        if create_plots:
            filename = self.visualizer.create_returns_analysis_plot(
                f'{ticker}_Weekly', weekly_returns, stats)
            stats['chart_filename'] = filename
        
        # 保存结果
        self._save_results(stats, ticker, 'weekly_returns_analysis')
        
        return stats
    
    def _print_return_statistics(self, ticker: str, stats: Dict, period: str = 'Weekly'):
        """打印周收益率统计信息"""
        print(f"\n📊 {ticker} {period} 收益率统计：")
        print(f"   总{period.lower()}数: {stats['count']}")
        print(f"   平均收益率: {stats['mean']:.3f}%")
        print(f"   中位数收益率: {stats['median']:.3f}%")
        print(f"   标准差: {stats['std']:.3f}%")
        print(f"   最大收益: {stats['max']:.3f}%")
        print(f"   最小收益: {stats['min']:.3f}%")
        
        print(f"\n📈 收益分布：")
        if 'positive_weeks' in stats:
            print(f"   上涨周数: {stats['positive_weeks']} ({stats['positive_ratio']*100:.1f}%)")
            print(f"   下跌周数: {stats['negative_weeks']}")
            print(f"   平盘周数: {stats['flat_weeks']}")
        
        print(f"\n📊 整体百分位数分析：")
        for p, value in stats['percentiles'].items():
            print(f"   {p:2d}% percentile: {value:6.3f}%")
        
        # 打印上涨周数的分位数
        if 'positive_percentiles' in stats and stats['positive_percentiles']:
            print(f"\n📈 上涨周数分位数分析（共{stats.get('positive_weeks', 0)}周）：")
            for p, value in stats['positive_percentiles'].items():
                print(f"   {p:2d}% percentile: {value:6.3f}%")
        
        # 打印下跌周数的分位数
        if 'negative_percentiles' in stats and stats['negative_percentiles']:
            print(f"\n📉 下跌周数分位数分析（共{stats.get('negative_weeks', 0)}周）：")
            for p, value in stats['negative_percentiles'].items():
                print(f"   {p:2d}% percentile: {value:6.3f}%")

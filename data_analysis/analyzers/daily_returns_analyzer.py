"""
Daily Returns Analyzer - 每日收益率分析器

专门负责分析股票的每日涨跌幅度分布
"""

from typing import Dict
from .base_analyzer import BaseAnalyzer


class DailyReturnsAnalyzer(BaseAnalyzer):
    """每日收益率分析器 - 分析股票的每日涨跌幅度分布"""
    
    def get_analysis_name(self) -> str:
        """返回分析类型名称"""
        return "每日涨跌幅度分布"
    
    def analyze(self, ticker: str, create_plots: bool = True, **kwargs) -> Dict:
        """
        分析股票的每日涨跌幅度分布
        
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
        data = self.data_provider.get_stock_data_from_db(ticker, '1d')
        if data is None:
            print(f"❌ 无法获取 {ticker} 的数据")
            return {}
        
        # 计算每日收益率
        daily_returns = self.stats_calculator.calculate_returns(data, 'Close')
        
        # 计算基础统计指标
        stats = self.stats_calculator.calculate_basic_stats(daily_returns)
        
        # 添加收益率特定的统计
        return_metrics = self.stats_calculator.calculate_return_metrics(daily_returns)
        stats.update(return_metrics)
        
        # 添加分析元信息
        stats.update({
            'analysis_type': 'daily_returns',
            'description': '每日涨跌幅分析（收盘价相对前一日收盘价）',
            'ticker': ticker,
            'original_ticker': original_ticker
        })
        
        # 打印统计结果
        self._print_return_statistics(original_ticker, stats, period='Daily')
        
        # 创建图表
        if create_plots:
            filename = self.visualizer.create_returns_analysis_plot(ticker, daily_returns, stats)
            stats['chart_filename'] = filename
        
        # 保存结果
        self._save_results(stats, ticker, 'daily_returns_analysis')
        
        return stats
    
    def _print_return_statistics(self, ticker: str, stats: Dict, period: str = 'Daily'):
        """打印收益率统计信息"""
        print(f"\n📊 {ticker} {period} 收益率统计：")
        print(f"   总{period.lower()}数: {stats['count']}")
        print(f"   平均收益率: {stats['mean']:.3f}%")
        print(f"   中位数收益率: {stats['median']:.3f}%")
        print(f"   标准差: {stats['std']:.3f}%")
        print(f"   最大收益: {stats['max']:.3f}%")
        print(f"   最小收益: {stats['min']:.3f}%")
        
        if 'volatility_annual' in stats:
            print(f"   年化波动率: {stats['volatility_annual']:.3f}%")
        if 'sharpe_ratio' in stats:
            print(f"   夏普比率: {stats['sharpe_ratio']:.3f}")
        
        print(f"\n📈 收益分布：")
        if 'positive_days' in stats:
            print(f"   上涨天数: {stats['positive_days']} ({stats['positive_ratio']*100:.1f}%)")
            print(f"   下跌天数: {stats['negative_days']} ({(1-stats['positive_ratio']-stats['flat_days']/stats['count'])*100:.1f}%)")
            print(f"   平盘天数: {stats['flat_days']}")
        
        print(f"\n📊 整体百分位数分析：")
        for p, value in stats['percentiles'].items():
            print(f"   {p:2d}% percentile: {value:6.3f}%")
        
        # 打印上涨天数的分位数
        if 'positive_percentiles' in stats and stats['positive_percentiles']:
            print(f"\n📈 上涨天数分位数分析（共{stats.get('positive_days', 0)}天）：")
            for p, value in stats['positive_percentiles'].items():
                print(f"   {p:2d}% percentile: {value:6.3f}%")
        
        # 打印下跌天数的分位数
        if 'negative_percentiles' in stats and stats['negative_percentiles']:
            print(f"\n📉 下跌天数分位数分析（共{stats.get('negative_days', 0)}天）：")
            for p, value in stats['negative_percentiles'].items():
                print(f"   {p:2d}% percentile: {value:6.3f}%")

"""
Intraday Returns Analyzer - 日内收益率分析器

专门负责分析股票的日内涨跌幅度分布（开盘到收盘）
包含按开盘缺口分组的详细分析
"""

from typing import Dict
from .base_analyzer import BaseAnalyzer


class IntradayReturnsAnalyzer(BaseAnalyzer):
    """日内收益率分析器 - 分析股票的日内涨跌幅度分布（开盘到收盘）"""
    
    def get_analysis_name(self) -> str:
        """返回分析类型名称"""
        return "日内涨跌幅度分布（开盘到收盘）"
    
    def analyze(self, ticker: str, create_plots: bool = True, **kwargs) -> Dict:
        """
        分析股票的日内涨跌幅度分布（开盘到收盘）
        
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
        print(f"   分类方式: 高开(>0) | 低开(<0) | 平开(=0)")
        
        # 从数据库获取数据
        data = self.data_provider.get_stock_data_from_db(ticker, '1d')
        if data is None:
            print(f"❌ 无法获取 {ticker} 的数据")
            return {}
        
        # 计算日内收益率（开盘到收盘）
        intraday_returns = self.stats_calculator.calculate_intraday_returns(data)
        
        # 计算开盘缺口信息
        gaps = self.stats_calculator.calculate_gap_info(data)
        
        # 计算基础统计指标
        stats = self.stats_calculator.calculate_basic_stats(intraday_returns)
        
        # 添加日内收益率特定的统计
        intraday_metrics = self.stats_calculator.calculate_return_metrics(intraday_returns)
        stats.update(intraday_metrics)
        
        # 计算按开盘缺口分组的统计
        gap_grouped_stats = self.stats_calculator.calculate_gap_grouped_stats(intraday_returns, gaps)
        
        # 添加日内特有的统计信息
        stats.update({
            'analysis_type': 'intraday_returns',
            'description': '日内涨跌幅分析（开盘到收盘）',
            'total_trading_days': len(intraday_returns),
            'positive_intraday_days': (intraday_returns > 0).sum(),
            'negative_intraday_days': (intraday_returns < 0).sum(),
            'flat_intraday_days': (intraday_returns == 0).sum(),
            'positive_intraday_ratio': (intraday_returns > 0).sum() / len(intraday_returns),
            'gap_analysis': gap_grouped_stats,  # 添加缺口分组分析结果
            'ticker': ticker,
            'original_ticker': original_ticker
        })
        
        # 打印统计结果
        self._print_intraday_statistics(original_ticker, stats)
        
        # 创建图表
        if create_plots:
            filename = self.visualizer.create_returns_analysis_plot(
                f'{ticker}_Intraday', intraday_returns, stats)
            stats['chart_filename'] = filename
        
        # 保存结果
        self._save_results(stats, ticker, 'intraday_returns_analysis')
        
        return stats
    
    def _print_intraday_statistics(self, ticker: str, stats: Dict):
        """打印日内收益率统计信息"""
        print(f"\n📊 {ticker} 日内收益率统计（开盘到收盘）：")
        print(f"   总交易天数: {stats['total_trading_days']}")
        print(f"   平均日内收益率: {stats['mean']:.3f}%")
        print(f"   中位数日内收益率: {stats['median']:.3f}%")
        print(f"   标准差: {stats['std']:.3f}%")
        print(f"   最大日内收益: {stats['max']:.3f}%")
        print(f"   最小日内收益: {stats['min']:.3f}%")
        
        if 'volatility_annual' in stats:
            print(f"   年化波动率: {stats['volatility_annual']:.3f}%")
        if 'sharpe_ratio' in stats:
            print(f"   夏普比率: {stats['sharpe_ratio']:.3f}")
        
        print(f"\n📈 日内收益分布：")
        print(f"   日内上涨天数: {stats['positive_intraday_days']} ({stats['positive_intraday_ratio']*100:.1f}%)")
        print(f"   日内下跌天数: {stats['negative_intraday_days']} ({(stats['negative_intraday_days']/stats['total_trading_days'])*100:.1f}%)")
        print(f"   日内平盘天数: {stats['flat_intraday_days']}")
        
        print(f"\n📊 整体日内涨跌幅百分位数分析：")
        for p, value in stats['percentiles'].items():
            print(f"   {p:2d}% percentile: {value:6.3f}%")
        
        # 打印日内上涨天数的分位数
        if 'positive_percentiles' in stats and stats['positive_percentiles']:
            print(f"\n📈 日内上涨天数分位数分析（共{stats.get('positive_intraday_days', 0)}天）：")
            for p, value in stats['positive_percentiles'].items():
                print(f"   {p:2d}% percentile: {value:6.3f}%")
        
        # 打印日内下跌天数的分位数
        if 'negative_percentiles' in stats and stats['negative_percentiles']:
            print(f"\n📉 日内下跌天数分位数分析（共{stats.get('negative_intraday_days', 0)}天）：")
            for p, value in stats['negative_percentiles'].items():
                print(f"   {p:2d}% percentile: {value:6.3f}%")
        
        # 打印开盘缺口分组分析
        if 'gap_analysis' in stats and stats['gap_analysis']:
            self._print_gap_analysis(stats['gap_analysis'])
    
    def _print_gap_analysis(self, gap_analysis: Dict):
        """打印开盘缺口分组分析结果"""
        print(f"\n🔍 按开盘缺口类型分组的日内表现分析：")
        
        if 'summary' in gap_analysis:
            summary = gap_analysis['summary']
            print(f"   分类方式: {summary.get('classification', '简单分类')}")
            print(f"   总有效交易天数: {summary['total_days']}")
            print(f"   高开天数: {summary['gap_up_days']} ({summary['gap_up_ratio']*100:.1f}%)")
            print(f"   低开天数: {summary['gap_down_days']} ({summary['gap_down_ratio']*100:.1f}%)")
            print(f"   平开天数: {summary['gap_flat_days']} ({summary['gap_flat_ratio']*100:.1f}%)")
        
        # 打印高开统计
        if 'gap_up' in gap_analysis:
            gap_up = gap_analysis['gap_up']
            print(f"\n📈 高开日内表现统计（共{gap_up['count']}天）：")
            self._print_gap_group_stats(gap_up['stats'])
        
        # 打印低开统计
        if 'gap_down' in gap_analysis:
            gap_down = gap_analysis['gap_down']
            print(f"\n📉 低开日内表现统计（共{gap_down['count']}天）：")
            self._print_gap_group_stats(gap_down['stats'])
        
        # 打印平开统计
        if 'gap_flat' in gap_analysis:
            gap_flat = gap_analysis['gap_flat']
            print(f"\n➡️ 平开日内表现统计（共{gap_flat['count']}天）：")
            self._print_gap_group_stats(gap_flat['stats'])
    
    def _print_gap_group_stats(self, stats: Dict):
        """打印单个缺口分组的统计信息"""
        print(f"     平均日内收益: {stats['mean']:.3f}%")
        print(f"     中位数: {stats['median']:.3f}%")
        print(f"     标准差: {stats['std']:.3f}%")
        print(f"     最大收益: {stats['max']:.3f}%")
        print(f"     最小收益: {stats['min']:.3f}%")
        
        # 显示关键百分位数
        key_percentiles = [10, 25, 50, 75, 90]
        print(f"     关键百分位数:")
        for p in key_percentiles:
            if p in stats.get('percentiles', {}):
                print(f"       {p:2d}%: {stats['percentiles'][p]:6.3f}%")

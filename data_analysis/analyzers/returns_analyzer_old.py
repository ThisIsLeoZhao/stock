"""
Returns Analyzer - 收益率分析器

专门用于分析股票收益率的各种统计特征，使用组合模式
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from ..modules.data_provider import DataProvider
from ..modules.statistics_calculator import StatisticsCalculator
from ..modules.file_manager import FileManager
from ..visualizers.returns_visualizer import ReturnsVisualizer


class ReturnsAnalyzer:
    """收益率分析器 - 使用组合模式，聚合各个功能模块"""
    
    def __init__(self, db_path: str = "ticker_data/stock_cache.db"):
        """
        初始化收益率分析器
        
        Args:
            db_path: SQLite数据库路径
        """
        self.data_provider = DataProvider(db_path)
        self.stats_calculator = StatisticsCalculator()
        self.file_manager = FileManager()
        self.visualizer = ReturnsVisualizer()
    
    def analyze_daily_returns(self, ticker: str, create_plots: bool = True) -> Dict:
        """
        分析股票的每日涨跌幅度分布
        
        Args:
            ticker: 股票代码
            create_plots: 是否创建可视化图表
            
        Returns:
            分析结果字典
        """
        print(f"\n=== 分析 {ticker} 每日涨跌幅度分布 ===")
        
        # 从数据库获取数据
        data = self.data_provider.get_stock_data_from_db(ticker, '1d')
        if data is None:
            return {}
        
        # 计算每日收益率
        daily_returns = self.stats_calculator.calculate_returns(data, 'Close')
        
        # 计算基础统计指标
        stats = self.stats_calculator.calculate_basic_stats(daily_returns)
        
        # 添加收益率特定的统计
        return_metrics = self.stats_calculator.calculate_return_metrics(daily_returns)
        stats.update(return_metrics)
        
        # 打印统计结果
        self._print_return_statistics(ticker, stats)
        
        # 创建图表
        if create_plots:
            filename = self.visualizer.create_returns_analysis_plot(ticker, daily_returns, stats)
            stats['chart_filename'] = filename
        
        # 保存结果
        self.file_manager.save_analysis_results(stats, f'{ticker}_returns_analysis')
        
        return stats
    
    def analyze_intraday_returns(self, ticker: str, create_plots: bool = True) -> Dict:
        """
        分析股票的日内涨跌幅度分布（开盘到收盘）
        
        Args:
            ticker: 股票代码
            create_plots: 是否创建可视化图表
            
        Returns:
            分析结果字典
        """
        print(f"\n=== 分析 {ticker} 日内涨跌幅度分布（开盘到收盘） ===")
        
        # 从数据库获取数据
        data = self.data_provider.get_stock_data_from_db(ticker, '1d')
        if data is None:
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
            'analysis_type': 'intraday',
            'description': '日内涨跌幅分析（开盘到收盘）',
            'total_trading_days': len(intraday_returns),
            'positive_intraday_days': (intraday_returns > 0).sum(),
            'negative_intraday_days': (intraday_returns < 0).sum(),
            'flat_intraday_days': (intraday_returns == 0).sum(),
            'positive_intraday_ratio': (intraday_returns > 0).sum() / len(intraday_returns),
            'gap_analysis': gap_grouped_stats  # 添加缺口分组分析结果
        })
        
        # 打印统计结果
        self._print_intraday_statistics(ticker, stats)
        
        # 创建图表
        if create_plots:
            filename = self.visualizer.create_returns_analysis_plot(
                f'{ticker}_Intraday', intraday_returns, stats)
            stats['chart_filename'] = filename
        
        # 保存结果
        self.file_manager.save_analysis_results(stats, f'{ticker}_intraday_returns_analysis')
        
        return stats
    
    def analyze_weekly_returns(self, ticker: str, create_plots: bool = True) -> Dict:
        """
        分析股票的周收益率分布
        
        Args:
            ticker: 股票代码
            create_plots: 是否创建可视化图表
            
        Returns:
            分析结果字典
        """
        print(f"\n=== 分析 {ticker} 周收益率分布 ===")
        
        # 从数据库获取数据
        data = self.data_provider.get_stock_data_from_db(ticker, '1wk')
        if data is None:
            return {}
        
        # 计算周收益率
        weekly_returns = self.stats_calculator.calculate_returns(data, 'Close')
        
        # 计算统计指标
        stats = self.stats_calculator.calculate_basic_stats(weekly_returns)
        
        # 添加周收益率特定的统计
        stats.update({
            'positive_weeks': (weekly_returns > 0).sum(),
            'negative_weeks': (weekly_returns < 0).sum(),
            'flat_weeks': (weekly_returns == 0).sum(),
            'positive_ratio': (weekly_returns > 0).sum() / len(weekly_returns),
        })
        
        # 打印统计结果
        self._print_return_statistics(ticker, stats, period='Weekly')
        
        # 创建图表
        if create_plots:
            filename = self.visualizer.create_returns_analysis_plot(
                f'{ticker}_Weekly', weekly_returns, stats)
            stats['chart_filename'] = filename
        
        return stats
    
    def compare_returns(self, tickers: List[str], create_plots: bool = True) -> Dict:
        """
        比较多个股票的收益率特征
        
        Args:
            tickers: 股票代码列表
            create_plots: 是否创建对比图表
            
        Returns:
            对比分析结果
        """
        print(f"\n=== 比较收益率分析: {', '.join(tickers)} ===")
        
        returns_data = {}
        comparison_stats = {}
        
        # 获取所有股票的收益率数据
        for ticker in tickers:
            data = self.data_provider.get_stock_data_from_db(ticker, '1d')
            if data is not None:
                returns = self.stats_calculator.calculate_returns(data, 'Close')
                returns_data[ticker] = returns
                comparison_stats[ticker] = self.stats_calculator.calculate_basic_stats(returns)
        
        if not returns_data:
            print("❌ 没有找到任何股票数据")
            return {}
        
        # 创建对比图表
        if create_plots and len(returns_data) > 1:
            filename = self.visualizer.create_comparison_plot(returns_data)
            comparison_stats['comparison_chart'] = filename
        
        # 计算相关性矩阵
        if len(returns_data) > 1:
            corr_df = self.stats_calculator.calculate_correlation_matrix(returns_data)
            comparison_stats['correlation_matrix'] = corr_df.to_dict()
        
        # 打印对比结果
        self._print_comparison_results(comparison_stats, list(returns_data.keys()))
        
        return comparison_stats
    
    def get_available_data(self) -> List[Dict]:
        """获取数据库中可用的数据列表"""
        return self.data_provider.get_available_data()
    
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
        
        # 显示正负比例
        positive_count = sum(1 for p, v in stats.get('percentiles', {}).items() if v > 0)
        total_percentiles = len(stats.get('percentiles', {}))
        if total_percentiles > 0:
            print(f"     日内上涨比例: {(stats.get('percentiles', {}).get(50, 0) > 0)}（基于中位数）")
    
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
        elif 'positive_weeks' in stats:
            print(f"   上涨周数: {stats['positive_weeks']} ({stats['positive_ratio']*100:.1f}%)")
            print(f"   下跌周数: {stats['negative_weeks']}")
            print(f"   平盘周数: {stats['flat_weeks']}")
        
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
    
    def _print_comparison_results(self, comparison_stats: Dict, tickers: List[str]):
        """打印对比分析结果"""
        print(f"\n📊 收益率对比分析结果：")
        
        # 创建对比表格
        comparison_df = pd.DataFrame({
            ticker: {
                'Mean': stats['mean'],
                'Std': stats['std'],
                'Min': stats['min'],
                'Max': stats['max'],
                'Skewness': stats['skewness'],
                'Kurtosis': stats['kurtosis']
            }
            for ticker, stats in comparison_stats.items()
            if ticker in tickers  # 排除非ticker的键
        }).T
        
        print(comparison_df.round(4))
        
        # 打印相关性信息
        if 'correlation_matrix' in comparison_stats:
            print(f"\n📈 收益率相关性矩阵：")
            corr_df = pd.DataFrame(comparison_stats['correlation_matrix'])
            print(corr_df.round(4))

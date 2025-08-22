"""
Daily Range Analyzer - 日内波动范围分析器

专门负责分析股票的日内波动范围
计算从昨日收盘价到今日高点的最大涨幅和到今日低点的最大跌幅
"""

from typing import Dict
from .base_analyzer import BaseAnalyzer


class DailyRangeAnalyzer(BaseAnalyzer):
    """日内波动范围分析器 - 分析股票的日内最大涨跌幅范围"""
    
    def get_analysis_name(self) -> str:
        """返回分析类型名称"""
        return "日内波动范围分析（双起点：昨收&今开）"
    
    def analyze(self, ticker: str, create_plots: bool = True, **kwargs) -> Dict:
        """
        分析股票的日内波动范围
        
        计算从昨日收盘价到今日高点的最大涨幅和到今日低点的最大跌幅
        
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
        print(f"   分析内容: 【昨收起点】昨收→今日高低点 & 【今开起点】今开→今日高低点")
        
        # 从数据库获取数据
        data = self.data_provider.get_stock_data_from_db(ticker, '1d')
        if data is None:
            print(f"❌ 无法获取 {ticker} 的数据")
            return {}
        
        # === 昨收为起点的波动范围分析 ===
        max_gain_from_close, max_loss_from_close = self.stats_calculator.calculate_daily_range_metrics(data)
        
        # 计算昨收起点的统计
        close_gain_stats = self.stats_calculator.calculate_basic_stats(max_gain_from_close)
        close_gain_stats = self._add_prefix_to_stats(close_gain_stats, 'close_gain_')
        
        close_loss_stats = self.stats_calculator.calculate_basic_stats(max_loss_from_close)
        close_loss_stats = self._add_prefix_to_stats(close_loss_stats, 'close_loss_')
        
        close_range = max_gain_from_close - max_loss_from_close
        close_range_stats = self.stats_calculator.calculate_basic_stats(close_range)
        close_range_stats = self._add_prefix_to_stats(close_range_stats, 'close_range_')
        
        # === 今开为起点的波动范围分析 ===
        open_to_high, open_to_low = self.stats_calculator.calculate_open_to_extremes_metrics(data)
        
        # 计算今开起点的统计
        open_high_stats = self.stats_calculator.calculate_basic_stats(open_to_high)
        open_high_stats = self._add_prefix_to_stats(open_high_stats, 'open_high_')
        
        open_low_stats = self.stats_calculator.calculate_basic_stats(open_to_low)
        open_low_stats = self._add_prefix_to_stats(open_low_stats, 'open_low_')
        
        open_range = open_to_high - open_to_low
        open_range_stats = self.stats_calculator.calculate_basic_stats(open_range)
        open_range_stats = self._add_prefix_to_stats(open_range_stats, 'open_range_')
        
        # 合并所有统计结果
        stats = {}
        stats.update(close_gain_stats)
        stats.update(close_loss_stats)
        stats.update(close_range_stats)
        stats.update(open_high_stats)
        stats.update(open_low_stats)
        stats.update(open_range_stats)
        
        # 添加分析元信息
        stats.update({
            'analysis_type': 'daily_range',
            'description': '日内波动范围分析（双起点：昨收&今开）',
            'total_trading_days': len(max_gain_from_close),
            'ticker': ticker,
            'original_ticker': original_ticker,
            'metrics_explanation': {
                'close_based': {
                    'close_gain': '从昨日收盘价到今日最高价的涨幅',
                    'close_loss': '从昨日收盘价到今日最低价的跌幅',
                    'close_range': '昨收起点的波动范围'
                },
                'open_based': {
                    'open_high': '从今日开盘价到今日最高价的涨幅',
                    'open_low': '从今日开盘价到今日最低价的跌幅', 
                    'open_range': '今开起点的波动范围'
                }
            }
        })
        
        # 打印统计结果
        self._print_dual_range_statistics(original_ticker, stats, 
                                         max_gain_from_close, max_loss_from_close, close_range,
                                         open_to_high, open_to_low, open_range)
        
        # 创建图表
        if create_plots:
            # 这里可以创建特殊的波动范围图表
            # 暂时使用现有的可视化工具，以昨收起点的范围为主
            filename = self.visualizer.create_returns_analysis_plot(
                f'{ticker}_DailyRange', close_range, close_range_stats)
            stats['chart_filename'] = filename
        
        # 保存结果
        self._save_results(stats, ticker, 'daily_range_analysis')
        
        return stats
    
    def _add_prefix_to_stats(self, stats: Dict, prefix: str) -> Dict:
        """为统计指标添加前缀"""
        prefixed_stats = {}
        for key, value in stats.items():
            if key == 'percentiles':
                # 特殊处理百分位数
                prefixed_stats[f'{prefix}percentiles'] = value
            elif key in ['positive_percentiles', 'negative_percentiles']:
                # 特殊处理正负百分位数
                prefixed_stats[f'{prefix}{key}'] = value
            else:
                prefixed_stats[f'{prefix}{key}'] = value
        return prefixed_stats
    
    def _print_dual_range_statistics(self, ticker: str, stats: Dict, 
                                   close_gain, close_loss, close_range,
                                   open_high, open_low, open_range):
        """打印双起点日内波动范围统计信息"""
        print(f"\n📊 {ticker} 日内波动范围统计（双起点分析）：")
        print(f"   总交易天数: {stats['total_trading_days']}")
        
        print(f"\n" + "="*60)
        print(f"🔵 【昨收起点分析】昨日收盘价 → 今日高低点")
        print(f"="*60)
        
        print(f"\n📈 最大涨幅统计（昨收→今日高点）：")
        print(f"   平均最大涨幅: {stats['close_gain_mean']:.3f}%")
        print(f"   中位数最大涨幅: {stats['close_gain_median']:.3f}%")
        print(f"   标准差: {stats['close_gain_std']:.3f}%")
        print(f"   历史最大涨幅: {stats['close_gain_max']:.3f}%")
        print(f"   历史最小涨幅: {stats['close_gain_min']:.3f}%")
        
        print(f"\n📉 最大跌幅统计（昨收→今日低点）：")
        print(f"   平均最大跌幅: {stats['close_loss_mean']:.3f}%")
        print(f"   中位数最大跌幅: {stats['close_loss_median']:.3f}%")
        print(f"   标准差: {stats['close_loss_std']:.3f}%")
        print(f"   历史最大跌幅: {stats['close_loss_min']:.3f}%")
        print(f"   历史最小跌幅: {stats['close_loss_max']:.3f}%")
        
        print(f"\n📏 昨收起点波动范围：")
        print(f"   平均波动范围: {stats['close_range_mean']:.3f}%")
        print(f"   中位数波动范围: {stats['close_range_median']:.3f}%")
        print(f"   最大波动范围: {stats['close_range_max']:.3f}%")
        
        print(f"\n" + "="*60)
        print(f"🟠 【今开起点分析】今日开盘价 → 今日高低点")
        print(f"="*60)
        
        print(f"\n📈 开盘到高点涨幅统计：")
        print(f"   平均涨幅: {stats['open_high_mean']:.3f}%")
        print(f"   中位数涨幅: {stats['open_high_median']:.3f}%")
        print(f"   标准差: {stats['open_high_std']:.3f}%")
        print(f"   历史最大涨幅: {stats['open_high_max']:.3f}%")
        print(f"   历史最小涨幅: {stats['open_high_min']:.3f}%")
        
        print(f"\n📉 开盘到低点跌幅统计：")
        print(f"   平均跌幅: {stats['open_low_mean']:.3f}%")
        print(f"   中位数跌幅: {stats['open_low_median']:.3f}%")
        print(f"   标准差: {stats['open_low_std']:.3f}%")
        print(f"   历史最大跌幅: {stats['open_low_min']:.3f}%")
        print(f"   历史最小跌幅: {stats['open_low_max']:.3f}%")
        
        print(f"\n📏 今开起点波动范围：")
        print(f"   平均波动范围: {stats['open_range_mean']:.3f}%")
        print(f"   中位数波动范围: {stats['open_range_median']:.3f}%")
        print(f"   最大波动范围: {stats['open_range_max']:.3f}%")
        
        print(f"\n" + "="*60)
        print(f"📊 【百分位数分析】")
        print(f"="*60)
        
        print(f"\n🔵 昨收起点 - 最大涨幅百分位数：")
        for p, value in stats['close_gain_percentiles'].items():
            print(f"   {p:2d}%: {value:6.3f}%")
        
        print(f"\n🔵 昨收起点 - 最大跌幅百分位数：")
        for p, value in stats['close_loss_percentiles'].items():
            print(f"   {p:2d}%: {value:6.3f}%")
        
        print(f"\n🟠 今开起点 - 开盘到高点百分位数：")
        for p, value in stats['open_high_percentiles'].items():
            print(f"   {p:2d}%: {value:6.3f}%")
        
        print(f"\n🟠 今开起点 - 开盘到低点百分位数：")
        for p, value in stats['open_low_percentiles'].items():
            print(f"   {p:2d}%: {value:6.3f}%")
        
        print(f"\n📏 波动范围百分位数：")
        print(f"🔵 昨收起点波动范围：")
        for p, value in stats['close_range_percentiles'].items():
            print(f"   {p:2d}%: {value:6.3f}%")
        
        print(f"🟠 今开起点波动范围：")
        for p, value in stats['open_range_percentiles'].items():
            print(f"   {p:2d}%: {value:6.3f}%")
        
        print(f"\n" + "="*60)
        print(f"🎯 【对比分析】")
        print(f"="*60)
        
        # 统计分析
        close_positive_days = (close_gain > 0).sum()
        open_positive_days = (open_high > 0).sum()
        
        print(f"\n📈 上涨概率对比：")
        print(f"   昨收→高点上涨天数: {close_positive_days} ({close_positive_days/len(close_gain)*100:.1f}%)")
        print(f"   今开→高点上涨天数: {open_positive_days} ({open_positive_days/len(open_high)*100:.1f}%)")
        
        print(f"\n📏 波动范围对比：")
        print(f"   昨收起点平均波动: {stats['close_range_mean']:.3f}%")
        print(f"   今开起点平均波动: {stats['open_range_mean']:.3f}%")
        print(f"   波动差异: {abs(stats['close_range_mean'] - stats['open_range_mean']):.3f}%")
        
        # 极值分析
        close_gain_max_day = close_gain.idxmax()
        close_loss_min_day = close_loss.idxmin()
        open_high_max_day = open_high.idxmax()
        open_low_min_day = open_low.idxmin()
        
        print(f"\n🔥 极值记录对比：")
        print(f"   昨收最大涨幅: {stats['close_gain_max']:.3f}% ({close_gain_max_day.strftime('%Y-%m-%d')})")
        print(f"   今开最大涨幅: {stats['open_high_max']:.3f}% ({open_high_max_day.strftime('%Y-%m-%d')})")
        print(f"   昨收最大跌幅: {stats['close_loss_min']:.3f}% ({close_loss_min_day.strftime('%Y-%m-%d')})")
        print(f"   今开最大跌幅: {stats['open_low_min']:.3f}% ({open_low_min_day.strftime('%Y-%m-%d')})")

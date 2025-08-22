"""
Comparison Analyzer - 对比分析器

专门负责比较多个股票的收益率特征
"""

from typing import Dict, List
import pandas as pd
from .base_analyzer import BaseAnalyzer


class ComparisonAnalyzer(BaseAnalyzer):
    """对比分析器 - 比较多个股票的收益率特征"""
    
    def get_analysis_name(self) -> str:
        """返回分析类型名称"""
        return "多股票收益率对比分析"
    
    def analyze(self, tickers: List[str], create_plots: bool = True, **kwargs) -> Dict:
        """
        比较多个股票的收益率特征
        
        Args:
            tickers: 股票代码列表
            create_plots: 是否创建对比图表
            
        Returns:
            对比分析结果
        """
        # 打印分析标题
        original_tickers = tickers[:]
        print(f"\n=== 比较收益率分析: {', '.join(original_tickers)} ===")
        
        returns_data = {}
        comparison_stats = {}
        
        # 获取所有股票的收益率数据
        for ticker in tickers:
            original_ticker = ticker
            ticker = self._convert_ticker(ticker)
            
            data = self.data_provider.get_stock_data_from_db(ticker, '1d')
            if data is not None:
                returns = self.stats_calculator.calculate_returns(data, 'Close')
                returns_data[original_ticker] = returns
                stats = self.stats_calculator.calculate_basic_stats(returns)
                stats['ticker'] = ticker
                stats['original_ticker'] = original_ticker
                comparison_stats[original_ticker] = stats
                print(f"   ✅ 获取 {original_ticker} 数据: {len(returns)} 条记录")
            else:
                print(f"   ❌ 无法获取 {original_ticker} 数据")
        
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
        
        # 添加对比分析元信息
        comparison_stats['analysis_metadata'] = {
            'analysis_type': 'comparison',
            'description': '多股票收益率对比分析',
            'compared_tickers': list(returns_data.keys()),
            'total_comparisons': len(returns_data)
        }
        
        # 打印对比结果
        self._print_comparison_results(comparison_stats, list(returns_data.keys()))
        
        # 保存结果
        filename_suffix = '_'.join([self._convert_ticker(t) for t in original_tickers])
        self._save_results(comparison_stats, filename_suffix, 'comparison_analysis')
        
        return comparison_stats
    
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
        
        # 打印风险收益比较
        print(f"\n🎯 风险收益特征排名：")
        risk_return_data = []
        for ticker in tickers:
            if ticker in comparison_stats:
                stats = comparison_stats[ticker]
                risk_return_data.append({
                    'Ticker': ticker,
                    'Return': stats['mean'],
                    'Risk': stats['std'],
                    'Sharpe': stats['mean'] / stats['std'] if stats['std'] > 0 else 0
                })
        
        if risk_return_data:
            risk_return_df = pd.DataFrame(risk_return_data)
            
            print("   按收益率排序:")
            sorted_by_return = risk_return_df.sort_values('Return', ascending=False)
            for i, row in sorted_by_return.iterrows():
                print(f"     {row['Ticker']}: {row['Return']:.3f}%")
            
            print("   按风险排序（标准差）:")
            sorted_by_risk = risk_return_df.sort_values('Risk', ascending=True)
            for i, row in sorted_by_risk.iterrows():
                print(f"     {row['Ticker']}: {row['Risk']:.3f}%")
            
            print("   按夏普比率排序:")
            sorted_by_sharpe = risk_return_df.sort_values('Sharpe', ascending=False)
            for i, row in sorted_by_sharpe.iterrows():
                print(f"     {row['Ticker']}: {row['Sharpe']:.3f}")

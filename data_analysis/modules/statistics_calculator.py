"""
Statistics Calculator - 统计计算器

专门负责各种统计指标的计算，独立的功能模块
"""

import pandas as pd
import numpy as np
from typing import Dict


class StatisticsCalculator:
    """统计计算器 - 负责各种统计指标的计算"""
    
    @staticmethod
    def calculate_returns(data: pd.DataFrame, price_column: str = 'Close') -> pd.Series:
        """
        计算收益率
        
        Args:
            data: 股票数据DataFrame
            price_column: 价格列名
            
        Returns:
            收益率Series（百分比）
        """
        if price_column not in data.columns:
            raise ValueError(f"Column '{price_column}' not found in data")
        
        returns = data[price_column].pct_change() * 100  # 转换为百分比
        return returns.dropna()
    
    @staticmethod
    def calculate_basic_stats(data: pd.Series) -> Dict:
        """
        计算基础统计指标
        
        Args:
            data: 数据Series
            
        Returns:
            统计指标字典
        """
        stats = {
            'count': len(data),
            'mean': data.mean(),
            'median': data.median(),
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'skewness': data.skew(),
            'kurtosis': data.kurtosis()
        }
        
        # 计算整体百分位数
        percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        stats['percentiles'] = {}
        for p in percentiles:
            stats['percentiles'][p] = np.percentile(data, p)
        
        # 分别计算上涨和下跌的百分位数
        positive_data = data[data > 0]
        negative_data = data[data < 0]
        
        if len(positive_data) > 0:
            stats['positive_percentiles'] = {}
            for p in percentiles:
                stats['positive_percentiles'][p] = np.percentile(positive_data, p)
        else:
            stats['positive_percentiles'] = {}
            
        if len(negative_data) > 0:
            stats['negative_percentiles'] = {}
            for p in percentiles:
                stats['negative_percentiles'][p] = np.percentile(negative_data, p)
        else:
            stats['negative_percentiles'] = {}
        
        return stats
    
    @staticmethod
    def calculate_return_metrics(daily_returns: pd.Series) -> Dict:
        """
        计算收益率相关的专门指标
        
        Args:
            daily_returns: 日收益率Series
            
        Returns:
            收益率指标字典
        """
        metrics = {
            'positive_days': (daily_returns > 0).sum(),
            'negative_days': (daily_returns < 0).sum(),
            'flat_days': (daily_returns == 0).sum(),
            'positive_ratio': (daily_returns > 0).sum() / len(daily_returns),
            'negative_ratio': (daily_returns < 0).sum() / len(daily_returns),
            'volatility_annual': daily_returns.std() * np.sqrt(252),  # 年化波动率
        }
        
        # 计算夏普比率（假设无风险利率为0）
        if daily_returns.std() > 0:
            metrics['sharpe_ratio'] = (daily_returns.mean() * 252) / (daily_returns.std() * np.sqrt(252))
        else:
            metrics['sharpe_ratio'] = 0
            
        return metrics
    
    @staticmethod
    def calculate_correlation_matrix(returns_dict: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        计算多个股票收益率的相关性矩阵
        
        Args:
            returns_dict: {ticker: returns_series} 字典
            
        Returns:
            相关性矩阵DataFrame
        """
        returns_df = pd.DataFrame(returns_dict)
        return returns_df.corr()
    
    @staticmethod
    def calculate_drawdown(price_series: pd.Series) -> Dict:
        """
        计算最大回撤等风险指标
        
        Args:
            price_series: 价格时间序列
            
        Returns:
            回撤指标字典
        """
        # 计算累计收益
        cumulative = (1 + price_series.pct_change()).cumprod()
        
        # 计算滚动最大值
        rolling_max = cumulative.expanding().max()
        
        # 计算回撤
        drawdown = (cumulative - rolling_max) / rolling_max
        
        return {
            'max_drawdown': drawdown.min(),
            'max_drawdown_duration': StatisticsCalculator._calculate_max_drawdown_duration(drawdown),
            'current_drawdown': drawdown.iloc[-1] if len(drawdown) > 0 else 0
        }
    
    @staticmethod
    def _calculate_max_drawdown_duration(drawdown: pd.Series) -> int:
        """计算最大回撤持续时间"""
        is_drawdown = drawdown < 0
        drawdown_periods = []
        current_period = 0
        
        for is_dd in is_drawdown:
            if is_dd:
                current_period += 1
            else:
                if current_period > 0:
                    drawdown_periods.append(current_period)
                current_period = 0
        
        # 添加最后一个回撤期（如果存在）
        if current_period > 0:
            drawdown_periods.append(current_period)
        
        return max(drawdown_periods) if drawdown_periods else 0

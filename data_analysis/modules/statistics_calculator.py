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
        计算每日涨跌幅（收益率）

        具体做法：
        - 取出指定的价格列（如'Close'收盘价）
        - 用pandas的pct_change()方法，计算相邻两天的百分比变化
          即：(今日价格 - 昨日价格) / 昨日价格
        - 结果乘以100，得到百分比形式的涨跌幅
        - 去除首行的NaN（因为第一天没有前一天可比）

        Args:
            data: 股票数据DataFrame
            price_column: 价格列名

        Returns:
            每日涨跌幅Series（百分比）
        """
        if price_column not in data.columns:
            raise ValueError(f"Column '{price_column}' not found in data")
        
        # 计算每日涨跌幅百分比
        returns = data[price_column].pct_change() * 100
        return returns.dropna()
    
    @staticmethod
    def calculate_intraday_returns(data: pd.DataFrame) -> pd.Series:
        """
        计算日内涨跌幅（开盘到收盘）

        具体做法：
        - 计算每天从开盘价到收盘价的涨跌幅
        - 公式：(收盘价 - 开盘价) / 开盘价 * 100
        - 这反映了每天交易日内的价格变化

        Args:
            data: 股票数据DataFrame，必须包含'Open'和'Close'列

        Returns:
            日内涨跌幅Series（百分比）
        """
        required_columns = ['Open', 'Close']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # 计算日内涨跌幅百分比：(收盘价 - 开盘价) / 开盘价 * 100
        intraday_returns = (data['Close'] - data['Open']) / data['Open'] * 100
        return intraday_returns.dropna()
    
    @staticmethod
    def calculate_gap_info(data: pd.DataFrame) -> pd.Series:
        """
        计算开盘缺口信息
        
        计算每天开盘价相对于前一天收盘价的缺口：
        - 正值表示高开（gap up）
        - 负值表示低开（gap down）
        - 接近0表示平开
        
        Args:
            data: 股票数据DataFrame，必须包含'Open'和'Close'列
            
        Returns:
            开盘缺口Series（百分比）
        """
        required_columns = ['Open', 'Close']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # 计算开盘缺口：(今日开盘价 - 昨日收盘价) / 昨日收盘价 * 100
        prev_close = data['Close'].shift(1)
        gap = (data['Open'] - prev_close) / prev_close * 100
        return gap.dropna()
    
    @staticmethod
    def calculate_daily_range_metrics(data: pd.DataFrame) -> tuple:
        """
        计算日内波动范围指标
        
        计算从昨日收盘价到今日高点的最大涨幅，以及到今日低点的最大跌幅：
        - 最大涨幅：(今日最高价 - 昨日收盘价) / 昨日收盘价 * 100
        - 最大跌幅：(今日最低价 - 昨日收盘价) / 昨日收盘价 * 100
        
        Args:
            data: 股票数据DataFrame，必须包含'High', 'Low', 'Close'列
            
        Returns:
            (最大涨幅Series, 最大跌幅Series) 元组，单位为百分比
        """
        required_columns = ['High', 'Low', 'Close']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # 获取前一日收盘价
        prev_close = data['Close'].shift(1)
        
        # 计算最大涨幅：(今日最高价 - 昨日收盘价) / 昨日收盘价 * 100
        max_gain = (data['High'] - prev_close) / prev_close * 100
        
        # 计算最大跌幅：(今日最低价 - 昨日收盘价) / 昨日收盘价 * 100
        max_loss = (data['Low'] - prev_close) / prev_close * 100
        
        return max_gain.dropna(), max_loss.dropna()
    
    @staticmethod
    def calculate_open_to_extremes_metrics(data: pd.DataFrame) -> tuple:
        """
        计算从今日开盘价到今日高低点的波动范围指标
        
        计算从今日开盘价到今日高点的涨幅，以及到今日低点的跌幅：
        - 开盘到高点涨幅：(今日最高价 - 今日开盘价) / 今日开盘价 * 100
        - 开盘到低点跌幅：(今日最低价 - 今日开盘价) / 今日开盘价 * 100
        
        Args:
            data: 股票数据DataFrame，必须包含'High', 'Low', 'Open'列
            
        Returns:
            (开盘到高点涨幅Series, 开盘到低点跌幅Series) 元组，单位为百分比
        """
        required_columns = ['High', 'Low', 'Open']
        missing_columns = [col for col in required_columns if col not in data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # 计算从开盘到高点的涨幅：(今日最高价 - 今日开盘价) / 今日开盘价 * 100
        open_to_high = (data['High'] - data['Open']) / data['Open'] * 100
        
        # 计算从开盘到低点的跌幅：(今日最低价 - 今日开盘价) / 今日开盘价 * 100
        open_to_low = (data['Low'] - data['Open']) / data['Open'] * 100
        
        return open_to_high.dropna(), open_to_low.dropna()
    
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
    
    @staticmethod
    def calculate_gap_grouped_stats(intraday_returns: pd.Series, gaps: pd.Series) -> Dict:
        """
        按开盘缺口类型分组计算日内收益率统计
        
        简单分类：
        - 高开：开盘缺口 > 0%
        - 低开：开盘缺口 < 0%
        - 平开：开盘缺口 = 0%
        
        Args:
            intraday_returns: 日内收益率Series
            gaps: 开盘缺口Series
            
        Returns:
            分组统计结果字典
        """
        # 确保两个Series的索引对齐
        aligned_data = pd.DataFrame({
            'intraday_returns': intraday_returns,
            'gaps': gaps
        }).dropna()
        
        if len(aligned_data) == 0:
            return {}
        
        # 分类开盘类型（简单分类）
        gap_up_mask = aligned_data['gaps'] > 0
        gap_down_mask = aligned_data['gaps'] < 0
        gap_flat_mask = aligned_data['gaps'] == 0
        
        results = {}
        
        # 高开统计
        gap_up_returns = aligned_data.loc[gap_up_mask, 'intraday_returns']
        if len(gap_up_returns) > 0:
            results['gap_up'] = {
                'count': len(gap_up_returns),
                'stats': StatisticsCalculator.calculate_basic_stats(gap_up_returns),
                'description': '高开日内表现（开盘价 > 前日收盘价）'
            }
        
        # 低开统计
        gap_down_returns = aligned_data.loc[gap_down_mask, 'intraday_returns']
        if len(gap_down_returns) > 0:
            results['gap_down'] = {
                'count': len(gap_down_returns),
                'stats': StatisticsCalculator.calculate_basic_stats(gap_down_returns),
                'description': '低开日内表现（开盘价 < 前日收盘价）'
            }
        
        # 平开统计
        gap_flat_returns = aligned_data.loc[gap_flat_mask, 'intraday_returns']
        if len(gap_flat_returns) > 0:
            results['gap_flat'] = {
                'count': len(gap_flat_returns),
                'stats': StatisticsCalculator.calculate_basic_stats(gap_flat_returns),
                'description': '平开日内表现（开盘价 = 前日收盘价）'
            }
        
        # 添加总体统计信息
        results['summary'] = {
            'total_days': len(aligned_data),
            'gap_up_days': len(gap_up_returns),
            'gap_down_days': len(gap_down_returns),
            'gap_flat_days': len(gap_flat_returns),
            'gap_up_ratio': len(gap_up_returns) / len(aligned_data) if len(aligned_data) > 0 else 0,
            'gap_down_ratio': len(gap_down_returns) / len(aligned_data) if len(aligned_data) > 0 else 0,
            'gap_flat_ratio': len(gap_flat_returns) / len(aligned_data) if len(aligned_data) > 0 else 0,
            'classification': '简单分类（>0 高开, <0 低开, =0 平开）'
        }
        
        return results

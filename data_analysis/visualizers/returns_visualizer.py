"""
Returns Visualizer - 收益率可视化工具

专门用于创建收益率相关的各种图表
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ReturnsVisualizer:
    """收益率可视化器"""
    
    def __init__(self, style: str = 'seaborn-v0_8', figsize: tuple = (16, 10)):
        """
        初始化可视化器
        
        Args:
            style: matplotlib样式
            figsize: 图表大小
        """
        plt.style.use(style)
        self.figsize = figsize
    
    def create_returns_analysis_plot(self, 
                                   ticker: str, 
                                   daily_returns: pd.Series, 
                                   stats: Dict,
                                   save_path: Optional[str] = None) -> str:
        """
        创建完整的收益率分析图表
        
        Args:
            ticker: 股票代码
            daily_returns: 日收益率数据
            stats: 统计指标字典
            save_path: 保存路径（可选）
            
        Returns:
            保存的文件名
        """
        fig = plt.figure(figsize=self.figsize)
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # 1. 历史收益率时间序列图
        self._plot_time_series(fig.add_subplot(gs[0, :]), daily_returns, stats, ticker)
        
        # 2. 收益率分布直方图
        self._plot_distribution_histogram(fig.add_subplot(gs[1, 0]), daily_returns, stats, ticker)
        
        # 3. 收益率箱线图和百分位数
        self._plot_boxplot_with_percentiles(fig.add_subplot(gs[1, 1]), daily_returns, stats, ticker)
        
        # 设置总标题
        plt.suptitle(f'{ticker} Daily Returns Analysis - {datetime.now().strftime("%Y-%m-%d")}', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        # 保存图表
        if save_path is None:
            from ..modules.file_manager import FileManager
            filename = FileManager.generate_chart_filename(ticker, 'daily_returns_analysis')
        else:
            filename = save_path
            
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"\n📊 图表已保存为: {filename}")
        
        plt.show()
        return filename
    
    def _plot_time_series(self, ax, daily_returns: pd.Series, stats: Dict, ticker: str):
        """绘制时间序列图"""
        daily_returns.plot(ax=ax, alpha=0.7, color='steelblue', linewidth=0.8)
        ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax.axhline(y=stats['mean'], color='green', linestyle='--', alpha=0.7, 
                  label=f"Mean: {stats['mean']:.3f}%")
        
        ax.set_title(f'{ticker} Daily Returns Over Time', fontsize=14, fontweight='bold')
        ax.set_ylabel('Daily Return (%)', fontsize=12)
        ax.set_xlabel('Date', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_distribution_histogram(self, ax, daily_returns: pd.Series, stats: Dict, ticker: str):
        """绘制分布直方图"""
        n_bins = min(50, max(20, len(daily_returns) // 50))
        
        # 绘制直方图
        n, bins, patches = ax.hist(daily_returns, bins=n_bins, alpha=0.7, color='lightblue', 
                                  edgecolor='black', linewidth=0.5, density=True)
        
        # 添加统计线
        ax.axvline(stats['median'], color='red', linestyle='--', 
                  label=f"Median: {stats['median']:.3f}%", linewidth=2)
        ax.axvline(stats['mean'], color='green', linestyle='--', 
                  label=f"Mean: {stats['mean']:.3f}%", linewidth=2)
        
        # 添加正态分布拟合曲线
        x = np.linspace(daily_returns.min(), daily_returns.max(), 100)
        normal_dist = (1/(stats['std'] * np.sqrt(2 * np.pi))) * \
                     np.exp(-0.5 * ((x - stats['mean'])/stats['std'])**2)
        ax.plot(x, normal_dist, 'r-', linewidth=2, alpha=0.8, label='Normal Distribution')
        
        ax.set_title(f'{ticker} Daily Returns Distribution', fontsize=14, fontweight='bold')
        ax.set_xlabel('Daily Return (%)', fontsize=12)
        ax.set_ylabel('Density', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_boxplot_with_percentiles(self, ax, daily_returns: pd.Series, stats: Dict, ticker: str):
        """绘制箱线图和百分位数"""
        # 箱线图
        box_plot = ax.boxplot([daily_returns], patch_artist=True, labels=[ticker])
        box_plot['boxes'][0].set_facecolor('lightgreen')
        box_plot['boxes'][0].set_alpha(0.7)
        
        # 添加百分位数标注
        percentiles_to_show = [5, 25, 50, 75, 95]
        colors = ['red', 'orange', 'blue', 'orange', 'red']
        
        for i, (p, color) in enumerate(zip(percentiles_to_show, colors)):
            value = stats['percentiles'][p]
            ax.axhline(y=value, color=color, linestyle=':', alpha=0.8, linewidth=1.5)
            ax.text(1.1, value, f'{p}%: {value:.2f}%', 
                   verticalalignment='center', fontsize=10, color=color)
        
        ax.set_title(f'{ticker} Returns Box Plot', fontsize=14, fontweight='bold')
        ax.set_ylabel('Daily Return (%)', fontsize=12)
        ax.grid(True, alpha=0.3)
    
    def create_comparison_plot(self, 
                             returns_data: Dict[str, pd.Series], 
                             save_path: Optional[str] = None) -> str:
        """
        创建多个股票收益率对比图
        
        Args:
            returns_data: {ticker: returns_series} 字典
            save_path: 保存路径（可选）
            
        Returns:
            保存的文件名
        """
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        axes = axes.flatten()
        
        # 时间序列对比
        ax1 = axes[0]
        for ticker, returns in returns_data.items():
            returns.plot(ax=ax1, alpha=0.7, label=ticker, linewidth=0.8)
        ax1.set_title('Returns Comparison Over Time', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Daily Return (%)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 分布对比
        ax2 = axes[1]
        for ticker, returns in returns_data.items():
            ax2.hist(returns, bins=30, alpha=0.6, label=ticker, density=True)
        ax2.set_title('Returns Distribution Comparison', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Daily Return (%)', fontsize=12)
        ax2.set_ylabel('Density', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 箱线图对比
        ax3 = axes[2]
        data_for_boxplot = [returns.values for returns in returns_data.values()]
        box_plot = ax3.boxplot(data_for_boxplot, labels=list(returns_data.keys()), 
                              patch_artist=True)
        for patch in box_plot['boxes']:
            patch.set_facecolor('lightblue')
            patch.set_alpha(0.7)
        ax3.set_title('Returns Box Plot Comparison', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Daily Return (%)', fontsize=12)
        ax3.grid(True, alpha=0.3)
        
        # 相关性热图
        ax4 = axes[3]
        corr_df = pd.DataFrame(returns_data).corr()
        sns.heatmap(corr_df, annot=True, cmap='coolwarm', center=0, ax=ax4)
        ax4.set_title('Returns Correlation Matrix', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # 保存图表
        if save_path is None:
            from ..modules.file_manager import FileManager
            filename = FileManager.generate_comparison_filename(list(returns_data.keys()), 'returns')
        else:
            filename = save_path
            
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"\n📊 对比图表已保存为: {filename}")
        
        plt.show()
        return filename

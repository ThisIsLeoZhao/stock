"""
File Manager - 文件管理器

负责分析结果的保存和文件管理
"""

import json
import os
from datetime import datetime
from typing import Dict, Any


class FileManager:
    """文件管理器 - 负责保存分析结果和管理输出文件"""
    
    def __init__(self):
        """初始化文件管理器，创建必要的文件夹"""
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self):
        """确保必要的目录存在"""
        directories = [
            "charts",
            "charts/returns_analysis", 
            "charts/comparison_analysis",
            "results"
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def save_analysis_results(self, results: Dict[str, Any], base_filename: str) -> str:
        """
        保存分析结果到JSON文件
        
        Args:
            results: 分析结果字典
            base_filename: 基础文件名
            
        Returns:
            保存的完整文件名
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        full_filename = f"results/{base_filename}_{timestamp}.json"
        
        try:
            with open(full_filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            print(f"✓ 分析结果已保存到: {full_filename}")
            return full_filename
        except Exception as e:
            print(f"保存结果时出错: {e}")
            return ""
    
    @staticmethod
    def generate_chart_filename(ticker: str, analysis_type: str, extension: str = "png") -> str:
        """
        生成图表文件名
        
        Args:
            ticker: 股票代码
            analysis_type: 分析类型
            extension: 文件扩展名
            
        Returns:
            生成的文件名（包含路径）
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{ticker}_{analysis_type}_{timestamp}.{extension}"
        return f"charts/returns_analysis/{filename}"
    
    @staticmethod
    def generate_comparison_filename(tickers: list, analysis_type: str, extension: str = "png") -> str:
        """
        生成对比图表文件名
        
        Args:
            tickers: 股票代码列表
            analysis_type: 分析类型
            extension: 文件扩展名
            
        Returns:
            生成的文件名（包含路径）
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        ticker_str = "_".join(tickers[:3])  # 最多使用前3个ticker
        if len(tickers) > 3:
            ticker_str += f"_and_{len(tickers)-3}_more"
        filename = f"{ticker_str}_{analysis_type}_comparison_{timestamp}.{extension}"
        return f"charts/comparison_analysis/{filename}"

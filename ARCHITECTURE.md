# 股票分析平台架构说明

## 🏗️ 重构后的架构

### 📁 目录结构
```
data_analysis/
├── analyzers/
│   ├── base_analyzer.py              # 基础分析器抽象类
│   ├── daily_returns_analyzer.py     # 每日收益率分析器
│   ├── intraday_returns_analyzer.py  # 日内收益率分析器（开盘到收盘）
│   ├── weekly_returns_analyzer.py    # 周收益率分析器
│   ├── comparison_analyzer.py        # 多股票对比分析器
│   ├── returns_analyzer_factory.py   # 分析器工厂（主入口）
│   └── returns_analyzer_old.py       # 旧版本备份
├── modules/                           # 通用分析模块
├── visualizers/                       # 可视化工具
└── __init__.py
```

### 🎯 设计原则

1. **单一职责原则**：每个分析器只负责一种特定的分析类型
2. **开闭原则**：易于扩展新的分析器，不需要修改现有代码
3. **依赖倒置**：所有分析器都继承自 `BaseAnalyzer` 抽象类
4. **工厂模式**：`ReturnsAnalyzer` 作为工厂类，统一管理各种分析器

### 📋 分析器类型

| 分析器 | 功能 | 文件 |
|--------|------|------|
| **DailyReturnsAnalyzer** | 每日收益率分析 | `daily_returns_analyzer.py` |
| **IntradayReturnsAnalyzer** | 日内收益率分析（含高开/低开分组） | `intraday_returns_analyzer.py` |
| **WeeklyReturnsAnalyzer** | 周收益率分析 | `weekly_returns_analyzer.py` |
| **ComparisonAnalyzer** | 多股票对比分析 | `comparison_analyzer.py` |

### 🔧 使用方式

#### 1. 向后兼容的使用方式（推荐）
```python
from data_analysis import ReturnsAnalyzer

analyzer = ReturnsAnalyzer()

# 每日分析
analyzer.analyze_daily_returns('SPX')

# 日内分析
analyzer.analyze_intraday_returns('SPX')

# 周分析  
analyzer.analyze_weekly_returns('SPX')

# 对比分析
analyzer.compare_returns(['AAPL', 'GOOGL', 'MSFT'])
```

#### 2. 直接使用特定分析器
```python
from data_analysis.analyzers import IntradayReturnsAnalyzer

analyzer = IntradayReturnsAnalyzer()
result = analyzer.analyze('SPX', create_plots=True)
```

#### 3. 使用统一分析接口
```python
from data_analysis import ReturnsAnalyzer

analyzer = ReturnsAnalyzer()

# 通过类型字符串调用
result = analyzer.run_analysis('intraday', ticker='SPX')
result = analyzer.run_analysis('comparison', tickers=['AAPL', 'GOOGL'])
```

### ➕ 如何添加新的分析器

1. **创建新分析器文件**：继承 `BaseAnalyzer`
```python
from .base_analyzer import BaseAnalyzer

class NewAnalyzer(BaseAnalyzer):
    def get_analysis_name(self) -> str:
        return "新分析类型"
    
    def analyze(self, ticker: str, create_plots: bool = True, **kwargs) -> Dict:
        # 实现分析逻辑
        pass
```

2. **在工厂类中注册**：在 `returns_analyzer_factory.py` 中添加新方法

3. **更新 `__init__.py`**：导出新分析器

### 🎯 架构优势

1. **可扩展性**：添加新分析器非常简单
2. **可维护性**：每个分析器独立，便于维护和测试
3. **模块化**：清晰的职责分离
4. **向后兼容**：保持原有接口不变
5. **类型安全**：使用抽象基类确保一致的接口

### 🔄 命令行使用

所有原有命令保持不变：

```bash
python3 main.py analyze SPX      # 使用 DailyReturnsAnalyzer
python3 main.py intraday SPX     # 使用 IntradayReturnsAnalyzer  
python3 main.py compare AAPL GOOGL  # 使用 ComparisonAnalyzer
```

### 📝 未来扩展建议

可以轻松添加的新分析器：
- **MonthlyReturnsAnalyzer**：月收益率分析
- **VolatilityAnalyzer**：波动率专项分析
- **TrendAnalyzer**：趋势分析
- **SeasonalityAnalyzer**：季节性分析
- **RiskAnalyzer**：风险指标分析
- **PerformanceAnalyzer**：绩效归因分析

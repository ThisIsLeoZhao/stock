# Stock Analysis Platform V2.0 - 工程化股票分析平台

这是一个功能完整的股票分析平台，采用现代化工程架构设计，支持数据获取、智能缓存、多维度分析和专业可视化。

## 🏗️ 工程化架构

### 项目结构
```
stock/
├── 📁 data_fetching/           # 数据获取模块
│   ├── __init__.py
│   ├── data_fetcher.py         # 核心数据获取
│   ├── cache_manager.py        # 智能缓存管理
│   └── example_usage.py        # 使用示例
├── 📁 data_analysis/           # 数据分析模块
│   ├── __init__.py
│   ├── 📁 modules/             # 基础分析模块
│   │   ├── __init__.py
│   │   └── base_analyzer.py    # 基础分析器
│   ├── 📁 analyzers/           # 专门分析器
│   │   ├── __init__.py
│   │   └── returns_analyzer.py # 收益率分析器
│   └── 📁 visualizers/         # 可视化工具
│       ├── __init__.py
│       └── returns_visualizer.py # 收益率可视化
├── 📁 ticker_data/             # 数据存储
│   └── stock_cache.db          # SQLite缓存数据库
├── 📁 strategy/                # 策略分析文档
├── main.py                     # 主入口文件
├── start.sh                    # 环境启动脚本
├── requirements.txt            # 依赖包列表
└── README.md                   # 说明文档
```

## 🆕 V2.0版本重大改进

### 🏗️ 工程化重构
- **模块化设计**: 数据获取和分析完全分离，各司其职
- **可扩展架构**: 新增分析功能只需添加新的分析器
- **统一入口**: `main.py` 提供命令行界面，操作简单直观
- **包管理**: 规范的Python包结构，支持相对导入

### 📊 分析功能升级
- **专业分析器**: `ReturnsAnalyzer` 专门处理收益率分析
- **高级可视化**: `ReturnsVisualizer` 提供多种专业图表
- **统计完备**: 支持均值、中位数、标准差、百分位数、夏普比率等
- **多股对比**: 支持多个股票的收益率对比分析

### 🎨 可视化增强
- **协调配色**: 统一的颜色方案和字体大小 [[memory:6811451]]
- **多图表类型**: 时间序列、分布直方图、箱线图、相关性热图
- **高质量输出**: 300 DPI PNG文件，支持学术和商业使用
- **中文支持**: 完整的中文显示支持

## 🚀 快速开始

### 1. 环境设置
```bash
# 使用便捷脚本（推荐）
source start.sh

# 或手动设置
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 命令行使用

#### 获取数据
```bash
# 获取SPX 10年数据
python3 main.py fetch SPX

# 获取AAPL 5年数据
python3 main.py fetch AAPL --period 5y

# 获取周线数据
python3 main.py fetch GOOGL --period 2y --interval 1wk
```

#### 分析单个股票
```bash
# 分析SPX收益率分布
python3 main.py analyze SPX

# 分析AAPL收益率
python3 main.py analyze AAPL
```

#### 比较多个股票
```bash
# 比较科技股收益率
python3 main.py compare AAPL GOOGL MSFT

# 比较指数和个股
python3 main.py compare SPX AAPL TSLA
```

#### 查看可用数据
```bash
# 显示数据库中所有可用数据
python3 main.py list
```

### 3. 编程接口使用

#### 数据获取
```python
from data_fetching import StockDataService

service = StockDataService()
spx_data = service.get_stock_data('^GSPC', period='10y', interval='1d')
```

#### 收益率分析
```python
from data_analysis import ReturnsAnalyzer

analyzer = ReturnsAnalyzer()

# 分析单个股票
results = analyzer.analyze_daily_returns('^GSPC', create_plots=True)

# 比较多个股票
comparison = analyzer.compare_returns(['^GSPC', 'AAPL', 'GOOGL'], create_plots=True)
```

## 📊 分析功能

### 收益率统计分析
- **基础统计**: 均值、中位数、标准差、偏度、峰度
- **风险指标**: 年化波动率、夏普比率
- **分布分析**: 1%, 5%, 10%, 25%, 50%, 75%, 90%, 95%, 99% 百分位数
- **涨跌统计**: 上涨/下跌天数及比例

### 可视化图表
1. **时间序列图**: 收益率历史走势，包含均值线
2. **分布直方图**: 收益率分布密度，叠加正态分布拟合
3. **箱线图**: 四分位数分析，异常值标识
4. **对比图表**: 多股票收益率对比和相关性分析

### 输出文件
- **图表文件**: 高质量PNG图片 (300 DPI)
- **分析报告**: JSON格式的详细统计结果
- **控制台输出**: 结构化的分析摘要

## 🔧 技术特性

### 数据获取模块
- **SQLite缓存**: 高性能数据库存储
- **智能缓存**: 基于数据覆盖范围的缓存逻辑
- **API容错**: 完善的错误处理和重试机制
- **多维度支持**: 日线、周线、月线数据

### 分析引擎
- **模块化设计**: 基础分析器 + 专门分析器
- **可扩展性**: 轻松添加新的分析功能
- **高性能**: 优化的数据处理和计算
- **类型安全**: 完整的类型注解

### 可视化系统
- **专业图表**: 基于matplotlib + seaborn
- **美观设计**: 协调的配色方案和布局
- **多格式支持**: PNG、SVG等多种输出格式
- **响应式布局**: 自适应图表大小和元素

## 📈 使用场景

- **投资分析**: 个股和指数的收益率特征分析
- **风险管理**: 波动率和风险指标计算
- **策略研究**: 多资产收益率对比分析
- **学术研究**: 规范的统计分析和可视化
- **量化交易**: 为策略开发提供基础分析

## 🛠️ 扩展开发

### 添加新的分析器
1. 在 `data_analysis/analyzers/` 中创建新的分析器
2. 继承 `BaseAnalyzer` 类
3. 在 `data_analysis/__init__.py` 中导出

### 添加新的可视化器
1. 在 `data_analysis/visualizers/` 中创建新的可视化器
2. 遵循现有的设计模式
3. 在对应分析器中调用

### 集成示例
```python
# 自定义分析器示例
from data_analysis.modules.base_analyzer import BaseAnalyzer

class CustomAnalyzer(BaseAnalyzer):
    def analyze_volatility(self, ticker: str):
        data = self.get_stock_data_from_db(ticker)
        # 实现您的分析逻辑
        return results
```

## 📋 依赖包

- `yfinance`: 股票数据获取
- `pandas`: 数据处理和分析
- `numpy`: 数值计算
- `matplotlib`: 基础绘图
- `seaborn`: 统计图表

## 🚀 未来规划

- **技术指标**: RSI、MACD、布林带等技术分析
- **策略回测**: 完整的量化策略回测框架
- **机器学习**: 价格预测和模式识别
- **实时数据**: 支持实时数据流和分析
- **Web界面**: 基于Flask/Django的Web界面

---

这个平台为股票分析提供了坚实的基础架构，既适合快速原型开发，也支持复杂的量化分析需求。通过模块化设计，您可以轻松扩展新功能，构建属于自己的股票分析工具箱。
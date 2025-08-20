# 股票数据获取模块 V2

这是一个功能完整的股票数据获取系统，采用现代化架构设计，支持多维度数据拉取和智能缓存机制。

## 🆕 V2版本改进

- **SQLite存储**: 使用SQLite数据库替代JSON文件，提供更好的性能和可靠性
- **智能缓存**: 基于数据覆盖范围的缓存逻辑，而非文件时间戳
- **关注点分离**: 数据获取和缓存逻辑完全分离，代码更易理解和维护
- **更好的性能**: 优化的缓存查询和数据管理

## 功能特性

- **多维度支持**: 支持日线、周线、月线数据
- **智能缓存**: SQLite数据库缓存，基于数据范围的过期判断
- **灵活配置**: 可自定义时间范围和数据维度  
- **OHLC数据**: 提供开盘、最高、最低、收盘价格数据
- **错误处理**: 完善的错误处理和日志记录
- **易于使用**: 简洁的API接口

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 基本用法

```python
from data_fetcher import StockDataService

# 创建数据服务（整合了获取和缓存）
service = StockDataService()

# 获取苹果公司10年日线数据（默认参数）
aapl_data = service.get_stock_data('AAPL')

# 获取谷歌5年周线数据
googl_weekly = service.get_stock_data('GOOGL', period='5y', interval='1wk')

# 获取标普500 3年月线数据
spy_monthly = service.get_stock_data('SPY', period='3y', interval='1mo')
```

### 便捷函数

```python
from data_fetcher import get_stock_data

# 快速获取数据
data = get_stock_data('TSLA', period='2y', interval='1wk')
```

### 分离的组件使用

```python
# 如果需要更精细的控制，可以分别使用各组件
from cache_manager import CacheManager
from data_fetcher import DataFetcher

cache = CacheManager()
fetcher = DataFetcher()

# 直接从API获取
fresh_data = fetcher.fetch_from_api('AAPL', '1y', '1d')

# 手动缓存管理
cache.cache_data('AAPL', '1d', fresh_data)
```

## 参数说明

### `get_stock_data` 方法参数

- `ticker` (str): 股票代码，如 'AAPL', 'GOOGL', 'TSLA'
- `period` (str): 时间范围，默认 '10y'
  - 支持格式: '1y', '2y', '5y', '10y', '6mo', '3mo' 等
- `interval` (str): 数据维度，默认 '1d'
  - `'1d'`: 日线数据
  - `'1wk'`: 周线数据
  - `'1mo'`: 月线数据
- `force_refresh` (bool): 强制刷新缓存，默认 False

## 数据格式

返回的DataFrame包含以下列：
- `Open`: 开盘价
- `High`: 最高价
- `Low`: 最低价
- `Close`: 收盘价
- `Volume`: 成交量（如果可用）

索引为日期时间格式，方便进行时间序列分析。

## 缓存机制

- **SQLite存储**: 使用SQLite数据库替代JSON文件，提供更好的性能
- **智能缓存**: 基于数据覆盖范围判断是否需要重新获取
  - 如果缓存中已有覆盖请求范围的数据，直接返回
  - 只有在缓存数据无法覆盖请求范围时才从API获取
- **数据库位置**: 默认保存在 `ticker_data/stock_cache.db`

### 缓存管理

```python
# 查看缓存信息
cache_info = service.get_cache_info()

# 清除特定股票的缓存
service.clear_cache('AAPL')

# 清除特定间隔的缓存
service.clear_cache(interval='1d')

# 清除所有缓存
service.clear_cache()

# 清理旧缓存（30天前的）
service.cleanup_old_cache(days_old=30)
```

## 示例代码

运行 `example_usage.py` 查看完整的使用示例：

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行示例
python3 example_usage.py
```

## 项目结构

```
stock/
├── data_fetcher.py      # 核心数据获取模块
├── cache_manager.py     # 缓存管理模块
├── example_usage.py     # 使用示例
├── requirements.txt     # 依赖包列表
├── venv/               # Python虚拟环境
├── ticker_data/        # 缓存数据目录
│   └── stock_cache.db  # SQLite缓存数据库
├── strategy/           # 策略分析文档
└── README.md          # 说明文档
```

## 虚拟环境设置

为了确保项目在不同电脑上的可移植性，建议使用虚拟环境：

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行示例
python3 example_usage.py
```

## 后续发展

该模块为股票分析系统的基础模块，后续可以在此基础上构建：
- 技术指标计算模块
- 量化策略回测模块
- 数据可视化模块
- 机器学习预测模块

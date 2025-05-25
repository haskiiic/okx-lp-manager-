# OKX钱包LP管理系统

基于OKX钱包API和PancakeSwap V3的流动性提供(LP)自动管理系统，帮助用户高效管理多个LP头寸，支持批量操作和实时监控。

## 🚀 核心功能

### 🔗 OKX钱包集成
- **钱包账户管理**: 创建和管理OKX钱包账户
- **余额查询**: 实时查询多链代币余额
- **交易签名**: 集成OKX签名SDK进行安全交易
- **交易广播**: 自动广播已签名的交易到区块链

### 🥞 PancakeSwap V3 LP管理
- **流动性添加**: 创建指定价格区间的LP头寸
- **智能路由**: 自动选择最优的交易路径
- **费率选择**: 支持0.01%、0.05%、0.3%、1%等多种费率
- **价格计算**: 精确的tick计算和价格区间设置

### 💰 多链支持
- **BSC (Binance Smart Chain)**: 主要支持网络
- **Ethereum**: 以太坊主网支持
- **Polygon**: Polygon网络支持
- **扩展性**: 易于添加其他EVM兼容链

### 📊 实时监控
- **头寸跟踪**: 实时监控LP头寸状态
- **收益计算**: 自动计算手续费收益
- **价格监控**: 监控价格变化和范围状态
- **报警系统**: 价格偏离时自动提醒

### ⚡ 批量操作
- **批量创建**: 同时创建多个LP头寸
- **批量管理**: 统一管理所有头寸
- **自动化**: 支持定时和策略化操作

## 🛠️ 技术架构

### 后端技术栈
- **FastAPI**: 高性能的Web框架
- **SQLAlchemy**: 异步ORM数据库操作
- **PostgreSQL**: 主数据库
- **Redis**: 缓存和实时数据
- **Web3.py**: 区块链交互
- **Celery**: 异步任务队列

### 数据库设计
- **钱包管理**: 存储钱包地址和加密私钥
- **LP头寸**: 记录所有流动性头寸信息
- **交易记录**: 完整的交易历史追踪
- **策略配置**: 自动化策略参数

### API设计
- **RESTful**: 标准的REST API接口
- **异步处理**: 支持高并发请求
- **错误处理**: 完善的异常处理机制
- **文档生成**: 自动生成API文档

## 📦 安装配置

### 环境要求
```bash
Python 3.8+
PostgreSQL 12+
Redis 6+
```

### 1. 克隆项目
```bash
git clone <repository-url>
cd okx_api
```

### 2. 安装依赖
```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 安装依赖
pip install poetry
poetry install --no-root
```

### 3. 配置环境变量
```bash
# 复制配置文件
cp config.env.example .env

# 编辑配置文件
vim .env
```

### 4. 配置OKX API
在`.env`文件中配置你的OKX API密钥:
```env
OKX_API_KEY=your_okx_api_key_here
OKX_SECRET_KEY=your_okx_secret_key_here  
OKX_PASSPHRASE=your_okx_passphrase_here
OKX_BASE_URL=https://web3.okx.com
```

### 5. 配置数据库
```bash
# PostgreSQL配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost/okx_lp_db

# Redis配置  
REDIS_URL=redis://localhost:6379/0
```

### 6. 启动服务
```bash
# 启动主应用
python main.py
```

服务将在 `http://localhost:8000` 启动

## 📖 使用指南

### API文档
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 基本使用流程

#### 1. 创建钱包账户
```bash
curl -X GET "http://localhost:8000/api/v1/wallet/0x742d35Cc6644C93A5B9Ba20bD40FA0bd5CfDD7C3/account?networks=bsc,ethereum"
```

#### 2. 查询钱包余额
```bash
curl -X POST "http://localhost:8000/api/v1/wallet/balance" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "0x742d35Cc6644C93A5B9Ba20bD40FA0bd5CfDD7C3",
    "token_addresses": ["native", "0x55d398326f99059fF775485246999027B3197955"],
    "network": "bsc"
  }'
```

#### 3. 创建LP头寸
```bash
curl -X POST "http://localhost:8000/api/v1/lp/create" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "0x742d35Cc6644C93A5B9Ba20bD40FA0bd5CfDD7C3",
    "token0_symbol": "BNB",
    "token1_symbol": "USDT",
    "token0_address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
    "token1_address": "0x55d398326f99059fF775485246999027B3197955",
    "amount0_desired": 0.1,
    "amount1_desired": 30.0,
    "price_lower": 250.0,
    "price_upper": 350.0,
    "fee_tier": 3000,
    "network": "bsc"
  }'
```

#### 4. 执行交易
```bash
curl -X POST "http://localhost:8000/api/v1/lp/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "position_id": 1,
    "signed_tx": "0x...",
    "account_id": "your_account_id"
  }'
```

### 使用示例脚本
```bash
# 运行完整示例
python scripts/example_usage.py
```

## 🔧 高级配置

### 支持的网络和代币

#### BSC (Binance Smart Chain)
```python
NETWORK_CONFIG = {
    "bsc": {
        "chain_id": 56,
        "rpc_url": "https://bsc-dataseed1.binance.org/",
        "tokens": {
            "WBNB": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
            "USDT": "0x55d398326f99059fF775485246999027B3197955",
            "USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
            "CAKE": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82"
        }
    }
}
```

### PancakeSwap V3 费率等级
- **100 (0.01%)**: 稳定币对，如USDT/USDC
- **500 (0.05%)**: 主流币对，如ETH/USDC  
- **3000 (0.3%)**: 标准费率，适合大多数币对
- **10000 (1%)**: 高风险币对

### 价格区间策略
```python
# 保守策略
CONSERVATIVE_RANGE = {
    "stable_pairs": "±2-5%",   # 稳定币对
    "major_pairs": "±10-20%",  # 主流币对
    "volatile_pairs": "±30-50%" # 高波动币对
}

# 激进策略  
AGGRESSIVE_RANGE = {
    "stable_pairs": "±1-2%",
    "major_pairs": "±5-10%", 
    "volatile_pairs": "±15-30%"
}
```

## 🔒 安全说明

### 私钥管理
- 私钥采用AES-256加密存储
- 支持硬件钱包集成
- 建议使用环境变量管理敏感信息

### API安全
- 所有API调用需要验证
- 支持JWT身份认证
- 请求限制和防护措施

### 交易安全
- 交易前余额验证
- 滑点保护机制
- 超时和重试处理

## 📊 监控和告警

### 头寸监控
```python
# 启动监控
curl -X GET "http://localhost:8000/api/v1/monitoring/start"
```

### 监控指标
- LP头寸价值变化
- 手续费收益统计
- 价格偏离程度
- 交易执行状态

## 🚨 常见问题

### Q: 如何获取OKX API密钥？
A: 访问 [OKX开发者中心](https://web3.okx.com) 注册并申请API密钥

### Q: 支持哪些钱包？
A: 目前支持OKX钱包，计划支持MetaMask、Trust Wallet等

### Q: 如何设置价格区间？
A: 建议根据币对波动性设置，稳定币对用窄区间，高波动币对用宽区间

### Q: 交易失败怎么办？
A: 检查余额、网络状态、滑点设置，查看日志获取详细错误信息

## 🛣️ 开发路线

### 已完成功能 ✅
- [x] OKX钱包API集成
- [x] PancakeSwap V3 LP管理
- [x] 多链支持 (BSC/ETH/Polygon)
- [x] 实时监控系统
- [x] 批量操作功能

### 开发中 🚧
- [ ] Web前端界面
- [ ] 移动端应用
- [ ] 高级策略引擎
- [ ] 风险管理模块

### 计划功能 📋
- [ ] 更多DEX支持 (Uniswap, SushiSwap)
- [ ] 跨链桥集成
- [ ] DeFi聚合器功能
- [ ] 社区策略分享

## 👥 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 开发环境设置
```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest

# 代码格式化
black app/
isort app/
```

### 提交规范
- 功能: `feat: 添加新功能`
- 修复: `fix: 修复bug`
- 文档: `docs: 更新文档`
- 重构: `refactor: 代码重构`

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📧 联系我们

- 📧 邮箱: your-email@example.com
- 💬 Discord: [加入我们的社区](https://discord.gg/your-server)
- 🐦 Twitter: [@your_twitter](https://twitter.com/your_twitter)

---

⭐ 如果这个项目对您有帮助，请给个Star支持！ 
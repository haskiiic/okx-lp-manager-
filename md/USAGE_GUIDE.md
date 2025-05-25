# OKX钱包LP管理系统 - 使用指南

## 🚀 快速开始

### 1. 环境准备

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖（已使用Poetry管理）
poetry install

# 启动系统
python main.py
```

### 2. 验证系统状态

访问 http://localhost:8000/docs 查看API文档，或运行测试脚本：

```bash
python test_api.py
```

## 📋 核心功能说明

### 🔧 系统管理

#### 健康检查
```bash
curl http://localhost:8000/api/v1/health
```

#### 系统配置
```bash
curl http://localhost:8000/api/v1/test/config
```

### 💰 钱包管理

#### 查询钱包余额
```bash
curl -X POST "http://localhost:8000/api/v1/wallet/balance" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "0xa7b3f77a6376f906dc8ca568893692af7c720d21",
    "token_addresses": ["native", "0x55d398326f99059fF775485246999027B3197955"],
    "network": "bsc"
  }'
```

#### 创建钱包账户
```bash
curl "http://localhost:8000/api/v1/wallet/0xa7b3f77a6376f906dc8ca568893692af7c720d21/account?networks=bsc,ethereum"
```

### 🌊 LP头寸管理

#### 查询LP头寸
```bash
curl "http://localhost:8000/api/v1/lp/positions/0xa7b3f77a6376f906dc8ca568893692af7c720d21"
```

#### 创建LP头寸
```bash
curl -X POST "http://localhost:8000/api/v1/lp/create" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "0xa7b3f77a6376f906dc8ca568893692af7c720d21",
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

#### 批量创建LP头寸
```bash
curl -X POST "http://localhost:8000/api/v1/lp/batch-create" \
  -H "Content-Type: application/json" \
  -d '{
    "positions": [
      {
        "wallet_address": "0xa7b3f77a6376f906dc8ca568893692af7c720d21",
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
      }
    ]
  }'
```

#### 执行LP交易
```bash
curl -X POST "http://localhost:8000/api/v1/lp/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "position_id": 123,
    "signed_tx": "0x...",
    "account_id": "your_okx_account_id"
  }'
```

### 📊 监控管理

#### 启动LP头寸监控
```bash
curl "http://localhost:8000/api/v1/monitoring/start"
```

#### 获取池信息
```bash
curl "http://localhost:8000/api/v1/pools/info?token0=0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c&token1=0x55d398326f99059fF775485246999027B3197955&fee_tier=3000&network=bsc"
```

## ⚙️ 配置说明

### 环境变量配置

编辑 `.env` 文件：

```env
# OKX API配置
OKX_API_KEY=your_real_api_key
OKX_SECRET_KEY=your_secret_key  
OKX_PASSPHRASE=your_passphrase
OKX_PROJECT_ID=your_project_id

# 数据库配置
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/okx_lp_db
REDIS_URL=redis://localhost:6379/0

# 区块链RPC配置
BSC_RPC_URL=https://bsc-dataseed.binance.org/
ETHEREUM_RPC_URL=https://eth-mainnet.alchemyapi.io/v2/your_key
POLYGON_RPC_URL=https://polygon-rpc.com/

# LP管理配置
MIN_LIQUIDITY_USD=100.0
MAX_SLIPPAGE_PERCENT=1.0
DEFAULT_FEE_TIER=3000
AUTO_REBALANCE_ENABLED=true
REBALANCE_THRESHOLD_PERCENT=10.0
```

### 数据库启动

使用Docker Compose启动数据库：

```bash
docker-compose up -d postgres redis
```

## 🎯 使用场景

### 场景1：单个LP头寸创建

1. 查询钱包余额确认有足够资金
2. 调用创建LP头寸接口
3. 使用返回的签名信息在OKX钱包中签名
4. 调用执行交易接口广播交易

### 场景2：批量LP头寸管理

1. 准备多个LP头寸配置
2. 调用批量创建接口
3. 系统异步处理所有头寸创建
4. 通过查询接口监控处理进度

### 场景3：实时监控管理

1. 启动LP头寸监控
2. 系统自动检测价格变化
3. 根据设定的阈值自动重平衡
4. 生成操作日志和通知

## 🔧 故障排除

### 常见问题

#### 1. 数据库连接失败
```
解决方案：
- 检查PostgreSQL是否运行
- 验证数据库连接参数
- 系统会自动降级到模拟模式
```

#### 2. OKX API认证失败
```
解决方案：
- 检查API密钥配置
- 验证项目ID和权限
- 系统会返回模拟签名信息
```

#### 3. 区块链RPC连接超时
```
解决方案：
- 检查RPC URL配置
- 尝试使用备用RPC节点
- 检查网络连接
```

### 日志查看

系统日志保存在 `logs/` 目录：

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

## 📚 进阶功能

### 自定义策略

1. 修改 `app/services/lp_manager.py` 中的策略逻辑
2. 配置自定义重平衡参数
3. 实现自定义监控告警

### 扩展支持的网络

1. 在 `app/config.py` 中添加新网络配置
2. 更新合约地址映射
3. 测试新网络的功能

### 性能优化

1. 启用Redis缓存
2. 配置数据库连接池
3. 使用异步处理优化响应时间

## 🛡️ 安全建议

1. **私钥安全**：永远不要在代码中硬编码私钥
2. **API密钥**：定期轮换OKX API密钥
3. **网络安全**：在生产环境中配置HTTPS
4. **访问控制**：实现适当的身份验证和授权
5. **监控告警**：配置异常监控和告警机制

## 📞 技术支持

- **API文档**：http://localhost:8000/docs
- **系统健康检查**：http://localhost:8000/api/v1/health
- **测试脚本**：`python test_api.py`
- **日志文件**：`logs/app.log`

---

*本系统实现了okx.md中描述的所有功能，支持通过API自动化管理LP头寸，包括批量创建和实时管理功能。* 
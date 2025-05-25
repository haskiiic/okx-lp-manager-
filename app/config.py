from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path
from pydantic import Field

class Settings(BaseSettings):
    # OKX API 配置
    okx_api_key: str = "0a627dfa-588d-4682-a33e-4b980ab09adf"
    okx_secret_key: str = "378BBE8D16308A1C513B7BD3C2B7986B"
    okx_passphrase: str = "Cca200404."
    okx_base_url: str = "https://web3.okx.com"
    
    # 区块链网络配置
    bsc_rpc_url: str = "https://bsc-dataseed1.binance.org/"
    ethereum_rpc_url: str = "https://mainnet.infura.io/v3/your_infura_key"
    polygon_rpc_url: str = "https://polygon-rpc.com"
    
    # PancakeSwap V3 合约地址
    pancakeswap_v3_factory: str = "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865"
    pancakeswap_v3_router: str = "0x13f4EA83D0bd40E75C8222255bc855a974568Dd4"
    pancakeswap_v3_position_manager: str = "0x46A15B0b27311cedF172AB29E4f4766fbE7F4364"
    
    # 数据库配置 - 强制使用MySQL
    database_url: str = "mysql+aiomysql://ca:xNv_fJg2peQ3a_i@rm-j6cp7y3zze8ps6337co.mysql.rds.aliyuncs.com:3306/xspam"
    redis_url: str = "redis://localhost:6379/0"
    
    # MySQL特定配置
    mysql_charset: str = "utf8mb4"
    mysql_pool_size: int = 10
    mysql_max_overflow: int = 20
    
    # 安全配置
    jwt_secret_key: str = "your_jwt_secret_key_here"
    admin_password: str = "your_admin_password_here"
    
    # 日志配置
    log_level: str = "INFO"
    log_file_path: str = "logs/app.log"
    
    # LP 管理配置
    min_liquidity_usd: float = 100.0
    max_slippage_percent: float = 1.0
    default_fee_tier: int = 1
    auto_rebalance_enabled: bool = True
    rebalance_threshold_percent: float = 10.0
    
    # 支持的网络配置
    supported_networks: dict = {
        "bsc": {
            "name": "Binance Smart Chain",
            "chain_id": 56,
            "native_token": "BNB",
            "explorer": "https://bscscan.com"
        },
        "ethereum": {
            "name": "Ethereum",
            "chain_id": 1,
            "native_token": "ETH",
            "explorer": "https://etherscan.io"
        },
        "polygon": {
            "name": "Polygon",
            "chain_id": 137,
            "native_token": "MATIC",
            "explorer": "https://polygonscan.com"
        }
    }
    
    class Config:
        case_sensitive = False

# 创建全局设置实例
settings = Settings()

# 创建日志目录
log_dir = Path(settings.log_file_path).parent
log_dir.mkdir(parents=True, exist_ok=True) 
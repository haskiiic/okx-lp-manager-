from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from app.config import settings

Base = declarative_base()

class Wallet(Base):
    """钱包模型"""
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(42), unique=True, index=True, nullable=False)
    private_key_encrypted = Column(Text)  # 加密后的私钥
    name = Column(String(100), nullable=True)
    network = Column(String(20), nullable=False)  # bsc, ethereum, polygon
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # 关联关系
    lp_positions = relationship("LPPosition", back_populates="wallet")

class LPPosition(Base):
    """LP 流动性头寸模型"""
    __tablename__ = "lp_positions"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"))
    position_id = Column(String(100), index=True)  # PancakeSwap V3 NFT Token ID
    pool_address = Column(String(42), nullable=False)  # 池子合约地址
    
    # 代币信息
    token0_address = Column(String(42), nullable=False)
    token1_address = Column(String(42), nullable=False)
    token0_symbol = Column(String(20), nullable=False)
    token1_symbol = Column(String(20), nullable=False)
    
    # LP参数
    fee_tier = Column(Integer, nullable=False)  # 费率等级
    tick_lower = Column(Integer, nullable=False)  # 价格下限tick
    tick_upper = Column(Integer, nullable=False)  # 价格上限tick
    liquidity = Column(String(100), default="0")  # 流动性数量
    
    # 数量信息
    amount0 = Column(String(100), nullable=False)  # token0数量(wei)
    amount1 = Column(String(100), nullable=False)  # token1数量(wei)
    usd_value = Column(Numeric(20, 8), default=0.0)  # USD价值
    
    # 状态信息
    status = Column(String(20), default="pending")  # pending, active, closed
    network = Column(String(20), default="bsc")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    wallet = relationship("Wallet", back_populates="lp_positions")
    transactions = relationship("LPTransaction", back_populates="position")

class LPTransaction(Base):
    """LP 交易记录模型"""
    __tablename__ = "lp_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    position_id = Column(Integer, ForeignKey("lp_positions.id"), nullable=False)
    tx_hash = Column(String(66), unique=True, index=True, nullable=False)
    tx_type = Column(String(20), nullable=False)  # add_liquidity, remove_liquidity, collect_fees
    amount0 = Column(String(100), nullable=True)
    amount1 = Column(String(100), nullable=True)
    fees_collected0 = Column(String(100), nullable=True)
    fees_collected1 = Column(String(100), nullable=True)
    gas_used = Column(String(100), nullable=True)
    gas_price = Column(String(100), nullable=True)
    block_number = Column(Integer, nullable=True)
    status = Column(String(20), default="pending")  # pending, confirmed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    position = relationship("LPPosition", back_populates="transactions")

class TokenPrice(Base):
    """代币价格模型"""
    __tablename__ = "token_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    token_address = Column(String(42), nullable=False)
    symbol = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    price_usd = Column(Float, nullable=False)
    network = Column(String(20), nullable=False)
    decimals = Column(Integer, nullable=False)
    market_cap = Column(Float, nullable=True)
    volume_24h = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LPStrategy(Base):
    """LP 策略模型"""
    __tablename__ = "lp_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    token0_symbol = Column(String(20), nullable=False)
    token1_symbol = Column(String(20), nullable=False)
    network = Column(String(20), nullable=False)
    fee_tier = Column(Integer, nullable=False)
    min_price_ratio = Column(Float, nullable=False)  # 最小价格比例
    max_price_ratio = Column(Float, nullable=False)  # 最大价格比例
    rebalance_threshold = Column(Float, default=10.0)  # 重平衡阈值%
    auto_compound = Column(Boolean, default=True)  # 自动复投
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 创建异步数据库引擎
def create_engine():
    """创建数据库引擎"""
    if settings.database_url.startswith("mysql"):
        # MySQL配置
        engine = create_async_engine(
            settings.database_url,
            echo=True if settings.log_level == "DEBUG" else False,
            pool_size=settings.mysql_pool_size,
            max_overflow=settings.mysql_max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,  # 1小时回收连接
            connect_args={
                "charset": settings.mysql_charset,
                "autocommit": False
            }
        )
    else:
        # PostgreSQL配置（保持向后兼容）
        engine = create_async_engine(
            settings.database_url,
            echo=True if settings.log_level == "DEBUG" else False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
    return engine

engine = create_engine()

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_database():
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """创建数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) 
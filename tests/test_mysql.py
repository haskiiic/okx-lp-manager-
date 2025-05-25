#!/usr/bin/env python3
"""
MySQL数据库连接测试脚本
测试与阿里云RDS MySQL的连接
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from loguru import logger

# 直接设置MySQL连接URL
MYSQL_URL = "mysql+aiomysql://ca:xNv_fJg2peQ3a_i@rm-j6cp7y3zze8ps6337co.mysql.rds.aliyuncs.com:3306/xspam"

async def test_mysql_connection():
    """测试MySQL连接"""
    print("🔗 测试MySQL数据库连接...")
    print(f"数据库URL: {MYSQL_URL[:50]}...")
    
    try:
        # 创建引擎
        engine = create_async_engine(
            MYSQL_URL,
            echo=True,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                "charset": "utf8mb4",
                "autocommit": False
            }
        )
        
        # 测试连接
        async with engine.begin() as conn:
            # 测试基本查询
            result = await conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            print(f"✅ 基本连接测试通过: {test_value}")
            
            # 测试数据库信息
            result = await conn.execute(text("SELECT DATABASE() as db_name"))
            db_name = result.scalar()
            print(f"✅ 当前数据库: {db_name}")
            
            # 测试版本
            result = await conn.execute(text("SELECT VERSION() as version"))
            version = result.scalar()
            print(f"✅ MySQL版本: {version}")
            
            # 测试字符集
            result = await conn.execute(text("SELECT @@character_set_database as charset"))
            charset = result.scalar()
            print(f"✅ 数据库字符集: {charset}")
            
        print("🎉 MySQL连接测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ MySQL连接测试失败: {e}")
        return False
    finally:
        try:
            await engine.dispose()
        except:
            pass

async def test_create_tables():
    """测试创建表"""
    print("\n📋 测试创建数据表...")
    
    try:
        # 导入模型
        from app.models.database import Base
        
        engine = create_async_engine(
            MYSQL_URL,
            echo=True,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                "charset": "utf8mb4",
                "autocommit": False
            }
        )
        
        # 创建表
        async with engine.begin() as conn:
            # 删除已存在的表（如果存在）
            await conn.execute(text("DROP TABLE IF EXISTS lp_transactions"))
            await conn.execute(text("DROP TABLE IF EXISTS lp_positions"))
            await conn.execute(text("DROP TABLE IF EXISTS lp_strategies"))
            await conn.execute(text("DROP TABLE IF EXISTS token_prices"))
            await conn.execute(text("DROP TABLE IF EXISTS wallets"))
            
            # 创建新表
            await conn.run_sync(Base.metadata.create_all)
            
        print("✅ 数据表创建成功！")
        
        # 验证表是否创建
        async with engine.begin() as conn:
            result = await conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ 已创建的表: {', '.join(tables)}")
            
        return True
        
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        return False
    finally:
        try:
            await engine.dispose()
        except:
            pass

async def test_insert_data():
    """测试插入数据"""
    print("\n💾 测试插入测试数据...")
    
    try:
        from app.models.database import Wallet, LPPosition
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.orm import sessionmaker
        
        engine = create_async_engine(
            MYSQL_URL,
            echo=False,  # 减少日志输出
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={
                "charset": "utf8mb4",
                "autocommit": False
            }
        )
        
        AsyncSessionLocal = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with AsyncSessionLocal() as session:
            # 创建测试钱包
            test_wallet = Wallet(
                address="0x1234567890123456789012345678901234567890",
                name="测试钱包",
                network="bsc",
                private_key_encrypted="encrypted_test_key"
            )
            
            session.add(test_wallet)
            await session.flush()  # 获取ID但不提交
            
            # 创建测试LP头寸
            test_position = LPPosition(
                wallet_id=test_wallet.id,
                position_id="12345",
                pool_address="0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
                token0_address="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                token1_address="0x55d398326f99059fF775485246999027B3197955",
                token0_symbol="BNB",
                token1_symbol="USDT",
                fee_tier=3000,
                tick_lower=55200,
                tick_upper=58560,
                liquidity="1000000000000000000",
                amount0="100000000000000000",
                amount1="30000000000000000000",
                usd_value=60.0,
                status="active",
                network="bsc"
            )
            
            session.add(test_position)
            await session.commit()
            
        print("✅ 测试数据插入成功！")
        
        # 验证数据
        async with AsyncSessionLocal() as session:
            from sqlalchemy import select
            
            result = await session.execute(select(Wallet))
            wallets = result.scalars().all()
            print(f"✅ 钱包数量: {len(wallets)}")
            
            result = await session.execute(select(LPPosition))
            positions = result.scalars().all()
            print(f"✅ LP头寸数量: {len(positions)}")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ 插入数据失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🚀 MySQL数据库集成测试")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3
    
    # 测试1: 连接测试
    if await test_mysql_connection():
        success_count += 1
    
    # 测试2: 创建表测试
    if await test_create_tables():
        success_count += 1
    
    # 测试3: 插入数据测试
    if await test_insert_data():
        success_count += 1
    
    # 总结
    print("\n" + "=" * 60)
    print("🎯 测试结果总结")
    print("=" * 60)
    print(f"✅ 成功: {success_count}/{total_tests}")
    print(f"❌ 失败: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！MySQL数据库集成成功！")
        print("\n💡 接下来您可以：")
        print("1. 重启OKX钱包LP管理系统")
        print("2. 使用真实的MySQL数据库功能")
        print("3. 所有LP头寸将持久化保存")
    else:
        print("⚠️ 部分测试失败，请检查数据库配置")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 
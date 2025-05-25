#!/usr/bin/env python3
"""
OKX钱包LP管理系统使用示例

本脚本展示如何使用API来:
1. 创建OKX钱包账户
2. 查询钱包余额
3. 创建LP流动性头寸
4. 监控LP头寸状态
5. 批量创建多个LP头寸

使用前请确保:
1. 系统已启动 (python main.py)
2. 已配置OKX API密钥
3. 钱包中有足够的代币余额
"""

import asyncio
import httpx
import json
from typing import Dict, Any

class OKXLPClient:
    """OKX LP管理API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/v1/health")
            return response.json()
    
    async def create_wallet_account(self, wallet_address: str, networks: str = "bsc,ethereum") -> Dict[str, Any]:
        """创建OKX钱包账户"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/wallet/{wallet_address}/account",
                params={"networks": networks}
            )
            return response.json()
    
    async def get_wallet_balance(self, wallet_address: str, token_addresses: list, network: str = "bsc") -> Dict[str, Any]:
        """查询钱包余额"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/wallet/balance",
                json={
                    "wallet_address": wallet_address,
                    "token_addresses": token_addresses,
                    "network": network
                }
            )
            return response.json()
    
    async def create_lp_position(self, position_config: Dict[str, Any]) -> Dict[str, Any]:
        """创建LP流动性头寸"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/lp/create",
                json=position_config
            )
            return response.json()
    
    async def get_lp_positions(self, wallet_address: str) -> Dict[str, Any]:
        """获取LP头寸列表"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/lp/positions/{wallet_address}"
            )
            return response.json()
    
    async def batch_create_lp_positions(self, positions: list) -> Dict[str, Any]:
        """批量创建LP头寸"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/lp/batch-create",
                json={"positions": positions}
            )
            return response.json()
    
    async def get_pool_info(self, token0: str, token1: str, fee_tier: int = 3000, network: str = "bsc") -> Dict[str, Any]:
        """获取流动性池信息"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/pools/info",
                params={
                    "token0": token0,
                    "token1": token1,
                    "fee_tier": fee_tier,
                    "network": network
                }
            )
            return response.json()

async def example_workflow():
    """完整的LP管理工作流程示例"""
    client = OKXLPClient()
    
    # 示例钱包地址 (请替换为真实地址)
    wallet_address = "0x742d35Cc6644C93A5B9Ba20bD40FA0bd5CfDD7C3"
    
    print("🚀 开始OKX钱包LP管理示例流程...")
    
    # 1. 健康检查
    print("\n1️⃣ 系统健康检查...")
    try:
        health = await client.health_check()
        print(f"✅ 系统状态: {health}")
    except Exception as e:
        print(f"❌ 系统连接失败: {e}")
        return
    
    # 2. 创建钱包账户
    print("\n2️⃣ 创建OKX钱包账户...")
    try:
        account_result = await client.create_wallet_account(wallet_address, "bsc,ethereum")
        print(f"✅ 钱包账户创建结果: {account_result}")
    except Exception as e:
        print(f"⚠️  钱包账户创建失败: {e}")
    
    # 3. 查询钱包余额
    print("\n3️⃣ 查询钱包余额...")
    try:
        # BSC网络常用代币地址示例
        token_addresses = [
            "native",  # BNB
            "0x55d398326f99059fF775485246999027B3197955",  # USDT
            "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82"   # CAKE
        ]
        
        balance_result = await client.get_wallet_balance(wallet_address, token_addresses, "bsc")
        print(f"✅ 钱包余额: {balance_result}")
    except Exception as e:
        print(f"⚠️  余额查询失败: {e}")
    
    # 4. 获取流动性池信息
    print("\n4️⃣ 获取PancakeSwap流动性池信息...")
    try:
        # BNB/USDT 池示例
        pool_info = await client.get_pool_info(
            token0="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",  # WBNB
            token1="0x55d398326f99059fF775485246999027B3197955",  # USDT
            fee_tier=3000,  # 0.3%
            network="bsc"
        )
        print(f"✅ 流动性池信息: {pool_info}")
    except Exception as e:
        print(f"⚠️  池信息获取失败: {e}")
    
    # 5. 创建单个LP头寸
    print("\n5️⃣ 创建LP流动性头寸...")
    try:
        lp_config = {
            "wallet_address": wallet_address,
            "token0_symbol": "BNB",
            "token1_symbol": "USDT", 
            "token0_address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",  # WBNB
            "token1_address": "0x55d398326f99059fF775485246999027B3197955",  # USDT
            "amount0_desired": 0.1,  # 0.1 BNB
            "amount1_desired": 30.0,  # 30 USDT
            "price_lower": 250.0,    # 价格下限
            "price_upper": 350.0,    # 价格上限
            "fee_tier": 3000,        # 0.3%费率
            "network": "bsc"
        }
        
        create_result = await client.create_lp_position(lp_config)
        print(f"✅ LP头寸创建结果: {create_result}")
        
        if create_result.get("code") == 200:
            position_id = create_result["data"]["position_id"]
            print(f"📝 LP头寸ID: {position_id}")
            print("💡 下一步: 使用钱包签名交易数据并调用执行接口")
    except Exception as e:
        print(f"⚠️  LP头寸创建失败: {e}")
    
    # 6. 查询现有LP头寸
    print("\n6️⃣ 查询钱包LP头寸...")
    try:
        positions = await client.get_lp_positions(wallet_address)
        print(f"✅ LP头寸列表: {positions}")
    except Exception as e:
        print(f"⚠️  头寸查询失败: {e}")
    
    # 7. 批量创建LP头寸示例
    print("\n7️⃣ 批量创建LP头寸示例...")
    try:
        batch_positions = [
            {
                "wallet_address": wallet_address,
                "token0_symbol": "BNB",
                "token1_symbol": "CAKE",
                "token0_address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "token1_address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                "amount0_desired": 0.05,
                "amount1_desired": 10.0,
                "price_lower": 15.0,
                "price_upper": 25.0,
                "fee_tier": 3000,
                "network": "bsc"
            },
            {
                "wallet_address": wallet_address,
                "token0_symbol": "USDT",
                "token1_symbol": "CAKE",
                "token0_address": "0x55d398326f99059fF775485246999027B3197955",
                "token1_address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
                "amount0_desired": 50.0,
                "amount1_desired": 10.0,
                "price_lower": 4.0,
                "price_upper": 6.0,
                "fee_tier": 3000,
                "network": "bsc"
            }
        ]
        
        batch_result = await client.batch_create_lp_positions(batch_positions)
        print(f"✅ 批量创建结果: {batch_result}")
    except Exception as e:
        print(f"⚠️  批量创建失败: {e}")
    
    print("\n🎉 示例流程完成!")
    print("\n📝 注意事项:")
    print("1. 示例中使用的是测试数据，实际使用请替换为真实的钱包地址和代币信息")
    print("2. 创建LP头寸后需要使用钱包私钥签名交易数据")
    print("3. 签名后调用 /api/v1/lp/execute 接口执行交易")
    print("4. 建议先在测试网络测试功能")

async def example_specific_operations():
    """特定操作示例"""
    client = OKXLPClient()
    
    print("🔧 特定操作示例...")
    
    # 常用代币地址 (BSC)
    token_addresses = {
        "WBNB": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
        "USDT": "0x55d398326f99059fF775485246999027B3197955", 
        "USDC": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
        "CAKE": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
        "BUSD": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56"
    }
    
    print("\n🪙 支持的代币地址 (BSC):")
    for symbol, address in token_addresses.items():
        print(f"  {symbol}: {address}")
    
    # PancakeSwap V3 费率等级说明
    fee_tiers = {
        100: "0.01% - 稳定币对",
        500: "0.05% - 主流币对", 
        3000: "0.3% - 标准费率",
        10000: "1% - 特殊币对"
    }
    
    print("\n💰 PancakeSwap V3 费率等级:")
    for tier, description in fee_tiers.items():
        print(f"  {tier}: {description}")
    
    print("\n📊 价格区间设置建议:")
    print("  - 稳定币对: ±2-5% 区间")
    print("  - 主流币对: ±10-20% 区间") 
    print("  - 波动性大的币对: ±20-50% 区间")
    print("  - 价格区间越窄，资金效率越高，但无常损失风险越大")

if __name__ == "__main__":
    print("=" * 60)
    print("🥞 OKX钱包 + PancakeSwap V3 LP管理系统")
    print("=" * 60)
    
    # 运行完整工作流程示例
    asyncio.run(example_workflow())
    
    print("\n" + "=" * 60)
    
    # 运行特定操作示例
    asyncio.run(example_specific_operations()) 
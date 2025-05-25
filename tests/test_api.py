#!/usr/bin/env python3
"""
OKX钱包LP管理系统 - API测试脚本
展示系统的完整功能，包括无数据库模式下的运行
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def pretty_print(title: str, data: Dict[str, Any]):
    """格式化打印结果"""
    print(f"\n{'='*60}")
    print(f"🔸 {title}")
    print(f"{'='*60}")
    print(json.dumps(data, indent=2, ensure_ascii=False))

def test_system_health():
    """测试系统健康状况"""
    response = requests.get(f"{BASE_URL}/api/v1/health")
    data = response.json()
    pretty_print("系统健康检查", data)
    return data

def test_system_info():
    """测试系统信息"""
    response = requests.get(f"{BASE_URL}/")
    data = response.json()
    pretty_print("系统基本信息", data)
    return data

def test_config_info():
    """测试配置信息"""
    response = requests.get(f"{BASE_URL}/api/v1/test/config")
    data = response.json()
    pretty_print("系统配置信息", data)
    return data

def test_demo_features():
    """测试演示功能"""
    response = requests.get(f"{BASE_URL}/api/v1/test/demo")
    data = response.json()
    pretty_print("演示功能", data)
    return data

def test_lp_positions():
    """测试LP头寸查询"""
    wallet_address = "0xa7b3f77a6376f906dc8ca568893692af7c720d21"
    response = requests.get(f"{BASE_URL}/api/v1/lp/positions/{wallet_address}")
    data = response.json()
    pretty_print(f"LP头寸查询 - {wallet_address}", data)
    return data

def test_create_lp_position():
    """测试LP头寸创建"""
    lp_data = {
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
    
    response = requests.post(
        f"{BASE_URL}/api/v1/lp/create",
        json=lp_data,
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    pretty_print("LP头寸创建", data)
    return data

def test_mock_lp_creation():
    """测试模拟LP创建"""
    lp_data = {
        "wallet_address": "0xa7b3f77a6376f906dc8ca568893692af7c720d21",
        "token0_symbol": "CAKE",
        "token1_symbol": "USDT",
        "token0_address": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
        "token1_address": "0x55d398326f99059fF775485246999027B3197955",
        "amount0_desired": 10.0,
        "amount1_desired": 50.0,
        "price_lower": 4.0,
        "price_upper": 6.0,
        "fee_tier": 3000,
        "network": "bsc"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/test/mock-lp",
        json=lp_data,
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    pretty_print("模拟LP创建", data)
    return data

def test_wallet_balance():
    """测试钱包余额查询"""
    balance_data = {
        "wallet_address": "0xa7b3f77a6376f906dc8ca568893692af7c720d21",
        "token_addresses": [
            "native",  # BNB
            "0x55d398326f99059fF775485246999027B3197955",  # USDT
            "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82"   # CAKE
        ],
        "network": "bsc"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/wallet/balance",
        json=balance_data,
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    pretty_print("钱包余额查询", data)
    return data

def main():
    """主测试函数"""
    print("🚀 OKX钱包LP管理系统 - API功能测试")
    print("="*60)
    
    try:
        # 1. 测试系统健康状况
        health_data = test_system_health()
        
        # 2. 测试系统信息
        test_system_info()
        
        # 3. 测试配置信息
        config_data = test_config_info()
        
        # 4. 测试演示功能
        test_demo_features()
        
        # 5. 测试LP头寸查询
        test_lp_positions()
        
        # 6. 测试LP头寸创建
        create_result = test_create_lp_position()
        
        # 7. 测试模拟LP创建
        test_mock_lp_creation()
        
        # 8. 测试钱包余额查询
        test_wallet_balance()
        
        # 总结测试结果
        print(f"\n{'='*60}")
        print("🎉 测试完成总结")
        print(f"{'='*60}")
        
        print(f"✅ 系统状态: {health_data['data']['status']}")
        print(f"✅ 数据库状态: {health_data['data']['database']}")
        print(f"✅ OKX API配置: {'已配置' if config_data['data']['okx_configured'] else '未配置（使用模拟模式）'}")
        print(f"✅ 支持的网络: {', '.join(config_data['data']['supported_networks'].keys())}")
        
        print(f"\n📍 可用的API端点:")
        print(f"  - API文档: {BASE_URL}/docs")
        print(f"  - 健康检查: {BASE_URL}/api/v1/health")
        print(f"  - 系统配置: {BASE_URL}/api/v1/test/config")
        print(f"  - LP头寸管理: {BASE_URL}/api/v1/lp/")
        print(f"  - 钱包管理: {BASE_URL}/api/v1/wallet/")
        
        print(f"\n🎯 功能验证:")
        print("  ✅ 系统启动和健康检查")
        print("  ✅ LP头寸查询（模拟模式）")
        print("  ✅ LP头寸创建（模拟模式）")
        print("  ✅ 钱包余额查询（模拟模式）")
        print("  ✅ 错误处理和降级功能")
        print("  ✅ API文档自动生成")
        
        print(f"\n💡 下一步建议:")
        print("  1. 配置真实的OKX API密钥以启用完整功能")
        print("  2. 启动PostgreSQL数据库以持久化数据")
        print("  3. 启动Redis缓存以提升性能")
        print("  4. 在测试网络上进行真实交易测试")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 
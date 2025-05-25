from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from loguru import logger
from datetime import datetime

from app.services.lp_manager import LPManager
from app.services.okx_wallet_api import OKXWalletAPI

router = APIRouter()

# Pydantic 模型定义
class CreateLPPositionRequest(BaseModel):
    wallet_address: str
    token0_symbol: str
    token1_symbol: str
    token0_address: str
    token1_address: str
    amount0_desired: float
    amount1_desired: float
    price_lower: float
    price_upper: float
    fee_tier: int = 3000  # 使用整数，3000 = 0.3%
    network: str = "bsc"

class ExecuteLPTransactionRequest(BaseModel):
    position_id: int
    signed_tx: str
    account_id: str

class BatchCreateLPRequest(BaseModel):
    positions: List[CreateLPPositionRequest]

class WalletBalanceRequest(BaseModel):
    wallet_address: str
    token_addresses: List[str]
    network: str = "bsc"

class AutoRebalanceRequest(BaseModel):
    wallet_address: str
    fee_tier: int = 3000  # 费率等级
    price_range_percent: float = 10.0  # 价格范围百分比
    rebalance_threshold: float = 5.0  # 重平衡阈值百分比
    enabled: bool = True

# 依赖注入
def get_lp_manager() -> LPManager:
    return LPManager()

def get_okx_api() -> OKXWalletAPI:
    return OKXWalletAPI()

@router.post("/lp/create", summary="创建LP流动性头寸")
async def create_lp_position(
    request: CreateLPPositionRequest,
    lp_manager: LPManager = Depends(get_lp_manager)
):
    """
    创建LP流动性头寸
    
    - **wallet_address**: 钱包地址
    - **token0_symbol**: 代币0符号 (如: BNB)
    - **token1_symbol**: 代币1符号 (如: USDT)
    - **token0_address**: 代币0合约地址
    - **token1_address**: 代币1合约地址
    - **amount0_desired**: 期望投入的代币0数量
    - **amount1_desired**: 期望投入的代币1数量
    - **price_lower**: 价格区间下限
    - **price_upper**: 价格区间上限
    - **fee_tier**: 费率等级 (100=0.01%, 500=0.05%, 3000=0.3%, 10000=1%)
    - **network**: 网络 (bsc, ethereum, polygon)
    """
    try:
        # 验证费率等级
        valid_fee_tiers = [100, 500, 3000, 10000]
        if request.fee_tier not in valid_fee_tiers:
            raise ValueError(f"无效的费率等级: {request.fee_tier}，支持的费率: {valid_fee_tiers}")
        
        result = await lp_manager.create_lp_position(
            wallet_address=request.wallet_address,
            token0_symbol=request.token0_symbol,
            token1_symbol=request.token1_symbol,
            token0_address=request.token0_address,
            token1_address=request.token1_address,
            amount0_desired=request.amount0_desired,
            amount1_desired=request.amount1_desired,
            price_lower=request.price_lower,
            price_upper=request.price_upper,
            fee_tier=request.fee_tier,
            network=request.network
        )
        return {
            "code": 200,
            "message": "LP头寸创建成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"创建LP头寸API错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/lp/execute", summary="执行LP交易")
async def execute_lp_transaction(
    request: ExecuteLPTransactionRequest,
    lp_manager: LPManager = Depends(get_lp_manager)
):
    """
    执行已签名的LP交易
    
    - **position_id**: LP头寸ID
    - **signed_tx**: 已签名的交易数据
    - **account_id**: OKX账户ID
    """
    try:
        result = await lp_manager.execute_lp_transaction(
            position_id=request.position_id,
            signed_tx=request.signed_tx,
            account_id=request.account_id
        )
        return {
            "code": 200,
            "message": "交易执行成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"执行LP交易API错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/lp/positions/{wallet_address}", summary="获取钱包LP头寸")
async def get_lp_positions(
    wallet_address: str,
    lp_manager: LPManager = Depends(get_lp_manager)
):
    """
    获取指定钱包的所有LP头寸
    
    - **wallet_address**: 钱包地址
    """
    try:
        positions = await lp_manager.get_lp_positions(wallet_address)
        return {
            "code": 200,
            "message": "获取LP头寸成功",
            "data": {
                "wallet_address": wallet_address,
                "positions": positions,
                "total_count": len(positions)
            }
        }
    except Exception as e:
        logger.error(f"获取LP头寸API错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/lp/batch-create", summary="批量创建LP头寸")
async def batch_create_lp_positions(
    request: BatchCreateLPRequest,
    background_tasks: BackgroundTasks,
    lp_manager: LPManager = Depends(get_lp_manager)
):
    """
    批量创建多个LP头寸
    
    - **positions**: LP头寸配置列表
    """
    try:
        # 转换为字典列表
        positions_config = [pos.dict() for pos in request.positions]
        
        # 异步执行批量创建
        background_tasks.add_task(
            lp_manager.create_multiple_lp_positions,
            positions_config
        )
        
        return {
            "code": 200,
            "message": f"已提交批量创建任务，共 {len(positions_config)} 个LP头寸",
            "data": {
                "submitted_count": len(positions_config),
                "status": "processing"
            }
        }
    except Exception as e:
        logger.error(f"批量创建LP头寸API错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/wallet/balance", summary="查询钱包余额")
async def get_wallet_balance(
    request: WalletBalanceRequest,
    okx_api: OKXWalletAPI = Depends(get_okx_api)
):
    """
    查询钱包代币余额
    
    - **wallet_address**: 钱包地址
    - **token_addresses**: 代币合约地址列表 (使用 "native" 表示原生代币)
    - **network**: 网络名称 (bsc, ethereum, polygon)
    """
    try:
        chain_indexes = {
            "ethereum": "1",
            "bsc": "56", 
            "polygon": "137"
        }
        
        if request.network not in chain_indexes:
            raise ValueError(f"不支持的网络: {request.network}，支持的网络: {list(chain_indexes.keys())}")
            
        chain_index = chain_indexes[request.network]
        
        balances = []
        for token_address in request.token_addresses:
            try:
                # 处理原生代币
                actual_token_address = None if token_address == "native" else token_address
                
                balance_result = await okx_api.get_token_balance(
                    chain_index=chain_index,
                    address=request.wallet_address,
                    token_address=actual_token_address
                )
                
                balances.append({
                    "token_address": token_address,
                    "chain_index": chain_index,
                    "balance_result": balance_result,
                    "success": True
                })
                
            except Exception as token_error:
                logger.warning(f"获取代币 {token_address} 余额失败: {token_error}")
                balances.append({
                    "token_address": token_address,
                    "chain_index": chain_index,
                    "error": str(token_error),
                    "success": False
                })
        
        return {
            "code": 200,
            "message": "查询余额完成",
            "data": {
                "wallet_address": request.wallet_address,
                "network": request.network,
                "chain_index": chain_index,
                "balances": balances,
                "success_count": len([b for b in balances if b.get("success", False)]),
                "total_count": len(balances)
            }
        }
    except Exception as e:
        logger.error(f"查询钱包余额API错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/wallet/{wallet_address}/account", summary="创建OKX钱包账户")
async def create_wallet_account(
    wallet_address: str,
    networks: str = "bsc,ethereum",  # 逗号分隔的网络列表
    okx_api: OKXWalletAPI = Depends(get_okx_api)
):
    """
    为钱包地址创建OKX账户
    
    - **wallet_address**: 钱包地址
    - **networks**: 支持的网络，逗号分隔 (如: bsc,ethereum,polygon)
    """
    try:
        chain_indexes = {
            "ethereum": "1",
            "bsc": "56",
            "polygon": "137"
        }
        
        network_list = [n.strip() for n in networks.split(",")]
        addresses = []
        
        for network in network_list:
            if network in chain_indexes:
                addresses.append({
                    "chainIndex": chain_indexes[network],
                    "address": wallet_address
                })
        
        if not addresses:
            raise ValueError("没有有效的网络")
        
        result = await okx_api.create_wallet_account(addresses)
        
        return {
            "code": 200,
            "message": "创建钱包账户成功",
            "data": {
                "wallet_address": wallet_address,
                "networks": network_list,
                "result": result
            }
        }
    except Exception as e:
        logger.error(f"创建钱包账户API错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/monitoring/start", summary="启动LP头寸监控")
async def start_monitoring(
    background_tasks: BackgroundTasks,
    lp_manager: LPManager = Depends(get_lp_manager)
):
    """启动LP头寸监控任务"""
    try:
        background_tasks.add_task(lp_manager.monitor_positions)
        
        return {
            "code": 200,
            "message": "LP头寸监控已启动",
            "data": {
                "status": "monitoring_started"
            }
        }
    except Exception as e:
        logger.error(f"启动监控API错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pools/info", summary="获取PancakeSwap池信息")
async def get_pool_info(
    token0: str,
    token1: str,
    fee_tier: int = 3000,  # 改为int类型，默认3000 = 0.3%
    network: str = "bsc",
    lp_manager: LPManager = Depends(get_lp_manager)
):
    """
    获取PancakeSwap V3流动性池信息
    
    - **token0**: 代币0地址
    - **token1**: 代币1地址
    - **fee_tier**: 费率等级 (100=0.01%, 500=0.05%, 3000=0.3%, 10000=1%)
    - **network**: 网络
    """
    try:
        # 验证费率等级
        valid_fee_tiers = [100, 500, 3000, 10000]
        if fee_tier not in valid_fee_tiers:
            raise ValueError(f"无效的费率等级: {fee_tier}，支持的费率: {valid_fee_tiers}")
        
        pool_address = await lp_manager.pancake_service.get_pool_address(
            token0, token1, fee_tier
        )
        
        return {
            "code": 200,
            "message": "获取池信息成功",
            "data": {
                "pool_address": pool_address,
                "token0": token0,
                "token1": token1,
                "fee_tier": fee_tier,
                "fee_percentage": f"{fee_tier / 10000}%",
                "network": network
            }
        }
    except Exception as e:
        logger.error(f"获取池信息API错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/health", summary="健康检查")
async def health_check():
    """系统健康检查"""
    # 检查数据库连接状态
    db_status = "unknown"
    try:
        from app.models.database import engine
        from sqlalchemy import text
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "disconnected"
    
    return {
        "code": 200,
        "message": "系统运行正常",
        "data": {
            "status": "healthy",
            "version": "1.0.0",
            "database": db_status,
            "features": [
                "🔗 OKX钱包API集成",
                "🥞 PancakeSwap V3 LP管理", 
                "💰 多链支持 (BSC, Ethereum, Polygon)",
                "📊 实时头寸监控" if db_status == "healthy" else "📊 头寸监控 (需要数据库)",
                "⚡ 批量操作",
                "🔄 自动重平衡" if db_status == "healthy" else "🔄 自动重平衡 (需要数据库)"
            ]
        }
    }

@router.get("/test/demo", summary="演示接口")
async def demo_endpoint():
    """演示接口，展示系统能力"""
    return {
        "code": 200,
        "message": "系统演示接口",
        "data": {
            "timestamp": "2025-05-23T13:00:00Z",
            "demo_features": {
                "okx_wallet": {
                    "description": "OKX钱包API集成",
                    "status": "已配置",
                    "capabilities": ["余额查询", "交易签名", "广播交易"]
                },
                "pancakeswap": {
                    "description": "PancakeSwap V3 LP管理",
                    "status": "已集成",
                    "supported_networks": ["BSC", "Ethereum", "Polygon"],
                    "fee_tiers": ["0.01%", "0.05%", "0.3%", "1%"]
                },
                "blockchain": {
                    "description": "区块链交互",
                    "web3_version": "7.12.0",
                    "supported_chains": {
                        "BSC": "56",
                        "Ethereum": "1", 
                        "Polygon": "137"
                    }
                }
            }
        }
    }

@router.get("/test/config", summary="配置信息")
async def config_info():
    """显示系统配置信息"""
    from app.config import settings
    
    return {
        "code": 200,
        "message": "系统配置信息",
        "data": {
            "okx_configured": settings.okx_api_key != "your_okx_api_key_here",
            "supported_networks": settings.supported_networks,
            "contracts": {
                "pancakeswap_v3_factory": settings.pancakeswap_v3_factory,
                "pancakeswap_v3_router": settings.pancakeswap_v3_router,
                "pancakeswap_v3_position_manager": settings.pancakeswap_v3_position_manager
            },
            "lp_settings": {
                "min_liquidity_usd": settings.min_liquidity_usd,
                "max_slippage_percent": settings.max_slippage_percent,
                "default_fee_tier": settings.default_fee_tier,
                "auto_rebalance_enabled": settings.auto_rebalance_enabled
            }
        }
    }

@router.post("/test/mock-lp", summary="模拟LP创建")
async def mock_create_lp(request: CreateLPPositionRequest):
    """模拟LP创建请求（测试用）"""
    return {
        "code": 200,
        "message": "模拟LP头寸创建成功",
        "data": {
            "mock_position_id": 12345,
            "request_data": request.dict(),
            "estimated_gas": "0.002 BNB",
            "estimated_fees": f"{request.fee_tier / 10000}%",
            "price_range": f"{request.price_lower} - {request.price_upper}",
            "note": "这是一个模拟响应，实际创建需要数据库连接"
        }
    }

@router.post("/lp/auto-rebalance/config", summary="配置自动重平衡")
async def configure_auto_rebalance(
    request: AutoRebalanceRequest,
    lp_manager: LPManager = Depends(get_lp_manager)
):
    """
    为指定钱包配置自动重平衡
    
    - **wallet_address**: 钱包地址
    - **fee_tier**: 费率等级 (100=0.01%, 500=0.05%, 3000=0.3%, 10000=1%)
    - **price_range_percent**: 价格范围百分比，影响重平衡的敏感度
    - **rebalance_threshold**: 重平衡阈值百分比，当价格偏离超过此阈值时触发重平衡
    - **enabled**: 是否启用自动重平衡
    """
    try:
        # 验证费率等级
        valid_fee_tiers = [100, 500, 3000, 10000]
        if request.fee_tier not in valid_fee_tiers:
            raise ValueError(f"无效的费率等级: {request.fee_tier}，支持的费率: {valid_fee_tiers}")
        
        config = {
            "fee_tier": request.fee_tier,
            "price_range_percent": request.price_range_percent,
            "rebalance_threshold": request.rebalance_threshold,
            "enabled": request.enabled
        }
        
        result = await lp_manager.start_auto_rebalance(
            wallet_address=request.wallet_address,
            rebalance_config=config
        )
        
        return {
            "code": 200,
            "message": "自动重平衡配置成功",
            "data": result
        }
    except Exception as e:
        logger.error(f"配置自动重平衡API错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/lp/auto-rebalance/status/{wallet_address}", summary="查询自动重平衡状态")
async def get_auto_rebalance_status(
    wallet_address: str,
    lp_manager: LPManager = Depends(get_lp_manager)
):
    """
    查询指定钱包的自动重平衡状态
    
    - **wallet_address**: 钱包地址
    """
    try:
        positions = await lp_manager.get_lp_positions(wallet_address)
        
        # 统计自动重平衡状态
        auto_rebalance_positions = []
        total_positions = len([p for p in positions if not p.get("error")])
        enabled_count = 0
        
        for position in positions:
            if not position.get("error"):
                auto_enabled = position.get("auto_rebalance_enabled", False)
                if auto_enabled:
                    enabled_count += 1
                
                auto_rebalance_positions.append({
                    "position_id": position.get("id"),
                    "token_pair": f"{position.get('token0_symbol')}/{position.get('token1_symbol')}",
                    "fee_tier": position.get("fee_tier"),
                    "auto_rebalance_enabled": auto_enabled,
                    "rebalance_threshold": position.get("rebalance_threshold", 5.0),
                    "status": position.get("status")
                })
        
        return {
            "code": 200,
            "message": "获取自动重平衡状态成功",
            "data": {
                "wallet_address": wallet_address,
                "total_positions": total_positions,
                "auto_rebalance_enabled_count": enabled_count,
                "positions": auto_rebalance_positions,
                "global_auto_rebalance": enabled_count > 0
            }
        }
    except Exception as e:
        logger.error(f"查询自动重平衡状态API错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/lp/positions/{wallet_address}/real-time", summary="获取实时区块链LP头寸")
async def get_real_time_lp_positions(
    wallet_address: str,
    network: str = "bsc",
    lp_manager: LPManager = Depends(get_lp_manager)
):
    """
    直接从区块链获取实时LP头寸数据
    
    - **wallet_address**: 钱包地址
    - **network**: 网络 (bsc, ethereum, polygon)
    """
    try:
        logger.info(f"获取实时LP头寸: {wallet_address} @ {network}")
        
        # 直接从区块链获取数据
        real_positions = await lp_manager.blockchain_reader.get_real_lp_positions(wallet_address, network)
        
        if real_positions:
            formatted_positions = [lp_manager._format_real_position(pos) for pos in real_positions]
            
            return {
                "code": 200,
                "message": f"成功获取 {len(real_positions)} 个实时LP头寸",
                "data": {
                    "wallet_address": wallet_address,
                    "network": network,
                    "positions": formatted_positions,
                    "total_count": len(formatted_positions),
                    "data_source": "blockchain",
                    "real_time": True,
                    "timestamp": f"{datetime.utcnow().isoformat()}Z"
                }
            }
        else:
            return {
                "code": 200,
                "message": "未发现LP头寸",
                "data": {
                    "wallet_address": wallet_address,
                    "network": network,
                    "positions": [],
                    "total_count": 0,
                    "data_source": "blockchain",
                    "real_time": True,
                    "note": "该钱包在PancakeSwap V3中暂无活跃LP头寸",
                    "suggestions": [
                        "检查钱包地址是否正确",
                        "确认在PancakeSwap V3中有LP头寸",
                        "尝试其他网络 (ethereum, polygon)"
                    ]
                }
            }
            
    except Exception as e:
        logger.error(f"获取实时LP头寸API错误: {e}")
        raise HTTPException(status_code=400, detail=str(e)) 
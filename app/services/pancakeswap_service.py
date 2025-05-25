import json
import math
from typing import Dict, List, Optional, Tuple, Any
from web3 import Web3
from web3.contract import Contract
from loguru import logger
from app.config import settings

class PancakeSwapV3Service:
    """PancakeSwap V3 服务类"""
    
    def __init__(self, network: str = "bsc"):
        self.network = network
        self.web3 = self._get_web3_instance()
        self.factory_address = settings.pancakeswap_v3_factory
        self.router_address = settings.pancakeswap_v3_router
        self.position_manager_address = settings.pancakeswap_v3_position_manager
        
        # 加载合约 ABI
        self.factory_contract = self._load_contract(self.factory_address, self._get_factory_abi())
        self.position_manager_contract = self._load_contract(self.position_manager_address, self._get_position_manager_abi())
    
    def _get_web3_instance(self) -> Web3:
        """获取Web3实例"""
        if self.network == "bsc":
            rpc_url = settings.bsc_rpc_url
        elif self.network == "ethereum":
            rpc_url = settings.ethereum_rpc_url
        elif self.network == "polygon":
            rpc_url = settings.polygon_rpc_url
        else:
            raise ValueError(f"不支持的网络: {self.network}")
        
        return Web3(Web3.HTTPProvider(rpc_url))
    
    def _load_contract(self, address: str, abi: List[Dict]) -> Contract:
        """加载智能合约"""
        return self.web3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)
    
    def _get_factory_abi(self) -> List[Dict]:
        """获取Factory合约ABI"""
        return [
            {
                "inputs": [
                    {"internalType": "address", "name": "tokenA", "type": "address"},
                    {"internalType": "address", "name": "tokenB", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"}
                ],
                "name": "getPool",
                "outputs": [{"internalType": "address", "name": "pool", "type": "address"}],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def _get_position_manager_abi(self) -> List[Dict]:
        """获取Position Manager合约ABI（简化版）"""
        return [
            {
                "inputs": [
                    {
                        "components": [
                            {"internalType": "address", "name": "token0", "type": "address"},
                            {"internalType": "address", "name": "token1", "type": "address"},
                            {"internalType": "uint24", "name": "fee", "type": "uint24"},
                            {"internalType": "int24", "name": "tickLower", "type": "int24"},
                            {"internalType": "int24", "name": "tickUpper", "type": "int24"},
                            {"internalType": "uint256", "name": "amount0Desired", "type": "uint256"},
                            {"internalType": "uint256", "name": "amount1Desired", "type": "uint256"},
                            {"internalType": "uint256", "name": "amount0Min", "type": "uint256"},
                            {"internalType": "uint256", "name": "amount1Min", "type": "uint256"},
                            {"internalType": "address", "name": "recipient", "type": "address"},
                            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                        ],
                        "internalType": "struct INonfungiblePositionManager.MintParams",
                        "name": "params",
                        "type": "tuple"
                    }
                ],
                "name": "mint",
                "outputs": [
                    {"internalType": "uint256", "name": "tokenId", "type": "uint256"},
                    {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
                    {"internalType": "uint256", "name": "amount0", "type": "uint256"},
                    {"internalType": "uint256", "name": "amount1", "type": "uint256"}
                ],
                "stateMutability": "payable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
                "name": "positions",
                "outputs": [
                    {"internalType": "uint96", "name": "nonce", "type": "uint96"},
                    {"internalType": "address", "name": "operator", "type": "address"},
                    {"internalType": "address", "name": "token0", "type": "address"},
                    {"internalType": "address", "name": "token1", "type": "address"},
                    {"internalType": "uint24", "name": "fee", "type": "uint24"},
                    {"internalType": "int24", "name": "tickLower", "type": "int24"},
                    {"internalType": "int24", "name": "tickUpper", "type": "int24"},
                    {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
                    {"internalType": "uint256", "name": "feeGrowthInside0LastX128", "type": "uint256"},
                    {"internalType": "uint256", "name": "feeGrowthInside1LastX128", "type": "uint256"},
                    {"internalType": "uint128", "name": "tokensOwed0", "type": "uint128"},
                    {"internalType": "uint128", "name": "tokensOwed1", "type": "uint128"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    async def get_pool_address(self, token0: str, token1: str, fee_tier: int) -> str:
        """获取流动性池地址"""
        try:
            pool_address = self.factory_contract.functions.getPool(
                Web3.to_checksum_address(token0),
                Web3.to_checksum_address(token1),
                fee_tier
            ).call()
            
            if pool_address == "0x0000000000000000000000000000000000000000":
                raise ValueError(f"不存在 {token0}/{token1} 费率 {fee_tier} 的流动性池")
            
            return pool_address
        except Exception as e:
            logger.error(f"获取流动性池地址失败: {e}")
            raise
    
    def calculate_tick_from_price(self, price: float) -> int:
        """根据价格计算tick值"""
        # tick = log(price) / log(1.0001)
        tick = math.log(price) / math.log(1.0001)
        return int(tick)
    
    def calculate_price_from_tick(self, tick: int) -> float:
        """根据tick值计算价格"""
        # price = 1.0001^tick
        return 1.0001 ** tick
    
    def get_tick_spacing(self, fee_tier: int) -> int:
        """获取tick间距"""
        tick_spacings = {
            100: 1,      # 0.01%
            500: 10,     # 0.05%
            3000: 60,    # 0.3%
            10000: 200   # 1%
        }
        return tick_spacings.get(fee_tier, 60)
    
    def align_tick_to_spacing(self, tick: int, fee_tier: int) -> int:
        """将tick对齐到间距"""
        spacing = self.get_tick_spacing(fee_tier)
        return int(tick / spacing) * spacing
    
    async def create_lp_position_data(self, 
                                    token0: str, 
                                    token1: str, 
                                    fee_tier: int,
                                    amount0: int, 
                                    amount1: int,
                                    price_lower: float, 
                                    price_upper: float,
                                    recipient: str,
                                    deadline: int) -> Dict[str, Any]:
        """创建LP流动性头寸的交易数据
        
        Args:
            token0: 代币0地址
            token1: 代币1地址
            fee_tier: 费率等级 (100, 500, 3000, 10000)
            amount0: 代币0数量
            amount1: 代币1数量
            price_lower: 价格下限
            price_upper: 价格上限
            recipient: 接收地址
            deadline: 交易截止时间
        """
        try:
            # 计算tick范围
            tick_lower = self.calculate_tick_from_price(price_lower)
            tick_upper = self.calculate_tick_from_price(price_upper)
            
            # 对齐tick到间距
            tick_lower = self.align_tick_to_spacing(tick_lower, fee_tier)
            tick_upper = self.align_tick_to_spacing(tick_upper, fee_tier)
            
            # 确保token0 < token1 (按字典序排列)
            if token0.lower() > token1.lower():
                token0, token1 = token1, token0
                amount0, amount1 = amount1, amount0
            
            # 构建mint参数
            mint_params = {
                'token0': Web3.to_checksum_address(token0),
                'token1': Web3.to_checksum_address(token1),
                'fee': fee_tier,
                'tickLower': tick_lower,
                'tickUpper': tick_upper,
                'amount0Desired': amount0,
                'amount1Desired': amount1,
                'amount0Min': int(amount0 * 0.95),  # 5% 滑点保护
                'amount1Min': int(amount1 * 0.95),  # 5% 滑点保护
                'recipient': Web3.to_checksum_address(recipient),
                'deadline': deadline
            }
            
            # 构建交易数据
            function = self.position_manager_contract.functions.mint(mint_params)
            transaction_data = function.build_transaction({
                'from': Web3.to_checksum_address(recipient),
                'gas': 500000,  # 预估gas
                'gasPrice': self.web3.eth.gas_price,
                'nonce': self.web3.eth.get_transaction_count(Web3.to_checksum_address(recipient))
            })
            
            return {
                'to': self.position_manager_address,
                'data': transaction_data['data'],
                'value': transaction_data.get('value', 0),
                'gas': transaction_data['gas'],
                'gasPrice': transaction_data['gasPrice'],
                'nonce': transaction_data['nonce'],
                'mint_params': mint_params
            }
            
        except Exception as e:
            logger.error(f"创建LP头寸交易数据失败: {e}")
            raise
    
    async def get_position_info(self, token_id: int) -> Dict[str, Any]:
        """获取LP头寸信息
        
        Args:
            token_id: NFT Token ID
        """
        try:
            position_info = self.position_manager_contract.functions.positions(token_id).call()
            
            return {
                'nonce': position_info[0],
                'operator': position_info[1],
                'token0': position_info[2],
                'token1': position_info[3],
                'fee': position_info[4],
                'tickLower': position_info[5],
                'tickUpper': position_info[6],
                'liquidity': position_info[7],
                'feeGrowthInside0LastX128': position_info[8],
                'feeGrowthInside1LastX128': position_info[9],
                'tokensOwed0': position_info[10],
                'tokensOwed1': position_info[11]
            }
        except Exception as e:
            logger.error(f"获取LP头寸信息失败: {e}")
            raise
    
    async def estimate_lp_amounts(self, 
                                token0_address: str, 
                                token1_address: str, 
                                fee_tier: int,
                                amount0_desired: int, 
                                amount1_desired: int,
                                price_lower: float, 
                                price_upper: float) -> Dict[str, int]:
        """估算实际需要的代币数量
        
        Args:
            token0_address: 代币0地址
            token1_address: 代币1地址
            fee_tier: 费率等级
            amount0_desired: 期望的代币0数量
            amount1_desired: 期望的代币1数量
            price_lower: 价格下限
            price_upper: 价格上限
        """
        try:
            # 获取当前池价格（简化计算，实际需要从池子获取）
            # 这里为演示目的，使用简化的计算方法
            
            # 计算tick范围
            tick_lower = self.align_tick_to_spacing(
                self.calculate_tick_from_price(price_lower), fee_tier
            )
            tick_upper = self.align_tick_to_spacing(
                self.calculate_tick_from_price(price_upper), fee_tier
            )
            
            # 简化的流动性计算（实际应用中需要更精确的计算）
            price_current = (price_lower + price_upper) / 2  # 简化假设当前价格在中间
            
            # 根据当前价格和范围计算实际需要的代币数量
            if price_current <= price_lower:
                # 只需要 token0
                amount0_actual = amount0_desired
                amount1_actual = 0
            elif price_current >= price_upper:
                # 只需要 token1
                amount0_actual = 0
                amount1_actual = amount1_desired
            else:
                # 需要两种代币，按比例计算
                ratio = (price_current - price_lower) / (price_upper - price_lower)
                amount0_actual = int(amount0_desired * (1 - ratio))
                amount1_actual = int(amount1_desired * ratio)
            
            return {
                'amount0': amount0_actual,
                'amount1': amount1_actual,
                'tick_lower': tick_lower,
                'tick_upper': tick_upper
            }
        except Exception as e:
            logger.error(f"估算LP数量失败: {e}")
            raise
    
    async def calculate_fees_earned(self, token_id: int) -> Dict[str, int]:
        """计算已赚取的手续费
        
        Args:
            token_id: NFT Token ID
        """
        try:
            position_info = await self.get_position_info(token_id)
            
            # 这里简化了手续费计算，实际需要更复杂的链上计算
            fees_token0 = position_info['tokensOwed0']
            fees_token1 = position_info['tokensOwed1']
            
            return {
                'fees_token0': fees_token0,
                'fees_token1': fees_token1
            }
        except Exception as e:
            logger.error(f"计算手续费失败: {e}")
            raise
    
    def is_position_in_range(self, position_info: Dict[str, Any], current_tick: int) -> bool:
        """判断头寸是否在价格范围内"""
        return position_info['tickLower'] <= current_tick <= position_info['tickUpper'] 
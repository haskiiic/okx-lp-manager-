"""
区块链数据读取服务
直接从区块链获取LP头寸数据，不依赖中心化API
"""
from typing import Dict, List, Any, Optional
from web3 import Web3
from loguru import logger
import asyncio
import aiohttp
import json

class BlockchainReader:
    """区块链数据读取器"""
    
    def __init__(self):
        # BSC网络配置
        self.networks = {
            "bsc": {
                "rpc": "https://bsc-dataseed1.binance.org/",
                "chain_id": 56,
                "pancake_factory": "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865",
                "pancake_position_manager": "0x46A15B0b27311cedF172AB29E4f4766fbE7F4364"
            },
            "ethereum": {
                "rpc": "https://eth.llamarpc.com",
                "chain_id": 1,
                "uniswap_factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
                "uniswap_position_manager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88"
            }
        }
        
        # 初始化Web3连接
        self.w3_connections = {}
        for network, config in self.networks.items():
            try:
                w3 = Web3(Web3.HTTPProvider(config["rpc"]))
                if w3.is_connected():
                    self.w3_connections[network] = w3
                    logger.info(f"✅ {network.upper()} 区块链连接成功")
                else:
                    logger.warning(f"⚠️ {network.upper()} 区块链连接失败")
            except Exception as e:
                logger.error(f"❌ {network.upper()} 区块链连接错误: {e}")
    
    async def get_real_lp_positions(self, wallet_address: str, network: str = "bsc") -> List[Dict[str, Any]]:
        """获取钱包的真实LP头寸数据"""
        try:
            if network not in self.w3_connections:
                raise ValueError(f"不支持的网络: {network}")
            
            w3 = self.w3_connections[network]
            
            # 获取钱包地址的标准格式
            wallet_address = w3.to_checksum_address(wallet_address)
            
            # 1. 获取钱包在PancakeSwap V3中的LP NFT代币
            positions = await self._get_nft_positions(wallet_address, network)
            
            # 2. 获取每个位置的详细信息
            detailed_positions = []
            for position in positions:
                try:
                    detail = await self._get_position_details(position, network)
                    detailed_positions.append(detail)
                except Exception as e:
                    logger.warning(f"获取位置详情失败: {position}, {e}")
            
            return detailed_positions
            
        except Exception as e:
            logger.error(f"获取真实LP头寸失败: {e}")
            return []
    
    async def _get_nft_positions(self, wallet_address: str, network: str) -> List[int]:
        """获取钱包的LP NFT位置ID"""
        try:
            w3 = self.w3_connections[network]
            config = self.networks[network]
            
            # PancakeSwap V3 Position Manager ABI (简化版)
            position_manager_abi = [
                {
                    "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                },
                {
                    "inputs": [
                        {"internalType": "address", "name": "owner", "type": "address"},
                        {"internalType": "uint256", "name": "index", "type": "uint256"}
                    ],
                    "name": "tokenOfOwnerByIndex",
                    "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
            
            # 创建合约实例
            if network == "bsc":
                contract_address = config["pancake_position_manager"]
            else:
                contract_address = config["uniswap_position_manager"]
                
            contract = w3.eth.contract(
                address=w3.to_checksum_address(contract_address),
                abi=position_manager_abi
            )
            
            # 获取钱包拥有的LP NFT数量
            balance = contract.functions.balanceOf(wallet_address).call()
            logger.info(f"钱包 {wallet_address} 拥有 {balance} 个LP NFT")
            
            # 获取所有位置ID
            position_ids = []
            for i in range(balance):
                try:
                    token_id = contract.functions.tokenOfOwnerByIndex(wallet_address, i).call()
                    position_ids.append(token_id)
                except Exception as e:
                    logger.warning(f"获取位置ID失败 (索引{i}): {e}")
            
            return position_ids
            
        except Exception as e:
            logger.error(f"获取NFT位置失败: {e}")
            return []
    
    async def _get_position_details(self, token_id: int, network: str) -> Dict[str, Any]:
        """获取单个LP位置的详细信息"""
        try:
            w3 = self.w3_connections[network]
            config = self.networks[network]
            
            # Position Manager的positions函数ABI
            position_abi = [
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
            
            # 创建合约实例
            if network == "bsc":
                contract_address = config["pancake_position_manager"]
            else:
                contract_address = config["uniswap_position_manager"]
                
            contract = w3.eth.contract(
                address=w3.to_checksum_address(contract_address),
                abi=position_abi
            )
            
            # 调用positions函数获取位置信息
            position_data = contract.functions.positions(token_id).call()
            
            # 解析数据
            (nonce, operator, token0, token1, fee, tick_lower, tick_upper, 
             liquidity, fee_growth_0, fee_growth_1, tokens_owed_0, tokens_owed_1) = position_data
            
            # 获取代币符号
            token0_symbol = await self._get_token_symbol(token0, network)
            token1_symbol = await self._get_token_symbol(token1, network)
            
            # 计算价格范围
            price_lower = 1.0001 ** tick_lower
            price_upper = 1.0001 ** tick_upper
            
            return {
                "token_id": token_id,
                "token0_address": token0,
                "token1_address": token1,
                "token0_symbol": token0_symbol,
                "token1_symbol": token1_symbol,
                "fee_tier": fee,
                "fee_percentage": f"{fee / 10000}%",
                "tick_lower": tick_lower,
                "tick_upper": tick_upper,
                "price_lower": price_lower,
                "price_upper": price_upper,
                "liquidity": str(liquidity),
                "tokens_owed_0": str(tokens_owed_0),
                "tokens_owed_1": str(tokens_owed_1),
                "status": "active" if liquidity > 0 else "closed",
                "network": network,
                "source": "blockchain",
                "real_time": True
            }
            
        except Exception as e:
            logger.error(f"获取位置详情失败: {e}")
            raise
    
    async def _get_token_symbol(self, token_address: str, network: str) -> str:
        """获取代币符号"""
        try:
            w3 = self.w3_connections[network]
            
            # ERC20 token symbol ABI
            token_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "symbol",
                    "outputs": [{"name": "", "type": "string"}],
                    "type": "function"
                }
            ]
            
            contract = w3.eth.contract(
                address=w3.to_checksum_address(token_address),
                abi=token_abi
            )
            
            symbol = contract.functions.symbol().call()
            return symbol
            
        except Exception as e:
            logger.warning(f"获取代币符号失败 {token_address}: {e}")
            
            # 常见代币地址映射（BSC）
            known_tokens = {
                "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c": "WBNB",
                "0x55d398326f99059fF775485246999027B3197955": "USDT",
                "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56": "BUSD",
                "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d": "USDC",
                "0x2170Ed0880ac9A755fd29B2688956BD959F933F8": "ETH"
            }
            
            return known_tokens.get(token_address, f"Token_{token_address[:6]}")
    
    async def get_token_price(self, token_address: str, network: str = "bsc") -> float:
        """获取代币价格（使用DEX价格）"""
        try:
            # 这里可以集成价格API，比如CoinGecko或者直接从DEX获取
            # 暂时返回模拟价格
            prices = {
                "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c": 300.0,  # WBNB
                "0x55d398326f99059fF775485246999027B3197955": 1.0,    # USDT
                "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56": 1.0,    # BUSD
                "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d": 1.0,    # USDC
                "0x2170Ed0880ac9A755fd29B2688956BD959F933F8": 2000.0  # ETH
            }
            
            return prices.get(token_address, 1.0)
            
        except Exception as e:
            logger.error(f"获取代币价格失败: {e}")
            return 1.0 
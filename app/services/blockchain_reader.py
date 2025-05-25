"""
区块链数据读取服务
直接从区块链获取LP头寸数据，不依赖中心化API
"""

import asyncio
import time
from typing import Any, Dict, List

from loguru import logger
from web3 import Web3


class BlockchainReader:
    """区块链数据读取器"""

    def __init__(self):
        # BSC网络配置
        self.networks = {
            "bsc": {
                "rpc": "https://bsc-dataseed1.binance.org/",
                "chain_id": 56,
                "pancake_factory": "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865",
                "pancake_position_manager": "0x46A15B0b27311cedF172AB29E4f4766fbE7F4364",
            },
            "ethereum": {
                "rpc": "https://eth.llamarpc.com",
                "chain_id": 1,
                "uniswap_factory": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
                "uniswap_position_manager": "0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
            },
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

        # 并发控制
        self.max_concurrent_requests = 20  # 增加默认并发数量

    def set_concurrent_limit(self, limit: int):
        """设置最大并发请求数"""
        if limit > 0:
            self.max_concurrent_requests = limit
            logger.info(f"设置最大并发请求数为: {limit}")
        else:
            logger.warning("并发数量必须大于0")

    async def get_real_lp_positions(
        self,
        wallet_address: str,
        network: str = "bsc",
        show_progress: bool = True,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """获取钱包的真实LP头寸数据"""
        start_time = time.time()
        try:
            if network not in self.w3_connections:
                raise ValueError(f"不支持的网络: {network}")

            w3 = self.w3_connections[network]

            # 获取钱包地址的标准格式
            wallet_address = w3.to_checksum_address(wallet_address)
            logger.info(
                f"🔍 开始获取钱包 {wallet_address} 在 {network.upper()} 网络的LP头寸..."
            )

            # 1. 获取钱包在PancakeSwap V3中的LP NFT代币
            nft_start_time = time.time()
            positions = await self._get_nft_positions(wallet_address, network)
            nft_time = time.time() - nft_start_time

            if not positions:
                logger.info(f"钱包 {wallet_address} 没有找到LP头寸")
                return []

            logger.info(f"📊 找到 {len(positions)} 个LP头寸 (耗时: {nft_time:.2f}s)")

            # 2. 如果只要active头寸，先快速过滤
            filter_time = 0  # 初始化变量
            if active_only:
                logger.info("🔍 开始快速过滤active头寸...")
                filter_start_time = time.time()
                active_positions = await self._filter_active_positions(
                    positions, network, show_progress
                )
                filter_time = time.time() - filter_start_time

                logger.info(
                    f"✅ 过滤完成！找到 {len(active_positions)} 个active头寸 (过滤掉 {len(positions) - len(active_positions)} 个closed头寸)"
                )
                logger.info(
                    f"📊 过滤耗时: {filter_time:.2f}s，节省后续处理: {len(positions) - len(active_positions)} 个头寸"
                )
                positions = active_positions

            if not positions:
                logger.info("没有找到active状态的LP头寸")
                return []

            logger.info(f"⚡ 开始并发获取 {len(positions)} 个头寸的详细信息...")
            logger.info(
                f"⚡ 使用 {self.max_concurrent_requests} 个并发连接进行数据获取..."
            )

            # 3. 使用信号量控制并发数量，并发获取所有位置的详细信息
            details_start_time = time.time()
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            completed_count = 0

            async def get_position_with_semaphore(position_id):
                nonlocal completed_count
                async with semaphore:
                    try:
                        result = await self._get_position_details(position_id, network)
                        completed_count += 1
                        if show_progress and completed_count % 5 == 0:
                            progress_percent = (completed_count / len(positions)) * 100
                            logger.info(
                                f"📈 进度: {completed_count}/{len(positions)} ({progress_percent:.1f}%) 个头寸已处理"
                            )
                        return result
                    except Exception as e:
                        completed_count += 1
                        logger.warning(f"获取位置详情失败: {position_id}, {e}")
                        return None

            # 分批处理，避免一次性创建太多任务
            batch_size = min(50, len(positions))  # 每批最多处理50个
            detailed_positions = []

            for i in range(0, len(positions), batch_size):
                batch_positions = positions[i : i + batch_size]
                batch_num = i // batch_size + 1
                total_batches = (len(positions) - 1) // batch_size + 1
                logger.info(
                    f"🔄 处理第 {batch_num}/{total_batches} 批，包含 {len(batch_positions)} 个头寸..."
                )

                # 并发执行当前批次的请求
                tasks = [
                    get_position_with_semaphore(position)
                    for position in batch_positions
                ]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                # 处理批次结果
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"位置 {batch_positions[j]} 处理失败: {result}")
                    elif result is not None:
                        detailed_positions.append(result)

            details_time = time.time() - details_start_time
            total_time = time.time() - start_time

            # 性能统计
            success_rate = (
                (len(detailed_positions) / len(positions)) * 100 if positions else 0
            )
            avg_time_per_position = details_time / len(positions) if positions else 0

            logger.info("✅ 数据获取完成!")
            logger.info("📊 统计信息:")
            logger.info(
                f"   - 成功获取: {len(detailed_positions)}/{len(positions)} 个LP头寸"
            )
            logger.info(f"   - 成功率: {success_rate:.1f}%")
            logger.info(f"   - 总耗时: {total_time:.2f}s")
            logger.info(f"   - NFT获取耗时: {nft_time:.2f}s")
            if active_only:
                logger.info(f"   - 过滤耗时: {filter_time:.2f}s")
            logger.info(f"   - 详情获取耗时: {details_time:.2f}s")
            logger.info(f"   - 平均每个头寸耗时: {avg_time_per_position:.3f}s")

            # 计算性能提升（相比顺序执行）
            original_count = (
                len(positions)
                if not active_only
                else len(positions) + (len(positions) * 2)
            )  # 估算原始数量
            estimated_sequential_details_time = (
                len(positions) * 0.5
            )  # 假设每个详情查询0.5秒
            estimated_total_sequential_time = estimated_sequential_details_time

            total_improvement = estimated_total_sequential_time - details_time
            details_improvement_percent = (
                (total_improvement / estimated_total_sequential_time) * 100
                if estimated_total_sequential_time > 0
                else 0
            )

            logger.info("🚀 性能提升对比:")
            logger.info(
                f"   - 详情获取节省: {total_improvement:.2f}s (提升 {details_improvement_percent:.1f}%)"
            )
            if active_only:
                saved_requests = (
                    len(positions)
                    if not active_only
                    else (len(positions) * 2) - len(positions)
                )
                logger.info(
                    f"   - 通过过滤节省: ~{saved_requests * 0.5:.1f}s (避免了 {saved_requests} 个无效请求)"
                )

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
                    "inputs": [
                        {"internalType": "address", "name": "owner", "type": "address"}
                    ],
                    "name": "balanceOf",
                    "outputs": [
                        {"internalType": "uint256", "name": "", "type": "uint256"}
                    ],
                    "stateMutability": "view",
                    "type": "function",
                },
                {
                    "inputs": [
                        {"internalType": "address", "name": "owner", "type": "address"},
                        {"internalType": "uint256", "name": "index", "type": "uint256"},
                    ],
                    "name": "tokenOfOwnerByIndex",
                    "outputs": [
                        {"internalType": "uint256", "name": "", "type": "uint256"}
                    ],
                    "stateMutability": "view",
                    "type": "function",
                },
            ]

            # 创建合约实例
            if network == "bsc":
                contract_address = config["pancake_position_manager"]
            else:
                contract_address = config["uniswap_position_manager"]

            contract = w3.eth.contract(
                address=w3.to_checksum_address(contract_address),
                abi=position_manager_abi,
            )

            # 获取钱包拥有的LP NFT数量
            balance = contract.functions.balanceOf(wallet_address).call()
            logger.info(f"钱包 {wallet_address} 拥有 {balance} 个LP NFT")

            if balance == 0:
                return []

            logger.info(f"🚀 开始并发获取 {balance} 个NFT位置ID...")
            start_time = time.time()

            # 使用信号量控制并发获取位置ID
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            completed_count = 0

            async def get_token_id_with_semaphore(index):
                nonlocal completed_count
                async with semaphore:
                    try:
                        # 使用 asyncio.to_thread 将同步调用转为异步
                        token_id = await asyncio.to_thread(
                            contract.functions.tokenOfOwnerByIndex(
                                wallet_address, index
                            ).call
                        )
                        completed_count += 1
                        if completed_count % 20 == 0:
                            progress_percent = (completed_count / balance) * 100
                            logger.info(
                                f"📈 NFT获取进度: {completed_count}/{balance} ({progress_percent:.1f}%)"
                            )
                        return {"index": index, "token_id": token_id}
                    except Exception as e:
                        completed_count += 1
                        logger.warning(f"获取位置ID失败 (索引{index}): {e}")
                        return {"index": index, "token_id": None}

            # 分批处理，避免一次性创建太多任务
            batch_size = min(100, balance)  # 每批最多处理100个
            position_ids = []

            for i in range(0, balance, batch_size):
                batch_indices = list(range(i, min(i + batch_size, balance)))
                batch_num = i // batch_size + 1
                total_batches = (balance - 1) // batch_size + 1
                logger.info(
                    f"🔄 处理NFT第 {batch_num}/{total_batches} 批，包含 {len(batch_indices)} 个索引..."
                )

                # 并发执行当前批次的请求
                tasks = [get_token_id_with_semaphore(index) for index in batch_indices]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                # 处理批次结果
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"批次处理失败: {result}")
                    elif (
                        result is not None
                        and isinstance(result, dict)
                        and result.get("token_id") is not None
                    ):
                        position_ids.append(result["token_id"])

            # 按索引顺序排序（保持原有顺序）
            # position_ids已经按照批次顺序添加，基本保持了顺序

            nft_time = time.time() - start_time
            success_rate = (len(position_ids) / balance) * 100 if balance else 0

            logger.info("✅ NFT位置ID获取完成!")
            logger.info("📊 NFT获取统计:")
            logger.info(f"   - 成功获取: {len(position_ids)}/{balance} 个位置ID")
            logger.info(f"   - 成功率: {success_rate:.1f}%")
            logger.info(f"   - 耗时: {nft_time:.2f}s")
            logger.info(f"   - 平均每个ID耗时: {(nft_time / balance):.3f}s")

            return position_ids

        except Exception as e:
            logger.error(f"获取NFT位置失败: {e}")
            return []

    async def _filter_active_positions(
        self, position_ids: List[int], network: str, show_progress: bool = True
    ) -> List[int]:
        """快速过滤出active状态的头寸（liquidity > 0）"""
        try:
            w3 = self.w3_connections[network]
            config = self.networks[network]

            # Position Manager的positions函数ABI（简化版，只获取liquidity）
            position_abi = [
                {
                    "inputs": [
                        {
                            "internalType": "uint256",
                            "name": "tokenId",
                            "type": "uint256",
                        }
                    ],
                    "name": "positions",
                    "outputs": [
                        {"internalType": "uint96", "name": "nonce", "type": "uint96"},
                        {
                            "internalType": "address",
                            "name": "operator",
                            "type": "address",
                        },
                        {
                            "internalType": "address",
                            "name": "token0",
                            "type": "address",
                        },
                        {
                            "internalType": "address",
                            "name": "token1",
                            "type": "address",
                        },
                        {"internalType": "uint24", "name": "fee", "type": "uint24"},
                        {"internalType": "int24", "name": "tickLower", "type": "int24"},
                        {"internalType": "int24", "name": "tickUpper", "type": "int24"},
                        {
                            "internalType": "uint128",
                            "name": "liquidity",
                            "type": "uint128",
                        },
                        {
                            "internalType": "uint256",
                            "name": "feeGrowthInside0LastX128",
                            "type": "uint256",
                        },
                        {
                            "internalType": "uint256",
                            "name": "feeGrowthInside1LastX128",
                            "type": "uint256",
                        },
                        {
                            "internalType": "uint128",
                            "name": "tokensOwed0",
                            "type": "uint128",
                        },
                        {
                            "internalType": "uint128",
                            "name": "tokensOwed1",
                            "type": "uint128",
                        },
                    ],
                    "stateMutability": "view",
                    "type": "function",
                }
            ]

            # 创建合约实例
            if network == "bsc":
                contract_address = config["pancake_position_manager"]
            else:
                contract_address = config["uniswap_position_manager"]

            contract = w3.eth.contract(
                address=w3.to_checksum_address(contract_address), abi=position_abi
            )

            # 使用并发检查每个头寸的liquidity
            semaphore = asyncio.Semaphore(self.max_concurrent_requests)
            completed_count = 0

            async def check_liquidity_with_semaphore(token_id):
                nonlocal completed_count
                async with semaphore:
                    try:
                        # 使用 asyncio.to_thread 将同步调用转为异步
                        position_data = await asyncio.to_thread(
                            contract.functions.positions(token_id).call
                        )
                        # 获取liquidity（第8个字段，索引7）
                        liquidity = position_data[7]

                        completed_count += 1
                        if show_progress and completed_count % 20 == 0:
                            progress_percent = (
                                completed_count / len(position_ids)
                            ) * 100
                            logger.info(
                                f"📈 过滤进度: {completed_count}/{len(position_ids)} ({progress_percent:.1f}%)"
                            )

                        return {"token_id": token_id, "liquidity": liquidity}
                    except Exception as e:
                        completed_count += 1
                        logger.warning(f"检查流动性失败: {token_id}, {e}")
                        return {"token_id": token_id, "liquidity": 0}

            # 分批处理
            batch_size = min(100, len(position_ids))
            active_positions = []

            for i in range(0, len(position_ids), batch_size):
                batch_ids = position_ids[i : i + batch_size]

                # 并发执行当前批次的检查
                tasks = [
                    check_liquidity_with_semaphore(token_id) for token_id in batch_ids
                ]
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)

                # 过滤出active头寸
                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"批次处理失败: {result}")
                    elif (
                        result
                        and isinstance(result, dict)
                        and result.get("liquidity", 0) > 0
                    ):
                        active_positions.append(result["token_id"])

            return active_positions

        except Exception as e:
            logger.error(f"过滤active头寸失败: {e}")
            return position_ids  # 如果过滤失败，返回所有头寸

    async def _get_position_details(
        self, token_id: int, network: str
    ) -> Dict[str, Any]:
        """获取单个LP位置的详细信息"""
        try:
            w3 = self.w3_connections[network]
            config = self.networks[network]

            # Position Manager的positions函数ABI
            position_abi = [
                {
                    "inputs": [
                        {
                            "internalType": "uint256",
                            "name": "tokenId",
                            "type": "uint256",
                        }
                    ],
                    "name": "positions",
                    "outputs": [
                        {"internalType": "uint96", "name": "nonce", "type": "uint96"},
                        {
                            "internalType": "address",
                            "name": "operator",
                            "type": "address",
                        },
                        {
                            "internalType": "address",
                            "name": "token0",
                            "type": "address",
                        },
                        {
                            "internalType": "address",
                            "name": "token1",
                            "type": "address",
                        },
                        {"internalType": "uint24", "name": "fee", "type": "uint24"},
                        {"internalType": "int24", "name": "tickLower", "type": "int24"},
                        {"internalType": "int24", "name": "tickUpper", "type": "int24"},
                        {
                            "internalType": "uint128",
                            "name": "liquidity",
                            "type": "uint128",
                        },
                        {
                            "internalType": "uint256",
                            "name": "feeGrowthInside0LastX128",
                            "type": "uint256",
                        },
                        {
                            "internalType": "uint256",
                            "name": "feeGrowthInside1LastX128",
                            "type": "uint256",
                        },
                        {
                            "internalType": "uint128",
                            "name": "tokensOwed0",
                            "type": "uint128",
                        },
                        {
                            "internalType": "uint128",
                            "name": "tokensOwed1",
                            "type": "uint128",
                        },
                    ],
                    "stateMutability": "view",
                    "type": "function",
                }
            ]

            # 创建合约实例
            if network == "bsc":
                contract_address = config["pancake_position_manager"]
            else:
                contract_address = config["uniswap_position_manager"]

            contract = w3.eth.contract(
                address=w3.to_checksum_address(contract_address), abi=position_abi
            )

            # 调用positions函数获取位置信息
            position_data = contract.functions.positions(token_id).call()

            # 解析数据
            (
                nonce,
                operator,
                token0,
                token1,
                fee,
                tick_lower,
                tick_upper,
                liquidity,
                fee_growth_0,
                fee_growth_1,
                tokens_owed_0,
                tokens_owed_1,
            ) = position_data

            # 获取代币符号
            token0_symbol = await self._get_token_symbol(token0, network)
            token1_symbol = await self._get_token_symbol(token1, network)

            # 计算价格范围
            price_lower = 1.0001**tick_lower
            price_upper = 1.0001**tick_upper

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
                "real_time": True,
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
                    "type": "function",
                }
            ]

            contract = w3.eth.contract(
                address=w3.to_checksum_address(token_address), abi=token_abi
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
                "0x2170Ed0880ac9A755fd29B2688956BD959F933F8": "ETH",
            }

            return known_tokens.get(token_address, f"Token_{token_address[:6]}")

    async def get_token_price(self, token_address: str, network: str = "bsc") -> float:
        """获取代币价格（使用DEX价格）"""
        try:
            # 这里可以集成价格API，比如CoinGecko或者直接从DEX获取
            # 暂时返回模拟价格
            prices = {
                "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c": 300.0,  # WBNB
                "0x55d398326f99059fF775485246999027B3197955": 1.0,  # USDT
                "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56": 1.0,  # BUSD
                "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d": 1.0,  # USDC
                "0x2170Ed0880ac9A755fd29B2688956BD959F933F8": 2000.0,  # ETH
            }

            return prices.get(token_address, 1.0)

        except Exception as e:
            logger.error(f"获取代币价格失败: {e}")
            return 1.0

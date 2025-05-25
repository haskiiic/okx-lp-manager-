"""
区块链读取器配置文件
管理并发设置、网络配置和性能参数
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ConcurrencyConfig:
    """并发配置"""

    # 默认并发数量
    default_concurrent_requests: int = 10

    # NFT批次大小
    nft_batch_size: int = 100

    # 详情批次大小
    details_batch_size: int = 50

    # 进度报告间隔
    nft_progress_interval: int = 20
    details_progress_interval: int = 5

    # 性能估算参数（秒）
    estimated_nft_query_time: float = 0.3
    estimated_details_query_time: float = 0.5


@dataclass
class NetworkConfig:
    """网络配置"""

    rpc: str
    chain_id: int
    factory_address: str
    position_manager_address: str
    name: str


class BlockchainConfig:
    """区块链配置管理器"""

    def __init__(self):
        self.concurrency = ConcurrencyConfig()

        # 网络配置
        self.networks: Dict[str, NetworkConfig] = {
            "bsc": NetworkConfig(
                rpc="https://bsc-dataseed1.binance.org/",
                chain_id=56,
                factory_address="0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865",
                position_manager_address="0x46A15B0b27311cedF172AB29E4f4766fbE7F4364",
                name="BSC (Binance Smart Chain)",
            ),
            "ethereum": NetworkConfig(
                rpc="https://eth.llamarpc.com",
                chain_id=1,
                factory_address="0x1F98431c8aD98523631AE4a59f267346ea31F984",
                position_manager_address="0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
                name="Ethereum Mainnet",
            ),
            "polygon": NetworkConfig(
                rpc="https://polygon-rpc.com",
                chain_id=137,
                factory_address="0x1F98431c8aD98523631AE4a59f267346ea31F984",
                position_manager_address="0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
                name="Polygon",
            ),
            "arbitrum": NetworkConfig(
                rpc="https://arb1.arbitrum.io/rpc",
                chain_id=42161,
                factory_address="0x1F98431c8aD98523631AE4a59f267346ea31F984",
                position_manager_address="0xC36442b4a4522E871399CD717aBDD847Ab11FE88",
                name="Arbitrum One",
            ),
        }

        # 常见代币地址映射
        self.known_tokens = {
            # BSC
            "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c": "WBNB",
            "0x55d398326f99059fF775485246999027B3197955": "USDT",
            "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56": "BUSD",
            "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d": "USDC",
            "0x2170Ed0880ac9A755fd29B2688956BD959F933F8": "ETH",
            "0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c": "BTCB",
            # Ethereum
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2": "WETH",
            "0xdAC17F958D2ee523a2206206994597C13D831ec7": "USDT",
            "0xA0b86a33E6417c4E4BE62F60F000D19f3b9B88c3": "USDC",
            "0x6B175474E89094C44Da98b954EedeAC495271d0F": "DAI",
            "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599": "WBTC",
        }

    def get_network_config(self, network: str) -> NetworkConfig:
        """获取网络配置"""
        if network not in self.networks:
            raise ValueError(f"不支持的网络: {network}")
        return self.networks[network]

    def get_supported_networks(self) -> list[str]:
        """获取支持的网络列表"""
        return list(self.networks.keys())

    def get_token_symbol(self, token_address: str) -> str:
        """获取已知代币符号"""
        return self.known_tokens.get(token_address, f"Token_{token_address[:6]}")

    def set_concurrent_limit(self, limit: int):
        """设置并发限制"""
        if limit > 0:
            self.concurrency.default_concurrent_requests = limit
        else:
            raise ValueError("并发数量必须大于0")

    def optimize_for_network(self, network: str):
        """根据网络优化配置"""
        if network == "bsc":
            # BSC节点通常较快，可以使用更高并发
            self.concurrency.default_concurrent_requests = 15
            self.concurrency.nft_batch_size = 150
        elif network == "ethereum":
            # Ethereum节点较慢，使用较低并发
            self.concurrency.default_concurrent_requests = 8
            self.concurrency.nft_batch_size = 80
        elif network in ["polygon", "arbitrum"]:
            # L2网络速度中等
            self.concurrency.default_concurrent_requests = 12
            self.concurrency.nft_batch_size = 120

    def get_performance_estimate(
        self, position_count: int, concurrent_limit: int | None = None
    ) -> Dict[str, float]:
        """获取性能估算"""
        if concurrent_limit is None:
            concurrent_limit = self.concurrency.default_concurrent_requests

        # 计算预估时间
        sequential_nft_time = position_count * self.concurrency.estimated_nft_query_time
        concurrent_nft_time = (
            position_count / concurrent_limit
        ) * self.concurrency.estimated_nft_query_time

        sequential_details_time = (
            position_count * self.concurrency.estimated_details_query_time
        )
        concurrent_details_time = (
            position_count / concurrent_limit
        ) * self.concurrency.estimated_details_query_time

        return {
            "sequential_total": sequential_nft_time + sequential_details_time,
            "concurrent_total": concurrent_nft_time + concurrent_details_time,
            "sequential_nft": sequential_nft_time,
            "concurrent_nft": concurrent_nft_time,
            "sequential_details": sequential_details_time,
            "concurrent_details": concurrent_details_time,
            "improvement_percent": (
                (
                    sequential_nft_time
                    + sequential_details_time
                    - concurrent_nft_time
                    - concurrent_details_time
                )
                / (sequential_nft_time + sequential_details_time)
            )
            * 100,
            "time_saved": (sequential_nft_time + sequential_details_time)
            - (concurrent_nft_time + concurrent_details_time),
        }


# 全局配置实例
blockchain_config = BlockchainConfig()

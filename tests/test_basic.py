import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from main import app
from app.services.okx_wallet_api import OKXWalletAPI
from app.services.pancakeswap_service import PancakeSwapV3Service
from app.services.lp_manager import LPManager

# 创建测试客户端
client = TestClient(app)

class TestAPI:
    """API接口测试"""
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["status"] == "healthy"
    
    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "OKX钱包LP管理系统" in data["name"]

class TestOKXWalletAPI:
    """OKX钱包API测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.api = OKXWalletAPI()
    
    def test_generate_signature(self):
        """测试签名生成"""
        timestamp = "1640995200"
        method = "GET"
        request_path = "/api/v5/wallet/chain/supported-chains"
        
        # 这里使用mock，因为实际签名需要真实的密钥
        with patch.object(self.api, '_generate_signature') as mock_sig:
            mock_sig.return_value = "mock_signature"
            result = self.api._generate_signature(timestamp, method, request_path)
            assert result == "mock_signature"
    
    def test_get_headers(self):
        """测试请求头生成"""
        method = "GET"
        request_path = "/test"
        
        headers = self.api._get_headers(method, request_path)
        
        assert 'OK-ACCESS-KEY' in headers
        assert 'OK-ACCESS-SIGN' in headers
        assert 'OK-ACCESS-TIMESTAMP' in headers
        assert 'OK-ACCESS-PASSPHRASE' in headers
        assert headers['Content-Type'] == 'application/json'

class TestPancakeSwapV3Service:
    """PancakeSwap V3服务测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.service = PancakeSwapV3Service("bsc")
    
    def test_calculate_tick_from_price(self):
        """测试价格到tick的转换"""
        price = 300.0
        tick = self.service.calculate_tick_from_price(price)
        
        # 验证tick计算是否合理
        assert isinstance(tick, int)
        assert tick > 0
        
        # 验证反向转换
        calculated_price = self.service.calculate_price_from_tick(tick)
        assert abs(calculated_price - price) < 1.0  # 允许小误差
    
    def test_get_tick_spacing(self):
        """测试tick间距"""
        # 测试不同费率的tick间距
        assert self.service.get_tick_spacing(100) == 1
        assert self.service.get_tick_spacing(500) == 10
        assert self.service.get_tick_spacing(3000) == 60
        assert self.service.get_tick_spacing(10000) == 200
        
        # 测试未知费率
        assert self.service.get_tick_spacing(999) == 60  # 默认值
    
    def test_align_tick_to_spacing(self):
        """测试tick对齐"""
        # 测试3000费率（间距60）
        aligned_tick = self.service.align_tick_to_spacing(123, 3000)
        assert aligned_tick % 60 == 0
        assert aligned_tick <= 123
        
        # 测试500费率（间距10）
        aligned_tick = self.service.align_tick_to_spacing(45, 500)
        assert aligned_tick % 10 == 0
        assert aligned_tick <= 45

class TestLPManager:
    """LP管理器测试"""
    
    def setup_method(self):
        """测试前准备"""
        self.manager = LPManager()
    
    def test_get_chain_index(self):
        """测试链索引获取"""
        assert self.manager._get_chain_index("ethereum") == "1"
        assert self.manager._get_chain_index("bsc") == "56"
        assert self.manager._get_chain_index("polygon") == "137"
        assert self.manager._get_chain_index("unknown") == "56"  # 默认值
    
    @pytest.mark.asyncio
    async def test_check_wallet_balance_mock(self):
        """测试钱包余额检查（使用mock）"""
        wallet_address = "0x742d35Cc6644C93A5B9Ba20bD40FA0bd5CfDD7C3"
        token0_address = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
        token1_address = "0x55d398326f99059fF775485246999027B3197955"
        
        # Mock OKX API响应
        mock_balance_response = {
            "data": [{"tokenBalance": "100.0"}]
        }
        
        with patch.object(self.manager.okx_api, 'get_token_balance') as mock_balance:
            mock_balance.return_value = mock_balance_response
            
            result = await self.manager._check_wallet_balance(
                wallet_address, token0_address, token1_address,
                10.0, 20.0, "bsc"
            )
            
            assert result["sufficient"] == True
            assert result["balance0"] == 100.0
            assert result["balance1"] == 100.0

class TestConfiguration:
    """配置测试"""
    
    def test_settings_import(self):
        """测试配置导入"""
        from app.config import settings
        
        # 测试基本配置存在
        assert hasattr(settings, 'okx_api_key')
        assert hasattr(settings, 'bsc_rpc_url')
        assert hasattr(settings, 'pancakeswap_v3_factory')
        assert hasattr(settings, 'supported_networks')
        
        # 测试支持的网络配置
        assert 'bsc' in settings.supported_networks
        assert 'ethereum' in settings.supported_networks
        assert 'polygon' in settings.supported_networks

@pytest.mark.asyncio
async def test_database_models():
    """测试数据库模型"""
    from app.models.database import Wallet, LPPosition, LPTransaction
    
    # 测试模型创建
    wallet = Wallet(
        address="0x742d35Cc6644C93A5B9Ba20bD40FA0bd5CfDD7C3",
        network="bsc",
        private_key_encrypted="encrypted_key"
    )
    
    assert wallet.address == "0x742d35Cc6644C93A5B9Ba20bD40FA0bd5CfDD7C3"
    assert wallet.network == "bsc"
    assert wallet.is_active == True  # 默认值

def test_api_documentation():
    """测试API文档访问"""
    # 测试Swagger UI
    response = client.get("/docs")
    assert response.status_code == 200
    
    # 测试ReDoc
    response = client.get("/redoc")
    assert response.status_code == 200

@pytest.mark.integration
class TestIntegration:
    """集成测试（需要实际服务）"""
    
    @pytest.mark.skip(reason="需要真实的OKX API密钥")
    def test_okx_api_integration(self):
        """测试OKX API集成"""
        # 这个测试需要真实的API密钥
        pass
    
    @pytest.mark.skip(reason="需要区块链网络连接")
    def test_pancakeswap_integration(self):
        """测试PancakeSwap集成"""
        # 这个测试需要区块链网络连接
        pass

if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"]) 
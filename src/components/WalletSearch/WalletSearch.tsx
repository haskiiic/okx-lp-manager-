import React, { useState, useCallback } from 'react';
import { Input, Button, Select, Space, message, Card, Typography } from 'antd';
import { SearchOutlined, WalletOutlined, GlobalOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import { ChainType } from '@/types';
import { useStore } from '@/store';

const { Option } = Select;
const { Text } = Typography;

// 样式化组件
const SearchContainer = styled(Card)`
  margin-bottom: 24px;
  
  .ant-card-body {
    padding: 24px;
  }
`;

const SearchForm = styled.div`
  .search-input-group {
    display: flex;
    gap: 12px;
    align-items: flex-end;
    
    @media (max-width: 768px) {
      flex-direction: column;
      align-items: stretch;
    }
  }
  
  .wallet-input {
    flex: 1;
    min-width: 0;
  }
  
  .chain-select {
    min-width: 140px;
    
    @media (max-width: 768px) {
      width: 100%;
    }
  }
  
  .search-button {
    min-width: 120px;
    
    @media (max-width: 768px) {
      width: 100%;
    }
  }
`;

const InfoText = styled(Text)`
  color: #64748b;
  font-size: 14px;
  display: block;
  margin-bottom: 16px;
`;

// 网络配置
const NETWORKS = {
  bsc: {
    label: 'BSC',
    value: 'bsc',
    color: '#f0b90b',
    icon: '🔶',
  },
  ethereum: {
    label: 'Ethereum',
    value: 'ethereum', 
    color: '#627eea',
    icon: '💎',
  },
  polygon: {
    label: 'Polygon',
    value: 'polygon',
    color: '#8247e5',
    icon: '🔷',
  },
};

interface WalletSearchProps {
  onSearch: (walletAddress: string, chain: ChainType) => void;
  loading?: boolean;
}

const WalletSearch: React.FC<WalletSearchProps> = ({ onSearch, loading = false }) => {
  const [walletAddress, setWalletAddress] = useState('');
  const [selectedChain, setSelectedChain] = useState<ChainType>('bsc');
  
  // 从store获取状态
  const { setCurrentWallet, setSelectedChain: setStoreChain } = useStore();

  // 验证钱包地址格式
  const isValidAddress = useCallback((address: string): boolean => {
    // 以太坊地址格式验证：0x开头，40个十六进制字符
    const ethAddressRegex = /^0x[a-fA-F0-9]{40}$/;
    return ethAddressRegex.test(address);
  }, []);

  // 处理搜索
  const handleSearch = useCallback(async () => {
    if (!walletAddress.trim()) {
      message.warning('请输入钱包地址');
      return;
    }

    if (!isValidAddress(walletAddress)) {
      message.error('请输入有效的钱包地址格式 (0x...)');
      return;
    }

    try {
      // 更新store状态
      setCurrentWallet(walletAddress);
      setStoreChain(selectedChain);
      
      // 调用搜索回调
      await onSearch(walletAddress, selectedChain);
      
      message.success(`成功加载 ${NETWORKS[selectedChain].label} 网络上的钱包数据`);
    } catch (error) {
      message.error('加载钱包数据失败，请重试');
      console.error('搜索钱包失败:', error);
    }
  }, [walletAddress, selectedChain, isValidAddress, onSearch, setCurrentWallet, setStoreChain]);

  // 处理回车键搜索
  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  }, [handleSearch]);

  // 快速填入示例地址
  const handleExampleAddress = useCallback(() => {
    const exampleAddresses = {
      bsc: '0x1234567890123456789012345678901234567890',
      ethereum: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
      polygon: '0x9876543210987654321098765432109876543210',
    };
    
    setWalletAddress(exampleAddresses[selectedChain]);
  }, [selectedChain]);

  // 加载演示数据
  const handleDemoData = useCallback(async () => {
    const demoAddress = '0xDemo1234567890123456789012345678901234567';
    setWalletAddress(demoAddress);
    
    try {
      // 调用搜索回调，触发演示数据加载
      await onSearch(demoAddress, selectedChain);
    } catch (error) {
      console.error('加载演示数据失败:', error);
    }
  }, [selectedChain, onSearch]);

  return (
    <SearchContainer>
      <div style={{ marginBottom: 16 }}>
        <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
          <WalletOutlined style={{ color: '#667eea' }} />
          钱包地址搜索
        </h3>
        <InfoText>
          输入钱包地址快速查询LP头寸，支持BSC、Ethereum、Polygon网络
        </InfoText>
      </div>

      <SearchForm>
        <div className="search-input-group">
          {/* 钱包地址输入 */}
          <div className="wallet-input">
            <Input
              size="large"
              placeholder="输入钱包地址 (0x...)"
              value={walletAddress}
              onChange={(e) => setWalletAddress(e.target.value)}
              onKeyPress={handleKeyPress}
              prefix={<WalletOutlined style={{ color: '#94a3b8' }} />}
              suffix={
                <Button 
                  type="link" 
                  size="small" 
                  onClick={handleExampleAddress}
                  style={{ fontSize: '12px' }}
                >
                  示例
                </Button>
              }
            />
          </div>

          {/* 网络选择 */}
          <div className="chain-select">
            <Select
              size="large"
              value={selectedChain}
              onChange={setSelectedChain}
              style={{ width: '100%' }}
              suffixIcon={<GlobalOutlined />}
            >
              {Object.values(NETWORKS).map((network) => (
                <Option key={network.value} value={network.value}>
                  <Space>
                    <span>{network.icon}</span>
                    <span>{network.label}</span>
                  </Space>
                </Option>
              ))}
            </Select>
          </div>

          {/* 搜索按钮 */}
          <div className="search-button">
            <Button 
              type="primary" 
              size="large"
              icon={<SearchOutlined />}
              loading={loading}
              onClick={handleSearch}
              style={{ width: '100%', marginBottom: '8px' }}
            >
              {loading ? '搜索中...' : '搜索LP头寸'}
            </Button>
            
            <Button 
              size="large"
              onClick={handleDemoData}
              style={{ width: '100%' }}
              disabled={loading}
            >
              🎭 查看演示效果
            </Button>
          </div>
        </div>
      </SearchForm>

      {/* 快速操作提示 */}
      <div style={{ marginTop: 16, fontSize: '12px', color: '#64748b' }}>
        <Space split={<span>•</span>}>
          <span>支持多链钱包查询</span>
          <span>实时数据更新</span>
          <span>按回车键快速搜索</span>
        </Space>
      </div>
    </SearchContainer>
  );
};

export default WalletSearch; 
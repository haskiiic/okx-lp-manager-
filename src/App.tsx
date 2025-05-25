import React, { useEffect, useState, useCallback } from 'react';
import { Layout, ConfigProvider, theme, message, Spin } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import styled from 'styled-components';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// 组件导入
import StatsCards from './components/Dashboard/StatsCards';
import WalletSearch from './components/WalletSearch/WalletSearch';
import PositionsList from './components/LPPositions/PositionsList';

// Store和服务导入
import { useStore } from './store';
import api from './services/api';
import { ChainType, LPPosition } from './types';

// 临时类型定义，用于处理后端返回的原始数据
interface RawPositionData {
  id?: string | number;
  token_id?: number;
  tokenId?: number;
  pool_address?: string;
  token0_address?: string;
  token1_address?: string;
  token0_symbol?: string;
  token1_symbol?: string;
  fee_tier?: number;
  tick_lower?: number;
  tick_upper?: number;
  price_lower?: number;
  price_upper?: number;
  liquidity?: string;
  amount0?: string;
  amount1?: string;
  tokens_owed_0?: string;
  tokens_owed_1?: string;
  status?: string;
  usd_value?: number;
  created_at?: string;
  updated_at?: string;
  network?: string;
  error?: boolean;
  message?: string;
}

const { Header, Content, Sider } = Layout;

// 样式化组件
const AppContainer = styled(Layout)`
  min-height: 100vh;
  background: #f8fafc;
`;

const AppHeader = styled(Header)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
    color: white;
    font-size: 20px;
    font-weight: 600;
    
    .logo-icon {
      font-size: 24px;
    }
  }
  
  .header-actions {
    display: flex;
    align-items: center;
    gap: 16px;
    color: white;
    
    .connection-status {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #10b981;
        
        &.offline {
          background: #ef4444;
        }
      }
    }
  }
`;

const AppSider = styled(Sider)`
  background: white;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  
  .ant-layout-sider-children {
    padding: 24px 16px;
  }
`;

const AppContent = styled(Content)`
  padding: 24px;
  background: #f8fafc;
`;

const LoadingContainer = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  height: 400px;
  
  .loading-content {
    text-align: center;
    
    .loading-text {
      margin-top: 16px;
      color: #64748b;
      font-size: 16px;
    }
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: 60px 20px;
  
  .empty-icon {
    font-size: 64px;
    color: #d1d5db;
    margin-bottom: 16px;
  }
  
  .empty-title {
    font-size: 18px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 8px;
  }
  
  .empty-description {
    color: #6b7280;
    font-size: 14px;
  }
`;

const App: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  // Store状态
  const {
    stats,
    positions,
    currentWallet,
    selectedChain,
    setStats,
    setPositions,
    setLoading: setStoreLoading,
  } = useStore();

  // 初始化应用
  useEffect(() => {
    const initApp = async () => {
      try {
        // 检查系统健康状态
        await api.system.healthCheck();
        console.log('✅ 系统连接正常');
      } catch (error) {
        console.error('❌ 系统连接失败:', error);
        message.error('无法连接到后端服务，请检查网络连接');
      } finally {
        setInitialLoading(false);
      }
    };

    initApp();
  }, []);

  // 搜索钱包LP头寸
  const handleWalletSearch = useCallback(async (walletAddress: string, chain: ChainType) => {
    setLoading(true);
    setStoreLoading(true);

    try {
      // 检查是否是演示地址
      if (walletAddress.startsWith('0xDemo')) {
        // 返回演示数据
        const demoPositions: LPPosition[] = [
          {
            id: 'demo-1',
            tokenId: 12345,
            owner: walletAddress,
            pool: {
              address: '0xdemo_pool_1',
              token0: {
                address: '0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c',
                symbol: 'WBNB',
                name: 'Wrapped BNB',
                decimals: 18,
                price: 320.50,
              },
              token1: {
                address: '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
                symbol: 'USDC',
                name: 'USD Coin',
                decimals: 18,
                price: 1.00,
              },
              fee: 3000,
              tickSpacing: 60,
              liquidity: '1234567890123456789',
              sqrtPriceX96: '0',
              tick: 0,
              tvl: 1250000,
              volume24h: 850000,
              feesUSD24h: 2550,
              apr: 15.8,
            },
            tickLower: 200000,
            tickUpper: 210000,
            liquidity: '1234567890123456789',
            amount0: '5.25',
            amount1: '1680.75',
            uncollectedFees0: '0.05',
            uncollectedFees1: '16.20',
            feeGrowthInside0LastX128: '0',
            feeGrowthInside1LastX128: '0',
            tokensOwed0: '0.05',
            tokensOwed1: '16.20',
            status: 'active',
            inRange: true,
            currentPrice: 320.15,
            priceRange: {
              lower: 310.00,
              upper: 330.00,
            },
            valueUSD: 3362.25,
            feesEarnedUSD: 32.42,
            createdAt: '2024-01-15T08:30:00.000Z',
            updatedAt: new Date().toISOString(),
          },
          {
            id: 'demo-2',
            tokenId: 12346,
            owner: walletAddress,
            pool: {
              address: '0xdemo_pool_2',
              token0: {
                address: '0x2170Ed0880ac9A755fd29B2688956BD959F933F8',
                symbol: 'ETH',
                name: 'Ethereum Token',
                decimals: 18,
                price: 2450.80,
              },
              token1: {
                address: '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
                symbol: 'USDC',
                name: 'USD Coin',
                decimals: 18,
                price: 1.00,
              },
              fee: 500,
              tickSpacing: 10,
              liquidity: '987654321098765432',
              sqrtPriceX96: '0',
              tick: 0,
              tvl: 5680000,
              volume24h: 1200000,
              feesUSD24h: 600,
              apr: 8.2,
            },
            tickLower: 180000,
            tickUpper: 200000,
            liquidity: '987654321098765432',
            amount0: '2.15',
            amount1: '5269.22',
            uncollectedFees0: '0.02',
            uncollectedFees1: '49.01',
            feeGrowthInside0LastX128: '0',
            feeGrowthInside1LastX128: '0',
            tokensOwed0: '0.02',
            tokensOwed1: '49.01',
            status: 'active',
            inRange: false,
            currentPrice: 2451.20,
            priceRange: {
              lower: 2400.00,
              upper: 2500.00,
            },
            valueUSD: 10538.94,
            feesEarnedUSD: 98.02,
            createdAt: '2024-01-20T14:15:00.000Z',
            updatedAt: new Date().toISOString(),
          },
        ];

        // 计算演示统计数据
        const demoStats = {
          totalPositions: demoPositions.length,
          activePositions: demoPositions.filter(p => p.status === 'active').length,
          totalValueUSD: demoPositions.reduce((sum, p) => sum + p.valueUSD, 0),
          totalFeesEarnedUSD: demoPositions.reduce((sum, p) => sum + p.feesEarnedUSD, 0),
          totalFeesEarned24h: 130.44,
          averageAPR: 12.0,
          inRangePositions: demoPositions.filter(p => p.inRange).length,
          outOfRangePositions: demoPositions.filter(p => !p.inRange).length,
        };

        // 更新store状态
        setPositions(demoPositions);
        setStats(demoStats);

        message.success(`🎭 演示模式：已加载 ${demoPositions.length} 个示例LP头寸`);
        return;
      }

      // 获取真实头寸数据
      const response = await api.lp.getPositions(walletAddress, chain);
      
      // 处理后端返回的数据结构
      let rawPositions: RawPositionData[] = [];
      
      // 检查response是否是标准API响应格式
      if (response && response.positions && Array.isArray(response.positions)) {
        // 直接API调用返回的格式 { positions: [...], total: number }
        rawPositions = response.positions.filter((item: any) => 
          item && !item.error && !item.message && (item.id || item.token_id)
        );
      } else if (response && typeof response === 'object' && 'data' in response) {
        // 通过API客户端处理后的格式，response.data是后端真实返回的数据
        const backendData = (response as any).data;
        if (backendData && backendData.positions && Array.isArray(backendData.positions)) {
          rawPositions = backendData.positions.filter((item: any) => 
            item && !item.error && !item.message && (item.id || item.token_id)
          );
        }
      } else if (Array.isArray(response)) {
        // 直接返回数组格式
        rawPositions = response.filter((item: any) => 
          item && !item.error && !item.message && (item.id || item.token_id)
        );
      }
      
      // 转换数据格式以匹配前端类型定义
      const formattedPositions: LPPosition[] = rawPositions.map((pos: RawPositionData) => ({
        id: pos.id?.toString() || pos.token_id?.toString() || 'unknown',
        tokenId: pos.token_id || pos.tokenId || 0,
        owner: walletAddress,
        pool: {
          address: pos.pool_address || '',
          token0: {
            address: pos.token0_address || '',
            symbol: pos.token0_symbol || 'UNKNOWN',
            name: pos.token0_symbol || 'Unknown Token',
            decimals: 18,
            price: 0,
          },
          token1: {
            address: pos.token1_address || '',
            symbol: pos.token1_symbol || 'UNKNOWN', 
            name: pos.token1_symbol || 'Unknown Token',
            decimals: 18,
            price: 0,
          },
          fee: pos.fee_tier || 3000,
          tickSpacing: 60,
          liquidity: pos.liquidity || '0',
          sqrtPriceX96: '0',
          tick: 0,
          tvl: 0,
          volume24h: 0,
          feesUSD24h: 0,
          apr: 0,
        },
        tickLower: pos.tick_lower || 0,
        tickUpper: pos.tick_upper || 0,
        liquidity: pos.liquidity || '0',
        amount0: pos.amount0 || '0',
        amount1: pos.amount1 || '0',
        uncollectedFees0: pos.tokens_owed_0 || '0',
        uncollectedFees1: pos.tokens_owed_1 || '0',
        feeGrowthInside0LastX128: '0',
        feeGrowthInside1LastX128: '0',
        tokensOwed0: pos.tokens_owed_0 || '0',
        tokensOwed1: pos.tokens_owed_1 || '0',
        status: pos.status === 'active' ? 'active' : 'closed',
        inRange: true, // 默认在范围内，实际需要计算
        currentPrice: ((pos.price_lower || 0) + (pos.price_upper || 0)) / 2,
        priceRange: {
          lower: pos.price_lower || 0,
          upper: pos.price_upper || 0,
        },
        valueUSD: pos.usd_value || 0,
        feesEarnedUSD: 0, // 需要计算
        createdAt: pos.created_at || new Date().toISOString(),
        updatedAt: pos.updated_at || new Date().toISOString(),
      }));
      
      // 计算统计数据
      const stats = {
        totalPositions: formattedPositions.length,
        activePositions: formattedPositions.filter(p => p.status === 'active').length,
        totalValueUSD: formattedPositions.reduce((sum, p) => sum + (p.valueUSD || 0), 0),
        totalFeesEarnedUSD: formattedPositions.reduce((sum, p) => sum + (p.feesEarnedUSD || 0), 0),
        totalFeesEarned24h: 0, // 暂时设为0，因为没有24h数据
        averageAPR: 0, // 暂时设为0，因为没有APR数据
        inRangePositions: formattedPositions.filter(p => p.inRange).length,
        outOfRangePositions: formattedPositions.filter(p => !p.inRange).length,
      };

      // 更新store状态
      setPositions(formattedPositions);
      setStats(stats);

      if (formattedPositions.length > 0) {
        message.success(`成功加载 ${formattedPositions.length} 个LP头寸`);
      } else {
        message.info('该钱包暂无LP头寸，您可以尝试创建新的流动性头寸');
      }
    } catch (error) {
      console.error('获取钱包数据失败:', error);
      message.error('获取钱包数据失败，请检查钱包地址是否正确或稍后重试');
      
      // 清空数据
      setPositions([]);
      setStats(null);
    } finally {
      setLoading(false);
      setStoreLoading(false);
    }
  }, [setPositions, setStats, setStoreLoading]);

  // LP头寸操作处理
  const handleViewPosition = useCallback((position: LPPosition) => {
    console.log('查看头寸详情:', position);
    // TODO: 打开头寸详情弹窗
  }, []);

  const handleEditPosition = useCallback((position: LPPosition) => {
    console.log('编辑头寸:', position);
    // TODO: 打开编辑头寸弹窗
  }, []);

  const handleCollectFees = useCallback(async (position: LPPosition) => {
    try {
      message.loading('收集手续费中...', 0);
      
      const result = await api.lp.collectFees(position.id);
      
      message.destroy();
      message.success('手续费收集成功！');
      
      console.log('收集手续费成功:', result);
      
      // 重新获取头寸数据
      if (currentWallet) {
        await handleWalletSearch(currentWallet, selectedChain);
      }
    } catch (error) {
      message.destroy();
      message.error('收集手续费失败');
      console.error('收集手续费失败:', error);
    }
  }, [currentWallet, selectedChain, handleWalletSearch]);

  const handleAddLiquidity = useCallback((position: LPPosition) => {
    console.log('增加流动性:', position);
    // TODO: 打开增加流动性弹窗
  }, []);

  const handleDeletePosition = useCallback(async (position: LPPosition) => {
    try {
      message.loading('关闭头寸中...', 0);
      
      const result = await api.lp.closePosition(position.id);
      
      message.destroy();
      message.success('头寸关闭成功！');
      
      console.log('关闭头寸成功:', result);
      
      // 重新获取头寸数据
      if (currentWallet) {
        await handleWalletSearch(currentWallet, selectedChain);
      }
    } catch (error) {
      message.destroy();
      message.error('关闭头寸失败');
      console.error('关闭头寸失败:', error);
    }
  }, [currentWallet, selectedChain, handleWalletSearch]);

  // 渲染加载状态
  if (initialLoading) {
    return (
      <ConfigProvider locale={zhCN}>
        <LoadingContainer>
          <div className="loading-content">
            <Spin size="large" />
            <div className="loading-text">正在初始化系统...</div>
          </div>
        </LoadingContainer>
      </ConfigProvider>
    );
  }

  return (
    <ConfigProvider 
      locale={zhCN}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: '#667eea',
          borderRadius: 8,
        },
      }}
    >
      <Router>
        <AppContainer>
          {/* 顶部导航栏 */}
          <AppHeader>
            <div className="logo">
              <span className="logo-icon">🥞</span>
              <span>OKX LP管理系统</span>
            </div>
            
            <div className="header-actions">
              <div className="connection-status">
                <span className="status-dot"></span>
                <span>系统运行正常</span>
              </div>
            </div>
          </AppHeader>

          <Layout>
            {/* 主要内容区域 */}
            <AppContent>
              <Routes>
                <Route path="/" element={
                  <div>
                    {/* 钱包搜索组件 */}
                    <WalletSearch 
                      onSearch={handleWalletSearch}
                      loading={loading}
                    />

                    {/* 统计面板 */}
                    <StatsCards 
                      stats={stats}
                      loading={loading}
                    />

                    {/* LP头寸列表 */}
                    {currentWallet ? (
                      positions.length > 0 ? (
                        <PositionsList
                          loading={loading}
                          onViewPosition={handleViewPosition}
                          onEditPosition={handleEditPosition}
                          onDeletePosition={handleDeletePosition}
                          onCollectFees={handleCollectFees}
                          onAddLiquidity={handleAddLiquidity}
                        />
                      ) : (
                        !loading && (
                          <EmptyState>
                            <div className="empty-icon">📊</div>
                            <div className="empty-title">暂无LP头寸</div>
                            <div className="empty-description">
                              该钱包在 {selectedChain.toUpperCase()} 网络上暂无活跃的LP头寸
                            </div>
                          </EmptyState>
                        )
                      )
                    ) : (
                      <EmptyState>
                        <div className="empty-icon">🔍</div>
                        <div className="empty-title">开始搜索</div>
                        <div className="empty-description">
                          请在上方输入钱包地址，开始查询LP头寸
                        </div>
                      </EmptyState>
                    )}
                  </div>
                } />
                
                {/* 其他路由 */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </AppContent>
          </Layout>
        </AppContainer>
      </Router>
    </ConfigProvider>
  );
};

export default App; 
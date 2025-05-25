import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  LPPosition, 
  WalletBalance, 
  StatsData, 
  CreateLPParams, 
  RebalanceConfig, 
  Pool, 
  ApiResponse,
  ChainType,
  FilterParams,
  PaginationParams
} from '@/types';

// API客户端配置
class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api/v1') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        console.log('🚀 API请求:', config.method?.toUpperCase(), config.url);
        return config;
      },
      (error) => {
        console.error('❌ API请求错误:', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => {
        console.log('✅ API响应:', response.status, response.config.url);
        return response;
      },
      (error) => {
        console.error('❌ API响应错误:', error.response?.status, error.response?.data);
        
        // 统一错误处理
        if (error.response?.status === 401) {
          // 处理未授权错误
          console.warn('⚠️ 未授权访问，请检查API密钥');
        } else if (error.response?.status >= 500) {
          // 处理服务器错误
          console.error('🔥 服务器错误，请稍后重试');
        }
        
        return Promise.reject(error);
      }
    );
  }

  // 通用GET请求
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get<ApiResponse<T>>(url, { params });
    return response.data.data;
  }

  // 通用POST请求
  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<ApiResponse<T>>(url, data);
    return response.data.data;
  }

  // 通用PUT请求
  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<ApiResponse<T>>(url, data);
    return response.data.data;
  }

  // 通用DELETE请求
  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<ApiResponse<T>>(url);
    return response.data.data;
  }
}

// 创建API客户端实例
const apiClient = new ApiClient();

// LP头寸相关API
export const lpApi = {
  // 获取钱包的所有LP头寸
  async getPositions(
    walletAddress: string, 
    chain: ChainType,
    filters?: FilterParams,
    pagination?: PaginationParams
  ): Promise<{ positions: LPPosition[]; total: number }> {
    const params = new URLSearchParams();
    params.append('chain', chain);
    
    // 添加过滤参数
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v.toString()));
          } else {
            params.append(key, value.toString());
          }
        }
      });
    }
    
    // 添加分页参数
    if (pagination) {
      Object.entries(pagination).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, value.toString());
        }
      });
    }
    
    const queryString = params.toString();
    const url = `/lp/positions/${walletAddress}${queryString ? `?${queryString}` : ''}`;
    
    return apiClient.get(url);
  },

  // 获取单个LP头寸详情
  async getPosition(positionId: string): Promise<LPPosition> {
    return apiClient.get(`/lp/positions/detail/${positionId}`);
  },

  // 创建新的LP头寸
  async createPosition(params: CreateLPParams): Promise<{ transactionHash: string; positionId: string }> {
    return apiClient.post('/lp/create', params);
  },

  // 增加流动性
  async addLiquidity(positionId: string, amount0: string, amount1: string): Promise<{ transactionHash: string }> {
    return apiClient.post(`/lp/positions/${positionId}/add-liquidity`, {
      amount0,
      amount1,
    });
  },

  // 移除流动性
  async removeLiquidity(positionId: string, liquidity: string): Promise<{ transactionHash: string }> {
    return apiClient.post(`/lp/positions/${positionId}/remove-liquidity`, {
      liquidity,
    });
  },

  // 收集手续费
  async collectFees(positionId: string): Promise<{ transactionHash: string }> {
    return apiClient.post(`/lp/positions/${positionId}/collect-fees`);
  },

  // 关闭头寸
  async closePosition(positionId: string): Promise<{ transactionHash: string }> {
    return apiClient.post(`/lp/positions/${positionId}/close`);
  },

  // 批量操作
  async batchOperation(operation: string, positionIds: string[], params?: any): Promise<{ transactionHashes: string[] }> {
    return apiClient.post('/lp/batch', {
      operation,
      positionIds,
      params,
    });
  },
};

// 钱包相关API
export const walletApi = {
  // 获取钱包余额
  async getBalance(walletAddress: string, chain: ChainType): Promise<WalletBalance> {
    return apiClient.get(`/wallet/balance/${walletAddress}?chain=${chain}`);
  },

  // 获取多链钱包余额
  async getMultiChainBalance(walletAddress: string): Promise<WalletBalance[]> {
    return apiClient.get(`/wallet/multi-chain-balance/${walletAddress}`);
  },

  // 连接钱包
  async connectWallet(address: string, signature: string): Promise<{ token: string }> {
    return apiClient.post('/wallet/connect', {
      address,
      signature,
    });
  },
};

// 流动性池相关API
export const poolApi = {
  // 获取流行的流动性池
  async getPopularPools(chain: ChainType, limit: number = 20): Promise<Pool[]> {
    return apiClient.get('/pools/popular', {
      chain,
      limit,
    });
  },

  // 搜索流动性池
  async searchPools(query: string, chain: ChainType): Promise<Pool[]> {
    return apiClient.get('/pools/search', {
      query,
      chain,
    });
  },

  // 获取池详情
  async getPoolDetails(poolAddress: string): Promise<Pool> {
    return apiClient.get(`/pools/${poolAddress}`);
  },

  // 获取池的历史数据
  async getPoolHistory(poolAddress: string, period: string = '24h'): Promise<any[]> {
    return apiClient.get(`/pools/${poolAddress}/history`, {
      period,
    });
  },
};

// 统计数据API
export const statsApi = {
  // 获取钱包统计数据
  async getWalletStats(walletAddress: string, chain?: ChainType): Promise<StatsData> {
    const params = new URLSearchParams();
    if (chain) {
      params.append('chain', chain);
    }
    
    const queryString = params.toString();
    const url = `/stats/wallet/${walletAddress}${queryString ? `?${queryString}` : ''}`;
    
    return apiClient.get(url);
  },

  // 获取全局统计数据
  async getGlobalStats(): Promise<StatsData> {
    return apiClient.get('/stats/global');
  },
};

// 自动重平衡相关API
export const rebalanceApi = {
  // 获取重平衡配置
  async getConfigs(walletAddress: string): Promise<RebalanceConfig[]> {
    return apiClient.get('/rebalance/configs', {
      wallet: walletAddress,
    });
  },

  // 创建重平衡配置
  async createConfig(config: Omit<RebalanceConfig, 'id' | 'createdAt'>): Promise<RebalanceConfig> {
    return apiClient.post('/rebalance/configs', config);
  },

  // 更新重平衡配置
  async updateConfig(configId: string, updates: Partial<RebalanceConfig>): Promise<RebalanceConfig> {
    return apiClient.put(`/rebalance/configs/${configId}`, updates);
  },

  // 删除重平衡配置
  async deleteConfig(configId: string): Promise<void> {
    return apiClient.delete(`/rebalance/configs/${configId}`);
  },

  // 手动触发重平衡
  async triggerRebalance(positionId: string): Promise<{ transactionHash: string }> {
    return apiClient.post(`/rebalance/trigger/${positionId}`);
  },
};

// 系统相关API
export const systemApi = {
  // 健康检查
  async healthCheck(): Promise<{ status: string; version: string }> {
    return apiClient.get('/health');
  },

  // 获取支持的网络
  async getSupportedNetworks(): Promise<any[]> {
    return apiClient.get('/networks');
  },

  // 获取系统配置
  async getConfig(): Promise<any> {
    return apiClient.get('/config');
  },
};

// 导出API客户端
export { apiClient };
export default {
  lp: lpApi,
  wallet: walletApi,
  pool: poolApi,
  stats: statsApi,
  rebalance: rebalanceApi,
  system: systemApi,
}; 
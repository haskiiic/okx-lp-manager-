// 网络类型
export type ChainType = 'bsc' | 'ethereum' | 'polygon';

// LP头寸状态
export type PositionStatus = 'active' | 'out_of_range' | 'closed';

// 代币信息
export interface Token {
  address: string;
  symbol: string;
  name: string;
  decimals: number;
  logoURI?: string;
  price?: number;
}

// 流动性池信息
export interface Pool {
  address: string;
  token0: Token;
  token1: Token;
  fee: number;
  tickSpacing: number;
  liquidity: string;
  sqrtPriceX96: string;
  tick: number;
  tvl: number;
  volume24h: number;
  feesUSD24h: number;
  apr: number;
}

// LP头寸信息
export interface LPPosition {
  id: string;
  tokenId: number;
  owner: string;
  pool: Pool;
  tickLower: number;
  tickUpper: number;
  liquidity: string;
  amount0: string;
  amount1: string;
  uncollectedFees0: string;
  uncollectedFees1: string;
  feeGrowthInside0LastX128: string;
  feeGrowthInside1LastX128: string;
  tokensOwed0: string;
  tokensOwed1: string;
  status: PositionStatus;
  inRange: boolean;
  currentPrice: number;
  priceRange: {
    lower: number;
    upper: number;
  };
  valueUSD: number;
  feesEarnedUSD: number;
  createdAt: string;
  updatedAt: string;
}

// 钱包余额
export interface WalletBalance {
  address: string;
  chain: ChainType;
  tokens: Array<{
    token: Token;
    balance: string;
    balanceUSD: number;
  }>;
  totalValueUSD: number;
  lastUpdated: string;
}

// 统计数据
export interface StatsData {
  totalPositions: number;
  activePositions: number;
  totalValueUSD: number;
  totalFeesEarnedUSD: number;
  totalFeesEarned24h: number;
  averageAPR: number;
  inRangePositions: number;
  outOfRangePositions: number;
}

// 创建LP参数
export interface CreateLPParams {
  pool: string;
  amount0: string;
  amount1: string;
  tickLower: number;
  tickUpper: number;
  slippage: number;
  deadline: number;
}

// 重平衡配置
export interface RebalanceConfig {
  id: string;
  positionId: string;
  enabled: boolean;
  strategy: 'aggressive' | 'moderate' | 'conservative';
  thresholds: {
    outOfRangeThreshold: number;
    feeThreshold: number;
    priceDeviationThreshold: number;
  };
  autoCompound: boolean;
  maxGasPrice: number;
  createdAt: string;
}

// API响应类型
export interface ApiResponse<T = any> {
  code: number;
  message: string;
  data: T;
  timestamp: string;
}

// WebSocket消息类型
export interface WSMessage {
  type: 'price_update' | 'position_update' | 'balance_update' | 'pool_update';
  data: any;
  timestamp: string;
}

// 网络配置
export interface NetworkConfig {
  chainId: number;
  name: string;
  symbol: string;
  rpcUrl: string;
  blockExplorer: string;
  contracts: {
    nonfungiblePositionManager: string;
    quoter: string;
    router: string;
    factory: string;
  };
}

// 分页参数
export interface PaginationParams {
  page: number;
  pageSize: number;
  total?: number;
}

// 搜索过滤参数
export interface FilterParams {
  search?: string;
  status?: PositionStatus[];
  chains?: ChainType[];
  pools?: string[];
  minValue?: number;
  maxValue?: number;
  sortBy?: 'value' | 'fees' | 'apr' | 'created_at';
  sortOrder?: 'asc' | 'desc';
} 
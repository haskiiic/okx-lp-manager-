import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { 
  LPPosition, 
  WalletBalance, 
  StatsData, 
  ChainType, 
  FilterParams, 
  RebalanceConfig,
  Pool 
} from '@/types';

// 应用主状态接口
interface AppState {
  // 基础状态
  loading: boolean;
  connected: boolean;
  currentWallet: string | null;
  selectedChain: ChainType;
  
  // 数据状态
  positions: LPPosition[];
  walletBalances: WalletBalance[];
  stats: StatsData | null;
  pools: Pool[];
  rebalanceConfigs: RebalanceConfig[];
  
  // 过滤和分页
  filters: FilterParams;
  pagination: {
    current: number;
    pageSize: number;
    total: number;
  };
  
  // WebSocket连接状态
  wsConnected: boolean;
  
  // Actions
  setLoading: (loading: boolean) => void;
  setConnected: (connected: boolean) => void;
  setCurrentWallet: (wallet: string | null) => void;
  setSelectedChain: (chain: ChainType) => void;
  
  // 数据更新
  setPositions: (positions: LPPosition[]) => void;
  updatePosition: (position: LPPosition) => void;
  removePosition: (positionId: string) => void;
  
  setWalletBalances: (balances: WalletBalance[]) => void;
  updateWalletBalance: (balance: WalletBalance) => void;
  
  setStats: (stats: StatsData | null) => void;
  updateStats: (partialStats: Partial<StatsData>) => void;
  
  setPools: (pools: Pool[]) => void;
  updatePool: (pool: Pool) => void;
  
  setRebalanceConfigs: (configs: RebalanceConfig[]) => void;
  updateRebalanceConfig: (config: RebalanceConfig) => void;
  removeRebalanceConfig: (configId: string) => void;
  
  // 过滤和搜索
  setFilters: (filters: Partial<FilterParams>) => void;
  clearFilters: () => void;
  
  // 分页
  setPagination: (pagination: Partial<{ current: number; pageSize: number; total: number }>) => void;
  
  // WebSocket
  setWsConnected: (connected: boolean) => void;
  
  // 重置状态
  reset: () => void;
}

// 初始状态
const initialState = {
  loading: false,
  connected: false,
  currentWallet: null,
  selectedChain: 'bsc' as ChainType,
  positions: [],
  walletBalances: [],
  stats: null,
  pools: [],
  rebalanceConfigs: [],
  filters: {},
  pagination: {
    current: 1,
    pageSize: 10,
    total: 0,
  },
  wsConnected: false,
};

// 创建store
export const useStore = create<AppState>()(
  subscribeWithSelector((set, get) => ({
    ...initialState,
    
    // 基础状态更新
    setLoading: (loading) => set({ loading }),
    setConnected: (connected) => set({ connected }),
    setCurrentWallet: (currentWallet) => set({ currentWallet }),
    setSelectedChain: (selectedChain) => set({ selectedChain }),
    
    // LP头寸管理
    setPositions: (positions) => set({ positions }),
    updatePosition: (position) => set((state) => ({
      positions: state.positions.map(p => 
        p.id === position.id ? position : p
      )
    })),
    removePosition: (positionId) => set((state) => ({
      positions: state.positions.filter(p => p.id !== positionId)
    })),
    
    // 钱包余额管理
    setWalletBalances: (walletBalances) => set({ walletBalances }),
    updateWalletBalance: (balance) => set((state) => ({
      walletBalances: state.walletBalances.map(b => 
        b.address === balance.address && b.chain === balance.chain ? balance : b
      )
    })),
    
    // 统计数据管理
    setStats: (stats: StatsData | null) => set({ stats }),
    updateStats: (partialStats: Partial<StatsData>) => set((state) => ({
      stats: state.stats ? { ...state.stats, ...partialStats } : null
    })),
    
    // 流动性池管理
    setPools: (pools) => set({ pools }),
    updatePool: (pool) => set((state) => ({
      pools: state.pools.map(p => 
        p.address === pool.address ? pool : p
      )
    })),
    
    // 重平衡配置管理
    setRebalanceConfigs: (rebalanceConfigs) => set({ rebalanceConfigs }),
    updateRebalanceConfig: (config) => set((state) => ({
      rebalanceConfigs: state.rebalanceConfigs.map(c => 
        c.id === config.id ? config : c
      )
    })),
    removeRebalanceConfig: (configId) => set((state) => ({
      rebalanceConfigs: state.rebalanceConfigs.filter(c => c.id !== configId)
    })),
    
    // 过滤器管理
    setFilters: (filters) => set((state) => ({
      filters: { ...state.filters, ...filters }
    })),
    clearFilters: () => set({ filters: {} }),
    
    // 分页管理
    setPagination: (pagination) => set((state) => ({
      pagination: { ...state.pagination, ...pagination }
    })),
    
    // WebSocket状态
    setWsConnected: (wsConnected) => set({ wsConnected }),
    
    // 重置所有状态
    reset: () => set(initialState),
  }))
);

// 选择器hooks - 提供性能优化的状态选择
export const usePositions = () => useStore(state => state.positions);
export const useStats = () => useStore(state => state.stats);
export const useLoading = () => useStore(state => state.loading);
export const useConnected = () => useStore(state => state.connected);
export const useCurrentWallet = () => useStore(state => state.currentWallet);
export const useSelectedChain = () => useStore(state => state.selectedChain);
export const useWalletBalances = () => useStore(state => state.walletBalances);
export const usePools = () => useStore(state => state.pools);
export const useFilters = () => useStore(state => state.filters);
export const usePagination = () => useStore(state => state.pagination);
export const useWsConnected = () => useStore(state => state.wsConnected);
export const useRebalanceConfigs = () => useStore(state => state.rebalanceConfigs);

// 计算衍生状态的hooks
export const useFilteredPositions = () => {
  return useStore(state => {
    const { positions, filters } = state;
    let filtered = positions;
    
    // 按状态过滤
    if (filters.status && filters.status.length > 0) {
      filtered = filtered.filter(p => filters.status!.includes(p.status));
    }
    
    // 按链过滤
    if (filters.chains && filters.chains.length > 0) {
      // 这里需要根据pool地址判断链，暂时跳过
    }
    
    // 按搜索词过滤
    if (filters.search) {
      const search = filters.search.toLowerCase();
      filtered = filtered.filter(p => 
        p.pool.token0.symbol.toLowerCase().includes(search) ||
        p.pool.token1.symbol.toLowerCase().includes(search) ||
        p.id.toLowerCase().includes(search)
      );
    }
    
    // 按价值范围过滤
    if (filters.minValue !== undefined) {
      filtered = filtered.filter(p => p.valueUSD >= filters.minValue!);
    }
    if (filters.maxValue !== undefined) {
      filtered = filtered.filter(p => p.valueUSD <= filters.maxValue!);
    }
    
    // 排序
    if (filters.sortBy) {
      filtered.sort((a, b) => {
        let aValue: number, bValue: number;
        
        switch (filters.sortBy) {
          case 'value':
            aValue = a.valueUSD;
            bValue = b.valueUSD;
            break;
          case 'fees':
            aValue = a.feesEarnedUSD;
            bValue = b.feesEarnedUSD;
            break;
          case 'created_at':
            aValue = new Date(a.createdAt).getTime();
            bValue = new Date(b.createdAt).getTime();
            break;
          default:
            return 0;
        }
        
        return filters.sortOrder === 'desc' ? bValue - aValue : aValue - bValue;
      });
    }
    
    return filtered;
  });
};

// 获取当前选择链的钱包余额
export const useCurrentChainBalance = () => {
  return useStore(state => {
    const { walletBalances, selectedChain, currentWallet } = state;
    return walletBalances.find(b => 
      b.chain === selectedChain && b.address === currentWallet
    );
  });
}; 
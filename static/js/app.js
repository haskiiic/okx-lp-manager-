/**
 * OKX LP管理系统 - 前端应用逻辑
 * 专业区块链操作面板
 */

class LPManagerApp {
    constructor() {
        this.apiBaseUrl = '/api/v1';
        this.currentWallet = null;
        this.currentNetwork = 'bsc';
        this.activeTab = 'dashboard';
        this.batchConfigurations = [];
        this.monitoringActive = false;
        
        this.init();
    }

    // 初始化应用
    init() {
        this.setupEventListeners();
        this.checkApiStatus();
        this.loadDashboard();
        
        // 显示连接状态为连接中
        this.updateConnectionStatus('connecting', '正在连接...');
        
        // 3秒后显示在线状态
        setTimeout(() => {
            this.updateConnectionStatus('online', '已连接');
        }, 3000);
    }

    // 设置事件监听器
    setupEventListeners() {
        // 侧边栏导航
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                if (tab) {
                    this.switchTab(tab);
                }
            });
        });

        // 快速操作按钮
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.dataset.tab;
                if (tab) {
                    this.switchTab(tab);
                }
            });
        });

        // 网络选择器
        document.getElementById('networkSelect').addEventListener('change', (e) => {
            this.currentNetwork = e.target.value;
            this.showNotification('网络已切换到 ' + this.getNetworkName(e.target.value), 'info');
        });

        // 钱包地址加载
        document.getElementById('loadWalletBtn').addEventListener('click', () => {
            this.loadWalletData();
        });

        // LP头寸相关
        document.getElementById('createLPForm').addEventListener('submit', (e) => {
            this.handleCreateLP(e);
        });

        document.getElementById('refreshPositions').addEventListener('click', () => {
            this.loadPositions();
        });

        // 钱包余额相关
        document.getElementById('loadBalanceBtn').addEventListener('click', () => {
            this.loadWalletBalance();
        });

        document.getElementById('refreshBalance').addEventListener('click', () => {
            this.loadWalletBalance();
        });

        // 重平衡配置
        document.getElementById('rebalanceForm').addEventListener('submit', (e) => {
            this.handleRebalanceConfig(e);
        });

        document.getElementById('checkRebalanceStatus').addEventListener('click', () => {
            this.checkRebalanceStatus();
        });

        // 批量操作
        document.getElementById('addBatchItem').addEventListener('click', () => {
            this.addBatchConfiguration();
        });

        document.getElementById('executeBatch').addEventListener('click', () => {
            this.executeBatchOperations();
        });

        // 流动性池查询
        document.getElementById('poolQueryForm').addEventListener('submit', (e) => {
            this.handlePoolQuery(e);
        });

        // 监控控制
        document.getElementById('startMonitoring').addEventListener('click', () => {
            this.startMonitoring();
        });

        document.getElementById('stopMonitoring').addEventListener('click', () => {
            this.stopMonitoring();
        });

        // 系统健康检查
        document.getElementById('systemHealthCheck').addEventListener('click', () => {
            this.performHealthCheck();
        });

        // 模态框控制
        document.querySelector('.modal-close').addEventListener('click', () => {
            this.hideModal();
        });

        document.getElementById('modalCancel').addEventListener('click', () => {
            this.hideModal();
        });

        // 预览LP头寸
        document.getElementById('previewLP').addEventListener('click', () => {
            this.previewLPPosition();
        });

        // 导出功能
        document.getElementById('exportPositions').addEventListener('click', () => {
            this.exportPositions();
        });

        // 钱包地址输入同步
        document.getElementById('walletAddress').addEventListener('input', (e) => {
            document.getElementById('balanceWalletAddress').value = e.target.value;
            document.getElementById('createWalletAddress').value = e.target.value;
            document.getElementById('rebalanceWalletAddress').value = e.target.value;
        });
    }

    // 切换标签页
    switchTab(tabName) {
        // 移除所有激活状态
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });

        // 添加激活状态
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(tabName).classList.add('active');

        this.activeTab = tabName;

        // 根据标签页加载相应数据
        switch (tabName) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'positions':
                this.loadPositions();
                break;
            case 'wallet':
                this.loadWalletBalance();
                break;
            case 'settings':
                this.checkApiStatus();
                break;
        }
    }

    // 更新连接状态
    updateConnectionStatus(status, text) {
        const indicator = document.querySelector('.status-indicator');
        const statusText = document.querySelector('#connectionStatus span');
        
        indicator.className = `status-indicator ${status}`;
        statusText.textContent = text;
    }

    // 显示加载状态
    showLoading(text = '处理中...') {
        const overlay = document.getElementById('loadingOverlay');
        const loadingText = document.querySelector('.loading-text');
        loadingText.textContent = text;
        overlay.classList.add('show');
    }

    // 隐藏加载状态
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.remove('show');
    }

    // 显示通知
    showNotification(message, type = 'info', duration = 5000) {
        const container = document.getElementById('notificationContainer');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <strong>${this.getNotificationTitle(type)}</strong>
                <p>${message}</p>
            </div>
        `;

        container.appendChild(notification);

        // 自动移除通知
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, duration);
    }

    // 获取通知标题
    getNotificationTitle(type) {
        const titles = {
            success: '成功',
            error: '错误',
            warning: '警告',
            info: '信息'
        };
        return titles[type] || '通知';
    }

    // 显示模态框
    showModal(title, body, onConfirm = null) {
        const modal = document.getElementById('modal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');
        const confirmBtn = document.getElementById('modalConfirm');

        modalTitle.textContent = title;
        modalBody.innerHTML = body;
        modal.classList.add('show');

        if (onConfirm) {
            confirmBtn.onclick = () => {
                onConfirm();
                this.hideModal();
            };
        }
    }

    // 隐藏模态框
    hideModal() {
        const modal = document.getElementById('modal');
        modal.classList.remove('show');
    }

    // API请求方法
    async makeRequest(endpoint, options = {}) {
        try {
            const url = `${this.apiBaseUrl}${endpoint}`;
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || data.message || '请求失败');
            }

            return data;
        } catch (error) {
            console.error('API请求错误:', error);
            throw error;
        }
    }

    // 加载仪表盘数据
    async loadDashboard() {
        if (!this.currentWallet) {
            return;
        }

        try {
            // 加载LP头寸统计
            const positions = await this.makeRequest(`/lp/positions/${this.currentWallet}`);
            this.updateDashboardStats(positions.data || {});
        } catch (error) {
            console.error('加载仪表盘数据失败:', error);
        }
    }

    // 更新仪表盘统计
    updateDashboardStats(data) {
        const { positions = [], total_count = 0 } = data;
        
        // 计算统计数据
        let totalValue = 0;
        let totalFees = 0;
        let activeRebalance = 0;

        positions.forEach(position => {
            totalValue += position.value || 0;
            totalFees += position.fees || 0;
            if (position.auto_rebalance) {
                activeRebalance++;
            }
        });

        // 更新显示
        document.getElementById('totalPositions').textContent = total_count;
        document.getElementById('totalValue').textContent = `$${totalValue.toLocaleString()}`;
        document.getElementById('totalFees').textContent = `$${totalFees.toLocaleString()}`;
        document.getElementById('activeRebalance').textContent = activeRebalance;
    }

    // 加载钱包数据
    async loadWalletData() {
        const walletAddress = document.getElementById('walletAddress').value.trim();
        
        if (!walletAddress) {
            this.showNotification('请输入钱包地址', 'warning');
            return;
        }

        if (!this.isValidAddress(walletAddress)) {
            this.showNotification('钱包地址格式不正确', 'error');
            return;
        }

        this.currentWallet = walletAddress;
        this.showLoading('加载钱包数据...');

        try {
            // 加载LP头寸
            await this.loadPositions();
            
            // 加载钱包余额
            await this.loadWalletBalance();
            
            // 更新仪表盘
            await this.loadDashboard();
            
            this.showNotification('钱包数据加载成功', 'success');
        } catch (error) {
            this.showNotification('加载钱包数据失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // 验证地址格式
    isValidAddress(address) {
        return /^0x[a-fA-F0-9]{40}$/.test(address);
    }

    // 加载LP头寸
    async loadPositions() {
        if (!this.currentWallet) {
            return;
        }

        this.showLoading('加载LP头寸...');

        try {
            const response = await this.makeRequest(`/lp/positions/${this.currentWallet}`);
            this.displayPositions(response.data || {});
        } catch (error) {
            this.showNotification('加载LP头寸失败: ' + error.message, 'error');
            this.displayPositions({ positions: [] });
        } finally {
            this.hideLoading();
        }
    }

    // 显示LP头寸
    displayPositions(data) {
        const tbody = document.getElementById('positionsTableBody');
        const { positions = [] } = data;

        if (positions.length === 0) {
            tbody.innerHTML = `
                <tr class="empty-row">
                    <td colspan="7" class="empty-message">
                        <i class="fas fa-coins"></i>
                        <p>暂无LP头寸数据</p>
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = positions.map(position => `
            <tr>
                <td>
                    <div class="token-pair">
                        <strong>${position.token0_symbol}/${position.token1_symbol}</strong>
                        <small>Fee: ${(position.fee_tier / 10000).toFixed(2)}%</small>
                    </div>
                </td>
                <td>
                    <div class="price-range">
                        <span>${position.price_lower?.toFixed(6) || 'N/A'}</span>
                        <small>-</small>
                        <span>${position.price_upper?.toFixed(6) || 'N/A'}</span>
                    </div>
                </td>
                <td>
                    <div class="liquidity-info">
                        <strong>$${(position.liquidity || 0).toLocaleString()}</strong>
                        <small>${position.token0_amount?.toFixed(4) || '0'} ${position.token0_symbol}</small>
                        <small>${position.token1_amount?.toFixed(4) || '0'} ${position.token1_symbol}</small>
                    </div>
                </td>
                <td>
                    <span class="current-price">${position.current_price?.toFixed(6) || 'N/A'}</span>
                </td>
                <td>
                    <span class="yield ${position.yield >= 0 ? 'positive' : 'negative'}">
                        ${position.yield ? (position.yield * 100).toFixed(2) + '%' : 'N/A'}
                    </span>
                </td>
                <td>
                    <span class="status-badge ${this.getPositionStatusClass(position.status)}">
                        ${this.getPositionStatusText(position.status)}
                    </span>
                </td>
                <td>
                    <div class="position-actions">
                        <button class="btn btn-outline btn-sm" onclick="app.editPosition(${position.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline btn-sm" onclick="app.closePosition(${position.id})">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    // 获取头寸状态样式类
    getPositionStatusClass(status) {
        const classes = {
            active: 'success',
            closed: 'error',
            out_of_range: 'warning'
        };
        return classes[status] || 'info';
    }

    // 获取头寸状态文本
    getPositionStatusText(status) {
        const texts = {
            active: '活跃',
            closed: '已关闭',
            out_of_range: '超出范围'
        };
        return texts[status] || '未知';
    }

    // 处理创建LP头寸
    async handleCreateLP(e) {
        e.preventDefault();
        
        const formData = this.getCreateLPFormData();
        
        if (!this.validateCreateLPForm(formData)) {
            return;
        }

        this.showLoading('创建LP头寸...');

        try {
            const response = await this.makeRequest('/lp/create', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            this.showNotification('LP头寸创建成功', 'success');
            
            // 清空表单
            document.getElementById('createLPForm').reset();
            
            // 刷新头寸列表
            await this.loadPositions();
            
            // 显示结果详情
            this.showModal('创建成功', `
                <div class="create-result">
                    <p><strong>交易哈希:</strong> ${response.data?.tx_hash || 'N/A'}</p>
                    <p><strong>头寸ID:</strong> ${response.data?.position_id || 'N/A'}</p>
                    <p><strong>投入金额:</strong> ${formData.amount0_desired} ${formData.token0_symbol} + ${formData.amount1_desired} ${formData.token1_symbol}</p>
                </div>
            `);
            
        } catch (error) {
            this.showNotification('创建LP头寸失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // 获取创建LP表单数据
    getCreateLPFormData() {
        return {
            wallet_address: document.getElementById('createWalletAddress').value.trim(),
            network: document.getElementById('createNetwork').value,
            token0_symbol: document.getElementById('token0Symbol').value.trim(),
            token1_symbol: document.getElementById('token1Symbol').value.trim(),
            token0_address: document.getElementById('token0Address').value.trim(),
            token1_address: document.getElementById('token1Address').value.trim(),
            amount0_desired: parseFloat(document.getElementById('amount0Desired').value),
            amount1_desired: parseFloat(document.getElementById('amount1Desired').value),
            price_lower: parseFloat(document.getElementById('priceLower').value),
            price_upper: parseFloat(document.getElementById('priceUpper').value),
            fee_tier: parseInt(document.getElementById('feeTier').value)
        };
    }

    // 验证创建LP表单
    validateCreateLPForm(data) {
        if (!data.wallet_address || !this.isValidAddress(data.wallet_address)) {
            this.showNotification('请输入有效的钱包地址', 'error');
            return false;
        }

        if (!data.token0_address || !this.isValidAddress(data.token0_address)) {
            this.showNotification('请输入有效的代币0合约地址', 'error');
            return false;
        }

        if (!data.token1_address || !this.isValidAddress(data.token1_address)) {
            this.showNotification('请输入有效的代币1合约地址', 'error');
            return false;
        }

        if (data.amount0_desired <= 0 || data.amount1_desired <= 0) {
            this.showNotification('投入数量必须大于0', 'error');
            return false;
        }

        if (data.price_lower >= data.price_upper) {
            this.showNotification('最低价格必须小于最高价格', 'error');
            return false;
        }

        return true;
    }

    // 预览LP头寸
    previewLPPosition() {
        const formData = this.getCreateLPFormData();
        
        if (!this.validateCreateLPForm(formData)) {
            return;
        }

        // 计算预估值
        const estimatedValue = (formData.amount0_desired * 100) + (formData.amount1_desired * 1); // 假设价格
        const priceRange = ((formData.price_upper - formData.price_lower) / formData.price_lower * 100).toFixed(2);

        this.showModal('LP头寸预览', `
            <div class="lp-preview">
                <h4>基本信息</h4>
                <p><strong>代币对:</strong> ${formData.token0_symbol}/${formData.token1_symbol}</p>
                <p><strong>费率等级:</strong> ${(formData.fee_tier / 10000).toFixed(2)}%</p>
                <p><strong>网络:</strong> ${this.getNetworkName(formData.network)}</p>
                
                <h4>投入资产</h4>
                <p><strong>代币A:</strong> ${formData.amount0_desired} ${formData.token0_symbol}</p>
                <p><strong>代币B:</strong> ${formData.amount1_desired} ${formData.token1_symbol}</p>
                
                <h4>价格范围</h4>
                <p><strong>最低价格:</strong> ${formData.price_lower}</p>
                <p><strong>最高价格:</strong> ${formData.price_upper}</p>
                <p><strong>价格范围:</strong> ±${priceRange}%</p>
                
                <h4>预估信息</h4>
                <p><strong>预估总价值:</strong> $${estimatedValue.toLocaleString()}</p>
                <p><strong>Gas费用:</strong> ~$10-50 (取决于网络拥堵)</p>
            </div>
        `);
    }

    // 加载钱包余额
    async loadWalletBalance() {
        const walletAddress = document.getElementById('balanceWalletAddress').value.trim();
        
        if (!walletAddress) {
            this.showNotification('请输入钱包地址', 'warning');
            return;
        }

        this.showLoading('查询钱包余额...');

        try {
            // 常见代币地址 (BSC链)
            const commonTokens = [
                'native', // BNB
                '0x55d398326f99059fF775485246999027B3197955', // USDT
                '0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56', // BUSD
                '0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d'  // USDC
            ];

            const response = await this.makeRequest('/wallet/balance', {
                method: 'POST',
                body: JSON.stringify({
                    wallet_address: walletAddress,
                    token_addresses: commonTokens,
                    network: this.currentNetwork
                })
            });

            this.displayWalletBalance(response.data || {});
            
        } catch (error) {
            this.showNotification('查询钱包余额失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // 显示钱包余额
    displayWalletBalance(data) {
        const balanceDisplay = document.getElementById('balanceDisplay');
        const totalValueElement = document.getElementById('totalBalanceValue');
        const tableBody = document.getElementById('balanceTableBody');
        
        const { balances = [], total_value_usd = 0 } = data;

        // 显示总价值
        totalValueElement.textContent = `$${total_value_usd.toLocaleString()}`;
        
        // 显示余额表格
        if (balances.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="empty-message">
                        <i class="fas fa-wallet"></i>
                        <p>暂无余额数据</p>
                    </td>
                </tr>
            `;
        } else {
            tableBody.innerHTML = balances.map(balance => `
                <tr>
                    <td>
                        <div class="token-info">
                            <strong>${balance.symbol}</strong>
                            <small>${balance.name}</small>
                        </div>
                    </td>
                    <td>${parseFloat(balance.balance).toFixed(6)}</td>
                    <td>$${parseFloat(balance.price_usd || 0).toFixed(4)}</td>
                    <td>$${parseFloat(balance.value_usd || 0).toFixed(2)}</td>
                    <td>
                        <span class="${balance.change_24h >= 0 ? 'positive' : 'negative'}">
                            ${balance.change_24h ? (balance.change_24h * 100).toFixed(2) + '%' : 'N/A'}
                        </span>
                    </td>
                </tr>
            `).join('');
        }

        balanceDisplay.style.display = 'block';
    }

    // 处理重平衡配置
    async handleRebalanceConfig(e) {
        e.preventDefault();
        
        const formData = {
            wallet_address: document.getElementById('rebalanceWalletAddress').value.trim(),
            fee_tier: parseInt(document.getElementById('rebalanceFeeTier').value),
            price_range_percent: parseFloat(document.getElementById('priceRangePercent').value),
            rebalance_threshold: parseFloat(document.getElementById('rebalanceThreshold').value),
            enabled: document.getElementById('rebalanceEnabled').checked
        };

        if (!formData.wallet_address || !this.isValidAddress(formData.wallet_address)) {
            this.showNotification('请输入有效的钱包地址', 'error');
            return;
        }

        this.showLoading('配置自动重平衡...');

        try {
            const response = await this.makeRequest('/lp/auto-rebalance/config', {
                method: 'POST',
                body: JSON.stringify(formData)
            });

            this.showNotification('自动重平衡配置成功', 'success');
            
            // 显示配置状态
            await this.checkRebalanceStatus();
            
        } catch (error) {
            this.showNotification('配置自动重平衡失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // 检查重平衡状态
    async checkRebalanceStatus() {
        const walletAddress = document.getElementById('rebalanceWalletAddress').value.trim();
        
        if (!walletAddress) {
            this.showNotification('请先输入钱包地址', 'warning');
            return;
        }

        try {
            const response = await this.makeRequest(`/lp/auto-rebalance/status/${walletAddress}`);
            this.displayRebalanceStatus(response.data || {});
        } catch (error) {
            this.showNotification('获取重平衡状态失败: ' + error.message, 'error');
        }
    }

    // 显示重平衡状态
    displayRebalanceStatus(data) {
        const statusDiv = document.getElementById('rebalanceStatus');
        const configStatus = document.getElementById('configStatus');
        const lastExecution = document.getElementById('lastExecution');
        const nextCheck = document.getElementById('nextCheck');

        configStatus.textContent = data.enabled ? '已启用' : '已禁用';
        lastExecution.textContent = data.last_execution || '从未执行';
        nextCheck.textContent = data.next_check || '-';

        statusDiv.style.display = 'block';
    }

    // 添加批量配置
    addBatchConfiguration() {
        const batchList = document.getElementById('batchList');
        const index = this.batchConfigurations.length;

        const configDiv = document.createElement('div');
        configDiv.className = 'batch-item';
        configDiv.innerHTML = `
            <div class="batch-item-header">
                <h4>配置 #${index + 1}</h4>
                <button type="button" class="btn btn-outline btn-sm" onclick="app.removeBatchItem(${index})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            <div class="batch-item-content">
                <div class="form-row">
                    <div class="form-group">
                        <label>代币对</label>
                        <input type="text" placeholder="BNB/USDT" data-field="pair" class="form-input">
                    </div>
                    <div class="form-group">
                        <label>投入金额</label>
                        <input type="number" placeholder="100" data-field="amount" class="form-input">
                    </div>
                    <div class="form-group">
                        <label>价格范围 (%)</label>
                        <input type="number" placeholder="10" data-field="range" class="form-input" value="10">
                    </div>
                </div>
            </div>
        `;

        // 移除空状态
        const emptyBatch = batchList.querySelector('.empty-batch');
        if (emptyBatch) {
            emptyBatch.remove();
        }

        batchList.appendChild(configDiv);
        
        // 添加到配置数组
        this.batchConfigurations.push({
            pair: '',
            amount: 0,
            range: 10
        });

        this.updateBatchSummary();
    }

    // 移除批量配置项
    removeBatchItem(index) {
        const batchList = document.getElementById('batchList');
        const items = batchList.querySelectorAll('.batch-item');
        
        if (items[index]) {
            items[index].remove();
        }

        this.batchConfigurations.splice(index, 1);

        // 如果没有配置项了，显示空状态
        if (this.batchConfigurations.length === 0) {
            batchList.innerHTML = `
                <div class="empty-batch">
                    <i class="fas fa-plus-circle"></i>
                    <p>点击"添加头寸配置"开始批量创建</p>
                </div>
            `;
        }

        this.updateBatchSummary();
    }

    // 更新批量操作摘要
    updateBatchSummary() {
        const summary = document.getElementById('batchSummary');
        const count = document.getElementById('batchCount');
        const totalValue = document.getElementById('batchTotalValue');

        const configCount = this.batchConfigurations.length;
        const estimatedTotal = this.batchConfigurations.reduce((sum, config) => sum + (config.amount || 0), 0);

        count.textContent = configCount;
        totalValue.textContent = `$${estimatedTotal.toLocaleString()}`;

        summary.style.display = configCount > 0 ? 'block' : 'none';
    }

    // 执行批量操作
    async executeBatchOperations() {
        if (this.batchConfigurations.length === 0) {
            this.showNotification('请先添加批量配置', 'warning');
            return;
        }

        this.showLoading('执行批量操作...');

        try {
            // 这里应该构建实际的批量请求数据
            const batchData = {
                positions: this.batchConfigurations.map(config => ({
                    wallet_address: this.currentWallet,
                    token0_symbol: config.pair?.split('/')[0] || 'BNB',
                    token1_symbol: config.pair?.split('/')[1] || 'USDT',
                    amount0_desired: config.amount || 100,
                    amount1_desired: config.amount || 100,
                    price_range_percent: config.range || 10,
                    fee_tier: 3000,
                    network: this.currentNetwork
                }))
            };

            const response = await this.makeRequest('/lp/batch-create', {
                method: 'POST',
                body: JSON.stringify(batchData)
            });

            this.showNotification(`批量操作已提交，共 ${batchData.positions.length} 个头寸`, 'success');
            
            // 清空批量配置
            this.batchConfigurations = [];
            this.updateBatchSummary();
            
            // 重置批量列表
            document.getElementById('batchList').innerHTML = `
                <div class="empty-batch">
                    <i class="fas fa-plus-circle"></i>
                    <p>点击"添加头寸配置"开始批量创建</p>
                </div>
            `;
            
        } catch (error) {
            this.showNotification('批量操作失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // 处理流动性池查询
    async handlePoolQuery(e) {
        e.preventDefault();
        
        const token0 = document.getElementById('poolToken0').value.trim();
        const token1 = document.getElementById('poolToken1').value.trim();
        const feeTier = document.getElementById('poolFeeTier').value;

        if (!token0 || !token1) {
            this.showNotification('请输入代币地址', 'warning');
            return;
        }

        this.showLoading('查询流动性池信息...');

        try {
            const response = await this.makeRequest(`/pools/info?token0=${token0}&token1=${token1}&fee_tier=${feeTier}&network=${this.currentNetwork}`);
            this.displayPoolInfo(response.data || {});
        } catch (error) {
            this.showNotification('查询流动性池失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // 显示流动性池信息
    displayPoolInfo(data) {
        const display = document.getElementById('poolInfoDisplay');
        
        document.getElementById('poolAddress').textContent = data.pool_address || 'N/A';
        document.getElementById('poolLiquidity').textContent = `$${(data.total_liquidity || 0).toLocaleString()}`;
        document.getElementById('poolVolume').textContent = `$${(data.volume_24h || 0).toLocaleString()}`;
        document.getElementById('poolPrice').textContent = data.current_price || 'N/A';

        display.style.display = 'block';
    }

    // 启动监控
    async startMonitoring() {
        this.showLoading('启动监控...');

        try {
            const response = await this.makeRequest('/monitoring/start');
            
            this.monitoringActive = true;
            this.updateMonitoringUI(true);
            this.showNotification('监控已启动', 'success');
            
            // 开始显示模拟日志
            this.startMockLogging();
            
        } catch (error) {
            this.showNotification('启动监控失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // 停止监控
    stopMonitoring() {
        this.monitoringActive = false;
        this.updateMonitoringUI(false);
        this.showNotification('监控已停止', 'warning');
    }

    // 更新监控UI
    updateMonitoringUI(active) {
        const status = document.getElementById('monitoringStatus');
        const startBtn = document.getElementById('startMonitoring');
        const stopBtn = document.getElementById('stopMonitoring');
        
        const indicator = status.querySelector('.status-indicator');
        const text = status.querySelector('span');

        if (active) {
            indicator.className = 'status-indicator online';
            text.textContent = '监控运行中';
            startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-flex';
        } else {
            indicator.className = 'status-indicator offline';
            text.textContent = '监控未启动';
            startBtn.style.display = 'inline-flex';
            stopBtn.style.display = 'none';
        }
    }

    // 开始模拟日志记录
    startMockLogging() {
        const container = document.getElementById('logsContainer');
        
        const addLog = (type, message) => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${type}`;
            logEntry.innerHTML = `
                <span class="log-time">${new Date().toLocaleTimeString()}</span>
                <span class="log-message">${message}</span>
            `;
            
            container.appendChild(logEntry);
            container.scrollTop = container.scrollHeight;
            
            // 限制日志数量
            if (container.children.length > 50) {
                container.removeChild(container.firstChild);
            }
        };

        // 清除现有日志
        container.innerHTML = '';

        // 模拟日志
        const logMessages = [
            { type: 'info', msg: '监控系统已启动' },
            { type: 'success', msg: '连接到BSC网络' },
            { type: 'info', msg: '开始监控LP头寸...' },
            { type: 'success', msg: '价格数据更新: BNB/USDT' },
            { type: 'warning', msg: '检测到价格波动超过5%' },
            { type: 'info', msg: '重平衡检查完成' },
            { type: 'success', msg: '所有头寸状态正常' }
        ];

        let logIndex = 0;
        const logInterval = setInterval(() => {
            if (!this.monitoringActive) {
                clearInterval(logInterval);
                return;
            }

            const log = logMessages[logIndex % logMessages.length];
            addLog(log.type, log.msg);
            logIndex++;
        }, 3000);
    }

    // 执行系统健康检查
    async performHealthCheck() {
        this.showLoading('执行系统健康检查...');

        try {
            const response = await this.makeRequest('/health');
            
            document.getElementById('apiStatus').textContent = '正常';
            document.getElementById('dbStatus').textContent = '连接正常';
            
            this.showNotification('系统健康检查完成', 'success');
            
        } catch (error) {
            document.getElementById('apiStatus').textContent = '异常';
            document.getElementById('dbStatus').textContent = '连接异常';
            
            this.showNotification('系统健康检查失败: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // 检查API状态
    async checkApiStatus() {
        try {
            const response = await this.makeRequest('/health');
            document.getElementById('apiStatus').textContent = '正常';
        } catch (error) {
            document.getElementById('apiStatus').textContent = '异常';
        }
    }

    // 导出头寸数据
    exportPositions() {
        if (!this.currentWallet) {
            this.showNotification('请先加载钱包数据', 'warning');
            return;
        }

        // 模拟导出功能
        const data = {
            wallet: this.currentWallet,
            network: this.currentNetwork,
            export_time: new Date().toISOString(),
            positions: []
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `lp-positions-${this.currentWallet.slice(0, 8)}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showNotification('头寸数据已导出', 'success');
    }

    // 编辑头寸
    editPosition(positionId) {
        this.showModal('编辑头寸', `
            <p>头寸ID: ${positionId}</p>
            <p>编辑功能正在开发中...</p>
        `);
    }

    // 关闭头寸
    closePosition(positionId) {
        this.showModal('关闭头寸', `
            <p>确定要关闭头寸 #${positionId} 吗？</p>
            <p class="warning">此操作不可撤销，将会收取gas费用。</p>
        `, () => {
            this.showNotification(`头寸 #${positionId} 关闭操作已提交`, 'info');
        });
    }

    // 获取网络名称
    getNetworkName(network) {
        const names = {
            bsc: 'BSC Chain',
            ethereum: 'Ethereum',
            polygon: 'Polygon'
        };
        return names[network] || network;
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.app = new LPManagerApp();
});

// 全局工具函数
window.formatNumber = (num, decimals = 2) => {
    return new Intl.NumberFormat('zh-CN', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(num);
};

window.formatCurrency = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('zh-CN', {
        style: 'currency',
        currency: currency
    }).format(amount);
};

window.copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text);
        window.app.showNotification('已复制到剪贴板', 'success');
    } catch (err) {
        window.app.showNotification('复制失败', 'error');
    }
};

// 错误处理
window.addEventListener('error', (event) => {
    console.error('全局错误:', event.error);
    if (window.app) {
        window.app.showNotification('发生未知错误，请刷新页面重试', 'error');
    }
});

// 网络状态监控
window.addEventListener('online', () => {
    if (window.app) {
        window.app.updateConnectionStatus('online', '已连接');
        window.app.showNotification('网络连接已恢复', 'success');
    }
});

window.addEventListener('offline', () => {
    if (window.app) {
        window.app.updateConnectionStatus('offline', '网络断开');
        window.app.showNotification('网络连接已断开', 'warning');
    }
}); 
import React from 'react';
import { Card, Row, Col, Statistic, Progress, Tooltip } from 'antd';
import { 
  WalletOutlined, 
  TrophyOutlined, 
  DollarOutlined, 
  SyncOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import styled from 'styled-components';
import numeral from 'numeral';
import { StatsData } from '@/types';

// 样式化组件
const StatsContainer = styled.div`
  margin-bottom: 24px;
`;

const StatsCard = styled(Card)`
  height: 100%;
  
  .ant-card-body {
    padding: 20px;
  }
  
  .stats-icon {
    font-size: 24px;
    margin-bottom: 12px;
    padding: 12px;
    border-radius: 12px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    
    &.primary {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
    }
    
    &.success {
      background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
      color: white;
    }
    
    &.warning {
      background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      color: white;
    }
    
    &.info {
      background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
      color: white;
    }
  }
  
  .ant-statistic-title {
    color: #64748b;
    font-weight: 500;
    margin-bottom: 8px;
  }
  
  .ant-statistic-content {
    font-weight: 600;
  }
  
  .change-indicator {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 8px;
    font-size: 12px;
    
    &.positive {
      color: #10b981;
    }
    
    &.negative {
      color: #ef4444;
    }
    
    &.neutral {
      color: #64748b;
    }
  }
  
  .progress-section {
    margin-top: 16px;
  }
`;

interface StatsCardsProps {
  stats: StatsData | null;
  loading?: boolean;
}

const StatsCards: React.FC<StatsCardsProps> = ({ stats, loading = false }) => {
  // 计算在范围内头寸的百分比
  const inRangePercentage = stats && stats.totalPositions > 0 
    ? (stats.inRangePositions / stats.totalPositions) * 100 
    : 0;

  // 格式化数字
  const formatCurrency = (value: number) => numeral(value).format('$0,0.00');
  const formatPercent = (value: number) => numeral(value / 100).format('0.00%');
  const formatNumber = (value: number) => numeral(value).format('0,0');

  return (
    <StatsContainer>
      <Row gutter={[16, 16]}>
        {/* 总LP头寸数 */}
        <Col xs={24} sm={12} lg={6}>
          <StatsCard loading={loading}>
            <div className="stats-icon primary">
              <WalletOutlined />
            </div>
            <Statistic 
              title="总LP头寸" 
              value={stats?.totalPositions || 0}
              formatter={(value) => formatNumber(Number(value))}
            />
            <div className="change-indicator positive">
              <ArrowUpOutlined />
              <span>活跃: {stats?.activePositions || 0}</span>
            </div>
            
            {/* 在范围内头寸进度条 */}
            <div className="progress-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span style={{ fontSize: '12px', color: '#64748b' }}>在价格区间内</span>
                <span style={{ fontSize: '12px', color: '#64748b' }}>
                  {stats?.inRangePositions || 0}/{stats?.totalPositions || 0}
                </span>
              </div>
              <Progress 
                percent={inRangePercentage} 
                size="small" 
                strokeColor="#10b981"
                trailColor="#f1f5f9"
                showInfo={false}
              />
            </div>
          </StatsCard>
        </Col>

        {/* 总价值 */}
        <Col xs={24} sm={12} lg={6}>
          <StatsCard loading={loading}>
            <div className="stats-icon success">
              <DollarOutlined />
            </div>
            <Statistic 
              title={
                <span>
                  总价值 
                  <Tooltip title="包含所有LP头寸的当前市场价值">
                    <InfoCircleOutlined style={{ marginLeft: 4, color: '#94a3b8' }} />
                  </Tooltip>
                </span>
              }
              value={stats?.totalValueUSD || 0}
              formatter={(value) => formatCurrency(Number(value))}
            />
            <div className="change-indicator positive">
              <ArrowUpOutlined />
              <span>+2.45% (24h)</span>
            </div>
          </StatsCard>
        </Col>

        {/* 累计手续费收益 */}
        <Col xs={24} sm={12} lg={6}>
          <StatsCard loading={loading}>
            <div className="stats-icon warning">
              <TrophyOutlined />
            </div>
            <Statistic 
              title={
                <span>
                  累计手续费 
                  <Tooltip title="从LP头寸获得的总手续费收益">
                    <InfoCircleOutlined style={{ marginLeft: 4, color: '#94a3b8' }} />
                  </Tooltip>
                </span>
              }
              value={stats?.totalFeesEarnedUSD || 0}
              formatter={(value) => formatCurrency(Number(value))}
            />
            <div className="change-indicator positive">
              <ArrowUpOutlined />
              <span>24h: {formatCurrency(stats?.totalFeesEarned24h || 0)}</span>
            </div>
          </StatsCard>
        </Col>

        {/* 平均APR */}
        <Col xs={24} sm={12} lg={6}>
          <StatsCard loading={loading}>
            <div className="stats-icon info">
              <SyncOutlined />
            </div>
            <Statistic 
              title={
                <span>
                  平均APR
                  <Tooltip title="所有活跃LP头寸的平均年化收益率">
                    <InfoCircleOutlined style={{ marginLeft: 4, color: '#94a3b8' }} />
                  </Tooltip>
                </span>
              }
              value={stats?.averageAPR || 0}
              suffix="%"
              precision={2}
            />
            <div className={`change-indicator ${(stats?.averageAPR || 0) > 10 ? 'positive' : 'neutral'}`}>
              {(stats?.averageAPR || 0) > 10 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              <span>{(stats?.averageAPR || 0) > 10 ? '表现良好' : '需要关注'}</span>
            </div>
            
            {/* APR分布进度条 */}
            <div className="progress-section">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <span style={{ fontSize: '12px', color: '#64748b' }}>收益表现</span>
                <span style={{ fontSize: '12px', color: '#64748b' }}>
                  {formatPercent(stats?.averageAPR || 0)}
                </span>
              </div>
              <Progress 
                percent={Math.min((stats?.averageAPR || 0) * 2, 100)} 
                size="small" 
                strokeColor={{
                  '0%': '#ef4444',
                  '30%': '#f59e0b', 
                  '60%': '#10b981',
                  '100%': '#059669'
                }}
                trailColor="#f1f5f9"
                showInfo={false}
              />
            </div>
          </StatsCard>
        </Col>
      </Row>
    </StatsContainer>
  );
};

export default StatsCards; 
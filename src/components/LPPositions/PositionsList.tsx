import React, { useState, useMemo, useCallback } from 'react';
import { 
  Table, 
  Tag, 
  Button, 
  Space, 
  Tooltip, 
  Progress, 
  Dropdown, 
  Modal,
  message,
  Badge,
  Typography,
  Card
} from 'antd';
import { 
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  MoreOutlined,
  DollarOutlined,
  PercentageOutlined,
  ClockCircleOutlined,
  InfoCircleOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import styled from 'styled-components';
import numeral from 'numeral';
import dayjs from 'dayjs';
import { LPPosition, PositionStatus } from '@/types';
import { useFilteredPositions } from '@/store';

const { Text } = Typography;

// 样式化组件
const PositionsContainer = styled(Card)`
  .ant-table-thead > tr > th {
    background: #fafbfc;
    border-bottom: 1px solid #e5e7eb;
    font-weight: 600;
    color: #374151;
  }
  
  .position-pair {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .token-icons {
      display: flex;
      align-items: center;
      
      .token-icon {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #f3f4f6;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        border: 2px solid white;
        
        &:not(:first-child) {
          margin-left: -8px;
        }
      }
    }
    
    .pair-info {
      display: flex;
      flex-direction: column;
      
      .pair-name {
        font-weight: 600;
        color: #111827;
      }
      
      .pool-fee {
        font-size: 12px;
        color: #6b7280;
      }
    }
  }
  
  .price-range {
    display: flex;
    flex-direction: column;
    gap: 4px;
    
    .range-text {
      font-size: 12px;
      color: #6b7280;
    }
    
    .current-price {
      font-weight: 600;
      color: #111827;
    }
  }
  
  .value-cell {
    text-align: right;
    
    .main-value {
      font-weight: 600;
      color: #111827;
    }
    
    .sub-value {
      font-size: 12px;
      color: #6b7280;
    }
  }
  
  .status-badge {
    &.active {
      background: #dcfce7;
      color: #166534;
      border: 1px solid #bbf7d0;
    }
    
    &.out-of-range {
      background: #fef3c7;
      color: #92400e;
      border: 1px solid #fde68a;
    }
    
    &.closed {
      background: #fee2e2;
      color: #991b1b;
      border: 1px solid #fecaca;
    }
  }
`;

const ActionButton = styled(Button)`
  &.collect-fees {
    border-color: #10b981;
    color: #10b981;
    
    &:hover {
      background: #10b981;
      color: white;
    }
  }
  
  &.add-liquidity {
    border-color: #3b82f6;
    color: #3b82f6;
    
    &:hover {
      background: #3b82f6;
      color: white;
    }
  }
`;

interface PositionsListProps {
  loading?: boolean;
  onViewPosition?: (position: LPPosition) => void;
  onEditPosition?: (position: LPPosition) => void;
  onDeletePosition?: (position: LPPosition) => void;
  onCollectFees?: (position: LPPosition) => void;
  onAddLiquidity?: (position: LPPosition) => void;
}

const PositionsList: React.FC<PositionsListProps> = ({
  loading = false,
  onViewPosition,
  onEditPosition,
  onDeletePosition,
  onCollectFees,
  onAddLiquidity,
}) => {
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  const [deletingPosition, setDeletingPosition] = useState<LPPosition | null>(null);

  // 从store获取过滤后的头寸数据
  const positions = useFilteredPositions();

  // 格式化函数
  const formatCurrency = useCallback((value: number) => numeral(value).format('$0,0.00'), []);
  const formatPercent = useCallback((value: number) => numeral(value / 100).format('0.00%'), []);
  const formatNumber = useCallback((value: number) => numeral(value).format('0,0'), []);

  // 获取状态标签
  const getStatusTag = useCallback((status: PositionStatus, inRange: boolean) => {
    if (status === 'closed') {
      return <Tag className="status-badge closed">已关闭</Tag>;
    }
    
    if (inRange) {
      return <Tag className="status-badge active">活跃</Tag>;
    } else {
      return <Tag className="status-badge out-of-range">超出范围</Tag>;
    }
  }, []);

  // 计算在范围内的百分比
  const getInRangePercentage = useCallback((position: LPPosition) => {
    const { currentPrice, priceRange } = position;
    if (currentPrice >= priceRange.lower && currentPrice <= priceRange.upper) {
      return 100;
    }
    
    if (currentPrice < priceRange.lower) {
      return 0;
    }
    
    if (currentPrice > priceRange.upper) {
      return 0;
    }
    
    return 50; // 部分在范围内
  }, []);

  // 操作菜单
  const getActionMenu = useCallback((position: LPPosition) => ({
    items: [
      {
        key: 'view',
        icon: <EyeOutlined />,
        label: '查看详情',
        onClick: () => onViewPosition?.(position),
      },
      {
        key: 'edit',
        icon: <EditOutlined />,
        label: '编辑头寸',
        onClick: () => onEditPosition?.(position),
      },
      {
        type: 'divider' as const,
      },
      {
        key: 'collect',
        icon: <DollarOutlined />,
        label: '收集手续费',
        onClick: () => onCollectFees?.(position),
        disabled: Number(position.uncollectedFees0) + Number(position.uncollectedFees1) === 0,
      },
      {
        key: 'add',
        icon: <ThunderboltOutlined />,
        label: '增加流动性',
        onClick: () => onAddLiquidity?.(position),
      },
      {
        type: 'divider' as const,
      },
      {
        key: 'delete',
        icon: <DeleteOutlined />,
        label: '关闭头寸',
        danger: true,
        onClick: () => {
          setDeletingPosition(position);
          setDeleteModalVisible(true);
        },
      },
    ],
  }), [onViewPosition, onEditPosition, onCollectFees, onAddLiquidity]);

  // 确认删除
  const handleConfirmDelete = useCallback(async () => {
    if (deletingPosition) {
      try {
        await onDeletePosition?.(deletingPosition);
        message.success('头寸关闭成功');
      } catch (error) {
        message.error('关闭头寸失败');
      }
    }
    setDeleteModalVisible(false);
    setDeletingPosition(null);
  }, [deletingPosition, onDeletePosition]);

  // 表格列定义
  const columns: ColumnsType<LPPosition> = useMemo(() => [
    {
      title: '交易对',
      dataIndex: 'pool',
      key: 'pair',
      width: 200,
      render: (pool) => (
        <div className="position-pair">
          <div className="token-icons">
            <div className="token-icon">{pool.token0.symbol.slice(0, 2)}</div>
            <div className="token-icon">{pool.token1.symbol.slice(0, 2)}</div>
          </div>
          <div className="pair-info">
            <div className="pair-name">
              {pool.token0.symbol}/{pool.token1.symbol}
            </div>
            <div className="pool-fee">{(pool.fee / 10000).toFixed(2)}% 费率</div>
          </div>
        </div>
      ),
    },
    {
      title: '价格范围',
      key: 'priceRange',
      width: 160,
      render: (_, record) => (
        <div className="price-range">
          <div className="range-text">
            {numeral(record.priceRange.lower).format('0,0.0000')} -  
            {numeral(record.priceRange.upper).format('0,0.0000')}
          </div>
          <div className="current-price">
            当前: {numeral(record.currentPrice).format('0,0.0000')}
          </div>
          <Progress 
            percent={getInRangePercentage(record)} 
            size="small" 
            strokeColor={record.inRange ? '#10b981' : '#ef4444'}
            showInfo={false}
          />
        </div>
      ),
    },
    {
      title: '流动性',
      key: 'liquidity',
      width: 120,
      align: 'right',
      render: (_, record) => (
        <div className="value-cell">
          <div className="main-value">{formatCurrency(record.valueUSD)}</div>
          <div className="sub-value">
            {numeral(record.amount0).format('0,0.00')} {record.pool.token0.symbol}
          </div>
          <div className="sub-value">
            {numeral(record.amount1).format('0,0.00')} {record.pool.token1.symbol}
          </div>
        </div>
      ),
    },
    {
      title: '未收取手续费',
      key: 'fees',
      width: 120,
      align: 'right',
      render: (_, record) => {
        const hasUncollectedFees = 
          Number(record.uncollectedFees0) > 0 || Number(record.uncollectedFees1) > 0;
        
        return (
          <div className="value-cell">
            <div className="main-value">{formatCurrency(record.feesEarnedUSD)}</div>
            {hasUncollectedFees && (
              <Badge 
                status="processing" 
                text={
                  <span style={{ fontSize: '12px' }}>
                    待收取: {formatCurrency(
                      Number(record.uncollectedFees0) * (record.pool.token0.price || 0) +
                      Number(record.uncollectedFees1) * (record.pool.token1.price || 0)
                    )}
                  </span>
                }
              />
            )}
          </div>
        );
      },
    },
    {
      title: '状态',
      key: 'status',
      width: 100,
      align: 'center',
      render: (_, record) => getStatusTag(record.status, record.inRange),
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 120,
      render: (createdAt) => (
        <Tooltip title={dayjs(createdAt).format('YYYY-MM-DD HH:mm:ss')}>
          <div style={{ fontSize: '12px', color: '#6b7280' }}>
            <ClockCircleOutlined style={{ marginRight: 4 }} />
            {dayjs(createdAt).fromNow()}
          </div>
        </Tooltip>
      ),
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      align: 'center',
      render: (_, record) => (
        <Space size="small">
          <ActionButton
            size="small"
            className="collect-fees"
            icon={<DollarOutlined />}
            onClick={() => onCollectFees?.(record)}
            disabled={
              Number(record.uncollectedFees0) + Number(record.uncollectedFees1) === 0
            }
          >
            收费
          </ActionButton>
          
          <Dropdown menu={getActionMenu(record)} trigger={['click']}>
            <Button size="small" icon={<MoreOutlined />} />
          </Dropdown>
        </Space>
      ),
    },
  ], [
    formatCurrency, 
    getInRangePercentage, 
    getStatusTag, 
    getActionMenu, 
    onCollectFees
  ]);

  // 行选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: setSelectedRowKeys,
    selections: [
      Table.SELECTION_ALL,
      Table.SELECTION_INVERT,
      Table.SELECTION_NONE,
    ],
  };

  return (
    <PositionsContainer>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
          <DollarOutlined style={{ color: '#667eea' }} />
          LP头寸列表
          <Badge count={positions.length} style={{ backgroundColor: '#667eea' }} />
        </h3>
        
        {selectedRowKeys.length > 0 && (
          <Space>
            <Text type="secondary">{selectedRowKeys.length} 项已选中</Text>
            <Button size="small">批量收费</Button>
            <Button size="small" danger>批量关闭</Button>
          </Space>
        )}
      </div>

      <Table<LPPosition>
        columns={columns}
        dataSource={positions}
        rowKey="id"
        loading={loading}
        rowSelection={rowSelection}
        pagination={{
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => 
            `显示 ${range[0]}-${range[1]} 项，共 ${total} 项`,
        }}
        scroll={{ x: 1200 }}
        size="middle"
      />

      {/* 删除确认弹窗 */}
      <Modal
        title="确认关闭头寸"
        open={deleteModalVisible}
        onOk={handleConfirmDelete}
        onCancel={() => {
          setDeleteModalVisible(false);
          setDeletingPosition(null);
        }}
        okText="确认关闭"
        cancelText="取消"
        okButtonProps={{ danger: true }}
      >
        <p>确定要关闭该LP头寸吗？此操作将：</p>
        <ul>
          <li>移除所有流动性</li>
          <li>收集未收取的手续费</li>
          <li>将代币返还到您的钱包</li>
        </ul>
        <p style={{ color: '#ef4444', marginTop: 16 }}>
          <InfoCircleOutlined style={{ marginRight: 4 }} />
          此操作不可撤销，请谨慎操作
        </p>
      </Modal>
    </PositionsContainer>
  );
};

export default PositionsList; 
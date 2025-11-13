import React, { useState, useEffect } from 'react';
import { Card, List, Empty, Spin, Typography, Tag, Space, Button, Popconfirm } from 'antd';
import { DeleteOutlined, FileTextOutlined, SwapOutlined } from '@ant-design/icons';
import { getAllReports, deleteReport, ReportSummary, getAllComparisons, deleteComparison, ComparisonSummary } from '../api/client';
import './ReportList.css';

const { Title, Text } = Typography;

interface ReportListProps {
  onSelectReport: (reportId: number, type: 'analysis' | 'comparison') => void;
}

const ReportList: React.FC<ReportListProps> = ({ onSelectReport }) => {
  const [reports, setReports] = useState<ReportSummary[]>([]);
  const [comparisons, setComparisons] = useState<ComparisonSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Loading reports and comparisons...');
      
      const [reportsData, comparisonsData] = await Promise.all([
        getAllReports().catch((err) => {
          console.error('Error loading reports:', err);
          return [];
        }),
        getAllComparisons().catch((err) => {
          console.error('Error loading comparisons:', err);
          return [];
        })
      ]);
      
      console.log('Reports data received:', reportsData);
      console.log('Reports count:', Array.isArray(reportsData) ? reportsData.length : 'Not an array');
      console.log('Comparisons data received:', comparisonsData);
      console.log('Comparisons count:', Array.isArray(comparisonsData) ? comparisonsData.length : 'Not an array');
      
      // 确保数据是数组，防止 undefined
      const safeReports = Array.isArray(reportsData) ? reportsData : [];
      const safeComparisons = Array.isArray(comparisonsData) ? comparisonsData : [];
      
      console.log('Setting reports:', safeReports.length);
      console.log('Setting comparisons:', safeComparisons.length);
      
      setReports(safeReports);
      setComparisons(safeComparisons);
    } catch (err: any) {
      console.error('Failed to load report list:', err);
      setError('Failed to load report list: ' + (err.message || 'Unknown error'));
      // 确保即使出错也设置为空数组
      setReports([]);
      setComparisons([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number, type: 'analysis' | 'comparison', e?: React.MouseEvent) => {
    e?.stopPropagation();
    try {
      if (type === 'analysis') {
        await deleteReport(id);
        setReports(prevReports => (Array.isArray(prevReports) ? prevReports.filter(r => r.id !== id) : []));
      } else {
        await deleteComparison(id);
        setComparisons(prevComparisons => (Array.isArray(prevComparisons) ? prevComparisons.filter(c => c.id !== id) : []));
      }
    } catch (err: any) {
      // 错误处理
      console.error('Failed to delete:', err);
    }
  };

  if (loading) {
    return (
      <div className="report-list-loading">
        <Spin size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <Empty description={error} />
      </Card>
    );
  }

  // 确保 reports 和 comparisons 始终是数组
  const safeReports = Array.isArray(reports) ? reports : [];
  const safeComparisons = Array.isArray(comparisons) ? comparisons : [];

  return (
    <div className="report-list">
      <Title level={2}>History</Title>
      
      {/* 调试信息 */}
      {process.env.NODE_ENV === 'development' && (
        <div style={{ marginBottom: 16, padding: 8, background: '#f0f0f0', borderRadius: 4 }}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            Debug: Reports: {safeReports.length}, Comparisons: {safeComparisons.length}
          </Text>
        </div>
      )}
      
      {/* 分析报告部分 */}
      <div style={{ marginBottom: 32 }}>
        <Title level={4}>
          <FileTextOutlined /> Analysis Reports ({safeReports.length})
        </Title>
        {safeReports.length === 0 ? (
          <Card>
            <Empty
              description="No analysis reports yet"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            >
              <Text type="secondary">Go to "Analyze Policy" page to start analyzing</Text>
            </Empty>
          </Card>
        ) : (
          <List
            grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 3 }}
            dataSource={safeReports}
            renderItem={(report) => (
              <List.Item>
                <Card
                  hoverable
                  className="report-card"
                  onClick={() => onSelectReport(report.id, 'analysis')}
                  actions={[
                    <Popconfirm
                      key="delete"
                      title="Are you sure you want to delete this report?"
                      onConfirm={(e) => {
                        e?.stopPropagation();
                        handleDelete(report.id, 'analysis', e!);
                      }}
                      onCancel={(e) => e?.stopPropagation()}
                      okText="Yes"
                      cancelText="No"
                    >
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={(e) => e.stopPropagation()}
                      >
                        Delete
                      </Button>
                    </Popconfirm>
                  ]}
                >
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    <div>
                      <Text strong ellipsis style={{ fontSize: '16px' }}>
                        {new URL(report.url).hostname}
                      </Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {new Date(report.created_at).toLocaleString('en-US')}
                      </Text>
                    </div>
                    
                    <Space size="small" wrap>
                      <Tag icon={<FileTextOutlined />}>
                        Segments: {report.summary.total_segments}
                      </Tag>
                      <Tag color={getRiskColor(report.summary.average_risk_score)}>
                        Risk: {report.summary.average_risk_score.toFixed(2)}
                      </Tag>
                      <Tag>Data Types: {report.summary.total_data_types}</Tag>
                      <Tag>Third Parties: {report.summary.total_third_parties}</Tag>
                    </Space>
                  </Space>
                </Card>
              </List.Item>
            )}
          />
        )}
      </div>

      {/* 对比报告部分 */}
      <div>
        <Title level={4}>
          <SwapOutlined /> Comparisons ({safeComparisons.length})
        </Title>
        {safeComparisons.length === 0 ? (
          <Card>
            <Empty
              description="No comparison reports yet"
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            >
              <Text type="secondary">Go to "Compare Versions" page to start comparing</Text>
            </Empty>
          </Card>
        ) : (
          <List
            grid={{ gutter: 16, xs: 1, sm: 1, md: 2, lg: 2, xl: 3, xxl: 3 }}
            dataSource={safeComparisons}
            renderItem={(comparison) => (
              <List.Item>
                <Card
                  hoverable
                  className="report-card"
                  onClick={() => onSelectReport(comparison.id, 'comparison')}
                  actions={[
                    <Popconfirm
                      key="delete"
                      title="Are you sure you want to delete this comparison?"
                      onConfirm={(e) => {
                        e?.stopPropagation();
                        handleDelete(comparison.id, 'comparison', e!);
                      }}
                      onCancel={(e) => e?.stopPropagation()}
                      okText="Yes"
                      cancelText="No"
                    >
                      <Button
                        type="text"
                        danger
                        icon={<DeleteOutlined />}
                        onClick={(e) => e.stopPropagation()}
                      >
                        Delete
                      </Button>
                    </Popconfirm>
                  ]}
                >
                  <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                    <div>
                      <Text strong ellipsis style={{ fontSize: '16px' }}>
                        {comparison.old_url && comparison.new_url
                          ? `${new URL(comparison.old_url).hostname} → ${new URL(comparison.new_url).hostname}`
                          : 'Text Comparison'}
                      </Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {new Date(comparison.created_at).toLocaleString('en-US')}
                      </Text>
                    </div>
                    
                    <Space size="small" wrap>
                      <Tag icon={<SwapOutlined />}>Comparison</Tag>
                      <Tag color={comparison.summary.risk_change > 0 ? 'red' : 'green'}>
                        Risk Change: {(comparison.summary.risk_change * 100).toFixed(2)}%
                      </Tag>
                      <Tag>Old Risk: {(comparison.summary.old_average_risk * 100).toFixed(2)}%</Tag>
                      <Tag>New Risk: {(comparison.summary.new_average_risk * 100).toFixed(2)}%</Tag>
                    </Space>
                  </Space>
                </Card>
              </List.Item>
            )}
          />
        )}
      </div>
    </div>
  );
};

function getRiskColor(score: number): string {
  if (score < 0.3) return 'success';
  if (score < 0.6) return 'warning';
  return 'error';
}

export default ReportList;

import React, { useState, useEffect } from 'react';
import { Card, Tabs, Row, Col, Statistic, Empty, Spin, Button, Typography, Tag, Space, Collapse, Alert } from 'antd';
import { ArrowLeftOutlined, FileTextOutlined, WarningOutlined, CheckCircleOutlined, ExclamationCircleOutlined, SwapOutlined, PlusOutlined, MinusOutlined } from '@ant-design/icons';
import { getReportById, AnalysisResult, getComparisonById, ComparisonResult } from '../api/client';
import ReactMarkdown from 'react-markdown';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import './ReportViewer.css';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface ReportViewerProps {
  reportId: number;
  reportType?: 'analysis' | 'comparison';
  onBack: () => void;
}

const ReportViewer: React.FC<ReportViewerProps> = ({ reportId, reportType = 'analysis', onBack }) => {
  const [report, setReport] = useState<AnalysisResult | ComparisonResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('summary');

  useEffect(() => {
    loadReport();
  }, [reportId, reportType]);

  const loadReport = async () => {
    try {
      setLoading(true);
      setError(null);
      let data;
      if (reportType === 'comparison') {
        data = await getComparisonById(reportId);
      } else {
        data = await getReportById(reportId);
      }
      
      // 调试：打印数据
      console.log('Loaded report data:', data);
      console.log('Has analysis_result:', data && 'analysis_result' in data);
      if (data && 'analysis_result' in data) {
        console.log('analysis_result type:', typeof data.analysis_result);
        console.log('Has summary:', data.analysis_result && 'summary' in data.analysis_result);
        console.log('Has segment_analyses:', data.analysis_result && 'segment_analyses' in data.analysis_result);
      }
      
      setReport(data);
    } catch (err: any) {
      console.error('Failed to load report:', err);
      setError('Failed to load report: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="report-viewer-loading">
        <Spin size="large" />
      </div>
    );
  }

  if (error || !report) {
    return (
      <Card>
        <Empty description={error || 'Report not found'}>
          <Button type="primary" onClick={onBack} icon={<ArrowLeftOutlined />}>
            Back to List
          </Button>
        </Empty>
      </Card>
    );
  }

  // 如果是对比结果，使用不同的渲染逻辑
  if (reportType === 'comparison' && 'comparison_result' in report) {
    const comparison = report as ComparisonResult;
    
    // 安全检查：确保 comparison_result 存在
    if (!comparison.comparison_result) {
      return (
        <Card>
          <Empty description="Comparison result data is missing">
            <Button type="primary" onClick={onBack} icon={<ArrowLeftOutlined />}>
              Back to List
            </Button>
          </Empty>
        </Card>
      );
    }
    
    const comp = comparison.comparison_result;
    const risk = comp.risk_change;
    
    // 确保 risk_change 存在
    if (!risk) {
      return (
        <Card>
          <Empty description="Comparison data is incomplete">
            <Button type="primary" onClick={onBack} icon={<ArrowLeftOutlined />}>
              Back to List
            </Button>
          </Empty>
        </Card>
      );
    }
    
    return (
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Button type="link" onClick={onBack} icon={<ArrowLeftOutlined />}>
            Back to List
          </Button>
          <Title level={3} style={{ marginTop: 8 }}>
            <SwapOutlined /> Policy Version Comparison
          </Title>
          <Text type="secondary">
            Compared on {comparison.created_at ? new Date(comparison.created_at).toLocaleString('en-US') : 'Unknown date'}
          </Text>
          {comparison.old_url && comparison.new_url && (
            <div style={{ marginTop: 8 }}>
              <Text strong>Old: </Text>
              <Text>{comparison.old_url}</Text>
              <br />
              <Text strong>New: </Text>
              <Text>{comparison.new_url}</Text>
            </div>
          )}
        </div>

        <Tabs
          defaultActiveKey="risk"
          items={[
            {
              key: 'risk',
              label: 'Risk Assessment',
              children: (
                <Row gutter={16}>
                  <Col span={8}>
                    <Statistic
                      title="Old Version Average Risk"
                      value={risk.old_average_risk}
                      precision={2}
                      valueStyle={{ color: '#3f8600' }}
                      suffix="%"
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="New Version Average Risk"
                      value={risk.new_average_risk}
                      precision={2}
                      valueStyle={{ color: risk.risk_increased ? '#cf1322' : '#3f8600' }}
                      suffix="%"
                    />
                  </Col>
                  <Col span={8}>
                    <Statistic
                      title="Risk Change"
                      value={Math.abs(risk.risk_change)}
                      precision={2}
                      valueStyle={{ color: risk.risk_increased ? '#cf1322' : '#3f8600' }}
                      prefix={risk.risk_increased ? '+' : '-'}
                      suffix="%"
                    />
                  </Col>
                </Row>
              ),
            },
            {
              key: 'summary',
              label: 'Summary Changes',
              children: (
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  {comp.summary_changes && Object.entries(comp.summary_changes).map(([key, changes]) => (
                    <Card key={key} title={key.replace(/_/g, ' ').toUpperCase()} size="small">
                      {changes && changes.has_changes ? (
                        <Space direction="vertical" size="small">
                          {Array.isArray(changes.added) && changes.added.length > 0 && (
                            <div>
                              <Tag color="green" icon={<PlusOutlined />}>
                                Added ({changes.added.length}): {changes.added.slice(0, 5).join(', ')}
                                {changes.added.length > 5 && ` +${changes.added.length - 5} more`}
                              </Tag>
                            </div>
                          )}
                          {Array.isArray(changes.removed) && changes.removed.length > 0 && (
                            <div>
                              <Tag color="red" icon={<MinusOutlined />}>
                                Removed ({changes.removed.length}): {changes.removed.slice(0, 5).join(', ')}
                                {changes.removed.length > 5 && ` +${changes.removed.length - 5} more`}
                              </Tag>
                            </div>
                          )}
                        </Space>
                      ) : (
                        <Tag color="default">No changes</Tag>
                      )}
                    </Card>
                  ))}
                  {(!comp.summary_changes || Object.keys(comp.summary_changes).length === 0) && (
                    <Empty description="No summary changes data available" />
                  )}
                </Space>
              ),
            },
          ]}
        />
      </Card>
    );
  }

  // 分析结果渲染
  const analysisReport = report as AnalysisResult;
  
  // 安全检查：确保 analysis_result 存在
  if (!analysisReport.analysis_result) {
    return (
      <Card>
        <Empty description="Analysis result data is missing">
          <Button type="primary" onClick={onBack} icon={<ArrowLeftOutlined />}>
            Back to List
          </Button>
        </Empty>
      </Card>
    );
  }
  
  const { summary, segment_analyses } = analysisReport.analysis_result;
  
  // 确保 summary 和 segment_analyses 存在
  if (!summary || !segment_analyses) {
    return (
      <Card>
        <Empty description="Report data is incomplete">
          <Button type="primary" onClick={onBack} icon={<ArrowLeftOutlined />}>
            Back to List
          </Button>
        </Empty>
      </Card>
    );
  }

  // 准备图表数据（添加安全检查）
  const categoryData = summary.category_distribution 
    ? Object.entries(summary.category_distribution).map(([name, value]) => ({
        name: name.replace(/_/g, ' '),
        value
      }))
    : [];

  const safeSegmentAnalyses = Array.isArray(segment_analyses) ? segment_analyses : [];
  const riskData = [
    { name: 'Low Risk', value: safeSegmentAnalyses.filter(s => s.risk_score < 0.3).length },
    { name: 'Medium Risk', value: safeSegmentAnalyses.filter(s => s.risk_score >= 0.3 && s.risk_score < 0.6).length },
    { name: 'High Risk', value: safeSegmentAnalyses.filter(s => s.risk_score >= 0.6).length },
  ];

  const COLORS = ['#52c41a', '#faad14', '#ff4d4f'];

  const tabItems = [
    {
      key: 'summary',
      label: 'Summary',
      children: (
        <div className="summary-content">
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Segments Analyzed"
                  value={summary.total_segments}
                  prefix={<FileTextOutlined />}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Average Risk Score"
                  value={summary.average_risk_score}
                  precision={2}
                  valueStyle={{ color: getRiskColorValue(summary.average_risk_score) }}
                  prefix={getRiskIcon(summary.average_risk_score)}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Data Types"
                  value={Array.isArray(summary.total_data_types) ? summary.total_data_types.length : 0}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} md={6}>
              <Card>
                <Statistic
                  title="Third Parties"
                  value={Array.isArray(summary.total_third_parties) ? summary.total_third_parties.length : 0}
                />
              </Card>
            </Col>
          </Row>

          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} lg={12}>
              <Card title="PIPEDA Category Distribution" className="chart-card">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={categoryData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="name" 
                      angle={-45} 
                      textAnchor="end" 
                      height={100}
                      interval={0}
                    />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="value" fill="#1890ff" />
                  </BarChart>
                </ResponsiveContainer>
              </Card>
            </Col>
            <Col xs={24} lg={12}>
              <Card title="Risk Distribution" className="chart-card">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={riskData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {riskData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Card>
            </Col>
          </Row>

          {summary.data_collection_by_activity && Object.keys(summary.data_collection_by_activity).length > 0 && (
            <Card title="Data Collection by Activity" style={{ marginBottom: 24 }}>
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                {Object.entries(summary.data_collection_by_activity).map(([activity, info]) => (
                  <Card key={activity} size="small" className="activity-card">
                    <Space direction="vertical" size="small" style={{ width: '100%' }}>
                      <div>
                        <Text strong>{info.description}</Text>
                        <br />
                        <Text type="secondary">
                          Segments: {info.segment_count} | Data Types: {info.data_types.length}
                        </Text>
                      </div>
                      <div>
                        <Space size={[8, 8]} wrap>
                          {info.data_types.slice(0, 10).map((dt, idx) => (
                            <Tag key={idx}>{dt}</Tag>
                          ))}
                          {info.data_types.length > 10 && (
                            <Tag>+{info.data_types.length - 10} more</Tag>
                          )}
                        </Space>
                      </div>
                    </Space>
                  </Card>
                ))}
              </Space>
            </Card>
          )}

          <Row gutter={[16, 16]}>
            {Array.isArray(summary.total_data_types) && summary.total_data_types.length > 0 && (
              <Col xs={24} md={12}>
                <Card title="Data Types Collected" size="small">
                  <Space size={[8, 8]} wrap>
                    {summary.total_data_types.slice(0, 50).map((dt, idx) => (
                      <Tag key={idx}>{dt}</Tag>
                    ))}
                    {summary.total_data_types.length > 50 && (
                      <Tag>+{summary.total_data_types.length - 50} more</Tag>
                    )}
                  </Space>
                </Card>
              </Col>
            )}
            {Array.isArray(summary.total_third_parties) && summary.total_third_parties.length > 0 && (
              <Col xs={24} md={12}>
                <Card title="Third Party Partners" size="small">
                  <Space size={[8, 8]} wrap>
                    {summary.total_third_parties.slice(0, 30).map((tp, idx) => (
                      <Tag key={idx} color="blue">{tp}</Tag>
                    ))}
                    {summary.total_third_parties.length > 30 && (
                      <Tag>+{summary.total_third_parties.length - 30} more</Tag>
                    )}
                  </Space>
                </Card>
              </Col>
            )}
          </Row>
        </div>
      ),
    },
    {
      key: 'details',
      label: 'Detailed Analysis',
      children: (
        <div className="details-content">
          <Collapse
            items={safeSegmentAnalyses.map((segment, idx) => ({
              key: idx,
              label: (
                <Space>
                  <Text strong>Segment {idx + 1}</Text>
                  <Tag color={getRiskTagColor(segment.risk_score)}>
                    Risk: {segment.risk_score.toFixed(2)}
                  </Tag>
                  <Tag>{getCategoryName(segment.category)}</Tag>
                </Space>
              ),
              children: (
                <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                  <Card size="small">
                    <Paragraph style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                      {segment.text || 'No text available'}
                    </Paragraph>
                  </Card>
                  
                  {(segment.parameters.data_types.length > 0 || 
                    segment.parameters.purposes.length > 0 || 
                    segment.parameters.third_parties.length > 0) && (
                    <Card size="small" title="Extracted Parameters">
                      <Space direction="vertical" size="small" style={{ width: '100%' }}>
                        {segment.parameters.data_types.length > 0 && (
                          <div>
                            <Text strong>Data Types: </Text>
                            <Space size={[8, 8]} wrap>
                              {segment.parameters.data_types.map((dt, i) => (
                                <Tag key={i}>{dt}</Tag>
                              ))}
                            </Space>
                          </div>
                        )}
                        {segment.parameters.purposes.length > 0 && (
                          <div>
                            <Text strong>Purposes: </Text>
                            <Space size={[8, 8]} wrap>
                              {segment.parameters.purposes.slice(0, 3).map((p, i) => (
                                <Tag key={i} color="green">{p}</Tag>
                              ))}
                            </Space>
                          </div>
                        )}
                        {segment.parameters.third_parties.length > 0 && (
                          <div>
                            <Text strong>Third Parties: </Text>
                            <Space size={[8, 8]} wrap>
                              {segment.parameters.third_parties.map((tp, i) => (
                                <Tag key={i} color="orange">{tp}</Tag>
                              ))}
                            </Space>
                          </div>
                        )}
                      </Space>
                    </Card>
                  )}
                  
                  <Card size="small" title="Analysis Explanation">
                    <ReactMarkdown>{segment.explanation}</ReactMarkdown>
                  </Card>
                </Space>
              ),
            }))}
          />
        </div>
      ),
    },
  ];

  return (
    <div className="report-viewer">
      <Card>
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <div>
            <Button 
              icon={<ArrowLeftOutlined />} 
              onClick={onBack}
              style={{ marginBottom: 16 }}
            >
              Back to List
            </Button>
            <Title level={3}>Analysis Report</Title>
            <Text type="secondary" ellipsis style={{ display: 'block' }}>
              {analysisReport.url}
            </Text>
          </div>

          <Tabs
            activeKey={activeTab}
            onChange={setActiveTab}
            items={tabItems}
          />
        </Space>
      </Card>
    </div>
  );
};

function getCategoryName(category: string): string {
  const categoryMap: Record<string, string> = {
    'accountability': 'Accountability',
    'identifying_purposes': 'Identifying Purposes',
    'consent': 'Consent',
    'limiting_collection': 'Limiting Collection',
    'limiting_use': 'Limiting Use, Disclosure & Retention',
    'accuracy': 'Accuracy',
    'safeguards': 'Safeguards',
    'openness': 'Openness',
    'individual_access': 'Individual Access',
    'challenging_compliance': 'Challenging Compliance'
  };
  return categoryMap[category] || category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function getRiskColorValue(score: number): string {
  if (score < 0.3) return '#52c41a';
  if (score < 0.6) return '#faad14';
  return '#ff4d4f';
}

function getRiskIcon(score: number) {
  if (score < 0.3) return <CheckCircleOutlined />;
  if (score < 0.6) return <ExclamationCircleOutlined />;
  return <WarningOutlined />;
}

function getRiskTagColor(score: number): string {
  if (score < 0.3) return 'success';
  if (score < 0.6) return 'warning';
  return 'error';
}

function getRiskLevel(score: number): string {
  if (score < 0.3) return 'low';
  if (score < 0.6) return 'medium';
  return 'high';
}

export default ReportViewer;

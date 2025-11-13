import React, { useState } from 'react';
import {
  Card,
  Input,
  Button,
  Alert,
  Spin,
  Typography,
  Space,
  Tabs,
  Row,
  Col,
  Statistic,
  Tag,
  Collapse,
  Progress,
  Steps,
  Divider,
  Checkbox,
  message,
} from 'antd';
import {
  ArrowRightOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  PlusOutlined,
  MinusOutlined,
  EditOutlined,
  SaveOutlined,
} from '@ant-design/icons';
import { comparePolicies, ComparisonResult } from '../api/client';
import './PolicyComparator.css';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

interface PolicyComparatorProps {
  onComparisonComplete?: (result: ComparisonResult) => void;
}

const PolicyComparator: React.FC<PolicyComparatorProps> = ({ onComparisonComplete }) => {
  const [comparisonMode, setComparisonMode] = useState<'url' | 'text'>('url');
  const [oldUrl, setOldUrl] = useState('');
  const [newUrl, setNewUrl] = useState('');
  const [oldText, setOldText] = useState('');
  const [newText, setNewText] = useState('');
  const [saveResult, setSaveResult] = useState(true);  // 默认保存
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    { title: 'Fetching Old Version', description: 'Crawling old policy content...' },
    { title: 'Fetching New Version', description: 'Crawling new policy content...' },
    { title: 'Analyzing Old Version', description: 'Analyzing old policy structure...' },
    { title: 'Analyzing New Version', description: 'Analyzing new policy structure...' },
    { title: 'Comparing Versions', description: 'Identifying differences...' },
    { title: 'Generating Report', description: 'Finalizing comparison report...' },
  ];

  const handleCompare = async () => {
    setError(null);
    setResult(null);
    setLoading(true);
    setCurrentStep(0);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev < steps.length - 1) {
            return prev + 1;
          }
          clearInterval(progressInterval);
          return prev;
        });
      }, 2000);

      let comparisonResult: ComparisonResult;
      
      if (comparisonMode === 'url') {
        if (!oldUrl || !newUrl) {
          throw new Error('Please provide both old and new URLs');
        }
        comparisonResult = await comparePolicies(oldUrl, newUrl, undefined, undefined, saveResult);
      } else {
        if (!oldText || !newText) {
          throw new Error('Please provide both old and new policy texts');
        }
        comparisonResult = await comparePolicies(undefined, undefined, oldText, newText, saveResult);
      }

      clearInterval(progressInterval);
      setCurrentStep(steps.length - 1);
      setResult(comparisonResult);
      
      if (comparisonResult.saved_id) {
        message.success('Comparison result saved successfully!');
      }
      
      if (onComparisonComplete) {
        onComparisonComplete(comparisonResult);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to compare policies');
    } finally {
      setLoading(false);
    }
  };

  const getCategoryName = (category: string): string => {
    const categoryMap: Record<string, string> = {
      accountability: 'Accountability',
      identifying_purposes: 'Identifying Purposes',
      consent: 'Consent',
      limiting_collection: 'Limiting Collection',
      limiting_use: 'Limiting Use, Disclosure, and Retention',
      accuracy: 'Accuracy',
      safeguards: 'Safeguards',
      openness: 'Openness',
      individual_access: 'Individual Access',
      challenging_compliance: 'Challenging Compliance',
    };
    return categoryMap[category] || category;
  };

  const renderRiskChange = () => {
    if (!result) return null;
    
    const risk = result.comparison_result.risk_change;
    const riskChangePercent = (risk.risk_change * 100).toFixed(2);
    const isPositive = risk.risk_change > 0;

    return (
      <Card>
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
              valueStyle={{ color: isPositive ? '#cf1322' : '#3f8600' }}
              suffix="%"
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="Risk Change"
              value={Math.abs(risk.risk_change)}
              precision={2}
              valueStyle={{ color: isPositive ? '#cf1322' : '#3f8600' }}
              prefix={isPositive ? '+' : '-'}
              suffix="%"
            />
          </Col>
        </Row>
        {risk.risk_increased && (
          <Alert
            message="Warning: Privacy risk has increased!"
            type="warning"
            icon={<ExclamationCircleOutlined />}
            style={{ marginTop: 16 }}
          />
        )}
      </Card>
    );
  };

  const renderSummaryChanges = () => {
    if (!result) return null;
    
    const summary = result.comparison_result.summary_changes;

    return (
      <Card title="Key Changes Summary">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {Object.entries(summary).map(([key, changes]) => (
            <div key={key}>
              <Text strong style={{ textTransform: 'capitalize' }}>
                {key.replace(/_/g, ' ')}:
              </Text>
              <div style={{ marginTop: 8 }}>
                {changes.added.length > 0 && (
                  <div>
                    <Tag color="green" icon={<PlusOutlined />}>
                      Added ({changes.added.length}): {changes.added.slice(0, 5).join(', ')}
                      {changes.added.length > 5 && ` +${changes.added.length - 5} more`}
                    </Tag>
                  </div>
                )}
                {changes.removed.length > 0 && (
                  <div style={{ marginTop: 4 }}>
                    <Tag color="red" icon={<MinusOutlined />}>
                      Removed ({changes.removed.length}): {changes.removed.slice(0, 5).join(', ')}
                      {changes.removed.length > 5 && ` +${changes.removed.length - 5} more`}
                    </Tag>
                  </div>
                )}
                {!changes.has_changes && (
                  <Tag color="default">No changes</Tag>
                )}
              </div>
            </div>
          ))}
        </Space>
      </Card>
    );
  };

  const renderCategoryChanges = () => {
    if (!result) return null;
    
    const categoryChanges = result.comparison_result.category_changes;
    const categoriesWithChanges = Object.entries(categoryChanges).filter(
      ([_, changes]) =>
        changes.count_change !== 0 ||
        changes.added_segments.length > 0 ||
        changes.removed_segments.length > 0 ||
        changes.modified_segments.length > 0
    );

    if (categoriesWithChanges.length === 0) {
      return (
        <Card>
          <Text type="secondary">No significant changes detected in any category.</Text>
        </Card>
      );
    }

    return (
      <Card title="Category Changes">
        <Collapse>
          {categoriesWithChanges.map(([category, changes]) => (
            <Panel
              key={category}
              header={
                <Space>
                  <Text strong>{getCategoryName(category)}</Text>
                  <Tag color={changes.count_change > 0 ? 'blue' : changes.count_change < 0 ? 'orange' : 'default'}>
                    {changes.old_count} → {changes.new_count} ({changes.count_change > 0 ? '+' : ''}{changes.count_change})
                  </Tag>
                  {changes.added_segments.length > 0 && (
                    <Tag color="green">+{changes.added_segments.length} added</Tag>
                  )}
                  {changes.removed_segments.length > 0 && (
                    <Tag color="red">-{changes.removed_segments.length} removed</Tag>
                  )}
                  {changes.modified_segments.length > 0 && (
                    <Tag color="orange">{changes.modified_segments.length} modified</Tag>
                  )}
                </Space>
              }
            >
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                {changes.added_segments.length > 0 && (
                  <div>
                    <Text strong style={{ color: '#52c41a' }}>Added Segments:</Text>
                    {changes.added_segments.slice(0, 3).map((seg, idx) => (
                      <Card key={idx} size="small" style={{ marginTop: 8 }}>
                        <Paragraph style={{ marginBottom: 8 }}>{seg.text.substring(0, 200)}...</Paragraph>
                        <Space>
                          <Tag>Risk: {(seg.risk_score * 100).toFixed(1)}%</Tag>
                          {seg.parameters.data_types.length > 0 && (
                            <Tag color="blue">Data: {seg.parameters.data_types.join(', ')}</Tag>
                          )}
                          {seg.parameters.third_parties.length > 0 && (
                            <Tag color="orange">Third Parties: {seg.parameters.third_parties.join(', ')}</Tag>
                          )}
                        </Space>
                      </Card>
                    ))}
                    {changes.added_segments.length > 3 && (
                      <Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
                        +{changes.added_segments.length - 3} more added segments
                      </Text>
                    )}
                  </div>
                )}

                {changes.removed_segments.length > 0 && (
                  <div>
                    <Text strong style={{ color: '#ff4d4f' }}>Removed Segments:</Text>
                    {changes.removed_segments.slice(0, 3).map((seg, idx) => (
                      <Card key={idx} size="small" style={{ marginTop: 8, backgroundColor: '#fff1f0' }}>
                        <Paragraph style={{ marginBottom: 0 }}>{seg.text.substring(0, 200)}...</Paragraph>
                      </Card>
                    ))}
                    {changes.removed_segments.length > 3 && (
                      <Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
                        +{changes.removed_segments.length - 3} more removed segments
                      </Text>
                    )}
                  </div>
                )}

                {changes.modified_segments.length > 0 && (
                  <div>
                    <Text strong style={{ color: '#fa8c16' }}>Modified Segments:</Text>
                    {changes.modified_segments.slice(0, 3).map((seg, idx) => (
                      <Card key={idx} size="small" style={{ marginTop: 8 }}>
                        <Space direction="vertical" size="small" style={{ width: '100%' }}>
                          <div>
                            <Text type="secondary">Similarity: {(seg.similarity * 100).toFixed(0)}%</Text>
                            <Tag color={seg.risk_change > 0 ? 'red' : 'green'} style={{ marginLeft: 8 }}>
                              Risk: {(seg.risk_change * 100).toFixed(1)}%
                            </Tag>
                          </div>
                          <div>
                            <Text strong>Old:</Text>
                            <Paragraph style={{ marginTop: 4, marginBottom: 8 }}>
                              {seg.old_text.substring(0, 150)}...
                            </Paragraph>
                            <Text strong>New:</Text>
                            <Paragraph style={{ marginTop: 4, marginBottom: 0 }}>
                              {seg.new_text.substring(0, 150)}...
                            </Paragraph>
                          </div>
                        </Space>
                      </Card>
                    ))}
                    {changes.modified_segments.length > 3 && (
                      <Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
                        +{changes.modified_segments.length - 3} more modified segments
                      </Text>
                    )}
                  </div>
                )}
              </Space>
            </Panel>
          ))}
        </Collapse>
      </Card>
    );
  };

  return (
    <div className="policy-comparator">
      <Card>
        <Title level={3}>Policy Version Comparison</Title>
        <Text type="secondary">
          Compare two versions of a privacy policy to identify changes, new data collection practices, and risk variations.
        </Text>

        <Divider />

        <Tabs
          activeKey={comparisonMode}
          onChange={(key) => {
            setComparisonMode(key as 'url' | 'text');
            setError(null);
            setResult(null);
          }}
          items={[
            {
              key: 'url',
              label: 'Compare by URL',
              children: (
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <div>
                    <Text strong>Old Version URL:</Text>
                    <Input
                      size="large"
                      placeholder="https://example.com/privacy-policy-v1"
                      value={oldUrl}
                      onChange={(e) => setOldUrl(e.target.value)}
                      disabled={loading}
                      style={{ marginTop: 8 }}
                    />
                  </div>
                  <div>
                    <Text strong>New Version URL:</Text>
                    <Input
                      size="large"
                      placeholder="https://example.com/privacy-policy-v2"
                      value={newUrl}
                      onChange={(e) => setNewUrl(e.target.value)}
                      disabled={loading}
                      style={{ marginTop: 8 }}
                    />
                  </div>
                </Space>
              ),
            },
            {
              key: 'text',
              label: 'Compare by Text',
              children: (
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                  <div>
                    <Text strong>Old Version Text:</Text>
                    <TextArea
                      size="large"
                      placeholder="Paste the old version of the privacy policy here..."
                      value={oldText}
                      onChange={(e) => setOldText(e.target.value)}
                      rows={8}
                      disabled={loading}
                      style={{ marginTop: 8 }}
                    />
                  </div>
                  <div>
                    <Text strong>New Version Text:</Text>
                    <TextArea
                      size="large"
                      placeholder="Paste the new version of the privacy policy here..."
                      value={newText}
                      onChange={(e) => setNewText(e.target.value)}
                      rows={8}
                      disabled={loading}
                      style={{ marginTop: 8 }}
                    />
                  </div>
                </Space>
              ),
            },
          ]}
        />

        <div style={{ marginTop: 24 }}>
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <Checkbox
              checked={saveResult}
              onChange={(e) => setSaveResult(e.target.checked)}
            >
              Save comparison result to history
            </Checkbox>
            <Button
              type="primary"
              size="large"
              onClick={handleCompare}
              loading={loading}
              disabled={
                loading ||
                (comparisonMode === 'url' && (!oldUrl.trim() || !newUrl.trim())) ||
                (comparisonMode === 'text' && (!oldText.trim() || !newText.trim()))
              }
              icon={<ArrowRightOutlined />}
              block
            >
              Compare Policies
            </Button>
          </Space>
        </div>

        {error && (
          <Alert
            message="Error"
            description={error}
            type="error"
            showIcon
            style={{ marginTop: 16 }}
            closable
            onClose={() => setError(null)}
          />
        )}

        {loading && (
          <Card className="loading-card" style={{ marginTop: 24 }}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Progress
                percent={Math.round(((currentStep + 1) / steps.length) * 100)}
                status="active"
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
              />
              <Steps
                direction="vertical"
                current={currentStep}
                size="small"
                items={steps.map((step, index) => ({
                  title: step.title,
                  description: step.description,
                  icon: index === currentStep ? <LoadingOutlined spin /> : index < currentStep ? <CheckCircleOutlined /> : undefined,
                }))}
              />
            </Space>
          </Card>
        )}

        {result && (
          <div style={{ marginTop: 24 }}>
            <Tabs
              defaultActiveKey="risk"
              items={[
                {
                  key: 'risk',
                  label: 'Risk Assessment',
                  children: renderRiskChange(),
                },
                {
                  key: 'summary',
                  label: 'Summary Changes',
                  children: renderSummaryChanges(),
                },
                {
                  key: 'categories',
                  label: 'Category Changes',
                  children: renderCategoryChanges(),
                },
              ]}
            />
          </div>
        )}
      </Card>
    </div>
  );
};

export default PolicyComparator;
import React, { useState, useEffect } from 'react';
import { Card, Input, Button, Alert, Spin, Typography, Space, Steps, Progress } from 'antd';
import { 
  SearchOutlined, 
  LoadingOutlined, 
  GlobalOutlined,
  FileTextOutlined,
  ToolOutlined,
  ExperimentOutlined,
  CheckCircleOutlined,
  SaveOutlined
} from '@ant-design/icons';
import { analyzePolicy } from '../api/client';
import './PolicyAnalyzer.css';

const { Title, Text } = Typography;

interface PolicyAnalyzerProps {
  onAnalysisComplete: (reportId: number) => void;
}

interface AnalysisStep {
  title: string;
  description: string;
  icon: React.ReactNode;
  status: 'wait' | 'process' | 'finish' | 'error';
}

const PolicyAnalyzer: React.FC<PolicyAnalyzerProps> = ({ onAnalysisComplete }) => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);

  const steps: AnalysisStep[] = [
    {
      title: 'Validating URL',
      description: 'Checking URL format and accessibility',
      icon: <SearchOutlined />,
      status: 'wait'
    },
    {
      title: 'Fetching Content',
      description: 'Crawling webpage and downloading content',
      icon: <GlobalOutlined />,
      status: 'wait'
    },
    {
      title: 'Preprocessing',
      description: 'Cleaning HTML and filtering noise content',
      icon: <ToolOutlined />,
      status: 'wait'
    },
    {
      title: 'Analyzing Policy',
      description: 'Extracting privacy parameters using NLP',
      icon: <ExperimentOutlined />,
      status: 'wait'
    },
    {
      title: 'Classifying Segments',
      description: 'Categorizing content by PIPEDA framework',
      icon: <FileTextOutlined />,
      status: 'wait'
    },
    {
      title: 'Generating Report',
      description: 'Creating analysis report and summary',
      icon: <CheckCircleOutlined />,
      status: 'wait'
    },
    {
      title: 'Saving Results',
      description: 'Storing analysis results in database',
      icon: <SaveOutlined />,
      status: 'wait'
    }
  ];

  // 模拟进度更新
  useEffect(() => {
    if (!loading) {
      setCurrentStep(0);
      setProgress(0);
      return;
    }

    const stepDurations = [1000, 3000, 2000, 5000, 3000, 2000, 1000]; // 每个步骤的持续时间（毫秒）
    const totalDuration = stepDurations.reduce((a, b) => a + b, 0);
    
    let stepIndex = 0;
    let accumulatedTime = 0;
    
    const interval = setInterval(() => {
      accumulatedTime += 200; // 每200ms更新一次
      
      // 更新进度条（最多到95%，等待实际完成）
      const currentProgress = Math.min((accumulatedTime / totalDuration) * 100, 95);
      setProgress(currentProgress);
      
      // 更新当前步骤
      let newStepIndex = 0;
      let timeSum = 0;
      for (let i = 0; i < stepDurations.length; i++) {
        timeSum += stepDurations[i];
        if (accumulatedTime >= timeSum) {
          newStepIndex = i + 1;
        }
      }
      
      if (newStepIndex !== stepIndex) {
        stepIndex = newStepIndex;
        setCurrentStep(Math.min(stepIndex, steps.length - 1));
      }
    }, 200);

    return () => clearInterval(interval);
  }, [loading, steps.length]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim()) {
      setError('Please enter a valid URL');
      return;
    }

    setLoading(true);
    setError(null);
    setCurrentStep(0);
    setProgress(0);

    try {
      const result = await analyzePolicy(url);
      
      // 调试：打印返回结果
      console.log('Analysis result:', result);
      console.log('Result ID:', result.id);
      console.log('Has analysis_result:', 'analysis_result' in result);
      
      // 完成所有步骤
      setCurrentStep(steps.length);
      setProgress(100);
      
      // 短暂延迟后跳转，让用户看到完成状态
      setTimeout(() => {
        setLoading(false);
        if (result && result.id) {
          onAnalysisComplete(result.id);
        } else {
          setError('Analysis completed but report ID is missing');
          setCurrentStep(0);
          setProgress(0);
        }
      }, 800);
    } catch (err: any) {
      console.error('Analysis error:', err);
      setError(err.response?.data?.error || 'Analysis failed. Please check if the URL is correct.');
      setLoading(false);
      setCurrentStep(0);
      setProgress(0);
    }
  };

  const updatedSteps = steps.map((step, index) => ({
    ...step,
    status: (
      index < currentStep ? 'finish' :
      index === currentStep ? 'process' :
      'wait'
    ) as 'wait' | 'process' | 'finish' | 'error'
  }));

  // 确保进度不超过100%
  const displayProgress = Math.min(Math.round(progress), 100);

  return (
    <div className="policy-analyzer">
      <Card className="analyzer-card">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center', paddingBottom: 8 }}>
            <Title level={2} style={{ 
              background: 'linear-gradient(135deg, #4A90E2 0%, #5B9BD5 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              marginBottom: 8
            }}>
              Analyze Privacy Policy
            </Title>
            <Text type="secondary" style={{ fontSize: '15px' }}>
              Enter the privacy policy webpage URL, and the system will automatically crawl and analyze the content
            </Text>
          </div>
          
          <form onSubmit={handleSubmit}>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>Privacy Policy URL</Text>
                <Input
                  size="large"
                  placeholder="https://example.com/privacy-policy"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  disabled={loading}
                  prefix={<SearchOutlined />}
                />
              </div>

              {error && (
                <Alert
                  message="Error"
                  description={error}
                  type="error"
                  showIcon
                  closable
                  onClose={() => setError(null)}
                />
              )}

              <Button
                type="primary"
                size="large"
                htmlType="submit"
                loading={loading}
                disabled={!url.trim()}
                block
                icon={loading ? <LoadingOutlined /> : <SearchOutlined />}
              >
                {loading ? 'Analyzing...' : 'Start Analysis'}
              </Button>
            </Space>
          </form>

          {loading && (
            <Card className="loading-card">
              <Space direction="vertical" size="large" style={{ width: '100%' }}>
                <div>
                  <div style={{ marginBottom: 16 }}>
                    <Text strong style={{ fontSize: '16px' }}>Analysis Progress</Text>
                  </div>
                  <Progress 
                    percent={displayProgress} 
                    status={displayProgress >= 100 ? "success" : "active"}
                    strokeColor={{
                      '0%': '#108ee9',
                      '100%': '#87d068',
                    }}
                    showInfo={true}
                  />
                </div>
                
                <Steps 
                  direction="vertical" 
                  current={Math.min(currentStep, steps.length - 1)}
                  size="small"
                  items={updatedSteps.map((step, index) => {
                    let iconElement = step.icon;
                    if (step.status === 'process') {
                      iconElement = <LoadingOutlined spin style={{ fontSize: '16px' }} />;
                    } else if (step.status === 'finish') {
                      iconElement = <CheckCircleOutlined style={{ fontSize: '16px' }} />;
                    }
                    return {
                      title: step.title,
                      description: step.description,
                      icon: iconElement,
                      status: step.status
                    };
                  })}
                />
                
                <div style={{ textAlign: 'center', marginTop: 16 }}>
                  <Text type="secondary" style={{ fontSize: '13px', fontWeight: 500 }}>
                    {displayProgress >= 100 
                      ? '✓ Analysis completed successfully!' 
                      : updatedSteps[Math.min(currentStep, steps.length - 1)]?.description || 'Processing...'}
                  </Text>
                </div>
              </Space>
            </Card>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default PolicyAnalyzer;

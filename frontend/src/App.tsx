import React, { useState } from 'react';
import { Layout, Button, Space, Typography, Drawer } from 'antd';
import { FileSearchOutlined, HistoryOutlined, SwapOutlined, MenuOutlined } from '@ant-design/icons';
import PolicyAnalyzer from './components/PolicyAnalyzer';
import ReportList from './components/ReportList';
import ReportViewer from './components/ReportViewer';
import PolicyComparator from './components/PolicyComparator';
import './App.css';

const { Header, Content } = Layout;
const { Title } = Typography;

function App() {
  const [currentView, setCurrentView] = useState<'analyzer' | 'reports' | 'viewer' | 'comparator'>('analyzer');
  const [selectedReportId, setSelectedReportId] = useState<number | null>(null);
  const [selectedReportType, setSelectedReportType] = useState<'analysis' | 'comparison'>('analysis');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleMenuClick = (view: 'analyzer' | 'reports' | 'comparator') => {
    setCurrentView(view);
    setMobileMenuOpen(false);
  };

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div className="header-content">
          <Title level={3} className="app-title">
            Privacy Policy Analyzer
          </Title>
          {/* 桌面端菜单 */}
          <Space className="app-menu desktop-menu" size="middle" wrap={false}>
            <Button
              type={currentView === 'analyzer' ? 'primary' : 'default'}
              icon={<FileSearchOutlined />}
              onClick={() => setCurrentView('analyzer')}
            >
              Analyze Policy
            </Button>
            <Button
              type={currentView === 'comparator' ? 'primary' : 'default'}
              icon={<SwapOutlined />}
              onClick={() => setCurrentView('comparator')}
            >
              Compare Versions
            </Button>
            <Button
              type={currentView === 'reports' ? 'primary' : 'default'}
              icon={<HistoryOutlined />}
              onClick={() => setCurrentView('reports')}
            >
              History
            </Button>
          </Space>
          
          {/* 移动端汉堡菜单按钮 */}
          <Button
            className="mobile-menu-button"
            icon={<MenuOutlined />}
            onClick={() => setMobileMenuOpen(true)}
            type="text"
          />
        </div>
      </Header>

      {/* 移动端抽屉菜单 */}
      <Drawer
        title="Menu"
        placement="right"
        onClose={() => setMobileMenuOpen(false)}
        open={mobileMenuOpen}
        className="mobile-menu-drawer"
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Button
            type={currentView === 'analyzer' ? 'primary' : 'default'}
            icon={<FileSearchOutlined />}
            onClick={() => handleMenuClick('analyzer')}
            block
            size="large"
            style={{ height: '48px', fontSize: '16px' }}
          >
            Analyze Policy
          </Button>
          <Button
            type={currentView === 'comparator' ? 'primary' : 'default'}
            icon={<SwapOutlined />}
            onClick={() => handleMenuClick('comparator')}
            block
            size="large"
            style={{ height: '48px', fontSize: '16px' }}
          >
            Compare Versions
          </Button>
          <Button
            type={currentView === 'reports' ? 'primary' : 'default'}
            icon={<HistoryOutlined />}
            onClick={() => handleMenuClick('reports')}
            block
            size="large"
            style={{ height: '48px', fontSize: '16px' }}
          >
            History
          </Button>
        </Space>
      </Drawer>

      <Content className="app-content">
        {currentView === 'analyzer' && (
          <PolicyAnalyzer 
            onAnalysisComplete={(reportId) => {
              setSelectedReportId(reportId);
              setCurrentView('viewer');
            }}
          />
        )}
        
        {currentView === 'comparator' && (
          <PolicyComparator />
        )}
        
        {currentView === 'reports' && (
          <ReportList 
            onSelectReport={(reportId, type) => {
              setSelectedReportId(reportId);
              setSelectedReportType(type);
              setCurrentView('viewer');
            }}
          />
        )}
        
        {currentView === 'viewer' && selectedReportId && (
          <ReportViewer 
            reportId={selectedReportId}
            reportType={selectedReportType}
            onBack={() => setCurrentView('reports')}
          />
        )}
      </Content>
    </Layout>
  );
}

export default App;

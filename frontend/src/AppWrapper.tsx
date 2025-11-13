import React from 'react';
import { ConfigProvider } from 'antd';
import App from './App';

const AppWrapper: React.FC = () => {
  return (
    <ConfigProvider>
      <App />
    </ConfigProvider>
  );
};

export default AppWrapper;


import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// 导入dayjs的中文语言包和插件
import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
import relativeTime from 'dayjs/plugin/relativeTime';

// 配置dayjs
dayjs.locale('zh-cn');
dayjs.extend(relativeTime);

// 渲染应用
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
); 
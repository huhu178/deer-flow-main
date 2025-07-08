/**
 * API配置组件 - 团队协作必备
 * 允许每个人配置自己的本地后端地址
 */
'use client';

import React, { useState } from 'react';
import { Settings, Save, RotateCcw } from 'lucide-react';

interface ApiConfigProps {
  className?: string;
}

const ApiConfig: React.FC<ApiConfigProps> = ({ className = '' }) => {
  // 默认API地址列表
  const defaultUrls = [
    'http://localhost:8000/api',
    'http://localhost:3000/api', 
    'http://localhost:5000/api',
    'http://127.0.0.1:8000/api',
  ];

  const [apiUrl, setApiUrl] = useState(defaultUrls[0] || 'http://localhost:8000/api');
  const [isOpen, setIsOpen] = useState(false);
  const [saved, setSaved] = useState(false);
  const [tempApiUrl, setTempApiUrl] = useState(apiUrl);

  // 保存API地址
  const saveApiUrl = () => {
    if (!tempApiUrl.trim()) {
      alert('请输入有效的API地址');
      return;
    }
    try {
      new URL(tempApiUrl);
      setApiUrl(tempApiUrl);
      
      if (typeof window !== 'undefined') {
        (window as any).DEERFLOW_API_URL = tempApiUrl.trim();
        (window as any).getDeerFlowApiUrl = () => tempApiUrl.trim();
      }
      
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
      setIsOpen(false); 
    } catch (error) {
      alert('请输入正确的URL格式，例如：http://localhost:8000/api');
    }
  };

  // 重置为默认地址
  const resetToDefault = () => {
    setTempApiUrl(defaultUrls[0] || 'http://localhost:8000/api');
  };
  
  const handleOpen = () => {
    setTempApiUrl(apiUrl);
    setIsOpen(true);
  }

  return (
    <div className={`relative ${className}`}>
      {/* 配置按钮 */}
      <button
        onClick={handleOpen}
        className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        title="配置API地址"
      >
        <Settings size={16} />
        API配置
      </button>

      {/* 配置面板 */}
      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-lg p-4 z-50">
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                🔧 后端API地址配置
              </h3>
              <p className="text-xs text-gray-500 mb-3">
                请输入你本地运行的后端服务地址，用于调试和开发
              </p>
            </div>

            {/* URL输入框 */}
            <div>
              <label className="block text-xs text-gray-600 mb-1">
                API地址:
              </label>
              <input
                type="text"
                value={tempApiUrl}
                onChange={(e) => setTempApiUrl(e.target.value)}
                placeholder="http://localhost:8000/api"
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* 快速选择 */}
            <div>
              <label className="block text-xs text-gray-600 mb-1">
                常用地址:
              </label>
              <div className="grid grid-cols-2 gap-1">
                {defaultUrls.map((url, index) => (
                  <button
                    key={index}
                    onClick={() => setTempApiUrl(url)}
                    className="text-xs px-2 py-1 bg-blue-50 hover:bg-blue-100 rounded text-blue-600 transition-colors"
                  >
                    {url.replace('/api', '')}
                  </button>
                ))}
              </div>
            </div>

            {/* 当前状态显示 */}
            <div className="bg-gray-50 p-2 rounded text-xs">
              <span className="text-gray-600">当前配置: </span>
              <span className="font-mono text-blue-600">
                {apiUrl}
              </span>
            </div>

            {/* 操作按钮 */}
            <div className="flex gap-2">
              <button
                onClick={saveApiUrl}
                className={`flex items-center gap-1 px-3 py-2 text-sm rounded-md transition-colors ${
                  saved 
                    ? 'bg-green-500 text-white' 
                    : 'bg-blue-500 hover:bg-blue-600 text-white'
                }`}
              >
                <Save size={14} />
                {saved ? '已保存!' : '保存配置'}
              </button>
              
              <button
                onClick={resetToDefault}
                className="flex items-center gap-1 px-3 py-2 text-sm bg-gray-500 hover:bg-gray-600 text-white rounded-md transition-colors"
              >
                <RotateCcw size={14} />
                重置
              </button>
            </div>

            {/* 使用说明 */}
            <div className="border-t pt-3">
              <p className="text-xs text-gray-500 space-y-1">
                <span className="block">💡 <strong>使用说明:</strong></span>
                <span className="block">1. 启动你的后端服务（如: python src/server.py）</span>
                <span className="block">2. 在上方输入框中输入后端地址</span>
                <span className="block">3. 点击"保存配置"使设置生效</span>
                <span className="block">4. 刷新页面开始调试</span>
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiConfig; 
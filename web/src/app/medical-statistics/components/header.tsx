// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { Settings, User, Server } from "lucide-react";
import React, { useState, useEffect } from "react";

import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";

/**
 * 头部导航组件
 * @description 包含平台标题和用户信息的头部导航栏
 */
export function Header() {
  const [backendUrl, setBackendUrl] = useState("");
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    // On mount, try to load the saved URL from localStorage
    const savedUrl = localStorage.getItem("backendUrl");
    if (savedUrl) {
      setBackendUrl(savedUrl);
    } else {
      // 如果没有保存的URL，可以设置一个默认的开发URL
      setBackendUrl("http://localhost:8000");
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem("backendUrl", backendUrl);
    alert(`后端地址已保存: ${backendUrl}`);
    setShowSettings(false);
  };

  return (
    <header className="sticky top-0 z-50 flex h-16 items-center justify-between gap-4 border-b bg-background px-4 md:px-6">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-bold md:text-2xl">
          国家健康医疗大数据研究院 - 智能数据分析平台
        </h1>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center">
          <span className="mr-2 hidden md:inline">张医生</span>
          <div className="w-8 h-8 rounded-full flex items-center justify-center bg-gray-200 dark:bg-gray-700">
            <User className="h-5 w-5 text-gray-600 dark:text-gray-300" />
          </div>
        </div>
        
        {/* Backend Settings */}
        <div className="relative">
          <Button
            variant="outline"
            size="icon"
            className="h-8 w-8"
            onClick={() => setShowSettings(!showSettings)}
            title="配置后端地址"
          >
            <Settings className="h-5 w-5" />
          </Button>
          {showSettings && (
            <div className="absolute top-full right-0 mt-2 w-80 rounded-md border bg-background p-4 shadow-lg">
              <h4 className="font-medium">配置后端服务地址</h4>
              <p className="mt-1 text-sm text-muted-foreground">
                请输入您暴露的本地后端 URL (例如，使用 ngrok)。
              </p>
              <div className="mt-4 flex items-center gap-2">
                <Server className="h-4 w-4 text-muted-foreground" />
                <Input
                  type="url"
                  placeholder="https://...ngrok-free.app"
                  value={backendUrl}
                  onChange={(e) => setBackendUrl(e.target.value)}
                />
              </div>
              <Button className="mt-4 w-full" onClick={handleSave}>
                保存
              </Button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
} 
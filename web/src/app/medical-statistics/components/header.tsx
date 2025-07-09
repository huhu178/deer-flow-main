// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { Bot, FileCode, Github, LifeBuoy, Settings, User } from "lucide-react";
import React from "react";

import { Button } from "~/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from "~/components/ui/dropdown-menu";

/**
 * 头部导航组件
 * @description 包含平台标题和用户信息的头部导航栏
 */

export function Header() {
  return (
    <header className="bg-blue-700 text-white p-4 shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <h1 className="text-3xl font-bold">
          国家健康医疗大数据研究院 - 智能数据分析平台
        </h1>
        <div className="flex items-center space-x-4">
          <Button 
            variant="ghost" 
            size="icon"
            className="p-2 rounded hover:bg-blue-600 text-white hover:text-white"
            title="设置"
          >
            <Settings className="h-5 w-5" />
          </Button>
          <div className="flex items-center">
            <span className="mr-2">张医生</span>
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <User className="h-4 w-4 text-white" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
} 
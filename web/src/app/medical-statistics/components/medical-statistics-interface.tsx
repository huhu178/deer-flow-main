"use client";

// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import Image from "next/image";
import React, { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "~/components/ui/button";

import { MedicalChatInterface } from "~/app/medical-statistics/components/medical-chat-interface";
import { DatabasePanel } from "./database-panel";
import { DesignAnalysisPanel } from "./design-analysis-panel";

/**
 * 医学统计分析界面组件
 * @description 主界面组件，包含三栏布局：设计分析智能体、聊天界面、数据库智能体
 * 集成现有的聊天接口和状态管理系统
 */
export function MedicalStatisticsInterface() {
  const [leftPanelVisible, setLeftPanelVisible] = useState(true);
  const [rightPanelVisible, setRightPanelVisible] = useState(true);

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <header className="sticky top-0 left-0 z-40 w-full bg-indigo-800 px-6 py-4 text-white shadow-md">
        <div className="flex w-full items-center">
          <div className="mr-4 flex-shrink-0">
            <div className="flex h-20 w-20 items-center justify-center overflow-hidden rounded-full bg-gray-100 p-1.5">
              <Image
                src="/images/logo2.png"
                alt="平台Logo"
                width={56}
                height={56}
                className="object-contain"
              />
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 sm:gap-x-4">
            <span className="whitespace-nowrap text-4xl font-medium">
              国家健康医疗大数据研究院
            </span>
            <span className="hidden text-gray-300 sm:inline">|</span>
            <span className="whitespace-nowrap text-5xl font-semibold">
              医学研究设计与分析AI智能平台
            </span>
            <span className="hidden text-gray-300 md:inline">|</span>
            <span className="whitespace-nowrap text-3xl text-gray-200">
              AI Agent Platform for Medical Research Design and Analysis
            </span>
          </div>
        </div>
      </header>
      
      {/* 主要内容区域 */}
      <div className="flex flex-1 overflow-hidden">
        {/* 左侧面板 */}
        {leftPanelVisible && <DesignAnalysisPanel />}

        {/* 中央区域，包含聊天和切换按钮 */}
        <div className="flex-1 flex flex-col relative">
          {/* 左侧面板切换按钮 */}
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-1/2 -translate-y-1/2 left-0 z-10 h-12 w-6 rounded-l-none bg-gray-200/50 hover:bg-gray-200"
            onClick={() => setLeftPanelVisible(!leftPanelVisible)}
          >
            {leftPanelVisible ? <ChevronLeft className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
          </Button>

          <MedicalChatInterface />

          {/* 右侧面板切换按钮 */}
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-1/2 -translate-y-1/2 right-0 z-10 h-12 w-6 rounded-r-none bg-gray-200/50 hover:bg-gray-200"
            onClick={() => setRightPanelVisible(!rightPanelVisible)}
          >
            {rightPanelVisible ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
          </Button>
        </div>

        {/* 右侧面板 */}
        {rightPanelVisible && <DatabasePanel />}
      </div>
    </div>
  );
} 
// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { Database, FileUp, Filter, Search, Upload } from "lucide-react";
import React from "react";

import { Button } from "~/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "~/components/ui/card";
import { sendMessage } from "~/core/store";

interface DataTypeCardProps {
  title: string;
  subtitle: string;
  tags: string[];
  onSelect: () => void;
}

function DataTypeCard({ title, subtitle, tags, onSelect }: DataTypeCardProps) {
  return (
    <div 
      className="p-4 border border-blue-200 rounded hover:bg-blue-50 cursor-pointer"
      onClick={onSelect}
    >
      <div className="font-bold mb-2 text-lg text-gray-800">{title}</div>
      <div className="text-base text-gray-700 mb-3">{subtitle}</div>
      <div className="grid grid-cols-2 gap-2">
        {tags.map((tag, index) => (
          <div key={index} className="text-sm bg-gray-100 p-2 rounded text-gray-700 font-medium">
            {tag}
          </div>
        ))}
      </div>
    </div>
  );
}

interface CohortDatabaseProps {
  name: string;
  count: string;
  color: string;
}

function CohortDatabase({ name, count, color }: CohortDatabaseProps) {
  return (
    <div className="p-3 border border-blue-200 rounded text-base flex justify-between items-center">
      <div className="flex items-center">
        <Database className={`w-5 h-5 mr-3 ${color}`} />
        <span className="font-semibold text-gray-800">{name}</span>
      </div>
      <span className="text-sm text-gray-600 font-medium">{count}</span>
    </div>
  );
}

export function DatabasePanel() {
  const handleDataAnalysisSelect = async (dataType: string, analysisType: string) => {
    const prompt = `请帮我进行${dataType}的统计分析。

数据类型：${dataType}
分析类型：${analysisType}

请提供以下内容：
1. 数据预处理和清洗策略
2. 描述性统计分析方法
3. 推断统计分析方案
4. 可视化呈现建议
5. 结果解释和临床意义
6. 统计软件使用建议

请根据医学统计学原理提供专业的分析方案。`;
    await sendMessage(prompt);
  };

  const handleDatabaseConnection = async () => {
    const prompt = `我需要连接和访问医学队列数据库，请提供以下指导：

1. 数据库连接的标准流程
2. 数据安全和隐私保护措施
3. 数据质量评估方法
4. 数据提取和整理策略
5. 多数据源整合方案
6. 数据分析环境搭建

请提供专业的数据管理建议。`;
    await sendMessage(prompt);
  };

  return (
    <div className="bg-white border-l border-blue-200 w-72">
      <div className="p-4 h-full overflow-y-auto scrollbar-hide" style={{scrollbarWidth: 'none', msOverflowStyle: 'none'}}>
        <div className="mb-4">
          <h2 className="text-2xl font-bold mb-2 text-gray-900">数据库智能体</h2>
          <div className="text-base text-gray-700 mb-3">医学队列数据库智能管理与分析</div>
          <Button 
            className="mt-2 w-full p-3 bg-blue-600 text-white rounded flex items-center justify-center hover:bg-blue-700 text-lg font-semibold"
            onClick={handleDatabaseConnection}
          >
            <Database className="w-5 h-5 mr-2" />
            连接队列数据库
          </Button>
        </div>
        
        <div className="space-y-4">
          <DataTypeCard
            title="结构数据"
            subtitle="统计学语言表征智能体"
            tags={["人口学特征分析", "临床指标统计", "风险因素评估", "结局事件分析"]}
            onSelect={() => handleDataAnalysisSelect("结构数据", "统计学语言表征智能体")}
          />
          
          <DataTypeCard
            title="组学数据"
            subtitle="生物组学语言表征的跨组学数据库"
            tags={["基因组数据解析", "转录组表达谱"]}
            onSelect={() => handleDataAnalysisSelect("组学数据", "生物组学语言表征的跨组学数据库")}
          />
          
          <DataTypeCard
            title="多模态数据"
            subtitle="AI语言表征的多模态数据库"
            tags={["医学影像特征提取", "临床文本语义分析"]}
            onSelect={() => handleDataAnalysisSelect("多模态数据", "AI语言表征的多模态数据库")}
          />
        </div>
        
        <div className="mt-4 border-t border-blue-200 pt-4">
          <h3 className="text-xl font-bold mb-3 text-gray-800">可访问的队列数据库</h3>
          <div className="space-y-2">
            <CohortDatabase
              name="国家心血管疾病队列"
              count="10,453例"
              color="text-green-600"
            />
            <CohortDatabase
              name="肿瘤精准医疗队列"
              count="8,752例"
              color="text-blue-600"
            />
            <CohortDatabase
              name="慢性代谢性疾病队列"
              count="12,845例"
              color="text-purple-600"
            />
          </div>
        </div>
      </div>
    </div>
  );
} 
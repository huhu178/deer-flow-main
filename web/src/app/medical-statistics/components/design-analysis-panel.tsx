// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

/**
 * 设计分析面板组件
 * @description 左侧面板，包含各种流行病学研究设计的智能体选项
 */

import {
  Lightbulb,
  FileText,
  BarChart,
  Settings,
  Bot,
  Search,
  Layers,
  Zap,
} from "lucide-react";
import React from "react";

import { Input } from "~/components/ui/input";
import { sendMessage } from "~/core/store";

interface AnalysisAgentProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  iconColor: string;
  onSelect: () => void;
}

function AnalysisAgent({ icon, title, description, iconColor, onSelect }: AnalysisAgentProps) {
  return (
    <div 
      className="p-3 border border-blue-200 rounded hover:bg-blue-50 cursor-pointer transition"
      onClick={onSelect}
    >
      <div className="font-bold text-lg flex items-center text-gray-800">
        <span className={`${iconColor} mr-2`}>
          {icon}
        </span>
        {title}
      </div>
      <div className="text-lg text-gray-700 ml-6">{description}</div>
    </div>
  );
}

// 医学研究设计模板
const generateResearchDesignPrompt = (designType: string, description: string) => {
  return `请帮我设计一个${designType}研究方案。

研究类型：${designType}
研究描述：${description}

请提供以下内容：
1. 研究目标和假设
2. 研究设计要点
3. 样本量计算方法
4. 统计分析策略
5. 潜在的偏倚和局限性
6. 质量控制措施

请根据循证医学原则和流行病学方法学提供专业的建议。`;
};

export function DesignAnalysisPanel() {
  
  const handleResearchDesignSelect = async (designType: string, description: string) => {
    const prompt = generateResearchDesignPrompt(designType, description);
    await sendMessage(prompt);
  };



  return (
    <div className="bg-white border-r border-blue-200 w-72">
      <div className="p-4 h-full overflow-y-auto scrollbar-hide" style={{scrollbarWidth: 'none', msOverflowStyle: 'none'}}>
        <div className="mb-4">
          <h2 className="text-2xl font-bold mb-2 text-gray-900">设计分析智能体</h2>
          <div className="text-base text-gray-700 mb-3">流行病学研究设计与分析方法</div>
          <div className="relative mb-4">
            <Input 
              type="text" 
              placeholder="搜索研究设计..." 
              className="w-full p-3 pl-8 border border-blue-200 rounded text-lg"
            />
            <Search className="w-4 h-4 text-gray-400 absolute left-2 top-3" />
          </div>


        </div>



        {/* 实验性研究智能体 */}
        <div className="mb-4">
          <h3 className="text-xl font-bold mb-2 text-gray-800">实验性研究智能体</h3>
          <div className="space-y-3">
            <AnalysisAgent
              icon={<Layers className="w-4 h-3" />}
              title="随机对照临床试验（RCT）智能体"
              description="经典随机对照试验设计与分析"
              iconColor="text-red-600"
              onSelect={() => handleResearchDesignSelect("随机对照临床试验(RCT)", "经典随机对照试验设计与分析")}
            />
            <AnalysisAgent
              icon={<Zap className="w-4 h-3" />}
              title="实效性RCT智能体"
              description="研究真实世界临床效果的试验设计"
              iconColor="text-green-600"
              onSelect={() => handleResearchDesignSelect("实效性RCT", "研究真实世界临床效果的试验设计")}
            />
            <AnalysisAgent
              icon={<FileText className="w-4 h-3" />}
              title="适应性RCT智能体"
              description="可动态调整的临床试验设计"
              iconColor="text-purple-600"
              onSelect={() => handleResearchDesignSelect("适应性RCT", "可动态调整的临床试验设计")}
            />
            <AnalysisAgent
              icon={<Layers className="w-4 h-3" />}
              title="组群RCT智能体"
              description="按群体随机分组的临床试验"
              iconColor="text-blue-600"
              onSelect={() => handleResearchDesignSelect("组群RCT", "按群体随机分组的临床试验")}
            />
            <AnalysisAgent
              icon={<Zap className="w-4 h-3" />}
              title="组群序贯RCT智能体"
              description="序列组群随机对照试验设计"
              iconColor="text-orange-600"
              onSelect={() => handleResearchDesignSelect("组群序贯RCT", "序列组群随机对照试验设计")}
            />
            <AnalysisAgent
              icon={<FileText className="w-4 h-3" />}
              title="阶梯RCT智能体"
              description="多阶段渐进式临床试验设计"
              iconColor="text-teal-600"
              onSelect={() => handleResearchDesignSelect("阶梯RCT", "多阶段渐进式临床试验设计")}
            />
            <AnalysisAgent
              icon={<Layers className="w-4 h-3" />}
              title="病人偏好RCT智能体"
              description="考虑患者治疗偏好的随机试验"
              iconColor="text-indigo-600"
              onSelect={() => handleResearchDesignSelect("病人偏好RCT", "考虑患者治疗偏好的随机试验")}
            />
          </div>
        </div>

        {/* 观察性研究智能体 */}
        <div>
          <h3 className="text-xl font-bold mb-2 text-gray-800">观察性研究智能体</h3>
          <div className="space-y-3">
            <AnalysisAgent
              icon={<FileText className="w-4 h-3" />}
              title="病例系列设计智能体"
              description="聚焦特定疾病患者群体的临床特征分析"
              iconColor="text-blue-600"
              onSelect={() => handleResearchDesignSelect("病例系列设计", "聚焦特定疾病患者群体的临床特征分析")}
            />
            <AnalysisAgent
              icon={<Zap className="w-4 h-3" />}
              title="横断面设计智能体"
              description="特定时间点的疾病与因素关系研究"
              iconColor="text-orange-600"
              onSelect={() => handleResearchDesignSelect("横断面设计", "特定时间点的疾病与因素关系研究")}
            />
            <AnalysisAgent
              icon={<Layers className="w-4 h-3" />}
              title="病例对照设计智能体"
              description="疾病与暴露因素关联的回顾性分析"
              iconColor="text-purple-600"
              onSelect={() => handleResearchDesignSelect("病例对照设计", "疾病与暴露因素关联的回顾性分析")}
            />
            <AnalysisAgent
              icon={<FileText className="w-4 h-3" />}
              title="队列设计智能体"
              description="前瞻性跟踪观察不同暴露人群"
              iconColor="text-green-600"
              onSelect={() => handleResearchDesignSelect("队列设计", "前瞻性跟踪观察不同暴露人群")}
            />
            <AnalysisAgent
              icon={<Layers className="w-4 h-3" />}
              title="巢式病例对照设计智能体"
              description="队列内嵌套的病例对照研究设计"
              iconColor="text-indigo-600"
              onSelect={() => handleResearchDesignSelect("巢式病例对照设计", "队列内嵌套的病例对照研究设计")}
            />
            <AnalysisAgent
              icon={<FileText className="w-4 h-3" />}
              title="病例队列设计智能体"
              description="混合病例系列与队列特点的研究设计"
              iconColor="text-red-600"
              onSelect={() => handleResearchDesignSelect("病例队列设计", "混合病例系列与队列特点的研究设计")}
            />
            <AnalysisAgent
              icon={<Zap className="w-4 h-3" />}
              title="病例交叉设计智能体"
              description="自身对照非稳定暴露的影响研究"
              iconColor="text-yellow-600"
              onSelect={() => handleResearchDesignSelect("病例交叉设计", "自身对照非稳定暴露的影响研究")}
            />
            <AnalysisAgent
              icon={<Layers className="w-4 h-3" />}
              title="病例-时间-对照设计智能体"
              description="病例发生与暴露时间关系的评估"
              iconColor="text-blue-500"
              onSelect={() => handleResearchDesignSelect("病例-时间-对照设计", "病例发生与暴露时间关系的评估")}
            />
            <AnalysisAgent
              icon={<FileText className="w-4 h-3" />}
              title="纵向队列设计智能体"
              description="长期追踪观察的队列数据分析方法"
              iconColor="text-teal-600"
              onSelect={() => handleResearchDesignSelect("纵向队列设计", "长期追踪观察的队列数据分析方法")}
            />
            <AnalysisAgent
              icon={<Zap className="w-4 h-3" />}
              title="新使用者设计智能体"
              description="药物或治疗新使用者队列的效应评估"
              iconColor="text-pink-600"
              onSelect={() => handleResearchDesignSelect("新使用者设计", "药物或治疗新使用者队列的效应评估")}
            />
            <AnalysisAgent
              icon={<FileText className="w-4 h-3" />}
              title="自主设计智能体"
              description="定制个性化研究设计方案"
              iconColor="text-orange-600"
              onSelect={() => handleResearchDesignSelect("自主设计", "定制个性化研究设计方案")}
            />
          </div>
        </div>
      </div>
    </div>
  );
} 
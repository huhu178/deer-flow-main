#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Research 功能实现指南
在当前 Deer-Flow 系统中实现 Google Gemini Deep Research 功能
"""

import sys
import os
import time
sys.path.append('src')

class DeepResearchEngine:
    """Deep Research 引擎，基于 Gemini 2.5 Pro 实现"""
    
    def __init__(self):
        """初始化 Deep Research 引擎"""
        try:
            from llms.llm import get_llm_by_type
            self.llm = get_llm_by_type("BASIC_MODEL")  # 使用OpenRouter的Gemini 2.5 Pro
            print("✅ Deep Research 引擎初始化成功")
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            self.llm = None
    
    def deep_research(self, topic, research_depth="comprehensive", time_range="2023-2025"):
        """
        执行深度研究
        
        Args:
            topic: 研究主题
            research_depth: 研究深度 (basic/comprehensive/expert)
            time_range: 时间范围
        """
        if not self.llm:
            return "❌ LLM未正确初始化"
        
        # 构建Deep Research专用提示词
        prompt = self._build_deep_research_prompt(topic, research_depth, time_range)
        
        try:
            print(f"🔬 开始深度研究: {topic}")
            print("=" * 50)
            
            from langchain.schema import HumanMessage
            messages = [HumanMessage(content=prompt)]
            
            start_time = time.time()
            result = self.llm.invoke(messages)
            end_time = time.time()
            
            duration = end_time - start_time
            content = result.content if hasattr(result, 'content') else str(result)
            
            print(f"✅ 研究完成，用时: {duration:.1f}秒")
            print(f"📊 报告长度: {len(content)}字符")
            
            return content
            
        except Exception as e:
            return f"❌ 研究过程出错: {e}"
    
    def _build_deep_research_prompt(self, topic, depth, time_range):
        """构建Deep Research专用提示词"""
        
        depth_instructions = {
            "basic": "进行基础层面的研究分析",
            "comprehensive": "进行全面深入的研究分析，包含多个维度和角度",
            "expert": "进行专家级深度研究，要求极高的分析质量和洞察深度"
        }
        
        prompt = f"""
[DEEP RESEARCH MODE - 深度研究模式]

作为一个专业的AI研究助手，请对以下主题进行深度研究分析：

📋 研究主题: {topic}
🎯 研究深度: {depth_instructions.get(depth, '全面分析')}
⏰ 时间范围: {time_range}

🔍 请按以下流程执行深度研究：

## 第一阶段：研究规划 (PLANNING)
1. 分析研究主题的核心要素
2. 制定多维度研究计划
3. 确定关键研究方向和问题

## 第二阶段：信息搜索 (SEARCHING) 
4. 利用您的知识库搜索相关信息
5. 识别权威来源和最新发展
6. 收集多角度的观点和数据

## 第三阶段：深度推理 (REASONING)
7. 对收集的信息进行批判性分析
8. 识别模式、趋势和关联性
9. 评估不同观点的可靠性
10. 进行逻辑推理和假设验证

## 第四阶段：综合报告 (REPORTING)
11. 整合所有研究发现
12. 生成结构化的研究报告
13. 提供明确的结论和建议
14. 注明信息来源和置信度

📊 输出要求：
- 使用清晰的标题和子标题结构化内容
- 在每个部分展示您的思考过程
- 提供具体的数据、案例和证据
- 包含前瞻性的分析和预测
- 标注关键信息的可靠性评估

🎯 特别要求：
- 展示多步推理过程
- 考虑不同利益相关者的观点
- 分析潜在的风险和机遇
- 提供可操作的建议

现在开始执行深度研究...
"""
        
        return prompt
    
    def batch_research(self, topics_list):
        """批量执行深度研究"""
        results = {}
        
        for i, topic in enumerate(topics_list, 1):
            print(f"\n🔬 批量研究 {i}/{len(topics_list)}: {topic}")
            result = self.deep_research(topic)
            results[topic] = result
            
            # 避免API限制，添加延迟
            if i < len(topics_list):
                print("⏳ 等待5秒后继续...")
                time.sleep(5)
        
        return results

def demo_deep_research():
    """Deep Research 功能演示"""
    
    print("🎯 Deep Research 功能演示")
    print("=" * 60)
    
    # 初始化研究引擎
    engine = DeepResearchEngine()
    
    if not engine.llm:
        print("❌ 无法初始化，请检查配置")
        return
    
    # 示例研究主题
    demo_topics = [
        "人工智能在医疗诊断中的最新突破与挑战",
        "量子计算对现代密码学的影响",
        "2025年可持续能源技术发展趋势"
    ]
    
    print("📋 可选研究主题:")
    for i, topic in enumerate(demo_topics, 1):
        print(f"  {i}. {topic}")
    
    try:
        choice = input("\n请选择主题 (1-3) 或输入自定义主题: ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= 3:
            selected_topic = demo_topics[int(choice) - 1]
        else:
            selected_topic = choice if choice else demo_topics[0]
        
        print(f"\n🎯 开始研究: {selected_topic}")
        
        # 执行深度研究
        result = engine.deep_research(
            topic=selected_topic,
            research_depth="comprehensive"
        )
        
        print("\n" + "="*60)
        print("📝 深度研究报告:")
        print("="*60)
        print(result)
        
        # 保存报告
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"deep_research_report_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Deep Research Report\n\n")
            f.write(f"**主题**: {selected_topic}\n\n")
            f.write(f"**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            f.write(result)
        
        print(f"\n💾 报告已保存至: {filename}")
        
    except KeyboardInterrupt:
        print("\n👋 研究已取消")
    except Exception as e:
        print(f"\n❌ 执行出错: {e}")

if __name__ == "__main__":
    demo_deep_research() 
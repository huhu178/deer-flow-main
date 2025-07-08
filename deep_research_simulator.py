#!/usr/bin/env python3
"""
Deep Research 模拟器 - 使用Thinking模型 + 搜索工具实现类似Deep Research的功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import json
from typing import List, Dict
from datetime import datetime
import yaml

from llms.llm import get_llm
from tools.tavily_search.search import TavilySearchTool
from tools.crawl import CrawlTool

class DeepResearchSimulator:
    """模拟Deep Research功能的综合系统"""
    
    def __init__(self):
        """初始化研究模拟器"""
        self.llm = get_llm("BASIC_MODEL")  # 使用thinking版本
        self.search_tool = TavilySearchTool()
        self.crawl_tool = CrawlTool()
        self.research_plan = []
        self.gathered_info = []
        self.sources = []
        
    def create_research_plan(self, query: str) -> List[str]:
        """
        创建研究计划 - 模拟Deep Research的计划阶段
        """
        print("🔍 正在制定研究计划...")
        
        planning_prompt = f"""
作为一个AI研究助手，请为以下查询制定详细的研究计划：

查询：{query}

请按照Deep Research的方式，将这个复杂查询分解为多个可管理的子任务。
每个子任务应该：
1. 明确具体
2. 可以通过网络搜索解决
3. 互相补充形成完整画面

请以JSON格式返回研究计划：
{{
    "research_objectives": "总体研究目标",
    "sub_tasks": [
        {{
            "task": "子任务描述",
            "search_keywords": ["搜索关键词1", "搜索关键词2"],
            "priority": 1
        }}
    ]
}}

请确保计划全面且逻辑清晰。
"""
        
        try:
            response = self.llm.invoke(planning_prompt)
            # 尝试解析JSON
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                plan_data = json.loads(json_match.group())
                self.research_plan = plan_data.get('sub_tasks', [])
                print(f"✅ 研究计划已制定，包含 {len(self.research_plan)} 个子任务")
                return self.research_plan
            else:
                # 如果JSON解析失败，创建基础计划
                return self._create_basic_plan(query)
        except Exception as e:
            print(f"⚠️ 计划制定过程中出现问题：{e}")
            return self._create_basic_plan(query)
    
    def _create_basic_plan(self, query: str) -> List[str]:
        """创建基础研究计划"""
        basic_tasks = [
            {
                "task": f"搜索{query}的基本信息和定义",
                "search_keywords": [query, "定义", "介绍"],
                "priority": 1
            },
            {
                "task": f"查找{query}的最新发展和趋势",
                "search_keywords": [query, "最新", "趋势", "2024", "2025"],
                "priority": 2
            },
            {
                "task": f"分析{query}的具体案例和应用",
                "search_keywords": [query, "案例", "应用", "实例"],
                "priority": 3
            }
        ]
        self.research_plan = basic_tasks
        return basic_tasks
    
    async def execute_research_plan(self) -> List[Dict]:
        """
        执行研究计划 - 模拟Deep Research的搜索阶段
        """
        print("🔎 开始执行研究计划...")
        
        for i, task in enumerate(self.research_plan, 1):
            print(f"\n📋 执行子任务 {i}: {task['task']}")
            
            # 为每个子任务执行搜索
            search_results = []
            for keyword in task.get('search_keywords', []):
                try:
                    print(f"  🔍 搜索关键词: {keyword}")
                    results = await self.search_tool.search(keyword, max_results=3)
                    if results:
                        search_results.extend(results)
                    await asyncio.sleep(1)  # 避免请求过于频繁
                except Exception as e:
                    print(f"  ⚠️ 搜索出错: {e}")
            
            # 保存搜索结果
            if search_results:
                task_info = {
                    "task": task['task'],
                    "results": search_results,
                    "timestamp": datetime.now().isoformat()
                }
                self.gathered_info.append(task_info)
                
                # 收集源链接
                for result in search_results:
                    if 'url' in result:
                        self.sources.append(result['url'])
                
                print(f"  ✅ 找到 {len(search_results)} 条相关信息")
            else:
                print(f"  ❌ 未找到相关信息")
        
        print(f"\n🎯 研究完成！共收集 {len(self.gathered_info)} 个任务的信息")
        return self.gathered_info
    
    def synthesize_report(self, original_query: str) -> str:
        """
        综合报告 - 模拟Deep Research的报告生成阶段
        """
        print("📝 正在生成综合研究报告...")
        
        # 准备所有收集到的信息
        all_info = ""
        for task_info in self.gathered_info:
            all_info += f"\n\n## {task_info['task']}\n"
            for result in task_info['results']:
                all_info += f"- {result.get('title', '')}\n"
                all_info += f"  摘要: {result.get('content', '')[:200]}...\n"
                all_info += f"  来源: {result.get('url', '')}\n"
        
        synthesis_prompt = f"""
作为一个专业的研究分析师，请基于以下收集的信息，为查询"{original_query}"生成一份全面的Deep Research风格报告。

收集到的信息：
{all_info}

请按照以下结构生成报告：

# {original_query} - 深度研究报告

## 执行摘要
[提供核心发现的简洁概述]

## 背景与概述
[详细介绍主题背景]

## 关键发现
[基于搜索结果的主要发现，分点列出]

## 深度分析
[对关键发现进行深入分析和解释]

## 趋势与展望
[基于收集信息分析未来趋势]

## 结论与建议
[总结关键要点并提供实用建议]

## 参考来源
[列出所有引用的来源]

要求：
1. 使用thinking过程展示你的分析思路
2. 基于实际搜索结果，不要编造信息
3. 保持客观和批判性思维
4. 突出关键洞察和模式
5. 提供实用的结论
"""
        
        try:
            response = self.llm.invoke(synthesis_prompt)
            return response.content
        except Exception as e:
            print(f"❌ 报告生成失败: {e}")
            return f"报告生成过程中出现错误: {e}"
    
    async def run_deep_research(self, query: str) -> Dict:
        """
        运行完整的Deep Research模拟流程
        """
        print(f"🚀 启动Deep Research模拟器")
        print(f"📋 研究查询: {query}")
        print("=" * 60)
        
        start_time = datetime.now()
        
        # 1. 制定研究计划
        plan = self.create_research_plan(query)
        
        # 2. 执行研究
        research_data = await self.execute_research_plan()
        
        # 3. 生成报告
        report = self.synthesize_report(query)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 保存结果
        result = {
            "query": query,
            "research_plan": plan,
            "gathered_data": research_data,
            "report": report,
            "sources": list(set(self.sources)),  # 去重
            "duration": duration,
            "timestamp": start_time.isoformat()
        }
        
        # 保存到文件
        output_dir = "outputs/deep_research_simulation"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"deep_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Deep Research模拟完成！")
        print(f"⏱️ 耗时: {duration:.1f} 秒")
        print(f"📄 报告已保存: {filepath}")
        print(f"🔗 共收集 {len(self.sources)} 个信息源")
        
        return result

async def main():
    """主函数"""
    simulator = DeepResearchSimulator()
    
    # 示例查询
    test_queries = [
        "人工智能在医疗健康领域的最新应用和发展趋势",
        "2025年量子计算技术的突破性进展",
        "可持续能源技术的创新发展现状"
    ]
    
    print("🎯 Deep Research 模拟器")
    print("请选择一个查询进行测试，或输入自定义查询：")
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query}")
    
    choice = input("\n请输入选择 (1-3) 或直接输入自定义查询: ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= 3:
        selected_query = test_queries[int(choice) - 1]
    else:
        selected_query = choice if choice else test_queries[0]
    
    print(f"\n🔍 开始研究: {selected_query}")
    
    try:
        result = await simulator.run_deep_research(selected_query)
        
        print("\n" + "="*60)
        print("📋 研究报告预览:")
        print("="*60)
        print(result['report'][:1000] + "..." if len(result['report']) > 1000 else result['report'])
        
    except Exception as e:
        print(f"❌ 研究过程中出现错误: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模型研究系统启动脚本 - 集成版
使用src项目的完整工作流，支持多模型并行报告生成
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目路径
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from src.workflow import run_agent_workflow_async
from src.utils.multi_model_manager import MultiModelManager

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def run_integrated_multi_model_research(
    query: str, 
    enable_multi_model: bool = True,
    max_plan_iterations: int = 2,
    max_step_num: int = 5
):
    """
    运行集成的多模型研究
    
    Args:
        query: 研究查询
        enable_multi_model: 是否启用多模型报告生成
        max_plan_iterations: 最大计划迭代次数
        max_step_num: 最大步骤数
    """
    print(f"🚀 启动集成多模型研究系统")
    print(f"📝 研究查询: {query[:100]}...")
    print(f"🔧 多模型模式: {'启用' if enable_multi_model else '禁用'}")
    print(f"⚙️ 最大计划迭代: {max_plan_iterations}")
    print(f"📊 最大步骤数: {max_step_num}")
    print("=" * 80)
    
    try:
        # 运行完整的工作流
        final_state = await run_agent_workflow_async(
            user_input=query,
            debug=False,
            max_plan_iterations=max_plan_iterations,
            max_step_num=max_step_num,
            enable_background_investigation=True,
            enable_multi_model_report=enable_multi_model,
            locale="zh-CN"
        )
        
        print("\n✅ 研究任务完成！")
        
        # 输出结果摘要
        if "final_report" in final_state:
            print("\n📊 生成的报告:")
            print("=" * 80)
            print(final_state["final_report"][:1500])  # 显示前1500字符
            if len(final_state["final_report"]) > 1500:
                print("...\n(报告内容较长，已截断显示)")
            print("=" * 80)
        
        # 如果有多模型结果，显示详细信息
        if "multi_model_results" in final_state:
            results = final_state["multi_model_results"]
            print(f"\n🎯 多模型生成统计:")
            print(f"- 参与模型: {results['summary']['total_models']}")
            print(f"- 成功生成: {results['summary']['successful_reports']}")
            print(f"- 总耗时: {results['summary']['total_execution_time']:.2f}秒")
            
            print(f"\n📁 保存的文件:")
            if "saved_files" in final_state:
                for file_type, filepath in final_state["saved_files"].items():
                    print(f"- {file_type}: {filepath}")
        
        return final_state
        
    except Exception as e:
        print(f"❌ 研究任务执行失败: {e}")
        logger.error(f"工作流执行错误: {e}")
        raise


async def demo_13_dimension_research():
    """
    演示13维度调研框架的多模型研究
    """
    print("🎯 13维度调研框架多模型演示")
    print("=" * 80)
    
    # 13维度调研查询
    query = """
请基于13维度调研框架，对"基于DXA影像AI特征的骨-心血管轴研究"进行全面分析。

请重点关注以下13个维度：

1. **重要的临床问题**: 当前骨-心血管疾病诊断和治疗面临的主要挑战
2. **重要的科学问题**: AI技术在DXA影像分析中的核心科学问题
3. **近三年科学进展**: 2022-2024年骨-心血管轴研究的重要突破
4. **交叉学科机会**: AI、医学影像、心血管学、骨科学的融合机会
5. **方法学创新**: 新的算法、模型架构和分析技术
6. **专利授权状况**: 相关技术的知识产权现状和趋势
7. **国际合作机会**: 全球范围内的合作研究机会和平台
8. **科研资金支持**: 政府和企业在该领域的资助情况
9. **伦理与合规要求**: 医疗AI的伦理规范和监管要求
10. **开放数据资源**: 可用的公开数据集和共享资源
11. **公共卫生事件影响**: 疫情等对该研究领域的影响
12. **国家政策环境**: 相关政策法规和发展规划
13. **综合评估与机会识别**: 未来发展机遇、挑战和建议

请生成详细的研究报告，包括现状分析、技术趋势、挑战与机遇、发展建议等内容。
    """
    
    print(f"📋 研究主题: 基于DXA影像AI特征的骨-心血管轴研究")
    print(f"🔍 分析框架: 13维度调研框架")
    print(f"🎯 目标: 全面分析和评估")
    print("\n" + "=" * 80)
    
    # 运行多模型研究
    result = await run_integrated_multi_model_research(
        query=query, 
        enable_multi_model=True,
        max_plan_iterations=2,
        max_step_num=6
    )
    
    return result


async def demo_ai_medical_imaging():
    """
    演示AI医学影像分析的多模型研究
    """
    print("🎯 AI医学影像分析多模型演示")
    print("=" * 80)
    
    query = """
请对人工智能在医学影像分析领域的应用进行全面研究分析。

研究重点包括：
1. 技术现状和发展趋势
2. 主要应用场景和成功案例
3. 技术挑战和解决方案
4. 市场前景和商业化机会
5. 监管环境和伦理考量
6. 未来发展方向和建议

请生成专业的研究报告，包括技术分析、市场分析、风险评估等内容。
    """
    
    print(f"📋 研究主题: AI医学影像分析")
    print(f"🔍 分析角度: 技术、市场、监管、未来")
    print(f"🎯 目标: 全面评估和建议")
    print("\n" + "=" * 80)
    
    # 运行多模型研究
    result = await run_integrated_multi_model_research(
        query=query, 
        enable_multi_model=True,
        max_plan_iterations=2,
        max_step_num=4
    )
    
    return result


async def compare_single_vs_multi_model():
    """
    对比单模型和多模型的效果
    """
    print("\n🔍 单模型 vs 多模型对比测试")
    print("=" * 80)
    
    test_query = """
请分析深度学习技术在骨科疾病诊断中的应用现状，包括：
1. 主要技术方法和算法
2. 临床应用效果和案例
3. 技术挑战和限制
4. 发展前景和建议

要求生成简洁但全面的分析报告。
    """
    
    print("🔄 运行单模型模式...")
    single_result = await run_integrated_multi_model_research(
        test_query, 
        enable_multi_model=False,
        max_plan_iterations=1,
        max_step_num=3
    )
    
    print("\n🔄 运行多模型模式...")
    multi_result = await run_integrated_multi_model_research(
        test_query, 
        enable_multi_model=True,
        max_plan_iterations=1,
        max_step_num=3
    )
    
    print("\n📊 对比结果:")
    print(f"- 单模型报告长度: {len(single_result.get('final_report', ''))}字符")
    if 'multi_model_results' in multi_result:
        multi_summary = multi_result['multi_model_results']['summary']
        print(f"- 多模型参与数量: {multi_summary['total_models']}")
        print(f"- 多模型成功数量: {multi_summary['successful_reports']}")
        print(f"- 多模型总耗时: {multi_summary['total_execution_time']:.2f}秒")


def show_system_status():
    """显示系统状态"""
    print("🔧 系统状态检查")
    print("=" * 60)
    
    # 检查多模型配置
    try:
        manager = MultiModelManager()
        manager.show_status()
        
        available_models = manager.get_available_models()
        if available_models:
            print(f"\n✅ 系统就绪，可使用 {len(available_models)} 个模型")
        else:
            print(f"\n⚠️ 没有可用的模型，请检查配置")
            
    except Exception as e:
        print(f"\n❌ 系统检查失败: {e}")


def main():
    """
    主函数
    """
    print("🎉 欢迎使用deer-flow集成多模型研究系统！")
    print("=" * 80)
    
    # 显示系统状态
    show_system_status()
    
    print("\n选择运行模式:")
    print("1. 13维度调研框架演示 (推荐)")
    print("2. AI医学影像分析演示")
    print("3. 单模型vs多模型对比")
    print("4. 自定义研究查询")
    print("5. 仅显示系统状态")
    
    try:
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            asyncio.run(demo_13_dimension_research())
        elif choice == "2":
            asyncio.run(demo_ai_medical_imaging())
        elif choice == "3":
            asyncio.run(compare_single_vs_multi_model())
        elif choice == "4":
            custom_query = input("请输入您的研究查询: ").strip()
            if custom_query:
                enable_multi = input("是否启用多模型? (y/n): ").strip().lower() == 'y'
                asyncio.run(run_integrated_multi_model_research(
                    custom_query, 
                    enable_multi_model=enable_multi
                ))
            else:
                print("❌ 查询不能为空")
        elif choice == "5":
            print("✅ 系统状态检查完成")
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 执行过程中发生错误: {e}")
        logger.error(f"程序执行失败: {e}")


if __name__ == "__main__":
    main() 
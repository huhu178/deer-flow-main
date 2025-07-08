# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import asyncio
import logging
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage

from .graph import build_graph

logger = logging.getLogger(__name__)


async def run_agent_workflow_async(
    user_input: str,
    debug: bool = False,
    max_plan_iterations: int = 2,
    max_step_num: int = 3,
    enable_background_investigation: bool = True,
    enable_multi_model_report: bool = False,
    locale: str = "zh-CN"
) -> Dict[str, Any]:
    """
    异步运行Agent工作流
    
    Args:
        user_input: 用户输入
        debug: 是否开启调试模式
        max_plan_iterations: 最大计划迭代次数
        max_step_num: 最大步骤数
        enable_background_investigation: 是否启用背景调研
        enable_multi_model_report: 是否启用多模型报告生成
        locale: 语言区域
        
    Returns:
        Dict[str, Any]: 工作流执行结果
    """
    logger.info(f"开始异步工作流执行")
    logger.info(f"用户输入: {user_input}")
    logger.info(f"多模型模式: {enable_multi_model_report}")
    
    # 构建工作流图
    graph = build_graph()
    
    # 准备初始状态
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "locale": locale,
        "enable_multi_model_report": enable_multi_model_report,
        "enable_background_investigation": enable_background_investigation,
        "auto_accepted_plan": False,  # 🔧 改为False，让用户可以审查计划（但系统会自动接受）
        "plan_iterations": 0,
        "observations": [],
        "current_step_index": 0,  # 🔧 确保步骤索引从0开始
        "research_team_loop_counter": 0  # 🔧 确保循环计数器从0开始
    }
    
    # 配置 - 增加递归限制
    config = {
        "configurable": {
            "max_search_results": 10,
            "max_plan_iterations": max_plan_iterations,
            "max_step_num": max_step_num
        },
        "recursion_limit": 100  # 增加递归限制
    }
    
    try:
        # 运行工作流
        final_state = await graph.ainvoke(initial_state, config=config)
        
        logger.info("工作流执行完成")
        return final_state
        
    except Exception as e:
        logger.error(f"工作流执行失败: {e}")
        
        # 如果是递归限制错误，尝试简化模式重新运行
        if "recursion_limit" in str(e).lower() or "recursion limit" in str(e).lower():
            logger.warning("检测到递归限制错误，尝试简化模式重新运行...")
            
            # 简化状态和配置
            simplified_state = {
                "messages": [HumanMessage(content=user_input)],
                "locale": locale,
                "enable_multi_model_report": False,  # 关闭多模型模式
                "enable_background_investigation": True,  # 关闭背景调研
                "auto_accepted_plan": True,
                "plan_iterations": 0,
                "observations": [],
                "current_step_index": 0,  # 🔧 确保步骤索引从0开始
                "research_team_loop_counter": 0  # 🔧 确保循环计数器从0开始
            }
            
            simplified_config = {
                "configurable": {
                    "max_search_results": 5,
                    "max_plan_iterations": 1,
                    "max_step_num": 2
                },
                "recursion_limit": 50
            }
            
            try:
                logger.info("开始简化模式执行...")
                final_state = await graph.ainvoke(simplified_state, config=simplified_config)
                logger.info("简化模式执行成功")
                
                # 添加简化模式说明
                if "final_report" in final_state:
                    final_state["final_report"] = f"""# 简化模式执行结果

⚠️ **注意**: 由于系统复杂度限制，本次执行使用了简化模式，部分功能被禁用。

{final_state["final_report"]}

---

*如需完整功能，请尝试减少查询复杂度或分段执行*
"""
                
                return final_state
                
            except Exception as simplified_error:
                logger.error(f"简化模式也执行失败: {simplified_error}")
                raise simplified_error
        else:
            raise


def run_agent_workflow(
    user_input: str,
    debug: bool = False,
    max_plan_iterations: int = 2,
    max_step_num: int = 3,
    enable_background_investigation: bool = True,
    enable_multi_model_report: bool = False,
    locale: str = "zh-CN"
) -> Dict[str, Any]:
    """
    同步运行Agent工作流（兼容性接口）
    
    Args:
        user_input: 用户输入
        debug: 是否开启调试模式
        max_plan_iterations: 最大计划迭代次数
        max_step_num: 最大步骤数
        enable_background_investigation: 是否启用背景调研
        enable_multi_model_report: 是否启用多模型报告生成
        locale: 语言区域
        
    Returns:
        Dict[str, Any]: 工作流执行结果
    """
    return asyncio.run(run_agent_workflow_async(
        user_input=user_input,
        debug=debug,
        max_plan_iterations=max_plan_iterations,
        max_step_num=max_step_num,
        enable_background_investigation=enable_background_investigation,
        enable_multi_model_report=enable_multi_model_report,
        locale=locale
    ))


if __name__ == "__main__":
    print(build_graph().get_graph(xray=True).draw_mermaid())

# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
增强节点集成模块
===============

功能特性：
- 🔄 与现有节点系统无缝集成
- 🧠 保持原有API兼容性
- 📋 支持模式切换（标准/增强）
- 💡 自动检测复杂度并调整交互模式
- 🎯 零配置的多轮交互支持

使用方法：
```python
# 1. 简单集成 - 替换现有节点
from src.graph.enhanced_node_integration import EnhancedNodeWrapper

# 原有调用方式保持不变
coordinator_result = coordinator_node(state)  # 自动支持多轮交互

# 2. 显式启用增强模式
config = Configuration(interaction_mode="enhanced")
coordinator_result = coordinator_node(state, config)
```
"""

import json
import logging
from typing import Literal, Optional, Dict, Any, List
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from src.config.configuration import Configuration, InteractionPresets
from src.llms.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP
from .types import State
from .enhanced_planning_nodes import (
    EnhancedCoordinatorNode, 
    EnhancedPlannerNode,
    PlanningConfig
)

logger = logging.getLogger(__name__)


class EnhancedNodeWrapper:
    """增强节点包装器 - 智能选择标准模式或增强模式"""
    
    def __init__(self):
        self.enhanced_coordinator = None
        self.enhanced_planner = None
        # 🔧 新增：强制模式标志
        self.force_enhanced_mode = False
        self._init_enhanced_nodes()
    
    def _init_enhanced_nodes(self):
        """延迟初始化增强节点"""
        try:
            # 🔧 关键修复：使用在conf.yaml中定义的有效模型名称，例如'coordinator'或'planner'
            # 确保 AGENT_LLM_MAP["coordinator"] 返回的是一个在conf.yaml中定义的有效键
            self.enhanced_coordinator = EnhancedCoordinatorNode(
                llm_type=AGENT_LLM_MAP["coordinator"]
            )
            self.enhanced_planner = EnhancedPlannerNode(
                llm_type=AGENT_LLM_MAP["planner"]
            )
            logger.info("✅ 增强节点(coordinator, planner)初始化完成")
        except Exception as e:
            logger.warning(f"⚠️ 增强节点初始化失败: {e}")
            import traceback
            logger.error(f"Stack trace: {traceback.format_exc()}")
    
    def should_use_enhanced_mode(self, state: State, config: Optional[RunnableConfig] = None) -> bool:
        """智能判断是否使用增强模式 - 已彻底关闭"""
        
        # 🔧 彻底关闭增强模式
        logger.info("📋 增强模式已彻底关闭，使用标准流程")
        return False

    def __call__(self, state: State) -> Command:
        """智能协调器主入口"""
        logger.info("🧠 启动智能协调器节点")
        
        # 🔧 多轮交互已彻底关闭 - 直接使用标准流程
        logger.info("📋 多轮交互已关闭，使用标准处理流程")
        
        # 🔧 强制关闭多轮模式
        should_use_multi_round = False
        
        if should_use_multi_round:
            logger.info("🔄 检测到复杂查询，启用多轮交互模式")
            logger.info("🔄 使用增强交互模式")
            
            # 转到增强理解节点
            return Command(
                update={
                    **state,
                    "enable_multi_round": True,
                    "multi_round_config": {
                        "max_understanding_rounds": 2,
                        "max_planning_rounds": 1,
                        "quality_threshold": 0.8
                    }
                },
                goto="enhanced_coordinator"
            )
        else:
            logger.info("🔄 简单查询，使用标准处理流程")
            
            # 直接转到背景调查
            return Command(
                update={
                    **state,
                    "enable_multi_round": False
                },
                goto="background_investigation"
            )


# 🔄 智能节点包装器实例
_enhanced_wrapper = EnhancedNodeWrapper()

# 🚀 多轮交互模式已关闭 - 回到简单高效的单轮模式
FORCE_MULTI_ROUND_MODE = False  # 🔧 关闭多轮模式，使用标准流程

def set_multi_round_mode(enable: bool = True):
    """
    🎯 直接控制多轮交互模式
    
    Args:
        enable: True=强制启用多轮, False=恢复自动检测
    """
    global FORCE_MULTI_ROUND_MODE
    FORCE_MULTI_ROUND_MODE = enable
    mode_str = "强制多轮模式" if enable else "自动检测模式"
    logger.info(f"🔧 切换交互模式: {mode_str}")

def get_current_interaction_mode() -> str:
    """获取当前交互模式"""
    return "强制多轮模式" if FORCE_MULTI_ROUND_MODE else "自动检测模式"


def enhanced_coordinator_node(
    state: State,
    config: Optional[RunnableConfig] = None
) -> Command[Literal["planner", "background_investigator", "__end__"]]:
    """
    增强的协调器节点 - 智能选择标准模式或增强模式
    
    完全兼容原有coordinator_node的接口和行为
    """
    logger.info("🧠 启动智能协调器节点")
    
    # 智能选择模式
    if _enhanced_wrapper.should_use_enhanced_mode(state, config):
        logger.info("🔄 使用增强交互模式")
        
        # 确保增强节点可用
        if _enhanced_wrapper.enhanced_coordinator is None:
            logger.warning("⚠️ 增强节点不可用，回退到标准模式")
            return _fallback_to_standard_coordinator(state)
        
        # 使用增强协调器
        try:
            result = _enhanced_wrapper.enhanced_coordinator(state)
            
            # 适配返回值以兼容原有工作流
            if hasattr(result, 'goto') and result.goto == "planner":
                # 重定向到兼容的规划器节点
                return Command(
                    update=result.update if hasattr(result, 'update') else {},
                    goto="planner"
                )
            
            return result
        except Exception as e:
            logger.error(f"❌ 增强协调器执行失败: {e}")
            return _fallback_to_standard_coordinator(state)
    else:
        logger.info("📋 使用标准交互模式")
        return _fallback_to_standard_coordinator(state)


def enhanced_planner_node(
    state: State, 
    config: Optional[RunnableConfig] = None
) -> Command[Literal["human_feedback", "reporter"]]:
    """
    增强的规划器节点 - 智能选择标准模式或增强模式
    
    完全兼容原有planner_node的接口和行为
    """
    logger.info("📋 启动智能规划器节点")
    
    # 智能选择模式
    if _enhanced_wrapper.should_use_enhanced_mode(state, config):
        logger.info("🔄 使用增强规划模式")
        
        # 确保增强节点可用
        if _enhanced_wrapper.enhanced_planner is None:
            logger.warning("⚠️ 增强规划器不可用，回退到标准模式")
            return _fallback_to_standard_planner(state, config)
        
        # 使用增强规划器
        try:
            result = _enhanced_wrapper.enhanced_planner(state, config)
            
            # 适配返回值以兼容原有工作流
            if hasattr(result, 'goto') and result.goto == "planner":
                # 重定向到自身以继续多轮规划
                return Command(
                    update=result.update if hasattr(result, 'update') else {},
                    goto="planner"  # 继续当前节点
                )
            
            return result
        except Exception as e:
            logger.error(f"❌ 增强规划器执行失败: {e}")
            return _fallback_to_standard_planner(state, config)
    else:
        logger.info("📋 使用标准规划模式")
        return _fallback_to_standard_planner(state, config)


def _fallback_to_standard_coordinator(state: State) -> Command:
    """回退到标准协调器"""
    # 导入原有节点（避免循环导入）
    from .nodes import coordinator_node
    try:
        return coordinator_node(state)
    except Exception as e:
        logger.error(f"❌ 标准协调器也执行失败: {e}")
        return Command(goto="__end__")


def _fallback_to_standard_planner(state: State, config: Optional[RunnableConfig] = None) -> Command:
    """回退到标准规划器"""
    # 导入原有节点（避免循环导入）
    from .nodes import planner_node
    try:
        return planner_node(state, config)
    except Exception as e:
        logger.error(f"❌ 标准规划器也执行失败: {e}")
        return Command(goto="reporter")


def configure_enhanced_mode(
    interaction_mode: str = "enhanced",
    understanding_rounds: int = 5,
    planning_rounds: int = 3,
    quality_threshold: float = 0.8
) -> RunnableConfig:
    """
    配置增强交互模式
    
    Args:
        interaction_mode: 交互模式 ("standard", "enhanced", "auto")
        understanding_rounds: 理解轮次
        planning_rounds: 规划轮次
        quality_threshold: 质量阈值
    
    Returns:
        RunnableConfig: 可传递给节点的配置对象
    """
    from src.config.configuration import create_interaction_config
    
    config = create_interaction_config(
        mode=interaction_mode,
        understanding_rounds=understanding_rounds,
        planning_rounds=planning_rounds,
        quality_threshold=quality_threshold
    )
    
    return {
        "configurable": {
            "interaction_mode": config.interaction_mode,
            "max_understanding_rounds": config.max_understanding_rounds,
            "max_planning_rounds": config.max_planning_rounds,
            "understanding_quality_threshold": config.understanding_quality_threshold,
            "planning_quality_threshold": config.planning_quality_threshold,
            "enable_deep_thinking": config.enable_deep_thinking,
            "thinking_time_seconds": config.thinking_time_seconds
        }
    }


def get_interaction_stats(state: State) -> Dict[str, Any]:
    """
    获取交互统计信息
    
    Args:
        state: 当前状态
    
    Returns:
        dict: 交互统计信息
    """
    return {
        "understanding_rounds": state.get("understanding_rounds", 0),
        "planning_rounds": state.get("planning_rounds", 0),
        "understanding_completed": state.get("understanding_completed", False),
        "planning_completed": state.get("planning_completed", False),
        "interaction_mode": "enhanced" if state.get("understanding_rounds", 0) > 1 else "standard",
        "total_interactions": (
            state.get("understanding_rounds", 0) + 
            state.get("planning_rounds", 0)
        )
    }


# 🛠️ 便捷的工作流更新函数
def patch_workflow_with_enhanced_nodes(workflow):
    """
    给现有工作流打补丁，添加增强交互功能
    
    Args:
        workflow: LangGraph工作流对象
    """
    logger.info("🔧 为工作流添加增强交互功能")
    
    try:
        # 替换现有节点（如果存在）
        if hasattr(workflow, '_nodes') and 'coordinator' in workflow._nodes:
            workflow._nodes['coordinator'] = enhanced_coordinator_node
            logger.info("✅ 已替换coordinator节点")
        
        if hasattr(workflow, '_nodes') and 'planner' in workflow._nodes:
            workflow._nodes['planner'] = enhanced_planner_node
            logger.info("✅ 已替换planner节点")
        
        logger.info("🎯 增强交互功能已成功集成")
    except Exception as e:
        logger.error(f"❌ 工作流补丁失败: {e}")


# 📝 使用示例
def demo_enhanced_interaction():
    """演示增强交互功能的使用"""
    print("🧪 增强交互功能演示")
    
    # 1. 简单用法 - 自动检测
    test_states = [
        {
            "messages": [HumanMessage(content="你好")],
            "expected_mode": "standard"
        },
        {
            "messages": [HumanMessage(content="我想开发一个基于AI和影像组学的医学诊断系统，需要分析多种医学影像数据，预测疾病风险，并提供个性化治疗建议")],
            "expected_mode": "enhanced"
        }
    ]
    
    for i, test_case in enumerate(test_states, 1):
        print(f"\n测试案例 {i}:")
        print(f"输入: {test_case['messages'][0].content[:50]}...")
        
        should_enhance = _enhanced_wrapper._detect_complexity(test_case)
        actual_mode = "enhanced" if should_enhance else "standard"
        
        print(f"预期模式: {test_case['expected_mode']}")
        print(f"实际模式: {actual_mode}")
        print(f"结果: {'✅ 正确' if actual_mode == test_case['expected_mode'] else '❌ 错误'}")
    
    # 2. 显式配置用法
    print("\n🔧 显式配置演示:")
    config = configure_enhanced_mode(
        interaction_mode="enhanced",
        understanding_rounds=3,
        planning_rounds=2,
        quality_threshold=0.7
    )
    print(f"配置: {config}")
    
    print("✅ 演示完成")


if __name__ == "__main__":
    demo_enhanced_interaction() 
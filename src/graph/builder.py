# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .types import State

# 🔧 强制使用标准节点 - 多轮交互已彻底关闭
from .nodes import (
    coordinator_node,
    planner_node,
)
logger = logging.getLogger(__name__)
logger.info("📋 使用标准节点 - 多轮交互已关闭")
ENHANCED_NODES_AVAILABLE = False

# 导入其他标准节点
from .nodes import (
    reporter_node,
    research_team_node,
    researcher_node,
    coder_node,
    human_feedback_node,
    background_investigation_node,
)

# 🔍 导入文献预研究节点
from .literature_preresearch_node import literature_preresearch_node

logger = logging.getLogger(__name__)


def _build_base_graph():
    """Build and return the base state graph with all nodes and edges."""
    try:
        builder = StateGraph(State)
        
        # 🔧 添加节点时进行错误检查
        if ENHANCED_NODES_AVAILABLE:
            logger.info("🚀 构建增强LangGraph - 支持多轮交互...")
        else:
            logger.info("📋 构建标准LangGraph - 单轮交互...")
        
        # 🔍 新的工作流程：START → coordinator → literature_preresearch → planner
        builder.add_edge(START, "coordinator")
        builder.add_node("coordinator", coordinator_node)
        builder.add_node("literature_preresearch", literature_preresearch_node)  # 新增文献预研究节点
        builder.add_node("background_investigator", background_investigation_node)
        builder.add_node("planner", planner_node)
        builder.add_node("reporter", reporter_node)
        builder.add_node("research_team", research_team_node)
        builder.add_node("researcher", researcher_node)
        builder.add_node("coder", coder_node)
        builder.add_node("human_feedback", human_feedback_node)
        builder.add_edge("reporter", END)
        
        mode_info = "文献驱动研究模式" if ENHANCED_NODES_AVAILABLE else "标准文献预研究模式"
        logger.info(f"✅ LangGraph构建成功 - {mode_info}")
        return builder
        
    except Exception as e:
        logger.error(f"❌ LangGraph构建失败: {str(e)}")
        raise


def build_graph_with_memory():
    """Build and return the agent workflow graph with memory."""
    try:
        # use persistent memory to save conversation history
        # TODO: be compatible with SQLite / PostgreSQL
        memory = MemorySaver()

        # build state graph
        builder = _build_base_graph()
        graph = builder.compile(checkpointer=memory)
        
        mode_info = "文献预研究 + 内存模式" if ENHANCED_NODES_AVAILABLE else "标准文献预研究 + 内存模式"
        logger.info(f"✅ {mode_info}编译成功")
        return graph
        
    except Exception as e:
        logger.error(f"❌ 带内存的LangGraph编译失败: {str(e)}")
        # 降级到无内存版本
        logger.info("🔄 降级到无内存版本...")
        return build_graph()


def build_graph():
    """Build and return the agent workflow graph without memory."""
    try:
        # build state graph
        builder = _build_base_graph()
        graph = builder.compile()
        
        mode_info = "文献驱动研究模式" if ENHANCED_NODES_AVAILABLE else "标准文献预研究模式"
        logger.info(f"✅ {mode_info}编译成功")
        return graph
        
    except Exception as e:
        logger.error(f"❌ LangGraph编译失败: {str(e)}")
        raise


def get_workflow_info():
    """获取当前工作流模式信息"""
    return {
        "enhanced_nodes_available": ENHANCED_NODES_AVAILABLE,
        "mode": "文献驱动研究模式" if ENHANCED_NODES_AVAILABLE else "标准文献预研究模式",
        "features": {
            "literature_preresearch": True,  # 新增功能
            "comprehensive_literature_search": True,  # 100篇文献搜索
            "quality_literature_analysis": True,  # 高质量文献分析
            "mechanism_understanding": True,  # 深度机制理解
            "multi_round_understanding": ENHANCED_NODES_AVAILABLE,
            "progressive_planning": ENHANCED_NODES_AVAILABLE,
            "complexity_detection": ENHANCED_NODES_AVAILABLE,
            "quality_assessment": ENHANCED_NODES_AVAILABLE
        }
    }


# 🔧 使用安全的graph构建方式
try:
    graph = build_graph()
    workflow_info = get_workflow_info()
    logger.info(f"🎯 默认LangGraph实例创建成功 - {workflow_info['mode']}")
except Exception as e:
    logger.error(f"❌ 默认LangGraph创建失败: {str(e)}")
    graph = None

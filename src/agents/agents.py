# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from langgraph.prebuilt import create_react_agent

from src.prompts import apply_prompt_template
from src.llms.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP

logger = logging.getLogger(__name__)

def _check_model_supports_tools(model):
    """检查模型是否支持工具调用"""
    try:
        # 检查模型配置
        model_name = getattr(model, 'model_name', '')
        base_url = getattr(model, 'base_url', '')
        
        # OpenRouter MiniMax不支持工具调用
        if 'openrouter.ai' in str(base_url) and 'minimax' in str(model_name).lower():
            logger.info(f"🔧 检测到OpenRouter MiniMax模型({model_name})，不支持工具调用")
            return False
            
        # 其他检查可以在这里添加
        return True
    except Exception as e:
        logger.warning(f"⚠️ 模型工具支持检查失败: {e}，默认支持工具调用")
        return True

def _create_simple_agent(agent_name: str, model, prompt_template: str, recursion_limit: int = 100):
    """创建不使用工具的简化agent"""
    from langgraph.graph import StateGraph, END
    from langchain_core.messages import HumanMessage, AIMessage
    from typing import TypedDict, Annotated
    from langgraph.graph.message import add_messages
    from langgraph.types import Command
    
    # 定义状态
    class SimpleAgentState(TypedDict):
        messages: Annotated[list, add_messages]
    
    async def simple_agent_node(state: SimpleAgentState):
        """简化的agent节点，不使用工具调用"""
        try:
            # 应用提示模板
            template_result = apply_prompt_template(prompt_template, state)
            
            # 提取系统提示内容
            if isinstance(template_result, list) and len(template_result) > 0:
                # 从apply_prompt_template返回的list中提取system message
                system_msg = template_result[0]
                if isinstance(system_msg, dict) and system_msg.get("role") == "system":
                    prompt_content = system_msg.get("content", "")
                else:
                    prompt_content = str(system_msg)
            else:
                prompt_content = str(template_result)
            
            # 准备消息
            messages = state.get("messages", [])
            if prompt_content:
                # 将提示添加为系统消息
                full_messages = [HumanMessage(content=prompt_content)] + messages
            else:
                full_messages = messages
            
            # 调用模型（无工具）
            response = await model.ainvoke(full_messages)
            
            return {"messages": [response]}
            
        except Exception as e:
            logger.error(f"❌ 简化agent调用失败: {e}")
            # 返回错误消息
            error_msg = AIMessage(content=f"抱歉，处理您的请求时遇到了技术问题：{str(e)}")
            return {"messages": [error_msg]}
    
    # 创建图
    graph = StateGraph(SimpleAgentState)
    graph.add_node("agent", simple_agent_node)
    graph.set_entry_point("agent")
    graph.add_edge("agent", END)
    
    # 编译图
    compiled_graph = graph.compile()
    compiled_graph.recursion_limit = recursion_limit
    
    logger.info(f"✅ 创建了简化agent: {agent_name} (无工具调用)")
    return compiled_graph

# Create agents using configured LLM types
def create_agent(agent_name: str, agent_type: str, tools: list, prompt_template: str, recursion_limit: int = 100):
    """Factory function to create agents with consistent configuration."""
    
    # 获取模型
    model = get_llm_by_type(AGENT_LLM_MAP[agent_type])
    
    # 检查模型是否支持工具调用
    supports_tools = _check_model_supports_tools(model)
    
    if not supports_tools or not tools:
        # 如果模型不支持工具调用或没有工具，创建简化版agent
        logger.info(f"🔧 为{agent_name}创建简化agent (原因: 模型不支持工具={not supports_tools}, 无工具={not tools})")
        return _create_simple_agent(agent_name, model, prompt_template, recursion_limit)
    
    # 如果支持工具调用，创建标准的ReAct agent
    try:
        def prompt_converter(state):
            """转换prompt格式，确保兼容ReAct agent"""
            try:
                template_result = apply_prompt_template(prompt_template, state)
                # 🔧 修复：如果返回的是list，直接返回，ReAct agent期望list格式
                if isinstance(template_result, list):
                    return template_result
                else:
                    # 如果不是list，转换为预期格式
                    return [{"role": "system", "content": str(template_result)}] + state.get("messages", [])
            except Exception as e:
                logger.error(f"❌ Prompt转换失败 ({agent_name}): {e}")
                logger.error(f"❌ 详细错误信息: {type(e).__name__}: {str(e)}")
                # 返回基础消息以确保agent不会完全失败
                return state.get("messages", [])
        
        agent = create_react_agent(
            name=agent_name,
            model=model,
            tools=tools,
            prompt=prompt_converter,
        )
        
        # 单独设置递归限制
        agent.recursion_limit = recursion_limit
        logger.info(f"✅ 创建了标准ReAct agent: {agent_name} (支持{len(tools)}个工具)")
        return agent
        
    except Exception as e:
        logger.error(f"❌ 标准agent创建失败 ({agent_name}): {e}")
        logger.error(f"❌ 详细错误类型: {type(e).__name__}")
        logger.error(f"❌ 错误详情: {str(e)}")
        import traceback
        logger.error(f"❌ 堆栈跟踪: {traceback.format_exc()}")
        return _create_simple_agent(agent_name, model, prompt_template, recursion_limit)

# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.llms.llm import get_llm_by_type
from src.graph.builder import build_graph_with_memory
from src.server.chat_request import ChatMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/gemini-research", tags=["Gemini Deep Research"])

class DeepResearchRequest(BaseModel):
    """深度研究请求模型"""
    question: str  # 用户问题
    research_depth: str = "comprehensive"  # 研究深度: basic, detailed, comprehensive
    max_iterations: int = 3  # 最大研究迭代次数
    enable_real_time_search: bool = True  # 是否启用实时搜索
    output_format: str = "markdown"  # 输出格式: markdown, html, json

class DeepResearchResponse(BaseModel):
    """深度研究响应模型"""
    success: bool
    research_id: str
    question: str
    research_result: str
    metadata: Dict[str, Any]
    timestamp: str

# 全局变量存储研究状态
research_sessions = {}

@router.post("/start")
async def start_deep_research(request: DeepResearchRequest):
    """启动深度研究任务"""
    try:
        research_id = f"research_{int(time.time() * 1000)}"
        
        research_sessions[research_id] = {
            "status": "started",
            "question": request.question,
            "start_time": datetime.now(),
            "progress": 0,
            "current_stage": "初始化",
            "result": ""
        }
        
        # 异步执行深度研究
        asyncio.create_task(execute_deep_research(research_id, request))
        
        return {
            "success": True,
            "research_id": research_id,
            "question": request.question,
            "message": "研究已开始",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"启动深度研究失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{research_id}")
async def get_research_status(research_id: str):
    """获取研究状态"""
    if research_id not in research_sessions:
        raise HTTPException(status_code=404, detail="研究会话不存在")
    
    session = research_sessions[research_id]
    return {
        "research_id": research_id,
        "status": session["status"],
        "progress": session["progress"],
        "current_stage": session["current_stage"],
        "has_result": len(session["result"]) > 0
    }

@router.get("/result/{research_id}")
async def get_research_result(research_id: str):
    """获取研究结果"""
    if research_id not in research_sessions:
        raise HTTPException(status_code=404, detail="研究会话不存在")
    
    session = research_sessions[research_id]
    
    if session["status"] == "completed":
        return {
            "success": True,
            "research_id": research_id,
            "question": session["question"],
            "result": session["result"],
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "success": False,
            "message": f"研究尚未完成，当前状态: {session['status']}",
            "current_stage": session["current_stage"],
            "progress": session["progress"]
        }

@router.get("/stream/{research_id}")
async def stream_research_progress(research_id: str):
    """
    流式返回研究进度
    """
    if research_id not in research_sessions:
        raise HTTPException(status_code=404, detail="研究会话不存在")
    
    async def generate_progress_stream():
        while research_id in research_sessions:
            session = research_sessions[research_id]
            
            # 发送当前状态
            status_data = {
                "type": "status",
                "research_id": research_id,
                "status": session["status"],
                "progress": session["progress"],
                "current_stage": session["current_stage"]
            }
            
            yield f"data: {json.dumps(status_data, ensure_ascii=False)}\n\n"
            
            # 如果完成了，发送结果
            if session["status"] == "completed":
                result_data = {
                    "type": "result",
                    "research_id": research_id,
                    "result": session["result"]
                }
                yield f"data: {json.dumps(result_data, ensure_ascii=False)}\n\n"
                break
            
            # 如果失败了，发送错误信息
            if session["status"] == "failed":
                error_data = {
                    "type": "error",
                    "research_id": research_id,
                    "error": session.get("error", "未知错误")
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                break
            
            await asyncio.sleep(2)  # 每2秒更新一次
    
    return StreamingResponse(
        generate_progress_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

async def execute_deep_research(research_id: str, request: DeepResearchRequest):
    """执行深度研究的核心逻辑"""
    try:
        session = research_sessions[research_id]
        
        # 第一阶段：初始化
        session["current_stage"] = "初始化Gemini 2.5 Pro"
        session["progress"] = 10
        
        # 构建深度研究提示
        deep_research_prompt = f"""
你是一个专业的深度研究助手。请对以下问题进行深度研究：

{request.question}

请按照以下结构进行详细研究：
1. 问题分析与分解
2. 背景调研
3. 多角度探索
4. 关键发现
5. 深度分析
6. 结论与建议
7. 参考资料

请提供详细、准确、有价值的研究结果。
"""
        
        # 第二阶段：执行研究
        session["current_stage"] = "Gemini 2.5 Pro 深度分析中"
        session["progress"] = 30
        
        # 构建图并执行
        graph = build_graph_with_memory()
        thread_id = f"deep_research_{research_id}"
        
        result_content = ""
        
        session["progress"] = 50
        session["current_stage"] = "生成深度研究报告"
        
        # 执行图工作流
        async for event in graph.astream(
            {
                "messages": [{"role": "user", "content": deep_research_prompt}],
                "thread_id": thread_id,
                "max_plan_iterations": request.max_iterations,
                "max_step_num": 10,
                "max_search_results": 20,
                "auto_accepted_plan": True,
                "interrupt_feedback": "",
                "mcp_settings": {},
                "enable_background_investigation": request.enable_real_time_search,
                "enable_multi_model_report": False
            },
            {"configurable": {"thread_id": thread_id}}
        ):
            if "messages" in event and event["messages"]:
                last_message = event["messages"][-1]
                if hasattr(last_message, 'content') and last_message.content:
                    result_content = last_message.content
                    session["progress"] = min(90, session["progress"] + 5)
        
        # 第三阶段：格式化结果
        session["current_stage"] = "格式化结果"
        session["progress"] = 95
        
        if not result_content:
            result_content = "深度研究完成，但未获取到具体结果。"
        
        # 添加元数据
        metadata_header = f"""# 深度研究报告

**研究问题**: {request.question}
**研究ID**: {research_id}
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**使用模型**: Gemini 2.5 Pro

---

"""
        
        final_result = metadata_header + result_content
        
        # 完成
        session["current_stage"] = "研究完成"
        session["progress"] = 100
        session["status"] = "completed"
        session["result"] = final_result
        session["completion_time"] = datetime.now()
        
        logger.info(f"深度研究任务完成: {research_id}")
        
    except Exception as e:
        logger.error(f"深度研究执行失败: {str(e)}")
        session = research_sessions.get(research_id, {})
        session["status"] = "failed"
        session["error"] = str(e)
        session["current_stage"] = f"执行失败: {str(e)}"

@router.delete("/session/{research_id}")
async def delete_research_session(research_id: str):
    """
    删除研究会话
    """
    if research_id in research_sessions:
        del research_sessions[research_id]
        return {"success": True, "message": f"研究会话 {research_id} 已删除"}
    else:
        raise HTTPException(status_code=404, detail="研究会话不存在")

@router.get("/sessions")
async def list_research_sessions():
    """
    列出所有研究会话
    """
    sessions_info = []
    for research_id, session in research_sessions.items():
        sessions_info.append({
            "research_id": research_id,
            "question": session["question"],
            "status": session["status"],
            "start_time": session["start_time"].isoformat(),
            "progress": session["progress"],
            "current_stage": session["current_stage"]
        })
    
    return {
        "total_sessions": len(sessions_info),
        "sessions": sessions_info
    } 
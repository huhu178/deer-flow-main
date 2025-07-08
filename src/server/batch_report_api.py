#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分批报告生成API
支持流式输出，解决16k token限制问题
"""

import sys
import os
import json
import asyncio
from typing import AsyncGenerator, Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ⚠️ 注意：此API已被新的分批生成系统替代
# 新的分批生成系统集成在 src/graph/nodes.py 中的 SimpleBatchGenerator 类
# 原有的 generate_dxa_batch_report 模块已被删除
try:
    # from generate_dxa_batch_report import DXABatchReportGenerator  # 已删除
    print("⚠️ 旧的DXABatchReportGenerator已被SimpleBatchGenerator替代")
    print("📍 新的分批生成系统位于: src/graph/nodes.py")
    DXABatchReportGenerator = None  # 设置为None以避免未定义错误
except ImportError as e:
    print(f"❌ 导入 DXABatchReportGenerator 失败: {e}")
    print("💡 建议：使用新的SimpleBatchGenerator分批生成系统")
    DXABatchReportGenerator = None

router = APIRouter(prefix="/api/batch-report", tags=["batch-report"])


class BatchReportRequest(BaseModel):
    """分批报告生成请求"""
    report_name: str = None
    mode: str = "all"  # "all", "demo", "single"
    direction_index: int = None  # 用于single模式


class BatchReportResponse(BaseModel):
    """分批报告生成响应"""
    success: bool
    message: str = None
    data: Dict[str, Any] = None


@router.post("/start", response_model=BatchReportResponse)
async def start_batch_report(request: BatchReportRequest):
    """
    启动分批报告生成
    """
    if DXABatchReportGenerator is None:
        return BatchReportResponse(
            success=False,
            message="旧的分批生成系统已被替代，请使用新的工作流程系统",
            data={
                "info": "新的分批生成系统已集成在主工作流程中",
                "location": "src/graph/nodes.py - SimpleBatchGenerator类",
                "usage": "通过主聊天界面自动触发分批生成"
            }
        )
    
    try:
        generator = DXABatchReportGenerator(request.report_name)
        
        return BatchReportResponse(
            success=True,
            message="分批报告生成器已启动",
            data={
                "report_name": generator.report_name,
                "total_directions": generator.total_directions,
                "mode": request.mode
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动失败: {str(e)}")


@router.get("/stream/{report_name}")
async def stream_batch_report(report_name: str, mode: str = "all"):
    """
    流式生成分批报告
    支持Server-Sent Events (SSE)
    """
    
    if DXABatchReportGenerator is None:
        async def error_stream():
            error_data = {
                "type": "error",
                "error": "旧的分批生成系统已被替代，请使用新的工作流程系统"
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        
        return StreamingResponse(
            error_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
    
    async def generate_report_stream():
        """异步生成器，逐个生成研究方向"""
        try:
            generator = DXABatchReportGenerator(report_name)
            
            # 发送开始事件
            yield f"data: {json.dumps({'type': 'start', 'total': generator.total_directions}, ensure_ascii=False)}\n\n"
            
            # 根据模式决定生成数量
            if mode == "demo":
                total_to_generate = 5
            elif mode == "all":
                total_to_generate = generator.total_directions
            else:
                total_to_generate = 1
            
            # 逐个生成研究方向
            for i in range(total_to_generate):
                result = generator.generate_single_direction(i)
                
                if result["success"]:
                    # 发送成功事件
                    event_data = {
                        "type": "section_complete",
                        "direction_number": result["direction_number"],
                        "title": result["title"],
                        "content": result["content"],
                        "word_count": result["word_count"],
                        "progress": result["progress"],
                        "percentage": result["percentage"]
                    }
                    yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
                else:
                    # 发送错误事件
                    error_data = {
                        "type": "error",
                        "error": result["error"]
                    }
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                    break
                
                # 模拟延迟
                await asyncio.sleep(0.1)
            
            # 合并最终报告
            merge_result = generator.merge_final_report()
            if merge_result["success"]:
                final_data = {
                    "type": "complete",
                    "final_path": merge_result["final_path"],
                    "stats": merge_result["stats"]
                }
                yield f"data: {json.dumps(final_data, ensure_ascii=False)}\n\n"
            else:
                error_data = {
                    "type": "error",
                    "error": merge_result["error"]
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
                
        except Exception as e:
            error_data = {
                "type": "error",
                "error": f"生成过程中出错: {str(e)}"
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_report_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@router.post("/single", response_model=BatchReportResponse)
async def generate_single_direction(request: BatchReportRequest):
    """
    生成单个研究方向
    """
    try:
        if request.direction_index is None:
            raise HTTPException(status_code=400, detail="direction_index 参数必须提供")
        
        generator = DXABatchReportGenerator(request.report_name)
        result = generator.generate_single_direction(request.direction_index)
        
        if result["success"]:
            return BatchReportResponse(
                success=True,
                message="单个研究方向生成成功",
                data=result
            )
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.get("/progress/{report_name}")
async def get_progress(report_name: str):
    """
    获取报告生成进度
    """
    try:
        generator = DXABatchReportGenerator(report_name)
        progress_info = generator.get_progress_info()
        
        return BatchReportResponse(
            success=True,
            message="进度信息获取成功",
            data=progress_info
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进度失败: {str(e)}")


@router.post("/merge/{report_name}")
async def merge_report(report_name: str):
    """
    合并报告章节
    """
    try:
        generator = DXABatchReportGenerator(report_name)
        merge_result = generator.merge_final_report()
        
        if merge_result["success"]:
            return BatchReportResponse(
                success=True,
                message="报告合并成功",
                data=merge_result
            )
        else:
            raise HTTPException(status_code=500, detail=merge_result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"合并失败: {str(e)}")


# 添加到主应用
def include_batch_report_routes(app):
    """将分批报告路由添加到主应用"""
    app.include_router(router) 
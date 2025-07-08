#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分批输出管理器 API 接口
提供完整的分批生成服务
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from src.utils.batch_output_manager import SystemBatchOutputManager, create_batch_manager
    from src.utils.batch_output_manager import BatchItem, BatchResult, GenerationProgress
except ImportError as e:
    print(f"导入分批输出管理器失败: {e}")
    raise

# 创建路由器
router = APIRouter(prefix="/api/batch", tags=["batch"])

# 全局管理器存储
batch_managers: Dict[str, SystemBatchOutputManager] = {}


class CreateBatchTaskRequest(BaseModel):
    """创建分批任务请求"""
    task_name: str = Field(..., description="任务名称")
    report_name: str = Field(..., description="报告名称")
    batch_size: int = Field(default=5, description="每批处理数量")
    max_tokens_per_item: int = Field(default=4000, description="每项最大token数")
    base_dir: Optional[str] = Field(default=None, description="输出目录")


class AddBatchItemRequest(BaseModel):
    """添加批次项目请求"""
    task_name: str = Field(..., description="任务名称")
    item_id: str = Field(..., description="项目ID")
    item_type: str = Field(..., description="项目类型")
    title: str = Field(..., description="项目标题")
    content_template: str = Field(..., description="内容模板")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")
    estimated_tokens: int = Field(default=0, description="预估token数")


class AddBatchItemsRequest(BaseModel):
    """批量添加项目请求"""
    task_name: str = Field(..., description="任务名称")
    items: List[Dict[str, Any]] = Field(..., description="项目列表")


class GenerateBatchRequest(BaseModel):
    """生成批次请求"""
    task_name: str = Field(..., description="任务名称")
    use_stream: bool = Field(default=False, description="是否使用流式输出")


class BatchTaskResponse(BaseModel):
    """批次任务响应"""
    success: bool
    task_name: str
    message: str
    data: Optional[Dict[str, Any]] = None


class BatchProgressResponse(BaseModel):
    """批次进度响应"""
    success: bool
    task_name: str
    progress: Dict[str, Any]


class BatchResultResponse(BaseModel):
    """批次结果响应"""
    success: bool
    task_name: str
    results: List[Dict[str, Any]]


def get_manager(task_name: str) -> SystemBatchOutputManager:
    """获取管理器实例"""
    if task_name not in batch_managers:
        raise HTTPException(status_code=404, detail=f"任务 {task_name} 不存在")
    return batch_managers[task_name]


def create_content_generator():
    """创建内容生成器"""
    def content_generator(item: BatchItem) -> str:
        """
        自定义内容生成器
        这里可以集成您的AI模型或其他内容生成逻辑
        """
        # 基础内容模板
        content = f"""# {item.title}

## 项目概述

**项目类型**: {item.type}
**项目ID**: {item.id}
**章节编号**: {item.section_number}
**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 详细内容

{item.content_template}

## 项目元数据

"""
        
        # 添加元数据
        if item.metadata:
            for key, value in item.metadata.items():
                content += f"- **{key}**: {value}\n"
        
        # 根据项目类型生成不同的内容
        if item.type == "survey_aspect":
            content += """

## 调研分析

### 1. 现状分析
当前在该领域的研究现状和发展水平...

### 2. 关键问题
需要解决的核心问题和挑战...

### 3. 发展趋势
未来发展方向和技术趋势...

### 4. 建议措施
具体的实施建议和行动方案...

"""
        elif item.type == "dxa_direction":
            content += """

## 研究方案

### 1. 研究背景
详细的研究背景和科学意义...

### 2. 研究目标
明确的研究目标和预期成果...

### 3. 技术路线
具体的技术实施路线和方法...

### 4. 创新点
本研究的主要创新点和突破...

### 5. 预期影响
研究成果的预期影响和应用价值...

"""
        else:
            content += """

## 内容详情

根据项目类型和需求，生成相应的详细内容...

"""
        
        content += f"""

## 总结

本项目通过系统性的分析和研究，为{item.title}提供了全面的解决方案和实施建议。

---

*本内容由分批输出管理器自动生成，生成时间: {datetime.now().isoformat()}*
"""
        
        return content
    
    return content_generator


@router.post("/create-task", response_model=BatchTaskResponse)
async def create_batch_task(request: CreateBatchTaskRequest):
    """创建分批任务"""
    try:
        if request.task_name in batch_managers:
            return BatchTaskResponse(
                success=False,
                task_name=request.task_name,
                message=f"任务 {request.task_name} 已存在"
            )
        
        # 创建管理器
        manager = create_batch_manager(
            report_name=request.report_name,
            batch_size=request.batch_size,
            max_tokens_per_item=request.max_tokens_per_item,
            base_dir=request.base_dir or "./outputs/batch_reports",
            content_generator=create_content_generator()
        )
        
        batch_managers[request.task_name] = manager
        
        return BatchTaskResponse(
            success=True,
            task_name=request.task_name,
            message="任务创建成功",
            data={
                "report_name": request.report_name,
                "batch_size": request.batch_size,
                "max_tokens_per_item": request.max_tokens_per_item,
                "created_at": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.post("/add-item", response_model=BatchTaskResponse)
async def add_batch_item(request: AddBatchItemRequest):
    """添加单个项目"""
    try:
        manager = get_manager(request.task_name)
        
        success = manager.add_item(
            item_id=request.item_id,
            item_type=request.item_type,
            title=request.title,
            content_template=request.content_template,
            metadata=request.metadata,
            estimated_tokens=request.estimated_tokens
        )
        
        if success:
            return BatchTaskResponse(
                success=True,
                task_name=request.task_name,
                message="项目添加成功",
                data={
                    "item_id": request.item_id,
                    "total_items": len(manager.items)
                }
            )
        else:
            return BatchTaskResponse(
                success=False,
                task_name=request.task_name,
                message="项目添加失败"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加项目失败: {str(e)}")


@router.post("/add-items", response_model=BatchTaskResponse)
async def add_batch_items(request: AddBatchItemsRequest):
    """批量添加项目"""
    try:
        manager = get_manager(request.task_name)
        
        success_count = manager.add_items_batch(request.items)
        
        return BatchTaskResponse(
            success=True,
            task_name=request.task_name,
            message=f"成功添加 {success_count}/{len(request.items)} 个项目",
            data={
                "success_count": success_count,
                "total_count": len(request.items),
                "total_items": len(manager.items)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量添加项目失败: {str(e)}")


@router.get("/progress/{task_name}", response_model=BatchProgressResponse)
async def get_batch_progress(task_name: str):
    """获取任务进度"""
    try:
        manager = get_manager(task_name)
        progress = manager.get_progress()
        
        return BatchProgressResponse(
            success=True,
            task_name=task_name,
            progress=progress
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进度失败: {str(e)}")


@router.get("/items/{task_name}")
async def get_batch_items(task_name: str):
    """获取任务项目列表"""
    try:
        manager = get_manager(task_name)
        items = manager.get_items()
        
        return {
            "success": True,
            "task_name": task_name,
            "items": items,
            "total_count": len(items)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目列表失败: {str(e)}")


@router.get("/results/{task_name}", response_model=BatchResultResponse)
async def get_batch_results(task_name: str):
    """获取任务结果"""
    try:
        manager = get_manager(task_name)
        results = manager.get_results()
        
        return BatchResultResponse(
            success=True,
            task_name=task_name,
            results=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取结果失败: {str(e)}")


@router.get("/status/{task_name}")
async def get_batch_status(task_name: str):
    """获取批次状态"""
    try:
        manager = get_manager(task_name)
        batch_status = manager.get_batch_status()
        
        return {
            "success": True,
            "task_name": task_name,
            "batch_status": batch_status,
            "generation_status": manager.generation_status.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.post("/generate/{task_name}")
async def generate_batch_content(task_name: str, background_tasks: BackgroundTasks):
    """开始生成内容（异步）"""
    try:
        manager = get_manager(task_name)
        
        # 在后台任务中执行生成
        background_tasks.add_task(manager.generate_all_sync)
        
        return {
            "success": True,
            "task_name": task_name,
            "message": "生成任务已启动",
            "status": "started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启动生成失败: {str(e)}")


@router.get("/generate-stream/{task_name}")
async def generate_batch_content_stream(task_name: str):
    """流式生成内容"""
    try:
        manager = get_manager(task_name)
        
        async def event_stream():
            """事件流生成器"""
            try:
                async for result in manager.generate_stream_async():
                    # 格式化为 Server-Sent Events
                    event_data = json.dumps(result, ensure_ascii=False)
                    yield f"data: {event_data}\n\n"
                
                # 发送结束事件
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
            except Exception as e:
                error_data = {
                    "type": "error",
                    "data": {"error": str(e)}
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"流式生成失败: {str(e)}")


@router.post("/cancel/{task_name}")
async def cancel_batch_generation(task_name: str):
    """取消生成"""
    try:
        manager = get_manager(task_name)
        manager.cancel_generation()
        
        return {
            "success": True,
            "task_name": task_name,
            "message": "生成已取消"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取消生成失败: {str(e)}")


@router.delete("/clear/{task_name}")
async def clear_batch_items(task_name: str):
    """清空任务项目"""
    try:
        manager = get_manager(task_name)
        manager.clear_items()
        
        return {
            "success": True,
            "task_name": task_name,
            "message": "项目已清空"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空项目失败: {str(e)}")


@router.delete("/delete/{task_name}")
async def delete_batch_task(task_name: str):
    """删除任务"""
    try:
        if task_name in batch_managers:
            del batch_managers[task_name]
        
        return {
            "success": True,
            "task_name": task_name,
            "message": "任务已删除"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


@router.get("/download/{task_name}")
async def download_batch_report(task_name: str):
    """下载生成的报告"""
    try:
        manager = get_manager(task_name)
        
        # 检查是否有完成的报告
        if manager.generation_status.value not in ["completed"]:
            raise HTTPException(status_code=400, detail="报告尚未生成完成")
        
        # 查找报告文件
        report_dir = manager.manager.report_dir
        report_file = report_dir / f"{manager.report_name}.txt"
        
        if not report_file.exists():
            raise HTTPException(status_code=404, detail="报告文件不存在")
        
        return FileResponse(
            path=str(report_file),
            filename=f"{manager.report_name}.txt",
            media_type="text/plain"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载报告失败: {str(e)}")


@router.get("/list")
async def list_batch_tasks():
    """列出所有任务"""
    try:
        tasks = []
        for task_name, manager in batch_managers.items():
            progress = manager.get_progress()
            tasks.append({
                "task_name": task_name,
                "report_name": manager.report_name,
                "total_items": len(manager.items),
                "completed_items": progress["completed_items"],
                "status": progress["status"],
                "progress_percentage": progress["progress_percentage"]
            })
        
        return {
            "success": True,
            "tasks": tasks,
            "total_count": len(tasks)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"列出任务失败: {str(e)}")


# 预定义的项目模板
@router.get("/templates")
async def get_item_templates():
    """获取项目模板"""
    templates = {
        "survey_aspect": {
            "type": "survey_aspect",
            "title_template": "调研方面{id}: {title}",
            "content_template": """
## 调研目标
{description}

## 关键词
{keywords}

## 详细分析
请在此处添加详细的调研分析内容...
""",
            "metadata_fields": ["id", "title", "description", "keywords"]
        },
        "dxa_direction": {
            "type": "dxa_direction",
            "title_template": "DXA研究方向{number}: {title}",
            "content_template": """
## 研究背景
{background}

## 研究假说
{hypothesis}

## 数据需求
{data_requirements}

## 创新点
{innovation}

## 详细方案
请在此处添加详细的研究方案...
""",
            "metadata_fields": ["number", "title", "background", "hypothesis", "data_requirements", "innovation"]
        }
    }
    
    return {
        "success": True,
        "templates": templates
    }


# 快速创建预定义任务
@router.post("/quick-create/{template_type}")
async def quick_create_task(template_type: str, task_name: str, report_name: str):
    """快速创建预定义类型的任务"""
    try:
        # 创建任务
        create_request = CreateBatchTaskRequest(
            task_name=task_name,
            report_name=report_name
        )
        await create_batch_task(create_request)
        
        # 根据模板类型添加示例项目
        if template_type == "dxa_research":
            # 添加DXA研究方向示例
            sample_items = [
                {
                    "item_id": "dxa_001",
                    "item_type": "dxa_direction",
                    "title": "骨骼-肌肉协同发育：DXA影像预测肌少症患者握力下降速率",
                    "content_template": "基于DXA影像的肌少症预测研究...",
                    "metadata": {
                        "background": "肌少症患者存在骨量流失与肌肉萎缩的协同进展",
                        "hypothesis": "长骨皮质厚度变化与肌肉功能衰退存在时序关联"
                    }
                },
                {
                    "item_id": "dxa_002",
                    "item_type": "dxa_direction",
                    "title": "骨-心血管轴：DXA影像预测冠心病患者5年主要不良心血管事件",
                    "content_template": "基于DXA影像的心血管风险预测研究...",
                    "metadata": {
                        "background": "骨骼与心血管系统存在共同的调节机制",
                        "hypothesis": "骨密度分布模式与血管钙化程度相关"
                    }
                }
            ]
            
            add_request = AddBatchItemsRequest(
                task_name=task_name,
                items=sample_items
            )
            await add_batch_items(add_request)
        
        return {
            "success": True,
            "task_name": task_name,
            "template_type": template_type,
            "message": f"快速创建 {template_type} 类型任务成功"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"快速创建任务失败: {str(e)}") 
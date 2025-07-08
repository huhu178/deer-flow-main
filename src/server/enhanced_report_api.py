"""
增强的报告API - 支持完整的报告管理和n8n集成
"""

from fastapi import APIRouter, HTTPException, Query, Form, File, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional, Dict, Any
import json
import io
import zipfile
from datetime import datetime
from pydantic import BaseModel

from .report_manager import get_report_manager


router = APIRouter(prefix="/api/reports", tags=["reports"])


class ReportCreateRequest(BaseModel):
    """创建报告请求"""
    report_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class ReportSearchRequest(BaseModel):
    """搜索报告请求"""
    query: str
    limit: Optional[int] = 50


class N8NWebhookRequest(BaseModel):
    """n8n Webhook请求格式"""
    action: str  # create, get, list, search, delete, export
    data: Optional[Dict[str, Any]] = None


@router.post("/create")
async def create_report(request: ReportCreateRequest):
    """
    创建新报告
    
    支持n8n调用格式:
    POST /api/reports/create
    {
        "report_id": "research_001",
        "content": "# 研究报告...",
        "metadata": {"author": "AI", "type": "research"}
    }
    """
    try:
        report_manager = get_report_manager()
        
        report_info = report_manager.save_report(
            report_id=request.report_id,
            content=request.content,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "message": "报告创建成功",
            "data": report_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建报告失败: {str(e)}")


@router.get("/list")
async def list_reports(
    limit: int = Query(100, description="返回数量限制"),
    offset: int = Query(0, description="偏移量"),
    format: str = Query("json", description="返回格式: json, csv")
):
    """
    列出所有报告
    
    支持n8n调用:
    GET /api/reports/list?limit=10&offset=0&format=json
    """
    try:
        report_manager = get_report_manager()
        result = report_manager.list_reports(limit=limit, offset=offset)
        
        if format == "csv":
            # 返回CSV格式
            import csv
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=["id", "filename", "size", "created_time", "word_count"])
            writer.writeheader()
            
            for report in result["reports"]:
                writer.writerow({
                    "id": report["id"],
                    "filename": report["filename"],
                    "size": report["size"],
                    "created_time": report["created_time"],
                    "word_count": report["word_count"]
                })
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=reports.csv"}
            )
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取报告列表失败: {str(e)}")


@router.get("/{report_id}")
async def get_report(
    report_id: str,
    include_content: bool = Query(False, description="是否包含报告内容")
):
    """
    获取单个报告
    
    支持n8n调用:
    GET /api/reports/research_001?include_content=true
    """
    try:
        report_manager = get_report_manager()
        
        report_info = report_manager.get_report(report_id)
        if not report_info:
            raise HTTPException(status_code=404, detail="报告不存在")
        
        result = {
            "success": True,
            "data": report_info
        }
        
        if include_content:
            content = report_manager.get_report_content(report_id)
            result["data"]["content"] = content
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取报告失败: {str(e)}")


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    format: str = Query("md", description="下载格式: md, json, txt")
):
    """
    下载报告文件
    
    支持n8n调用:
    GET /api/reports/research_001/download?format=md
    """
    try:
        report_manager = get_report_manager()
        
        report_info = report_manager.get_report(report_id)
        if not report_info:
            raise HTTPException(status_code=404, detail="报告不存在")
        
        content = report_manager.get_report_content(report_id)
        if not content:
            raise HTTPException(status_code=404, detail="报告内容不存在")
        
        if format == "json":
            # 返回JSON格式
            json_data = {
                "report_info": report_info,
                "content": content
            }
            filename = f"{report_id}.json"
            media_type = "application/json"
            file_content = json.dumps(json_data, ensure_ascii=False, indent=2)
            
        elif format == "txt":
            # 返回纯文本格式
            filename = f"{report_id}.txt"
            media_type = "text/plain"
            file_content = content
            
        else:  # md
            # 返回Markdown格式
            filename = f"{report_id}.md"
            media_type = "text/markdown"
            file_content = content
        
        return StreamingResponse(
            io.BytesIO(file_content.encode('utf-8')),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载报告失败: {str(e)}")


@router.post("/search")
async def search_reports(request: ReportSearchRequest):
    """
    搜索报告
    
    支持n8n调用:
    POST /api/reports/search
    {
        "query": "DXA AI",
        "limit": 20
    }
    """
    try:
        report_manager = get_report_manager()
        
        results = report_manager.search_reports(
            query=request.query,
            limit=request.limit
        )
        
        return {
            "success": True,
            "data": {
                "query": request.query,
                "results": results,
                "count": len(results)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索报告失败: {str(e)}")


@router.delete("/{report_id}")
async def delete_report(report_id: str):
    """
    删除报告
    
    支持n8n调用:
    DELETE /api/reports/research_001
    """
    try:
        report_manager = get_report_manager()
        
        success = report_manager.delete_report(report_id)
        if not success:
            raise HTTPException(status_code=404, detail="报告不存在")
        
        return {
            "success": True,
            "message": f"报告 {report_id} 已删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除报告失败: {str(e)}")


@router.get("/export/all")
async def export_all_reports():
    """
    导出所有报告为ZIP文件
    
    支持n8n调用:
    GET /api/reports/export/all
    """
    try:
        report_manager = get_report_manager()
        
        zip_path = report_manager.export_all_reports()
        
        return FileResponse(
            path=zip_path,
            filename=f"all_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            media_type="application/zip"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出报告失败: {str(e)}")


@router.get("/stats")
async def get_statistics():
    """
    获取报告统计信息
    
    支持n8n调用:
    GET /api/reports/stats
    """
    try:
        report_manager = get_report_manager()
        stats = report_manager.get_statistics()
        
        return {
            "success": True,
            "data": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@router.post("/webhook/n8n")
async def n8n_webhook(request: N8NWebhookRequest):
    """
    n8n专用Webhook接口 - 统一处理所有操作
    
    支持的操作:
    - create: 创建报告
    - get: 获取报告
    - list: 列出报告
    - search: 搜索报告
    - delete: 删除报告
    - export: 导出报告
    - stats: 获取统计
    
    示例调用:
    POST /api/reports/webhook/n8n
    {
        "action": "create",
        "data": {
            "report_id": "test_001",
            "content": "# 测试报告",
            "metadata": {"type": "test"}
        }
    }
    """
    try:
        report_manager = get_report_manager()
        action = request.action.lower()
        data = request.data or {}
        
        if action == "create":
            # 创建报告
            report_info = report_manager.save_report(
                report_id=data["report_id"],
                content=data["content"],
                metadata=data.get("metadata")
            )
            return {"success": True, "action": action, "data": report_info}
            
        elif action == "get":
            # 获取报告
            report_id = data["report_id"]
            report_info = report_manager.get_report(report_id)
            if not report_info:
                return {"success": False, "error": "报告不存在"}
            
            if data.get("include_content", False):
                content = report_manager.get_report_content(report_id)
                report_info["content"] = content
            
            return {"success": True, "action": action, "data": report_info}
            
        elif action == "list":
            # 列出报告
            limit = data.get("limit", 100)
            offset = data.get("offset", 0)
            result = report_manager.list_reports(limit=limit, offset=offset)
            return {"success": True, "action": action, "data": result}
            
        elif action == "search":
            # 搜索报告
            query = data["query"]
            limit = data.get("limit", 50)
            results = report_manager.search_reports(query=query, limit=limit)
            return {"success": True, "action": action, "data": {"results": results, "count": len(results)}}
            
        elif action == "delete":
            # 删除报告
            report_id = data["report_id"]
            success = report_manager.delete_report(report_id)
            return {"success": success, "action": action, "message": f"报告 {report_id} 删除{'成功' if success else '失败'}"}
            
        elif action == "stats":
            # 获取统计
            stats = report_manager.get_statistics()
            return {"success": True, "action": action, "data": stats}
            
        else:
            return {"success": False, "error": f"不支持的操作: {action}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}


# 导出路由器
__all__ = ["router"] 
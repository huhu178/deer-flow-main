"""
健康检查API - 用于系统监控和Docker健康检查
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import psutil
import os
from datetime import datetime
from pathlib import Path

from .report_manager import get_report_manager

router = APIRouter(prefix="/api/reports", tags=["health"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    系统健康检查
    
    返回系统状态信息，用于Docker健康检查和监控
    """
    try:
        # 基础状态
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "deer-flow-api",
            "version": "1.0.0"
        }
        
        # 系统资源状态
        status["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
        
        # 检查关键目录
        reports_dir = Path("./outputs/reports")
        status["storage"] = {
            "reports_dir_exists": reports_dir.exists(),
            "reports_dir_writable": os.access(reports_dir, os.W_OK) if reports_dir.exists() else False
        }
        
        # 检查报告管理器
        try:
            report_manager = get_report_manager()
            stats = report_manager.get_statistics()
            status["reports"] = {
                "total_reports": stats.get("total_reports", 0),
                "manager_status": "ok"
            }
        except Exception as e:
            status["reports"] = {
                "manager_status": "error",
                "error": str(e)
            }
            status["status"] = "degraded"
        
        # 环境变量检查
        required_env_vars = ["PYTHONPATH"]
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            status["environment"] = {
                "status": "warning",
                "missing_vars": missing_vars
            }
        else:
            status["environment"] = {"status": "ok"}
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"健康检查失败: {str(e)}")


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    获取系统指标
    
    用于监控和性能分析
    """
    try:
        # 系统指标
        cpu_times = psutil.cpu_times()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "times": {
                        "user": cpu_times.user,
                        "system": cpu_times.system,
                        "idle": cpu_times.idle
                    }
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
            }
        }
        
        # 进程信息
        try:
            process = psutil.Process()
            metrics["process"] = {
                "pid": process.pid,
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "memory_info": process.memory_info()._asdict(),
                "create_time": process.create_time(),
                "num_threads": process.num_threads()
            }
        except Exception as e:
            metrics["process"] = {"error": str(e)}
        
        # 报告统计
        try:
            report_manager = get_report_manager()
            stats = report_manager.get_statistics()
            metrics["reports"] = stats
        except Exception as e:
            metrics["reports"] = {"error": str(e)}
        
        return metrics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取指标失败: {str(e)}")


@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    简单状态检查
    
    快速返回服务状态，用于负载均衡器健康检查
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "deer-flow-api"
    } 
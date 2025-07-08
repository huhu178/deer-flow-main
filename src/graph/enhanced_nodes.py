# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
增强节点执行器 - 提供更好的错误处理、并行执行和状态管理
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from functools import wraps

from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

logger = logging.getLogger(__name__)

@dataclass
class NodeExecutionResult:
    """节点执行结果"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0
    retry_count: int = 0

@dataclass 
class NodeConfig:
    """节点配置"""
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_parallel: bool = False
    critical: bool = True  # 是否为关键节点

class EnhancedNodeExecutor:
    """增强节点执行器"""
    
    def __init__(self):
        self.execution_history = []
        self.node_configs = {
            'background_investigation': NodeConfig(timeout=30, max_retries=2, critical=False),
            'planner': NodeConfig(timeout=45, max_retries=3, critical=True),
            'researcher': NodeConfig(timeout=120, max_retries=2, critical=True),
            'reporter': NodeConfig(timeout=90, max_retries=2, critical=True),
            'coder': NodeConfig(timeout=60, max_retries=2, critical=False)
        }
    
    def with_enhanced_execution(self, node_name: str):
        """装饰器：为节点添加增强执行能力"""
        
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await self.execute_node(node_name, func, *args, **kwargs)
            return wrapper
        return decorator
    
    async def execute_node(self, node_name: str, func: Callable, *args, **kwargs) -> Any:
        """增强节点执行"""
        
        config = self.node_configs.get(node_name, NodeConfig())
        start_time = time.time()
        
        logger.info(f"🚀 开始执行节点: {node_name}")
        
        for attempt in range(config.max_retries + 1):
            try:
                # 设置超时执行
                if asyncio.iscoroutinefunction(func):
                    result = await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=config.timeout
                    )
                else:
                    # 同步函数异步执行
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, func, *args, **kwargs),
                        timeout=config.timeout
                    )
                
                execution_time = time.time() - start_time
                
                # 记录成功执行
                execution_result = NodeExecutionResult(
                    success=True,
                    data={'result': result},
                    execution_time=execution_time,
                    retry_count=attempt
                )
                self.execution_history.append((node_name, execution_result))
                
                logger.info(f"✅ 节点 {node_name} 执行成功，耗时 {execution_time:.2f}s，重试 {attempt} 次")
                return result
                
            except TimeoutError:
                logger.warning(f"⏰ 节点 {node_name} 执行超时 (尝试 {attempt + 1}/{config.max_retries + 1})")
                
            except Exception as e:
                logger.error(f"❌ 节点 {node_name} 执行失败 (尝试 {attempt + 1}/{config.max_retries + 1}): {e}")
                
                if attempt < config.max_retries:
                    await asyncio.sleep(config.retry_delay * (attempt + 1))  # 指数退避
                    continue
            
            # 如果是非关键节点，返回降级结果
            if not config.critical:
                logger.info(f"🔄 非关键节点 {node_name} 执行失败，返回降级结果")
                return self.get_fallback_result(node_name)
        
        # 所有重试都失败了
        execution_time = time.time() - start_time
        execution_result = NodeExecutionResult(
            success=False,
            data={},
            error=f"节点执行失败，已重试 {config.max_retries} 次",
            execution_time=execution_time,
            retry_count=config.max_retries
        )
        self.execution_history.append((node_name, execution_result))
        
        if config.critical:
            logger.error(f"💥 关键节点 {node_name} 执行失败，系统将停止")
            raise Exception(f"关键节点 {node_name} 执行失败")
        else:
            logger.warning(f"⚠️ 非关键节点 {node_name} 执行失败，继续执行")
            return self.get_fallback_result(node_name)
    
    def get_fallback_result(self, node_name: str) -> Any:
        """获取节点的降级结果"""
        
        fallback_results = {
            'background_investigation': Command(
                update={"background_investigation_results": "[]"},
                goto="planner"
            ),
            'coder': {
                'code_output': '# 代码执行失败，请手动检查',
                'success': False
            }
        }
        
        return fallback_results.get(node_name, {})
    
    async def parallel_execute(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """并行执行多个任务"""
        
        logger.info(f"🔄 开始并行执行 {len(tasks)} 个任务")
        
        async def execute_task(task):
            task_name = task['name']
            task_func = task['func']
            task_args = task.get('args', [])
            task_kwargs = task.get('kwargs', {})
            
            try:
                result = await self.execute_node(task_name, task_func, *task_args, **task_kwargs)
                return {'name': task_name, 'success': True, 'result': result}
            except Exception as e:
                logger.error(f"❌ 并行任务 {task_name} 执行失败: {e}")
                return {'name': task_name, 'success': False, 'error': str(e)}
        
        # 并行执行所有任务
        results = await asyncio.gather(*[execute_task(task) for task in tasks], return_exceptions=True)
        
        # 整理结果
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
        logger.info(f"✅ 并行执行完成，成功 {success_count}/{len(tasks)} 个任务")
        
        return {
            'total_tasks': len(tasks),
            'successful_tasks': success_count,
            'results': results
        }
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """获取执行统计信息"""
        
        if not self.execution_history:
            return {}
        
        stats = {}
        for node_name, result in self.execution_history:
            if node_name not in stats:
                stats[node_name] = {
                    'total_executions': 0,
                    'successful_executions': 0,
                    'total_time': 0.0,
                    'total_retries': 0,
                    'avg_execution_time': 0.0,
                    'success_rate': 0.0
                }
            
            node_stats = stats[node_name]
            node_stats['total_executions'] += 1
            node_stats['total_time'] += result.execution_time
            node_stats['total_retries'] += result.retry_count
            
            if result.success:
                node_stats['successful_executions'] += 1
        
        # 计算平均值和成功率
        for node_name, node_stats in stats.items():
            if node_stats['total_executions'] > 0:
                node_stats['avg_execution_time'] = node_stats['total_time'] / node_stats['total_executions']
                node_stats['success_rate'] = node_stats['successful_executions'] / node_stats['total_executions']
        
        return stats
    
    def log_performance_summary(self):
        """输出性能总结"""
        
        stats = self.get_execution_stats()
        
        logger.info("📊 节点执行性能总结:")
        for node_name, node_stats in stats.items():
            logger.info(
                f"  {node_name}: "
                f"成功率 {node_stats['success_rate']:.2%}, "
                f"平均耗时 {node_stats['avg_execution_time']:.2f}s, "
                f"总重试 {node_stats['total_retries']} 次"
            )

# 创建全局实例
enhanced_node_executor = EnhancedNodeExecutor()

# 便捷装饰器
def enhanced_execution(node_name: str):
    """便捷的增强执行装饰器"""
    return enhanced_node_executor.with_enhanced_execution(node_name) 
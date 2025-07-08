#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分批输出管理器 - 系统版本
支持分次生成、暂存和最终完整输出
解决大模型输出限制问题
可集成到现有系统中使用
"""

import sys
import os
import time
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Generator, Optional, Callable, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from src.utils.report_manager import ReportManager
except ImportError:
    # 简单的替代实现
    class SimpleReportManager:
        def __init__(self, report_name, base_dir="./outputs", keep_chunks=True):
            self.report_name = report_name
            self.base_dir = Path(base_dir)
            self.report_dir = self.base_dir / report_name
            self.chunks_dir = self.report_dir / "chunks"
            self.report_dir.mkdir(parents=True, exist_ok=True)
            self.chunks_dir.mkdir(parents=True, exist_ok=True)
            self.sections = []
        
        def save_section(self, title, content, section_number, metadata=None):
            section_file = self.chunks_dir / f"section_{section_number:03d}.txt"
            with open(section_file, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n{content}")
            
            section_info = {
                "number": section_number,
                "title": title,
                "file": str(section_file),
                "created_at": datetime.now().isoformat(),
                "word_count": len(content),
                **(metadata or {})
            }
            self.sections.append(section_info)
            return section_file
        
        def merge_report(self, include_toc=True, sort_by_number=True):
            if sort_by_number:
                sections = sorted(self.sections, key=lambda x: x.get('number', 0))
            else:
                sections = self.sections
            
            report_content = []
            report_content.append(f"# {self.report_name}")
            report_content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            if include_toc:
                report_content.append("\n## 目录\n")
                for section in sections:
                    number = section.get('number', 0)
                    title = section.get('title', '未命名章节')
                    report_content.append(f"{number}. {title}")
            
            for section in sections:
                section_file = Path(section['file'])
                if section_file.exists():
                    with open(section_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    report_content.append(f"\n\n{'='*80}\n")
                    report_content.append(content)
            
            final_content = '\n'.join(report_content)
            final_path = self.report_dir / f"{self.report_name}.txt"
            with open(final_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            return final_path
        
        def get_stats(self):
            total_size = sum(section.get('word_count', 0) for section in self.sections)
            return {
                'section_count': len(self.sections),
                'total_size_bytes': total_size * 3,
                'total_size_kb': round(total_size * 3 / 1024, 2),
                'created_at': datetime.now().isoformat()
            }
    
    ReportManager = SimpleReportManager


class BatchStatus(Enum):
    """批次状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class GenerationStatus(Enum):
    """生成状态枚举"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    GENERATING = "generating"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BatchItem:
    """批次项目数据结构"""
    id: str
    type: str
    title: str
    content_template: str
    metadata: Dict[str, Any]
    section_number: int
    estimated_tokens: int = 0
    
    def to_dict(self):
        return asdict(self)


@dataclass
class BatchResult:
    """批次结果数据结构"""
    batch_id: str
    item_id: str
    title: str
    content: str
    section_number: int
    word_count: int
    token_count: int
    generated_time: str
    status: str
    error_message: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class GenerationProgress:
    """生成进度数据结构"""
    total_items: int
    completed_items: int
    current_batch: int
    total_batches: int
    current_item: Optional[str]
    status: GenerationStatus
    start_time: str
    estimated_completion: Optional[str]
    error_message: Optional[str] = None
    
    @property
    def progress_percentage(self) -> float:
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100
    
    def to_dict(self):
        result = asdict(self)
        result['progress_percentage'] = self.progress_percentage
        return result


class SystemBatchOutputManager:
    """系统级分批输出管理器"""
    
    def __init__(
        self,
        report_name: str,
        base_dir: str = "./outputs/batch_reports",
        batch_size: int = 5,
        max_tokens_per_item: int = 4000,
        content_generator: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
        error_callback: Optional[Callable] = None
    ):
        """
        初始化分批输出管理器
        
        Args:
            report_name: 报告名称
            base_dir: 输出目录
            batch_size: 每批处理的项目数量
            max_tokens_per_item: 每个项目的最大token数
            content_generator: 内容生成器函数
            progress_callback: 进度回调函数
            error_callback: 错误回调函数
        """
        self.report_name = report_name
        self.base_dir = Path(base_dir)
        self.batch_size = batch_size
        self.max_tokens_per_item = max_tokens_per_item
        self.content_generator = content_generator
        self.progress_callback = progress_callback
        self.error_callback = error_callback
        
        # 创建报告管理器
        self.manager = ReportManager(
            report_name=report_name,
            base_dir=str(base_dir),
            keep_chunks=True
        )
        
        # 状态管理
        self.items: List[BatchItem] = []
        self.batches: Dict[str, List[BatchItem]] = {}
        self.results: Dict[str, BatchResult] = {}
        self.batch_status: Dict[str, BatchStatus] = {}
        self.generation_status = GenerationStatus.IDLE
        self.progress = GenerationProgress(
            total_items=0,
            completed_items=0,
            current_batch=0,
            total_batches=0,
            current_item=None,
            status=GenerationStatus.IDLE,
            start_time=datetime.now().isoformat()
        )
        
        # 创建状态文件目录
        self.state_dir = self.base_dir / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载已有状态
        self._load_state()
    
    def add_item(
        self,
        item_id: str,
        item_type: str,
        title: str,
        content_template: str,
        metadata: Optional[Dict[str, Any]] = None,
        estimated_tokens: int = 0
    ) -> bool:
        """
        添加待生成项目
        
        Args:
            item_id: 项目唯一标识
            item_type: 项目类型
            title: 项目标题
            content_template: 内容模板
            metadata: 元数据
            estimated_tokens: 预估token数
            
        Returns:
            bool: 是否添加成功
        """
        try:
            if estimated_tokens == 0:
                estimated_tokens = min(len(content_template) * 2, self.max_tokens_per_item)
            
            item = BatchItem(
                id=item_id,
                type=item_type,
                title=title,
                content_template=content_template,
                metadata=metadata or {},
                section_number=len(self.items) + 1,
                estimated_tokens=estimated_tokens
            )
            
            self.items.append(item)
            self._update_progress()
            self._save_state()
            
            return True
            
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"添加项目失败: {str(e)}")
            return False
    
    def add_items_batch(self, items: List[Dict[str, Any]]) -> int:
        """
        批量添加项目
        
        Args:
            items: 项目列表
            
        Returns:
            int: 成功添加的项目数量
        """
        success_count = 0
        for item_data in items:
            if self.add_item(**item_data):
                success_count += 1
        
        return success_count
    
    def clear_items(self):
        """清空所有项目"""
        self.items.clear()
        self.batches.clear()
        self.results.clear()
        self.batch_status.clear()
        self.generation_status = GenerationStatus.IDLE
        self._update_progress()
        self._save_state()
    
    def get_progress(self) -> Dict[str, Any]:
        """获取当前进度"""
        return self.progress.to_dict()
    
    def get_items(self) -> List[Dict[str, Any]]:
        """获取所有项目"""
        return [item.to_dict() for item in self.items]
    
    def get_results(self) -> List[Dict[str, Any]]:
        """获取所有结果"""
        return [result.to_dict() for result in self.results.values()]
    
    def get_batch_status(self) -> Dict[str, str]:
        """获取批次状态"""
        return {batch_id: status.value for batch_id, status in self.batch_status.items()}
    
    async def generate_all_async(self) -> Dict[str, Any]:
        """
        异步生成所有内容
        
        Returns:
            Dict: 生成结果
        """
        try:
            self.generation_status = GenerationStatus.INITIALIZING
            self._update_progress()
            
            # 创建批次
            self._create_batches()
            
            self.generation_status = GenerationStatus.GENERATING
            self._update_progress()
            
            # 逐批生成
            for batch_id, batch_items in self.batches.items():
                await self._generate_batch_async(batch_id, batch_items)
                
                if self.generation_status == GenerationStatus.FAILED:
                    break
            
            if self.generation_status != GenerationStatus.FAILED:
                # 合并报告
                self.generation_status = GenerationStatus.MERGING
                self._update_progress()
                
                merge_result = await self._merge_report_async()
                
                if merge_result["success"]:
                    self.generation_status = GenerationStatus.COMPLETED
                    self._update_progress()
                    
                    return {
                        "success": True,
                        "final_path": str(merge_result["final_path"]),
                        "stats": merge_result["stats"],
                        "progress": self.get_progress()
                    }
                else:
                    self.generation_status = GenerationStatus.FAILED
                    self.progress.error_message = merge_result.get("error", "合并失败")
                    self._update_progress()
                    
                    return {
                        "success": False,
                        "error": merge_result.get("error", "合并失败"),
                        "progress": self.get_progress()
                    }
            else:
                return {
                    "success": False,
                    "error": self.progress.error_message or "生成失败",
                    "progress": self.get_progress()
                }
                
        except Exception as e:
            self.generation_status = GenerationStatus.FAILED
            self.progress.error_message = str(e)
            self._update_progress()
            
            if self.error_callback:
                self.error_callback(f"生成过程出错: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "progress": self.get_progress()
            }
    
    def generate_all_sync(self) -> Dict[str, Any]:
        """
        同步生成所有内容
        
        Returns:
            Dict: 生成结果
        """
        return asyncio.run(self.generate_all_async())
    
    async def generate_stream_async(self) -> Generator[Dict[str, Any], None, None]:
        """
        流式生成内容
        
        Yields:
            Dict: 实时进度和结果
        """
        try:
            self.generation_status = GenerationStatus.INITIALIZING
            self._update_progress()
            yield {"type": "progress", "data": self.get_progress()}
            
            # 创建批次
            self._create_batches()
            
            self.generation_status = GenerationStatus.GENERATING
            self._update_progress()
            yield {"type": "progress", "data": self.get_progress()}
            
            # 逐批生成
            for batch_id, batch_items in self.batches.items():
                async for result in self._generate_batch_stream_async(batch_id, batch_items):
                    yield result
                
                if self.generation_status == GenerationStatus.FAILED:
                    break
            
            if self.generation_status != GenerationStatus.FAILED:
                # 合并报告
                self.generation_status = GenerationStatus.MERGING
                self._update_progress()
                yield {"type": "progress", "data": self.get_progress()}
                
                merge_result = await self._merge_report_async()
                
                if merge_result["success"]:
                    self.generation_status = GenerationStatus.COMPLETED
                    self._update_progress()
                    
                    yield {
                        "type": "completed",
                        "data": {
                            "success": True,
                            "final_path": str(merge_result["final_path"]),
                            "stats": merge_result["stats"],
                            "progress": self.get_progress()
                        }
                    }
                else:
                    self.generation_status = GenerationStatus.FAILED
                    self.progress.error_message = merge_result.get("error", "合并失败")
                    self._update_progress()
                    
                    yield {
                        "type": "error",
                        "data": {
                            "error": merge_result.get("error", "合并失败"),
                            "progress": self.get_progress()
                        }
                    }
            
        except Exception as e:
            self.generation_status = GenerationStatus.FAILED
            self.progress.error_message = str(e)
            self._update_progress()
            
            if self.error_callback:
                self.error_callback(f"流式生成出错: {str(e)}")
            
            yield {
                "type": "error",
                "data": {
                    "error": str(e),
                    "progress": self.get_progress()
                }
            }
    
    def cancel_generation(self):
        """取消生成"""
        self.generation_status = GenerationStatus.FAILED
        self.progress.error_message = "用户取消"
        self._update_progress()
        
        # 更新所有未完成批次的状态
        for batch_id, status in self.batch_status.items():
            if status in [BatchStatus.PENDING, BatchStatus.RUNNING]:
                self.batch_status[batch_id] = BatchStatus.CANCELLED
        
        self._save_state()
    
    def _create_batches(self):
        """创建批次"""
        self.batches.clear()
        self.batch_status.clear()
        
        for i in range(0, len(self.items), self.batch_size):
            batch_id = f"batch_{i // self.batch_size + 1}"
            batch_items = self.items[i:i + self.batch_size]
            
            self.batches[batch_id] = batch_items
            self.batch_status[batch_id] = BatchStatus.PENDING
        
        self.progress.total_batches = len(self.batches)
        self._update_progress()
    
    async def _generate_batch_async(self, batch_id: str, batch_items: List[BatchItem]):
        """异步生成单个批次"""
        try:
            self.batch_status[batch_id] = BatchStatus.RUNNING
            self.progress.current_batch = int(batch_id.split('_')[1])
            
            for item in batch_items:
                if self.generation_status == GenerationStatus.FAILED:
                    break
                
                self.progress.current_item = item.title
                self._update_progress()
                
                # 生成内容
                content = await self._generate_item_content_async(item)
                
                if content:
                    # 创建结果
                    result = BatchResult(
                        batch_id=batch_id,
                        item_id=item.id,
                        title=item.title,
                        content=content,
                        section_number=item.section_number,
                        word_count=len(content),
                        token_count=min(len(content) * 0.75, self.max_tokens_per_item),
                        generated_time=datetime.now().isoformat(),
                        status="completed"
                    )
                    
                    self.results[item.id] = result
                    self.progress.completed_items += 1
                    self._update_progress()
                    
                    # 保存到报告管理器
                    self.manager.save_section(
                        title=item.title,
                        content=content,
                        section_number=item.section_number,
                        metadata={
                            "batch_id": batch_id,
                            "item_type": item.type,
                            "generated_time": result.generated_time
                        }
                    )
                else:
                    # 生成失败
                    result = BatchResult(
                        batch_id=batch_id,
                        item_id=item.id,
                        title=item.title,
                        content="",
                        section_number=item.section_number,
                        word_count=0,
                        token_count=0,
                        generated_time=datetime.now().isoformat(),
                        status="failed",
                        error_message="内容生成失败"
                    )
                    
                    self.results[item.id] = result
            
            self.batch_status[batch_id] = BatchStatus.COMPLETED
            self._save_state()
            
        except Exception as e:
            self.batch_status[batch_id] = BatchStatus.FAILED
            if self.error_callback:
                self.error_callback(f"批次 {batch_id} 生成失败: {str(e)}")
    
    async def _generate_batch_stream_async(self, batch_id: str, batch_items: List[BatchItem]):
        """流式生成单个批次"""
        try:
            self.batch_status[batch_id] = BatchStatus.RUNNING
            self.progress.current_batch = int(batch_id.split('_')[1])
            
            yield {"type": "batch_start", "data": {"batch_id": batch_id, "items": len(batch_items)}}
            
            for item in batch_items:
                if self.generation_status == GenerationStatus.FAILED:
                    break
                
                self.progress.current_item = item.title
                self._update_progress()
                
                yield {"type": "item_start", "data": {"item_id": item.id, "title": item.title}}
                yield {"type": "progress", "data": self.get_progress()}
                
                # 生成内容
                content = await self._generate_item_content_async(item)
                
                if content:
                    # 创建结果
                    result = BatchResult(
                        batch_id=batch_id,
                        item_id=item.id,
                        title=item.title,
                        content=content,
                        section_number=item.section_number,
                        word_count=len(content),
                        token_count=min(len(content) * 0.75, self.max_tokens_per_item),
                        generated_time=datetime.now().isoformat(),
                        status="completed"
                    )
                    
                    self.results[item.id] = result
                    self.progress.completed_items += 1
                    self._update_progress()
                    
                    # 保存到报告管理器
                    self.manager.save_section(
                        title=item.title,
                        content=content,
                        section_number=item.section_number,
                        metadata={
                            "batch_id": batch_id,
                            "item_type": item.type,
                            "generated_time": result.generated_time
                        }
                    )
                    
                    yield {"type": "item_completed", "data": result.to_dict()}
                else:
                    # 生成失败
                    result = BatchResult(
                        batch_id=batch_id,
                        item_id=item.id,
                        title=item.title,
                        content="",
                        section_number=item.section_number,
                        word_count=0,
                        token_count=0,
                        generated_time=datetime.now().isoformat(),
                        status="failed",
                        error_message="内容生成失败"
                    )
                    
                    self.results[item.id] = result
                    yield {"type": "item_failed", "data": result.to_dict()}
                
                yield {"type": "progress", "data": self.get_progress()}
            
            self.batch_status[batch_id] = BatchStatus.COMPLETED
            self._save_state()
            
            yield {"type": "batch_completed", "data": {"batch_id": batch_id}}
            
        except Exception as e:
            self.batch_status[batch_id] = BatchStatus.FAILED
            yield {"type": "batch_failed", "data": {"batch_id": batch_id, "error": str(e)}}
            
            if self.error_callback:
                self.error_callback(f"批次 {batch_id} 生成失败: {str(e)}")
    
    async def _generate_item_content_async(self, item: BatchItem) -> Optional[str]:
        """异步生成单个项目内容"""
        try:
            if self.content_generator:
                # 使用自定义内容生成器
                if asyncio.iscoroutinefunction(self.content_generator):
                    return await self.content_generator(item)
                else:
                    return self.content_generator(item)
            else:
                # 使用默认内容生成器
                return self._default_content_generator(item)
                
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"生成项目 {item.id} 内容失败: {str(e)}")
            return None
    
    def _default_content_generator(self, item: BatchItem) -> str:
        """默认内容生成器"""
        return f"""# {item.title}

## 项目信息
- **项目ID**: {item.id}
- **项目类型**: {item.type}
- **章节号**: {item.section_number}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 内容模板
{item.content_template}

## 元数据
{json.dumps(item.metadata, ensure_ascii=False, indent=2)}

---
*此内容由默认生成器生成，请使用自定义内容生成器获得更好的结果。*
"""
    
    async def _merge_report_async(self) -> Dict[str, Any]:
        """异步合并报告"""
        try:
            final_path = self.manager.merge_report(
                include_toc=True,
                sort_by_number=True
            )
            
            stats = self.manager.get_stats()
            
            return {
                "success": True,
                "final_path": final_path,
                "stats": stats
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"合并报告时出错: {str(e)}"
            }
    
    def _update_progress(self):
        """更新进度"""
        self.progress.status = self.generation_status
        
        if self.progress_callback:
            self.progress_callback(self.progress.to_dict())
    
    def _save_state(self):
        """保存状态到文件"""
        try:
            state_data = {
                "items": [item.to_dict() for item in self.items],
                "results": {k: v.to_dict() for k, v in self.results.items()},
                "batch_status": {k: v.value for k, v in self.batch_status.items()},
                "progress": self.progress.to_dict(),
                "generation_status": self.generation_status.value,
                "saved_at": datetime.now().isoformat()
            }
            
            state_file = self.state_dir / "manager_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"保存状态失败: {str(e)}")
    
    def _load_state(self):
        """从文件加载状态"""
        try:
            state_file = self.state_dir / "manager_state.json"
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    state_data = json.load(f)
                
                # 恢复项目
                self.items = [BatchItem(**item_data) for item_data in state_data.get("items", [])]
                
                # 恢复结果
                results_data = state_data.get("results", {})
                self.results = {k: BatchResult(**v) for k, v in results_data.items()}
                
                # 恢复批次状态
                batch_status_data = state_data.get("batch_status", {})
                self.batch_status = {k: BatchStatus(v) for k, v in batch_status_data.items()}
                
                # 恢复进度
                progress_data = state_data.get("progress", {})
                if progress_data:
                    self.progress = GenerationProgress(**progress_data)
                
                # 恢复生成状态
                generation_status = state_data.get("generation_status", "idle")
                self.generation_status = GenerationStatus(generation_status)
                
        except Exception as e:
            if self.error_callback:
                self.error_callback(f"加载状态失败: {str(e)}")


# 工厂函数
def create_batch_manager(
    report_name: str,
    content_generator: Optional[Callable] = None,
    **kwargs
) -> SystemBatchOutputManager:
    """
    创建分批输出管理器实例
    
    Args:
        report_name: 报告名称
        content_generator: 内容生成器函数
        **kwargs: 其他参数
        
    Returns:
        SystemBatchOutputManager: 管理器实例
    """
    return SystemBatchOutputManager(
        report_name=report_name,
        content_generator=content_generator,
        **kwargs
    )


# 便捷函数
async def generate_batch_report_async(
    report_name: str,
    items: List[Dict[str, Any]],
    content_generator: Optional[Callable] = None,
    progress_callback: Optional[Callable] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    便捷的异步批量报告生成函数
    
    Args:
        report_name: 报告名称
        items: 项目列表
        content_generator: 内容生成器
        progress_callback: 进度回调
        **kwargs: 其他参数
        
    Returns:
        Dict: 生成结果
    """
    manager = create_batch_manager(
        report_name=report_name,
        content_generator=content_generator,
        progress_callback=progress_callback,
        **kwargs
    )
    
    manager.add_items_batch(items)
    return await manager.generate_all_async()


def generate_batch_report_sync(
    report_name: str,
    items: List[Dict[str, Any]],
    content_generator: Optional[Callable] = None,
    progress_callback: Optional[Callable] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    便捷的同步批量报告生成函数
    
    Args:
        report_name: 报告名称
        items: 项目列表
        content_generator: 内容生成器
        progress_callback: 进度回调
        **kwargs: 其他参数
        
    Returns:
        Dict: 生成结果
    """
    return asyncio.run(generate_batch_report_async(
        report_name=report_name,
        items=items,
        content_generator=content_generator,
        progress_callback=progress_callback,
        **kwargs
    )) 
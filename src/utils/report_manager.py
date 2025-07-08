import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

class ReportManager:
    """
    Deer Flow 大型报告管理器
    管理大型输出报告的生成、存储和合并
    """
    
    def __init__(self, 
                 report_name: Optional[str] = None,
                 base_dir: str = "./outputs/reports", 
                 keep_chunks: bool = True):
        """
        初始化报告管理器
        
        Args:
            report_name: 报告名称，默认使用时间戳
            base_dir: 报告存储基础目录
            keep_chunks: 是否保留中间章节文件
        """
        # 如果没有指定报告名称，使用时间戳创建
        if not report_name:
            timestamp = int(datetime.now().timestamp())
            report_name = f"report_{timestamp}"
            
        self.report_name = report_name
        self.base_dir = Path(base_dir)
        self.keep_chunks = keep_chunks
        
        # 创建报告目录结构
        self.report_dir = self.base_dir / report_name
        self.chunks_dir = self.report_dir / "chunks"
        
        # 确保目录存在
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化章节列表和元数据
        self.sections = []
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "sections": []
        }
        
        # 如果元数据文件已存在，加载它
        self._load_metadata()
    
    def _load_metadata(self):
        """加载现有的元数据"""
        metadata_path = self.report_dir / "metadata.json"
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                self.sections = self.metadata.get("sections", [])
            except Exception as e:
                print(f"警告：无法加载元数据文件: {e}")
    
    def save_section(self, title: str, content: str, section_number: int = None, metadata: dict = None) -> str:
        """
        保存报告章节
        
        Args:
            title: 章节标题
            content: 章节内容
            section_number: 章节编号（可选，自动递增）
            metadata: 额外的元数据（可选）
            
        Returns:
            str: 保存的文件路径
        """
        if section_number is None:
            section_number = len(self.sections) + 1
            
        # 创建章节文件名
        section_filename = f"section_{section_number:03d}.txt"
        section_path = self.chunks_dir / section_filename
        
        # 保存章节内容（使用UTF-8编码）
        with open(section_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 记录章节信息
        section_info = {
            "number": section_number,
            "title": title,
            "file": str(section_path),
            "created_at": datetime.now().isoformat(),
            "size_bytes": len(content.encode('utf-8')),
            **(metadata or {})
        }
        
        self.sections.append(section_info)
        self.metadata["sections"] = self.sections
        self._save_metadata()
        
        return str(section_path)
    
    def merge_report(self, include_toc: bool = True, sort_by_number: bool = True) -> str:
        """
        合并所有章节为完整报告
        
        Args:
            include_toc: 是否包含目录
            sort_by_number: 是否按章节编号排序
            
        Returns:
            str: 完整报告的文件路径
        """
        if sort_by_number:
            sections = sorted(self.sections, key=lambda x: x.get('number', 0))
        else:
            sections = self.sections
        
        # 创建完整报告
        report_content = []
        
        # 添加报告标题和生成时间
        report_content.append(f"# {self.report_name}")
        report_content.append("")
        report_content.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append("")
        
        # 添加目录
        if include_toc:
            report_content.append("目录")
            for section in sections:
                number = section.get('number', 0)
                title = section.get('title', '未命名章节')
                report_content.append(f"{number}. {title}")
            report_content.append("")
            report_content.append("=" * 50)
            report_content.append("")
        
        # 添加各章节内容
        for section in sections:
            number = section.get('number', 0)
            title = section.get('title', '未命名章节')
            file_path = section.get('file', '')
            
            # 添加章节分隔符
            report_content.append("=" * 50)
            report_content.append(f"章节 {number}: {title}")
            report_content.append("=" * 50)
            report_content.append("")
            
            # 读取章节内容（使用UTF-8编码）
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        chapter_content = f.read()
                    report_content.append(chapter_content)
                except Exception as e:
                    report_content.append(f"错误：无法读取章节文件 {file_path}: {e}")
            else:
                report_content.append(f"错误：章节文件不存在 {file_path}")
            
            report_content.append("")
            report_content.append("")
        
        # 保存完整报告（使用UTF-8编码）
        report_path = self.report_dir / f"{self.report_name}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))
        
        # 更新元数据
        self.metadata["merged_at"] = datetime.now().isoformat()
        self.metadata["final_report_path"] = str(report_path)
        self._save_metadata()
        
        return str(report_path)
    
    def _save_metadata(self):
        """保存报告元数据"""
        metadata_path = self.report_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def _cleanup_chunks(self):
        """清理中间章节文件"""
        import shutil
        if self.chunks_dir.exists():
            shutil.rmtree(self.chunks_dir)
        
    def get_stats(self) -> Dict[str, Any]:
        """
        获取报告统计信息
        
        Returns:
            Dict: 统计信息
        """
        sections = self.metadata.get("sections", [])
        total_size = sum(section.get("size_bytes", 0) for section in sections)
        
        return {
            "report_name": self.report_name,
            "section_count": len(sections),
            "total_size_bytes": total_size,
            "total_size_kb": round(total_size / 1024, 2),
            "created_at": self.metadata.get("created_at"),
            "merged_at": self.metadata.get("merged_at")
        }


# 使用示例
if __name__ == "__main__":
    # 创建报告管理器
    report_manager = ReportManager(report_name="测试报告")
    
    # 添加章节
    for i in range(1, 6):
        content = f"这是第{i}章节的内容\n" * 100
        report_manager.save_section(
            title=f"第{i}章: 测试内容", 
            content=content,
            metadata={"importance": i * 20}
        )
        print(f"已保存第{i}章")
    
    # 合并报告
    final_path = report_manager.merge_report()
    
    # 打印统计信息
    stats = report_manager.get_stats()
    print(f"报告生成完成: {final_path}")
    print(f"报告统计: 共{stats['section_count']}章，总大小{stats['total_size_kb']}KB") 
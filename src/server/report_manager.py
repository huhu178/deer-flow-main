"""
报告管理系统 - 统一管理所有生成的报告
支持多种存储方式和访问接口
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import zipfile
import hashlib


class ReportManager:
    """统一的报告管理器"""
    
    def __init__(self, base_dir: str = "./outputs"):
        self.base_dir = Path(base_dir)
        self.reports_dir = self.base_dir / "reports"
        self.archive_dir = self.base_dir / "archives"
        
        # 确保目录存在
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化索引文件
        self.index_file = self.reports_dir / "index.json"
        self._load_index()
    
    def _load_index(self):
        """加载报告索引"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        else:
            self.index = {
                "reports": {},
                "last_updated": datetime.now().isoformat()
            }
    
    def _save_index(self):
        """保存报告索引"""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def save_report(self, report_id: str, content: str, metadata: Dict = None) -> Dict:
        """
        保存报告
        
        Args:
            report_id: 报告唯一标识
            content: 报告内容
            metadata: 报告元数据
        
        Returns:
            报告信息字典
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 生成文件名
        filename = f"{report_id}_{timestamp}.md"
        report_path = self.reports_dir / filename
        
        # 保存报告内容
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 生成文件哈希
        file_hash = self._calculate_file_hash(report_path)
        
        # 构建报告信息
        report_info = {
            "id": report_id,
            "filename": filename,
            "path": str(report_path),
            "size": report_path.stat().st_size,
            "hash": file_hash,
            "created_time": timestamp,
            "metadata": metadata or {},
            "word_count": len(content.split()),
            "char_count": len(content)
        }
        
        # 更新索引
        self.index["reports"][report_id] = report_info
        self._save_index()
        
        return report_info
    
    def get_report(self, report_id: str) -> Optional[Dict]:
        """获取报告信息"""
        return self.index["reports"].get(report_id)
    
    def get_report_content(self, report_id: str) -> Optional[str]:
        """获取报告内容"""
        report_info = self.get_report(report_id)
        if not report_info:
            return None
        
        report_path = Path(report_info["path"])
        if not report_path.exists():
            return None
        
        with open(report_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def list_reports(self, limit: int = 100, offset: int = 0) -> Dict:
        """列出所有报告"""
        reports = list(self.index["reports"].values())
        
        # 按创建时间排序
        reports.sort(key=lambda x: x["created_time"], reverse=True)
        
        # 分页
        total = len(reports)
        reports = reports[offset:offset + limit]
        
        return {
            "reports": reports,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    def search_reports(self, query: str, limit: int = 50) -> List[Dict]:
        """搜索报告"""
        results = []
        query_lower = query.lower()
        
        for report_info in self.index["reports"].values():
            # 在报告ID、文件名、元数据中搜索
            searchable_text = f"{report_info['id']} {report_info['filename']} {json.dumps(report_info['metadata'])}"
            
            if query_lower in searchable_text.lower():
                results.append(report_info)
        
        # 按创建时间排序
        results.sort(key=lambda x: x["created_time"], reverse=True)
        
        return results[:limit]
    
    def delete_report(self, report_id: str) -> bool:
        """删除报告"""
        report_info = self.get_report(report_id)
        if not report_info:
            return False
        
        # 删除文件
        report_path = Path(report_info["path"])
        if report_path.exists():
            report_path.unlink()
        
        # 从索引中删除
        del self.index["reports"][report_id]
        self._save_index()
        
        return True
    
    def archive_report(self, report_id: str) -> str:
        """归档报告"""
        report_info = self.get_report(report_id)
        if not report_info:
            raise ValueError(f"报告 {report_id} 不存在")
        
        # 创建归档文件
        archive_name = f"{report_id}_{report_info['created_time']}.zip"
        archive_path = self.archive_dir / archive_name
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加报告文件
            report_path = Path(report_info["path"])
            zipf.write(report_path, report_path.name)
            
            # 添加元数据
            metadata_str = json.dumps(report_info, ensure_ascii=False, indent=2)
            zipf.writestr("metadata.json", metadata_str)
        
        return str(archive_path)
    
    def export_all_reports(self) -> str:
        """导出所有报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_name = f"all_reports_{timestamp}.zip"
        export_path = self.archive_dir / export_name
        
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 添加所有报告文件
            for report_info in self.index["reports"].values():
                report_path = Path(report_info["path"])
                if report_path.exists():
                    zipf.write(report_path, f"reports/{report_path.name}")
            
            # 添加索引文件
            zipf.write(self.index_file, "index.json")
        
        return str(export_path)
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        reports = list(self.index["reports"].values())
        
        total_size = sum(report["size"] for report in reports)
        total_words = sum(report["word_count"] for report in reports)
        total_chars = sum(report["char_count"] for report in reports)
        
        # 按日期分组统计
        daily_stats = {}
        for report in reports:
            date = report["created_time"][:8]  # YYYYMMDD
            if date not in daily_stats:
                daily_stats[date] = 0
            daily_stats[date] += 1
        
        return {
            "total_reports": len(reports),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "total_words": total_words,
            "total_chars": total_chars,
            "average_report_size": round(total_size / len(reports), 2) if reports else 0,
            "daily_stats": daily_stats,
            "storage_path": str(self.reports_dir)
        }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()


# 全局报告管理器实例
global_report_manager = ReportManager()


def get_report_manager() -> ReportManager:
    """获取全局报告管理器"""
    return global_report_manager 
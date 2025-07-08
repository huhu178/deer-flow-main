"""
完整报告生成器
按照8个批次生成完整的研究报告，而不是简单拼接研究方向
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ReportSection:
    """报告章节数据结构"""
    section_id: str
    title: str
    target_words: int
    content: str = ""
    generated: bool = False
    generation_time: Optional[datetime] = None

class CompleteReportGenerator:
    """完整报告生成器 - 按照8个批次生成完整的研究报告"""
    
    def __init__(self, report_name: str, output_dir: str = "./outputs/complete_reports"):
        self.report_name = report_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建时间戳
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / f"{report_name}_{self.timestamp}"
        self.session_dir.mkdir(exist_ok=True)
        
        # 定义报告结构 - 8个批次
        self.report_sections = self._define_report_structure()
        self.current_batch = 0
        self.generated_sections = {}
        
        logger.info(f"初始化完整报告生成器: {self.report_name}")
    
    def _define_report_structure(self) -> Dict[str, ReportSection]:
        """定义报告的8个批次结构"""
        return {
            "summary": ReportSection(
                section_id="summary",
                title="执行摘要",
                target_words=2500
            ),
            "introduction": ReportSection(
                section_id="introduction", 
                title="前言与研究背景",
                target_words=4500
            ),
            "current_status": ReportSection(
                section_id="current_status",
                title="领域现状与趋势分析", 
                target_words=6000
            ),
            "research_directions": ReportSection(
                section_id="research_directions",
                title="核心研究方向深度分析",
                target_words=55000  # 20个方向，每个约2750字
            ),
            "innovation_analysis": ReportSection(
                section_id="innovation_analysis",
                title="创新突破点综合分析",
                target_words=2500
            ),
            "implementation": ReportSection(
                section_id="implementation",
                title="实施建议与优先级分析", 
                target_words=2000
            ),
            "conclusion": ReportSection(
                section_id="conclusion",
                title="总结与展望",
                target_words=1500
            ),
            "references": ReportSection(
                section_id="references",
                title="参考文献汇总",
                target_words=1000
            )
        }
    
    def get_next_batch_prompt(self) -> Optional[str]:
        """获取下一个批次的生成提示"""
        section_keys = list(self.report_sections.keys())
        
        if self.current_batch >= len(section_keys):
            return None
            
        section_key = section_keys[self.current_batch]
        section = self.report_sections[section_key]
        
        # 为核心研究方向生成特殊的提示
        if section_key == "research_directions":
            return self._get_research_directions_prompt()
        
        # 为其他章节生成通用提示
        return self._get_section_prompt(section)
    
    def _get_section_prompt(self, section: ReportSection) -> str:
        """生成通用章节的提示"""
        context = self._get_report_context()
        
        prompt = f"""
# 角色：资深研究报告撰写专家

您正在撰写一份关于"基于人工智能与桡骨DXA影像的全身健康状态预测研究"的完整报告。

## 当前任务
请撰写报告的第{self.current_batch + 1}部分：**{section.title}**

## 字数要求
- 目标字数：{section.target_words}字
- 最少不低于：{int(section.target_words * 0.8)}字

## 内容要求

{self._get_section_content_requirements(section.section_id)}

## 写作要求
- 🎯 **学术严谨性**：使用准确的学术术语和科学表述
- 🔬 **深度分析**：提供深入的技术分析和科学洞察
- 💡 **创新性思维**：突出颠覆性创新点和前沿技术
- 📊 **数据支撑**：引用具体的研究数据和统计信息
- 🌐 **国际视野**：结合国际前沿研究和发展趋势

## 报告上下文
{context}

请直接输出{section.title}的完整内容，不需要额外的格式说明。
"""
        return prompt
    
    def _get_research_directions_prompt(self) -> str:
        """生成研究方向部分的特殊提示"""
        return f"""
# 角色：颠覆性研究方向专家

您正在撰写"基于人工智能与桡骨DXA影像的全身健康状态预测研究"报告的核心部分。

## 当前任务
请撰写报告的第4部分：**核心研究方向深度分析**

## 总体要求
- 提出20个具有颠覆性创新潜力的研究方向
- 每个方向约2750字，总计约55000字
- 每个方向必须包含10个完整子章节

## 20个研究方向框架
请按以下结构生成20个研究方向：

### 方向1-5：基础技术创新类
1. 基于深度学习的DXA影像自动骨质疏松诊断与分级
2. DXA影像组学在心血管疾病风险早期预测中的应用  
3. AI辅助DXA影像骨折风险评分模型的开发与验证
4. 多模态融合的DXA影像全身健康状态智能评估
5. 基于桡骨DXA影像预测糖尿病并发症风险的AI模型

### 方向6-10：技术方法突破类
6. DXA影像纹理分析在代谢综合征诊断中的创新应用
7. 基于图神经网络的DXA骨微结构连通性分析
8. DXA影像联邦学习框架在多中心研究中的构建
9. 可解释AI在DXA影像诊断决策支持中的应用
10. DXA影像时间序列分析与骨质流失进展预测

### 方向11-15：应用拓展创新类
11. 基于生成对抗网络的DXA影像超分辨率重建
12. DXA影像中腹主动脉钙化的AI自动识别与量化
13. 基于强化学习的DXA扫描优化协议智能推荐
14. DXA影像在肌肉减少症早期诊断中的AI应用
15. 基于注意力机制的DXA影像关键区域自动定位

### 方向16-20：前沿技术融合类
16. DXA影像质量控制的深度学习自动评估系统
17. 基于迁移学习的小样本DXA影像疾病诊断
18. DXA影像与基因组数据融合的精准医学预测模型
19. 边缘计算环境下的DXA影像实时分析与诊断
20. 基于对比学习的DXA影像疾病表型识别与分类

## 每个研究方向的10个子章节结构
1. **研究背景** (300字)
2. **立论依据与核心假说** (250字)
3. **研究内容与AI/ML策略** (400字)
4. **研究目标** (200字)
5. **拟解决的关键科学问题** (250字)
6. **研究方案** (400字)
7. **可行性分析** (300字)
8. **创新性与颠覆性潜力** (400字)
9. **预期时间表与成果** (200字)
10. **参考文献** (50字，8-12篇文献)

请开始生成所有20个研究方向的完整内容。
"""
    
    def _get_section_content_requirements(self, section_id: str) -> str:
        """获取各章节的具体内容要求"""
        requirements = {
            "summary": """
### 执行摘要内容要求
1. **研究背景概述** (600字)
   - DXA技术的现状和局限性
   - AI在医学影像领域的发展机遇
   - 全身健康预测的临床需求

2. **核心发现与创新点** (800字)
   - 20个研究方向的创新价值概述
   - 技术突破点和应用前景
   - 对现有技术的颠覆性改进

3. **预期影响与价值** (600字)
   - 科学价值：推动理论突破
   - 技术价值：形成核心技术体系
   - 社会价值：提升医疗诊断水平
   - 经济价值：创造产业机遇

4. **实施建议** (500字)
   - 优先级建议和阶段性规划
   - 资源配置和技术路线建议
""",
            "introduction": """
### 前言与研究背景内容要求
1. **技术发展背景** (1500字)
   - DXA技术的发展历程和技术原理
   - AI技术在医学影像的演进过程
   - 跨领域技术融合的发展趋势

2. **临床需求分析** (1500字)
   - 骨质疏松症的全球流行病学现状
   - 现有诊断方法的局限性分析
   - 全身健康预测的迫切需求

3. **技术机遇窗口** (1000字)
   - 深度学习技术的成熟契机
   - 医疗大数据的积累优势
   - 计算能力提升带来的可能性

4. **研究价值与意义** (500字)
   - 填补技术空白的重要性
   - 推动精准医疗的战略意义
""",
            "current_status": """
### 领域现状与趋势分析内容要求
1. **技术发展现状** (1800字)
   - 当前DXA影像分析技术水平
   - AI在骨科影像学的应用现状
   - 主流算法和模型的性能分析

2. **应用领域现状** (1800字)
   - 骨质疏松诊断的临床实践
   - 骨折风险评估工具的应用
   - 全身健康预测的探索进展

3. **存在问题与挑战** (1600字)
   - 技术局限性和瓶颈分析
   - 数据质量和标准化问题
   - 临床转化面临的障碍

4. **发展趋势预测** (800字)
   - 未来5-10年的技术发展方向
   - 新兴技术的应用前景
   - 产业发展机遇分析
""",
            "innovation_analysis": """
### 创新突破点综合分析内容要求
1. **技术创新汇总** (800字)
   - 算法创新：新型深度学习架构
   - 方法创新：多模态融合技术
   - 应用创新：新的临床应用场景

2. **理论创新汇总** (600字)
   - 科学假说的创新性
   - 跨学科理论整合
   - 新的生物医学机制发现

3. **应用创新汇总** (600字)
   - 诊断流程的革新
   - 预防医学的新模式
   - 个性化医疗的实现路径

4. **颠覆性影响分析** (500字)
   - 对传统诊断模式的冲击
   - 对医疗体系的重塑作用
   - 对产业生态的变革影响
""",
            "implementation": """
### 实施建议与优先级分析内容要求
1. **短期优先方向** (500字)
   - 1-2年内可实施的研究方向
   - 技术成熟度和资源需求分析
   - 快速见效的应用领域

2. **中期发展方向** (500字)
   - 3-5年的战略规划方向
   - 需要突破的关键技术
   - 产业化应用的准备

3. **长期前瞻方向** (500字)
   - 5-10年的前瞻性布局
   - 基础理论研究的重点
   - 颠覆性技术的孵化

4. **资源配置建议** (500字)
   - 人才队伍建设建议
   - 研发投入分配策略
   - 合作网络构建方案
""",
            "conclusion": """
### 总结与展望内容要求
1. **主要发现与贡献** (600字)
   - 报告的核心发现总结
   - 对学术界的贡献价值
   - 对产业界的指导意义

2. **领域发展趋势** (500字)
   - 基于分析的发展趋势判断
   - 技术演进的关键节点
   - 应用拓展的预期路径

3. **未来研究机遇** (400字)
   - 最具潜力的突破方向
   - 跨领域合作的机会
   - 新兴技术的融合点
""",
            "references": """
### 参考文献汇总内容要求
1. **文献分类整理** (400字)
   - 按研究领域分类
   - 按重要性等级排序
   - 按发表时间归档

2. **关键文献解读** (400字)
   - 核心理论文献的贡献
   - 重要实证研究的发现
   - 前沿技术文献的价值

3. **文献数据库** (200字)
   - 完整的参考文献列表
   - 包含DOI和影响因子
   - 按标准格式编排
"""
        }
        
        return requirements.get(section_id, "请根据章节标题生成相应内容。")
    
    def _get_report_context(self) -> str:
        """获取报告的整体上下文信息"""
        return f"""
## 报告概览
- **报告主题**：基于人工智能与桡骨DXA影像的全身健康状态预测研究
- **报告目标**：提出20个颠覆性创新研究方向，推动DXA影像AI应用的革命性发展
- **预期字数**：约7.5万字（含20个研究方向的5.5万字）
- **当前进度**：第{self.current_batch + 1}/8个批次

## 已完成章节
{self._get_completed_sections_summary()}

## 核心创新主线
1. **技术突破**：从单一骨密度测量到全身健康预测的范式转变
2. **方法创新**：多模态AI融合、联邦学习、可解释AI等前沿技术应用
3. **应用拓展**：从骨科诊断扩展到心血管、代谢、神经系统等全身疾病预测
4. **临床转化**：建立标准化、智能化的诊断决策支持系统
"""
    
    def _get_completed_sections_summary(self) -> str:
        """获取已完成章节的摘要"""
        if not self.generated_sections:
            return "暂无已完成章节"
        
        summary = []
        for section_id, content in self.generated_sections.items():
            section = self.report_sections[section_id]
            summary.append(f"✅ {section.title}：{len(content)}字")
        
        return "\n".join(summary) if summary else "暂无已完成章节"
    
    def save_section(self, content: str) -> Dict[str, Any]:
        """保存当前批次的章节内容"""
        section_keys = list(self.report_sections.keys())
        
        if self.current_batch >= len(section_keys):
            raise ValueError("所有批次已完成")
        
        section_key = section_keys[self.current_batch]
        section = self.report_sections[section_key]
        
        # 保存内容
        section.content = content
        section.generated = True
        section.generation_time = datetime.now()
        self.generated_sections[section_key] = content
        
        # 保存到文件
        section_file = self.session_dir / f"section_{self.current_batch + 1:02d}_{section_key}.md"
        with open(section_file, 'w', encoding='utf-8') as f:
            f.write(f"# {section.title}\n\n")
            f.write(content)
        
        # 更新批次计数
        self.current_batch += 1
        
        # 统计信息
        result = {
            "success": True,
            "section_id": section_key,
            "section_title": section.title,
            "section_file": str(section_file),
            "word_count": len(content),
            "target_words": section.target_words,
            "completion_rate": len(content) / section.target_words,
            "batch_number": self.current_batch,
            "total_batches": len(self.report_sections),
            "overall_progress": self.current_batch / len(self.report_sections)
        }
        
        logger.info(f"保存章节: {section.title}, {len(content)}字")
        return result
    
    def is_complete(self) -> bool:
        """检查是否所有批次都已完成"""
        return self.current_batch >= len(self.report_sections)
    
    def generate_final_report(self) -> Dict[str, Any]:
        """生成最终的完整报告"""
        if not self.is_complete():
            raise ValueError(f"报告未完成，当前进度: {self.current_batch}/{len(self.report_sections)}")
        
        # 创建完整报告内容
        final_content = self._create_final_report_content()
        
        # 保存最终报告
        final_file = self.session_dir / f"{self.report_name}_完整报告_{self.timestamp}.md"
        with open(final_file, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        # 生成HTML版本
        html_content = self._create_html_report(final_content)
        html_file = self.session_dir / f"{self.report_name}_完整报告_{self.timestamp}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 生成统计信息
        stats = self._generate_report_stats()
        
        # 保存统计信息
        stats_file = self.session_dir / "report_stats.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
        
        result = {
            "success": True,
            "final_markdown_file": str(final_file),
            "final_html_file": str(html_file),
            "stats_file": str(stats_file),
            "stats": stats,
            "session_dir": str(self.session_dir)
        }
        
        logger.info(f"完整报告生成完成: {final_file}")
        return result
    
    def _create_final_report_content(self) -> str:
        """创建最终报告的完整内容"""
        content = []
        
        # 报告标题和元信息
        content.append(f"# 基于人工智能与桡骨DXA影像的全身健康状态预测研究报告")
        content.append("")
        content.append(f"**报告生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        content.append(f"**报告版本**: V1.0")
        content.append(f"**生成会话**: {self.timestamp}")
        content.append("")
        content.append("---")
        content.append("")
        
        # 生成目录
        content.append("## 📋 目录")
        content.append("")
        for i, (section_key, section) in enumerate(self.report_sections.items(), 1):
            content.append(f"{i}. [{section.title}](#{section_key})")
        content.append("")
        content.append("---")
        content.append("")
        
        # 添加各章节内容
        for i, (section_key, section) in enumerate(self.report_sections.items(), 1):
            content.append(f"## {i}. 📖 {section.title} {{#{section_key}}}")
            content.append("")
            content.append(section.content)
            content.append("")
            content.append("---")
            content.append("")
        
        # 添加报告统计信息
        stats = self._generate_report_stats()
        content.append("## 📊 报告统计信息")
        content.append("")
        content.append(f"- **总字数**: {stats['total_words']:,}字")
        content.append(f"- **章节数量**: {stats['total_sections']}个")
        content.append(f"- **研究方向**: 20个完整方向")
        content.append(f"- **生成时间**: {stats['generation_time']}")
        content.append(f"- **平均章节字数**: {stats['avg_words_per_section']:,}字")
        content.append("")
        
        return "\n".join(content)
    
    def _create_html_report(self, markdown_content: str) -> str:
        """创建HTML格式的报告"""
        # 简单的HTML模板
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DXA影像AI研究完整报告</title>
    <style>
        body {{ font-family: 'Microsoft YaHei', sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .meta-info {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .toc {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .toc ul {{ list-style-type: none; padding: 0; }}
        .toc li {{ margin: 5px 0; }}
        .toc a {{ text-decoration: none; color: #3498db; }}
        .toc a:hover {{ text-decoration: underline; }}
        .section {{ margin: 40px 0; padding: 20px 0; border-top: 1px solid #ecf0f1; }}
        .stats {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #3498db; margin: 0; padding: 0 20px; color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="container">
        {self._markdown_to_html_simple(markdown_content)}
    </div>
</body>
</html>
"""
        return html_template
    
    def _markdown_to_html_simple(self, markdown_content: str) -> str:
        """简单的Markdown到HTML转换"""
        # 这是一个简化版本，实际项目中应该使用专业的Markdown解析器
        html = markdown_content
        
        # 基本转换
        html = html.replace('**', '<strong>', 1).replace('**', '</strong>', 1)
        html = html.replace('*', '<em>', 1).replace('*', '</em>', 1)
        html = html.replace('\n\n', '</p><p>')
        html = html.replace('\n', '<br>')
        html = f"<p>{html}</p>"
        
        return html
    
    def _generate_report_stats(self) -> Dict[str, Any]:
        """生成报告统计信息"""
        total_words = sum(len(section.content) for section in self.report_sections.values())
        
        section_stats = []
        for section_key, section in self.report_sections.items():
            section_stats.append({
                "section_id": section_key,
                "title": section.title,
                "target_words": section.target_words,
                "actual_words": len(section.content),
                "completion_rate": len(section.content) / section.target_words if section.target_words > 0 else 0,
                "generated": section.generated,
                "generation_time": section.generation_time
            })
        
        return {
            "report_name": self.report_name,
            "total_words": total_words,
            "total_sections": len(self.report_sections),
            "avg_words_per_section": total_words // len(self.report_sections),
            "generation_time": datetime.now().isoformat(),
            "session_timestamp": self.timestamp,
            "session_dir": str(self.session_dir),
            "section_stats": section_stats,
            "completion_status": "completed" if self.is_complete() else "in_progress"
        }
    
    def get_progress(self) -> Dict[str, Any]:
        """获取当前进度信息"""
        return {
            "report_name": self.report_name,
            "current_batch": self.current_batch,
            "total_batches": len(self.report_sections),
            "progress_percentage": (self.current_batch / len(self.report_sections)) * 100,
            "completed_sections": list(self.generated_sections.keys()),
            "next_section": list(self.report_sections.keys())[self.current_batch] if self.current_batch < len(self.report_sections) else None,
            "is_complete": self.is_complete()
        } 
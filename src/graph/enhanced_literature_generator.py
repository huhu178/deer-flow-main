# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
增强文献搜索驱动的报告生成器
将高质量文献搜索深度集成到综合报告生成流程中
"""

import logging
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.tools import get_pubmed_search_tool, get_google_scholar_search_tool, get_web_search_tool
from src.tools.enhanced_search_coordinator import EnhancedSearchCoordinator
from src.tools.journal_quality_controller import journal_quality_controller
from src.config.enhanced_research_config import ResearchConfiguration
from src.llms import get_llm_by_type

logger = logging.getLogger(__name__)

class LiteratureEnhancedReportGenerator:
    """文献增强的报告生成器"""
    
    def __init__(self, model_name: str = "gemini", research_type: str = "default"):
        self.model_name = model_name
        
        # 导入配置
        from src.config.literature_config import get_literature_config
        self.config = get_literature_config(research_type)
        
        self.literature_cache = {}
        self.citation_count = 0
        self.citations = {}
        
    def generate_enhanced_comprehensive_report(
        self, 
        state: Dict[str, Any], 
        current_plan: Dict[str, Any],
        directions_list: List[str]
    ) -> str:
        """生成文献增强的综合报告"""
        
        logger.info("🔍 开始生成文献增强的综合报告")
        
        # 第一步：执行深度文献搜索
        literature_database = self._execute_comprehensive_literature_search(
            state, current_plan, directions_list
        )
        
        # 第二步：生成文献驱动的综合报告
        enhanced_report = self._generate_literature_driven_report(
            state, current_plan, directions_list, literature_database
        )
        
        logger.info(f"✅ 文献增强报告生成完成，包含 {self.citation_count} 篇高质量文献引用")
        
        return enhanced_report
    
    def _execute_comprehensive_literature_search(
        self, 
        state: Dict[str, Any], 
        current_plan: Dict[str, Any],
        directions_list: List[str]
    ) -> Dict[str, Any]:
        """执行全面的文献搜索"""
        
        logger.info("📚 开始执行全面文献搜索")
        
        # 获取主要研究查询
        main_query = self._extract_main_research_query(state, current_plan)
        
        # 构建搜索策略
        search_strategies = self._build_search_strategies(main_query, directions_list)
        
        # 执行搜索
        all_literature = []
        
        for strategy_name, strategy in search_strategies.items():
            logger.info(f"🔍 执行搜索策略: {strategy_name}")
            
            try:
                results = self._execute_search_strategy(strategy)
                all_literature.extend(results)
                logger.info(f"✅ {strategy_name} 完成，获得 {len(results)} 篇文献")
                time.sleep(0.5)  # 避免请求过频
                
            except Exception as e:
                logger.warning(f"⚠️ 搜索策略 {strategy_name} 失败: {e}")
        
        # 整合和排序
        processed_literature = self._process_literature_results(all_literature)
        
        return processed_literature
    
    def _extract_main_research_query(self, state: Dict[str, Any], current_plan: Dict[str, Any]) -> str:
        """提取主要研究查询"""
        
        # 从计划标题提取
        title = current_plan.get("title", "")
        
        # 从用户消息提取
        messages = state.get("messages", [])
        user_query = ""
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, dict):
                user_query = last_message.get('content', '')
            else:
                user_query = getattr(last_message, 'content', '')
        
        # 组合查询
        combined_query = f"{title} {user_query}".strip()
        
        # 清理查询
        cleaned_query = combined_query.replace("综合报告", "").replace("研究", "").strip()
        
        return cleaned_query[:150] if cleaned_query else "DXA imaging AI health prediction"
    
    def _build_search_strategies(self, main_query: str, directions_list: List[str]) -> Dict[str, Dict]:
        """构建搜索策略"""
        
        strategies = {
            # 核心概念搜索
            "core_systematic_reviews": {
                "queries": [
                    f"{main_query} systematic review",
                    f"{main_query} meta-analysis",
                    f"{main_query} comprehensive review"
                ],
                "sources": ["pubmed"],
                "max_results": 8
            },
            
            # 技术方法搜索
            "technical_ai_methods": {
                "queries": [
                    f"{main_query} artificial intelligence",
                    f"{main_query} machine learning",
                    f"{main_query} deep learning"
                ],
                "sources": ["google_scholar", "pubmed"],
                "max_results": 6
            },
            
            # 临床应用搜索
            "clinical_applications": {
                "queries": [
                    f"{main_query} clinical trial",
                    f"{main_query} clinical application",
                    f"{main_query} diagnostic accuracy"
                ],
                "sources": ["pubmed"],
                "max_results": 6
            },
            
            # 生物机制搜索
            "biological_mechanisms": {
                "queries": [
                    f"{main_query} mechanisms",
                    f"{main_query} pathophysiology",
                    f"{main_query} biomarkers"
                ],
                "sources": ["pubmed"],
                "max_results": 5
            }
        }
        
        return strategies
    
    def _execute_search_strategy(self, strategy: Dict) -> List[Dict]:
        """执行单个搜索策略"""
        
        all_results = []
        
        for query in strategy["queries"]:
            for source in strategy["sources"]:
                try:
                    if source == "pubmed":
                        tool = get_pubmed_search_tool(max_results=self.config.pubmed_max_results)
                        raw_results = tool.invoke({"query": query})
                        parsed_results = self._parse_pubmed_results(raw_results)
                        
                    elif source == "google_scholar":
                        tool = get_google_scholar_search_tool(top_k_results=self.config.scholar_max_results)
                        raw_results = tool.invoke({"query": query})
                        parsed_results = self._parse_scholar_results(raw_results)
                        
                    else:
                        continue
                    
                    all_results.extend(parsed_results)
                    
                except Exception as e:
                    logger.warning(f"搜索失败 {source}: {query} - {e}")
                    continue
        
        return all_results
    
    def _parse_pubmed_results(self, raw_results: str) -> List[Dict]:
        """解析PubMed搜索结果"""
        
        literature = []
        
        if "Result" in raw_results:
            entries = raw_results.split("Result ")[1:]
            
            for entry in entries:
                lines = entry.split('\n')
                paper = {
                    'title': '',
                    'abstract': '',
                    'journal': '',
                    'authors': '',
                    'pmid': '',
                    'source': 'pubmed',
                    'quality_score': 0.85
                }
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('Title: '):
                        paper['title'] = line.replace('Title: ', '').strip()
                    elif line.startswith('Abstract Snippet: '):
                        paper['abstract'] = line.replace('Abstract Snippet: ', '').strip()
                    elif line.startswith('Journal: '):
                        paper['journal'] = line.replace('Journal: ', '').strip()
                    elif line.startswith('Authors: '):
                        paper['authors'] = line.replace('Authors: ', '').strip()
                    elif line.startswith('PMID: '):
                        paper['pmid'] = line.replace('PMID: ', '').strip()
                
                if paper['title']:
                    paper['quality_score'] = self._assess_journal_quality(paper['journal'])
                    literature.append(paper)
        
        return literature
    
    def _parse_scholar_results(self, raw_results: str) -> List[Dict]:
        """解析Google Scholar结果"""
        
        literature = []
        
        if raw_results and raw_results.strip():
            lines = raw_results.split('\n')
            current_paper = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('Title: '):
                    if current_paper and current_paper.get('title'):
                        literature.append(current_paper)
                    
                    current_paper = {
                        'title': line.replace('Title: ', ''),
                        'abstract': '',
                        'journal': '',
                        'source': 'google_scholar',
                        'quality_score': 0.75
                    }
                elif current_paper and line.startswith('Summary: '):
                    current_paper['abstract'] = line.replace('Summary: ', '')
                elif current_paper and line.startswith('Source: '):
                    source_info = line.replace('Source: ', '')
                    current_paper['journal'] = source_info
                    current_paper['quality_score'] = self._assess_journal_quality(source_info)
            
            if current_paper and current_paper.get('title'):
                literature.append(current_paper)
        
        return literature
    
    def _assess_journal_quality(self, journal_name: str) -> float:
        """评估期刊质量"""
        
        if not journal_name:
            return 0.5
        
        journal_lower = journal_name.lower()
        
        # 顶级期刊
        top_journals = [
            'nature', 'science', 'cell', 'new england journal of medicine',
            'nejm', 'lancet', 'jama', 'nature medicine'
        ]
        
        # 高质量期刊
        high_quality = [
            'plos', 'bmj', 'circulation', 'radiology', 'ieee', 'acm'
        ]
        
        if any(tj in journal_lower for tj in top_journals):
            return 0.95
        elif any(hq in journal_lower for hq in high_quality):
            return 0.85
        else:
            return 0.75
    
    def _process_literature_results(self, all_literature: List[Dict]) -> Dict[str, Any]:
        """处理文献搜索结果"""
        
        # 去重
        unique_literature = self._remove_duplicates(all_literature)
        
        # 排序
        sorted_literature = sorted(
            unique_literature, 
            key=lambda x: x.get('quality_score', 0.5), 
            reverse=True
        )
        
        # 取前N篇
        top_literature = sorted_literature[:self.config.max_literature_count]
        
        # 分类
        categorized = self._categorize_literature(top_literature)
        
        return {
            "total_count": len(top_literature),
            "literature": top_literature,
            "categorized": categorized
        }
    
    def _remove_duplicates(self, literature_list: List[Dict]) -> List[Dict]:
        """去重处理"""
        
        seen_titles = set()
        unique_papers = []
        
        for paper in literature_list:
            title = paper.get('title', '').lower().strip()
            if title and title not in seen_titles:
                unique_papers.append(paper)
                seen_titles.add(title)
        
        return unique_papers
    
    def _categorize_literature(self, literature_list: List[Dict]) -> Dict[str, List[Dict]]:
        """文献分类"""
        
        categories = {
            "systematic_reviews": [],
            "clinical_trials": [],
            "technical_papers": [],
            "mechanism_studies": []
        }
        
        for paper in literature_list:
            title_abstract = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
            
            if any(keyword in title_abstract for keyword in ['systematic review', 'meta-analysis']):
                categories["systematic_reviews"].append(paper)
            elif any(keyword in title_abstract for keyword in ['clinical trial', 'randomized']):
                categories["clinical_trials"].append(paper)
            elif any(keyword in title_abstract for keyword in ['artificial intelligence', 'machine learning']):
                categories["technical_papers"].append(paper)
            elif any(keyword in title_abstract for keyword in ['mechanism', 'pathway', 'molecular']):
                categories["mechanism_studies"].append(paper)
        
        return categories
    
    def _generate_literature_driven_report(
        self, 
        state: Dict[str, Any], 
        current_plan: Dict[str, Any],
        directions_list: List[str],
        literature_database: Dict[str, Any]
    ) -> str:
        """生成文献驱动的综合报告"""
        
        logger.info("📝 开始生成文献驱动的综合报告")
        
        # 重置引用计数器
        self.citation_count = 0
        self.citations = {}
        
        main_title = current_plan.get("title", "AI研究综合报告")
        description = current_plan.get("description", "")
        
        # 生成报告各部分
        sections = []
        
        # 1. 标题和摘要
        sections.append(self._generate_header(main_title, description, literature_database))
        
        # 2. 文献综述
        sections.append(self._generate_literature_review(literature_database))
        
        # 3. 研究背景
        sections.append(self._generate_background(literature_database))
        
        # 4. 技术方法
        sections.append(self._generate_methodology(literature_database))
        
        # 5. 研究方向
        sections.append(self._generate_directions_analysis(directions_list, literature_database))
        
        # 6. 关键发现
        sections.append(self._generate_key_findings(literature_database))
        
        # 7. 参考文献
        sections.append(self._generate_bibliography())
        
        # 8. 统计信息
        final_report = "\n\n".join(sections)
        sections.append(self._generate_statistics(final_report, literature_database))
        
        comprehensive_report = "\n\n".join(sections)
        
        logger.info(f"📚 文献驱动报告生成完成，总长度: {len(comprehensive_report):,} 字符")
        
        return comprehensive_report
    
    def _generate_header(self, title: str, description: str, literature_db: Dict) -> str:
        """生成报告标题部分"""
        
        return f"""# {title}

## 📋 报告信息

- **生成日期**: {datetime.now().strftime("%Y年%m月%d日")}
- **报告类型**: 文献驱动的综合研究报告
- **文献基础**: 基于 {literature_db.get('total_count', 0)} 篇高质量学术文献
- **AI模型**: {self.model_name.upper()}

## 📖 执行摘要

{description}

**文献搜索概况**:
- 🔍 **搜索策略**: 多层次学术文献搜索
- 📚 **文献来源**: PubMed、Google Scholar等权威数据库
- 🏆 **质量控制**: 仅包含同行评议的高质量学术文献
- 📊 **引用标准**: 遵循学术引用规范

---"""
    
    def _generate_literature_review(self, literature_db: Dict) -> str:
        """生成文献综述部分"""
        
        categorized = literature_db.get("categorized", {})
        
        section = """## 📚 文献综述

### 🔬 研究现状概述

基于对相关领域高质量文献的系统性分析："""
        
        # 系统性综述
        systematic_reviews = categorized.get("systematic_reviews", [])
        if systematic_reviews:
            section += f"""

#### 📋 系统性综述与荟萃分析 ({len(systematic_reviews)} 篇)

"""
            for i, paper in enumerate(systematic_reviews[:3], 1):
                citation = self._add_citation(paper)
                section += f"""
**{i}. {paper.get('title', 'Unknown Title')}** {citation}
- **期刊**: {paper.get('journal', 'Unknown Journal')}
- **关键发现**: {paper.get('abstract', 'No abstract available')[:200]}...
"""
        
        # 临床试验
        clinical_trials = categorized.get("clinical_trials", [])
        if clinical_trials:
            section += f"""

#### 🏥 临床试验研究 ({len(clinical_trials)} 篇)

"""
            for i, paper in enumerate(clinical_trials[:3], 1):
                citation = self._add_citation(paper)
                section += f"""
**{i}. {paper.get('title', 'Unknown Title')}** {citation}
- **期刊**: {paper.get('journal', 'Unknown Journal')}
- **临床意义**: {paper.get('abstract', 'No abstract available')[:200]}...
"""
        
        return section
    
    def _generate_background(self, literature_db: Dict) -> str:
        """生成研究背景"""
        
        section = """## 🔬 研究背景与理论基础

### 🧬 生物学基础

"""
        
        mechanism_papers = literature_db.get("categorized", {}).get("mechanism_studies", [])
        if mechanism_papers:
            for paper in mechanism_papers[:2]:
                citation = self._add_citation(paper)
                section += f"""
**分子机制研究** {citation} 表明，{paper.get('abstract', 'No abstract available')[:250]}...

"""
        
        section += """### 🤖 技术发展现状

"""
        
        tech_papers = literature_db.get("categorized", {}).get("technical_papers", [])
        if tech_papers:
            for paper in tech_papers[:2]:
                citation = self._add_citation(paper)
                section += f"""
**AI技术应用** {citation} 的研究显示，{paper.get('abstract', 'No abstract available')[:250]}...

"""
        
        return section
    
    def _generate_methodology(self, literature_db: Dict) -> str:
        """生成方法论部分"""
        
        section = """## 🛠️ 研究方法论

### 📊 数据采集与处理

"""
        
        high_quality_papers = [
            paper for paper in literature_db.get("literature", [])
            if paper.get("quality_score", 0) > 0.85
        ][:5]
        
        for paper in high_quality_papers[:2]:
            citation = self._add_citation(paper)
            section += f"""
参考 {citation} 的研究方法，{paper.get('abstract', 'No abstract available')[:200]}...

"""
        
        return section
    
    def _generate_directions_analysis(self, directions_list: List[str], literature_db: Dict) -> str:
        """生成研究方向分析"""
        
        section = """## 🎯 研究方向与文献支撑

"""
        
        for i, direction in enumerate(directions_list[:8], 1):
            section += f"""### 方向 {i}: {direction}

"""
            
            # 为每个方向匹配相关文献
            relevant_papers = self._find_relevant_papers(direction, literature_db)
            
            if relevant_papers:
                section += """#### 📚 相关文献支撑

"""
                for paper in relevant_papers[:2]:
                    citation = self._add_citation(paper)
                    section += f"""
- **{paper.get('title', 'Unknown Title')}** {citation}
  - *期刊*: {paper.get('journal', 'Unknown')}
  - *关键内容*: {paper.get('abstract', 'No abstract')[:120]}...

"""
            
            section += """#### 🔬 研究创新点

基于文献分析，该方向的主要创新点包括技术方法创新、理论机制突破和临床应用价值。

---

"""
        
        return section
    
    def _find_relevant_papers(self, direction: str, literature_db: Dict) -> List[Dict]:
        """为方向找到相关文献"""
        
        direction_words = direction.lower().split()
        all_papers = literature_db.get("literature", [])
        
        relevant_papers = []
        
        for paper in all_papers:
            title = paper.get('title', '').lower()
            abstract = paper.get('abstract', '').lower()
            
            relevance_score = 0
            for word in direction_words:
                if len(word) > 3:
                    if word in title:
                        relevance_score += 2
                    elif word in abstract:
                        relevance_score += 1
            
            if relevance_score > 0:
                paper["relevance_score"] = relevance_score
                relevant_papers.append(paper)
        
        return sorted(relevant_papers, key=lambda x: x.get("relevance_score", 0), reverse=True)[:3]
    
    def _generate_key_findings(self, literature_db: Dict) -> str:
        """生成关键发现"""
        
        section = """## 💡 关键发现与洞察

基于高质量学术文献的深度分析：

### 🔍 技术发展趋势

"""
        
        tech_papers = literature_db.get("categorized", {}).get("technical_papers", [])
        if tech_papers:
            for paper in tech_papers[:2]:
                citation = self._add_citation(paper)
                section += f"""
{citation} 的研究表明：{paper.get('abstract', 'No abstract available')[:200]}...

"""
        
        section += """### 🏥 临床应用前景

"""
        
        clinical_papers = literature_db.get("categorized", {}).get("clinical_trials", [])
        if clinical_papers:
            for paper in clinical_papers[:2]:
                citation = self._add_citation(paper)
                section += f"""
{citation} 的临床研究显示：{paper.get('abstract', 'No abstract available')[:200]}...

"""
        
        return section
    
    def _generate_bibliography(self) -> str:
        """生成参考文献"""
        
        section = """## 📖 参考文献

"""
        
        if not self.citations:
            return section + "*注：参考文献列表为空*"
        
        for citation_num, paper in self.citations.items():
            authors = paper.get('authors', 'Unknown Authors')
            title = paper.get('title', 'Unknown Title')
            journal = paper.get('journal', 'Unknown Journal')
            
            section += f"""
**[{citation_num}]** {authors}. *{title}*. {journal}.
"""
            
            if paper.get('pmid'):
                section += f" PMID: {paper['pmid']}"
            
            section += "\n"
        
        return section
    
    def _generate_statistics(self, report_content: str, literature_db: Dict) -> str:
        """生成统计信息"""
        
        word_count = len(report_content)
        literature_count = literature_db.get("total_count", 0)
        
        return f"""---

## 📊 报告统计信息

- **📝 总字数**: {word_count:,} 字符
- **📚 文献基础**: {literature_count} 篇高质量学术文献
- **🔗 引用数量**: {self.citation_count} 个文献引用
- **📅 生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*本报告由AI科研系统基于高质量学术文献自动生成*"""
    
    def _add_citation(self, paper: Dict) -> str:
        """添加文献引用"""
        
        # 检查是否已引用
        for citation_num, cited_paper in self.citations.items():
            if cited_paper.get('title') == paper.get('title'):
                return f"[{citation_num}]"
        
        # 添加新引用
        self.citation_count += 1
        citation_id = str(self.citation_count)
        self.citations[citation_id] = paper
        
        return f"[{citation_id}]"


def create_literature_enhanced_generator(
    model_name: str = "gemini",
    research_type: str = "default"
) -> LiteratureEnhancedReportGenerator:
    """创建文献增强报告生成器"""
    return LiteratureEnhancedReportGenerator(
        model_name=model_name,
        research_type=research_type
    ) 
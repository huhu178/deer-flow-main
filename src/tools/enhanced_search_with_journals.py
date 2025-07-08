# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
增强搜索接口 - 集成期刊质量控制
支持指定高质量期刊的智能搜索和结果过滤
"""

import logging
from typing import List, Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .search import (
    get_web_search_tool, 
    get_pubmed_search_tool, 
    get_google_scholar_search_tool
)
from .journal_quality_controller import (
    journal_quality_controller,
    JournalTier,
    JournalInfo,
    get_recommended_journals,
    create_journal_focused_search_query
)

logger = logging.getLogger(__name__)

class JournalAwareSearchEngine:
    """支持期刊质量控制的搜索引擎"""
    
    def __init__(self):
        self.quality_controller = journal_quality_controller
        
    def search_by_journal_quality(
        self, 
        query: str,
        target_tier: str = "high",          # "top", "high", "mid", "all"
        target_field: str = None,           # "ai_ml", "medical_imaging", "bone_health"
        specific_journals: List[str] = None, # 指定期刊名称列表
        max_results: int = 20,
        engines: List[str] = None           # ["google_scholar", "pubmed", "general"]
    ) -> Dict[str, Any]:
        """
        基于期刊质量进行搜索
        
        Args:
            query: 搜索查询
            target_tier: 目标期刊等级
            target_field: 目标研究领域  
            specific_journals: 指定的期刊名称列表
            max_results: 最大结果数
            engines: 使用的搜索引擎
            
        Returns:
            包含高质量文献的搜索结果
        """
        
        logger.info(f"🔍 开始期刊质量导向搜索: {query}")
        logger.info(f"📊 搜索参数: tier={target_tier}, field={target_field}, journals={specific_journals}")
        
        # 1. 确定目标期刊
        if specific_journals:
            # 使用用户指定的期刊
            target_journals = []
            for journal_name in specific_journals:
                journal_key = journal_name.lower().replace(' ', '_').replace('-', '_')
                journal_info = self.quality_controller.journal_database.get(journal_key)
                if journal_info:
                    target_journals.append(journal_info)
                else:
                    logger.warning(f"⚠️ 未找到期刊信息: {journal_name}")
        else:
            # 根据查询自动推荐期刊
            if target_field:
                tier_map = {
                    "top": JournalTier.TOP_TIER,
                    "high": JournalTier.HIGH_TIER, 
                    "mid": JournalTier.MID_TIER,
                    "all": JournalTier.EMERGING
                }
                min_tier = tier_map.get(target_tier, JournalTier.HIGH_TIER)
                target_journals = self.quality_controller.get_journals_by_field(target_field, min_tier)[:5]
            else:
                target_journals = get_recommended_journals(query, tier=target_tier)[:5]
        
        if not target_journals:
            logger.warning("⚠️ 未找到目标期刊，使用通用搜索")
            return self._fallback_search(query, max_results)
        
        logger.info(f"🎯 选定目标期刊: {[j.name for j in target_journals]}")
        
        # 2. 生成期刊特定的搜索查询
        search_strategy = self.quality_controller.get_search_strategy_for_journals(target_journals, query)
        
        # 3. 执行多引擎搜索
        if not engines:
            engines = ["google_scholar", "pubmed", "general"]
        
        all_results = []
        search_tasks = []
        
        # 为每个期刊和引擎组合创建搜索任务
        for journal in target_journals[:3]:  # 限制为前3个期刊，避免查询过多
            journal_queries = search_strategy['multi_engine_queries'].get(journal.name, {})
            
            for engine in engines:
                if engine in journal_queries:
                    search_tasks.append({
                        'engine': engine,
                        'journal': journal.name,
                        'query': journal_queries[engine],
                        'journal_info': journal
                    })
        
        # 并行执行搜索
        results_by_engine = self._execute_parallel_search(search_tasks, max_results)
        
        # 4. 结果质量过滤和排序
        tier_map = {
            "top": JournalTier.TOP_TIER,
            "high": JournalTier.HIGH_TIER,
            "mid": JournalTier.MID_TIER, 
            "all": JournalTier.EMERGING
        }
        min_tier = tier_map.get(target_tier, JournalTier.HIGH_TIER)
        
        filtered_results = self.quality_controller.filter_results_by_journal_quality(
            results_by_engine, min_tier
        )
        
        # 5. 添加期刊匹配信息
        enhanced_results = self._enhance_results_with_journal_info(filtered_results, target_journals)
        
        return {
            'query': query,
            'target_journals': [{'name': j.name, 'impact_factor': j.impact_factor} for j in target_journals],
            'total_results': len(enhanced_results),
            'results': enhanced_results[:max_results],
            'search_strategy': search_strategy
        }
    
    def search_top_tier_only(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """仅搜索顶级期刊 (Nature, Science, Cell等)"""
        
        logger.info(f"🏆 执行顶级期刊专项搜索: {query}")
        
        # 获取顶级期刊
        top_journals = self.quality_controller.get_top_journals(limit=5)
        
        return self.search_by_journal_quality(
            query=query,
            target_tier="top",
            specific_journals=[j.name for j in top_journals],
            max_results=max_results,
            engines=["google_scholar", "general"]  # 顶级期刊主要用Google Scholar
        )
    
    def search_by_field_experts(self, query: str, field: str, max_results: int = 15) -> Dict[str, Any]:
        """按专业领域搜索，使用该领域的权威期刊"""
        
        logger.info(f"🔬 执行领域专家搜索: {query} (领域: {field})")
        
        # 领域搜索引擎优化
        field_engine_map = {
            'medical_imaging': ["google_scholar", "pubmed"],
            'bone_health': ["pubmed", "google_scholar"],
            'ai_ml': ["google_scholar", "general"],
            'cardiovascular': ["pubmed", "google_scholar"]
        }
        
        engines = field_engine_map.get(field, ["google_scholar", "pubmed", "general"])
        
        return self.search_by_journal_quality(
            query=query,
            target_tier="high",
            target_field=field,
            max_results=max_results,
            engines=engines
        )
    
    def _execute_parallel_search(self, search_tasks: List[Dict], max_results: int) -> List[Dict]:
        """并行执行搜索任务"""
        
        all_results = []
        
        with ThreadPoolExecutor(max_workers=min(len(search_tasks), 4)) as executor:
            future_to_task = {}
            
            for task in search_tasks:
                try:
                    # 根据引擎类型创建搜索工具
                    if task['engine'] == 'google_scholar':
                        search_tool = get_google_scholar_search_tool()
                        future = executor.submit(search_tool.run, task['query'])
                    elif task['engine'] == 'pubmed':
                        search_tool = get_pubmed_search_tool()
                        future = executor.submit(search_tool.run, task['query'])
                    else:  # general/tavily
                        search_tool = get_web_search_tool(max_results // len(search_tasks))
                        future = executor.submit(search_tool.invoke, task['query'])
                    
                    future_to_task[future] = task
                    
                except Exception as e:
                    logger.error(f"❌ 搜索任务创建失败: {task['engine']} - {e}")
            
            # 收集结果
            for future in future_to_task:
                task = future_to_task[future]
                try:
                    raw_result = future.result(timeout=30)
                    
                    # 解析搜索结果
                    parsed_results = self._parse_search_result(raw_result, task)
                    all_results.extend(parsed_results)
                    
                    logger.info(f"✅ {task['engine']} 搜索完成: {len(parsed_results)} 个结果")
                    
                except Exception as e:
                    logger.warning(f"⚠️ {task['engine']} 搜索失败: {e}")
        
        return all_results
    
    def _parse_search_result(self, raw_result: Any, task: Dict) -> List[Dict]:
        """解析不同搜索引擎的结果格式"""
        
        parsed_results = []
        
        try:
            if task['engine'] == 'google_scholar':
                # Google Scholar 返回的是字符串格式
                if isinstance(raw_result, str) and raw_result.strip():
                    # 简单解析 Google Scholar 结果
                    lines = raw_result.split('\n')
                    current_paper = {}
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith('Title: '):
                            if current_paper:
                                parsed_results.append(current_paper)
                            current_paper = {
                                'title': line.replace('Title: ', ''),
                                'source': 'google_scholar',
                                'journal_source': task['journal'],
                                'content': ''
                            }
                        elif line.startswith('Authors: '):
                            current_paper['authors'] = line.replace('Authors: ', '')
                        elif line.startswith('Summary: '):
                            current_paper['content'] = line.replace('Summary: ', '')
                        elif line.startswith('URL: '):
                            current_paper['url'] = line.replace('URL: ', '')
                    
                    if current_paper:
                        parsed_results.append(current_paper)
            
            elif task['engine'] == 'pubmed':
                # PubMed 返回格式化的字符串
                if isinstance(raw_result, str) and 'Result' in raw_result:
                    # 解析 PubMed 结果
                    entries = raw_result.split('Result ')
                    for entry in entries[1:]:  # 跳过第一个空条目
                        result_dict = {
                            'source': 'pubmed',
                            'journal_source': task['journal'],
                            'title': '',
                            'content': '',
                            'url': ''
                        }
                        
                        lines = entry.split('\n')
                        for line in lines:
                            if line.strip().startswith('Title: '):
                                result_dict['title'] = line.replace('Title: ', '').strip()
                            elif line.strip().startswith('Abstract Snippet: '):
                                result_dict['content'] = line.replace('Abstract Snippet: ', '').strip()
                            elif line.strip().startswith('URL: '):
                                result_dict['url'] = line.replace('URL: ', '').strip()
                        
                        if result_dict['title']:
                            parsed_results.append(result_dict)
            
            elif isinstance(raw_result, list):
                # Tavily/通用搜索返回列表格式
                for item in raw_result:
                    if isinstance(item, dict):
                        result_dict = {
                            'title': item.get('title', ''),
                            'content': item.get('content', ''),
                            'url': item.get('url', ''),
                            'source': task['engine'],
                            'journal_source': task['journal']
                        }
                        parsed_results.append(result_dict)
        
        except Exception as e:
            logger.error(f"❌ 解析搜索结果失败: {task['engine']} - {e}")
        
        return parsed_results
    
    def _enhance_results_with_journal_info(self, results: List[Dict], target_journals: List[JournalInfo]) -> List[Dict]:
        """为结果添加期刊信息增强"""
        
        enhanced_results = []
        
        for result in results:
            enhanced_result = result.copy()
            
            # 添加目标期刊匹配信息
            matched_journal = None
            for journal in target_journals:
                if (journal.name.lower() in result.get('title', '').lower() or 
                    journal.name.lower() in result.get('content', '').lower() or
                    journal.full_name.lower() in result.get('content', '').lower()):
                    matched_journal = journal
                    break
            
            if matched_journal:
                enhanced_result['matched_journal'] = {
                    'name': matched_journal.name,
                    'full_name': matched_journal.full_name,
                    'impact_factor': matched_journal.impact_factor,
                    'tier': matched_journal.tier.value
                }
                enhanced_result['quality_score'] = self._calculate_quality_score(result, matched_journal)
            
            enhanced_results.append(enhanced_result)
        
        # 按质量分数排序
        enhanced_results.sort(key=lambda r: r.get('quality_score', 0), reverse=True)
        
        return enhanced_results
    
    def _calculate_quality_score(self, result: Dict, journal: JournalInfo) -> float:
        """计算结果质量分数"""
        
        base_score = 0.5
        
        # 期刊影响因子加权
        if journal.impact_factor > 20:
            base_score += 0.4
        elif journal.impact_factor > 10:
            base_score += 0.3
        elif journal.impact_factor > 5:
            base_score += 0.2
        else:
            base_score += 0.1
        
        # 期刊等级加权
        tier_bonus = {
            JournalTier.TOP_TIER: 0.3,
            JournalTier.HIGH_TIER: 0.2,
            JournalTier.MID_TIER: 0.1,
            JournalTier.EMERGING: 0.0
        }
        base_score += tier_bonus.get(journal.tier, 0)
        
        # 内容质量评估
        content_length = len(result.get('content', ''))
        if content_length > 500:
            base_score += 0.1
        
        return min(base_score, 1.0)
    
    def _fallback_search(self, query: str, max_results: int) -> Dict[str, Any]:
        """降级搜索策略"""
        
        logger.info("🔄 执行降级搜索策略")
        
        try:
            # 使用通用搜索工具
            web_tool = get_web_search_tool(max_results)
            results = web_tool.invoke(query)
            
            if isinstance(results, list):
                return {
                    'query': query,
                    'total_results': len(results),
                    'results': results,
                    'search_strategy': 'fallback'
                }
        except Exception as e:
            logger.error(f"❌ 降级搜索也失败了: {e}")
        
        return {
            'query': query,
            'total_results': 0,
            'results': [],
            'search_strategy': 'failed'
        }

# 创建全局实例
journal_aware_search_engine = JournalAwareSearchEngine()

# 便捷接口函数
def search_high_quality_journals(query: str, field: str = None, max_results: int = 15) -> Dict[str, Any]:
    """搜索高质量期刊文献"""
    return journal_aware_search_engine.search_by_journal_quality(
        query=query,
        target_tier="high",
        target_field=field,
        max_results=max_results
    )

def search_top_tier_journals_only(query: str, max_results: int = 10) -> Dict[str, Any]:
    """仅搜索顶级期刊 (Nature, Science, Cell等)"""
    return journal_aware_search_engine.search_top_tier_only(query, max_results)

def search_specific_journals(query: str, journals: List[str], max_results: int = 20) -> Dict[str, Any]:
    """搜索指定期刊列表"""
    return journal_aware_search_engine.search_by_journal_quality(
        query=query,
        specific_journals=journals,
        max_results=max_results
    ) 
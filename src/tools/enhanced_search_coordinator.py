# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
增强搜索协调器 - 智能选择最佳搜索策略
实现多引擎并行搜索、质量过滤、中英文优化
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .search import (
    LoggedTavilySearch, 
    LoggedPubMedSearch, 
    LoggedGoogleScholarSearch,
    LoggedDuckDuckGoSearch
)

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """标准化搜索结果格式"""
    title: str
    content: str
    url: str
    source: str  # 搜索引擎名称
    quality_score: float  # 质量评分 0-1
    relevance_score: float  # 相关性评分 0-1
    is_academic: bool  # 是否学术文献
    publish_year: Optional[int] = None
    impact_factor: Optional[float] = None

@dataclass
class SearchStrategy:
    """搜索策略配置"""
    query_type: str  # "general", "academic", "medical", "technical"
    languages: List[str]  # ["en", "zh", "mixed"]
    engines: List[str]  # 使用的搜索引擎
    max_results_per_engine: int
    quality_threshold: float
    parallel_search: bool

class EnhancedSearchCoordinator:
    """增强搜索协调器"""
    
    def __init__(self):
        self.engines = {
            'tavily': LoggedTavilySearch,
            'pubmed': LoggedPubMedSearch,
            'google_scholar': LoggedGoogleScholarSearch,
            'duckduckgo': LoggedDuckDuckGoSearch
        }
        
        # 预定义搜索策略
        self.strategies = {
            'medical_research': SearchStrategy(
                query_type="medical",
                languages=["en", "zh"],
                engines=["pubmed", "google_scholar", "tavily"],
                max_results_per_engine=10,
                quality_threshold=0.7,
                parallel_search=True
            ),
            'ai_technology': SearchStrategy(
                query_type="technical", 
                languages=["en"],
                engines=["google_scholar", "tavily"],
                max_results_per_engine=15,
                quality_threshold=0.6,
                parallel_search=True
            ),
            'general_research': SearchStrategy(
                query_type="general",
                languages=["en", "zh"],
                engines=["tavily", "duckduckgo"],
                max_results_per_engine=8,
                quality_threshold=0.5,
                parallel_search=False
            ),
            'comprehensive_survey': SearchStrategy(
                query_type="academic",
                languages=["en", "zh"],
                engines=["pubmed", "google_scholar", "tavily"],
                max_results_per_engine=20,
                quality_threshold=0.8,
                parallel_search=True
            )
        }
    
    def select_strategy(self, query: str, context: Dict[str, Any] = None) -> SearchStrategy:
        """智能选择搜索策略"""
        
        # 基于查询内容的关键词检测
        medical_keywords = ['dxa', 'medical', 'clinical', 'patient', 'disease', 'therapy', 'drug']
        ai_keywords = ['ai', 'machine learning', 'deep learning', 'neural network', 'algorithm']
        academic_keywords = ['research', 'study', 'analysis', 'methodology', 'systematic review']
        
        query_lower = query.lower()
        
        # 检测中文内容
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in query)
        
        # 智能策略选择
        if any(keyword in query_lower for keyword in medical_keywords):
            strategy = self.strategies['medical_research'].copy() if hasattr(self.strategies['medical_research'], 'copy') else self.strategies['medical_research']
            logger.info("🔍 选择医学研究搜索策略")
            
        elif any(keyword in query_lower for keyword in ai_keywords):
            strategy = self.strategies['ai_technology']
            logger.info("🔍 选择AI技术搜索策略")
            
        elif any(keyword in query_lower for keyword in academic_keywords) or (context and context.get('is_comprehensive')):
            strategy = self.strategies['comprehensive_survey']
            logger.info("🔍 选择综合学术搜索策略")
            
        else:
            strategy = self.strategies['general_research']
            logger.info("🔍 选择通用研究搜索策略")
        
        # 如果有中文内容，确保包含中文搜索
        if has_chinese and "zh" not in strategy.languages:
            strategy.languages.append("zh")
        
        return strategy
    
    def optimize_query(self, query: str, language: str, engine: str) -> str:
        """针对不同引擎和语言优化查询语句"""
        
        optimized_queries = {
            'en': {
                'pubmed': f"({query}) AND (systematic review OR meta-analysis OR clinical trial)",
                'google_scholar': f'"{query}" systematic review OR methodology',
                'tavily': f"{query} latest research findings",
                'duckduckgo': query
            },
            'zh': {
                'tavily': f"{query} 最新研究",
                'duckduckgo': f"{query} 研究 综述",
                'google_scholar': f"{query} 系统性综述",
                'pubmed': query  # PubMed主要英文，保持原查询
            }
        }
        
        return optimized_queries.get(language, {}).get(engine, query)
    
    def assess_result_quality(self, result: Dict[str, Any], source: str) -> float:
        """评估搜索结果质量"""
        
        quality_score = 0.5  # 基础分数
        
        # 来源权重
        source_weights = {
            'pubmed': 0.9,
            'google_scholar': 0.8,
            'tavily': 0.6,
            'duckduckgo': 0.5
        }
        quality_score *= source_weights.get(source, 0.5)
        
        # 标题质量检查
        title = result.get('title', '').lower()
        if any(keyword in title for keyword in ['systematic review', 'meta-analysis', 'clinical trial']):
            quality_score += 0.2
        if any(keyword in title for keyword in ['2023', '2024', 'recent', 'latest']):
            quality_score += 0.1
            
        # 内容长度检查
        content = result.get('content', '')
        if len(content) > 500:
            quality_score += 0.1
        if len(content) > 1000:
            quality_score += 0.1
            
        # URL质量检查
        url = result.get('url', '').lower()
        quality_domains = [
            'pubmed.ncbi.nlm.nih.gov', 'scholar.google.com', 'arxiv.org',
            'nature.com', 'cell.com', 'science.org', 'nejm.org', 'thelancet.com'
        ]
        if any(domain in url for domain in quality_domains):
            quality_score += 0.2
            
        return min(quality_score, 1.0)  # 确保不超过1.0
    
    async def parallel_search(self, strategy: SearchStrategy, query: str) -> List[SearchResult]:
        """并行执行多引擎搜索"""
        
        results = []
        search_tasks = []
        
        # 为每个引擎和语言创建搜索任务
        for engine in strategy.engines:
            for language in strategy.languages:
                optimized_query = self.optimize_query(query, language, engine)
                
                if engine in self.engines:
                    try:
                        engine_instance = self.engines[engine]()
                        search_tasks.append({
                            'engine': engine,
                            'language': language, 
                            'query': optimized_query,
                            'instance': engine_instance
                        })
                    except Exception as e:
                        logger.warning(f"⚠️ 无法初始化搜索引擎 {engine}: {e}")
        
        # 并行执行搜索
        with ThreadPoolExecutor(max_workers=min(len(search_tasks), 5)) as executor:
            future_to_task = {}
            
            for task in search_tasks:
                try:
                    future = executor.submit(
                        task['instance'].invoke,
                        {'query': task['query']} if isinstance(task['query'], str) else task['query']
                    )
                    future_to_task[future] = task
                except Exception as e:
                    logger.error(f"❌ 搜索任务提交失败 {task['engine']}: {e}")
            
            # 收集结果
            for future in as_completed(future_to_task, timeout=30):
                task = future_to_task[future]
                try:
                    raw_results = future.result(timeout=10)
                    
                    # 标准化结果格式
                    if isinstance(raw_results, list):
                        for item in raw_results:
                            if isinstance(item, dict):
                                quality_score = self.assess_result_quality(item, task['engine'])
                                
                                if quality_score >= strategy.quality_threshold:
                                    result = SearchResult(
                                        title=item.get('title', ''),
                                        content=item.get('content', ''),
                                        url=item.get('url', ''),
                                        source=task['engine'],
                                        quality_score=quality_score,
                                        relevance_score=0.5,  # 可以进一步优化
                                        is_academic=task['engine'] in ['pubmed', 'google_scholar']
                                    )
                                    results.append(result)
                                    
                except Exception as e:
                    logger.warning(f"⚠️ 搜索引擎 {task['engine']} 执行失败: {e}")
        
        # 结果去重和排序
        unique_results = self.deduplicate_results(results)
        sorted_results = sorted(unique_results, 
                               key=lambda x: (x.quality_score + x.relevance_score) / 2, 
                               reverse=True)
        
        logger.info(f"✅ 并行搜索完成，获得 {len(sorted_results)} 个高质量结果")
        return sorted_results[:strategy.max_results_per_engine * len(strategy.engines)]
    
    def deduplicate_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """结果去重"""
        seen_urls = set()
        seen_titles = set()
        unique_results = []
        
        for result in results:
            # 基于URL去重
            if result.url and result.url in seen_urls:
                continue
            # 基于标题去重（考虑相似性）
            title_key = result.title.lower().strip()
            if title_key and title_key in seen_titles:
                continue
                
            seen_urls.add(result.url)
            seen_titles.add(title_key)
            unique_results.append(result)
        
        return unique_results
    
    async def enhanced_search(self, query: str, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """增强搜索主入口"""
        
        start_time = time.time()
        
        # 选择搜索策略
        strategy = self.select_strategy(query, context)
        logger.info(f"🔍 搜索策略: {strategy.query_type}, 引擎: {strategy.engines}, 语言: {strategy.languages}")
        
        # 执行搜索
        if strategy.parallel_search:
            results = await self.parallel_search(strategy, query)
        else:
            # 串行搜索（保留向后兼容）
            results = []
            for engine in strategy.engines:
                try:
                    engine_instance = self.engines[engine]()
                    raw_results = engine_instance.invoke(query)
                    # 处理结果...
                except Exception as e:
                    logger.warning(f"⚠️ 串行搜索失败 {engine}: {e}")
        
        # 转换为标准格式
        formatted_results = []
        for result in results:
            formatted_results.append({
                'title': result.title,
                'content': result.content,
                'url': result.url,
                'source': result.source,
                'quality_score': result.quality_score,
                'is_academic': result.is_academic
            })
        
        elapsed_time = time.time() - start_time
        logger.info(f"✅ 增强搜索完成，耗时 {elapsed_time:.2f}s，获得 {len(formatted_results)} 个结果")
        
        return formatted_results

# 创建全局实例
enhanced_search_coordinator = EnhancedSearchCoordinator() 
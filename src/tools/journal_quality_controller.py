# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
期刊质量控制器 - 支持高质量期刊的智能筛选和搜索优化
实现期刊影响因子过滤、声誉评估、专业领域匹配
"""

import logging
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)

class JournalTier(Enum):
    """期刊等级分类"""
    TOP_TIER = "top_tier"           # 顶级期刊 (IF > 15)
    HIGH_TIER = "high_tier"         # 高级期刊 (IF 5-15)  
    MID_TIER = "mid_tier"           # 中级期刊 (IF 2-5)
    EMERGING = "emerging"           # 新兴期刊 (IF < 2)

@dataclass
class JournalInfo:
    """期刊信息"""
    name: str
    full_name: str
    impact_factor: float
    tier: JournalTier
    fields: List[str]              # 专业领域
    publisher: str
    issn: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None

class JournalQualityController:
    """期刊质量控制器"""
    
    def __init__(self):
        # 🏆 顶级期刊数据库
        self.journal_database = self._initialize_journal_database()
        
        # 🎯 领域关键词映射
        self.field_keywords = {
            'ai_ml': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 'computer vision'],
            'medical_imaging': ['medical imaging', 'radiology', 'radiomics', 'tomography', 'mri', 'ct', 'dxa'],
            'bone_health': ['bone', 'osteoporosis', 'bone density', 'skeletal', 'bone mineral'],
            'cardiovascular': ['cardiovascular', 'cardiac', 'heart', 'vascular', 'cardiology'],
            'biomedical': ['biomedical', 'biotechnology', 'biomedicine', 'medical technology'],
            'data_science': ['data science', 'bioinformatics', 'computational biology', 'biostatistics']
        }
    
    def _initialize_journal_database(self) -> Dict[str, JournalInfo]:
        """初始化期刊数据库"""
        
        journals = {
            # 🏆 顶级期刊 (Nature系列)
            'nature': JournalInfo(
                name='Nature',
                full_name='Nature',
                impact_factor=64.8,
                tier=JournalTier.TOP_TIER,
                fields=['general_science', 'ai_ml', 'biomedical'],
                publisher='Nature Publishing Group',
                issn='0028-0836',
                url='https://www.nature.com/nature',
                description='世界顶级综合性科学期刊'
            ),
            'nature_medicine': JournalInfo(
                name='Nature Medicine',
                full_name='Nature Medicine',
                impact_factor=87.2,
                tier=JournalTier.TOP_TIER,
                fields=['medical_imaging', 'biomedical', 'bone_health'],
                publisher='Nature Publishing Group'
            ),
            'nature_ai': JournalInfo(
                name='Nature Machine Intelligence',
                full_name='Nature Machine Intelligence',
                impact_factor=25.9,
                tier=JournalTier.TOP_TIER,
                fields=['ai_ml', 'data_science'],
                publisher='Nature Publishing Group'
            ),
            
            # 🏆 顶级期刊 (Cell系列)
            'cell': JournalInfo(
                name='Cell',
                full_name='Cell',
                impact_factor=66.9,
                tier=JournalTier.TOP_TIER,
                fields=['biomedical', 'general_science'],
                publisher='Cell Press'
            ),
            
            # 🏆 顶级期刊 (Science系列)
            'science': JournalInfo(
                name='Science',
                full_name='Science',
                impact_factor=56.9,
                tier=JournalTier.TOP_TIER,
                fields=['general_science', 'ai_ml', 'biomedical'],
                publisher='AAAS'
            ),
            'science_translational_medicine': JournalInfo(
                name='Science Translational Medicine',
                full_name='Science Translational Medicine',
                impact_factor=19.3,
                tier=JournalTier.TOP_TIER,
                fields=['medical_imaging', 'biomedical'],
                publisher='AAAS'
            ),
            
            # 🏆 顶级医学期刊
            'nejm': JournalInfo(
                name='NEJM',
                full_name='New England Journal of Medicine',
                impact_factor=158.5,
                tier=JournalTier.TOP_TIER,
                fields=['medical_imaging', 'biomedical', 'bone_health'],
                publisher='Massachusetts Medical Society'
            ),
            'lancet': JournalInfo(
                name='The Lancet',
                full_name='The Lancet',
                impact_factor=202.7,
                tier=JournalTier.TOP_TIER,
                fields=['medical_imaging', 'biomedical', 'bone_health'],
                publisher='Elsevier'
            ),
            'jama': JournalInfo(
                name='JAMA',
                full_name='Journal of the American Medical Association',
                impact_factor=157.3,
                tier=JournalTier.TOP_TIER,
                fields=['medical_imaging', 'biomedical'],
                publisher='AMA'
            ),
            
            # 🏆 顶级技术期刊
            'ieee_tpami': JournalInfo(
                name='IEEE TPAMI',
                full_name='IEEE Transactions on Pattern Analysis and Machine Intelligence',
                impact_factor=24.3,
                tier=JournalTier.TOP_TIER,
                fields=['ai_ml', 'computer_vision', 'medical_imaging'],
                publisher='IEEE'
            ),
            'ieee_tmi': JournalInfo(
                name='IEEE TMI',
                full_name='IEEE Transactions on Medical Imaging',
                impact_factor=11.0,
                tier=JournalTier.HIGH_TIER,
                fields=['medical_imaging', 'ai_ml'],
                publisher='IEEE'
            ),
            
            # 🥈 高级医学影像期刊
            'radiology': JournalInfo(
                name='Radiology',
                full_name='Radiology',
                impact_factor=12.1,
                tier=JournalTier.HIGH_TIER,
                fields=['medical_imaging', 'radiology'],
                publisher='RSNA'
            ),
            'european_radiology': JournalInfo(
                name='European Radiology',
                full_name='European Radiology',
                impact_factor=7.0,
                tier=JournalTier.HIGH_TIER,
                fields=['medical_imaging', 'radiology'],
                publisher='Springer'
            ),
            
            # 🥈 骨骼健康专业期刊
            'jbmr': JournalInfo(
                name='JBMR',
                full_name='Journal of Bone and Mineral Research',
                impact_factor=6.2,
                tier=JournalTier.HIGH_TIER,
                fields=['bone_health', 'osteoporosis'],
                publisher='Wiley'
            ),
            'bone': JournalInfo(
                name='Bone',
                full_name='Bone',
                impact_factor=4.9,
                tier=JournalTier.MID_TIER,
                fields=['bone_health', 'osteoporosis'],
                publisher='Elsevier'
            ),
            'osteoporosis_international': JournalInfo(
                name='Osteoporosis International',
                full_name='Osteoporosis International',
                impact_factor=4.4,
                tier=JournalTier.MID_TIER,
                fields=['bone_health', 'osteoporosis'],
                publisher='Springer'
            ),
            
            # 🥈 AI/ML专业期刊
            'nature_biotechnology': JournalInfo(
                name='Nature Biotechnology',
                full_name='Nature Biotechnology',
                impact_factor=54.9,
                tier=JournalTier.TOP_TIER,
                fields=['ai_ml', 'biomedical', 'data_science'],
                publisher='Nature Publishing Group'
            ),
            'artificial_intelligence_in_medicine': JournalInfo(
                name='Artificial Intelligence in Medicine',
                full_name='Artificial Intelligence in Medicine',
                impact_factor=7.5,
                tier=JournalTier.HIGH_TIER,
                fields=['ai_ml', 'medical_imaging', 'biomedical'],
                publisher='Elsevier'
            )
        }
        
        logger.info(f"✅ 期刊数据库初始化完成，包含 {len(journals)} 个期刊")
        return journals
    
    def get_journals_by_field(self, field: str, min_tier: JournalTier = JournalTier.MID_TIER) -> List[JournalInfo]:
        """根据领域获取期刊列表"""
        
        matching_journals = []
        for journal in self.journal_database.values():
            # 检查期刊是否属于指定领域
            if field in journal.fields:
                # 检查期刊等级是否符合要求
                tier_order = [JournalTier.TOP_TIER, JournalTier.HIGH_TIER, JournalTier.MID_TIER, JournalTier.EMERGING]
                if tier_order.index(journal.tier) <= tier_order.index(min_tier):
                    matching_journals.append(journal)
        
        # 按影响因子排序
        matching_journals.sort(key=lambda j: j.impact_factor, reverse=True)
        
        logger.info(f"🔍 找到 {len(matching_journals)} 个 {field} 领域的期刊 (最低等级: {min_tier.value})")
        return matching_journals
    
    def get_top_journals(self, field: str = None, limit: int = 10) -> List[JournalInfo]:
        """获取顶级期刊列表"""
        
        journals = list(self.journal_database.values())
        
        # 如果指定了领域，进行过滤
        if field:
            journals = [j for j in journals if field in j.fields]
        
        # 按影响因子排序并限制数量
        top_journals = sorted(journals, key=lambda j: j.impact_factor, reverse=True)[:limit]
        
        logger.info(f"📊 获取顶级期刊列表: {len(top_journals)} 个期刊 (领域: {field or '全部'})")
        return top_journals
    
    def suggest_journals_for_query(self, query: str) -> Dict[str, List[JournalInfo]]:
        """根据查询内容推荐期刊"""
        
        query_lower = query.lower()
        suggested_fields = set()
        
        # 智能识别查询领域
        for field, keywords in self.field_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    suggested_fields.add(field)
        
        # 如果没有识别到特定领域，使用通用策略
        if not suggested_fields:
            suggested_fields = {'ai_ml', 'biomedical', 'medical_imaging'}
            logger.info("🤖 未识别到特定领域，使用通用AI/生物医学期刊")
        
        # 为每个领域获取推荐期刊
        recommendations = {}
        for field in suggested_fields:
            field_journals = self.get_journals_by_field(field, min_tier=JournalTier.HIGH_TIER)
            if field_journals:
                recommendations[field] = field_journals[:5]  # 每个领域最多5个期刊
        
        logger.info(f"💡 为查询 '{query}' 推荐了 {len(recommendations)} 个领域的期刊")
        return recommendations
    
    def generate_journal_specific_query(self, base_query: str, journal: JournalInfo) -> str:
        """生成期刊特定的搜索查询"""
        
        # 基础查询优化
        enhanced_query = base_query
        
        # 添加期刊名称限制
        journal_terms = [
            f'source:"{journal.full_name}"',
            f'journal:"{journal.name}"',
            f'"{journal.full_name}"'
        ]
        
        # 根据搜索引擎选择最佳语法
        # Google Scholar 语法
        enhanced_query = f'{base_query} source:"{journal.full_name}"'
        
        # PubMed 语法 (如果是医学期刊)
        if 'medical' in journal.fields or 'biomedical' in journal.fields:
            pubmed_query = f'{base_query} AND "{journal.full_name}"[Journal]'
            return {
                'google_scholar': enhanced_query,
                'pubmed': pubmed_query,
                'general': enhanced_query
            }
        
        return {
            'google_scholar': enhanced_query,
            'general': enhanced_query
        }
    
    def filter_results_by_journal_quality(self, results: List[Dict], min_tier: JournalTier = JournalTier.MID_TIER) -> List[Dict]:
        """根据期刊质量过滤搜索结果"""
        
        filtered_results = []
        tier_order = [JournalTier.TOP_TIER, JournalTier.HIGH_TIER, JournalTier.MID_TIER, JournalTier.EMERGING]
        min_tier_index = tier_order.index(min_tier)
        
        for result in results:
            # 提取期刊信息
            journal_quality = self._assess_journal_quality(result)
            
            if journal_quality:
                journal_tier_index = tier_order.index(journal_quality['tier'])
                if journal_tier_index <= min_tier_index:
                    result['journal_quality'] = journal_quality
                    filtered_results.append(result)
            else:
                # 如果无法识别期刊质量，使用保守策略
                if min_tier in [JournalTier.MID_TIER, JournalTier.EMERGING]:
                    result['journal_quality'] = {'tier': JournalTier.EMERGING, 'confidence': 0.3}
                    filtered_results.append(result)
        
        # 按期刊质量排序
        filtered_results.sort(key=lambda r: (
            tier_order.index(r.get('journal_quality', {}).get('tier', JournalTier.EMERGING)),
            r.get('journal_quality', {}).get('impact_factor', 0)
        ))
        
        logger.info(f"🎯 期刊质量过滤: {len(results)} → {len(filtered_results)} 个结果")
        return filtered_results
    
    def _assess_journal_quality(self, result: Dict) -> Optional[Dict]:
        """评估单个搜索结果的期刊质量"""
        
        # 从结果中提取期刊信息
        title = result.get('title', '').lower()
        content = result.get('content', '').lower()
        url = result.get('url', '').lower()
        
        # 尝试匹配已知期刊
        for journal_key, journal_info in self.journal_database.items():
            journal_names = [
                journal_info.name.lower(),
                journal_info.full_name.lower()
            ]
            
            # 检查是否在标题、内容或URL中找到期刊名称
            for name in journal_names:
                if name in title or name in content or name in url:
                    return {
                        'name': journal_info.name,
                        'full_name': journal_info.full_name,
                        'tier': journal_info.tier,
                        'impact_factor': journal_info.impact_factor,
                        'confidence': 0.9
                    }
        
        # 如果没有匹配到已知期刊，尝试启发式评估
        return self._heuristic_journal_assessment(result)
    
    def _heuristic_journal_assessment(self, result: Dict) -> Optional[Dict]:
        """启发式期刊质量评估"""
        
        content = (result.get('title', '') + ' ' + result.get('content', '')).lower()
        url = result.get('url', '').lower()
        
        # 高质量期刊的指标
        quality_indicators = {
            'top_tier': [
                'nature.com', 'cell.com', 'science.org', 'nejm.org', 'thelancet.com',
                'ieee.org', 'acm.org', 'pnas.org'
            ],
            'high_tier': [
                'springer.com', 'elsevier.com', 'wiley.com', 'pubmed.ncbi.nlm.nih.gov',
                'doi.org', 'impact factor', 'peer review'
            ]
        }
        
        # 检查URL域名
        for tier, indicators in quality_indicators.items():
            for indicator in indicators:
                if indicator in url or indicator in content:
                    tier_enum = JournalTier.TOP_TIER if tier == 'top_tier' else JournalTier.HIGH_TIER
                    return {
                        'tier': tier_enum,
                        'confidence': 0.6,
                        'reason': f'匹配到质量指标: {indicator}'
                    }
        
        return None
    
    def get_search_strategy_for_journals(self, target_journals: List[JournalInfo], query: str) -> Dict[str, Any]:
        """为指定期刊生成搜索策略"""
        
        strategy = {
            'multi_engine_queries': {},
            'journal_priorities': [],
            'expected_coverage': {}
        }
        
        # 为每个目标期刊生成特定查询
        for journal in target_journals:
            journal_queries = self.generate_journal_specific_query(query, journal)
            strategy['multi_engine_queries'][journal.name] = journal_queries
            strategy['journal_priorities'].append({
                'name': journal.name,
                'tier': journal.tier.value,
                'impact_factor': journal.impact_factor
            })
        
        # 设置预期覆盖率
        total_if = sum(j.impact_factor for j in target_journals)
        for journal in target_journals:
            weight = journal.impact_factor / total_if if total_if > 0 else 1 / len(target_journals)
            strategy['expected_coverage'][journal.name] = weight
        
        logger.info(f"📋 为 {len(target_journals)} 个期刊生成搜索策略")
        return strategy

# 创建全局实例
journal_quality_controller = JournalQualityController()

def get_recommended_journals(query: str, field: str = None, tier: str = "high") -> List[JournalInfo]:
    """便捷函数：获取推荐期刊列表"""
    
    tier_map = {
        "top": JournalTier.TOP_TIER,
        "high": JournalTier.HIGH_TIER,
        "mid": JournalTier.MID_TIER,
        "all": JournalTier.EMERGING
    }
    
    min_tier = tier_map.get(tier, JournalTier.HIGH_TIER)
    
    if field:
        return journal_quality_controller.get_journals_by_field(field, min_tier)
    else:
        recommendations = journal_quality_controller.suggest_journals_for_query(query)
        all_journals = []
        for field_journals in recommendations.values():
            all_journals.extend(field_journals)
        
        # 去重并按影响因子排序
        unique_journals = list({j.name: j for j in all_journals}.values())
        unique_journals.sort(key=lambda j: j.impact_factor, reverse=True)
        return unique_journals[:10]  # 返回前10个

def create_journal_focused_search_query(query: str, journals: List[str] = None) -> Dict[str, str]:
    """创建期刊聚焦的搜索查询"""
    
    if not journals:
        # 如果没有指定期刊，推荐高质量期刊
        recommended = journal_quality_controller.suggest_journals_for_query(query)
        journals = []
        for field_journals in recommended.values():
            journals.extend([j.name for j in field_journals[:2]])  # 每个领域前2个期刊
    
    # 生成多引擎查询
    queries = {}
    
    # Google Scholar 查询
    scholar_terms = []
    for journal in journals[:3]:  # 最多3个期刊，避免查询过长
        journal_info = journal_quality_controller.journal_database.get(journal.lower().replace(' ', '_'))
        if journal_info:
            scholar_terms.append(f'source:"{journal_info.full_name}"')
    
    if scholar_terms:
        queries['google_scholar'] = f"{query} ({' OR '.join(scholar_terms)})"
    else:
        queries['google_scholar'] = query
    
    # PubMed 查询
    pubmed_terms = []
    for journal in journals[:3]:
        journal_info = journal_quality_controller.journal_database.get(journal.lower().replace(' ', '_'))
        if journal_info and any(field in ['medical_imaging', 'biomedical', 'bone_health'] for field in journal_info.fields):
            pubmed_terms.append(f'"{journal_info.full_name}"[Journal]')
    
    if pubmed_terms:
        queries['pubmed'] = f"{query} AND ({' OR '.join(pubmed_terms)})"
    else:
        queries['pubmed'] = query
    
    # 通用查询
    queries['general'] = query
    
    logger.info(f"🎯 为 {len(journals)} 个期刊创建了专门的搜索查询")
    return queries 
# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
文献搜索增强功能配置
"""

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class LiteratureEnhancementConfig:
    """文献增强配置类"""
    
    # 🔍 搜索配置
    max_literature_count: int = 50          # 最大文献数量
    pubmed_max_results: int = 15           # PubMed每次搜索最大结果
    scholar_max_results: int = 12          # Google Scholar每次搜索最大结果
    
    # 🎯 搜索策略
    enable_systematic_reviews: bool = True   # 启用系统性综述搜索
    enable_clinical_trials: bool = True      # 启用临床试验搜索
    enable_technical_papers: bool = True     # 启用技术论文搜索
    enable_mechanism_studies: bool = True    # 启用机制研究搜索
    
    # 📊 质量控制
    min_quality_score: float = 0.7          # 最低质量分数
    prefer_recent_papers: bool = True        # 优先近期论文
    min_publication_year: int = 2020         # 最低发表年份
    
    # 🔗 引用配置
    max_citations_per_direction: int = 3    # 每个研究方向最大引用数
    enable_reference_links: bool = True     # 启用参考文献链接
    
    # ⚡ 性能配置
    search_timeout: int = 30                # 搜索超时时间（秒）
    pause_between_searches: float = 0.5     # 搜索间隔时间
    
    # 🎛️ 功能开关
    enable_auto_detection: bool = True      # 自动检测是否需要文献增强
    fallback_to_batch: bool = True         # 失败时降级到批量生成
    
    @classmethod
    def for_medical_research(cls) -> "LiteratureEnhancementConfig":
        """医学研究专用配置"""
        return cls(
            max_literature_count=60,
            pubmed_max_results=20,
            scholar_max_results=10,
            enable_systematic_reviews=True,
            enable_clinical_trials=True,
            min_quality_score=0.8,
            min_publication_year=2020
        )
    
    @classmethod
    def for_ai_research(cls) -> "LiteratureEnhancementConfig":
        """AI研究专用配置"""
        return cls(
            max_literature_count=45,
            pubmed_max_results=8,
            scholar_max_results=15,
            enable_technical_papers=True,
            enable_mechanism_studies=False,
            min_quality_score=0.75,
            min_publication_year=2022  # AI领域更新快
        )
    
    @classmethod
    def for_comprehensive_research(cls) -> "LiteratureEnhancementConfig":
        """综合研究配置（所有类型文献）"""
        return cls(
            max_literature_count=80,
            pubmed_max_results=20,
            scholar_max_results=20,
            enable_systematic_reviews=True,
            enable_clinical_trials=True,
            enable_technical_papers=True,
            enable_mechanism_studies=True,
            min_quality_score=0.7,
            min_publication_year=2019
        )
    
    @classmethod
    def for_quick_research(cls) -> "LiteratureEnhancementConfig":
        """快速研究配置（较少文献）"""
        return cls(
            max_literature_count=25,
            pubmed_max_results=10,
            scholar_max_results=8,
            min_quality_score=0.8,
            search_timeout=20,
            pause_between_searches=0.3
        )

# 全局配置实例
DEFAULT_LITERATURE_CONFIG = LiteratureEnhancementConfig()

# 预定义配置映射
RESEARCH_TYPE_CONFIGS = {
    "medical": LiteratureEnhancementConfig.for_medical_research(),
    "ai": LiteratureEnhancementConfig.for_ai_research(),
    "comprehensive": LiteratureEnhancementConfig.for_comprehensive_research(),
    "quick": LiteratureEnhancementConfig.for_quick_research(),
    "default": DEFAULT_LITERATURE_CONFIG
}

def get_literature_config(research_type: str = "default") -> LiteratureEnhancementConfig:
    """获取文献增强配置"""
    return RESEARCH_TYPE_CONFIGS.get(research_type, DEFAULT_LITERATURE_CONFIG)

def detect_research_type_from_query(query: str, plan_title: str = "") -> str:
    """从查询和计划标题中检测研究类型"""
    
    combined_text = f"{query} {plan_title}".lower()
    
    # 医学研究关键词
    medical_keywords = [
        "医学", "医疗", "健康", "疾病", "临床", "患者", "诊断", "治疗",
        "medical", "health", "disease", "clinical", "patient", "diagnosis", "treatment",
        "骨密度", "DXA", "影像", "放射", "bone", "imaging", "radiology"
    ]
    
    # AI研究关键词
    ai_keywords = [
        "人工智能", "机器学习", "深度学习", "神经网络", "算法",
        "artificial intelligence", "machine learning", "deep learning", 
        "neural network", "algorithm", "AI", "ML", "DL"
    ]
    
    # 计算匹配分数
    medical_score = sum(1 for keyword in medical_keywords if keyword in combined_text)
    ai_score = sum(1 for keyword in ai_keywords if keyword in combined_text)
    
    # 判断研究类型
    if medical_score >= 2 and ai_score >= 1:
        return "comprehensive"  # 医学+AI综合研究
    elif medical_score >= 2:
        return "medical"
    elif ai_score >= 2:
        return "ai"
    else:
        return "default"

# 文献搜索关键词模板
LITERATURE_SEARCH_TEMPLATES = {
    "systematic_review": [
        "{query} systematic review",
        "{query} meta-analysis", 
        "{query} comprehensive review"
    ],
    "clinical_trial": [
        "{query} clinical trial",
        "{query} randomized controlled trial",
        "{query} clinical study"
    ],
    "technical": [
        "{query} artificial intelligence",
        "{query} machine learning",
        "{query} deep learning"
    ],
    "mechanism": [
        "{query} mechanism",
        "{query} pathophysiology",
        "{query} molecular basis"
    ]
}

def get_search_queries(base_query: str, search_type: str) -> List[str]:
    """获取特定类型的搜索查询"""
    templates = LITERATURE_SEARCH_TEMPLATES.get(search_type, ["{query}"])
    return [template.format(query=base_query) for template in templates] 
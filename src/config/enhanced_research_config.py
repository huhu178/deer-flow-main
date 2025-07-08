# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
增强科研配置模块
================

针对科研项目的优化配置，解决以下问题：
1. 🔍 增加搜索结果数量（从3-5个增加到10-15个）
2. 🔄 简化多轮机制（直接3轮搜索，无需复杂阈值判断）
3. 📚 优化学术搜索策略
4. ⚡ 提高研究效率

使用方法：
```python
from src.config.enhanced_research_config import ResearchConfiguration

# 1. 使用科研优化配置
config = ResearchConfiguration.for_research_project()

# 2. 使用高强度搜索配置  
config = ResearchConfiguration.for_intensive_research()

# 3. 自定义配置
config = ResearchConfiguration(
    max_search_results=15,
    search_rounds=3,
    enable_multi_source=True
)
```
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class ResearchConfiguration:
    """科研项目专用配置类"""
    
    # 🔍 搜索配置 - 大幅增加搜索结果数量
    max_search_results: int = 12           # 主搜索结果数量（从3增加到12）
    pubmed_results: int = 10               # PubMed搜索结果（从5增加到10）
    google_scholar_results: int = 10       # Google Scholar结果（从5增加到10）
    arxiv_results: int = 8                 # ArXiv搜索结果
    
    # 🔄 多轮搜索配置 - 简化设计
    search_rounds: int = 3                 # 固定3轮搜索，无需复杂判断
    enable_multi_source: bool = True       # 启用多源搜索（PubMed + Scholar + Web）
    enable_iterative_search: bool = True   # 启用迭代式搜索优化
    
    # 📚 学术搜索策略
    academic_priority: bool = True         # 优先学术源
    high_impact_journals_only: bool = False  # 是否仅搜索高影响因子期刊
    recent_papers_weight: float = 1.2      # 近期论文权重加成
    
    # ⚡ 性能配置
    parallel_search: bool = True           # 并行搜索
    search_timeout: int = 30               # 搜索超时（秒）
    max_concurrent_searches: int = 3       # 最大并发搜索数
    
    # 🎯 质量控制
    min_citation_count: int = 0            # 最小引用数量要求
    min_publication_year: int = 2020       # 最小发表年份
    language_preference: List[str] = None  # 语言偏好
    
    def __post_init__(self):
        if self.language_preference is None:
            self.language_preference = ["en", "zh"]
    
    @classmethod
    def for_research_project(cls) -> "ResearchConfiguration":
        """科研项目标准配置"""
        return cls(
            max_search_results=12,
            search_rounds=3,
            enable_multi_source=True,
            academic_priority=True,
            parallel_search=True
        )
    
    @classmethod 
    def for_intensive_research(cls) -> "ResearchConfiguration":
        """高强度研究配置（更多搜索结果）"""
        return cls(
            max_search_results=20,
            pubmed_results=15,
            google_scholar_results=15,
            search_rounds=3,
            enable_multi_source=True,
            academic_priority=True,
            parallel_search=True,
            min_publication_year=2022  # 更严格的时间要求
        )
    
    @classmethod
    def for_medical_research(cls) -> "ResearchConfiguration":
        """医学研究专用配置"""
        return cls(
            max_search_results=15,
            pubmed_results=20,  # 医学研究优先PubMed
            google_scholar_results=8,
            search_rounds=3,
            enable_multi_source=True,
            academic_priority=True,
            high_impact_journals_only=True,
            min_citation_count=5
        )
    
    @classmethod
    def for_ai_research(cls) -> "ResearchConfiguration":
        """AI研究专用配置"""
        return cls(
            max_search_results=15,
            arxiv_results=12,  # AI研究优先ArXiv
            google_scholar_results=12,
            pubmed_results=5,
            search_rounds=3,
            enable_multi_source=True,
            academic_priority=True,
            min_publication_year=2023  # AI领域更新快，要求更近期
        )
    
    def get_search_strategy(self) -> Dict[str, Any]:
        """获取搜索策略配置"""
        return {
            "rounds": self.search_rounds,
            "multi_source": self.enable_multi_source,
            "parallel": self.parallel_search,
            "academic_priority": self.academic_priority,
            "timeout": self.search_timeout,
            "max_concurrent": self.max_concurrent_searches
        }
    
    def get_source_limits(self) -> Dict[str, int]:
        """获取各搜索源的结果数量限制"""
        return {
            "web_search": self.max_search_results,
            "pubmed": self.pubmed_results,
            "google_scholar": self.google_scholar_results,
            "arxiv": self.arxiv_results
        }
    
    def get_quality_filters(self) -> Dict[str, Any]:
        """获取质量过滤配置"""
        return {
            "min_citations": self.min_citation_count,
            "min_year": self.min_publication_year,
            "languages": self.language_preference,
            "high_impact_only": self.high_impact_journals_only,
            "recent_weight": self.recent_papers_weight
        }


class SimplifiedMultiRoundStrategy:
    """简化的多轮搜索策略"""
    
    def __init__(self, config: ResearchConfiguration):
        self.config = config
        self.round_strategies = [
            {"focus": "broad", "keywords": "general", "weight": 1.0},
            {"focus": "specific", "keywords": "technical", "weight": 1.2}, 
            {"focus": "latest", "keywords": "recent", "weight": 1.5}
        ]
    
    def get_round_config(self, round_num: int) -> Dict[str, Any]:
        """获取指定轮次的搜索配置"""
        if round_num < 1 or round_num > 3:
            raise ValueError("搜索轮次必须在1-3之间")
        
        strategy = self.round_strategies[round_num - 1]
        base_limits = self.config.get_source_limits()
        
        # 根据轮次调整搜索数量
        adjusted_limits = {}
        for source, limit in base_limits.items():
            adjusted_limits[source] = int(limit * strategy["weight"])
        
        return {
            "round": round_num,
            "strategy": strategy,
            "limits": adjusted_limits,
            "filters": self.config.get_quality_filters()
        }
    
    def should_continue_search(self, round_num: int, results_quality: float) -> bool:
        """判断是否继续搜索（简化版本）"""
        # 🎯 简化逻辑：固定3轮，不依赖复杂的质量评估
        return round_num < 3
    
    def get_search_summary(self) -> Dict[str, Any]:
        """获取搜索策略摘要"""
        return {
            "total_rounds": 3,
            "strategy": "fixed_3_rounds",
            "total_results": sum(self.config.get_source_limits().values()) * 3,
            "sources": list(self.config.get_source_limits().keys()),
            "parallel": self.config.parallel_search
        }


def create_research_optimized_config(
    research_type: str = "general",
    intensity: str = "standard"
) -> ResearchConfiguration:
    """
    创建针对研究优化的配置
    
    Args:
        research_type: 研究类型 ("general", "medical", "ai")
        intensity: 搜索强度 ("standard", "intensive")
    
    Returns:
        ResearchConfiguration: 优化的研究配置
    """
    
    if research_type == "medical":
        base_config = ResearchConfiguration.for_medical_research()
    elif research_type == "ai":
        base_config = ResearchConfiguration.for_ai_research()
    else:
        base_config = ResearchConfiguration.for_research_project()
    
    if intensity == "intensive":
        # 提升搜索强度
        base_config.max_search_results *= 2
        base_config.pubmed_results = int(base_config.pubmed_results * 1.5)
        base_config.google_scholar_results = int(base_config.google_scholar_results * 1.5)
    
    logger.info(f"🔬 创建{research_type}研究配置，强度：{intensity}")
    logger.info(f"📊 搜索配置：{base_config.get_source_limits()}")
    
    return base_config


def patch_system_with_research_config(config: ResearchConfiguration):
    """
    使用研究配置修补系统默认设置
    
    这个函数会修改系统的默认搜索配置，让所有搜索都使用更高的结果数量
    """
    
    # 修改默认配置
    from src.config.configuration import Configuration
    
    # 创建修补函数
    original_from_runnable_config = Configuration.from_runnable_config
    
    @classmethod
    def patched_from_runnable_config(cls, config_input=None):
        """修补后的配置创建方法"""
        original_config = original_from_runnable_config(config_input)
        
        # 应用研究优化配置
        original_config.max_search_results = config.max_search_results
        original_config.max_plan_iterations = 1  # 保持简单
        original_config.max_step_num = 5  # 增加步骤数量
        
        logger.info(f"🔧 已应用研究优化配置：max_search_results={config.max_search_results}")
        return original_config
    
    # 应用修补
    Configuration.from_runnable_config = patched_from_runnable_config
    
    logger.info("✅ 系统已修补为研究优化配置")


# 🎯 预定义的研究配置实例
STANDARD_RESEARCH_CONFIG = ResearchConfiguration.for_research_project()
INTENSIVE_RESEARCH_CONFIG = ResearchConfiguration.for_intensive_research()
MEDICAL_RESEARCH_CONFIG = ResearchConfiguration.for_medical_research()
AI_RESEARCH_CONFIG = ResearchConfiguration.for_ai_research()

# 🚀 自动应用优化配置（可选）
def auto_apply_research_optimization():
    """自动应用研究优化配置"""
    patch_system_with_research_config(STANDARD_RESEARCH_CONFIG)
    logger.info("🚀 已自动应用标准研究优化配置")


if __name__ == "__main__":
    # 测试配置
    config = ResearchConfiguration.for_research_project()
    strategy = SimplifiedMultiRoundStrategy(config)
    
    print("🔬 科研优化配置测试")
    print(f"📊 搜索源限制: {config.get_source_limits()}")
    print(f"🔄 搜索策略: {strategy.get_search_summary()}")
    print(f"🎯 第1轮配置: {strategy.get_round_config(1)}")
    print(f"🎯 第2轮配置: {strategy.get_round_config(2)}")
    print(f"🎯 第3轮配置: {strategy.get_round_config(3)}") 
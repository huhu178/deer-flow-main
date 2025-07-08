# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
客观质量控制系统
================

替代不可靠的LLM自评，使用客观指标进行质量控制：
1. 🔍 基于内容长度和结构的质量评估
2. 📊 基于关键词覆盖度的完整性评估  
3. ⏱️ 基于轮次和时间的合理性控制
4. 🎯 基于用户反馈的实际效果评估

核心原则：
- ❌ 不依赖LLM自评分数
- ✅ 使用可验证的客观指标
- ✅ 简单、可靠、可调试
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ObjectiveQualityMetrics:
    """客观质量指标"""
    content_length: int = 0              # 内容长度
    key_sections_count: int = 0          # 关键部分数量
    keyword_coverage_score: float = 0.0  # 关键词覆盖度
    structure_completeness: float = 0.0  # 结构完整性
    time_spent_seconds: float = 0.0      # 处理时间
    round_number: int = 0                # 轮次编号
    
    def get_overall_score(self) -> float:
        """计算综合质量分数"""
        # 基于客观指标的加权评分
        length_score = min(self.content_length / 500, 1.0) * 0.3  # 长度分数
        section_score = min(self.key_sections_count / 3, 1.0) * 0.3  # 结构分数
        keyword_score = self.keyword_coverage_score * 0.2  # 关键词分数
        structure_score = self.structure_completeness * 0.2  # 完整性分数
        
        return length_score + section_score + keyword_score + structure_score


class ObjectiveQualityController:
    """客观质量控制器"""
    
    def __init__(self):
        # 🔍 研究领域关键词库
        self.research_keywords = {
            "ai": ["人工智能", "ai", "machine learning", "深度学习", "神经网络", "算法"],
            "medical": ["医学", "医疗", "健康", "诊断", "治疗", "临床", "病理"],
            "imaging": ["影像", "图像", "dxa", "ct", "mri", "x-ray", "超声"],
            "data": ["数据", "dataset", "特征", "标注", "训练", "测试", "验证"],
            "system": ["系统", "平台", "框架", "架构", "开发", "部署", "应用"]
        }
        
        # 📋 必需的计划结构组件
        self.required_plan_sections = [
            "title", "thought", "steps", "locale"
        ]
        
        # 🎯 研究步骤类型
        self.valid_step_types = [
            "research", "analysis", "processing", "writing"
        ]
    
    def evaluate_understanding_quality(
        self, 
        user_input: str, 
        ai_response: str,
        round_num: int,
        processing_time: float = 0.0
    ) -> ObjectiveQualityMetrics:
        """评估理解质量 - 基于客观指标"""
        
        logger.info(f"🔍 客观质量评估 - 理解阶段第{round_num}轮")
        
        # 1. 内容长度评估
        content_length = len(ai_response)
        
        # 2. 关键词覆盖度评估
        keyword_coverage = self._calculate_keyword_coverage(user_input, ai_response)
        
        # 3. 结构完整性评估（理解阶段）
        structure_score = self._evaluate_understanding_structure(ai_response)
        
        # 4. 关键部分计数
        key_sections = self._count_understanding_sections(ai_response)
        
        metrics = ObjectiveQualityMetrics(
            content_length=content_length,
            key_sections_count=key_sections,
            keyword_coverage_score=keyword_coverage,
            structure_completeness=structure_score,
            time_spent_seconds=processing_time,
            round_number=round_num
        )
        
        overall_score = metrics.get_overall_score()
        logger.info(f"📊 理解质量评估结果: {overall_score:.2f}")
        logger.info(f"   - 内容长度: {content_length} 字符")
        logger.info(f"   - 关键词覆盖: {keyword_coverage:.2f}")
        logger.info(f"   - 结构完整: {structure_score:.2f}")
        logger.info(f"   - 关键部分: {key_sections} 个")
        
        return metrics
    
    def evaluate_planning_quality(
        self,
        plan_data: Dict[str, Any],
        user_input: str,
        round_num: int,
        processing_time: float = 0.0
    ) -> ObjectiveQualityMetrics:
        """评估规划质量 - 基于客观指标"""
        
        logger.info(f"📋 客观质量评估 - 规划阶段第{round_num}轮")
        
        # 1. 计划内容长度
        plan_text = str(plan_data)
        content_length = len(plan_text)
        
        # 2. 关键词覆盖度
        keyword_coverage = self._calculate_keyword_coverage(user_input, plan_text)
        
        # 3. 计划结构完整性
        structure_score = self._evaluate_plan_structure(plan_data)
        
        # 4. 关键组件计数
        key_sections = self._count_plan_sections(plan_data)
        
        metrics = ObjectiveQualityMetrics(
            content_length=content_length,
            key_sections_count=key_sections,
            keyword_coverage_score=keyword_coverage,
            structure_completeness=structure_score,
            time_spent_seconds=processing_time,
            round_number=round_num
        )
        
        overall_score = metrics.get_overall_score()
        logger.info(f"📊 规划质量评估结果: {overall_score:.2f}")
        logger.info(f"   - 计划长度: {content_length} 字符")
        logger.info(f"   - 关键词覆盖: {keyword_coverage:.2f}")
        logger.info(f"   - 结构完整: {structure_score:.2f}")
        logger.info(f"   - 关键组件: {key_sections} 个")
        
        return metrics
    
    def should_continue_processing(
        self,
        metrics: ObjectiveQualityMetrics,
        max_rounds: int,
        min_quality_threshold: float = 0.4  # 🔧 基于客观指标的阈值
    ) -> Tuple[bool, str]:
        """
        判断是否应该继续处理 - 基于客观指标
        
        Returns:
            (should_continue, reason)
        """
        
        # 1. 轮次限制（硬性条件）
        if metrics.round_number >= max_rounds:
            return False, f"达到最大轮次限制 ({max_rounds})"
        
        # 2. 质量达标（基于客观指标）
        overall_score = metrics.get_overall_score()
        if overall_score >= min_quality_threshold:
            return False, f"质量达标 ({overall_score:.2f} >= {min_quality_threshold})"
        
        # 3. 内容长度检查
        if metrics.content_length < 50:
            return True, "内容过短，需要补充"
        
        # 4. 结构完整性检查
        if metrics.structure_completeness < 0.5:
            return True, "结构不完整，需要改进"
        
        # 5. 关键词覆盖度检查
        if metrics.keyword_coverage_score < 0.3:
            return True, "关键词覆盖不足，需要完善"
        
        # 默认：质量未达标，继续处理
        return True, f"质量未达标 ({overall_score:.2f} < {min_quality_threshold})"
    
    def _calculate_keyword_coverage(self, user_input: str, ai_response: str) -> float:
        """计算关键词覆盖度"""
        user_lower = user_input.lower()
        response_lower = ai_response.lower()
        
        total_keywords = 0
        covered_keywords = 0
        
        for category, keywords in self.research_keywords.items():
            for keyword in keywords:
                total_keywords += 1
                # 如果用户输入包含该关键词
                if keyword.lower() in user_lower:
                    # 检查AI响应是否也包含
                    if keyword.lower() in response_lower:
                        covered_keywords += 1
        
        return covered_keywords / total_keywords if total_keywords > 0 else 0.0
    
    def _evaluate_understanding_structure(self, ai_response: str) -> float:
        """评估理解阶段的结构完整性"""
        score = 0.0
        
        # 检查是否包含关键理解要素
        understanding_indicators = [
            r"理解|understand|comprehend",
            r"需求|requirement|need",
            r"目标|goal|objective",
            r"方法|method|approach",
            r"步骤|step|process"
        ]
        
        for indicator in understanding_indicators:
            if re.search(indicator, ai_response, re.IGNORECASE):
                score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_plan_structure(self, plan_data: Dict[str, Any]) -> float:
        """评估计划结构完整性"""
        if not isinstance(plan_data, dict):
            return 0.0
        
        score = 0.0
        
        # 检查必需的计划组件
        for section in self.required_plan_sections:
            if section in plan_data and plan_data[section]:
                score += 0.25
        
        # 检查步骤的质量
        steps = plan_data.get("steps", [])
        if isinstance(steps, list) and len(steps) > 0:
            valid_steps = 0
            for step in steps:
                if isinstance(step, dict):
                    # 检查步骤是否包含必要字段
                    if all(field in step for field in ["step_type", "title", "description"]):
                        # 检查步骤类型是否有效
                        if step.get("step_type") in self.valid_step_types:
                            valid_steps += 1
            
            if valid_steps > 0:
                score += min(valid_steps / len(steps), 0.25)
        
        return min(score, 1.0)
    
    def _count_understanding_sections(self, ai_response: str) -> int:
        """计算理解阶段的关键部分数量"""
        sections = 0
        
        # 使用更宽松的模式匹配
        section_patterns = [
            r"理解|understand",
            r"分析|analysis", 
            r"建议|suggestion",
            r"问题|question",
            r"方案|solution"
        ]
        
        for pattern in section_patterns:
            if re.search(pattern, ai_response, re.IGNORECASE):
                sections += 1
        
        return sections
    
    def _count_plan_sections(self, plan_data: Dict[str, Any]) -> int:
        """计算计划的关键组件数量"""
        if not isinstance(plan_data, dict):
            return 0
        
        sections = 0
        
        # 检查基本组件
        basic_components = ["title", "thought", "steps"]
        for component in basic_components:
            if component in plan_data and plan_data[component]:
                sections += 1
        
        # 检查步骤数量
        steps = plan_data.get("steps", [])
        if isinstance(steps, list):
            sections += min(len(steps), 3)  # 最多加3分
        
        return sections


class SimplifiedQualityController:
    """简化的质量控制器 - 极简版本"""
    
    def __init__(self, max_rounds: int = 3):
        self.max_rounds = max_rounds
        self.objective_controller = ObjectiveQualityController()
    
    def should_continue_understanding(
        self, 
        user_input: str, 
        ai_response: str, 
        current_round: int
    ) -> Tuple[bool, str]:
        """简化的理解阶段继续判断"""
        
        # 🔧 极简策略：固定轮次，基于基本质量指标
        if current_round >= self.max_rounds:
            return False, f"达到最大轮次 ({self.max_rounds})"
        
        # 基本质量检查
        if len(ai_response) < 100:
            return True, "响应过短"
        
        # 检查是否包含基本理解要素
        has_understanding = any(keyword in ai_response.lower() for keyword in [
            "理解", "understand", "需求", "目标", "方法"
        ])
        
        if not has_understanding:
            return True, "缺少基本理解要素"
        
        return False, "基本质量达标"
    
    def should_continue_planning(
        self,
        plan_data: Dict[str, Any],
        user_input: str,
        current_round: int
    ) -> Tuple[bool, str]:
        """简化的规划阶段继续判断"""
        
        # 🔧 极简策略：固定轮次，基于基本结构检查
        if current_round >= self.max_rounds:
            return False, f"达到最大轮次 ({self.max_rounds})"
        
        # 基本结构检查
        if not isinstance(plan_data, dict):
            return True, "计划格式错误"
        
        required_fields = ["title", "steps"]
        for field in required_fields:
            if field not in plan_data or not plan_data[field]:
                return True, f"缺少必要字段: {field}"
        
        # 检查步骤数量和质量
        steps = plan_data.get("steps", [])
        if not isinstance(steps, list) or len(steps) < 2:
            return True, "步骤数量不足"
        
        return False, "基本结构完整"


# 🚀 便捷的工厂函数
def create_objective_quality_controller(mode: str = "simplified") -> Any:
    """
    创建质量控制器
    
    Args:
        mode: "simplified" (简化版) 或 "full" (完整版)
    """
    if mode == "simplified":
        return SimplifiedQualityController(max_rounds=3)
    else:
        return ObjectiveQualityController()


def patch_enhanced_nodes_with_objective_quality():
    """
    使用客观质量控制器修补增强节点
    
    这个函数会替换原有的基于LLM自评的质量控制逻辑
    """
    from src.graph import enhanced_planning_nodes
    
    # 创建客观质量控制器
    quality_controller = SimplifiedQualityController(max_rounds=3)
    
    # 修补理解节点的继续判断逻辑
    original_should_continue_understanding = enhanced_planning_nodes.EnhancedCoordinatorNode._should_continue_understanding
    
    def patched_should_continue_understanding(self, result, round_num):
        """使用客观指标的继续判断"""
        # 提取必要信息
        user_input = getattr(self, '_current_user_input', '')
        ai_response = result.thinking_process or ''
        
        should_continue, reason = quality_controller.should_continue_understanding(
            user_input, ai_response, round_num
        )
        
        logger.info(f"🔍 客观质量判断: {reason}")
        return should_continue
    
    # 应用修补
    enhanced_planning_nodes.EnhancedCoordinatorNode._should_continue_understanding = patched_should_continue_understanding
    
    logger.info("✅ 已应用客观质量控制修补")


if __name__ == "__main__":
    # 测试客观质量控制
    controller = ObjectiveQualityController()
    
    # 测试理解质量评估
    user_input = "开发一个基于AI的DXA影像分析系统"
    ai_response = "我理解您需要开发一个人工智能驱动的DXA影像分析系统，用于骨密度检测和健康预测。"
    
    metrics = controller.evaluate_understanding_quality(user_input, ai_response, 1)
    print(f"理解质量评分: {metrics.get_overall_score():.2f}")
    
    # 测试规划质量评估
    plan_data = {
        "title": "AI-DXA影像分析系统开发计划",
        "thought": "详细的开发思路",
        "steps": [
            {"step_type": "research", "title": "技术调研", "description": "调研相关技术"},
            {"step_type": "analysis", "title": "需求分析", "description": "分析具体需求"}
        ]
    }
    
    plan_metrics = controller.evaluate_planning_quality(plan_data, user_input, 1)
    print(f"规划质量评分: {plan_metrics.get_overall_score():.2f}")
    
    print("✅ 客观质量控制测试完成") 
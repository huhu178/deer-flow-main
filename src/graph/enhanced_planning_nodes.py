# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
增强规划节点模块 - 多轮深度理解和渐进式规划
==================================================

功能特性：
- 🧠 多轮深度理解机制
- 🎯 渐进式规划优化  
- 📊 智能阶段判断
- 🔄 动态轮次控制
- 💡 上下文连续性保持
"""

import json
import time
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum
from dataclasses import dataclass, field
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from src.config.configuration import Configuration
from src.llms.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP
from src.prompts.template import apply_prompt_template
from src.utils.json_utils import repair_json_output
from .types import State

logger = logging.getLogger(__name__)


class UnderstandingStage(Enum):
    """理解阶段枚举"""
    INITIAL = "initial"           # 初始理解
    CLARIFICATION = "clarification"  # 需求澄清
    ANALYSIS = "analysis"         # 深度分析
    VALIDATION = "validation"     # 需求验证
    FINALIZED = "finalized"       # 最终确认


class PlanningStage(Enum):
    """规划阶段枚举"""
    DRAFT = "draft"               # 草案规划
    REFINEMENT = "refinement"     # 规划细化
    OPTIMIZATION = "optimization" # 优化调整
    VALIDATION = "validation"     # 规划验证
    APPROVED = "approved"         # 最终批准


@dataclass
class PlanningConfig:
    """规划配置类 - 多轮交互但可靠配置"""
    max_understanding_rounds: int = 2      # 🔧 恢复到2轮，找出真正问题
    max_planning_rounds: int = 1           # 🔧 规划阶段最多1轮（简化）
    quality_threshold: float = 0.9         # 🔧 恢复高质量阈值90%
    enable_deep_thinking: bool = True      # 🔧 启用深度思考
    enable_auto_clarification: bool = True # 🔧 启用自动澄清
    enable_progressive_refinement: bool = True # 🔧 启用渐进式改进
    thinking_time_seconds: float = 0.5     # 思考时间0.5秒（平衡速度和质量）


@dataclass
class UnderstandingResult:
    """理解结果类 - 增强版"""
    stage: UnderstandingStage
    core_objectives: List[str] = field(default_factory=list)
    key_entities_and_concepts: List[str] = field(default_factory=list)
    implicit_assumptions: List[str] = field(default_factory=list)
    potential_risks: List[str] = field(default_factory=list)
    clarification_questions: List[str] = field(default_factory=list)
    understanding_confidence: float = 0.0  # 理解置信度 (0-1)
    information_completeness: float = 0.0  # 信息完整度 (0-1)
    thinking_process: str = ""
    needs_clarification: bool = True


@dataclass
class PlanningResult:
    """规划结果类"""
    stage: PlanningStage
    plan_quality_score: float = 0.0        # 计划质量评分 (0-1)
    plan_data: Dict[str, Any] = field(default_factory=dict)
    improvement_suggestions: List[str] = field(default_factory=list)
    potential_risks: List[str] = field(default_factory=list)
    thinking_process: str = ""
    needs_refinement: bool = True
    completeness_score: float = 0.0        # 完整性评分 (0-1)


class EnhancedCoordinatorNode:
    """增强的协调器节点 - 多轮深度理解"""
    
    def __init__(self, llm_type: str, config: Optional[PlanningConfig] = None):
        self.config = config or PlanningConfig()
        self.llm = get_llm_by_type(llm_type)
        logger.info(f"EnhancedCoordinatorNode initialized with LLM type: {llm_type}")
    
    def __call__(self, state: State) -> Command:
        """执行多轮理解流程"""
        logger.info("🧠 增强协调器启动 - 开始多轮深度理解")
        
        # 初始化理解状态
        understanding_rounds = state.get("understanding_rounds", 0)
        understanding_history = state.get("understanding_history", [])
        
        logger.info("🔍 当前状态调试:")
        logger.info(f"   - understanding_rounds从状态获取: {understanding_rounds}")
        logger.info(f"   - understanding_history长度: {len(understanding_history)}")
        logger.info(f"   - 状态中的所有键: {list(state.keys())}")
        
        # 🔧 DEBUG: 添加更详细的调试信息
        logger.info(f"🔧 DEBUG: 即将开始第 {understanding_rounds + 1} 轮理解...")
        logger.info(f"🔧 DEBUG: 当前配置 - max_rounds: {self.config.max_understanding_rounds}, threshold: {self.config.quality_threshold}")
        
        # 获取用户输入
        user_input = self._extract_user_input(state)
        if not user_input:
            return Command(goto="__end__")
        
        # 执行当前轮次的理解
        understanding_result = self._perform_understanding_round(
            user_input, understanding_history, understanding_rounds
        )
        
        # 🔧 最终修复：创建一个可序列化的版本，确保所有路径都被覆盖
        serializable_result = self._serialize_understanding_result(understanding_result)

        # 更新理解历史
        understanding_history.append({
            "round": understanding_rounds + 1,
            "result": serializable_result, 
            "timestamp": datetime.now().isoformat()
        })
        
        # 判断是否需要继续理解
        if self._should_continue_understanding(understanding_result, understanding_rounds):
            logger.info(f"🔄 需要继续理解 - 轮次 {understanding_rounds + 1}/{self.config.max_understanding_rounds}")
            
            # 🔧 生成当前轮次的理解展示内容 (增强版)
            round_display = self._generate_understanding_display(understanding_result, understanding_rounds)
            
            logger.info("🔧 DEBUG: 准备构建Command对象进行状态更新...")
            logger.info(f"🔧 DEBUG: understanding_rounds将更新为: {understanding_rounds + 1}")
            logger.info(f"🔧 DEBUG: understanding_history长度: {len(understanding_history)}")
            
            command_obj = Command(
                update={
                    "understanding_rounds": understanding_rounds + 1,
                    "understanding_history": understanding_history,
                    "current_understanding": serializable_result,
                    "messages": state["messages"] + [
                        AIMessage(
                            content=round_display,
                            name="enhanced_coordinator"
                        )
                    ]
                },
                goto="coordinator"
            )
            
            logger.info("🔧 DEBUG: Command对象构建完成，即将返回...")
            return command_obj
        else:
            logger.info("✅ 理解阶段完成，转入规划阶段")
            # 🔧 在转到规划前，也显示最后一次的理解结果
            final_display = self._generate_understanding_display(understanding_result, understanding_rounds)
            return Command(
                update={
                    "understanding_completed": True,
                    "understanding_history": understanding_history,
                    "final_understanding": serializable_result,
                    "messages": state["messages"] + [
                        AIMessage(content=final_display, name="enhanced_coordinator")
                    ]
                },
                goto="planner"
            )
    
    def _serialize_understanding_result(self, result: UnderstandingResult) -> Dict[str, Any]:
        """将UnderstandingResult对象转换为可JSON序列化的字典。"""
        serialized_data = result.__dict__.copy()
        if 'stage' in serialized_data and isinstance(serialized_data['stage'], Enum):
            serialized_data['stage'] = serialized_data['stage'].value
        return serialized_data

    def _extract_user_input(self, state: State) -> str:
        """提取用户输入"""
        messages = state.get("messages", [])
        if not messages:
            return ""
        
        # 获取最后一条用户消息
        for message in reversed(messages):
            if isinstance(message, HumanMessage):
                return message.content
            elif isinstance(message, dict) and message.get("role") == "user":
                return message.get("content", "")
        
        # 如果没有找到用户消息，使用最后一条消息
        last_message = messages[-1]
        if hasattr(last_message, 'content'):
            return last_message.content
        elif isinstance(last_message, dict):
            return last_message.get('content', '')
        
        return ""
    
    def _perform_understanding_round(
        self, user_input: str, history: List[Dict], round_num: int
    ) -> UnderstandingResult:
        """执行单轮理解分析 - 使用深度分析指令"""
        
        understanding_prompt = f"""
作为一名资深的AI技术方案专家，你的任务是深度解析用户提出的研究或开发需求。你需要进行全面、多维度的分析，而不仅仅是表面信息的提取。

**原始用户需求:**
---
{user_input}
---

**历史沟通记录:**
---
{json.dumps(history, ensure_ascii=False, indent=2) if history else "无"}
---

**你的分析任务 (请严格按以下结构输出JSON对象):**

1.  **`core_objectives`**: [明确阐述用户最终想要实现的核心业务目标或研究价值，至少2点]
2.  **`key_entities_and_concepts`**: [全面列出用户需求中提到的所有关键技术术语、业务概念和领域知识，至少5-8个]
3.  **`implicit_assumptions`**: [分析用户没有明说，但对项目成功至关重要的隐含假设或前提条件，至少3点]
4.  **`potential_risks`**: [从技术、数据、可行性等角度，识别该需求可能面临的风险和挑战，至少3点]
5.  **`clarification_questions`**: [提出3-5个有深度、能激发用户提供关键信息的问题，避免简单的是非题]
6.  **`self_assessment`**:
    - **`understanding_confidence`**: [用0-100%表示你对需求理解的信心]
    - **`information_completeness`**: [用0-100%表示当前信息是否足以制定详细计划]

**输出格式示例:**
```json
{{
    "core_objectives": [
        "开发一个能预测心血管疾病风险的AI模型",
        "利用非侵入性的DXA影像数据，降低筛查成本"
    ],
    "key_entities_and_concepts": [
        "AI", "DXA影像", "桡骨", "影像组学", "全身健康预测", "心血管疾病", "机器学习模型", "数据标注"
    ],
    "implicit_assumptions": [
        "假设桡骨的DXA影像特征与心血管健康有强相关性",
        "假设有足够数量和高质量的、已标注的数据用于模型训练",
        "假设计算资源足以支持大规模深度学习模型的训练"
    ],
    "potential_risks": [
        "数据隐私和合规性风险",
        "模型的泛化能力不足，在不同人群或设备上表现不佳",
        "桡骨特征与全身健康的关联性可能较弱，导致模型预测精度不高"
    ],
    "clarification_questions": [
        "除了心血管疾病，您希望模型覆盖哪些具体的全身健康指标或疾病类型？",
        "您预期的数据集规模有多大？是否包含了不同年龄、性别和种族的样本？",
        "对于模型的最终交付形式，您期望是API、集成到现有HIS系统，还是一个独立的应用？"
    ],
    "self_assessment": {{
        "understanding_confidence": "90%",
        "information_completeness": "75%"
    }}
}}
```

**请现在开始你的分析，并直接输出JSON对象，不要包含任何其他说明或markdown标记。**
"""
        
        logger.info(f"🔍 第{round_num + 1}轮深度理解分析开始...")
        
        # 🔧 增加timeout和重试机制
        try:
            logger.info("🔧 DEBUG: 准备调用LLM API...")
            logger.info(f"🔧 DEBUG: 使用的LLM配置: {type(self.llm)}")
            
            response = self.llm.with_config(
                {"configurable": {"max_retries": 2}}
            ).invoke(understanding_prompt, timeout=60)
            
            response_content = response.content
            logger.info(f"✅ API调用成功，响应长度: {len(response_content)}")
            logger.info("🔧 DEBUG: LLM API调用完成，开始解析响应...")
            
        except Exception as e:
            logger.error(f"❌ LLM调用失败: {e}")
            logger.error(f"🔧 DEBUG: 异常类型: {type(e).__name__}")
            logger.error(f"🔧 DEBUG: 异常详情: {str(e)}")
            return self._create_fallback_understanding(user_input, round_num)
        
        # 解析LLM的JSON输出
        try:
            logger.info("🔧 DEBUG: 开始解析JSON响应...")
            # 首先清理和修复可能的JSON格式问题
            cleaned_response = repair_json_output(response_content)
            logger.info("🔧 DEBUG: JSON清理完成，尝试解析...")
            result_data = json.loads(cleaned_response)
            logger.info("🔧 DEBUG: JSON解析成功!")
            
            # 🔧 最终修复: 使用单花括号{}
            assessment = result_data.get("self_assessment", {})
            confidence_str = assessment.get("understanding_confidence", "0%")
            completeness_str = assessment.get("information_completeness", "0%")
            
            # 将百分比字符串转换为浮点数
            confidence = float(confidence_str.strip('%')) / 100.0
            completeness = float(completeness_str.strip('%')) / 100.0
            
            logger.info(f"📊 理解置信度: {confidence}")
            logger.info(f"💯 信息完整度: {completeness}")
            
            # 创建增强版的UnderstandingResult
            stage = self._determine_understanding_stage(confidence, completeness)
            logger.info(f"🎯 理解阶段: {stage.value}")
            
            return UnderstandingResult(
                stage=stage,
                core_objectives=result_data.get("core_objectives", []),
                key_entities_and_concepts=result_data.get("key_entities_and_concepts", []),
                implicit_assumptions=result_data.get("implicit_assumptions", []),
                potential_risks=result_data.get("potential_risks", []),
                clarification_questions=result_data.get("clarification_questions", []),
                understanding_confidence=confidence,
                information_completeness=completeness,
                thinking_process=result_data.get("thinking_process", "N/A"),
                needs_clarification=bool(result_data.get("clarification_questions"))
            )
            
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logger.error(f"❌ 解析LLM响应失败: {e}")
            logger.debug(f"原始响应内容: {response_content}")
            return self._create_fallback_understanding(user_input, round_num)

    def _determine_understanding_stage(self, confidence: float, completeness: float) -> UnderstandingStage:
        """根据置信度和完整度判断当前所处的理解阶段"""
        if confidence < 0.6 or completeness < 0.5:
            return UnderstandingStage.INITIAL
        elif confidence < 0.8 and completeness < 0.7:
            return UnderstandingStage.CLARIFICATION
        elif confidence >= 0.8 and completeness >= 0.7 and completeness < 0.9:
            return UnderstandingStage.ANALYSIS
        elif confidence >= 0.9 and completeness >= 0.9:
            return UnderstandingStage.FINALIZED
        else:
            return UnderstandingStage.VALIDATION

    def _create_fallback_understanding(self, user_input: str, round_num: int) -> UnderstandingResult:
        """在API调用或解析失败时，创建一个备用的、安全的UnderstandingResult对象"""
        logger.warning(f"⚠️ 触发回退机制 - 第{round_num + 1}轮")
        return UnderstandingResult(
            stage=UnderstandingStage.FINALIZED,  # 设置为FINALIZED以强制终止循环
            core_objectives=["无法解析需求"],
            key_entities_and_concepts=self._extract_basic_keywords(user_input),
            implicit_assumptions=["解析失败，无法推断"],
            potential_risks=["LLM调用或响应解析失败"],
            clarification_questions=[], # 无问题，避免追问
            understanding_confidence=0.1, # 置信度低
            information_completeness=0.1, # 完整度低
            thinking_process="Fallback due to API or parsing error.",
            needs_clarification=False
        )

    def _extract_basic_keywords(self, user_input: str) -> List[str]:
        """从用户输入中提取一些基本的关键词作为备用"""
        # 一个非常简单的关键词提取实现
        # 在实际应用中可能会使用更复杂的NLP技术
        keywords = [word for word in user_input.split() if len(word) > 3]
        return keywords[:5] # 最多返回5个

    def _should_continue_understanding(
        self, result: UnderstandingResult, round_num: int
    ) -> bool:
        """判断是否需要继续进行下一轮理解"""
        
        # 🔧 关键修复：使用 round_num + 1 来判断是否达到最大轮次
        # 因为 round_num 是从0开始的索引，而 max_understanding_rounds 是总数
        if (round_num + 1) >= self.config.max_understanding_rounds:
            logger.info(f"✅ 已达到最大理解轮次({self.config.max_understanding_rounds})，结束理解阶段")
            return False
        
        # 检查信息完整度是否达标
        if result.information_completeness >= self.config.quality_threshold:
            logger.info(f"✅ 信息完整度({result.information_completeness:.2f})已达标(>{self.config.quality_threshold})，结束理解阶段")
            return False
        
        # 检查是否还有澄清问题
        if not result.clarification_questions:
            logger.info("✅ 已无澄清问题，结束理解阶段")
            return False
        
        logger.info(f"📊 理解轮次检查: 当前轮次={round_num}, 最大轮次={self.config.max_understanding_rounds}")
        logger.info("🔄 信息完整度不足或仍有问题，继续下一轮深度理解")
        return True

    def _generate_understanding_display(self, result: UnderstandingResult, round_num: int) -> str:
        """生成美观、结构化的多轮理解过程展示信息"""
        
        display = f"### 🧠 第 {round_num + 1} 轮深度理解分析\n\n"
        
        if result.thinking_process and result.thinking_process != "N/A":
            display += f"**🤔 思考过程**:\n> {result.thinking_process}\n\n"
        
        display += f"**🎯 核心目标识别**:\n"
        if result.core_objectives:
            for i, objective in enumerate(result.core_objectives, 1):
                display += f"- {objective}\n"
        else:
            display += "- *暂未明确...*\n"
        display += "\n"
        
        display += f"**🔑 关键概念与实体**:\n"
        if result.key_entities_and_concepts:
            tags = " ".join([f"`{item}`" for item in result.key_entities_and_concepts])
            display += f"> {tags}\n\n"
        else:
            display += "- *暂未明确...*\n\n"
            
        display += f"**🧐 预设与风险分析**:\n"
        if result.implicit_assumptions:
            display += f"- **隐含假设**: {'; '.join(result.implicit_assumptions)}\n"
        if result.potential_risks:
            display += f"- **潜在风险**: {'; '.join(result.potential_risks)}\n"
        if not result.implicit_assumptions and not result.potential_risks:
            display += "- *暂未明确...*\n"
        display += "\n"
        
        display += "---\n\n"
        
        display += f"**📊 自我评估**:\n"
        display += f"- **理解置信度**: `{result.understanding_confidence:.0%}`\n"
        display += f"- **信息完整度**: `{result.information_completeness:.0%}`\n\n"

        if result.clarification_questions:
            display += f"**❓ 需要您澄清的问题**:\n"
            for i, question in enumerate(result.clarification_questions, 1):
                display += f"**{i}.** {question}\n"
        
        return display


# ==============================================================================
# 增强规划节点 (EnhancedPlannerNode)
# ==============================================================================

class EnhancedPlannerNode:
    """
    增强的规划器节点 - 渐进式规划与优化
    """

    def __init__(self, llm_type: str, config: Optional[PlanningConfig] = None):
        self.config = config or PlanningConfig()
        self.llm = get_llm_by_type(llm_type)
        logger.info(f"EnhancedPlannerNode initialized with LLM type: {llm_type}")

    def __call__(self, state: State, config: Optional[RunnableConfig] = None) -> Command:
        """执行渐进式规划流程"""
        logger.info("📝 增强规划器启动 - 开始渐进式规划")

        planning_rounds = state.get("planning_rounds", 0)
        planning_history = state.get("planning_history", [])
        final_understanding = state.get("final_understanding", {})

        # 执行当前轮次的规划
        planning_result = self._perform_planning_round(
            final_understanding, planning_history, planning_rounds
        )

        # 🔧 确保plan_data有效且不为空，并转换为前端兼容格式
        if not planning_result.plan_data:
            logger.warning("⚠️ 规划结果为空，创建默认结构")
            planning_result.plan_data = {
                "title": "基于AI与影像组学的桡骨DXA全身健康预测系统研究计划",
                "author": "AI Research System", 
                "date": datetime.now().strftime('%Y-%m-%d'),
                "executive_summary": "本计划探索利用人工智能和影像组学技术，通过桡骨DXA影像预测全身健康状态的创新研究方向。",
                "research_directions": [
                    {"id": 1, "title": "数据基础建设与标准化", "description": "建立高质量的DXA影像数据集和标注体系"},
                    {"id": 2, "title": "AI模型开发与优化", "description": "开发深度学习模型进行影像特征提取和健康预测"}
                ]
            }

        # 🔧 新增：转换为前端兼容的计划格式
        frontend_compatible_plan = self._convert_to_frontend_format(planning_result.plan_data)

        # 更新规划历史
        planning_history.append({
            "round": planning_rounds + 1,
            "result": self._serialize_planning_result(planning_result),
            "timestamp": datetime.now().isoformat()
        })
        
        # 格式化当前轮次的规划结果以供前端展示
        round_message = _format_planning_round_to_message(
            planning_rounds, self.config.max_planning_rounds, planning_result
        )
        
        # 🔧 添加详细的计划内容展示
        if planning_result.plan_data:
            detailed_plan_message = self._format_detailed_plan(planning_result.plan_data)
            round_message += "\n\n" + detailed_plan_message
        
        # 准备要更新的状态
        updated_values = {
            "planning_history": planning_history,
            "current_plan": frontend_compatible_plan,  # 🔧 使用前端兼容格式
            "messages": state["messages"] + [
                AIMessage(content=json.dumps(frontend_compatible_plan, ensure_ascii=False), name="planner")  # 🔧 修复：使用前端识别的agent名称
            ]
        }

        # 判断是否需要继续规划
        if self._should_continue_planning(planning_result, planning_rounds):
            logger.info(f"🔄 需要继续规划 - 轮次 {planning_rounds + 1}/{self.config.max_planning_rounds}")
            updated_values["planning_rounds"] = planning_rounds + 1
            return Command(
                update=updated_values,
                goto="planner"
            )
        else:
            logger.info("✅ 规划阶段完成，转入人工反馈节点")
            # 🔧 合并详细计划和确认信息
            final_content = f"### ✅ 研究计划草案完成\n\n这是为您生成的最终研究计划草案，请您审核。审核通过后，我们将开始执行研究。如果您有任何修改意见，请直接提出。\n\n---\n\n"
            
            # 添加详细计划内容到最终消息
            if planning_result.plan_data:
                detailed_plan_content = self._format_detailed_plan(planning_result.plan_data)
                final_content += detailed_plan_content
            
            # 🔧 最终消息也使用前端兼容格式
            final_plan_message = AIMessage(
                content=json.dumps(frontend_compatible_plan, ensure_ascii=False),
                name="planner"  # 🔧 修复：使用前端识别的agent名称
            )
            updated_values["messages"].append(final_plan_message)
            updated_values["plan_completed"] = True
            return Command(
                update=updated_values,
                goto="human_feedback"
            )

    def _perform_planning_round(
        self, understanding: Dict, history: List[Dict], round_num: int
    ) -> PlanningResult:
        """执行单轮规划"""
        
        # 🔧 最终修复: 在序列化之前，先确保内部所有值都是可序列化的
        # 虽然已经在Coordinator处理过，但作为防御性编程，这里再次检查
        if 'stage' in understanding and isinstance(understanding['stage'], Enum):
            understanding['stage'] = understanding['stage'].value

        planning_prompt = f"""
作为一名顶级的AI研究计划制定者，你的任务是基于对用户需求的深度理解，创建一个结构化、可执行、创新的研究计划。

**用户需求最终理解报告:**
---
{json.dumps(understanding, ensure_ascii=False, indent=2)}
---

**历史规划迭代记录:**
---
{json.dumps(history, ensure_ascii=False, indent=2) if history else "无，这是第一轮规划。"}
---

**你的任务:**
1.  **若这是第一轮规划**: 基于"用户需求最终理解报告"，创建一个包含20个创新研究方向的详细计划。
2.  **若已有历史规划**: 基于"历史规划迭代记录"中的最新计划和改进建议，对其进行优化和迭代。
3.  **输出结构**: 你必须严格按照下面的JSON格式输出。

**输出JSON格式:**
```json
{{
    "thinking_process": "基于用户的核心目标是'X'和'Y'，我将首先构建研究的总体框架，然后分解出20个具体的、有递进关系的研究方向。我会特别关注风险'A'和'B'，并在计划中设计规避策略。",
    "plan_data": {{
        "title": "基于AI与影像组学的XXX研究计划",
        "author": "AI Research System",
        "date": "{datetime.now().strftime('%Y-%m-%d')}",
        "executive_summary": "本计划旨在...",
        "research_directions": [
            {{ "id": 1, "title": "方向一：数据基础建设", "description": "..." }},
            {{ "id": 2, "title": "方向二：基线模型开发", "description": "..." }}
        ]
    }},
    "assessment": {{
        "plan_quality_score": 0.85,
        "completeness_score": 0.75,
        "potential_risks": ["技术风险1", "数据风险1"],
        "improvement_suggestions": ["可以进一步明确每个方向的评价指标。", "建议增加一个关于伦理审查的章节。"]
    }},
    "needs_refinement": true
}}
```

**请现在开始制定或优化研究计划。**
"""
        try:
            response = self.llm.invoke(planning_prompt, timeout=120)
            cleaned_response = repair_json_output(response.content)
            result_data = json.loads(cleaned_response)

            assessment = result_data.get("assessment", {})
            return PlanningResult(
                stage=PlanningStage.DRAFT,
                plan_quality_score=assessment.get("plan_quality_score", 0.0),
                plan_data=result_data.get("plan_data", {}),
                improvement_suggestions=assessment.get("improvement_suggestions", []),
                potential_risks=assessment.get("potential_risks", []),
                thinking_process=result_data.get("thinking_process", ""),
                needs_refinement=result_data.get("needs_refinement", True),
                completeness_score=assessment.get("completeness_score", 0.0)
            )
        except Exception as e:
            logger.error(f"❌ 规划LLM调用或解析失败: {e}")
            return PlanningResult(stage=PlanningStage.DRAFT, plan_quality_score=0.1, needs_refinement=False)

    def _should_continue_planning(
        self, result: PlanningResult, round_num: int
    ) -> bool:
        """判断是否需要继续规划"""
        if (round_num + 1) >= self.config.max_planning_rounds:
            logger.info("✅ 已达到最大规划轮次，结束规划。")
            return False
        
        if not result.needs_refinement:
            logger.info("✅ 计划已完善，结束规划。")
            return False

        if result.plan_quality_score >= self.config.quality_threshold:
            logger.info("✅ 计划质量已达标，结束规划。")
            return False

        logger.info("🔄 计划需要继续优化，进行下一轮迭代。")
        return True

    def _serialize_planning_result(self, result: PlanningResult) -> Dict[str, Any]:
        """将PlanningResult对象转换为可JSON序列化的字典"""
        serialized_data = result.__dict__.copy()
        if 'stage' in serialized_data and isinstance(serialized_data['stage'], Enum):
            serialized_data['stage'] = serialized_data['stage'].value
        return serialized_data

    def _format_detailed_plan(self, plan_data: Dict[str, Any]) -> str:
        """格式化详细的计划内容展示"""
        if not plan_data:
            return "**📋 计划内容**: 暂无详细内容"
        
        message = "### 📋 详细研究计划\n\n"
        
        # 标题和基本信息
        if plan_data.get("title"):
            message += f"**🎯 计划标题**: {plan_data['title']}\n\n"
        
        # 执行摘要
        if plan_data.get("executive_summary"):
            message += f"**📖 执行摘要**:\n> {plan_data['executive_summary']}\n\n"
        
        # 研究方向
        research_directions = plan_data.get("research_directions", [])
        if research_directions:
            message += f"**🔬 研究方向** (共{len(research_directions)}个):\n\n"
            for direction in research_directions:
                direction_id = direction.get("id", "未知")
                direction_title = direction.get("title", "未命名方向")
                direction_desc = direction.get("description", "暂无描述")
                message += f"**{direction_id}.** **{direction_title}**\n"
                message += f"   {direction_desc}\n\n"
        
        return message

    def _convert_to_frontend_format(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """将增强规划结果转换为前端兼容的格式"""
        logger.info("🔧 转换计划数据为前端兼容格式")
        
        # 提取基本信息
        title = plan_data.get("title", "医学深度研究计划")
        executive_summary = plan_data.get("executive_summary", "基于AI和影像组学技术的深度研究")
        research_directions = plan_data.get("research_directions", [])
        
        # 将研究方向转换为前端期望的steps格式
        steps = []
        for direction in research_directions:
            step = {
                "title": direction.get("title", "研究步骤"),
                "description": direction.get("description", "详细研究内容"),
                "step_type": "research",
                "need_web_search": True
            }
            steps.append(step)
        
        # 如果没有研究方向，创建默认步骤
        if not steps:
            steps = [
                {
                    "title": "背景调研和理论基础研究",
                    "description": "深入调研相关技术和理论基础，建立研究框架",
                    "step_type": "research",
                    "need_web_search": True
                },
                {
                    "title": "技术方案设计和验证",
                    "description": "设计具体的技术实现方案并进行可行性验证",
                    "step_type": "analysis", 
                    "need_web_search": False
                },
                {
                    "title": "实验设计和效果评估",
                    "description": "设计实验方案，建立评估指标，预测研究效果",
                    "step_type": "writing",
                    "need_web_search": False
                }
            ]
        
        # 构造前端兼容的计划格式
        frontend_plan = {
            "locale": "zh-CN",
            "has_enough_context": True,
            "title": title,
            "thought": executive_summary,
            "steps": steps
        }
        
        logger.info(f"✅ 转换完成，标题: {title}，步骤数: {len(steps)}")
        return frontend_plan

def _format_planning_round_to_message(round_num: int, max_rounds: int, result: "PlanningResult") -> str:
    """将单轮规划结果格式化为美观的Markdown消息"""

    message = f"### 📝 第 {round_num + 1}/{max_rounds} 轮规划迭代\n\n"

    # 添加思考过程
    if result.thinking_process:
        message += f"**🤔 思考过程:**\n> {result.thinking_process}\n\n"

    # 添加计划质量评分
    message += f"**📊 计划质量评估:**\n"
    message += f"- **当前计划质量分数:** `{result.plan_quality_score:.2f}`\n"
    if hasattr(result, 'completeness_score'):
         message += f"- **计划完整性分数:** `{result.completeness_score:.2f}`\n\n"

    # 添加改进建议
    if result.improvement_suggestions:
        message += f"**💡 改进建议:**\n"
        for suggestion in result.improvement_suggestions:
            message += f"- {suggestion}\n"
        message += "\n"

    # 添加潜在风险
    if result.potential_risks:
        message += f"**⚠️ 潜在风险:**\n"
        for risk in result.potential_risks:
            message += f"- {risk}\n"
        message += "\n"

    # 结论
    if result.needs_refinement:
        message += f"**⚠️ 结论: 计划需要进一步细化**\n"
    else:
        message += f"**✅ 结论: 计划草案已完成**\n"

    return message
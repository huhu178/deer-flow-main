# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import operator
from typing import Annotated, Dict, Any, List

from langgraph.graph import MessagesState

from src.prompts.planner_model import Plan


class State(MessagesState):
    """State for the agent system, extends MessagesState with next field."""

    # Runtime Variables
    locale: str = "en-US"
    observations: list[str] = []
    plan_iterations: int = 0
    current_plan: Plan | str = None
    final_report: str = ""
    auto_accepted_plan: bool = False
    enable_background_investigation: bool = True
    background_investigation_results: str = None
    
    # 🔥 添加缺失的状态字段
    current_step_index: int = 0
    research_team_loop_counter: int = 0
    
    # 🔧 多轮交互状态字段
    understanding_rounds: int = 0
    understanding_history: List[Dict[str, Any]] = []
    understanding_completed: bool = False
    current_understanding: Dict[str, Any] = {}
    final_understanding: Dict[str, Any] = {}
    
    # 🔧 多轮规划状态字段
    planning_rounds: int = 0
    planning_history: List[Dict[str, Any]] = []
    planning_completed: bool = False
    current_planning_result: Dict[str, Any] = {}
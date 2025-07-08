# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Prompts package initialization
"""

from .template import (
    get_prompt_template,
    apply_prompt_template,
    RESEARCH_SURVEY_TEMPLATE,
    SURVEY_TASK_TEMPLATE
)

__all__ = [
    'get_prompt_template',
    'apply_prompt_template', 
    'RESEARCH_SURVEY_TEMPLATE',
    'SURVEY_TASK_TEMPLATE'
]

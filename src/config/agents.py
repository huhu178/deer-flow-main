# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from typing import Literal

# Define available LLM types
LLMType = Literal["basic", "reasoning", "vision"]

# Define agent-LLM mapping
AGENT_LLM_MAP: dict[str, LLMType] = {
    "coordinator": "BASIC_MODEL",
    "planner": "BASIC_MODEL",
    "researcher": "BASIC_MODEL",
    "coder": "BASIC_MODEL",
    "reporter": "BASIC_MODEL",
    "podcast_script_writer": "BASIC_MODEL",
    "ppt_composer": "BASIC_MODEL",
    "prose_writer": "BASIC_MODEL",
}

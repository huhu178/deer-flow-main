# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging

from langchain.schema import HumanMessage, SystemMessage

from src.config.agents import AGENT_LLM_MAP
from src.llms.llm import get_llm_by_type
from src.prompts.template import get_prompt_template
from src.utils.json_utils import repair_json_output

from ..types import Script
from .state import PodcastState

logger = logging.getLogger(__name__)


def script_writer_node(state: PodcastState):
    logger.info("Generating script for podcast...")
    model = get_llm_by_type(AGENT_LLM_MAP["podcast_script_writer"])
    
    prompt_content = get_prompt_template("podcast/podcast_script_writer")
    prompt_content += "\n\n请确保你的回复是有效的JSON格式，包含所需的所有字段。不要添加解释或其他文本，直接返回JSON对象。"
    
    response = model.invoke(
        [
            SystemMessage(content=prompt_content),
            HumanMessage(content=state["input"]),
        ],
    )
    
    try:
        script_json = json.loads(repair_json_output(response.content))
        script = Script.model_validate(script_json)
    except Exception as e:
        logger.error(f"Failed to parse script response: {e}")
        script = None
        
    print(script)
    return {"script": script, "audio_chunks": []}

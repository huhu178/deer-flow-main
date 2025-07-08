# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from pathlib import Path
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache
from langchain_openai import ChatOpenAI

from src.config.configuration import load_yaml_config
from .doubao_llm import DoubaoLLM

logger = logging.getLogger(__name__)

# --- Global LLM Cache ---
_llm_cache = {}
# Initialize cache
set_llm_cache(InMemoryCache())

def clear_llm_cache():
    """Clears the LLM cache to re-initialize models."""
    global _llm_cache
    _llm_cache.clear()
    set_llm_cache(InMemoryCache())  # Reset the cache
    logger.info("🔄 LLM cache has been cleared. Models will be re-initialized.")

def _create_openai_compatible_chat_model(model_name, api_key, base_url, temperature, max_tokens, streaming):
    """Creates and returns an OpenAI-compatible chat model instance."""
    return ChatOpenAI(
        model_name=model_name,
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=temperature,
        streaming=streaming,
        model_kwargs={
            "max_tokens": max_tokens,
        },
    )

def get_llm_by_type(llm_type: str, force_refresh: bool = False) -> ChatOpenAI:
    """
    Gets an LLM instance by type from conf.yaml. Returns a cached instance if available.
    """
    global _llm_cache
    if llm_type not in _llm_cache or force_refresh:
        conf_path = str((Path(__file__).parent.parent.parent / "conf.yaml").resolve())
        conf = load_yaml_config(conf_path)
        
        model_config = conf.get("llm", {}).get(llm_type)
        if not model_config:
            raise ValueError(f"LLM type '{llm_type}' not found in conf.yaml")

        logger.info(f"🔧 Initializing OpenAI-compatible model: {model_config.get('model')} (base_url: {model_config.get('base_url')})")

        _llm_cache[llm_type] = _create_openai_compatible_chat_model(
            model_name=model_config.get("model"),
            api_key=model_config.get("api_key"),
            base_url=model_config.get("base_url"),
            temperature=model_config.get("temperature", 0.7),
            max_tokens=model_config.get("max_tokens", 4096),
            streaming=model_config.get("streaming", True),
        )

    return _llm_cache[llm_type]

def get_vision_llm(force_refresh: bool = False) -> DoubaoLLM:
    """Gets or creates a Doubao vision language model instance."""
    global _llm_cache
    if "vision_llm" not in _llm_cache or force_refresh:
        conf_path = str((Path(__file__).parent.parent.parent / "conf.yaml").resolve())
        conf = load_yaml_config(conf_path)
        
        doubao_config_yaml = conf.get("llm", {}).get("doubao")
        if not doubao_config_yaml:
            raise ValueError("Doubao 'doubao' config section not found in conf.yaml")

        logger.info(f"🤖 Initializing Doubao model: {doubao_config_yaml.get('model')}")
        
        # Pass the loaded config dict directly to the DoubaoLLM constructor
        _llm_cache["vision_llm"] = DoubaoLLM(doubao_config_yaml)
        
    return _llm_cache["vision_llm"]

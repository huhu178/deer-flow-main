# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import yaml
from typing import Dict, Any


def replace_env_vars(value: str) -> str:
    """Replace environment variables in string values."""
    if not isinstance(value, str):
        return value
    if value.startswith("$"):
        env_var = value[1:]
        return os.getenv(env_var, value)
    return value


def process_dict(config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively process dictionary to replace environment variables."""
    result = {}
    for key, value in config.items():
        if isinstance(value, dict):
            result[key] = process_dict(value)
        elif isinstance(value, str):
            result[key] = replace_env_vars(value)
        else:
            result[key] = value
    return result


_config_cache: Dict[str, Dict[str, Any]] = {}


def load_yaml_config(file_path: str) -> Dict[str, Any]:
    """Load and process YAML configuration file with proper UTF-8 encoding."""
    # 如果文件不存在，返回{}
    if not os.path.exists(file_path):
        return {}

    # 检查缓存中是否已存在配置
    if file_path in _config_cache:
        return _config_cache[file_path]

    # 如果缓存中不存在，则加载并处理配置
    try:
        # 明确指定UTF-8编码以支持中文注释
        with open(file_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except UnicodeDecodeError:
        # 如果UTF-8失败，尝试使用系统默认编码
        try:
            with open(file_path, "r", encoding="gbk") as f:
                config = yaml.safe_load(f)
        except UnicodeDecodeError:
            # 最后尝试使用latin-1编码（几乎不会失败）
            with open(file_path, "r", encoding="latin-1") as f:
                config = yaml.safe_load(f)
    
    if config is None:
        config = {}
    
    processed_config = process_dict(config)

    # 将处理后的配置存入缓存
    _config_cache[file_path] = processed_config
    return processed_config

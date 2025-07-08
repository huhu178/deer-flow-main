# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
from dataclasses import dataclass, fields
from typing import Any, Optional, Dict
import yaml
from pathlib import Path

from langchain_core.runnables import RunnableConfig


@dataclass(kw_only=True)
class Configuration:
    """The configurable fields."""

    # 🔧 优化后的配置参数 - 大幅增加搜索结果
    max_plan_iterations: int = 1  # Maximum number of plan iterations
    max_step_num: int = 5  # 增加步骤数量（从3增加到5）
    max_search_results: int = 12  # 🔍 大幅增加搜索结果（从3增加到12）
    mcp_settings: dict = None  # MCP settings, including dynamic loaded tools
    
    # 🔄 多轮交互配置参数 - 不依赖质量阈值判断
    max_understanding_rounds: int = 5     # 🔧 理解阶段最多5轮深入交互
    max_planning_rounds: int = 3          # 🔧 规划阶段最多3轮迭代优化
    understanding_quality_threshold: float = 0.0  # 🔧 禁用理解质量阈值判断
    planning_quality_threshold: float = 0.0       # 🔧 禁用规划质量阈值判断
    enable_deep_thinking: bool = True     # 🔧 启用深度思考
    enable_progressive_planning: bool = True  # 🔧 启用渐进式规划
    thinking_time_seconds: float = 2.0    # 🔧 思考时间2秒
    auto_clarification: bool = True       # 🔧 启用自动澄清
    
    # 🎯 简化的交互模式控制
    interaction_mode: str = "enhanced"    # 🔧 默认使用增强模式
    # - standard: 原有模式 (1轮理解 + 1轮规划)  
    # - enhanced: 增强模式 (多轮理解 + 多轮规划)
    # - auto: 自动模式 (根据复杂度动态调整)
    
    # 🔍 新增：搜索策略配置
    enable_multi_source_search: bool = True    # 启用多源搜索
    pubmed_max_results: int = 10              # PubMed最大结果数
    scholar_max_results: int = 10             # Google Scholar最大结果数
    arxiv_max_results: int = 8                # ArXiv最大结果数

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})

    def get_understanding_config(self) -> dict:
        """获取理解阶段的配置参数"""
        return {
            "max_rounds": self.max_understanding_rounds,
            "quality_threshold": self.understanding_quality_threshold,
            "enable_deep_thinking": self.enable_deep_thinking,
            "thinking_time": self.thinking_time_seconds,
            "auto_clarification": self.auto_clarification
        }
    
    def get_planning_config(self) -> dict:
        """获取规划阶段的配置参数"""
        return {
            "max_rounds": self.max_planning_rounds,
            "quality_threshold": self.planning_quality_threshold,
            "enable_progressive": self.enable_progressive_planning,
            "thinking_time": self.thinking_time_seconds
        }
    
    def should_use_enhanced_mode(self) -> bool:
        """判断是否应该使用增强交互模式"""
        return self.interaction_mode in ["enhanced", "auto"]
    
    def get_total_max_iterations(self) -> int:
        """获取总的最大迭代次数（理解 + 规划）"""
        if self.interaction_mode == "enhanced":
            return self.max_understanding_rounds + self.max_planning_rounds
        elif self.interaction_mode == "auto":
            return max(3, self.max_understanding_rounds + self.max_planning_rounds)
        else:
            return self.max_plan_iterations  # 标准模式


def get_current_model_name() -> str:
    """
    获取当前使用的模型名称，用于文件命名
    
    优先级：
    1. 环境变量 CURRENT_MODEL
    2. conf.yaml 中的 MODEL_SWITCH.primary_model 配置
    3. 配置文件 model_name.txt
    4. 默认值 "gemini"
    
    Returns:
        str: 模型名称，用于文件命名
    """
    # 1. 检查环境变量
    model_from_env = os.environ.get('CURRENT_MODEL')
    if model_from_env:
        return model_from_env.strip()
    
    # 2. 从conf.yaml读取配置
    try:
        conf_file = os.path.join(os.path.dirname(__file__), '..', '..', 'conf.yaml')
        if os.path.exists(conf_file):
            with open(conf_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # 🎯 优先从FILE_NAMING.model_name读取（最直接的配置）
            file_naming_model = config.get('FILE_NAMING', {}).get('model_name', '')
            if file_naming_model:
                return file_naming_model.strip()
                
            # 备用：从MODEL_SWITCH.primary_model获取配置key
            primary_model = config.get('MODEL_SWITCH', {}).get('primary_model', '')
            
            # 将配置key转换为模型名称
            model_name_mapping = {
                'BASIC_MODEL': 'gemini',
                'DEEPSEEK_MODEL': 'deepseek', 
                'QIANWEN_MODEL': 'qianwen'
            }
            
            if primary_model in model_name_mapping:
                return model_name_mapping[primary_model]
    except Exception as e:
        print(f"⚠️  读取conf.yaml失败: {e}")
    
    # 3. 检查配置文件
    try:
        config_file = os.path.join(os.path.dirname(__file__), 'model_name.txt')
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                model_from_file = f.read().strip()
                if model_from_file:
                    return model_from_file
    except Exception:
        pass
    
    # 4. 默认值
    return "gemini"


def set_current_model_name(model_name: str) -> None:
    """
    设置当前使用的模型名称
    
    Args:
        model_name: 模型名称 (如: "gemini", "deepseek", "qwen" 等)
    """
    # 方法1：优先修改conf.yaml
    try:
        update_conf_yaml_model(model_name)
        print(f"✅ 已在conf.yaml中设置模型为: {model_name}")
    except Exception as e:
        print(f"⚠️  无法修改conf.yaml: {e}")
        # 方法2：降级到配置文件
        try:
            config_file = os.path.join(os.path.dirname(__file__), 'model_name.txt')
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(model_name.strip())
            print(f"✅ 已在配置文件中设置模型为: {model_name}")
        except Exception as e2:
            print(f"❌ 设置模型名称失败: {e2}")
            return
    
    print(f"📁 文件将保存到: outputs/batch_directions_{model_name} 和 outputs/complete_reports_{model_name}")


def update_conf_yaml_model(model_name: str) -> None:
    """
    更新conf.yaml中的模型配置
    
    Args:
        model_name: 模型名称 (如: "gemini", "deepseek", "qwen", "doubao")
    """
    conf_file = os.path.join(os.path.dirname(__file__), '..', '..', 'conf.yaml')
    
    # 读取配置
    with open(conf_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 更新MODEL_SWITCH.primary_model
    if 'MODEL_SWITCH' not in config:
        config['MODEL_SWITCH'] = {}
    
    config['MODEL_SWITCH']['primary_model'] = model_name.lower()
    
    # 🔧 同时更新FILE_NAMING.model_name
    if 'FILE_NAMING' not in config:
        config['FILE_NAMING'] = {}
    config['FILE_NAMING']['model_name'] = model_name.lower()
    
    # 写回文件
    with open(conf_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def list_available_models() -> list:
    """
    列出可用的模型名称建议
    
    Returns:
        list: 常用模型名称列表
    """
    return [
        "gemini",      # Google Gemini
        "doubao",      # 字节豆包
        "deepseek",    # DeepSeek
        "qwen",        # 阿里通义千问
        "chatgpt",     # OpenAI ChatGPT
        "claude",      # Anthropic Claude
        "llama",       # Meta LLaMA
        "yi",          # 零一万物
        "baichuan",    # 百川智能
        "custom"       # 自定义模型
    ]


def get_model_output_info() -> dict:
    """
    获取当前模型的输出信息
    
    Returns:
        dict: 包含模型名称和输出目录的信息
    """
    current_model = get_current_model_name()
    return {
        "model_name": current_model,
        "batch_directions_dir": f"outputs/batch_directions_{current_model}",
        "complete_reports_dir": f"outputs/complete_reports_{current_model}",
        "config_file": os.path.join(os.path.dirname(__file__), 'model_name.txt')
    }


# 🔄 多轮交互配置预设
class InteractionPresets:
    """多轮交互配置预设"""
    
    @staticmethod
    def get_standard_config() -> Configuration:
        """标准配置 - 与原有系统保持一致"""
        return Configuration(
            max_plan_iterations=1,
            interaction_mode="standard",
            max_understanding_rounds=1,
            max_planning_rounds=1
        )
    
    @staticmethod
    def get_enhanced_config() -> Configuration:
        """增强配置 - 支持多轮深度交互"""
        return Configuration(
            max_plan_iterations=5,  # 兼容原有参数
            interaction_mode="enhanced",
            max_understanding_rounds=5,
            max_planning_rounds=3,
            understanding_quality_threshold=0.8,
            planning_quality_threshold=0.8,
            enable_deep_thinking=True,
            thinking_time_seconds=1.0
        )
    
    @staticmethod  
    def get_auto_config() -> Configuration:
        """自动配置 - 根据问题复杂度动态调整"""
        return Configuration(
            max_plan_iterations=3,
            interaction_mode="auto",
            max_understanding_rounds=3,
            max_planning_rounds=2,
            understanding_quality_threshold=0.7,
            planning_quality_threshold=0.7,
            enable_deep_thinking=True,
            thinking_time_seconds=0.5
        )
    
    @staticmethod
    def get_fast_config() -> Configuration:
        """快速配置 - 最小交互，快速响应"""
        return Configuration(
            max_plan_iterations=1,
            interaction_mode="standard",
            max_understanding_rounds=1,
            max_planning_rounds=1,
            understanding_quality_threshold=0.6,
            planning_quality_threshold=0.6,
            enable_deep_thinking=False,
            thinking_time_seconds=0.0
        )


def create_interaction_config(
    mode: str = "enhanced", 
    understanding_rounds: int = 5,
    planning_rounds: int = 3,
    quality_threshold: float = 0.8
) -> Configuration:
    """
    创建自定义交互配置
    
    Args:
        mode: 交互模式 ("standard", "enhanced", "auto")
        understanding_rounds: 理解轮次
        planning_rounds: 规划轮次  
        quality_threshold: 质量阈值
    
    Returns:
        Configuration: 配置对象
    """
    return Configuration(
        interaction_mode=mode,
        max_understanding_rounds=understanding_rounds,
        max_planning_rounds=planning_rounds,
        understanding_quality_threshold=quality_threshold,
        planning_quality_threshold=quality_threshold,
        max_plan_iterations=understanding_rounds + planning_rounds,  # 兼容原有参数
        enable_deep_thinking=True,
        thinking_time_seconds=1.0 if mode == "enhanced" else 0.5
    )


def load_yaml_config(path: str) -> Dict[str, Any]:
    """Loads a YAML configuration file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise ValueError(f"Configuration file not found at: {path}")
    except Exception as e:
        raise ValueError(f"Error loading configuration file at {path}: {e}")

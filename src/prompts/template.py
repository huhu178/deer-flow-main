# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import dataclasses
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from langgraph.prebuilt.chat_agent_executor import AgentState
from src.config.configuration import Configuration

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_prompt_template(prompt_name: str) -> str:
    """
    Load and return a prompt template using Jinja2.

    Args:
        prompt_name: Name of the prompt template file (without .md extension)

    Returns:
        The template string with proper variable substitution syntax
    """
    try:
        template = env.get_template(f"{prompt_name}.md")
        return template.render()
    except Exception as e:
        raise ValueError(f"Error loading template {prompt_name}: {e}")


def apply_prompt_template(
    prompt_name: str, state: AgentState, configurable: Configuration = None
) -> list:
    """
    Apply template variables to a prompt template and return formatted messages.

    Args:
        prompt_name: Name of the prompt template to use
        state: Current agent state containing variables to substitute

    Returns:
        List of messages with the system prompt as the first message
    """
    # Convert state to dict for template rendering
    state_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **state,
    }

    # Add configurable variables
    if configurable:
        state_vars.update(dataclasses.asdict(configurable))

    try:
        template = env.get_template(f"{prompt_name}.md")
        system_prompt = template.render(**state_vars)
        return [{"role": "system", "content": system_prompt}] + state["messages"]
    except Exception as e:
        raise ValueError(f"Error applying template {prompt_name}: {e}")

# 13维度调研框架模板
RESEARCH_SURVEY_TEMPLATE = """
# {research_field} 领域综合调研分析

## 调研目标
对 {research_field} 领域进行全面、深入的现状调研和趋势分析，为后续研究方向制定提供基础。

## 调研范围
按照13个维度进行系统性调研：

### 1. 重要的临床/实践问题
- 识别该领域尚未得到有效解决的关键问题
- 分析问题的规模、影响范围和紧迫性
- 评估现有解决方案的局限性

### 2. 重要的科学问题  
- 厘清基础研究中的关键未解机制
- 识别理论模型与实际观察的差距
- 分析跨学科交叉的科学问题

### 3. 近三年的最有影响力的科学进展
- 收集2022-2024年该领域的重大突破
- 分析高影响因子期刊的关键论文
- 评估产业界的技术创新

### 4. 交叉学科机会
- 评估技术学科的应用潜力
- 分析相关基础学科的理论支撑
- 识别新兴交叉学科机会

### 5. 方法学创新
- 评估新型研究设计和分析方法
- 分析新兴技术工具的应用
- 识别方法学发展趋势

### 6. 专利授权状况
- 分析核心技术专利分布
- 评估专利空白和技术机会
- 识别专利壁垒和风险

### 7. 国际合作机会
- 识别国际顶尖研究机构
- 分析现有合作项目和联盟
- 评估合作机会和挑战

### 8. 科研资金支持
- 分析政府资助政策和重点
- 评估企业投入和产学研机会
- 识别国际资助机会

### 9. 伦理与合规要求
- 分析研究伦理审查要求
- 评估数据隐私和技术伦理问题
- 识别合规风险和应对策略

### 10. 开放数据资源
- 识别可获取的公开数据资源
- 评估数据质量和使用限制
- 分析数据整合机会

### 11. 公共事件影响
- 分析近年重大事件对该领域的影响
- 评估社会需求变化和政策调整
- 预测未来可能的挑战和热点

### 12. 国家政策环境
- 分析发展规划和政策支持
- 评估相关法规和监管要求
- 识别政策机会和约束

### 13. 综合评估与机会识别
- 进行跨维度关联分析
- 识别研究机会优先级
- 评估风险和制定应对策略

## 预期产出
形成一份针对 {research_field} 领域的综合性调研分析报告，为后续研究方向制定提供科学依据。
"""

# 调研任务分配模板
SURVEY_TASK_TEMPLATE = """
## 调研任务：{dimension_name} - {research_field}

### 任务描述
{task_description}

### 调研要点
{research_points}

### 输出要求
{output_requirements}

### 质量标准
- 信息来源权威可靠
- 数据时效性强（重点关注近3年）
- 分析深入全面
- 结论有据可依

### 特别关注
- 与 {research_field} 领域的相关性和特殊性
- 对后续研究方向制定的指导意义
- 跨维度的关联性分析
- 基于该领域特点的定制化建议
"""

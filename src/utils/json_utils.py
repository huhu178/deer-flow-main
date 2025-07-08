# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import json
import json_repair

logger = logging.getLogger(__name__)


def repair_json_output(content: str) -> str:
    """
    Repair and normalize JSON output.

    Args:
        content (str): String content that may contain JSON

    Returns:
        str: Repaired JSON string, or original content if not JSON
    """
    # 🔧 添加None值安全检查
    if content is None:
        logger.warning("输入内容为None，返回空JSON对象")
        return "{}"
        
    if not isinstance(content, str):
        logger.warning(f"输入内容类型错误: {type(content)}，尝试转换为字符串")
        content = str(content)
    
    content = content.strip()
    if content.startswith(("{", "[")) or "```json" in content or "```ts" in content:
        try:
            # If content is wrapped in ```json code block, extract the JSON part
            if content.startswith("```json"):
                content = content.removeprefix("```json")

            if content.startswith("```ts"):
                content = content.removeprefix("```ts")

            if content.endswith("```"):
                content = content.removesuffix("```")

            # Try to repair and parse JSON
            repaired_content = json_repair.loads(content)
            return json.dumps(repaired_content, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"JSON repair failed: {e}")
            return "{}"  # 🔧 修复失败时返回空JSON而不是原内容
    
    # 🔧 如果不是JSON格式，返回原内容，但确保不为空
    return content if content else "{}"

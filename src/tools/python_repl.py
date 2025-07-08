# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import re
import ast
import sys
import traceback
from io import StringIO
from typing import Annotated, Any, Dict, Optional
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from .decorators import log_io

# Initialize REPL and logger
repl = PythonREPL()
logger = logging.getLogger(__name__)

def fix_unterminated_strings(code):
    """尝试修复未终止的字符串字面量"""
    # 检查并修复由单引号开始但未终止的字符串
    lines = code.split('\n')
    fixed_lines = []
    
    for line in lines:
        # 计算一行中单引号和双引号的数量
        single_quotes = line.count("'")
        double_quotes = line.count('"')
        
        # 如果单引号数量为奇数，在行尾添加单引号
        if single_quotes % 2 == 1 and "'''" not in line and "\"\"\"" not in line:
            line += "'"
            logger.warning(f"Fixed unterminated single quote string: {line}")
        
        # 如果双引号数量为奇数，在行尾添加双引号
        if double_quotes % 2 == 1 and "'''" not in line and "\"\"\"" not in line:
            line += '"'
            logger.warning(f"Fixed unterminated double quote string: {line}")
        
        fixed_lines.append(line)
    
    # 尝试将单行字符串转换为多行字符串
    fixed_code = '\n'.join(fixed_lines)
    
    # 如果代码中有多行字符串内容但没有使用三引号，尝试修复
    if '\n' in fixed_code and "'''" not in fixed_code and '"""' not in fixed_code:
        # 使用正则表达式查找以单引号或双引号开始但未终止且包含换行符的字符串
        pattern = r"(['\"])((?:\\\1|(?!\1).)*\n.*?)(?:\1|$)"
        match = re.search(pattern, fixed_code)
        if match:
            quote_type = match.group(1)
            content = match.group(2)
            # 替换为三引号字符串
            if quote_type == "'":
                fixed_code = fixed_code.replace(f"'{content}", f"'''{content}'''")
            else:
                fixed_code = fixed_code.replace(f'"{content}', f'"""{content}"""')
            logger.warning("Converted single line string to multi-line string")
    
    # 检查是否有未闭合的三引号字符串
    if '"""' in fixed_code:
        # 计算三引号的数量
        triple_quotes_count = fixed_code.count('"""')
        # 如果是奇数个三引号，说明有未闭合的三引号字符串
        if triple_quotes_count % 2 == 1:
            # 在代码末尾添加三引号来闭合
            fixed_code += '\n"""'
            logger.warning("Fixed unterminated triple-quoted string by adding closing quotes at the end")
    
    return fixed_code

def validate_python_syntax(code: str) -> tuple[bool, str]:
    """
    验证Python代码语法，特别检查引号相关的错误
    
    Args:
        code: 要验证的Python代码
        
    Returns:
        tuple: (是否有效, 错误信息)
    """
    # 大幅放宽检查条件，只检查最严重的错误
    quote_patterns = [
        # 只保留最基本的检查，避免误报
        (r'\"\"\"[^\"]*\"[^\"]*\"[^\"]*\"\"\"(?!\s*[,\]\}])', "检测到可能的三引号嵌套错误"),
        (r"'''[^']*'[^']*'[^']*'''(?!\s*[,\]\}])", "检测到可能的三引号嵌套错误"),
    ]
    
    # 暂时禁用严格的字典键检查，因为容易误报
    # for pattern, message in quote_patterns:
    #     if re.search(pattern, code):
    #         return False, f"语法错误: {message}"
    
    # 使用AST进行基本语法检查
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        # 只有真正的语法错误才返回False
        if "unterminated" in str(e).lower() or "unexpected eof" in str(e).lower():
            return False, f"Python语法错误: {str(e)}"
        else:
            # 其他语法错误可能是误报，先跳过
            logger.warning(f"Potential syntax issue ignored: {str(e)}")
            return True, ""
    except Exception as e:
        logger.warning(f"Code validation warning: {str(e)}")
        return True, ""  # 验证失败时默认允许执行

@tool
@log_io
def python_repl_tool(
    code: Annotated[
        str, "The python code to execute to do further analysis or calculation."
    ],
):
    """Use this to execute python code and do data analysis or calculation. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    if not isinstance(code, str):
        error_msg = f"Invalid input: code must be a string, got {type(code)}"
        logger.error(error_msg)
        return f"Error executing code:\n```python\n{code}\n```\nError: {error_msg}"

    logger.info("Executing Python code")
    
    # 检查是否有常见需要导入的库没有导入
    if 'pandas' in code and 'import pandas' not in code:
        code = "import pandas as pd\n" + code
        logger.info("Added missing pandas import")
    
    # 尝试修复未终止的字符串
    try:
        fixed_code = fix_unterminated_strings(code)
        if fixed_code != code:
            logger.info("Applied string fixes to code")
            code = fixed_code
    except Exception as e:
        logger.warning(f"Failed to fix string issues: {str(e)}")
    
    # 预先验证语法
    is_valid, error_msg = validate_python_syntax(code)
    if not is_valid:
        return f"代码执行前语法检查失败:\n{error_msg}\n\n请修正语法错误后重试。\n\n提示：\n- 字典键请使用单引号或双引号，如 'key' 或 \"key\"\n- 避免在字典键中使用三引号\n- 确保所有引号正确配对"
    
    try:
        result = repl.run(code)
        # Check if the result is an error message by looking for typical error patterns
        if isinstance(result, str) and ("Error" in result or "Exception" in result):
            logger.error(result)
            
            # 如果是语法错误，尝试给出更详细的建议
            if "SyntaxError" in result:
                if "unterminated string literal" in result:
                    return (f"Error executing code: 未终止的字符串字面量。请检查代码中的引号是否成对。\n"
                            f"建议使用三引号(''' 或 \"\"\")来处理多行文本。\n"
                            f"```python\n{code}\n```\nError: {result}")
                elif "EOL while scanning string literal" in result:
                    return (f"Error executing code: 扫描字符串时遇到行尾。请确保字符串在同一行内完成，或使用三引号。\n"
                            f"```python\n{code}\n```\nError: {result}")
            
            return f"Error executing code:\n```python\n{code}\n```\nError: {result}"
        
        # 如果是NameError和'pd'相关，提示导入pandas
        if isinstance(result, str) and "NameError" in result and "pd" in result:
            return (f"Error executing code: 缺少 pandas 导入。请在代码开头添加 'import pandas as pd'\n"
                    f"```python\n{code}\n```\nError: {result}")
                    
        logger.info("Code execution successful")
    except BaseException as e:
        error_msg = repr(e)
        logger.error(error_msg)
        
        # 特殊处理pandas未导入的错误
        if "NameError" in error_msg and "pd" in error_msg:
            return (f"Error executing code: 缺少 pandas 导入。请在代码开头添加 'import pandas as pd'\n"
                    f"```python\n{code}\n```\nError: {error_msg}")
        
        return f"Error executing code:\n```python\n{code}\n```\nError: {error_msg}"

    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return result_str

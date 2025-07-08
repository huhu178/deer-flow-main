# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
import re
from typing import Dict, List, Optional

import httpx
from langchain_community.utilities import ArxivAPIWrapper as OriginalArxivAPIWrapper

logger = logging.getLogger(__name__)

def is_chinese(text: str) -> bool:
    """
    检测文本是否包含中文字符
    """
    # 使用正则表达式匹配中文字符
    return bool(re.search(r'[\u4e00-\u9fff]', text))

def translate_to_english(text: str) -> str:
    """
    将中文文本翻译成英文
    注：实际生产中建议使用更可靠的翻译服务
    """
    try:
        # 简单方法：使用有道翻译API（免费版）
        url = "http://fanyi.youdao.com/translate"
        params = {
            "doctype": "json",  # 返回格式
            "type": "ZH_CN2EN",  # 中译英
            "i": text  # 翻译内容
        }
        
        # 发送请求
        response = httpx.post(url, data=params, timeout=10.0)
        data = response.json()
        
        # 提取翻译结果
        if "translateResult" in data and len(data["translateResult"]) > 0:
            result = ""
            for items in data["translateResult"]:
                for item in items:
                    result += item.get("tgt", "")
            return result
        
        # 如果没有得到结果，尝试使用备用词典替换
        logger.warning(f"无法使用API翻译，使用备用方法: {text}")
        return _backup_translate(text)
        
    except Exception as e:
        logger.error(f"翻译出错: {str(e)}, 使用备用翻译")
        return _backup_translate(text)

def _backup_translate(text: str) -> str:
    """
    备用的简单关键词替换翻译
    """
    # 医学和生物学术术语对照表
    medical_terms = {
        "骨密度": "bone density",
        "骨骼": "bone skeleton",
        "骨质疏松": "osteoporosis",
        "全身健康": "whole body health",
        "心血管": "cardiovascular",
        "心脏": "heart",
        "阿尔茨海默病": "Alzheimer's disease",
        "神经退行性疾病": "neurodegenerative disease",
        "胰岛素抵抗": "insulin resistance",
        "代谢": "metabolism",
        "甲状腺": "thyroid",
        "全死因死亡率": "all-cause mortality",
        "机制": "mechanism",
        "预测": "prediction",
        "生物标志物": "biomarker",
        "影像": "imaging",
        "DXA": "DXA",
        "风险": "risk",
        "通讯": "communication",
    }
    
    # 替换词语
    result = text
    for cn, en in medical_terms.items():
        result = result.replace(cn, en)
    
    # 如果结果还包含中文，则移除这些中文字符
    if is_chinese(result):
        result = re.sub(r'[\u4e00-\u9fff]', '', result).strip()
    
    return result or "osteoporosis bone health"  # 默认关键词


class EnhancedArxivAPIWrapper(OriginalArxivAPIWrapper):
    """
    增强型ArXiv API包装器，添加中文查询自动翻译功能
    """
    
    def run(self, query: str) -> str:
        """
        使用ArXiv API运行查询，自动检测并翻译中文查询
        
        Args:
            query: 用户查询，可以是中文或英文
            
        Returns:
            str: 查询结果JSON字符串
        """
        # 检查是否为中文查询
        if is_chinese(query):
            # 记录原始查询
            logger.info(f"检测到中文查询: {query}")
            
            # 翻译成英文
            english_query = translate_to_english(query)
            logger.info(f"已将查询翻译为英文: {english_query}")
            
            # 使用翻译后的查询
            return super().run(english_query)
        
        # 英文查询直接使用
        return super().run(query) 
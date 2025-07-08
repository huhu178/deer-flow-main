# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import os
import logging
from typing import Any, Dict, Optional

from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_community.utilities.google_scholar import GoogleScholarAPIWrapper

logger = logging.getLogger(__name__)

class GoogleScholarSearchTool(BaseTool):
    """
    Tool that queries the Google Scholar API using SerpAPI.

    To use, you should have the environment variable ``SERPAPI_API_KEY``
    set with your API key, or pass ``serpapi_api_key`` as a named parameter
    to the constructor. Sign up at: https://serpapi.com/users/sign_up
    """

    name: str = "google_scholar_search"
    description: str = (
        "A wrapper around Google Scholar. "
        "Useful for when you need to answer questions about academic papers, "
        "research, and scholarly articles. "
        "Input should be a search query."
    )
    api_wrapper: GoogleScholarAPIWrapper

    def __init__(self, serpapi_api_key: Optional[str] = None, top_k_results: int = 5, hl: str = "en", lr: str = "lang_en", **kwargs: Any):
        """Initialize with SerpAPI key and other parameters."""
        # 直接使用提供的API密钥，如果没有则尝试从环境变量获取
        serpapi_api_key_env = os.getenv("SERPAPI_API_KEY")
        final_serpapi_api_key = serpapi_api_key or serpapi_api_key_env or "03b74241f799db78c221f985bb374d661d8e73b52ed43ba38b13d19ca277922d"
        
        # 打印日志，确认使用了哪个源获取API密钥
        if serpapi_api_key:
            logger.info("Using serpapi_api_key passed as parameter")
        elif serpapi_api_key_env:
            logger.info("Using serpapi_api_key from environment variable")
        else:
            logger.info("Using hardcoded serpapi_api_key")
        
        # 输出一段API密钥的开头和结尾，用于调试（不要输出整个密钥）
        key_length = len(final_serpapi_api_key)
        logger.info(f"API key found (length: {key_length}, starts with: {final_serpapi_api_key[:4]}..., ends with: ...{final_serpapi_api_key[-4:]})")
        
        # 先创建api_wrapper
        api_wrapper = GoogleScholarAPIWrapper(
            serp_api_key=final_serpapi_api_key, 
            top_k_results=top_k_results,
            hl=hl,
            lr=lr
        )
        
        # 将api_wrapper添加到kwargs中
        kwargs["api_wrapper"] = api_wrapper
        
        # 现在调用super().__init__
        super().__init__(**kwargs)

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        try:
            logger.info(f"🔍 Google Scholar搜索开始: '{query}'")
            result = self.api_wrapper.run(query)
            
            if not result or result.strip() == "":
                logger.warning(f"⚠️ Google Scholar搜索返回空结果: '{query}'")
                return "No good Google Scholar Result was found. 未找到相关的学术文献。请尝试使用其他搜索工具或调整搜索关键词。"
            
            logger.info(f"✅ Google Scholar搜索成功，结果长度: {len(result)} 字符")
            return result
            
        except Exception as e:
            logger.error(f"❌ Google Scholar搜索失败: {e}")
            error_msg = f"Google Scholar搜索出现错误: {str(e)}"
            
            # 检查是否是API密钥问题
            if "api" in str(e).lower() or "key" in str(e).lower():
                error_msg += "\n可能的原因：API密钥无效或网络连接问题。"
            
            # 检查是否是网络问题
            if "network" in str(e).lower() or "connection" in str(e).lower() or "timeout" in str(e).lower():
                error_msg += "\n可能的原因：网络连接问题，请检查网络设置。"
            
            return error_msg

    async def _arun(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        try:
            logger.info(f"🔍 Google Scholar异步搜索开始: '{query}'")
            result = self.api_wrapper.run(query) 
            
            if not result or result.strip() == "":
                logger.warning(f"⚠️ Google Scholar异步搜索返回空结果: '{query}'")
                return "No good Google Scholar Result was found. 未找到相关的学术文献。请尝试使用其他搜索工具或调整搜索关键词。"
            
            logger.info(f"✅ Google Scholar异步搜索成功，结果长度: {len(result)} 字符")
            return result
            
        except Exception as e:
            logger.error(f"❌ Google Scholar异步搜索失败: {e}")
            error_msg = f"Google Scholar异步搜索出现错误: {str(e)}"
            
            # 检查是否是API密钥问题
            if "api" in str(e).lower() or "key" in str(e).lower():
                error_msg += "\n可能的原因：API密钥无效或网络连接问题。"
            
            return error_msg

if __name__ == "__main__":
    # This is for testing purposes.
    # Ensure SERPAPI_API_KEY is set in your environment.
    if not os.getenv("SERPAPI_API_KEY"):
        print("Please set the SERPAPI_API_KEY environment variable to test this tool.")
    else:
        try:
            tool = GoogleScholarSearchTool()
            # Test basic run
            # result = tool.run("latest research on LLM agents for software engineering")
            # print(f"Search Result:\\n{result}")

            # Test with a specific query that might return fewer results or error
            result_specific = tool.run("fhqwhgads") 
            print(f"Specific Search Result:\\n{result_specific}")

        except ValueError as ve:
            print(f"Initialization Error: {ve}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}") 
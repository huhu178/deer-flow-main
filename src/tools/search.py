# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import json
import logging
import os

from langchain_community.tools import BraveSearch, DuckDuckGoSearchResults
from langchain_community.tools.arxiv import ArxivQueryRun
from langchain_community.utilities import BraveSearchWrapper
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.tools import GoogleSerperRun

from src.config import SearchEngine, SELECTED_SEARCH_ENGINE
from src.tools.tavily_search.tavily_search_results_with_images import (
    TavilySearchResultsWithImages,
)
from src.tools.arxiv_translate import EnhancedArxivAPIWrapper
from src.tools.pubmed_search import PubMedSearchTool
from .google_scholar_search import GoogleScholarSearchTool

from src.tools.decorators import create_logged_tool

logger = logging.getLogger(__name__)

# Create logged versions of the search tools
LoggedTavilySearch = create_logged_tool(TavilySearchResultsWithImages)
LoggedDuckDuckGoSearch = create_logged_tool(DuckDuckGoSearchResults)
LoggedBraveSearch = create_logged_tool(BraveSearch)
LoggedArxivSearch = create_logged_tool(ArxivQueryRun)
LoggedPubMedSearch = create_logged_tool(PubMedSearchTool)
LoggedGoogleScholarSearch = create_logged_tool(GoogleScholarSearchTool)
LoggedGoogleSearch = create_logged_tool(GoogleSerperRun)


# Get the selected search tool
def get_web_search_tool(max_search_results: int, search_strategy: str = "auto", target_journals: list = None):
    """
    获取Web搜索工具，支持智能策略选择
    
    Args:
        max_search_results: 最大搜索结果数
        search_strategy: 搜索策略 ("auto", "academic", "general", "medical")
    """
    
    # 🔧 智能搜索引擎选择
    if search_strategy == "academic":
        logger.info(f"📚 使用学术搜索策略，优先Google Scholar")
        # 可以返回Google Scholar工具或组合搜索
        
    elif search_strategy == "medical":
        logger.info(f"🏥 使用医学搜索策略，优先PubMed")
        # 可以返回PubMed工具或组合搜索
    
    # 默认或通用策略
    if SELECTED_SEARCH_ENGINE == SearchEngine.TAVILY.value:
        logger.info(f"🔍 使用Tavily搜索引擎，max_results: {max_search_results}")
        return LoggedTavilySearch(
            name="web_search",
            max_results=max_search_results,
            include_raw_content=True,
            include_images=True,
            include_image_descriptions=True,
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.DUCKDUCKGO.value:
        logger.info(f"Using DuckDuckGo search engine with max_results: {max_search_results}")
        return LoggedDuckDuckGoSearch(name="web_search", max_results=max_search_results)
    elif SELECTED_SEARCH_ENGINE == SearchEngine.BRAVE_SEARCH.value:
        logger.info(f"Using Brave search engine with max_results: {max_search_results}")
        return LoggedBraveSearch(
            name="web_search",
            search_wrapper=BraveSearchWrapper(
                api_key=os.getenv("BRAVE_SEARCH_API_KEY", ""),
                search_kwargs={"count": max_search_results},
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.GOOGLE.value:
        logger.info(f"Using Google search engine with max_results: {max_search_results}")
        return LoggedGoogleSearch(
            name="web_search",
            api_wrapper=GoogleSerperAPIWrapper(
                serper_api_key=os.getenv("SERPER_API_KEY", ""),
                k=max_search_results,
            ),
        )
    elif SELECTED_SEARCH_ENGINE == SearchEngine.ARXIV.value:
        logger.info("Using ArXiv (via web_search config) with EnhancedArxivAPIWrapper.")
        return LoggedArxivSearch(
            name="web_search",
            api_wrapper=EnhancedArxivAPIWrapper(
                top_k_results=max_search_results,
                load_max_docs=max_search_results,
                load_all_available_meta=True,
            ),
        )
    else:
        logger.error(f"Unsupported or unconfigured search engine: {SELECTED_SEARCH_ENGINE}, falling back to DuckDuckGo by default for 'web_search'")
        return LoggedDuckDuckGoSearch(name="web_search", max_results=max_search_results)


# New function to specifically get the PubMed tool
def get_pubmed_search_tool(max_results: int = 10):
    """Returns an instance of the LoggedPubMedSearch tool."""
    logger.info(f"Providing PubMedSearchTool with max_results: {max_results}")
    return LoggedPubMedSearch()


# New function to specifically get the Google Scholar tool
def get_google_scholar_search_tool(top_k_results: int = 10, hl: str = "en", lr: str = "lang_en"):
    """Returns an instance of the LoggedGoogleScholarSearch tool."""
    logger.info(f"Providing GoogleScholarSearchTool with top_k_results: {top_k_results}, hl: {hl}, lr: {lr}.")
    try:
        return GoogleScholarSearchTool(
            name="google_scholar_search",
            top_k_results=top_k_results,
            hl=hl,
            lr=lr
        )
    except ValueError as e:
        logger.error(f"Failed to initialize GoogleScholarSearchTool: {e}. SERPAPI_API_KEY might be missing or invalid.")
        raise e


if __name__ == "__main__":
    results = LoggedDuckDuckGoSearch(
        name="web_search", max_results=3, output_format="list"
    ).invoke("cute panda")
    print(json.dumps(results, indent=2, ensure_ascii=False))

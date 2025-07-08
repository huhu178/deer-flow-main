"""
增强搜索工具 - 结合SerpAPI实时搜索与现有搜索能力
"""
import os
import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# SerpAPI导入
try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
    logger.info("✅ SerpAPI可用")
except ImportError:
    SERPAPI_AVAILABLE = False
    logger.warning("⚠️ SerpAPI不可用，将使用备用搜索方案")

def enhanced_real_time_search(query: str, num_results: int = 10) -> Dict[str, Any]:
    """增强的实时搜索 - 优先使用SerpAPI，备用Tavily"""
    
    if SERPAPI_AVAILABLE:
        try:
            api_key = os.getenv("SERPAPI_API_KEY")
            if not api_key:
                raise ValueError("SerpAPI API密钥未配置")
            
            search_params = {
                "q": query,
                "api_key": api_key,
                "engine": "google",
                "location": "China",
                "num": num_results,
                "google_domain": "google.com",
                "gl": "cn",
                "hl": "zh-cn",
            }
            
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            organic_results = results.get("organic_results", [])
            processed_results = []
            sources = []
            
            for i, result in enumerate(organic_results):
                title = result.get("title", "")
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                
                processed_results.append({
                    "type": "organic",
                    "title": title,
                    "url": link,
                    "content": snippet,
                    "relevance_score": 0.9 - (i * 0.1)
                })
                
                sources.append({
                    "label": title[:60] + "..." if len(title) > 60 else title,
                    "url": link,
                    "type": "web"
                })
            
            summary = generate_search_summary(query, processed_results)
            
            return {
                "status": "success",
                "source": "SerpAPI",
                "query": query,
                "results_count": len(processed_results),
                "results": processed_results,
                "sources": sources,
                "summary": summary,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"SerpAPI搜索失败: {str(e)}")
            return fallback_search(query, num_results, error=str(e))
    
    else:
        return fallback_search(query, num_results)


def fallback_search(query: str, num_results: int, error: str = None) -> Dict[str, Any]:
    """备用搜索方案"""
    try:
        from src.tools.tavily_search.tavily_search_tool import search_web
        tavily_results = search_web(query)
        
        processed_results = []
        sources = []
        
        if isinstance(tavily_results, list):
            for i, result in enumerate(tavily_results[:num_results]):
                if isinstance(result, dict):
                    processed_results.append({
                        "type": "web",
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "relevance_score": 0.8 - (i * 0.05)
                    })
                    
                    sources.append({
                        "label": result.get("title", "")[:60] + "...",
                        "url": result.get("url", ""),
                        "type": "web"
                    })
        
        summary = generate_search_summary(query, processed_results)
        
        return {
            "status": "fallback",
            "source": "Tavily",
            "query": query,
            "results_count": len(processed_results),
            "results": processed_results,
            "sources": sources,
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
            "fallback_reason": error or "SerpAPI不可用"
        }
        
    except Exception as e:
        logger.error(f"备用搜索也失败: {str(e)}")
        return {
            "status": "error",
            "query": query,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def generate_search_summary(query: str, results: List[Dict]) -> str:
    """基于搜索结果生成智能摘要"""
    if not results:
        return f"未找到关于'{query}'的相关信息。"
    
    sorted_results = sorted(results, key=lambda x: x.get("relevance_score", 0), reverse=True)
    top_results = sorted_results[:3]
    
    summary = f"🔍 **搜索摘要：{query}**\n\n📊 找到{len(results)}个相关结果\n\n🎯 **核心发现**：\n"
    
    for i, result in enumerate(top_results, 1):
        title = result.get("title", "")[:80]
        content = result.get("content", "")[:150]
        summary += f"\n{i}. **{title}**\n   {content}...\n"
    
    return summary


# 导出主要函数
__all__ = ["enhanced_real_time_search", "generate_search_summary"]

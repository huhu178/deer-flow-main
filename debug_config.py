#!/usr/bin/env python3
"""
调试配置和API问题的脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def debug_configuration():
    """调试配置问题"""
    print("🔧 调试配置信息...")
    
    try:
        from src.config.configuration import Configuration
        from src.config import SELECTED_SEARCH_ENGINE
        
        # 测试默认配置
        config = Configuration()
        print(f"✅ 默认配置:")
        print(f"   max_search_results: {config.max_search_results}")
        print(f"   max_plan_iterations: {config.max_plan_iterations}")
        print(f"   max_step_num: {config.max_step_num}")
        print(f"   interaction_mode: {config.interaction_mode}")
        
        # 测试搜索引擎配置
        print(f"\n🔍 搜索引擎配置:")
        print(f"   SELECTED_SEARCH_ENGINE: {SELECTED_SEARCH_ENGINE}")
        
        # 检查环境变量
        print(f"\n🌍 环境变量:")
        tavily_key = os.getenv("TAVILY_API_KEY", "未设置")
        print(f"   TAVILY_API_KEY: {'已设置' if tavily_key != '未设置' else '未设置'}")
        
        serper_key = os.getenv("SERPER_API_KEY", "未设置")
        print(f"   SERPER_API_KEY: {'已设置' if serper_key != '未设置' else '未设置'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_search_tools():
    """测试搜索工具"""
    print("\n🔍 测试搜索工具...")
    
    try:
        from src.tools.search import get_web_search_tool, LoggedTavilySearch
        
        # 测试获取搜索工具
        print("📋 测试get_web_search_tool...")
        search_tool = get_web_search_tool(max_search_results=10)
        print(f"✅ 搜索工具类型: {type(search_tool)}")
        print(f"   搜索工具名称: {getattr(search_tool, 'name', 'N/A')}")
        
        # 测试直接创建Tavily工具
        print("\n📋 测试直接创建Tavily工具...")
        try:
            tavily_tool = LoggedTavilySearch(max_results=5)
            print(f"✅ Tavily工具创建成功: {type(tavily_tool)}")
        except Exception as e:
            print(f"❌ Tavily工具创建失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 搜索工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_search():
    """测试模拟搜索请求"""
    print("\n🧪 测试模拟搜索请求...")
    
    try:
        from src.tools.search import get_web_search_tool
        
        # 创建搜索工具，使用较大的结果数
        search_tool = get_web_search_tool(max_search_results=10)
        
        # 执行一个简单的搜索
        test_query = "AI medical imaging research"
        print(f"🔍 测试查询: {test_query}")
        
        try:
            # 注意：这里可能会消耗API配额
            results = search_tool.invoke(test_query)
            
            if isinstance(results, list):
                print(f"✅ 搜索成功，返回 {len(results)} 个结果")
                for i, result in enumerate(results[:3], 1):
                    if isinstance(result, dict):
                        title = result.get('title', 'N/A')[:50]
                        print(f"   {i}. {title}...")
                    else:
                        print(f"   {i}. {str(result)[:50]}...")
            else:
                print(f"⚠️ 搜索返回非列表结果: {type(results)}")
                print(f"   结果预览: {str(results)[:200]}...")
                
        except Exception as search_error:
            print(f"❌ 搜索执行失败: {search_error}")
            
            # 分析错误类型
            if "api" in str(search_error).lower():
                print("   可能是API密钥或配额问题")
            elif "network" in str(search_error).lower() or "connection" in str(search_error).lower():
                print("   可能是网络连接问题")
            else:
                print("   未知错误类型")
        
        return True
        
    except Exception as e:
        print(f"❌ 模拟搜索测试失败: {e}")
        return False

def check_literature_preresearch():
    """检查文献预研究功能"""
    print("\n📚 检查文献预研究功能...")
    
    try:
        from src.graph.literature_preresearch_node import literature_preresearch_node
        print("✅ 文献预研究节点导入成功")
        
        from src.graph.builder import build_graph_with_memory
        graph = build_graph_with_memory()
        
        # 检查节点是否存在
        nodes = graph.nodes
        print(f"📋 图中的节点: {list(nodes.keys())}")
        
        if 'literature_preresearch' in nodes:
            print("✅ 文献预研究节点已正确添加到图中")
        else:
            print("❌ 文献预研究节点未找到")
        
        return True
        
    except Exception as e:
        print(f"❌ 文献预研究检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔧 调试配置和API问题")
    print("=" * 60)
    
    # 1. 调试配置
    config_ok = debug_configuration()
    
    print("\n" + "=" * 40)
    
    # 2. 测试搜索工具
    search_ok = test_search_tools()
    
    print("\n" + "=" * 40)
    
    # 3. 检查文献预研究
    literature_ok = check_literature_preresearch()
    
    print("\n" + "=" * 40)
    
    # 4. 可选：测试搜索（可能消耗API配额）
    user_input = input("\n🤔 是否要测试实际搜索请求？这可能会消耗API配额 (y/N): ")
    if user_input.lower() in ['y', 'yes']:
        test_mock_search()
    
    print("\n" + "=" * 60)
    print("🎯 调试总结:")
    print(f"   配置检查: {'✅ 通过' if config_ok else '❌ 失败'}")
    print(f"   搜索工具: {'✅ 通过' if search_ok else '❌ 失败'}")
    print(f"   文献预研究: {'✅ 通过' if literature_ok else '❌ 失败'}")
    
    if all([config_ok, search_ok, literature_ok]):
        print("\n🎉 所有检查通过！问题可能在运行时配置或API访问上。")
        print("\n📋 建议:")
        print("1. 检查网络连接和防火墙设置")
        print("2. 验证API密钥是否有效且有足够配额")
        print("3. 考虑临时使用DuckDuckGo作为备用搜索引擎")
    else:
        print("\n⚠️ 发现问题，请根据上述错误信息进行修复。")

if __name__ == "__main__":
    main() 
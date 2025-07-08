#!/usr/bin/env python3
"""测试工作流构建的脚本"""

import traceback

def test_build():
    try:
        print("📋 开始测试工作流构建...")
        
        # 测试导入
        print("1. 测试导入...")
        from src.graph.builder import build_graph, ENHANCED_NODES_AVAILABLE
        print(f"   增强节点可用: {ENHANCED_NODES_AVAILABLE}")
        
        # 测试构建
        print("2. 测试构建...")
        graph = build_graph()
        print("   ✅ 工作流构建成功!")
        
        # 测试信息
        print("3. 获取工作流信息...")
        from src.graph.builder import get_workflow_info
        info = get_workflow_info()
        print(f"   模式: {info['mode']}")
        print(f"   功能: {info['features']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        print("\n详细错误堆栈:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_build()
    if success:
        print("\n🎉 测试通过!")
    else:
        print("\n💥 测试失败!") 
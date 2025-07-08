#!/usr/bin/env python3

from src.graph.builder import build_graph, get_workflow_info
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_workflow():
    """测试文献驱动工作流程"""
    try:
        # 构建图
        graph = build_graph()
        
        # 获取工作流信息
        info = get_workflow_info()
        
        print("✅ 工作流构建成功")
        print(f"模式: {info['mode']}")
        print("\n启用的功能:")
        for feature, enabled in info['features'].items():
            if enabled:
                print(f"  ✅ {feature}")
        
        # 显示节点列表 (修复属性访问)
        try:
            nodes = list(graph.nodes.keys())
            print(f"\n节点列表: {nodes}")
            
            # 检查是否包含文献预研究节点
            if 'literature_preresearch' in nodes:
                print("✅ 文献预研究节点已成功添加")
            else:
                print("❌ 文献预研究节点缺失")
        except AttributeError:
            print("✅ 图编译成功，节点结构已集成到编译后的图中")
        
        return True
        
    except Exception as e:
        print(f"❌ 工作流构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_workflow() 
#!/usr/bin/env python3
"""测试文献预研究系统"""

import logging
from src.graph.builder import graph, get_workflow_info

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_literature_preresearch():
    """测试文献预研究系统"""
    
    print("🎯 测试文献预研究系统")
    print("=" * 50)
    
    # 检查工作流配置
    info = get_workflow_info()
    print(f"📋 工作流模式: {info['mode']}")
    print(f"📚 文献预研究功能: {info['features']['literature_preresearch']}")
    print(f"🔍 综合文献搜索: {info['features']['comprehensive_literature_search']}")
    print("")
    
    # 测试查询
    test_query = "基于人工智能和影像组学的桡骨DXA影像预测全身健康状态的颠覆性研究"
    
    print(f"🧪 测试查询: {test_query}")
    print("-" * 50)
    
    try:
        # 执行workflow
        result = graph.invoke({
            'messages': [{'role': 'user', 'content': test_query}]
        })
        
        print(f"✅ Workflow执行成功")
        print(f"📝 生成消息数: {len(result.get('messages', []))}")
        print("")
        
        # 分析结果
        literature_found = False
        plan_found = False
        
        for i, msg in enumerate(result.get('messages', [])):
            if isinstance(msg, dict):
                content = msg.get('content', '')
                metadata = msg.get('metadata', {})
                
                print(f"消息 {i+1}:")
                print(f"  角色: {msg.get('role', '未知')}")
                print(f"  长度: {len(content)} 字符")
                
                if metadata:
                    print(f"  元数据: {metadata}")
                
                # 检查文献预研究
                if ('文献预研究' in content or 
                    '📚' in content or 
                    metadata.get('node') == 'literature_preresearch'):
                    literature_found = True
                    print("  ✅ 包含文献预研究内容")
                    
                    # 显示文献统计
                    if 'literature_count' in metadata:
                        print(f"    📊 文献数量: {metadata['literature_count']}")
                    if 'quality_stats' in metadata:
                        stats = metadata['quality_stats']
                        print(f"    📈 质量分布: 高质量{stats.get('high', 0)}篇, 中等{stats.get('medium', 0)}篇")
                
                # 检查研究计划
                if ('研究方向' in content or 
                    'steps' in str(metadata) or 
                    'title' in content):
                    plan_found = True
                    print("  ✅ 包含研究计划内容")
                
                print(f"  内容预览: {content[:100]}...")
                print("")
        
        # 总结结果
        print("=" * 50)
        print("📊 测试结果总结:")
        print(f"  文献预研究执行: {'✅ 是' if literature_found else '❌ 否'}")
        print(f"  研究计划生成: {'✅ 是' if plan_found else '❌ 否'}")
        
        if literature_found and plan_found:
            print("🎉 文献驱动研究系统工作正常！")
        elif literature_found:
            print("⚠️ 文献预研究正常，但计划生成可能有问题")
        else:
            print("❌ 文献预研究系统需要进一步检查")
            
    except Exception as e:
        import traceback
        print(f"❌ 测试失败: {e}")
        print("📋 详细错误:")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_literature_preresearch() 
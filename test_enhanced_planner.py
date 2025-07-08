#!/usr/bin/env python3
"""
测试增强规划节点
"""

import sys
import os
sys.path.append('src')

from src.graph.enhanced_planning_nodes import EnhancedPlannerNode, PlanningConfig

def test_enhanced_planner():
    """测试增强规划节点"""
    print("🧪 开始测试增强规划节点...")
    
    # 测试增强规划节点
    config = PlanningConfig(max_planning_rounds=1, quality_threshold=0.5)
    planner = EnhancedPlannerNode('BASIC_MODEL', config)
    
    # 模拟状态
    state = {
        'planning_rounds': 0,
        'planning_history': [],
        'final_understanding': {
            'core_objectives': ['开发AI医学诊断系统', '基于DXA影像预测健康状态'],
            'key_entities_and_concepts': ['AI', 'DXA影像', '健康预测', '影像组学', '桡骨'],
            'understanding_confidence': 0.9,
            'information_completeness': 0.8
        },
        'messages': []
    }
    
    try:
        result = planner(state)
        print('✅ 增强规划节点测试成功')
        print(f'返回类型: {type(result)}')
        print(f'goto目标: {getattr(result, "goto", "无")}')
        
        if hasattr(result, 'update') and result.update:
            plan_data = result.update.get('current_plan', {})
            print(f'生成的计划标题: {plan_data.get("title", "未知")}')
            print(f'研究方向数量: {len(plan_data.get("research_directions", []))}')
            
            # 显示研究方向
            directions = plan_data.get("research_directions", [])
            if directions:
                print("\n📋 生成的研究方向:")
                for i, direction in enumerate(directions, 1):
                    print(f"  {i}. {direction.get('title', '未知标题')}")
                    print(f"     {direction.get('description', '无描述')}")
            
            # 检查消息
            messages = result.update.get('messages', [])
            if messages:
                print(f"\n💬 生成的消息数量: {len(messages)}")
                last_message = messages[-1]
                if hasattr(last_message, 'content'):
                    content_preview = last_message.content[:200] + "..." if len(last_message.content) > 200 else last_message.content
                    print(f"最后消息预览: {content_preview}")
                    
                    # 检查是否包含详细计划
                    if "详细研究计划" in last_message.content:
                        print("✅ 包含详细计划内容")
                    else:
                        print("⚠️ 未包含详细计划内容")
        else:
            print('⚠️ 无更新数据')
            
    except Exception as e:
        print(f'❌ 测试失败: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_planner() 
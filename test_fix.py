#!/usr/bin/env python3
"""
测试Plan验证修复是否成功
"""

import sys
import os

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_plan_validation():
    """测试Plan验证是否正常工作"""
    try:
        from src.utils.types import Plan
        from src.graph.nodes import _create_default_plan_dict
        
        print("🧪 测试Plan验证...")
        
        # 测试默认计划函数
        default_plan = _create_default_plan_dict()
        print(f"📝 默认计划数据: {default_plan}")
        
        # 测试Plan验证
        plan = Plan(**default_plan)
        print("✅ Plan验证成功！")
        print(f"📊 计划标题: {plan.title}")
        print(f"📋 步骤数量: {len(plan.steps)}")
        print(f"🌍 语言环境: {plan.locale}")
        print(f"✅ 上下文足够: {plan.has_enough_context}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_empty_dict_handling():
    """测试空字典处理"""
    try:
        from src.utils.types import Plan
        
        print("\n🧪 测试空字典处理...")
        
        # 模拟空字典错误
        empty_dict = {}
        try:
            Plan(**empty_dict)
            print("❌ 应该失败但没有失败")
            return False
        except Exception as e:
            print(f"✅ 空字典正确触发验证错误: {type(e).__name__}")
            
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🔧 开始测试Plan验证修复...")
    
    success1 = test_plan_validation()
    success2 = test_empty_dict_handling()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！修复成功！")
        print("📋 human_feedback_node现在应该能正常工作了")
    else:
        print("\n�� 部分测试失败，需要进一步检查") 
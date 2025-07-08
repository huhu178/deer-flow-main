#!/usr/bin/env python3
"""快速测试Plan验证修复"""

import sys
import os
sys.path.append('src')

def test_default_plan():
    try:
        from src.graph.nodes import _create_default_plan_dict
        from src.utils.types import Plan
        
        print("🧪 测试默认计划...")
        default_plan = _create_default_plan_dict()
        
        print("📝 测试Plan验证...")
        plan = Plan(**default_plan)
        
        print("✅ 修复成功！")
        print(f"   标题: {plan.title}")
        print(f"   步骤: {len(plan.steps)}")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_default_plan() 
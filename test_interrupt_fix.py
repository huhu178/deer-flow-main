#!/usr/bin/env python3
"""
测试interrupt函数修复
"""

import sys
import asyncio
sys.path.append('src')

async def test_human_feedback_node():
    """测试human_feedback_node的interrupt修复"""
    from src.graph.nodes import human_feedback_node
    from langchain_core.messages import AIMessage
    
    print("🧪 测试human_feedback_node的interrupt修复...")
    
    # 模拟状态：最后一条消息是AI消息（计划）
    state = {
        'messages': [
            AIMessage(content='这是一个测试研究计划')
        ]
    }
    
    try:
        result = await human_feedback_node(state)
        print('✅ human_feedback_node修复成功')
        print(f'返回类型: {type(result)}')
        print('✅ interrupt函数现在能正确工作了')
        return True
    except Exception as e:
        print(f'❌ 仍有错误: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_human_feedback_node())
    if success:
        print("\n🎉 所有测试通过！系统现在应该能正常运行了。")
    else:
        print("\n❌ 测试失败，需要进一步调查。") 
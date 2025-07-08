#!/usr/bin/env python3
"""
测试思考过程功能
"""
import sys
sys.path.append('src')

from graph.literature_preresearch_node import create_literature_context

def test_thinking_process():
    """测试文献预研究的思考过程"""
    print("🧪 测试思考过程功能...")
    
    # 模拟文献搜索结果
    test_results = {
        'literature_count': 25,
        'quality_stats': {
            'high': 8,
            'medium': 12,
            'low': 5
        }
    }
    
    # 生成文献上下文
    context = create_literature_context(test_results)
    
    # 检查是否包含思考过程
    if '<thinking>' in context and '</thinking>' in context:
        print('✅ 思考过程模块工作正常！')
        print('\n📝 生成的思考过程示例:')
        
        # 提取思考内容
        start = context.find('<thinking>') + 10
        end = context.find('</thinking>')
        thinking_content = context[start:end].strip()
        
        print('=' * 50)
        print(thinking_content[:300] + '...')
        print('=' * 50)
        
        print(f'\n📊 完整内容长度: {len(context)} 字符')
        return True
    else:
        print('❌ 思考过程模块未工作！')
        print(f'内容预览: {context[:200]}...')
        return False

if __name__ == "__main__":
    test_thinking_process() 
#!/usr/bin/env python3
"""调试workflow消息"""

from src.graph.builder import graph

def debug_workflow():
    # 执行简单测试
    result = graph.invoke({
        'messages': [{'role': 'user', 'content': '基于人工智能和影像组学的桡骨DXA影像预测全身健康状态的颠覆性研究'}]
    })

    print('📝 所有消息内容:')
    for i, msg in enumerate(result.get('messages', [])):
        print(f'--- 消息 {i+1} ---')
        print(f'类型: {type(msg)}')
        if isinstance(msg, dict):
            print(f'角色: {msg.get("role", "未知")}')
            print(f'内容长度: {len(msg.get("content", ""))}')
            metadata = msg.get('metadata', {})
            if metadata:
                print(f'元数据: {metadata}')
            content = msg.get('content', '')
            print(f'内容预览: {content[:200]}...')
        else:
            print(f'内容: {str(msg)[:200]}...')
        print()

    # 检查其他状态
    print('🔍 其他状态字段:')
    for key, value in result.items():
        if key != 'messages':
            print(f'{key}: {type(value)} - {len(str(value))} 字符')
    print()

if __name__ == "__main__":
    debug_workflow() 
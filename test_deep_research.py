#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenRouter Deep Research 功能测试
"""

import sys
sys.path.append('src')

def test_deep_research_simple():
    """简单测试 Deep Research 功能"""
    
    try:
        from llms.llm import get_llm_by_type
        
        print("🔬 测试 OpenRouter Gemini 2.5 Pro Deep Research")
        print("=" * 50)
        
        # 获取BASIC_MODEL类型的LLM实例（对应OpenRouter配置）
        llm = get_llm_by_type("BASIC_MODEL")
        
        # 简单的Deep Research测试
        prompt = """
[Deep Research Mode]

请对"2025年人工智能发展趋势"进行深度研究：

1. 分析技术突破点
2. 评估商业应用前景  
3. 识别潜在风险
4. 预测发展方向

请展示思考过程并生成结构化报告。
"""
        
        print("🤔 正在执行深度研究...")
        
        # 使用invoke方法调用模型
        from langchain.schema import HumanMessage
        messages = [HumanMessage(content=prompt)]
        result = llm.invoke(messages)
        
        print("✅ 研究完成！")
        print("📝 报告预览：")
        print("-" * 50)
        
        # 提取结果内容
        content = result.content if hasattr(result, 'content') else str(result)
        print(content[:800] + "..." if len(content) > 800 else content)
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_deep_research_simple() 
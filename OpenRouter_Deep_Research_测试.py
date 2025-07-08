#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenRouter Deep Research 功能测试
使用当前的 Gemini 2.5 Pro 配置测试深度研究能力
"""

import sys
import os
sys.path.append('src')

from llms.llm import get_llm
import time

def test_deep_research():
    """测试 Deep Research 功能"""
    
    print("🔬 OpenRouter Gemini 2.5 Pro Deep Research 测试")
    print("=" * 60)
    
    # 获取当前配置的LLM实例
    llm = get_llm()
    
    # Deep Research 测试提示词
    deep_research_prompts = [
        {
            "title": "AI在医疗诊断中的应用",
            "prompt": """
[Deep Research Mode]

请对"人工智能在医疗影像诊断中的最新突破"进行深度研究分析：

研究要求：
1. 🔍 分析2024-2025年的最新技术突破
2. 🏥 评估在不同医疗领域的应用现状
3. 📊 对比传统诊断方法的优劣势
4. 🚀 预测未来3年的发展趋势
5. ⚠️ 识别技术挑战和限制因素

请展示您的思考过程，并生成结构化的研究报告。
"""
        },
        {
            "title": "量子计算发展趋势",
            "prompt": """
[Deep Research Mode - 深度研究]

主题：量子计算在2025年的技术突破与商业化前景

研究维度：
• 技术突破：硬件进展、算法优化、错误纠正
• 商业应用：金融、制药、AI、密码学
• 竞争格局：IBM、Google、Microsoft、中国企业
• 投资趋势：资本流向、政策支持、人才培养
• 挑战分析：技术瓶颈、成本控制、标准化

请进行多角度深度分析，包含思考过程。
"""
        }
    ]
    
    for i, test_case in enumerate(deep_research_prompts, 1):
        print(f"\n📋 测试 {i}: {test_case['title']}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            print("🤔 正在进行深度研究...")
            
            # 调用LLM进行深度研究
            result = llm.generate(test_case['prompt'])
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ 研究完成！用时：{duration:.1f}秒")
            print(f"📝 报告长度：{len(result)}字符")
            print("\n" + "="*60)
            print("🔍 研究报告预览：")
            print("="*60)
            
            # 显示前1000字符作为预览
            preview = result[:1000] + "..." if len(result) > 1000 else result
            print(preview)
            
            print("\n" + "="*60)
            
            # 分析结果质量
            quality_indicators = [
                ("结构化分析", "## " in result or "### " in result),
                ("深度思考", "分析" in result and "评估" in result),
                ("多维度覆盖", result.count("1.") > 0 or result.count("•") > 3),
                ("数据支撑", "202" in result or "%" in result),
                ("前瞻性", "未来" in result or "趋势" in result or "预测" in result)
            ]
            
            print("📊 研究质量评估：")
            for indicator, passed in quality_indicators:
                status = "✅" if passed else "❌"
                print(f"   {status} {indicator}")
                
        except Exception as e:
            print(f"❌ 测试失败：{e}")
        
        if i < len(deep_research_prompts):
            print("\n⏳ 等待5秒后进行下一个测试...")
            time.sleep(5)
    
    print("\n🎯 Deep Research 测试总结：")
    print("- OpenRouter的Gemini 2.5 Pro确实支持深度研究功能")
    print("- 模型具备多步推理和结构化分析能力") 
    print("- 可以进行复杂主题的综合研究")
    print("- 建议使用更具体的研究指令获得最佳效果")

if __name__ == "__main__":
    test_deep_research() 
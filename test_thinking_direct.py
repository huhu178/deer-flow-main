#!/usr/bin/env python3
"""
直接测试Thinking功能
绕过配置缓存，直接验证thinking是否工作
"""

import os
import sys
import yaml
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from langchain_openai import ChatOpenAI

def test_thinking_directly():
    """直接测试thinking功能"""
    print("🔍 直接测试Thinking功能")
    print("=" * 60)
    
    # 读取配置
    with open('conf.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    basic_config = config['llm']['BASIC_MODEL']
    
    print(f"📋 配置信息:")
    print(f"  base_url: {basic_config['base_url']}")
    print(f"  model: {basic_config['model']}")
    print(f"  API key: {basic_config['api_key'][:20]}...")
    
    # 创建LLM实例
    print("\n🤖 创建LLM实例...")
    
    llm = ChatOpenAI(
        base_url=basic_config['base_url'],
        model=basic_config['model'],
        api_key=basic_config['api_key'],
        max_tokens=basic_config['max_tokens'],
        temperature=basic_config['temperature'],
        timeout=basic_config['timeout']
    )
    
    print(f"✅ LLM实例创建成功")
    print(f"  实际模型: {llm.model_name}")
    
    # 测试thinking功能
    thinking_test_prompt = """
请解决这个复杂的逻辑问题，并详细展示你的思考过程：

有三个盒子A、B、C，每个盒子里都有一些球。已知：
1. A盒子里的球数是B盒子的2倍
2. B盒子里的球数是C盒子的3倍  
3. 三个盒子里球的总数是66个

请问每个盒子里有多少个球？

要求：请在回答中清楚展示你的分析步骤和推理过程。
"""
    
    print("\n🧠 测试复杂推理问题...")
    print("问题:", thinking_test_prompt.strip())
    print("\n" + "-" * 60)
    print("AI回答:")
    print("-" * 60)
    
    try:
        response = llm.invoke(thinking_test_prompt)
        print(response.content)
        
        # 检查thinking特征
        content = response.content.lower()
        thinking_indicators = {
            "包含thinking标签": "<thinking>" in content,
            "展示分析步骤": any(word in content for word in ["步骤", "首先", "然后", "接着", "最后"]),
            "显示推理过程": any(word in content for word in ["分析", "推理", "思考", "考虑"]),
            "包含计算过程": any(word in content for word in ["设", "假设", "计算", "等式", "方程"]),
            "有逻辑链条": any(word in content for word in ["因为", "所以", "由于", "因此", "根据"])
        }
        
        print("\n" + "=" * 60)
        print("🔍 Thinking特征分析:")
        print("=" * 60)
        
        thinking_count = 0
        for feature, detected in thinking_indicators.items():
            status = "✅" if detected else "❌"
            print(f"{status} {feature}")
            if detected:
                thinking_count += 1
        
        print(f"\n📊 Thinking特征检测: {thinking_count}/{len(thinking_indicators)}")
        
        if thinking_count >= 3:
            print("🎉 Thinking功能工作正常！")
        elif thinking_count >= 1:
            print("⚠️ Thinking功能部分工作，可能需要优化")
        else:
            print("❌ 未检测到明显的thinking特征")
            
        print(f"\n📏 响应长度: {len(response.content)} 字符")
        
        return response.content
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return None

def test_simple_vs_complex():
    """对比简单和复杂问题的响应"""
    print("\n\n🔬 对比测试：简单 vs 复杂问题")
    print("=" * 60)
    
    # 读取配置
    with open('conf.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    basic_config = config['llm']['BASIC_MODEL']
    
    llm = ChatOpenAI(
        base_url=basic_config['base_url'],
        model=basic_config['model'], 
        api_key=basic_config['api_key'],
        max_tokens=basic_config['max_tokens'],
        temperature=basic_config['temperature']
    )
    
    test_cases = [
        {
            "type": "简单问题",
            "prompt": "3 + 5 = ?"
        },
        {
            "type": "复杂问题", 
            "prompt": "一家初创公司面临资金困难，有以下三个选择：1)寻求风险投资但需出让30%股权，2)申请银行贷款年利率8%，3)暂停扩张削减成本。请分析每个选择的利弊并给出建议。"
        }
    ]
    
    for case in test_cases:
        print(f"\n📋 {case['type']}:")
        print(f"问题: {case['prompt']}")
        print("-" * 40)
        
        try:
            response = llm.invoke(case['prompt'])
            
            # 检查thinking痕迹
            has_thinking = any(indicator in response.content.lower() for indicator in [
                "<thinking>", "分析", "考虑", "首先", "然后", "因此", "步骤"
            ])
            
            print(f"💭 包含thinking痕迹: {'✅' if has_thinking else '❌'}")
            print(f"📏 响应长度: {len(response.content)} 字符")
            print(f"📝 回答预览: {response.content[:200]}...")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")

def main():
    """主函数"""
    print("🚀 OpenRouter Thinking 功能验证测试")
    print("直接测试配置中的thinking模型是否正常工作")
    print("=" * 60)
    
    # 直接测试thinking
    test_thinking_directly()
    
    # 对比测试
    test_simple_vs_complex()
    
    print("\n" + "=" * 60)
    print("🎯 测试完成！")
    print("\n💡 如果看到详细的分析步骤和推理过程，说明thinking功能正常")
    print("💡 如果只有简单答案，可能需要检查模型配置或提示词")

if __name__ == "__main__":
    main() 
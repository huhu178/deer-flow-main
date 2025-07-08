#!/usr/bin/env python3
"""
测试OpenRouter Gemini 2.5 Pro Thinking功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llms.llm import get_llm
import yaml

def test_thinking_capability():
    """测试thinking功能"""
    print("🔍 测试OpenRouter Gemini 2.5 Pro Thinking功能...")
    
    try:
        # 加载配置
        with open('conf.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        llm_config = config['llm']['BASIC_MODEL']
        print(f"📋 当前模型: {llm_config['model']}")
        
        # 获取LLM实例
        llm = get_llm("BASIC_MODEL")
        
        # 测试thinking功能的提示词
        test_prompt = """
请解决这个数学问题，并详细展示你的思考过程：

有一个班级，学生总数是一个两位数。如果按照每行5个人排队，最后一行只有3个人；
如果按照每行6个人排队，最后一行只有4个人；如果按照每行7个人排队，最后一行只有5个人。
请问这个班级有多少个学生？

请在回答中展示完整的思考和推理过程。
"""
        
        print("\n🤖 正在调用thinking版本...")
        print("=" * 60)
        
        # 调用LLM
        response = llm.invoke(test_prompt)
        
        print("📝 AI回答:")
        print(response.content)
        print("=" * 60)
        
        # 检查是否包含thinking标签
        if "<thinking>" in response.content or "思考过程" in response.content:
            print("✅ Thinking功能正常工作！AI展示了思考过程")
        else:
            print("⚠️  没有检测到明显的thinking过程，但模型仍在工作")
            
        print(f"\n📊 响应长度: {len(response.content)} 字符")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("请检查配置文件和网络连接")

def test_complex_reasoning():
    """测试复杂推理任务"""
    print("\n🧠 测试复杂推理任务...")
    
    try:
        llm = get_llm("BASIC_MODEL")
        
        complex_prompt = """
假设你是一个AI研究专家，请分析以下场景并提供深度思考：

场景：一家科技公司想要开发一个新的AI助手产品，他们面临以下选择：
1. 使用现有的大语言模型API（如GPT、Claude）
2. 自主训练专门的模型
3. 采用混合方案（API + 本地微调）

请从技术、成本、风险、时间等多个维度进行分析，并给出最优建议。
要求展示完整的思考和权衡过程。
"""
        
        print("🤖 正在进行复杂推理...")
        response = llm.invoke(complex_prompt)
        
        print("📝 复杂推理结果:")
        print(response.content[:1000] + "..." if len(response.content) > 1000 else response.content)
        
        return True
        
    except Exception as e:
        print(f"❌ 复杂推理测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 OpenRouter Gemini 2.5 Pro Thinking功能测试")
    print("=" * 60)
    
    # 基础thinking测试
    test_thinking_capability()
    
    # 复杂推理测试
    test_complex_reasoning()
    
    print("\n✨ 测试完成！")
    print("💡 如果看到详细的思考过程，说明thinking功能已成功启用") 
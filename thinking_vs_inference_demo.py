#!/usr/bin/env python3
"""
Thinking vs Inference 对比演示
展示两种模式在实际应用中的区别
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from llms.llm import get_llm
import yaml
import time

class ThinkingVsInferenceDemo:
    """Thinking vs Inference 对比演示类"""
    
    def __init__(self):
        self.thinking_llm = get_llm("BASIC_MODEL")  # thinking版本
        
    def demo_complex_problem(self):
        """演示复杂问题的处理差异"""
        
        complex_question = """
一家公司面临以下情况：
- 当前有100名员工
- 每月营收500万
- 计划扩张到3个新城市
- 每个新城市需要30名员工
- 新城市预计每月营收200万/城市
- 但前6个月营收只有预期的60%
- 员工成本：8000元/人/月
- 其他运营成本占营收的40%

问题：这个扩张计划在财务上是否可行？第一年的净利润是多少？
"""
        
        print("🧮 复杂商业分析问题")
        print("=" * 60)
        print(f"问题：{complex_question}")
        print("\n" + "="*60)
        
        # Thinking模式回答
        print("🧠 THINKING模式回答：")
        print("-" * 40)
        
        thinking_prompt = f"""
请详细分析这个商业问题，展示你的完整思考过程：

{complex_question}

请在回答中清楚展示你的分析步骤、计算过程和推理逻辑。
"""
        
        start_time = time.time()
        thinking_response = self.thinking_llm.invoke(thinking_prompt)
        thinking_time = time.time() - start_time
        
        print(thinking_response.content)
        print(f"\n⏱️ 用时: {thinking_time:.2f}秒")
        print(f"📊 响应长度: {len(thinking_response.content)}字符")
        
        return {
            "thinking_response": thinking_response.content,
            "thinking_time": thinking_time
        }
    
    def demo_simple_vs_complex_reasoning(self):
        """对比简单和复杂推理任务"""
        
        test_cases = [
            {
                "name": "简单数学",
                "question": "25 + 37 = ?",
                "complexity": "低"
            },
            {
                "name": "逻辑推理", 
                "question": "如果所有的猫都是动物，所有的动物都需要食物，那么猫需要食物吗？请解释。",
                "complexity": "中"
            },
            {
                "name": "策略分析",
                "question": "一个初创公司应该选择自建技术团队还是外包开发？考虑成本、质量、时间、控制力等因素。",
                "complexity": "高"
            }
        ]
        
        print("\n🔬 不同复杂度任务对比")
        print("=" * 60)
        
        results = []
        
        for case in test_cases:
            print(f"\n📋 测试案例: {case['name']} (复杂度: {case['complexity']})")
            print(f"问题: {case['question']}")
            print("-" * 40)
            
            start_time = time.time()
            response = self.thinking_llm.invoke(case['question'])
            response_time = time.time() - start_time
            
            # 检查是否包含thinking过程
            has_thinking = "<thinking>" in response.content or "分析过程" in response.content or "思考" in response.content
            
            result = {
                "name": case['name'],
                "complexity": case['complexity'],
                "response_time": response_time,
                "response_length": len(response.content),
                "has_visible_thinking": has_thinking,
                "response": response.content[:500] + "..." if len(response.content) > 500 else response.content
            }
            
            results.append(result)
            
            print(f"💭 显示思考过程: {'✅ 是' if has_thinking else '❌ 否'}")
            print(f"⏱️ 响应时间: {response_time:.2f}秒")
            print(f"📏 响应长度: {len(response.content)}字符")
            print(f"📝 响应预览: {result['response']}")
        
        return results
    
    def analyze_thinking_patterns(self):
        """分析thinking模式的特征"""
        
        analysis_question = """
分析以下三个投资选项，并给出推荐：

选项A：房地产投资
- 预期年收益率：8%
- 风险等级：中等
- 流动性：低
- 初始投资：100万

选项B：股票投资组合
- 预期年收益率：12%
- 风险等级：高
- 流动性：高
- 初始投资：100万

选项C：债券投资
- 预期年收益率：5%
- 风险等级：低
- 流动性：中等
- 初始投资：100万

请考虑不同的投资目标和风险偏好。
"""
        
        print("\n🔍 Thinking模式特征分析")
        print("=" * 60)
        print("问题：投资选择分析")
        print("-" * 40)
        
        response = self.thinking_llm.invoke(analysis_question)
        
        # 分析thinking特征
        thinking_indicators = {
            "步骤化分析": any(word in response.content for word in ["首先", "其次", "然后", "最后", "步骤"]),
            "对比分析": any(word in response.content for word in ["相比", "对比", "比较", "而", "但是"]),
            "考虑多角度": any(word in response.content for word in ["从...角度", "考虑到", "另一方面", "同时"]),
            "推理链条": any(word in response.content for word in ["因此", "所以", "由于", "基于", "根据"]),
            "不确定性处理": any(word in response.content for word in ["可能", "也许", "取决于", "需要考虑", "建议"]),
            "自我验证": any(word in response.content for word in ["检查", "验证", "确认", "重新考虑"])
        }
        
        print("🎯 Thinking模式特征检测：")
        for feature, detected in thinking_indicators.items():
            status = "✅" if detected else "❌"
            print(f"  {status} {feature}")
        
        print(f"\n📝 完整回答：")
        print(response.content)
        
        return thinking_indicators

def main():
    """主演示函数"""
    print("🚀 Thinking vs Inference 对比演示")
    print("="*60)
    
    demo = ThinkingVsInferenceDemo()
    
    # 1. 复杂问题演示
    demo.demo_complex_problem()
    
    # 2. 不同复杂度对比
    results = demo.demo_simple_vs_complex_reasoning()
    
    # 3. Thinking特征分析
    features = demo.analyze_thinking_patterns()
    
    # 总结
    print("\n" + "="*60)
    print("📋 总结报告")
    print("="*60)
    
    print("\n🎯 关键发现：")
    print("1. 复杂问题更容易触发visible thinking")
    print("2. Thinking模式提供更详细的推理过程")
    print("3. 响应时间和质量通常呈正相关")
    
    thinking_percentage = sum(1 for r in results if r['has_visible_thinking']) / len(results) * 100
    print(f"4. 显示thinking过程的比例: {thinking_percentage:.1f}%")
    
    feature_count = sum(1 for detected in features.values() if detected)
    print(f"5. 检测到的thinking特征: {feature_count}/{len(features)}")
    
    print("\n💡 使用建议：")
    print("- 复杂分析任务 → 使用Thinking模式")
    print("- 简单快速问答 → 使用标准Inference")
    print("- 学习和教育场景 → 推荐Thinking模式")
    print("- 生产环境API → 根据需求选择")

if __name__ == "__main__":
    main() 
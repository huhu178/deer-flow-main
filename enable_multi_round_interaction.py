#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
启用多轮交互功能
==============

这个脚本演示如何在deer-flow系统中启用多轮理解与规划交互功能。

运行方式：
```bash
cd deer-flow-main
python enable_multi_round_interaction.py
```

特性：
- 🔄 支持最多5轮理解交互
- 📋 支持最多3轮规划优化  
- 🧠 智能复杂度检测
- 💡 自动模式切换
- 🎯 完全兼容现有系统
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from src.config.configuration import (
    Configuration, 
    InteractionPresets,
    create_interaction_config
)
from src.graph.enhanced_node_integration import (
    enhanced_coordinator_node,
    enhanced_planner_node, 
    configure_enhanced_mode,
    get_interaction_stats
)
from langchain_core.messages import HumanMessage

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_multi_round_interaction():
    """演示多轮交互功能"""
    print("\n" + "="*60)
    print("🚀 Deer-Flow 多轮交互功能演示")
    print("="*60)
    
    # 测试场景
    test_scenarios = [
        {
            "name": "简单问候",
            "input": "你好，你能做什么？",
            "expected": "标准模式 (1轮交互)",
            "description": "简单问候应该使用标准模式快速响应"
        },
        {
            "name": "复杂研究项目",
            "input": "我想开发一个基于AI和影像组学的桡骨DXA全身健康预测系统，需要分析医学影像数据、预测疾病风险、提供个性化治疗建议，并且要考虑多种算法的对比和优化",
            "expected": "增强模式 (多轮交互)",
            "description": "复杂项目应该自动启用多轮深度理解和规划"
        },
        {
            "name": "技术开发需求",
            "input": "设计一个机器学习框架，支持多模态数据处理和实时推理",
            "expected": "增强模式 (多轮交互)",
            "description": "技术开发需求应该启用深度规划"
        }
    ]
    
    print("\n📊 复杂度检测测试:")
    print("-" * 50)
    
    # 导入检测器
    from src.graph.enhanced_node_integration import _enhanced_wrapper
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   输入: {scenario['input'][:80]}...")
        
        # 创建测试状态
        test_state = {
            "messages": [HumanMessage(content=scenario['input'])]
        }
        
        # 检测复杂度
        should_enhance = _enhanced_wrapper._detect_complexity(test_state)
        actual_mode = "增强模式 (多轮交互)" if should_enhance else "标准模式 (1轮交互)"
        
        print(f"   预期: {scenario['expected']}")
        print(f"   实际: {actual_mode}")
        print(f"   结果: {'✅ 正确' if actual_mode == scenario['expected'] else '⚠️ 需调整'}")
        print(f"   说明: {scenario['description']}")


def show_configuration_options():
    """展示配置选项"""
    print("\n" + "="*60)
    print("⚙️ 多轮交互配置选项")
    print("="*60)
    
    # 预设配置
    presets = {
        "标准模式": InteractionPresets.get_standard_config(),
        "增强模式": InteractionPresets.get_enhanced_config(),
        "自动模式": InteractionPresets.get_auto_config(),
        "快速模式": InteractionPresets.get_fast_config()
    }
    
    for name, config in presets.items():
        print(f"\n📋 {name}:")
        print(f"   理解轮次: {config.max_understanding_rounds}")
        print(f"   规划轮次: {config.max_planning_rounds}")
        print(f"   质量阈值: {config.understanding_quality_threshold}")
        print(f"   深度思考: {'启用' if config.enable_deep_thinking else '禁用'}")
        print(f"   交互模式: {config.interaction_mode}")


def create_custom_config_example():
    """展示自定义配置示例"""
    print("\n" + "="*60)
    print("🔧 自定义配置示例")
    print("="*60)
    
    # 创建自定义配置
    custom_config = create_interaction_config(
        mode="enhanced",
        understanding_rounds=3,  # 3轮理解
        planning_rounds=2,       # 2轮规划
        quality_threshold=0.75   # 75%质量阈值
    )
    
    print("\n自定义配置代码:")
    print("""
from src.config.configuration import create_interaction_config

# 创建自定义配置
config = create_interaction_config(
    mode="enhanced",           # 启用增强模式
    understanding_rounds=3,    # 最多3轮理解
    planning_rounds=2,         # 最多2轮规划
    quality_threshold=0.75     # 75%质量阈值
)

# 在工作流中使用
result = coordinator_node(state, config)
    """)
    
    print(f"✅ 配置已创建: {custom_config.interaction_mode}模式")
    print(f"   理解轮次: {custom_config.max_understanding_rounds}")
    print(f"   规划轮次: {custom_config.max_planning_rounds}")


def integration_guide():
    """集成指南"""
    print("\n" + "="*60)
    print("📖 集成指南")
    print("="*60)
    
    print("\n🔄 方法1: 自动集成 (推荐)")
    print("-" * 30)
    print("""
# 在现有代码中只需要导入增强节点即可自动支持多轮交互
from src.graph.enhanced_node_integration import (
    enhanced_coordinator_node as coordinator_node,
    enhanced_planner_node as planner_node
)

# 原有调用方式完全不变，自动支持多轮交互
result = coordinator_node(state)
    """)
    
    print("\n🔧 方法2: 显式配置")
    print("-" * 30)
    print("""
from src.graph.enhanced_node_integration import configure_enhanced_mode

# 配置增强模式
config = configure_enhanced_mode(
    interaction_mode="enhanced",
    understanding_rounds=5,
    planning_rounds=3
)

# 使用配置
result = coordinator_node(state, config)
    """)
    
    print("\n🛠️ 方法3: 工作流补丁")
    print("-" * 30)
    print("""
from src.graph.enhanced_node_integration import patch_workflow_with_enhanced_nodes

# 给现有工作流添加增强功能
patch_workflow_with_enhanced_nodes(workflow)
    """)


def interactive_demo():
    """交互式演示"""
    print("\n" + "="*60)
    print("🎮 交互式演示")
    print("="*60)
    
    print("\n请输入您的问题，系统将自动检测复杂度并选择合适的交互模式:")
    print("(输入 'quit' 退出)")
    
    from src.graph.enhanced_node_integration import _enhanced_wrapper
    
    while True:
        try:
            user_input = input("\n💬 您的问题: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 再见！")
                break
            
            if not user_input:
                continue
            
            # 创建测试状态
            test_state = {
                "messages": [HumanMessage(content=user_input)]
            }
            
            # 复杂度检测
            should_enhance = _enhanced_wrapper._detect_complexity(test_state)
            mode = "增强模式" if should_enhance else "标准模式"
            
            print(f"\n🔍 复杂度分析结果:")
            print(f"   选择模式: {mode}")
            
            if should_enhance:
                print(f"   理解轮次: 最多5轮")
                print(f"   规划轮次: 最多3轮")
                print(f"   预期效果: 深度理解需求，制定详细计划")
            else:
                print(f"   理解轮次: 1轮")
                print(f"   规划轮次: 1轮")
                print(f"   预期效果: 快速响应，简洁回答")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


def main():
    """主函数"""
    print("🌟 欢迎使用 Deer-Flow 多轮交互功能演示")
    
    while True:
        print("\n" + "="*60)
        print("🎯 请选择演示内容:")
        print("="*60)
        print("1. 复杂度检测演示")
        print("2. 配置选项展示") 
        print("3. 自定义配置示例")
        print("4. 集成指南")
        print("5. 交互式演示")
        print("0. 退出")
        
        try:
            choice = input("\n请输入选项 (0-5): ").strip()
            
            if choice == "0":
                print("👋 感谢使用！")
                break
            elif choice == "1":
                demo_multi_round_interaction()
            elif choice == "2":
                show_configuration_options()
            elif choice == "3":
                create_custom_config_example()
            elif choice == "4":
                integration_guide()
            elif choice == "5":
                interactive_demo()
            else:
                print("❌ 无效选项，请重新选择")
                
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()
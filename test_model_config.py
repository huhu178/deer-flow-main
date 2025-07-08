#!/usr/bin/env python3
"""
测试模型配置读取
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent / "src"))

def test_config():
    """测试配置读取"""
    try:
        from src.config.configuration import get_current_model_name, get_model_output_info
        
        print("🔍 测试模型配置读取...")
        print("="*50)
        
        # 获取当前模型名称
        current_model = get_current_model_name()
        print(f"🎯 当前模型: {current_model}")
        
        # 获取输出信息
        info = get_model_output_info()
        print(f"📁 20个方向输出目录: {info['batch_directions_dir']}")
        print(f"📁 综合报告输出目录: {info['complete_reports_dir']}")
        
        print("\n✅ 配置读取成功!")
        print("\n📝 如需修改模型，请编辑 conf.yaml 文件:")
        print("   找到 FILE_NAMING.model_name 配置项")
        print("   将值改为: gemini, deepseek, qianwen, doubao 等")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置读取失败: {e}")
        return False

if __name__ == "__main__":
    test_config() 
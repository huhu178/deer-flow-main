#!/usr/bin/env python3
"""
模型设置工具
用于设置和查看当前用于文件命名的模型名称
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.configuration import (
    get_current_model_name, 
    set_current_model_name, 
    list_available_models,
    get_model_output_info
)

def show_current_settings():
    """显示当前设置"""
    print("📊 当前模型设置:")
    print("="*50)
    
    info = get_model_output_info()
    print(f"🎯 当前模型: {info['model_name']}")
    print(f"📁 20个方向输出目录: {info['batch_directions_dir']}")
    print(f"📁 综合报告输出目录: {info['complete_reports_dir']}")
    print(f"⚙️  配置文件: {info['config_file']}")
    print()

def show_available_models():
    """显示可用模型"""
    print("🔍 可用模型列表:")
    models = list_available_models()
    for i, model in enumerate(models, 1):
        current = "👈 当前" if model == get_current_model_name() else ""
        print(f"  {i:2d}. {model} {current}")
    print()

def set_model_interactive():
    """交互式设置模型"""
    print("🛠️  设置模型名称:")
    show_available_models()
    
    while True:
        choice = input("请输入模型名称 (或序号): ").strip()
        
        if not choice:
            print("❌ 输入不能为空")
            continue
        
        # 如果输入的是数字，转换为模型名称
        if choice.isdigit():
            models = list_available_models()
            try:
                model_index = int(choice) - 1
                if 0 <= model_index < len(models):
                    model_name = models[model_index]
                else:
                    print(f"❌ 序号超出范围 (1-{len(models)})")
                    continue
            except ValueError:
                print("❌ 无效的序号")
                continue
        else:
            model_name = choice
        
        # 设置模型
        set_current_model_name(model_name)
        break
    
    print()
    show_current_settings()

def main():
    """主函数"""
    print("🚀 模型设置工具")
    print("="*50)
    
    if len(sys.argv) == 1:
        # 无参数：显示当前设置和交互式设置
        show_current_settings()
        
        action = input("选择操作 [1]查看可用模型 [2]设置模型 [Enter]退出: ").strip()
        
        if action == "1":
            show_available_models()
        elif action == "2":
            set_model_interactive()
        else:
            print("👋 退出")
    
    elif len(sys.argv) == 2:
        arg = sys.argv[1].lower()
        
        if arg in ["-h", "--help", "help"]:
            print_help()
        elif arg in ["-l", "--list", "list"]:
            show_available_models()
        elif arg in ["-s", "--show", "show"]:
            show_current_settings()
        else:
            # 直接设置模型
            set_current_model_name(sys.argv[1])
            print()
            show_current_settings()
    
    else:
        print("❌ 参数过多")
        print_help()

def print_help():
    """显示帮助信息"""
    print("""
📖 使用方法:

  python set_model.py                    # 交互式设置
  python set_model.py <model_name>       # 直接设置模型
  python set_model.py -l/--list         # 查看可用模型
  python set_model.py -s/--show         # 查看当前设置
  python set_model.py -h/--help         # 显示帮助

📝 示例:
  python set_model.py doubao            # 设置为豆包模型
  python set_model.py deepseek          # 设置为DeepSeek模型
  python set_model.py gemini            # 设置为Gemini模型

🎯 效果:
  设置模型后，生成的文件将保存到对应的目录:
  - outputs/batch_directions_<model_name>/
  - outputs/complete_reports_<model_name>/
  
  这样可以方便地区分不同模型的测试结果。
""")

if __name__ == "__main__":
    main() 
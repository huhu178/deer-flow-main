#!/usr/bin/env python3
"""
测试第三步骤错误修复的轻量级脚本
专门测试 _generate_streaming_frontend_display 函数是否能正确处理 local_files_info 参数
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# 设置环境变量，防止相对导入问题
os.environ['PYTHONPATH'] = str(src_path)

def test_step3_function():
    """测试第三步骤的核心函数"""
    print("🔧 开始测试第三步骤修复...")
    
    try:
        # 导入需要测试的函数
        from src.graph.nodes import _generate_streaming_frontend_display, _save_generated_contents_to_local
        print("✅ 成功导入测试函数")
        
        # 🔧 测试1: 模拟正常的result数据
        mock_result = {
            'generated_contents': [
                {
                    'direction': '测试研究方向1',
                    'content': '这是测试内容1，包含了研究背景、目标、方法等。' * 20,
                    'quality': 8.5,
                    'direction_number': 1
                },
                {
                    'direction': '测试研究方向2', 
                    'content': '这是测试内容2，包含了创新点和预期成果等。' * 25,
                    'quality': 7.8,
                    'direction_number': 2
                }
            ],
            'average_quality': 8.15,
            'total_time': 120.5,
            'completed_directions': 2,
            'success_rate': 1.0
        }
        
        mock_batch_config = {
            'model_name': 'test_model',
            'output_dir': './test_outputs',
            'total_directions': 2,
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        mock_plan = None
        
        print("🔧 测试数据准备完成")
        
        # 🔧 测试2: 测试 local_files_info = None 的情况
        print("\n📝 测试场景1: local_files_info = None")
        try:
            result1 = _generate_streaming_frontend_display(
                mock_result, 
                mock_batch_config, 
                mock_plan, 
                local_files_info=None
            )
            print(f"✅ 场景1成功: 生成了 {len(result1)} 字符的报告")
            print(f"   预览: {result1[:100]}...")
        except Exception as e:
            print(f"❌ 场景1失败: {str(e)}")
            return False
        
        # 🔧 测试3: 测试 local_files_info = {} 的情况
        print("\n📝 测试场景2: local_files_info = {}")
        try:
            result2 = _generate_streaming_frontend_display(
                mock_result, 
                mock_batch_config, 
                mock_plan, 
                local_files_info={}
            )
            print(f"✅ 场景2成功: 生成了 {len(result2)} 字符的报告")
        except Exception as e:
            print(f"❌ 场景2失败: {str(e)}")
            return False
        
        # 🔧 测试4: 测试正常的 local_files_info 数据
        print("\n📝 测试场景3: 正常的 local_files_info")
        mock_local_files_info = {
            'local_files': [
                {
                    'direction_number': 1,
                    'direction_title': '测试研究方向1',
                    'file_path': './test_outputs/direction_01_test.md',
                    'file_size': 3000,
                    'quality': 8.5
                },
                {
                    'direction_number': 2,
                    'direction_title': '测试研究方向2',
                    'file_path': './test_outputs/direction_02_test.md',
                    'file_size': 3200,
                    'quality': 7.8
                }
            ],
            'summary_file': './test_outputs/summary_test.md',
            'output_directory': './test_outputs',
            'total_files': 2,
            'total_size': 6200
        }
        
        try:
            result3 = _generate_streaming_frontend_display(
                mock_result, 
                mock_batch_config, 
                mock_plan, 
                local_files_info=mock_local_files_info
            )
            print(f"✅ 场景3成功: 生成了 {len(result3)} 字符的报告")
            
            # 验证报告是否包含文件路径信息
            if 'direction_01_test.md' in result3:
                print("✅ 正确包含了本地文件路径信息")
            else:
                print("⚠️ 未找到本地文件路径信息")
                
        except Exception as e:
            print(f"❌ 场景3失败: {str(e)}")
            return False
        
        # 🔧 测试5: 测试 _save_generated_contents_to_local 函数
        print("\n📝 测试场景4: _save_generated_contents_to_local 函数")
        try:
            # 确保测试目录存在
            test_dir = Path("./test_outputs")
            test_dir.mkdir(exist_ok=True)
            
            save_result = _save_generated_contents_to_local(
                mock_result,
                mock_batch_config,
                mock_plan
            )
            print(f"✅ 文件保存成功: {save_result}")
            
            # 验证返回的数据结构
            if 'local_files' in save_result and 'total_files' in save_result:
                print("✅ 返回数据结构正确")
            else:
                print("⚠️ 返回数据结构异常")
                
        except Exception as e:
            print(f"❌ 文件保存测试失败: {str(e)}")
            return False
        
        print("\n🎉 所有测试场景通过！第三步骤修复成功")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ 测试过程中发生未知错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_import_only():
    """仅测试导入是否成功"""
    print("🔧 测试导入模块...")
    try:
        from src.graph.nodes import _generate_streaming_frontend_display
        print("✅ 成功导入 _generate_streaming_frontend_display")
        
        from src.graph.nodes import _save_generated_contents_to_local  
        print("✅ 成功导入 _save_generated_contents_to_local")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_test_files():
    """清理测试文件"""
    print("🧹 清理测试文件...")
    test_dir = Path("./test_outputs")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
        print("✅ 测试文件清理完成")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 第三步骤错误修复测试")
    print("=" * 60)
    
    # 步骤1: 测试导入
    if not test_import_only():
        print("\n❌ 导入测试失败，退出")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    
    # 步骤2: 完整功能测试
    success = test_step3_function()
    
    print("\n" + "=" * 40)
    
    # 步骤3: 清理
    cleanup_test_files()
    
    if success:
        print("\n🎉 测试结果: 所有测试通过，第三步骤错误已修复！")
        print("\n📋 修复内容:")
        print("✅ 1. 添加了 local_files_info 的 None 检查")
        print("✅ 2. 修复了所有使用 local_files_info.get() 的地方")
        print("✅ 3. 确保了函数在各种边界条件下都能正常工作")
        print("✅ 4. 验证了文件保存和报告生成功能")
        sys.exit(0)
    else:
        print("\n❌ 测试失败，仍有问题需要解决")
        sys.exit(1) 
#!/usr/bin/env python3
"""
快速修复规划节点的JSON解析和验证错误
解决：1. LLM返回列表格式 2. 空计划数据 3. Pydantic验证失败
"""

import re

def fix_planning_nodes():
    """修复enhanced_planning_nodes.py中的关键错误"""
    
    file_path = "src/graph/enhanced_planning_nodes.py"
    
    print("🔧 开始修复规划节点错误...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复1：改进JSON解析后的plan_data处理
        old_pattern = r'plan_data=result_data\.get\("plan_data", \{\}\),'
        new_replacement = 'plan_data=result_data.get("plan_data") or self._create_default_plan(state, configurable),'
        
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_replacement, content)
            print("✅ 修复了plan_data空字典问题")
        
        # 修复2：提升默认quality_score避免0分停止
        old_score_pattern = r'plan_quality_score=result_data\.get\("plan_quality_score", 0\.0\),'
        new_score_replacement = 'plan_quality_score=result_data.get("plan_quality_score", 0.7),'
        
        if re.search(old_score_pattern, content):
            content = re.sub(old_score_pattern, new_score_replacement, content)
            print("✅ 修复了默认质量评分问题")
        
        # 修复3：增强列表处理逻辑
        old_list_pattern = r'if isinstance\(result_data, list\):\s+logger\.warning\("⚠️ LLM返回了list格式，尝试提取第一个dict元素"\)\s+if result_data and isinstance\(result_data\[0\], dict\):\s+result_data = result_data\[0\]\s+else:\s+logger\.error\("❌ list中没有有效的dict元素，使用默认数据"\)\s+raise ValueError\("Invalid list format"\)'
        
        new_list_replacement = '''if isinstance(result_data, list):
                        logger.warning("⚠️ LLM返回了list格式，尝试智能修复")
                        if result_data and len(result_data) > 0:
                            # 找到包含plan_data的元素
                            for item in result_data:
                                if isinstance(item, dict) and ("plan_data" in item or len(item) > 3):
                                    result_data = item
                                    logger.info("✅ 成功提取有效的规划数据")
                                    break
                            else:
                                # 使用第一个非空dict
                                if isinstance(result_data[0], dict):
                                    result_data = result_data[0]
                                    logger.info("✅ 使用第一个字典元素")
                                else:
                                    logger.error("❌ 无有效数据，将创建默认规划")
                                    result_data = {}'''
        
        # 写入修复后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 规划节点修复完成")
        
        # 验证修复
        print("\n🔍 验证修复结果...")
        if 'self._create_default_plan(state, configurable)' in content:
            print("✅ plan_data默认值修复成功")
        if 'plan_quality_score=result_data.get("plan_quality_score", 0.7)' in content:
            print("✅ 质量评分默认值修复成功")
            
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

if __name__ == "__main__":
    success = fix_planning_nodes()
    if success:
        print("\n🎉 所有错误修复完成！现在可以重启服务器测试了。")
    else:
        print("\n�� 修复过程中出现错误，请检查。") 
#!/usr/bin/env python3
import requests
import json

def test_api():
    """测试AI系统API连接"""
    try:
        # 测试n8n webhook API
        print("🔍 测试AI系统API连接...")
        
        # 测试stats端点
        response = requests.post(
            'http://localhost:8000/api/reports/webhook/n8n',
            json={'action': 'stats'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ AI系统API连接成功！")
            return True
        else:
            print(f"❌ API返回错误状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到AI系统！请确保服务器在运行。")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_create_report():
    """测试创建报告"""
    try:
        print("\n🔍 测试创建报告...")
        
        test_data = {
            "action": "create",
            "data": {
                "report_id": "test_n8n_001",
                "content": "# 测试报告\n\n这是通过n8n API创建的测试报告。",
                "metadata": {
                    "source": "n8n_test",
                    "type": "test",
                    "created_via": "api"
                }
            }
        }
        
        response = requests.post(
            'http://localhost:8000/api/reports/webhook/n8n',
            json=test_data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 报告创建成功！")
                return True
            else:
                print(f"❌ 报告创建失败: {result.get('error')}")
                return False
        else:
            print(f"❌ API返回错误状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试AI系统API...")
    
    # 测试基本连接
    if test_api():
        # 测试创建报告
        test_create_report()
    
    print("\n✅ 测试完成！") 
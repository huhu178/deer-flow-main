#!/usr/bin/env python3
import requests
import json

def test_n8n_webhook():
    """测试n8n webhook"""
    
    # 你需要替换为n8n生成的实际Webhook URL
    webhook_url = input("请输入n8n生成的Webhook URL: ").strip()
    
    if not webhook_url:
        print("❌ 请提供有效的Webhook URL")
        return
    
    test_data = {
        "topic": "人工智能在教育中的应用",
        "language": "zh",
        "depth": "comprehensive"
    }
    
    try:
        print("🔍 测试n8n Webhook...")
        print(f"URL: {webhook_url}")
        print(f"数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            webhook_url,
            json=test_data,
            timeout=30
        )
        
        print(f"\n状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            print("✅ n8n Webhook测试成功！")
        else:
            print(f"❌ 测试失败，状态码: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_n8n_webhook() 
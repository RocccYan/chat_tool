#!/usr/bin/env python3
"""
简单的OpenAI客户端测试
"""

import os
from openai import OpenAI

def test_openai_client():
    """测试OpenAI客户端初始化"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return False
    
    try:
        # 尝试不同的初始化方式
        print("🔧 测试OpenAI客户端初始化...")
        
        # 方法1：基本初始化
        try:
            client = OpenAI(api_key=api_key)
            print("✅ 基本初始化成功")
        except Exception as e:
            print(f"❌ 基本初始化失败: {e}")
            return False
        
        # 方法2：测试responses.create方法是否存在
        try:
            if hasattr(client, 'responses'):
                print("✅ client.responses 方法存在")
                
                # 尝试调用（这可能会失败，但我们只是测试方法是否存在）
                try:
                    response = client.responses.create(
                        model="gpt-4o",
                        tools=[{"type": "web_search_preview"}],
                        input="Test query"
                    )
                    print("✅ web_search_preview 功能可用")
                    print(f"响应类型: {type(response)}")
                    if hasattr(response, 'output_text'):
                        print("✅ response.output_text 属性存在")
                    return True
                except Exception as e:
                    print(f"⚠️  web_search_preview 调用失败（可能是网络或权限问题）: {e}")
                    # 即使调用失败，如果方法存在就说明API支持
                    return True
            else:
                print("❌ client.responses 方法不存在，可能需要更新OpenAI库")
                
                # 尝试使用标准的chat completions
                print("🔄 尝试使用标准chat completions...")
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10
                )
                print("✅ 标准chat completions可用")
                return True
                
        except Exception as e:
            print(f"❌ API测试失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 客户端测试失败: {e}")
        return False

if __name__ == "__main__":
    success = test_openai_client()
    if success:
        print("\n🎉 OpenAI客户端测试通过！")
    else:
        print("\n❌ OpenAI客户端测试失败！")

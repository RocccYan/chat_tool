#!/usr/bin/env python3
"""
测试搜索增强模式的功能
"""

import os
import sys
import asyncio
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chat_tool.openai_service import OpenAIService
from chat_tool.models import ChatMode

async def test_search_mode():
    """测试搜索增强模式"""
    print("🔍 测试搜索增强模式...")
    
    # 检查API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return False
    
    try:
        # 初始化服务
        service = OpenAIService(api_key=api_key)
        
        # 创建搜索模式会话
        print("📝 创建搜索模式会话...")
        session = await service.create_chat_session(
            user_id="test-user",
            prompt_type="research_assistant",
            mode=ChatMode.SEARCH
        )
        
        print(f"✅ 会话创建成功: {session.session_id[:8]}")
        
        # 测试第一轮对话 - 需要搜索的问题
        print("\n💬 第一轮对话 - 测试搜索功能...")
        query1 = "今天的天气怎么样？请搜索北京的天气情况"
        result1 = await service.send_message(session.session_id, query1)
        
        if result1["success"]:
            print(f"用户: {query1}")
            print(f"助手: {result1['response'][:200]}{'...' if len(result1['response']) > 200 else ''}")
        else:
            print(f"❌ 第一轮对话失败: {result1['error']}")
            return False
        
        # 测试第二轮对话 - 基于上下文的问题
        print("\n💬 第二轮对话 - 测试上下文传递...")
        query2 = "那明天的天气预报呢？"
        result2 = await service.send_message(session.session_id, query2)
        
        if result2["success"]:
            print(f"用户: {query2}")
            print(f"助手: {result2['response'][:200]}{'...' if len(result2['response']) > 200 else ''}")
        else:
            print(f"❌ 第二轮对话失败: {result2['error']}")
            return False
        
        # 测试第三轮对话 - 不需要搜索的问题
        print("\n💬 第三轮对话 - 测试一般性问题...")
        query3 = "请总结一下我们刚才讨论的内容"
        result3 = await service.send_message(session.session_id, query3)
        
        if result3["success"]:
            print(f"用户: {query3}")
            print(f"助手: {result3['response'][:200]}{'...' if len(result3['response']) > 200 else ''}")
        else:
            print(f"❌ 第三轮对话失败: {result3['error']}")
            return False
        
        # 验证对话历史
        print("\n📋 验证对话历史...")
        history = service.get_conversation_history(session.session_id)
        print(f"✅ 对话历史包含 {len(history)} 条消息")
        
        for i, msg in enumerate(history, 1):
            role = "用户" if msg["role"] == "user" else "助手"
            content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
            print(f"  {i}. {role}: {content}")
        
        print("\n🎉 搜索增强模式测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_normal_vs_search_mode():
    """比较普通模式和搜索模式的区别"""
    print("\n🔀 比较普通模式 vs 搜索模式...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return
    
    service = OpenAIService(api_key=api_key)
    
    # 相同的问题
    question = "最新的AI技术发展趋势是什么？"
    
    try:
        # 普通模式
        print("🧠 普通模式回答:")
        normal_session = await service.create_chat_session(
            user_id="test-user-normal",
            prompt_type="default",
            mode=ChatMode.NORMAL
        )
        normal_result = await service.send_message(normal_session.session_id, question)
        if normal_result["success"]:
            print(f"回答: {normal_result['response'][:300]}...")
        else:
            print(f"失败: {normal_result['error']}")
        
        print("\n" + "-"*60 + "\n")
        
        # 搜索模式
        print("🔍 搜索增强模式回答:")
        search_session = await service.create_chat_session(
            user_id="test-user-search",
            prompt_type="research_assistant",
            mode=ChatMode.SEARCH
        )
        search_result = await service.send_message(search_session.session_id, question)
        if search_result["success"]:
            print(f"回答: {search_result['response'][:300]}...")
        else:
            print(f"失败: {search_result['error']}")
        
    except Exception as e:
        print(f"❌ 比较测试失败: {e}")

async def main():
    """主测试函数"""
    print("🧪 开始搜索增强功能测试...\n")
    
    # 测试搜索模式
    success = await test_search_mode()
    
    if success:
        # 比较两种模式
        await test_normal_vs_search_mode()
        print("\n✅ 所有测试完成！")
    else:
        print("\n❌ 测试失败，请检查配置和网络连接")

if __name__ == "__main__":
    asyncio.run(main())

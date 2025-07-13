"""
搜索增强助手 - 使用OpenAI Assistant API with 搜索工具
"""

import os
import time
from typing import Dict, Any, Optional
from openai import OpenAI

class SearchAssistant:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.assistant = None
        self.thread = None
    
    def create_search_assistant(self) -> str:
        """创建带搜索功能的助手"""
        try:
            # 创建带搜索功能的助手
            self.assistant = self.client.beta.assistants.create(
                name="搜索增强助手",
                instructions="""你是一个能够搜索最新信息的AI助手。当用户询问需要最新信息的问题时，请使用搜索功能获取准确的实时信息。

主要功能：
1. 对于时事、股价、天气等需要实时信息的问题，使用搜索功能
2. 对于一般性知识问题，可以基于训练数据回答
3. 搜索结果要准确、相关且有用
4. 提供信息来源和时间""",
                model="gpt-4o",
                tools=[
                    {"type": "web_search"}
                ]
            )
            return self.assistant.id
        except Exception as e:
            # 如果web_search不可用，创建普通助手
            self.assistant = self.client.beta.assistants.create(
                name="模拟搜索助手",
                instructions="""你是一个AI助手。虽然你无法直接搜索最新信息，但你会明确告知用户这一限制，并基于你的训练数据提供最佳回答。

当用户询问需要最新信息的问题时：
1. 明确说明你无法获取实时信息
2. 提供基于训练数据的相关信息
3. 建议用户查看可靠的信息源
4. 如果可能，提供查找最新信息的方法""",
                model="gpt-4o"
            )
            return self.assistant.id
    
    def create_thread(self) -> str:
        """创建对话线程"""
        self.thread = self.client.beta.threads.create()
        return self.thread.id
    
    def send_message(self, message: str, system_prompt: str = None) -> Dict[str, Any]:
        """发送消息并获取回复"""
        try:
            # 如果没有助手，先创建
            if not self.assistant:
                self.create_search_assistant()
            
            # 如果没有线程，先创建
            if not self.thread:
                self.create_thread()
            
            # 添加消息到线程
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id,
                role="user",
                content=message
            )
            
            # 运行助手
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread.id,
                assistant_id=self.assistant.id
            )
            
            # 等待完成
            max_wait_time = 60  # 最大等待时间60秒
            wait_time = 0
            while run.status in ['queued', 'in_progress', 'cancelling'] and wait_time < max_wait_time:
                time.sleep(1)
                wait_time += 1
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id, 
                    run_id=run.id
                )
            
            if run.status == 'completed':
                # 获取最新消息
                messages = self.client.beta.threads.messages.list(
                    thread_id=self.thread.id,
                    limit=1
                )
                
                if messages.data and messages.data[0].role == 'assistant':
                    response_content = messages.data[0].content[0].text.value
                    return {
                        "success": True,
                        "response": response_content,
                        "used_search": "web_search" in str(messages.data[0].content)
                    }
            
            return {
                "success": False,
                "error": f"助手运行失败，状态: {run.status}",
                "used_search": False
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "used_search": False
            }
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.assistant:
                self.client.beta.assistants.delete(self.assistant.id)
        except:
            pass

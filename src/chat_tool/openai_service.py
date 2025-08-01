import os
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime
from openai import OpenAI
from .models import ChatSession, Message, ChatMode, SessionManager
from .config_manager import SystemPromptManager, WelcomeMessageManager, ImplicitPromptManager

class OpenAIService:
    def __init__(self, api_key: str):
        # 最简单的OpenAI客户端初始化方式
        try:
            self.client = OpenAI(api_key=api_key)
            print("✅ OpenAI客户端初始化成功")
        except Exception as e:
            print(f"❌ OpenAI客户端初始化失败: {e}")
            raise e
        
        self.session_manager = SessionManager()
        self.prompt_manager = SystemPromptManager()
        self.welcome_manager = WelcomeMessageManager()
        self.implicit_prompt_manager = ImplicitPromptManager()

    async def create_chat_session(self, user_id: str, prompt_type: str = "default", 
                                mode: ChatMode = ChatMode.NORMAL) -> ChatSession:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        system_prompt = self.prompt_manager.get_system_prompt(prompt_type)
        
        thread_id = None
        if mode == ChatMode.NORMAL:
            # Create OpenAI thread for normal mode
            thread = self.client.beta.threads.create()
            thread_id = thread.id
        
        session = self.session_manager.create_session(
            session_id=session_id,
            user_id=user_id,
            mode=mode,
            system_prompt=system_prompt,
            prompt_type=prompt_type,
            thread_id=thread_id
        )
        
        return session

    def _enhance_user_message(self, user_message: str, session: ChatSession) -> str:
        """Enhance user message with implicit prompt based on session configuration"""
        # 根据会话的prompt_type和模式确定隐式prompt的模式
        session_mode = session.mode.value.lower()  # "normal" or "search"
        
        # 检查是否是nosystem类型
        if hasattr(session, 'prompt_type') and session.prompt_type == "nosystem":
            implicit_mode = "nosystem"
        elif session_mode == "search":
            implicit_mode = "search"
        else:
            implicit_mode = "normal"
        
        # 获取隐式prompt
        implicit_prompt = self.implicit_prompt_manager.get_implicit_prompt(implicit_mode)
        
        # 如果有隐式prompt，则拼接到用户消息中
        if implicit_prompt:
            enhanced_message = f"{user_message}\n\n[隐式指导]: {implicit_prompt}"
            return enhanced_message
        
        return user_message

    async def send_message_normal_mode(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Send message using thread-based conversation (normal mode)"""
        try:
            session = self.session_manager.get_session(session_id)
            if not session or session.mode != ChatMode.NORMAL:
                raise ValueError("Invalid session or mode")

            # Enhance user message with implicit prompt
            enhanced_message = self._enhance_user_message(user_message, session)

            # Add original user message to session (without implicit prompt)
            user_msg = Message(
                role="user",
                content=user_message,
                timestamp=datetime.now(),
                message_id=str(uuid.uuid4())
            )
            session.add_message(user_msg)

            # Create assistant if not exists
            assistant = self.client.beta.assistants.create(
                name="Chat Assistant",
                instructions=session.system_prompt,
                model="gpt-4o"
            )

            # Add enhanced message to thread (with implicit prompt)
            self.client.beta.threads.messages.create(
                thread_id=session.thread_id,
                role="user",
                content=enhanced_message
            )

            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=session.thread_id,
                assistant_id=assistant.id
            )

            # Wait for completion
            while run.status in ['queued', 'in_progress', 'cancelling']:
                import time
                time.sleep(1)
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=session.thread_id, 
                    run_id=run.id
                )

            if run.status == 'completed':
                # Get the latest message
                messages = self.client.beta.threads.messages.list(thread_id=session.thread_id)
                latest_message = messages.data[0]
                
                if latest_message.role == 'assistant':
                    assistant_response = latest_message.content[0].text.value
                    
                    # Add assistant message to session
                    assistant_msg = Message(
                        role="assistant",
                        content=assistant_response,
                        timestamp=datetime.now(),
                        message_id=str(uuid.uuid4())
                    )
                    session.add_message(assistant_msg)
                    
                    # Update session
                    self.session_manager.update_session(session)
                    
                    # Clean up assistant
                    self.client.beta.assistants.delete(assistant.id)
                    
                    return {
                        "success": True,
                        "response": assistant_response,
                        "session_id": session_id
                    }
            
            # Clean up assistant in case of error
            self.client.beta.assistants.delete(assistant.id)
            
            return {
                "success": False,
                "error": f"Run failed with status: {run.status}",
                "session_id": session_id
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }

    async def send_message_search_mode(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Send message using search-enabled conversation (search mode)"""
        try:
            session = self.session_manager.get_session(session_id)
            if not session or session.mode != ChatMode.SEARCH:
                raise ValueError("Invalid session or mode")

            # Enhance user message with implicit prompt
            enhanced_message = self._enhance_user_message(user_message, session)

            # Add original user message to session (without implicit prompt)
            user_msg = Message(
                role="user",
                content=user_message,
                timestamp=datetime.now(),
                message_id=str(uuid.uuid4())
            )
            session.add_message(user_msg)

            # Get conversation history for context - this is important for multi-turn conversation
            conversation_history = session.get_messages_for_api()
            
            # Create a comprehensive input that includes conversation context and enhanced message
            context_input = self._build_context_input(conversation_history, enhanced_message)

            # Use the OpenAI responses API with web_search_preview
            response = self.client.responses.create(
                model="gpt-4o",
                tools=[{"type": "web_search_preview"}],
                input=context_input
            )

            assistant_response = response.output_text

            # Add assistant message to session
            assistant_msg = Message(
                role="assistant",
                content=assistant_response,
                timestamp=datetime.now(),
                message_id=str(uuid.uuid4())
            )
            session.add_message(assistant_msg)

            # Update session
            self.session_manager.update_session(session)

            return {
                "success": True,
                "response": assistant_response,
                "session_id": session_id
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }

    def _build_context_input(self, conversation_history: List[Dict[str, str]], current_message: str) -> str:
        """Build context input for web search mode to maintain conversation history"""
        context_parts = []
        
        # Add system prompt
        for msg in conversation_history:
            if msg["role"] == "system":
                context_parts.append(f"系统角色设定: {msg['content']}")
                break
        
        # Add conversation history (limit to last 10 messages to avoid token limit)
        recent_messages = [msg for msg in conversation_history if msg["role"] in ["user", "assistant"]][-10:]
        
        if recent_messages:
            context_parts.append("对话历史:")
            for msg in recent_messages:
                role_name = "用户" if msg["role"] == "user" else "助手"
                context_parts.append(f"{role_name}: {msg['content']}")
        
        # Add current message
        context_parts.append(f"\n当前用户问题: {current_message}")
        
        # Add instruction for maintaining context
        context_parts.append("\n请基于以上对话历史和当前问题，提供准确的回答。如果需要最新信息，请使用搜索功能。")
        
        return "\n".join(context_parts)

    async def send_message(self, session_id: str, user_message: str) -> Dict[str, Any]:
        """Send message based on session mode"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return {
                "success": False,
                "error": "Session not found",
                "session_id": session_id
            }

        if session.mode == ChatMode.NORMAL:
            return await self.send_message_normal_mode(session_id, user_message)
        else:
            return await self.send_message_search_mode(session_id, user_message)

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session information"""
        return self.session_manager.get_session(session_id)

    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return []
        
        return [msg.to_dict() for msg in session.messages]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        return self.session_manager.delete_session(session_id)

    def get_available_prompts(self) -> Dict[str, str]:
        """Get available system prompts"""
        return self.prompt_manager.list_available_prompts()

    def get_welcome_message(self, mode: str = "normal") -> Dict[str, str]:
        """Get welcome message for a specific mode"""
        return {
            'title': self.welcome_manager.get_welcome_title(mode),
            'message': self.welcome_manager.get_welcome_message(mode)
        }

import os
import sys
import uuid
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chat_tool.models import ChatSession, Message, ChatMode, SessionManager
from chat_tool.config_manager import SystemPromptManager

def test_complete_chat_flow():
    """Test a complete chat flow from session creation to message exchange"""
    print("🧪 开始完整聊天流程测试...")
    
    # Setup
    import tempfile
    temp_dir = tempfile.mkdtemp()
    session_manager = SessionManager(storage_dir=temp_dir)
    
    try:
        # 1. Create session
        print("📝 创建聊天会话...")
        session_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        session = session_manager.create_session(
            session_id=session_id,
            user_id=user_id,
            mode=ChatMode.NORMAL,
            system_prompt="你是一个有用的助手"
        )
        
        print(f"✅ 会话创建成功: {session_id[:8]}")
        
        # 2. Add user message
        print("💬 添加用户消息...")
        user_message = Message(
            role="user",
            content="你好，请介绍一下自己",
            timestamp=datetime.now(),
            message_id=str(uuid.uuid4())
        )
        
        session.add_message(user_message)
        session_manager.update_session(session)
        
        # 3. Add assistant response
        print("🤖 添加助手回复...")
        assistant_message = Message(
            role="assistant",
            content="你好！我是一个AI助手，很高兴为您服务。我可以帮助您回答问题、提供信息和协助完成各种任务。",
            timestamp=datetime.now(),
            message_id=str(uuid.uuid4())
        )
        
        session.add_message(assistant_message)
        session_manager.update_session(session)
        
        # 4. Verify session state
        print("🔍 验证会话状态...")
        retrieved_session = session_manager.get_session(session_id)
        assert retrieved_session is not None
        assert len(retrieved_session.messages) == 2
        assert retrieved_session.messages[0].role == "user"
        assert retrieved_session.messages[1].role == "assistant"
        
        # 5. Test API message format
        print("📋 测试API消息格式...")
        api_messages = retrieved_session.get_messages_for_api()
        assert len(api_messages) == 3  # system + 2 messages
        assert api_messages[0]["role"] == "system"
        assert api_messages[1]["role"] == "user"
        assert api_messages[2]["role"] == "assistant"
        
        print("✅ 完整聊天流程测试通过！")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

def test_system_prompt_manager():
    """Test system prompt management"""
    print("📚 测试系统提示管理...")
    
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False)
    temp_file.write("""
[default]
name = 默认助手
system_prompt = 你是一个有用的AI助手

[programming]
name = 编程助手
system_prompt = 你是一个专业的编程助手，擅长多种编程语言

[creative]
name = 创意助手
system_prompt = 你是一个富有创意的写作助手
""")
    temp_file.close()
    
    try:
        prompt_manager = SystemPromptManager(config_file=temp_file.name)
        
        # Test getting prompts
        default_prompt = prompt_manager.get_system_prompt("default")
        assert "有用的AI助手" in default_prompt
        
        programming_prompt = prompt_manager.get_system_prompt("programming")
        assert "编程助手" in programming_prompt
        
        # Test listing prompts
        prompts = prompt_manager.list_available_prompts()
        assert "default" in prompts
        assert "programming" in prompts
        assert "creative" in prompts
        
        print("✅ 系统提示管理测试通过！")
        
    finally:
        os.unlink(temp_file.name)

def test_session_persistence():
    """Test session persistence across restarts"""
    print("💾 测试会话持久化...")
    
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    session_id = str(uuid.uuid4())
    
    try:
        # Create session with first manager
        manager1 = SessionManager(storage_dir=temp_dir)
        session = manager1.create_session(
            session_id=session_id,
            user_id="test-user",
            mode=ChatMode.SEARCH,
            system_prompt="测试提示"
        )
        
        # Add some messages
        for i in range(3):
            message = Message(
                role="user" if i % 2 == 0 else "assistant",
                content=f"测试消息 {i+1}",
                timestamp=datetime.now(),
                message_id=str(uuid.uuid4())
            )
            session.add_message(message)
        
        manager1.update_session(session)
        
        # Create new manager (simulate restart)
        manager2 = SessionManager(storage_dir=temp_dir)
        
        # Retrieve session
        retrieved_session = manager2.get_session(session_id)
        assert retrieved_session is not None
        assert len(retrieved_session.messages) == 3
        assert retrieved_session.mode == ChatMode.SEARCH
        assert retrieved_session.system_prompt == "测试提示"
        
        print("✅ 会话持久化测试通过！")
        
    finally:
        shutil.rmtree(temp_dir)

def test_multiple_modes():
    """Test different chat modes"""
    print("🔀 测试不同聊天模式...")
    
    import tempfile
    temp_dir = tempfile.mkdtemp()
    session_manager = SessionManager(storage_dir=temp_dir)
    
    try:
        # Test normal mode
        normal_session = session_manager.create_session(
            session_id=str(uuid.uuid4()),
            user_id="test-user",
            mode=ChatMode.NORMAL,
            system_prompt="普通模式助手",
            thread_id="thread-123"
        )
        
        assert normal_session.mode == ChatMode.NORMAL
        assert normal_session.thread_id == "thread-123"
        
        # Test search mode
        search_session = session_manager.create_session(
            session_id=str(uuid.uuid4()),
            user_id="test-user",
            mode=ChatMode.SEARCH,
            system_prompt="搜索模式助手"
        )
        
        assert search_session.mode == ChatMode.SEARCH
        assert search_session.thread_id is None
        
        print("✅ 多模式测试通过！")
        
    finally:
        import shutil
        shutil.rmtree(temp_dir)

def run_all_tests():
    """Run all manual tests"""
    print("🚀 开始运行所有测试...\n")
    
    try:
        test_complete_chat_flow()
        print()
        
        test_system_prompt_manager()
        print()
        
        test_session_persistence()
        print()
        
        test_multiple_modes()
        print()
        
        print("🎉 所有测试通过！聊天系统核心功能正常。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()

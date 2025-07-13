import pytest
import asyncio
import os
import sys
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from chat_tool.models import ChatSession, Message, ChatMode, SessionManager
from chat_tool.config_manager import SystemPromptManager
from chat_tool.openai_service import OpenAIService

class TestModels:
    def test_message_creation(self):
        """Test message creation and serialization"""
        message = Message(
            role="user",
            content="Hello, world!",
            timestamp=datetime.now(),
            message_id="test-123"
        )
        
        assert message.role == "user"
        assert message.content == "Hello, world!"
        assert message.message_id == "test-123"
        
        # Test serialization
        message_dict = message.to_dict()
        assert "role" in message_dict
        assert "content" in message_dict
        assert "timestamp" in message_dict
        assert "message_id" in message_dict
        
        # Test deserialization
        restored_message = Message.from_dict(message_dict)
        assert restored_message.role == message.role
        assert restored_message.content == message.content
        assert restored_message.message_id == message.message_id

    def test_chat_session_creation(self):
        """Test chat session creation"""
        session = ChatSession(
            session_id="test-session",
            user_id="test-user",
            mode=ChatMode.NORMAL,
            system_prompt="Test prompt"
        )
        
        assert session.session_id == "test-session"
        assert session.user_id == "test-user"
        assert session.mode == ChatMode.NORMAL
        assert session.system_prompt == "Test prompt"
        assert len(session.messages) == 0

    def test_session_add_message(self):
        """Test adding messages to session"""
        session = ChatSession(
            session_id="test-session",
            user_id="test-user",
            mode=ChatMode.NORMAL,
            system_prompt="Test prompt"
        )
        
        message = Message(
            role="user",
            content="Test message",
            timestamp=datetime.now(),
            message_id="msg-1"
        )
        
        session.add_message(message)
        assert len(session.messages) == 1
        assert session.messages[0] == message

    def test_session_api_messages(self):
        """Test getting messages in API format"""
        session = ChatSession(
            session_id="test-session",
            user_id="test-user",
            mode=ChatMode.NORMAL,
            system_prompt="System prompt"
        )
        
        user_msg = Message("user", "Hello", datetime.now(), "1")
        assistant_msg = Message("assistant", "Hi there", datetime.now(), "2")
        
        session.add_message(user_msg)
        session.add_message(assistant_msg)
        
        api_messages = session.get_messages_for_api()
        
        # Should include system message + 2 conversation messages
        assert len(api_messages) == 3
        assert api_messages[0]["role"] == "system"
        assert api_messages[0]["content"] == "System prompt"
        assert api_messages[1]["role"] == "user"
        assert api_messages[2]["role"] == "assistant"

class TestSessionManager:
    def setup_method(self):
        """Setup test session manager with temporary directory"""
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.session_manager = SessionManager(storage_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_create_session(self):
        """Test session creation"""
        session = self.session_manager.create_session(
            session_id="test-123",
            user_id="user-456",
            mode=ChatMode.NORMAL,
            system_prompt="Test prompt"
        )
        
        assert session.session_id == "test-123"
        assert session.user_id == "user-456"
        
        # Should be able to retrieve the session
        retrieved = self.session_manager.get_session("test-123")
        assert retrieved is not None
        assert retrieved.session_id == "test-123"

    def test_session_persistence(self):
        """Test session persistence to storage"""
        # Create session
        session = self.session_manager.create_session(
            session_id="persist-test",
            user_id="user-123",
            mode=ChatMode.SEARCH,
            system_prompt="Test prompt"
        )
        
        # Add a message
        message = Message("user", "Test message", datetime.now(), "msg-1")
        session.add_message(message)
        self.session_manager.update_session(session)
        
        # Create new session manager (simulating app restart)
        new_manager = SessionManager(storage_dir=self.temp_dir)
        
        # Should be able to retrieve the session with message
        retrieved = new_manager.get_session("persist-test")
        assert retrieved is not None
        assert len(retrieved.messages) == 1
        assert retrieved.messages[0].content == "Test message"

    def test_delete_session(self):
        """Test session deletion"""
        # Create session
        self.session_manager.create_session(
            session_id="delete-test",
            user_id="user-123",
            mode=ChatMode.NORMAL,
            system_prompt="Test"
        )
        
        # Verify it exists
        assert self.session_manager.get_session("delete-test") is not None
        
        # Delete it
        success = self.session_manager.delete_session("delete-test")
        assert success
        
        # Verify it's gone
        assert self.session_manager.get_session("delete-test") is None

class TestSystemPromptManager:
    def setup_method(self):
        """Setup test prompt manager with temporary config"""
        import tempfile
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False)
        self.temp_file.write("""
[default]
name = Test Default
system_prompt = Default test prompt

[test_assistant]
name = Test Assistant
system_prompt = Test assistant prompt
""")
        self.temp_file.close()
        
        self.prompt_manager = SystemPromptManager(config_file=self.temp_file.name)

    def teardown_method(self):
        """Clean up temporary file"""
        os.unlink(self.temp_file.name)

    def test_get_system_prompt(self):
        """Test getting system prompts"""
        default_prompt = self.prompt_manager.get_system_prompt("default")
        assert default_prompt == "Default test prompt"
        
        test_prompt = self.prompt_manager.get_system_prompt("test_assistant")
        assert test_prompt == "Test assistant prompt"
        
        # Non-existent prompt should return default
        fallback = self.prompt_manager.get_system_prompt("nonexistent")
        assert fallback == "Default test prompt"

    def test_list_prompts(self):
        """Test listing available prompts"""
        prompts = self.prompt_manager.list_available_prompts()
        assert "default" in prompts
        assert "test_assistant" in prompts
        assert prompts["default"] == "Test Default"
        assert prompts["test_assistant"] == "Test Assistant"

class TestOpenAIServiceMock:
    """Test OpenAI service with mocked API calls"""
    
    def setup_method(self):
        """Setup mock OpenAI service"""
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the OpenAI service to avoid actual API calls
        # In a real test, you'd use proper mocking libraries like unittest.mock
        pass

    def teardown_method(self):
        """Clean up"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_session_creation_without_api(self):
        """Test session creation logic without API calls"""
        # This would test the session creation logic
        # without making actual OpenAI API calls
        pass

if __name__ == "__main__":
    pytest.main([__file__])

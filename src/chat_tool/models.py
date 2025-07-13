from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from dataclasses import dataclass, asdict
from enum import Enum

class ChatMode(Enum):
    NORMAL = "normal"
    SEARCH = "search"

@dataclass
class Message:
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    message_id: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "message_id": self.message_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message_id=data["message_id"]
        )

@dataclass
class ChatSession:
    session_id: str
    user_id: str
    mode: ChatMode
    system_prompt: str
    thread_id: Optional[str] = None  # For normal mode
    messages: List[Message] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.messages is None:
            self.messages = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def add_message(self, message: Message):
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_messages_for_api(self) -> List[Dict[str, str]]:
        """Get messages in format suitable for OpenAI API"""
        api_messages = []
        
        # Add system message
        if self.system_prompt:
            api_messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        # Add conversation messages
        for msg in self.messages:
            if msg.role in ["user", "assistant"]:
                api_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        return api_messages

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "mode": self.mode.value,
            "system_prompt": self.system_prompt,
            "thread_id": self.thread_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        messages = [Message.from_dict(msg_data) for msg_data in data.get("messages", [])]
        return cls(
            session_id=data["session_id"],
            user_id=data["user_id"],
            mode=ChatMode(data["mode"]),
            system_prompt=data["system_prompt"],
            thread_id=data.get("thread_id"),
            messages=messages,
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

class SessionManager:
    def __init__(self, storage_dir: str = "data/sessions"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self._sessions: Dict[str, ChatSession] = {}
        self._load_sessions()

    def _get_session_file(self, session_id: str) -> str:
        return os.path.join(self.storage_dir, f"{session_id}.json")

    def _load_sessions(self):
        """Load all sessions from storage"""
        if not os.path.exists(self.storage_dir):
            return
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                session_id = filename[:-5]  # Remove .json extension
                try:
                    with open(os.path.join(self.storage_dir, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        session = ChatSession.from_dict(data)
                        self._sessions[session_id] = session
                except Exception as e:
                    print(f"Error loading session {session_id}: {e}")

    def _save_session(self, session: ChatSession):
        """Save session to storage"""
        session_file = self._get_session_file(session.session_id)
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)

    def create_session(self, session_id: str, user_id: str, mode: ChatMode, 
                      system_prompt: str, thread_id: Optional[str] = None) -> ChatSession:
        """Create a new chat session"""
        session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            mode=mode,
            system_prompt=system_prompt,
            thread_id=thread_id
        )
        self._sessions[session_id] = session
        self._save_session(session)
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get session by ID"""
        return self._sessions.get(session_id)

    def update_session(self, session: ChatSession):
        """Update session and save to storage"""
        session.updated_at = datetime.now()
        self._sessions[session.session_id] = session
        self._save_session(session)

    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            session_file = self._get_session_file(session_id)
            if os.path.exists(session_file):
                os.remove(session_file)
            return True
        return False

    def get_user_sessions(self, user_id: str) -> List[ChatSession]:
        """Get all sessions for a user"""
        return [session for session in self._sessions.values() if session.user_id == user_id]

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

from .openai_service import OpenAIService
from .models import ChatMode

# Load environment variables first
load_dotenv()

app = FastAPI(title="Chat Tool API", version="1.0.0")

# Setup static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize OpenAI service with error handling
def create_openai_service():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  警告: 未设置 OPENAI_API_KEY 环境变量")
        return None
    
    try:
        return OpenAIService(api_key=api_key)
    except Exception as e:
        print(f"❌ 初始化OpenAI服务失败: {e}")
        return None

openai_service = create_openai_service()

# Pydantic models for API
class CreateSessionRequest(BaseModel):
    prompt_type: str = "default"
    mode: str = "normal"  # "normal" or "search"

class SendMessageRequest(BaseModel):
    message: str

class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    mode: str
    prompt_name: str

class MessageResponse(BaseModel):
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    session_id: str

def check_service():
    """Check if OpenAI service is available"""
    if openai_service is None:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI service not available. Please check your API key configuration."
        )

@app.get("/favicon.ico")
async def favicon():
    """返回一个简单的favicon响应，避免404错误"""
    return Response(status_code=204)

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "Chat Tool API",
        "timestamp": datetime.now().isoformat(),
        "openai_service": "available" if openai_service else "unavailable"
    }

# 直接对话接口 - 三个固定链接

@app.get("/", response_class=HTMLResponse)
async def normal_chat(request: Request):
    """普通对话（默认首页）"""
    return await create_interface_session(request, "default", "normal", "智能助手")

@app.get("/search", response_class=HTMLResponse)
async def search_chat(request: Request):
    """带搜索的对话"""
    return await create_interface_session(request, "research_assistant", "search", "搜索助手")

@app.get("/nosystem", response_class=HTMLResponse)
async def nosystem_chat(request: Request):
    """普通对话且不带system prompt"""
    return await create_interface_session(request, "nosystem", "normal", "自由对话")

async def create_interface_session(request: Request, prompt_type: str, mode: str, interface_name: str):
    """为特定接口创建会话"""
    if openai_service is None:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "OpenAI服务未配置，请检查API密钥设置"
        })
    
    try:
        # 自动创建会话
        import uuid
        user_id = str(uuid.uuid4())
        chat_mode = ChatMode.SEARCH if mode == "search" else ChatMode.NORMAL
        
        session = await openai_service.create_chat_session(
            user_id=user_id,
            prompt_type=prompt_type,
            mode=chat_mode
        )
        
        return templates.TemplateResponse("chat_interface.html", {
            "request": request,
            "session": session,
            "interface_name": interface_name,
            "mode": mode,
            "history": []
        })
        
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": f"创建{interface_name}会话失败: {str(e)}"
        })

@app.get("/chat/{session_id}", response_class=HTMLResponse)
async def chat_interface(request: Request, session_id: str):
    """Serve the chat interface for a specific session"""
    check_service()
    session = openai_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    history = openai_service.get_conversation_history(session_id)
    prompts = openai_service.get_available_prompts()
    
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "session": session,
        "history": history,
        "prompts": prompts
    })

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    """Create a new chat session"""
    check_service()
    try:
        # Generate unique user ID
        user_id = str(uuid.uuid4())
        
        # Validate mode
        mode = ChatMode.NORMAL if request.mode == "normal" else ChatMode.SEARCH
        
        # Create session
        session = await openai_service.create_chat_session(
            user_id=user_id,
            prompt_type=request.prompt_type,
            mode=mode
        )
        
        prompt_name = openai_service.prompt_manager.get_prompt_name(request.prompt_type)
        
        return SessionResponse(
            session_id=session.session_id,
            user_id=session.user_id,
            mode=session.mode.value,
            prompt_name=prompt_name
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(session_id: str, request: SendMessageRequest):
    """Send a message in a chat session"""
    check_service()
    try:
        result = await openai_service.send_message(session_id, request.message)
        
        return MessageResponse(
            success=result["success"],
            response=result.get("response"),
            error=result.get("error"),
            session_id=session_id
        )
    
    except Exception as e:
        return MessageResponse(
            success=False,
            error=str(e),
            session_id=session_id
        )

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    session = openai_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "mode": session.mode.value,
        "created_at": session.created_at.isoformat(),
        "updated_at": session.updated_at.isoformat()
    }

@app.post("/api/sessions/{session_id}/export")
async def export_conversation(session_id: str):
    """Export conversation to JSON file"""
    check_service()
    
    # 直接从data/sessions目录读取现有的会话文件
    sessions_dir = os.path.join(os.getcwd(), "data", "sessions")
    session_file = os.path.join(sessions_dir, f"{session_id}.json")
    
    if not os.path.exists(session_file):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 读取现有会话数据
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read session data: {str(e)}")
    
    # 创建导出数据（添加导出时间戳）
    export_data = {
        **session_data,
        "exported_at": datetime.now().isoformat(),
        "total_messages": len(session_data.get("messages", []))
    }
    
    # 确保exports目录存在
    exports_dir = os.path.join(os.getcwd(), "exports")
    os.makedirs(exports_dir, exist_ok=True)
    
    # 生成文件名（添加时间戳使其更易识别）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{session_id}_{timestamp}.json"
    filepath = os.path.join(exports_dir, filename)
    
    # 保存到exports目录
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "filename": filename,
            "session_id": session_id,
            "exported_at": export_data["exported_at"],
            "total_messages": export_data["total_messages"],
            "download_url": f"/api/download/{filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export conversation: {str(e)}")

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download exported conversation file"""
    exports_dir = os.path.join(os.getcwd(), "exports")
    filepath = os.path.join(exports_dir, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Export file not found")
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='application/json'
    )

@app.get("/api/sessions/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    history = openai_service.get_conversation_history(session_id)
    return {"history": history}

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    success = openai_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}

@app.get("/api/prompts")
async def get_available_prompts():
    """Get available system prompts"""
    return openai_service.get_available_prompts()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv("HOST", "localhost"), 
        port=int(os.getenv("PORT", 8000))
    )

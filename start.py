#!/usr/bin/env python3
"""
启动脚本 - Chat Tool
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """检查依赖是否已安装"""
    try:
        import fastapi
        import uvicorn
        import openai
        import dotenv
        import pydantic
        import jinja2
        import aiofiles
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        return False

def install_requirements():
    """安装依赖"""
    print("📦 正在安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        return False

def check_env_file():
    """检查环境变量文件"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 创建 .env 文件...")
            env_file.write_text(env_example.read_text())
            print("⚠️  请编辑 .env 文件，设置你的 OPENAI_API_KEY")
            return False
        else:
            print("❌ 找不到 .env.example 文件")
            return False
    
    # 检查是否设置了API key
    env_content = env_file.read_text()
    if "your_openai_api_key_here" in env_content:
        print("⚠️  请在 .env 文件中设置你的真实 OPENAI_API_KEY")
        return False
    
    print("✅ 环境配置文件检查通过")
    return True

def create_directories():
    """创建必要的目录"""
    directories = [
        "data/sessions",
        "static",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ 目录结构创建完成")

def main():
    """主函数"""
    print("🚀 Chat Tool 启动中...\n")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要 Python 3.8 或更高版本")
        sys.exit(1)
    
    # 切换到项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 检查依赖
    if not check_requirements():
        print("📦 正在安装依赖...")
        if not install_requirements():
            print("❌ 启动失败：无法安装依赖")
            sys.exit(1)
    
    # 检查环境文件
    if not check_env_file():
        print("❌ 启动失败：请先配置环境变量")
        print("编辑 .env 文件，设置你的 OPENAI_API_KEY")
        sys.exit(1)
    
    # 创建目录
    create_directories()
    
    # 运行测试（可选）
    if "--test" in sys.argv:
        print("🧪 运行测试...")
        try:
            subprocess.check_call([sys.executable, "tests/test_manual.py"])
            print("✅ 测试通过")
        except subprocess.CalledProcessError:
            print("⚠️  测试失败，但继续启动服务")
    
    # 获取配置
    from dotenv import load_dotenv
    load_dotenv()
    
    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    print(f"🌟 启动 Chat Tool 服务...")
    print(f"📍 地址: http://{host}:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print("\n按 Ctrl+C 停止服务\n")
    
    # 启动服务
    try:
        if debug:
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "src.chat_tool.main:app",
                "--host", host,
                "--port", str(port),
                "--reload"
            ])
        else:
            subprocess.run([
                sys.executable, "-m", "uvicorn", 
                "src.chat_tool.main:app",
                "--host", host,
                "--port", str(port)
            ])
    except KeyboardInterrupt:
        print("\n👋 Chat Tool 服务已停止")

if __name__ == "__main__":
    main()

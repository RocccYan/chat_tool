# Chat Tool - OpenAI API聊天系统

基于OpenAI API的智能聊天系统，支持多种对话模式和自定义系统提示。

## 功能特性

- 🤖 **多种助手类型**: 通用聊天、编程助手、创意写作、研究助手、商业顾问
- 🔍 **双重对话模式**: 
  - 普通对话：基于训练数据的标准对话
  - 搜索增强：支持实时网络搜索的对话
- 💾 **会话管理**: 自动保存和恢复对话历史
- 🆔 **唯一身份标识**: 每个会话生成唯一ID，支持中断和恢复
- 🛠️ **错误处理**: 完善的错误处理和重试机制
- 📱 **响应式界面**: 现代化的Web界面，支持移动设备

## 技术架构

- **后端**: FastAPI + OpenAI API
- **前端**: HTML + CSS + JavaScript (原生)
- **数据存储**: JSON文件存储 (易于扩展到数据库)
- **配置管理**: INI配置文件

## 快速开始

### 1. 环境准备

```bash
# 克隆或下载项目
cd chat_tool

# 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖 (选择其一)
pip install -r requirements.txt          # 生产环境 - 精确版本
pip install -r requirements-minimal.txt  # 最小化依赖 - 轻量级
pip install -r requirements-dev.txt      # 开发环境 - 包含测试工具

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置你的 OpenAI API Key
```

### 2. 配置OpenAI API Key

在 `.env` 文件中设置：
```
OPENAI_API_KEY=your_openai_api_key_here
```

或者设置环境变量：
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

### 3. 运行应用

```bash
# 方法1：使用Python直接运行
cd src/chat_tool
python main.py

# 方法2：使用uvicorn运行
uvicorn src.chat_tool.main:app --host localhost --port 8000 --reload
```

### 4. 访问应用

打开浏览器访问：http://localhost:8000

## 项目结构

```
chat_tool/
├── src/chat_tool/           # 主要源代码
│   ├── main.py             # FastAPI应用入口
│   ├── models.py           # 数据模型
│   ├── openai_service.py   # OpenAI API服务
│   └── config_manager.py   # 配置管理
├── templates/              # HTML模板
│   ├── index.html         # 主页
│   └── chat.html          # 聊天界面
├── config/                 # 配置文件
│   └── system_prompts.ini # 系统提示配置
├── data/                  # 数据存储
│   └── sessions/         # 会话数据
├── tests/                 # 测试文件
│   ├── openai_api_test.ipynb # OpenAI API测试
│   ├── test_chat_system.py   # 单元测试
│   └── test_manual.py        # 手动测试
├── requirements.txt       # Python依赖
└── README.md             # 项目说明
```

## 使用说明

### 1. 选择助手类型

系统提供多种预设的助手类型：
- **通用聊天助手**: 日常对话和通用问题解答
- **编程助手**: 代码编写、调试、技术问题
- **创意写作助手**: 故事创作、文案写作
- **研究助手**: 信息搜索、数据分析
- **商业顾问**: 商业策略、市场分析

### 2. 选择对话模式

- **普通对话**: 基于OpenAI训练数据的标准对话
- **搜索增强**: 可以访问实时网络信息的对话

### 3. 开始对话

选择助手类型和模式后，点击"开始对话"创建新会话。每个会话都有唯一的ID，显示在界面左上角。

### 4. 会话管理

- **会话ID**: 每个会话都有8位短ID显示
- **历史记录**: 自动保存所有对话内容
- **中断恢复**: 可以随时关闭浏览器，稍后通过URL恢复会话
- **清空历史**: 可以清空当前会话的所有消息

## API接口

### 创建会话
```http
POST /api/sessions
Content-Type: application/json

{
    "prompt_type": "default",
    "mode": "normal"
}
```

### 发送消息
```http
POST /api/sessions/{session_id}/messages
Content-Type: application/json

{
    "message": "你好，世界！"
}
```

### 获取会话历史
```http
GET /api/sessions/{session_id}/history
```

## 自定义配置

### 添加新的助手类型

编辑 `config/system_prompts.ini` 文件：

```ini
[my_assistant]
name = 我的自定义助手
system_prompt = 你是一个专门的助手，擅长...
```

### 修改系统设置

编辑 `.env` 文件：

```env
DEBUG=True
HOST=localhost
PORT=8000
OPENAI_API_KEY=your_key_here
```

## 开发和测试

### 运行测试

```bash
# 运行手动测试
python tests/test_manual.py

# 运行Jupyter notebook测试
jupyter notebook tests/openai_api_test.ipynb
```

### 开发模式

```bash
# 启用热重载
uvicorn src.chat_tool.main:app --reload --host 0.0.0.0 --port 8000
```

## 故障排除

### 常见问题

1. **API Key错误**: 确保在.env文件中正确设置了OPENAI_API_KEY
2. **模块导入错误**: 确保从项目根目录运行应用
3. **端口占用**: 修改.env文件中的PORT设置
4. **网络错误**: 检查网络连接和防火墙设置

### 错误处理

系统提供完善的错误处理机制：
- API调用失败时显示错误信息
- 提供重试按钮
- 自动保存会话状态
- 网络断开时的提示

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 许可证

请查看LICENSE文件了解许可证信息。 

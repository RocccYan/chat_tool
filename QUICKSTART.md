# 快速开始指南

## 🚀 快速安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API Key

复制环境变量模板并设置你的OpenAI API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
OPENAI_API_KEY=your_actual_api_key_here
DEBUG=True
HOST=localhost
PORT=8000
```

### 3. 运行测试（可选）

```bash
# 测试核心功能
python tests/test_manual.py

# 测试OpenAI API功能（需要API Key）
jupyter notebook tests/openai_api_test.ipynb
```

### 4. 启动服务

#### 方法1：使用启动脚本（推荐）
```bash
python start.py
```

#### 方法2：直接使用uvicorn
```bash
uvicorn src.chat_tool.main:app --host localhost --port 8000 --reload
```

#### 方法3：直接运行Python
```bash
cd src/chat_tool
python main.py
```

### 5. 访问应用

打开浏览器访问：http://localhost:8000

## 🎯 功能演示

### 聊天界面功能
1. **选择助手类型**：默认提供5种预设助手
2. **选择对话模式**：普通对话 vs 搜索增强
3. **开始对话**：生成唯一会话ID
4. **消息交互**：支持多轮对话
5. **会话管理**：保存/恢复/清空历史

### API接口测试

```bash
# 创建新会话
curl -X POST "http://localhost:8000/api/sessions" \
  -H "Content-Type: application/json" \
  -d '{"prompt_type": "default", "mode": "normal"}'

# 发送消息（替换session_id）
curl -X POST "http://localhost:8000/api/sessions/YOUR_SESSION_ID/messages" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，世界！"}'

# 获取对话历史
curl "http://localhost:8000/api/sessions/YOUR_SESSION_ID/history"
```

## 🛠️ 开发模式

启用热重载进行开发：
```bash
uvicorn src.chat_tool.main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 系统要求

- Python 3.8+
- OpenAI API Key
- 网络连接（用于API调用）

## ⚠️ 注意事项

1. **API费用**：搜索增强模式会产生额外费用
2. **网络要求**：需要稳定的网络连接访问OpenAI API
3. **数据存储**：会话数据存储在 `data/sessions/` 目录
4. **安全性**：不要在公共环境中暴露API Key

## 🐛 故障排除

### 常见问题

1. **模块导入错误**
   ```bash
   # 确保从项目根目录运行
   cd /path/to/chat_tool
   python start.py
   ```

2. **API Key错误**
   ```bash
   # 检查环境变量
   cat .env | grep OPENAI_API_KEY
   ```

3. **端口占用**
   ```bash
   # 修改端口
   export PORT=8001
   python start.py
   ```

4. **依赖问题**
   ```bash
   # 重新安装依赖
   pip install -r requirements.txt --force-reinstall
   ```

## 🔧 自定义配置

### 添加新助手类型

编辑 `config/system_prompts.ini`：

```ini
[my_custom_assistant]
name = 我的自定义助手
system_prompt = 你是一个专门的助手，专长是...
```

### 修改界面样式

编辑 `templates/` 目录下的HTML文件来自定义界面。

### 扩展功能

- 修改 `src/chat_tool/models.py` 添加新的数据模型
- 修改 `src/chat_tool/openai_service.py` 添加新的AI功能
- 修改 `src/chat_tool/main.py` 添加新的API端点

# Chat Tool 部署指南

## 环境要求

- Python 3.8+
- pip (Python包管理器)
- 操作系统: Linux, macOS, Windows

## 部署选项

### 1. 生产环境部署

#### 使用精确版本 (推荐)
```bash
# 安装精确版本的依赖包 (锁定版本，确保环境一致性)
pip install -r requirements.txt
```

#### 使用最小化依赖 (轻量级部署)
```bash
# 仅安装核心功能依赖 (让pip自动解析最新兼容版本)
pip install -r requirements-minimal.txt
```

### 2. 开发环境设置

```bash
# 安装开发依赖 (包含测试和调试工具)
pip install -r requirements-dev.txt
```

## 依赖包说明

### 核心运行时依赖
| 包名 | 版本 | 用途 |
|-----|------|------|
| fastapi | 0.116.1 | Web API框架 |
| uvicorn | 0.35.0 | ASGI服务器 |
| openai | 1.95.1 | OpenAI API客户端 |
| python-dotenv | 1.1.1 | 环境变量管理 |
| pydantic | 2.11.7 | 数据验证和序列化 |
| jinja2 | 3.1.6 | HTML模板引擎 |
| aiofiles | 24.1.0 | 异步文件操作 |

### 可选开发依赖
| 包名 | 用途 |
|-----|------|
| jupyter | API测试和开发 |
| pytest | 单元测试 |
| black | 代码格式化 |
| mypy | 类型检查 |

## Docker 部署 (可选)

### 创建 Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "src.chat_tool.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 构建和运行
```bash
# 构建镜像
docker build -t chat-tool .

# 运行容器
docker run -d -p 8000:8000 -e OPENAI_API_KEY=your_key_here chat-tool
```

## 环境变量配置

### 必需环境变量
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 可选环境变量
```bash
HOST=localhost          # 服务器主机地址
PORT=8000              # 服务器端口
DEBUG=False            # 调试模式
```

## 性能优化

### 生产环境建议
1. 使用 `gunicorn` 多进程部署:
```bash
pip install gunicorn
gunicorn src.chat_tool.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. 使用反向代理 (Nginx):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 故障排除

### 常见问题
1. **依赖冲突**: 使用虚拟环境隔离依赖
2. **版本不兼容**: 使用 `requirements.txt` 中的精确版本
3. **OpenAI API错误**: 检查API密钥和网络连接

### 验证部署
```bash
# 检查服务状态
curl http://localhost:8000/health

# 测试API端点
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"prompt_type": "default", "mode": "normal"}'
```

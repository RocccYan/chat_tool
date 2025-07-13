# Chat Tool Windows 部署指南

## Windows 环境特殊配置

### 1. Python 环境检查

#### 检查 Python 版本
```cmd
python --version
# 或
python3 --version
```

如果没有安装 Python，请从 [python.org](https://www.python.org/downloads/) 下载 Python 3.8+ 版本。

#### 设置虚拟环境
```cmd
# Windows CMD
python -m venv venv
venv\Scripts\activate

# Windows PowerShell
python -m venv venv
venv\Scripts\Activate.ps1

# Git Bash (推荐)
python -m venv venv
source venv/Scripts/activate
```

### 2. 依赖安装

```cmd
# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt

# 如果出现网络问题，使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 3. 环境变量配置

#### 方法1: 使用 .env 文件
```cmd
# 复制配置文件
copy .env.example .env

# 编辑 .env 文件 (使用记事本或 VS Code)
notepad .env
```

在 .env 文件中设置：
```env
OPENAI_API_KEY=your_actual_api_key_here
HOST=localhost
PORT=8000
DEBUG=True
```

#### 方法2: 使用系统环境变量
```cmd
# CMD 方式 (临时)
set OPENAI_API_KEY=your_actual_api_key_here

# PowerShell 方式 (临时)
$env:OPENAI_API_KEY="your_actual_api_key_here"

# 永久设置 (系统环境变量)
setx OPENAI_API_KEY "your_actual_api_key_here"
```

### 4. 启动应用

```cmd
# 方法1: 直接运行
cd src\chat_tool
python main.py

# 方法2: 使用 uvicorn
uvicorn src.chat_tool.main:app --host 0.0.0.0 --port 8000 --reload

# 方法3: 在项目根目录运行
python -m src.chat_tool.main
```

## Windows 常见问题排除

### 问题1: 模块导入错误
```
ModuleNotFoundError: No module named 'src'
```

**解决方案:**
```cmd
# 确保在项目根目录
cd path\to\chat_tool

# 添加当前目录到 Python 路径
set PYTHONPATH=%cd%;%PYTHONPATH%

# 或者使用 -m 参数运行
python -m src.chat_tool.main
```

### 问题2: Request timed out (网络超时)
```
创建智能助手会话失败: Request timed out
```

**可能原因和解决方案:**

#### A. 网络连接问题
```cmd
# 测试网络连接
ping api.openai.com

# 如果无法连接，检查:
# 1. 防火墙设置
# 2. 代理配置
# 3. DNS设置
```

#### B. API密钥问题
```cmd
# 验证API密钥设置
echo %OPENAI_API_KEY%

# 重新设置API密钥
setx OPENAI_API_KEY "your_correct_api_key_here"

# 重启命令提示符使环境变量生效
```

#### C. OpenAI服务限制
- 检查API配额是否用完
- 验证API密钥是否有效
- 确认账户状态正常

#### D. 网络代理配置
如果使用公司网络或代理:
```cmd
# 设置代理 (如果需要)
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=http://proxy.company.com:8080

# 或在代码中配置 (不推荐，仅用于调试)
```

### 问题3: 控制台显示乱码
```
?[32mINFO?[0m: Started server process
```

**解决方案:**
```cmd
# 设置UTF-8编码
chcp 65001

# 使用Windows Terminal而不是CMD
# 或禁用颜色输出
set NO_COLOR=1
```

### 问题2: 端口被占用
```
OSError: [WinError 10048] 通常每个套接字地址(协议/网络地址/端口)只允许使用一次
```

**解决方案:**
```cmd
# 查看端口占用
netstat -ano | findstr :8000

# 结束占用端口的进程
taskkill /PID <进程ID> /F

# 或者使用不同端口
uvicorn src.chat_tool.main:app --port 8001
```

### 问题3: 权限问题
```
PermissionError: [WinError 5] 拒绝访问
```

**解决方案:**
```cmd
# 以管理员身份运行命令提示符
# 或者修改文件夹权限

# 检查防火墙设置
# Windows设置 -> 更新和安全 -> Windows安全中心 -> 防火墙和网络保护
```

### 问题4: SSL/网络连接问题
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**解决方案:**
```cmd
# 升级证书
pip install --upgrade certifi

# 临时禁用SSL验证 (不推荐生产环境)
set PYTHONHTTPSVERIFY=0
```

### 问题5: 编码问题
```
UnicodeDecodeError
```

**解决方案:**
```cmd
# 设置编码
set PYTHONIOENCODING=utf-8
chcp 65001
```

## Windows 性能优化

### 1. 使用 Windows Terminal
推荐安装 Windows Terminal 获得更好的命令行体验。

### 2. 防火墙配置
如果需要外部访问，在 Windows 防火墙中允许 Python 应用通过防火墙。

### 3. 后台服务运行
```cmd
# 使用 nssm 将应用注册为 Windows 服务
# 下载 nssm.exe

nssm install ChatToolService
# 设置程序路径: C:\path\to\python.exe
# 设置参数: -m src.chat_tool.main
# 设置工作目录: C:\path\to\chat_tool
```

## 自动化批处理脚本

创建 `start_chat_tool.bat`:
```batch
@echo off
echo Starting Chat Tool...

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查环境变量
if "%OPENAI_API_KEY%"=="" (
    echo ERROR: OPENAI_API_KEY not set!
    echo Please set your OpenAI API key in .env file or environment variables
    pause
    exit /b 1
)

REM 启动应用
echo Starting server on http://localhost:8000
python -m src.chat_tool.main

pause
```

创建 `install_dependencies.bat`:
```batch
@echo off
echo Installing Chat Tool dependencies...

REM 创建虚拟环境
python -m venv venv

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 升级 pip
python -m pip install --upgrade pip

REM 安装依赖
pip install -r requirements.txt

echo Installation complete!
echo Please configure your .env file with your OpenAI API key
echo Then run start_chat_tool.bat to start the application

pause
```

## Docker Windows 部署

如果您使用 Docker Desktop for Windows:

```dockerfile
# 使用 Windows 兼容的基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "src.chat_tool.main"]
```

构建和运行:
```cmd
docker build -t chat-tool .
docker run -d -p 8000:8000 -e OPENAI_API_KEY=your_key_here chat-tool
```

## 网络配置说明

### 内网访问配置
如果需要其他设备访问，修改启动命令：
```cmd
uvicorn src.chat_tool.main:app --host 0.0.0.0 --port 8000
```

### 防火墙端口开放
1. 打开 Windows 防火墙设置
2. 选择"高级设置"
3. 添加入站规则，开放 8000 端口

## 故障排除检查清单

1. ✅ Python 版本 >= 3.8
2. ✅ 虚拟环境已激活
3. ✅ 依赖包已安装
4. ✅ OPENAI_API_KEY 已设置
5. ✅ 端口 8000 未被占用
6. ✅ 防火墙允许应用通过
7. ✅ 工作目录正确
8. ✅ 网络连接正常

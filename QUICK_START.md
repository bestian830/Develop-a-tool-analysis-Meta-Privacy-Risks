# Privacy Policy Analyzer - 启动指南

## 快速启动

### macOS / Linux

```bash
./start.sh
```

### Windows

双击运行 `start.bat` 或在命令行执行：

```cmd
start.bat
```

## 手动启动

如果自动启动脚本有问题，可以手动启动：

### 1. 启动后端

```bash
# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 启动API服务器
python run_api.py
```

后端将在 http://localhost:5001 运行

### 2. 启动前端（新终端）

```bash
cd frontend
npm start
```

前端将在 http://localhost:3000 运行

## 功能

启动脚本会自动：
- ✅ 检查并创建Python虚拟环境
- ✅ 检查并安装后端依赖
- ✅ 检查并下载spaCy模型
- ✅ 检查并安装前端依赖
- ✅ 同时启动后端和前端服务
- ✅ 显示服务状态和访问地址

## 停止服务

- **macOS/Linux**: 按 `Ctrl+C`
- **Windows**: 关闭对应的命令行窗口


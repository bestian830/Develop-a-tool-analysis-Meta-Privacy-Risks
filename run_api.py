#!/usr/bin/env python3
"""
启动Flask API服务器
"""
import sys
from pathlib import Path

# 添加api目录到路径
api_dir = Path(__file__).parent / 'api'
sys.path.insert(0, str(api_dir))
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'tools'))

# 现在可以导入api目录下的模块
from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("隐私政策分析器 API 服务器")
    print("=" * 60)
    print("API地址: http://localhost:5001")
    print("健康检查: http://localhost:5001/api/health")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5001)


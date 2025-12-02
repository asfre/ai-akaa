# app/api/chat.py
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    from app.database.connection import get_mysql_connection
    print("✅ chat.py: 成功导入数据库连接")
except ImportError as e:
    print(f"❌ chat.py: 导入数据库连接失败: {e}")
    raise

router = APIRouter()

# 其余代码保持不变...
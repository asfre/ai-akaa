from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pymysql
import hashlib
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    from app.database.connection import get_mysql_connection
    print("✅ auth.py: 成功导入数据库连接")
except ImportError as e:
    print(f"❌ auth.py: 导入数据库连接失败: {e}")
    raise

router = APIRouter()
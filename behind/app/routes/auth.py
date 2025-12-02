from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
import pymysql
import hashlib
import traceback
import sys
import os
import jwt


# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

try:
    from app.database.connection import get_mysql_connection
    print("✅ auth.py: 成功导入数据库连接")
except ImportError as e:
    print(f"❌ auth.py: 导入数据库连接失败: {e}")
    # 创建临时的数据库连接函数
    def get_mysql_connection():
        return pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            database='chat',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )

router = APIRouter()

# 请求/响应模型
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: str
    user_id: int
    username: str

class ChangePasswordRequest(BaseModel):
    oldPassword: str
    newPassword: str

def get_user_id_from_token(token: str) -> Optional[int]:
    """
    从JWT token中提取用户ID
    
    Args:
        token: JWT token字符串
        
    Returns:
        用户ID或None（如果token无效）
    """
    try:
        # 移除Bearer前缀（如果有）
        if token.startswith('Bearer '):
            token = token[7:]
            
        # 解码token
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        
        # 返回用户ID
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        print("Token已过期")
        return None
    except jwt.InvalidTokenError:
        print("无效的Token")
        return None
    except Exception as e:
        print(f"Token解析错误: {e}")
        return None

def hash_password(password: str) -> str:
    """MD5加密密码"""
    return hashlib.md5(password.encode()).hexdigest()

def verify_password(plain_password, password_hash):
    """验证MD5加密密码"""
    try:
        hashed_input = hashlib.md5(plain_password.encode()).hexdigest()
        print(f"🔐 密码验证: 输入MD5={hashed_input}, 数据库MD5={password_hash}")
        return hashed_input == password_hash
    except Exception as e:
        print(f"❌ 密码验证错误: {e}")
        return False

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """用户登录"""
    connection = None
    try:
        print(f"🔑 登录尝试: 用户名={login_data.username}")
        
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            # 查询用户信息
            sql = "SELECT id, username, password_hash FROM users WHERE username = %s"
            cursor.execute(sql, (login_data.username,))
            user = cursor.fetchone()
        
        if not user:
            print("❌ 用户不存在")
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        print(f"✅ 找到用户: ID={user['id']}, 用户名={user['username']}")
        
        # 验证密码
        if not verify_password(login_data.password, user["password_hash"]):
            print("❌ 密码验证失败")
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        print("✅ 密码验证成功")
        
        # 生成token
        token = f"token_{user['id']}_{user['username']}"
        print(f"✅ 生成token: {token}")
        
        return LoginResponse(
            success=True,
            token=token,
            user_id=user["id"],
            username=user["username"]
        )
        
    except HTTPException as he:
        print(f"❌ HTTP异常: {he.detail}")
        raise he
    except Exception as e:
        print(f"❌ 登录过程异常: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")
    finally:
        if connection:
            connection.close()

@router.post("/logout")
async def logout():
    """用户退出登录"""
    return {"success": True, "message": "退出成功"}

@router.put("/password")
async def change_password(
    password_data: ChangePasswordRequest, 
    authorization: str = Header(...)
):
    """修改密码"""
    connection = None
    try:
        # 从token获取用户ID
        user_id = get_user_id_from_token(authorization)
        print(f"🔑 修改密码请求: 用户ID={user_id}")
        
        # 验证新密码长度
        # if len(password_data.newPassword) < 6:
        #     raise HTTPException(status_code=400, detail="新密码长度至少6位")
        
        # 验证新旧密码不能相同
        if password_data.oldPassword == password_data.newPassword:
            raise HTTPException(status_code=400, detail="新密码不能与旧密码相同")
        
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            # 查询用户当前密码
            sql = "SELECT id, username, password_hash FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="用户不存在")
            
            print(f"✅ 找到用户: {user['username']}")
            
            # 验证原密码
            if not verify_password(password_data.oldPassword, user["password_hash"]):
                print("❌ 原密码验证失败")
                raise HTTPException(status_code=400, detail="原密码错误")
            
            print("✅ 原密码验证成功")
            
            # 更新密码
            new_password_hash = hash_password(password_data.newPassword)
            sql = "UPDATE users SET password_hash = %s WHERE id = %s"
            cursor.execute(sql, (new_password_hash, user_id))
            connection.commit()
            
            print("✅ 密码更新成功")
            
            return {
                "success": True,
                "message": "密码修改成功"
            }
            
    except HTTPException as he:
        print(f"❌ HTTP异常: {he.detail}")
        raise he
    except Exception as e:
        print(f"❌ 修改密码过程异常: {e}")
        traceback.print_exc()
        # 回滚事务
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"修改密码失败: {str(e)}")
    finally:
        if connection:
            connection.close()
# chat.py
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
import time
from app.database.connection import get_mysql_connection

router = APIRouter()

# 数据模型
class SendMessageRequest(BaseModel):
    chat_id: int
    question: str
    timestamp: int

class SendMessageResponse(BaseModel):
    success: bool
    answer: str
    message_id: int

def get_user_id_from_token(authorization: str = Header(...)) -> int:
    """从token中提取用户ID（简化版）"""
    try:
        if authorization and authorization.startswith("token_"):
            parts = authorization.replace("token_", "").split("_")
            return int(parts[0])
        return 1  # 默认用户ID
    except:
        return 1

@router.get("/chats")
async def get_chat_list(authorization: str = Header(...)):
    """获取聊天列表"""
    print(f"🔍 收到获取聊天列表请求，token: {authorization}")
    user_id = get_user_id_from_token(authorization)
    print(f"👤 用户ID: {user_id}")
    
    connection = None
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            sql = """
            SELECT cs.id, cs.title, cs.created_at, cs.updated_at, 
                   COUNT(m.id) as message_count
            FROM chat_sessions cs
            LEFT JOIN messages m ON cs.id = m.session_id AND m.is_deleted = FALSE
            WHERE cs.user_id = %s AND cs.is_active = TRUE
            GROUP BY cs.id
            ORDER BY cs.updated_at DESC
            """
            cursor.execute(sql, (user_id,))
            results = cursor.fetchall()
            
            chat_list = []
            for row in results:
                chat_list.append({
                    "id": row['id'],
                    "title": row['title'],
                    "createTime": row['created_at'].strftime("%Y-%m-%d %H:%M"),
                    "messageCount": row['message_count']
                })
            
            print(f"✅ 返回聊天列表: {len(chat_list)} 个对话")
            return chat_list
    except Exception as e:
        print(f"❌ 获取聊天列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取聊天列表失败: {str(e)}")
    finally:
        if connection:
            connection.close()

@router.post("/chats")
async def create_chat(authorization: str = Header(...), title: str = "新对话"):
    """创建新聊天"""
    user_id = get_user_id_from_token(authorization)
    connection = None
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            sql = "INSERT INTO chat_sessions (user_id, title) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, title))
            chat_id = cursor.lastrowid
            connection.commit()
            
            return {
                "success": True,
                "chat_id": chat_id,
                "title": title
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建聊天失败: {str(e)}")
    finally:
        if connection:
            connection.close()

@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: int, authorization: str = Header(...)):
    """删除聊天"""
    user_id = get_user_id_from_token(authorization)
    connection = None
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            # 验证聊天属于该用户
            sql = "SELECT id FROM chat_sessions WHERE id = %s AND user_id = %s"
            cursor.execute(sql, (chat_id, user_id))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="聊天不存在或无权限")
            
            sql = "UPDATE chat_sessions SET is_active = FALSE WHERE id = %s"
            cursor.execute(sql, (chat_id,))
            connection.commit()
            
            return {"success": True, "message": "删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除聊天失败: {str(e)}")
    finally:
        if connection:
            connection.close()

@router.get("/chats/{chat_id}/messages")
async def get_chat_messages(chat_id: int, authorization: str = Header(...)):
    """获取聊天消息"""
    user_id = get_user_id_from_token(authorization)
    connection = None
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            # 验证聊天属于该用户
            sql = "SELECT id FROM chat_sessions WHERE id = %s AND user_id = %s AND is_active = TRUE"
            cursor.execute(sql, (chat_id, user_id))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="聊天不存在或无权限")
            
            sql = """
            SELECT id, role, content, created_at 
            FROM messages 
            WHERE session_id = %s AND is_deleted = FALSE 
            ORDER BY created_at ASC
            """
            cursor.execute(sql, (chat_id,))
            results = cursor.fetchall()
            
            messages = []
            for row in results:
                messages.append({
                    "id": row['id'],
                    "role": row['role'],
                    "content": row['content'],
                    "created_at": row['created_at'].strftime("%H:%M")
                })
            
            return {
                "success": True,
                "messages": messages
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息失败: {str(e)}")
    finally:
        if connection:
            connection.close()

@router.post("/chat/message")
async def send_message(request: SendMessageRequest, authorization: str = Header(...)):
    """发送消息"""
    user_id = get_user_id_from_token(authorization)
    connection = None
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            # 验证聊天属于该用户
            sql = "SELECT id, title FROM chat_sessions WHERE id = %s AND user_id = %s AND is_active = TRUE"
            cursor.execute(sql, (request.chat_id, user_id))
            chat = cursor.fetchone()
            if not chat:
                raise HTTPException(status_code=404, detail="聊天不存在或无权限")
            
            # 添加用户消息
            sql = "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)"
            cursor.execute(sql, (request.chat_id, 'user', request.question))
            user_message_id = cursor.lastrowid
            
            # 模拟 AI 回复
            ai_response = f"这是对您问题『{request.question}』的模拟回复。在实际应用中，这里会集成真实的 AI 接口。"
            
            # 添加AI回复
            cursor.execute(sql, (request.chat_id, 'assistant', ai_response))
            ai_message_id = cursor.lastrowid
            
            # 更新会话标题（如果是新对话）
            if chat['title'] == '新对话':
                new_title = request.question[:20] + ("..." if len(request.question) > 20 else "")
                sql = "UPDATE chat_sessions SET title = %s WHERE id = %s"
                cursor.execute(sql, (new_title, request.chat_id))
            
            # 更新会话时间
            sql = "UPDATE chat_sessions SET updated_at = NOW() WHERE id = %s"
            cursor.execute(sql, (request.chat_id,))
            
            connection.commit()
            
            return SendMessageResponse(
                success=True,
                answer=ai_response,
                message_id=ai_message_id
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")
    finally:
        if connection:
            connection.close()

@router.delete("/chats/{chat_id}/messages")
async def clear_chat_messages(chat_id: int, authorization: str = Header(...)):
    """清空聊天消息"""
    user_id = get_user_id_from_token(authorization)
    connection = None
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            # 验证聊天属于该用户
            sql = "SELECT id FROM chat_sessions WHERE id = %s AND user_id = %s"
            cursor.execute(sql, (chat_id, user_id))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="聊天不存在或无权限")
            
            sql = "UPDATE messages SET is_deleted = TRUE WHERE session_id = %s"
            cursor.execute(sql, (chat_id,))
            connection.commit()
            
            return {"success": True, "message": "消息已清空"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空消息失败: {str(e)}")
    finally:
        if connection:
            connection.close()
            
            
            
            @router.get("/test")
async def test_connection():
    """测试数据库连接和路由"""
    connection = None
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            return {
                "success": True,
                "message": "数据库连接正常",
                "test_result": result['test']
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"数据库连接失败: {str(e)}"
        }
    finally:
        if connection:
            connection.close()
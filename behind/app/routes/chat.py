from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Optional
import time
from app.database.connection import get_mysql_connection
from app.services.ai_service import ai_service
from app.routes.auth import get_user_id_from_token

router = APIRouter()

# 数据模型
class SendMessageRequest(BaseModel):
    chat_id: int
    question: str

class SendMessageResponse(BaseModel):
    success: bool
    answer: str
    message_id: int

def get_user_id_from_token(authorization: str = Header(...)) -> int:
    """从token中提取用户ID（简化版）"""
    try:
        # 实际应该使用JWT验证，这里简化处理
        if authorization.startswith("token_"):
            parts = authorization.replace("token_", "").split("_")
            return int(parts[0])
        return 1  # 默认用户ID
    except:
        return 1

@router.get("/chats")
async def get_chat_list(authorization: str = Header(...)):
    """获取聊天列表"""
    user_id = get_user_id_from_token(authorization)
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
            
            return chat_list
    except Exception as e:
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

@router.post("/message")
async def send_message(request: SendMessageRequest, authorization: str = Header(...)):
    """发送消息并获取AI回复"""
    user_id = get_user_id_from_token(authorization)
    connection = None
    try:
        connection = get_mysql_connection()
        with connection.cursor() as cursor:
            # 验证聊天属于该用户
            sql = "SELECT id, title FROM chat_sessions WHERE id = %s AND user_id = %s AND is_active = TRUE"
            await update_hot_questions(cursor, request.question, user_id)
            cursor.execute(sql, (request.chat_id, user_id))
            chat = cursor.fetchone()
            if not chat:
                raise HTTPException(status_code=404, detail="聊天不存在或无权限")
            
            # 获取最近的聊天历史（用于上下文）
            sql = """
                SELECT role, content 
                FROM messages 
                WHERE session_id = %s 
                ORDER BY created_at DESC 
                LIMIT 10
            """
            cursor.execute(sql, (request.chat_id,))
            history_messages = cursor.fetchall()
            # 反转顺序，让历史消息按时间正序排列
            chat_history = list(reversed(history_messages)) if history_messages else []
            
            # 添加用户消息到数据库
            sql = "INSERT INTO messages (session_id, role, content) VALUES (%s, %s, %s)"
            cursor.execute(sql, (request.chat_id, 'user', request.question))
            user_message_id = cursor.lastrowid
            
            # 调用真实的AI服务生成回复
            ai_response = await ai_service.generate_response(request.question, chat_history)
            
            # 如果AI回复为空或出错，使用备用回复
            if not ai_response or len(ai_response.strip()) == 0:
                ai_response = "抱歉，我暂时无法回答这个问题。请尝试重新提问或稍后再试。"
            
            # 添加AI回复到数据库
            cursor.execute(sql, (request.chat_id, 'assistant', ai_response))
            ai_message_id = cursor.lastrowid
            
            # 更新热门问题表
            try:
                # 检查问题是否已存在
                sql = "SELECT id, ask_count FROM hot_questions WHERE question_text = %s"
                cursor.execute(sql, (request.question,))
                existing_question = cursor.fetchone()
                
                if existing_question:
                    # 更新提问次数
                    sql = "UPDATE hot_questions SET ask_count = ask_count + 1, last_asked_at = NOW() WHERE id = %s"
                    cursor.execute(sql, (existing_question['id'],))
                else:
                    # 插入新问题
                    sql = "INSERT INTO hot_questions (question_text, ask_count) VALUES (%s, 1)"
                    cursor.execute(sql, (request.question,))
            except Exception as e:
                # 热门问题更新失败不影响主流程
                print(f"更新热门问题失败: {e}")
            
            # 更新会话标题（如果是新对话或标题为默认值）
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
        if connection:
            connection.rollback()
        raise HTTPException(status_code=500, detail=f"发送消息失败: {str(e)}")
    finally:
        if connection:
            connection.close()
async def update_hot_questions(cursor, question: str, user_id: int):
    """更新热门问题统计"""
    try:
        # 1. 问题预处理
        processed_question = preprocess_question(question)
        
        if not processed_question or len(processed_question.strip()) < 2:
            return
        
        # 2. 检查是否已存在类似问题（使用模糊匹配）
        similar_question_id = await find_similar_question(cursor, processed_question)
        
        if similar_question_id:
            # 更新现有问题的提问次数
            sql = """
                UPDATE hot_questions 
                SET ask_count = ask_count + 1, 
                    last_asked_at = NOW(),
                    user_ask_count = user_ask_count + 1
                WHERE id = %s
            """
            cursor.execute(sql, (similar_question_id,))
        else:
            # 插入新问题
            sql = """
                INSERT INTO hot_questions 
                (question_text, processed_text, ask_count, user_ask_count, first_asked_by, category) 
                VALUES (%s, %s, 1, 1, %s, %s)
            """
            category = categorize_question(processed_question)
            cursor.execute(sql, (question, processed_question, user_id, category))
        
        # 3. 提取关键词并更新关键词热度
        keywords = extract_keywords(processed_question)
        for keyword in keywords:
            await update_keyword_heat(cursor, keyword, user_id)
            
    except Exception as e:
        print(f"❌ 更新热门问题失败: {e}")

def preprocess_question(question: str) -> str:
    """问题预处理"""
    import re
    import jieba
    
    # 移除标点符号和特殊字符
    question = re.sub(r'[^\w\u4e00-\u9fa5]', ' ', question)
    
    # 分词处理
    words = jieba.cut(question)
    
    # 过滤停用词
    stop_words = {'吗', '呢', '的', '了', '啊', '呀', '什么', '怎么', '如何', '为什么', '是不是', '有没有'}
    filtered_words = [word for word in words if word.strip() and word not in stop_words and len(word) > 1]
    
    return ' '.join(filtered_words)

async def find_similar_question(cursor, processed_question: str) -> int:
    """查找相似问题（使用文本相似度）"""
    try:
        # 获取所有已处理的问题文本
        cursor.execute("SELECT id, processed_text FROM hot_questions")
        existing_questions = cursor.fetchall()
        
        for question in existing_questions:
            similarity = calculate_similarity(processed_question, question['processed_text'])
            if similarity > 0.7:  # 相似度阈值
                return question['id']
        
        return None
    except:
        return None

def calculate_similarity(text1: str, text2: str) -> float:
    """计算文本相似度（简化的Jaccard相似度）"""
    if not text1 or not text2:
        return 0.0
    
    set1 = set(text1.split())
    set2 = set(text2.split())
    
    if not set1 or not set2:
        return 0.0
    
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0

def categorize_question(question: str) -> str:
    """问题分类"""
    categories = {
        '技术': ['代码', '编程', '开发', '技术', 'bug', '错误', '框架', '库', 'API'],
        '学习': ['学习', '教程', '入门', '基础', '怎么学', '如何学'],
        '概念': ['什么', '概念', '定义', '意思', '区别', '对比'],
        '实践': ['项目', '实战', '案例', '示例', 'demo'],
        '其他': []
    }
    
    for category, keywords in categories.items():
        if any(keyword in question for keyword in keywords):
            return category
    
    return '其他'

def extract_keywords(question: str) -> list:
    """提取关键词"""
    import jieba.analyse
    
    # 使用TF-IDF提取关键词
    keywords = jieba.analyse.extract_tags(question, topK=5)
    return [kw for kw in keywords if len(kw) > 1]

async def update_keyword_heat(cursor, keyword: str, user_id: int):
    """更新关键词热度"""
    try:
        # 检查关键词是否存在
        cursor.execute("SELECT id, heat_count FROM hot_keywords WHERE keyword = %s", (keyword,))
        existing_keyword = cursor.fetchone()
        
        if existing_keyword:
            # 更新热度
            cursor.execute(
                "UPDATE hot_keywords SET heat_count = heat_count + 1, last_used = NOW() WHERE id = %s",
                (existing_keyword['id'],)
            )
        else:
            # 插入新关键词
            cursor.execute(
                "INSERT INTO hot_keywords (keyword, heat_count, first_used_by) VALUES (%s, 1, %s)",
                (keyword, user_id)
            )
    except Exception as e:
        print(f"❌ 更新关键词热度失败: {e}")
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
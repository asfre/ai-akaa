# app/routes/stats.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
import random
import time
from datetime import datetime

router = APIRouter()

class StatCard(BaseModel):
    title: str
    value: str
    trend: Dict[str, str]
    sparkline: List[int]

class OverviewResponse(BaseModel):
    success: bool
    data: List[StatCard]

class UsageTrendResponse(BaseModel):
    success: bool
    data: Dict[str, Any]

class UserDistributionResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]

class HotQuestionsResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]

class RealtimeDataResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]

# 尝试导入数据库连接
try:
    from app.database.connection import get_mysql_connection
    HAS_DB_CONNECTION = True
    print("✅ stats.py: 成功导入数据库连接")
except ImportError as e:
    HAS_DB_CONNECTION = False
    print(f"❌ stats.py: 无法导入数据库连接: {e}")

def get_empty_overview_stats():
    """返回空的概览统计数据"""
    return [
        {
            "title": "总调用次数",
            "value": "0",
            "trend": {"type": "up", "value": "+0%"},
            "sparkline": [0, 0, 0, 0, 0, 0, 0]
        },
        {
            "title": "活跃用户", 
            "value": "0",
            "trend": {"type": "up", "value": "+0%"},
            "sparkline": [0, 0, 0, 0, 0, 0, 0]
        },
        {
            "title": "在线人数",
            "value": "0",
            "trend": {"type": "down", "value": "-0%"}, 
            "sparkline": [0, 0, 0, 0, 0, 0, 0]
        },
        {
            "title": "游客人数",
            "value": "0",
            "trend": {"type": "up", "value": "+0%"},
            "sparkline": [0, 0, 0, 0, 0, 0, 0]
        }
    ]

@router.get("/overview")
async def get_overview():
    """获取数据概览"""
    if not HAS_DB_CONNECTION:
        return OverviewResponse(success=True, data=get_empty_overview_stats())
        
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            # 获取总用户数
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total_users = cursor.fetchone()['count']
            
            # 获取今日活跃用户数（今天有消息发送的用户）
            cursor.execute("""
                SELECT COUNT(DISTINCT cs.user_id) as count 
                FROM messages m 
                JOIN chat_sessions cs ON m.session_id = cs.id 
                WHERE DATE(m.created_at) = CURDATE()
            """)
            active_users_result = cursor.fetchone()
            active_users = active_users_result['count'] if active_users_result else 0
            
            # 获取总会话数
            cursor.execute("SELECT COUNT(*) as count FROM chat_sessions")
            total_chats = cursor.fetchone()['count']
            
            # 获取总消息数
            cursor.execute("SELECT COUNT(*) as count FROM messages")
            total_messages = cursor.fetchone()['count']
            
            # 获取今日消息趋势数据（最近7天）
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count 
                FROM messages 
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at) 
                ORDER BY date
            """)
            trend_data = cursor.fetchall()
            
            conn.close()
            
            # 处理趋势数据
            trend_counts = [item['count'] for item in trend_data]
            # 如果数据不足7天，补充0
            while len(trend_counts) < 7:
                trend_counts.append(0)
            
            # 计算趋势（简单比较最近两天）
            if len(trend_data) >= 2:
                today_count = trend_data[-1]['count'] if trend_data else 0
                yesterday_count = trend_data[-2]['count'] if len(trend_data) >= 2 else 0
                if yesterday_count > 0:
                    trend_percent = ((today_count - yesterday_count) / yesterday_count) * 100
                    trend_type = "up" if trend_percent >= 0 else "down"
                    trend_value = f"{'+' if trend_percent >= 0 else ''}{trend_percent:.1f}%"
                else:
                    trend_type = "up"
                    trend_value = "+0%"
            else:
                trend_type = "up"
                trend_value = "+0%"
            
            stats = [
                {
                    "title": "总调用次数",
                    "value": f"{total_messages:,}",
                    "trend": {"type": trend_type, "value": trend_value},
                    "sparkline": trend_counts[-7:]  # 取最近7天数据
                },
                {
                    "title": "活跃用户", 
                    "value": f"{active_users:,}",
                    "trend": {"type": "up", "value": "+0%"},  # 活跃用户趋势需要更复杂的计算
                    "sparkline": [max(0, int(x * 0.3)) for x in trend_counts[-7:]]
                },
                {
                    "title": "在线人数",
                    "value": "0",  # 在线人数需要实时统计，这里返回0
                    "trend": {"type": "down", "value": "-0%"}, 
                    "sparkline": [0, 0, 0, 0, 0, 0, 0]
                },
                {
                    "title": "游客人数",
                    "value": "0",  # 游客人数需要特殊统计，这里返回0
                    "trend": {"type": "up", "value": "+0%"},
                    "sparkline": [0, 0, 0, 0, 0, 0, 0]
                }
            ]
            
            return OverviewResponse(success=True, data=stats)
            
    except Exception as e:
        print(f"❌ 获取概览数据失败: {e}")
        return OverviewResponse(success=True, data=get_empty_overview_stats())

@router.get("/usage-trend")
async def get_usage_trend(range: str = "today"):
    """获取调用趋势"""
    if not HAS_DB_CONNECTION:
        return UsageTrendResponse(
            success=True,
            data={
                "hours": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "23:59"],
                "values": [0, 0, 0, 0, 0, 0, 0]
            }
        )
    
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            if range == "today":
                # 获取今天每4小时的消息数量
                hours = [f"{i:02d}:00" for i in range(0, 24, 4)]
                data = []
                
                for i in range(0, 24, 4):
                    hour_start = i
                    hour_end = i + 4
                    cursor.execute("""
                        SELECT COUNT(*) as count 
                        FROM messages 
                        WHERE DATE(created_at) = CURDATE() 
                        AND HOUR(created_at) >= %s 
                        AND HOUR(created_at) < %s
                    """, (hour_start, hour_end))
                    result = cursor.fetchone()
                    data.append(result['count'])
                
                conn.close()
                
                return UsageTrendResponse(
                    success=True,
                    data={
                        "hours": hours,
                        "values": data
                    }
                )
            else:
                # 其他时间范围返回全0数据
                return UsageTrendResponse(
                    success=True,
                    data={
                        "hours": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "23:59"],
                        "values": [0, 0, 0, 0, 0, 0, 0]
                    }
                )
                
    except Exception as e:
        print(f"❌ 获取使用趋势失败: {e}")
        return UsageTrendResponse(
            success=True,
            data={
                "hours": ["00:00", "04:00", "08:00", "12:00", "16:00", "20:00", "23:59"],
                "values": [0, 0, 0, 0, 0, 0, 0]
            }
        )
@router.get("/user-distribution")
async def get_user_distribution():
    """获取用户分布"""
    if not HAS_DB_CONNECTION:
        return UserDistributionResponse(success=True, data=[])
    
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            # 获取总用户数
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total_users = cursor.fetchone()['count']
            
            # 这里可以根据实际业务逻辑计算各种用户类型
            # 目前只返回注册用户，其他类型需要额外的业务逻辑
            distribution = [
                {"name": "注册用户", "value": total_users},
                {"name": "VIP用户", "value": 0},  # 需要VIP用户标识字段
                {"name": "游客", "value": 0},     # 需要游客统计逻辑
                {"name": "新用户", "value": 0}    # 需要新用户定义
            ]
            
            conn.close()
            return UserDistributionResponse(success=True, data=distribution)
            
    except Exception as e:
        print(f"❌ 获取用户分布失败: {e}")
        return UserDistributionResponse(success=True, data=[])

@router.get("/hot-questions")
async def get_hot_questions():
    """获取热门问题"""
    if not HAS_DB_CONNECTION:
        return HotQuestionsResponse(success=True, data=[])
    
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            # 修改查询，使用 DISTINCT 去重
            cursor.execute("""
                SELECT DISTINCT question_text as question, ask_count as count 
                FROM hot_questions 
                ORDER BY ask_count DESC 
                LIMIT 10
            """)
            hot_questions = cursor.fetchall()
            conn.close()
            
            return HotQuestionsResponse(success=True, data=hot_questions)
            
    except Exception as e:
        print(f"❌ 获取热门问题失败: {e}")
        return HotQuestionsResponse(success=True, data=[])
@router.get("/realtime")
async def get_realtime_data():
    """获取实时数据"""
    if not HAS_DB_CONNECTION:
        return RealtimeDataResponse(success=True, data=[])
    
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT m.id, m.role, m.content as message, m.created_at,
                       u.avatar_url as avatar
                FROM messages m
                LEFT JOIN chat_sessions cs ON m.session_id = cs.id
                LEFT JOIN users u ON cs.user_id = u.id
                ORDER BY m.created_at DESC
                LIMIT 5
            """)
            recent_messages = cursor.fetchall()
            conn.close()
            
            realtime_data = []
            for message in recent_messages:
                # 计算时间差
                time_diff = datetime.now() - message['created_at']
                minutes_ago = int(time_diff.total_seconds() / 60)
                
                if minutes_ago < 1:
                    time_text = "刚刚"
                elif minutes_ago < 60:
                    time_text = f"{minutes_ago}分钟前"
                else:
                    hours_ago = minutes_ago // 60
                    time_text = f"{hours_ago}小时前"
                
                realtime_data.append({
                    "id": message['id'],
                    "type": message['role'],
                    "avatar": message['avatar'] or "/src/assets/default_img.jpg",
                    "message": message['message'][:50] + "..." if len(message['message']) > 50 else message['message'],
                    "time": time_text
                })
            
            return RealtimeDataResponse(success=True, data=realtime_data)
            
    except Exception as e:
        print(f"❌ 获取实时数据失败: {e}")
        return RealtimeDataResponse(success=True, data=[])
@router.get("/hot-keywords")
async def get_hot_keywords(limit: int = 20):
    """获取热门关键词"""
    if not HAS_DB_CONNECTION:
        return {"success": True, "data": []}
    
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT keyword, heat_count 
                FROM hot_keywords 
                ORDER BY heat_count DESC, last_used DESC 
                LIMIT %s
            """, (limit,))
            keywords = cursor.fetchall()
            conn.close()
            
            return {
                "success": True,
                "data": keywords
            }
    except Exception as e:
        print(f"❌ 获取热门关键词失败: {e}")
        return {"success": True, "data": []}

@router.get("/question-categories")
async def get_question_categories():
    """获取问题分类统计"""
    if not HAS_DB_CONNECTION:
        return {"success": True, "data": []}
    
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT category, COUNT(*) as question_count, SUM(ask_count) as total_asks
                FROM hot_questions 
                WHERE category IS NOT NULL
                GROUP BY category 
                ORDER BY total_asks DESC
            """)
            categories = cursor.fetchall()
            conn.close()
            
            return {
                "success": True,
                "data": categories
            }
    except Exception as e:
        print(f"❌ 获取问题分类失败: {e}")
        return {"success": True, "data": []}

@router.get("/question-trends")
async def get_question_trends(days: int = 7):
    """获取问题趋势"""
    if not HAS_DB_CONNECTION:
        return {"success": True, "data": []}
    
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as new_questions, SUM(ask_count) as total_asks
                FROM hot_questions 
                WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY DATE(created_at) 
                ORDER BY date
            """, (days,))
            trends = cursor.fetchall()
            conn.close()
            
            return {
                "success": True,
                "data": trends
            }
    except Exception as e:
        print(f"❌ 获取问题趋势失败: {e}")
        return {"success": True, "data": []}
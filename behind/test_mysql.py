# test_mysql.py
import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # MySQL 配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '123456')  # 你的密码
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'chat')
    
    # 阿里云百炼配置
    ALIYUN_AI_KEY = os.getenv('ALIYUN_AI_KEY', 'sk-be95d529df6a4b428802f39ddfd25c52')
    ALIYUN_AI_ENDPOINT = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
    
    # JWT 配置
    JWT_SECRET = os.getenv('JWT_SECRET', 'ai-knowledge-assistant-secret-key-2024')
    JWT_ALGORITHM = 'HS256'
    
    # 应用配置
    DEBUG = os.getenv('DEBUG', True)

config = Config()

def test_mysql_connection():
    """测试MySQL数据库连接"""
    try:
        print("🔍 测试MySQL连接配置...")
        print(f"主机: {config.MYSQL_HOST}")
        print(f"端口: {config.MYSQL_PORT}")
        print(f"用户: {config.MYSQL_USER}")
        print(f"数据库: {config.MYSQL_DATABASE}")
        
        connection = pymysql.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        print("✅ MySQL连接成功")
        
        # 测试查询用户表
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            print(f"✅ 用户表数据: 找到 {len(users)} 个用户")
            for user in users:
                print(f"   - 用户: {user['username']}, ID: {user['id']}, 密码哈希: {user['password_hash']}")
        
        # 测试查询聊天会话表
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM chat_sessions")
            sessions = cursor.fetchall()
            print(f"✅ 聊天会话表: 找到 {len(sessions)} 个会话")
        
        # 测试查询消息表
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM messages")
            messages = cursor.fetchall()
            print(f"✅ 消息表: 找到 {len(messages)} 条消息")
        
        # 测试查询热门问题表
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM hot_questions")
            hot_questions = cursor.fetchall()
            print(f"✅ 热门问题表: 找到 {len(hot_questions)} 个热门问题")
        
        connection.close()
        print("✅ 所有数据库测试完成！")
        return True
        
    except pymysql.err.OperationalError as e:
        print(f"❌ MySQL操作错误: {e}")
        print("💡 可能的原因:")
        print("   - MySQL服务未启动")
        print("   - 用户名或密码错误") 
        print("   - 数据库不存在")
        print("   - 网络连接问题")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

def test_database_structure():
    """测试数据库表结构"""
    try:
        connection = pymysql.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # 检查所有表
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📊 数据库中的表: {[table['Tables_in_chat'] for table in tables]}")
            
            # 检查每个表的结构
            for table in tables:
                table_name = table['Tables_in_chat']
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                print(f"📋 表 {table_name} 的列:")
                for col in columns:
                    print(f"   - {col['Field']} ({col['Type']})")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ 数据库结构检查失败: {e}")

if __name__ == "__main__":
    print("🚀 开始数据库连接测试...")
    
    if test_mysql_connection():
        print("\n🔧 开始数据库结构测试...")
        test_database_structure()
        print("\n🎉 所有测试完成！数据库连接正常。")
    else:
        print("\n💥 数据库连接测试失败，请检查配置。")
        
        # 提供调试建议
        print("\n🔧 调试建议:")
        print("1. 检查MySQL服务是否运行: net start mysql81")
        print("2. 检查MySQL端口是否正确")
        print("3. 验证用户名和密码")
        print("4. 确认数据库 'chat' 是否存在")
        print("5. 检查防火墙设置")
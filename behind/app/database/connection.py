import pymysql
import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    # 尝试从项目根目录导入
    from config import config
    print("✅ 从根目录导入配置成功")
except ImportError:
    try:
        # 尝试从app目录导入
        from app.config import config
        print("✅ 从app目录导入配置成功")
    except ImportError as e:
        print(f"❌ 导入配置失败: {e}")
        # 创建临时配置
        class TempConfig:
            MYSQL_HOST = 'localhost'
            MYSQL_PORT = 3306
            MYSQL_USER = 'root'
            MYSQL_PASSWORD = '123456'
            MYSQL_DATABASE = 'chat'
            MYSQL_CHARSET = 'utf8mb4'
        
        config = TempConfig()
        print("⚠️ 使用临时配置")

def get_mysql_connection():
    """获取MySQL数据库连接"""
    try:
        print(f"🔧 连接数据库: host={config.MYSQL_HOST}, user={config.MYSQL_USER}")
        
        connection = pymysql.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            charset=config.MYSQL_CHARSET,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        print("✅ MySQL连接成功")
        return connection
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        raise e


def test_connection():
    """测试数据库连接"""
    try:
        conn = get_mysql_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("✅ 数据库连接测试成功！")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

if __name__ == "__main__":
    test_connection()
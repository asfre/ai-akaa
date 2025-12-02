import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # MySQL 配置
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '123456')  # 改成你的密码
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'chat')
    MYSQL_CHARSET = os.getenv('MYSQL_CHARSET', 'utf8mb4')
    
    # 阿里云百炼配置
    ALIYUN_AI_KEY = os.getenv('ALIYUN_AI_KEY', 'sk-be95d529df6a4b428802f39ddfd25c52')
    ALIYUN_AI_ENDPOINT = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
    ALIYUN_AI_MODEL = os.getenv('ALIYUN_AI_MODEL', 'qwen-turbo')  # 模型名称
    ALIYUN_AI_MAX_TOKENS = int(os.getenv('ALIYUN_AI_MAX_TOKENS', 2000))  # 最大token数
    
    # JWT 配置
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'ai-knowledge-assistant-secret-key-2024')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    
    # 应用配置
    DEBUG = os.getenv('DEBUG', True)

config = Config()
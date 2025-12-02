import dashscope
# import logging
# import json
import sys
import os


import sys
import os
import dashscope

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

try:
    # 尝试从根目录导入
    from config import config
    print("✅ ai_service.py: 从根目录导入配置成功")
except ImportError:
    try:
        # 尝试从app目录导入
        from app.config import config
        print("✅ ai_service.py: 从app目录导入配置成功")
    except ImportError as e:
        print(f"❌ ai_service.py: 导入配置失败: {e}")
        # 创建临时配置
        class TempConfig:
            ALIYUN_AI_KEY = 'sk-be95d529df6a4b428802f39ddfd25c52'
            ALIYUN_AI_MODEL = 'qwen-turbo'
            ALIYUN_AI_MAX_TOKENS = 2000
        
        config = TempConfig()
        print("⚠️ ai_service.py: 使用临时配置")

import logging

logger = logging.getLogger(__name__)



class AIService:
    def __init__(self):
        # 设置API Key
        dashscope.api_key = config.ALIYUN_AI_KEY
        self.model = config.ALIYUN_AI_MODEL
        self.max_tokens = config.ALIYUN_AI_MAX_TOKENS
    
    async def generate_response(self, question: str, chat_history: list = None) -> str:
        """
        生成AI回复
        
        Args:
            question: 用户问题
            chat_history: 聊天历史记录
            
        Returns:
            AI回复内容
        """
        try:
            # 构建消息列表
            messages = []
            
            # 系统提示词
            system_prompt = """你是一个专业的AI知识助理，专门帮助用户解答各种问题。请根据用户的问题提供准确、有用、友好的回答。
            
            回答要求：
            1. 保持专业、友好的语气
            2. 回答要准确、有条理
            3. 如果问题涉及专业领域，请提供详细的解释
            4. 如果不知道答案，请诚实地告知
            5. 避免生成有害、不当的内容
            
            请用中文回答用户的问题。"""
            
            messages.append({"role": "system", "content": system_prompt})
            
            # 添加历史对话（如果有）
            # if chat_history:
            #     for history in chat_history[-6:]:  # 只保留最近6轮对话，避免token超限
            #         messages.append({
            #             "role": history['role'],
            #             "content": history['content']
            #         })
            
            # 添加当前问题
            messages.append({"role": "user", "content": question})
            
            # 调用阿里云百炼API
            response = dashscope.Generation.call(
                model=self.model,
                messages=messages,
                result_format='message',  # 设置结果为message格式
                max_tokens=self.max_tokens,
                temperature=0.7,  # 控制创造性
                top_p=0.8
            )
            
            if response.status_code == 200:
                # 提取回复内容
                ai_response = response.output.choices[0].message.content
                logger.info(f"AI回复生成成功，长度: {len(ai_response)}")
                return ai_response.strip()
            else:
                error_msg = f"AI服务调用失败: {response.code} - {response.message}"
                logger.error(error_msg)
                return f"抱歉，AI服务暂时不可用。错误信息: {response.message}"
                
        except Exception as e:
            error_msg = f"AI服务调用异常: {str(e)}"
            logger.error(error_msg)
            return "抱歉，AI服务暂时不可用，请稍后重试。"
    
    def estimate_tokens(self, text: str) -> int:
        """
        粗略估算文本的token数量（中文大致按2个字符1个token估算）
        """
        return len(text) // 2

# 创建全局AI服务实例
ai_service = AIService()
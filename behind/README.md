# AI知识助理项目文档

![项目封面图（可选）](封面图路径)

# 📋 项目概述

AI知识助理是一个基于FastAPI构建的后端服务，提供用户认证、聊天会话管理、AI问答以及数据统计等功能。该项目使用MySQL数据库存储用户信息、聊天记录和统计数据，并集成了阿里云百炼平台的AI服务来生成智能回复。

# 📂 项目结构

```bash

.
├── app/
│   ├── api/                # API路由模块
│   ├── config/             # 配置文件
│   ├── database/           # 数据库连接和初始化脚本
│   ├── models/             # 数据模型定义
│   ├── routes/             # API路由实现
│   ├── services/           # 业务逻辑服务
│   ├── utils/              # 工具函数
│   └── main.py             # 应用入口文件
├── config.py               # 全局配置文件
├── run.py                  # 运行脚本
└── test_mysql.py           # 数据库测试脚本
```

# 🔧 核心功能模块

## 1. 用户认证模块

位于 `app/routes/auth.py`，提供以下功能：

- 用户登录验证

- 用户登出

- 修改密码

认证采用基于token的简单验证机制，实际生产环境中应使用JWT等更安全的认证方式。

## 2. 聊天会话模块

位于 `app/routes/chat.py`，提供以下功能：

- 获取聊天列表

- 创建新聊天会话

- 删除聊天会话

- 获取聊天消息历史

- 发送消息并接收AI回复

- 清空聊天记录

## 3. 数据统计模块

位于 `app/routes/stats.py`，提供以下功能：

- 获取系统概览数据（总调用次数、活跃用户等）

- 获取使用趋势数据

- 获取用户分布情况

- 获取热门问题列表

- 获取实时数据

- 获取热门关键词

- 获取问题分类统计

- 获取问题趋势

## 4. AI服务模块

位于 `app/services/ai_service.py`，集成了阿里云百炼平台的AI服务：

- 调用AI模型生成回复

- 管理API密钥和模型配置

- 处理聊天历史上下文

# 🗄️ 数据库设计

数据库初始化脚本位于 `app/database/database_init.sql`，包含以下主要表结构：

- **用户表 (users)**：存储用户基本信息，包括用户名、密码哈希、邮箱和头像URL。

- **聊天会话表 (chat_sessions)**：存储用户创建的聊天会话，关联用户ID，包含会话标题和活跃状态。

- **消息表 (messages)**：存储聊天消息，关联会话ID，区分用户消息和AI助手消息。

- **统计表 (statistics)**：存储系统统计数据，包括用户数、会话数、消息数等。

- **热门问题表 (hot_questions)**：记录用户提问频率高的问题，用于统计分析。

- **关键词热度表 (hot_keywords)**：记录关键词的使用热度。

- **问题分类表 (question_categories)**：对问题进行分类管理。

# 📡 API接口

## 认证相关接口

- POST /api/auth/login - 用户登录

- POST /api/auth/logout - 用户登出

- PUT /api/auth/password - 修改密码

## 聊天相关接口

- GET /api/chat/chats - 获取聊天列表

- POST /api/chat/chats - 创建新聊天

- DELETE /api/chat/chats/{chat_id} - 删除聊天

- GET /api/chat/chats/{chat_id}/messages - 获取聊天消息

- POST /api/chat/message - 发送消息

- DELETE /api/chat/chats/{chat_id}/messages - 清空聊天消息

## 统计相关接口

- GET /api/stats/overview - 获取数据概览

- GET /api/stats/usage-trend - 获取使用趋势

- GET /api/stats/user-distribution - 获取用户分布

- GET /api/stats/hot-questions - 获取热门问题

- GET /api/stats/realtime - 获取实时数据

- GET /api/stats/hot-keywords - 获取热门关键词

- GET /api/stats/question-categories - 获取问题分类统计

- GET /api/stats/question-trends - 获取问题趋势

- 接入真实的 AI 大模型 API，实现智能化服务；

- 引入数据库存储机制（如 IndexedDB 或远程服务器），持久化用户的对话记录；

- 支持多角色权限控制体系；

- 迁移到 Vue3 + TypeScript 技术栈，提升代码质量和可维护性；

- 增强系统的安全性、稳定性和响应速度；

- 扩展更多数据分析维度，增强可视化效果；

# ⚙️ 配置说明

项目配置包含以下关键参数：

- MySQL数据库连接信息（主机、端口、用户名、密码、数据库名）

- 阿里云AI服务密钥和模型配置

- CORS跨域配置

# 🚀 部署说明

## 安装依赖包

```bash

pip install fastapi uvicorn pymysql dashscope
```

## 配置数据库

1. 创建MySQL数据库

2. 执行 `app/database/database_init.sql` 初始化数据库表

## 配置环境

1. 设置阿里云API密钥

2. 配置数据库连接参数

## 启动服务

```bash

python run.py
```

# 🧱 技术选型概览

# 🔬 技术栈

|类别|技术栈|说明|
|---|---|---|
|后端框架|FastAPI|高性能异步API框架，自动生成接口文档|
|数据库|MySQL|存储用户、会话、消息及统计数据|
|AI服务|阿里云百炼平台|提供智能回复生成能力|
|异步支持|Python asyncio|提升服务并发处理能力|
|API文档|Swagger UI|FastAPI自动生成，便于接口调试|
|跨域支持|CORS中间件|解决前后端跨域访问问题|
# ⚠️ 安全注意事项

- 当前密码存储使用MD5哈希，生产环境应使用更安全的bcrypt等算法

- Token验证机制较为简单，建议使用JWT

- 需要添加输入验证和参数过滤，防止注入攻击

- 建议添加API限流机制防止滥用
> （注：文档部分内容可能由 AI 生成）
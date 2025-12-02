-- AI知识助理数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS `chat` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE `chat`;

-- 1. 用户表
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(50) UNIQUE NOT NULL COMMENT '用户名',
    `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
    `email` VARCHAR(100) COMMENT '邮箱',
    `avatar_url` VARCHAR(255) DEFAULT '/src/assets/default_img.jpg' COMMENT '头像URL',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 2. 聊天会话表
CREATE TABLE IF NOT EXISTS `chat_sessions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL COMMENT '用户ID',
    `title` VARCHAR(255) NOT NULL DEFAULT '新对话' COMMENT '会话标题',
    `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否活跃',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_user_id` (`user_id`),
    INDEX `idx_updated_at` (`updated_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='聊天会话表';

-- 3. 消息表
CREATE TABLE IF NOT EXISTS `messages` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `session_id` INT NOT NULL COMMENT '会话ID',
    `role` ENUM('user', 'assistant') NOT NULL COMMENT '消息角色',
    `content` TEXT NOT NULL COMMENT '消息内容',
    `token_count` INT DEFAULT 0 COMMENT 'token数量',
    `is_deleted` BOOLEAN DEFAULT FALSE COMMENT '是否删除',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (`session_id`) REFERENCES `chat_sessions`(`id`) ON DELETE CASCADE,
    INDEX `idx_session_id` (`session_id`),
    INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息表';

-- 4. 统计表
CREATE TABLE IF NOT EXISTS `statistics` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `stat_date` DATE NOT NULL UNIQUE COMMENT '统计日期',
    `total_users` INT DEFAULT 0 COMMENT '总用户数',
    `active_users` INT DEFAULT 0 COMMENT '活跃用户数',
    `total_chats` INT DEFAULT 0 COMMENT '总会话数',
    `total_messages` INT DEFAULT 0 COMMENT '总消息数',
    `online_users` INT DEFAULT 0 COMMENT '在线用户数',
    `guest_users` INT DEFAULT 0 COMMENT '游客数',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX `idx_stat_date` (`stat_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='统计表';

-- 5. 热门问题表
CREATE TABLE IF NOT EXISTS `hot_questions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `question_text` VARCHAR(500) NOT NULL COMMENT '问题内容',
    `ask_count` INT DEFAULT 1 COMMENT '提问次数',
    `last_asked_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '最后提问时间',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    INDEX `idx_ask_count` (`ask_count`),
    INDEX `idx_last_asked` (`last_asked_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='热门问题表';

-- 6. 关键词热度表
CREATE TABLE IF NOT EXISTS `hot_keywords` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `keyword` VARCHAR(50) NOT NULL UNIQUE COMMENT '关键词',
    `heat_count` INT DEFAULT 1 COMMENT '热度计数',
    `first_used_by` INT COMMENT '首次使用用户',
    `first_used_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '首次使用时间',
    `last_used_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后使用时间',
    INDEX `idx_heat_count` (`heat_count`),
    INDEX `idx_keyword` (`keyword`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='关键词热度表';

-- 7. 问题分类表
CREATE TABLE IF NOT EXISTS `question_categories` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(50) NOT NULL UNIQUE COMMENT '分类名称',
    `description` VARCHAR(200) COMMENT '分类描述',
    `question_count` INT DEFAULT 0 COMMENT '问题数量',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='问题分类表';

-- 修改热门问题表，增加新字段
ALTER TABLE `hot_questions` 
ADD COLUMN `processed_text` VARCHAR(500) COMMENT '处理后的文本',
ADD COLUMN `user_ask_count` INT DEFAULT 1 COMMENT '独立用户提问次数',
ADD COLUMN `first_asked_by` INT COMMENT '首次提问用户',
ADD COLUMN `category` VARCHAR(50) COMMENT '问题分类',
ADD COLUMN `avg_rating` DECIMAL(3,2) DEFAULT 5.00 COMMENT '平均评分',
ADD INDEX `idx_category` (`category`),
ADD INDEX `idx_user_ask_count` (`user_ask_count`);

-- 插入默认分类
INSERT IGNORE INTO `question_categories` (`name`, `description`) VALUES 
('技术', '编程、开发、技术相关问题'),
('学习', '学习方法、教程、入门指南'),
('概念', '概念解释、定义说明'),
('实践', '项目实践、案例分析'),
('其他', '其他类型问题');

-- 插入测试用户（密码已用 bcrypt 哈希处理，示例密码分别为: admin123 / user123）
INSERT IGNORE INTO `users` (`id`, `username`, `password_hash`, `email`) VALUES 
(1, 'admin', '$2b$12$SeYVGggnv9MiCyOHr3IA9.jN6aC6GFvGyfrdvZMImdb.XGt7zLsRO', 'admin@example.com'),
(2, 'user', '$2b$12$rQZgZhZs067gc/zJF5GJXeY6y72JD5v61ydvzq2IbId8ZrTZ3Hi6G', 'user@example.com');

-- 插入测试聊天会话
INSERT IGNORE INTO `chat_sessions` (`id`, `user_id`, `title`) VALUES 
(1, 1, '关于Vue3的问题'),
(2, 1, '学习人工智能'),
(3, 2, '项目开发讨论');

-- 插入测试消息
INSERT IGNORE INTO `messages` (`session_id`, `role`, `content`) VALUES 
-- 会话1的消息
(1, 'user', 'Vue3和Vue2有什么区别？'),
(1, 'assistant', 'Vue3引入了Composition API、更好的TypeScript支持、性能优化等新特性...'),
(1, 'user', '如何学习Vue3？'),
(1, 'assistant', '建议从官方文档开始，然后实践一些小项目...'),

-- 会话2的消息  
(2, 'user', '如何学习人工智能？'),
(2, 'assistant', '学习AI需要掌握数学基础、编程技能，然后逐步学习机器学习、深度学习...'),

-- 会话3的消息
(3, 'user', '项目开发需要注意什么？'),
(3, 'assistant', '项目开发需要注意代码规范、版本控制、测试和文档...');

-- 插入统计记录
INSERT IGNORE INTO `statistics` (`stat_date`, `total_users`, `active_users`, `total_chats`, `total_messages`, `online_users`, `guest_users`) VALUES 
(CURDATE(), 2, 1, 3, 7, 1, 0);

-- 插入热门问题
INSERT IGNORE INTO `hot_questions` (`question_text`, `ask_count`) VALUES 
('Vue3和Vue2有什么区别？', 15),
('如何学习Python编程？', 12),
('机器学习入门需要什么基础？', 8),
('React和Vue哪个更好？', 10),
('如何优化网站性能？', 6),
('前端框架怎么选择？', 5),
('数据库设计原则有哪些？', 7),
('如何部署Web项目？', 9),
('微服务架构是什么？', 4),
('Docker容器怎么使用？', 6);

-- 显示创建结果
SELECT '数据库初始化完成!' as '状态';

-- 显示各表记录数
SELECT 
    'users' as table_name, 
    COUNT(*) as record_count 
FROM `users`
UNION ALL
SELECT 
    'chat_sessions', 
    COUNT(*) 
FROM `chat_sessions`
UNION ALL
SELECT 
    'messages', 
    COUNT(*) 
FROM `messages`
UNION ALL
SELECT 
    'statistics', 
    COUNT(*) 
FROM `statistics`
UNION ALL
SELECT 
    'hot_questions', 
    COUNT(*) 
FROM `hot_questions`
UNION ALL
SELECT 
    'question_categories', 
    COUNT(*) 
FROM `question_categories`;
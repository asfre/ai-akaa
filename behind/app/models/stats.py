# app/models/stats.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, Enum, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import enum

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100))
    avatar_url = Column(String(255), default='/src/assets/default_img.jpg')
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class ChatSession(Base):
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), default='新对话')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class MessageRole(enum.Enum):
    USER = 'user'
    ASSISTANT = 'assistant'

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

class Statistics(Base):
    __tablename__ = 'statistics'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stat_date = Column(Date, nullable=False, unique=True)
    total_users = Column(Integer, default=0)
    active_users = Column(Integer, default=0)
    total_chats = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    online_users = Column(Integer, default=0)
    guest_users = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class HotQuestion(Base):
    __tablename__ = 'hot_questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(String(500), nullable=False)
    ask_count = Column(Integer, default=1)
    last_asked_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
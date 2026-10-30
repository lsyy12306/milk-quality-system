# -*- coding: utf-8 -*-
"""数据库 ORM 表模型：用户、分级历史、指标字典。"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(120), nullable=True)
    full_name = Column(String(120), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class GradeRecord(Base):
    __tablename__ = "grade_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    ph = Column(Float)
    temperature = Column(Float)
    taste = Column(Integer)
    odor = Column(Integer)
    fat = Column(Integer)
    turbidity = Column(Integer)
    colour = Column(Integer)
    predicted_grade = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), index=True, nullable=True)
    batch_no = Column(String(60), nullable=True)
    suggested_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Source(Base):
    """奶站/牧场来源档案（企业落地：优质优价追溯）。"""
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, index=True, nullable=False)
    source_type = Column(String(20), default="奶站")   # 奶站 / 牧场 / 合作社
    contact = Column(String(60), nullable=True)
    region = Column(String(120), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Indicator(Base):
    __tablename__ = "indicators"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(40), unique=True, index=True, nullable=False)
    name = Column(String(60), nullable=False)
    unit = Column(String(20), nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    description = Column(Text, nullable=True)


class UserPreference(Base):
    """用户偏好设置（Agent 记忆系统）。"""
    __tablename__ = "user_preferences"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    key = Column(String(60), nullable=False)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class AgentMessage(Base):
    """Agent 会话消息（多轮对话上下文）。"""
    __tablename__ = "agent_messages"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True, nullable=False)
    role = Column(String(20), nullable=False)   # 'user' / 'assistant' / 'system'
    content = Column(Text, nullable=False)
    tool_calls = Column(Text, nullable=True)    # JSON 序列化的工具调用记录
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

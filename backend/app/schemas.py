# -*- coding: utf-8 -*-
"""Pydantic 数据模型（请求/响应校验与序列化）。"""
from datetime import datetime
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """单条预测请求：7 项理化指标。"""
    ph: float = Field(..., ge=0, le=14, description="pH 值")
    temperature: float = Field(..., ge=0, le=100, description="温度 °C")
    taste: int = Field(..., ge=0, le=1, description="口感 0/1")
    odor: int = Field(..., ge=0, le=1, description="气味 0/1")
    fat: int = Field(..., ge=0, le=1, description="脂肪 0/1")
    turbidity: int = Field(..., ge=0, le=1, description="浑浊度 0/1")
    colour: int = Field(..., ge=0, le=255, description="颜色 0-255")


class PredictionResult(BaseModel):
    grade: str
    confidence: float
    probabilities: dict


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)
    email: str | None = None
    full_name: str | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None
    created_at: datetime | None = None
    model_config = {"from_attributes": True}


class GradeRecordOut(BaseModel):
    id: int
    ph: float
    temperature: float
    taste: int
    odor: int
    fat: int
    turbidity: int
    colour: int
    predicted_grade: str
    confidence: float
    created_at: datetime | None = None
    model_config = {"from_attributes": True}

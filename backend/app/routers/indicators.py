# -*- coding: utf-8 -*-
"""指标字典接口（前端录入表单的参考范围/说明）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from .. import models_db

router = APIRouter(prefix="/api/indicators", tags=["indicators"])


class IndicatorOut(BaseModel):
    key: str
    name: str
    unit: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    description: str | None = None
    model_config = {"from_attributes": True}


@router.get("", response_model=list[IndicatorOut])
def list_indicators(db: Session = Depends(get_db)):
    return db.query(models_db.Indicator).all()

# -*- coding: utf-8 -*-
"""来源档案接口：奶站 / 牧场 / 合作社的 CRUD（企业落地）。"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from .. import models_db

router = APIRouter(prefix="/api/sources", tags=["sources"])


class SourceIn(BaseModel):
    name: str
    source_type: str = "奶站"          # 奶站 / 牧场 / 合作社
    contact: str | None = None
    region: str | None = None
    note: str | None = None


@router.get("")
def list_sources(db: Session = Depends(get_db)):
    """来源列表（录入表单下拉用，无需鉴权）。"""
    return db.query(models_db.Source).order_by(models_db.Source.id).all()


@router.post("")
def create_source(s: SourceIn, current_user=Depends(get_current_user),
                  db: Session = Depends(get_db)):
    if db.query(models_db.Source).filter(models_db.Source.name == s.name).first():
        raise HTTPException(status_code=400, detail="来源名称已存在")
    src = models_db.Source(**s.model_dump())
    db.add(src)
    db.commit()
    db.refresh(src)
    return src


@router.put("/{source_id}")
def update_source(source_id: int, s: SourceIn, current_user=Depends(get_current_user),
                  db: Session = Depends(get_db)):
    src = db.query(models_db.Source).filter(models_db.Source.id == source_id).first()
    if not src:
        raise HTTPException(status_code=404, detail="来源不存在")
    for k, v in s.model_dump().items():
        setattr(src, k, v)
    db.commit()
    db.refresh(src)
    return src


@router.delete("/{source_id}")
def delete_source(source_id: int, current_user=Depends(get_current_user),
                  db: Session = Depends(get_db)):
    src = db.query(models_db.Source).filter(models_db.Source.id == source_id).first()
    if not src:
        raise HTTPException(status_code=404, detail="来源不存在")
    db.delete(src)
    db.commit()
    return {"ok": True}

# -*- coding: utf-8 -*-
"""用户注册 / 登录 / 个人中心。"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .. import schemas
from ..database import get_db
from .. import models_db
from ..auth import (
    hash_password, verify_password, create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut)
def register(u: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models_db.User).filter(models_db.User.username == u.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = models_db.User(
        username=u.username,
        hashed_password=hash_password(u.password),
        email=u.email, full_name=u.full_name,
    )
    db.add(user); db.commit(); db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(u: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models_db.User).filter(models_db.User.username == u.username).first()
    if not user or not verify_password(u.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


# ------------------------------------------------------------------ #
# 个人中心：查看资料 / 修改资料 / 修改密码（任务书 2.2.6）
# ------------------------------------------------------------------ #
class ProfileUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=schemas.UserOut)
def update_me(p: ProfileUpdate, current_user=Depends(get_current_user),
              db: Session = Depends(get_db)):
    if p.email is not None:
        current_user.email = p.email
    if p.full_name is not None:
        current_user.full_name = p.full_name
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/password")
def update_password(p: PasswordUpdate, current_user=Depends(get_current_user),
                    db: Session = Depends(get_db)):
    if not verify_password(p.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="原密码错误")
    if len(p.new_password) < 6:
        raise HTTPException(status_code=400, detail="新密码至少 6 位")
    current_user.hashed_password = hash_password(p.new_password)
    db.commit()
    return {"ok": True}

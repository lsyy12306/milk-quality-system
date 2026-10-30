# -*- coding: utf-8 -*-
"""FastAPI 应用入口：CORS、路由、启动初始化、前端静态托管。"""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .routers import predict, auth, history, indicators, model, agent, sources
from .database import init_db
from . import seed

# 前端构建产物目录（backend/../frontend/dist）
_DIST_DIR = (Path(__file__).resolve().parent.parent.parent / "frontend" / "dist").resolve()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed.seed()
    yield


app = FastAPI(title="牛奶品质分级系统 API", version="2.0.0", lifespan=lifespan)

# 开发期允许跨域（前端独立运行在不同端口）；生产应改为具体域名
# 说明：本项目用 Bearer Token 鉴权（非 Cookie），故关闭 credentials，
# 避免与 allow_origins=["*"] 冲突导致浏览器拦截。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router)
app.include_router(auth.router)
app.include_router(history.router)
app.include_router(indicators.router)
app.include_router(model.router)
app.include_router(agent.router)
app.include_router(sources.router)


@app.get("/")
def root():
    # 若已构建前端产物，则直接托管 SPA；否则返回 API 信息
    index = _DIST_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"name": "牛奶品质分级系统 API", "version": "2.0.0", "docs": "/docs"}


# 仅在存在构建产物时托管前端（不影响 /api/* 与 /docs）
if _DIST_DIR.exists():
    # 静态资源（JS/CSS/图片等）走精确前缀，不会与 /api 冲突
    _assets = _DIST_DIR / "assets"
    if _assets.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets)), name="assets")

    @app.get("/{full_path:path}")
    async def _spa_catch_all(full_path: str):
        # 兜底：已构建前端时，未知路径统一返回 index.html（React Router 前端路由）
        # /api 与 /docs 由更早注册的路由先行匹配，不会落入此处
        index = _DIST_DIR / "index.html"
        if index.exists() and not full_path.startswith("api/"):
            return FileResponse(index)
        raise HTTPException(status_code=404, detail="Not Found")

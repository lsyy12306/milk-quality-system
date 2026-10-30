# -*- coding: utf-8 -*-
"""Agent 智能体接口：分析、对话、趋势、报告、批量分析、企业日报。"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional
from .. import schemas
from ..database import get_db
from ..auth import get_current_user_optional, get_current_user
from .. import models_db
from ..agent.engine import AgentEngine
from ..agent.tools import ToolRegistry

router = APIRouter(prefix="/api/agent", tags=["agent"])


# ------------------------------------------------------------------ #
# 请求模型
# ------------------------------------------------------------------ #
class AgentAnalyzeRequest(BaseModel):
    """触发智能分析的请求（复用预测入参）。"""
    ph: float = Field(..., ge=0, le=14)
    temperature: float = Field(..., ge=0, le=100)
    taste: int = Field(..., ge=0, le=1)
    odor: int = Field(..., ge=0, le=1)
    fat: int = Field(..., ge=0, le=1)
    turbidity: int = Field(..., ge=0, le=1)
    colour: int = Field(..., ge=0, le=255)


class AgentChatRequest(BaseModel):
    """对话请求。"""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, max_length=64)


class AgentChatResponse(BaseModel):
    reply: str
    intent: str
    session_id: str


class AgentTrendRequest(BaseModel):
    days: int = Field(30, ge=1, le=365)


# ------------------------------------------------------------------ #
# 1. 智能分析（核心入口）
# ------------------------------------------------------------------ #
@router.post("/analyze")
def agent_analyze(req: AgentAnalyzeRequest,
                  current_user=Depends(get_current_user_optional),
                  db: Session = Depends(get_db)):
    """
    对单条样品执行完整的 Agent 智能分析：
    预测 → 根因分析 → 异常检测 → 改进建议 → 报告生成。
    """
    engine = AgentEngine(db=db)
    result = engine.analyze(
        ph=req.ph, temperature=req.temperature, taste=req.taste,
        odor=req.odor, fat=req.fat, turbidity=req.turbidity, colour=req.colour,
        user_id=current_user.id if current_user else None,
    )
    return result


# ------------------------------------------------------------------ #
# 2. 对话式交互
# ------------------------------------------------------------------ #
@router.post("/chat", response_model=AgentChatResponse)
def agent_chat(req: AgentChatRequest,
               current_user=Depends(get_current_user_optional),
               db: Session = Depends(get_db)):
    """与智能助手进行自然语言对话。"""
    import uuid
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:16]}"

    engine = AgentEngine(db=db)
    result = engine.chat(
        message=req.message,
        session_id=session_id,
        user_id=current_user.id if current_user else None,
    )
    return result


# ------------------------------------------------------------------ #
# 3. 趋势分析
# ------------------------------------------------------------------ #
@router.post("/trends")
def agent_trends(req: AgentTrendRequest = AgentTrendRequest(),
                 current_user=Depends(get_current_user),
                 db: Session = Depends(get_db)):
    """获取当前登录用户的品质趋势分析。"""
    engine = AgentEngine(db=db)
    return engine.get_trends(user_id=current_user.id, days=req.days)


# ------------------------------------------------------------------ #
# 4. 报告生成
# ------------------------------------------------------------------ #
@router.post("/report")
def agent_report(req: AgentAnalyzeRequest,
                 current_user=Depends(get_current_user_optional),
                 db: Session = Depends(get_db)):
    """生成完整的品质分析报告（Markdown）。"""
    engine = AgentEngine(db=db)
    analysis = engine.analyze(
        ph=req.ph, temperature=req.temperature, taste=req.taste,
        odor=req.odor, fat=req.fat, turbidity=req.turbidity, colour=req.colour,
        user_id=current_user.id if current_user else None,
    )
    return {
        "title": analysis["report"]["title"],
        "grade": analysis["prediction"]["grade"],
        "alert_level": analysis["report"]["alert_level"],
        "summary": analysis["report"]["summary"],
        "content": analysis["report"]["full_report"],
    }


# ------------------------------------------------------------------ #
# 5. 工具列表
# ------------------------------------------------------------------ #
@router.get("/tools")
def list_tools():
    """列出 Agent 支持的所有工具。"""
    registry = ToolRegistry()
    return {"tools": registry.list_tools()}


# ------------------------------------------------------------------ #
# 6. 批量智能分析
# ------------------------------------------------------------------ #
@router.post("/analyze/batch")
def agent_analyze_batch(records: list[AgentAnalyzeRequest],
                        current_user=Depends(get_current_user_optional),
                        db: Session = Depends(get_db)):
    """对多条记录执行批量智能分析。"""
    if len(records) > 50:
        raise HTTPException(status_code=400, detail="批量分析最多支持 50 条记录")

    engine = AgentEngine(db=db)
    rec_dicts = [r.model_dump() for r in records]
    return engine.analyze_batch(rec_dicts, user_id=current_user.id if current_user else None)


# ------------------------------------------------------------------ #
# 7. 会话历史
# ------------------------------------------------------------------ #
@router.get("/chat/history")
def chat_history(session_id: str,
                 current_user=Depends(get_current_user),
                 db: Session = Depends(get_db)):
    """获取指定会话的历史消息。"""
    engine = AgentEngine(db=db)
    return {"session_id": session_id, "messages": engine.memory.get_context(session_id)}


# ------------------------------------------------------------------ #
# 8. 企业质量日报（按日期汇总收购数据）
# ------------------------------------------------------------------ #
class DailyReportRequest(BaseModel):
    date: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD，默认今天")


@router.post("/daily-report")
def agent_daily_report(req: DailyReportRequest = DailyReportRequest(),
                       current_user=Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """生成企业质量日报：收购统计、等级分布、来源排名、定价汇总、异常预警。"""
    registry = ToolRegistry(db=db)
    return registry.call(
        "enterprise_daily_report",
        date=req.date,
        user_id=current_user.id,
    )

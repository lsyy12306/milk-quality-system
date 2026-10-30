# -*- coding: utf-8 -*-
"""Agent 记忆管理：用户偏好、历史上下文、会话状态。"""
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session
from .. import models_db


class AgentMemory:
    """简单记忆系统：基于数据库的用户偏好和会话上下文存储。"""

    def __init__(self, db: Session | None = None):
        self.db = db

    # ------------------------------------------------------------------ #
    # 用户偏好
    # ------------------------------------------------------------------ #
    def get_user_preference(self, user_id: int, key: str, default=None):
        """获取用户偏好设置。"""
        if not self.db:
            return default
        pref = self.db.query(models_db.UserPreference).filter(
            models_db.UserPreference.user_id == user_id,
            models_db.UserPreference.key == key,
        ).first()
        return pref.value if pref else default

    def set_user_preference(self, user_id: int, key: str, value: Any):
        """设置用户偏好。"""
        if not self.db:
            return
        pref = self.db.query(models_db.UserPreference).filter(
            models_db.UserPreference.user_id == user_id,
            models_db.UserPreference.key == key,
        ).first()
        if pref:
            pref.value = str(value)
            pref.updated_at = datetime.now(timezone.utc)
        else:
            self.db.add(models_db.UserPreference(
                user_id=user_id, key=key, value=str(value),
            ))
        self.db.commit()

    def get_common_preferences(self, user_id: int) -> dict:
        """获取用户的常用偏好设置。"""
        if not self.db:
            return {}
        prefs = self.db.query(models_db.UserPreference).filter(
            models_db.UserPreference.user_id == user_id,
        ).all()
        return {p.key: p.value for p in prefs}

    # ------------------------------------------------------------------ #
    # 会话上下文（用于多轮对话）
    # ------------------------------------------------------------------ #
    def get_context(self, session_id: str) -> list[dict]:
        """获取会话历史（最近 10 轮）。"""
        if not self.db:
            return []
        msgs = self.db.query(models_db.AgentMessage).filter(
            models_db.AgentMessage.session_id == session_id,
        ).order_by(models_db.AgentMessage.created_at).limit(10).all()
        return [{"role": m.role, "content": m.content, "tool_calls": m.tool_calls}
                for m in msgs]

    def add_message(self, session_id: str, role: str, content: str, tool_calls: str | None = None):
        """添加一条会话消息。"""
        if not self.db:
            return
        self.db.add(models_db.AgentMessage(
            session_id=session_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
        ))
        self.db.commit()

    def clear_context(self, session_id: str):
        """清空会话上下文。"""
        if not self.db:
            return
        self.db.query(models_db.AgentMessage).filter(
            models_db.AgentMessage.session_id == session_id,
        ).delete()
        self.db.commit()

    # ------------------------------------------------------------------ #
    # 统计洞察
    # ------------------------------------------------------------------ #
    def get_user_insights(self, user_id: int) -> dict:
        """基于用户历史数据生成个性化洞察。"""
        if not self.db:
            return {}

        from sqlalchemy import func

        total = self.db.query(func.count(models_db.GradeRecord.id)).filter(
            models_db.GradeRecord.user_id == user_id,
        ).scalar() or 0

        if total == 0:
            return {"has_history": False, "message": "暂无历史记录"}

        # 最常出现的问题指标
        records = self.db.query(models_db.GradeRecord).filter(
            models_db.GradeRecord.user_id == user_id,
        ).all()

        issue_counts = {"pH": 0, "Temperature": 0, "Taste": 0, "Odor": 0,
                        "Fat": 0, "Turbidity": 0, "Colour": 0}

        IDEAL = {
            "pH": (6.5, 6.8), "Temperature": (35.0, 45.0),
            "Taste": (1, 1), "Odor": (1, 1), "Fat": (1, 1),
            "Turbidity": (1, 1), "Colour": (250, 255),
        }

        for r in records:
            inputs = {"pH": r.ph, "Temperature": r.temperature, "Taste": r.taste,
                      "Odor": r.odor, "Fat": r.fat, "Turbidity": r.turbidity, "Colour": r.colour}
            for feat, (low, high) in IDEAL.items():
                if not (low <= inputs[feat] <= high):
                    issue_counts[feat] = issue_counts.get(feat, 0) + 1

        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        top_issues = [(k, v) for k, v in top_issues if v > 0][:3]

        return {
            "has_history": True,
            "total_records": total,
            "top_issues": top_issues,
            "focus_areas": [k for k, _ in top_issues],
            "personalized_tip": f"根据您的历史数据，建议重点关注 {'、'.join([k for k, _ in top_issues])} 指标。"
            if top_issues else "您的历史数据表现良好，请继续保持。",
        }

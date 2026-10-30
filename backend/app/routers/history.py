# -*- coding: utf-8 -*-
"""分级历史：查看（支持按批次筛选）与导出 CSV（支持按批次导出）。"""
import csv
import io
import re
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .. import schemas
from ..database import get_db
from ..auth import get_current_user
from .. import models_db

router = APIRouter(prefix="/api/history", tags=["history"])


def _group_key_of(r):
    """批次分组键：有批次号用批次号；否则按提交时间（精确到分钟）归组。"""
    if r.batch_no:
        return f"b:{r.batch_no}"
    return f"t:{r.created_at:%Y%m%d%H%M}"


def _group_label_of(r):
    if r.batch_no:
        return r.batch_no
    return f"手动预测 {r.created_at:%Y-%m-%d %H:%M}"


def _with_source(recs):
    """给记录附加来源名称（企业落地）与批次分组键。"""
    source_ids = {r.source_id for r in recs if r.source_id}
    sources = {}
    if source_ids:
        for s in recs_db_sources(source_ids):
            sources[s.id] = s.name
    out = []
    for r in recs:
        d = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        d["source_name"] = sources.get(r.source_id) if r.source_id else None
        d["batch_key"] = _group_key_of(r)
        d["batch_label"] = _group_label_of(r)
        out.append(d)
    return out


def recs_db_sources(ids):
    from ..database import SessionLocal
    db = SessionLocal()
    try:
        return db.query(models_db.Source).filter(models_db.Source.id.in_(ids)).all()
    finally:
        db.close()


@router.get("")
def list_history(current_user=Depends(get_current_user),
                 db: Session = Depends(get_db),
                 limit: int = 100, offset: int = 0):
    recs = (db.query(models_db.GradeRecord)
            .filter(models_db.GradeRecord.user_id == current_user.id)
            .order_by(desc(models_db.GradeRecord.created_at))
            .limit(limit).offset(offset).all())
    return _with_source(recs)


@router.get("/batches")
def list_batches(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    """返回批次列表（用于前端按批次筛选/导出）。"""
    recs = (db.query(models_db.GradeRecord)
            .filter(models_db.GradeRecord.user_id == current_user.id)
            .order_by(desc(models_db.GradeRecord.created_at)).all())
    groups, order = {}, []
    for r in recs:
        k = _group_key_of(r)
        if k not in groups:
            groups[k] = {"key": k, "label": _group_label_of(r),
                         "count": 0, "latest": r.created_at}
            order.append(k)
        groups[k]["count"] += 1
    return [groups[k] for k in order]


@router.get("/export")
def export_history(current_user=Depends(get_current_user),
                   db: Session = Depends(get_db),
                   batch: str | None = None):
    """导出 CSV。batch 为空导出全部；指定批次时只导出该批次。"""
    recs = (db.query(models_db.GradeRecord)
            .filter(models_db.GradeRecord.user_id == current_user.id)
            .order_by(desc(models_db.GradeRecord.created_at)).all())
    if batch:
        recs = [r for r in recs if _group_key_of(r) == batch]
    source_map = {s.id: s.name for s in
                  (db.query(models_db.Source).all() if any(r.source_id for r in recs) else [])}
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["id", "ph", "temperature", "taste", "odor", "fat",
                    "turbidity", "colour", "source", "batch_no",
                    "predicted_grade", "confidence", "suggested_price", "created_at"])
    for r in recs:
        writer.writerow([r.id, r.ph, r.temperature, r.taste, r.odor, r.fat,
                        r.turbidity, r.colour,
                        source_map.get(r.source_id, "") if r.source_id else "",
                        r.batch_no or "", r.predicted_grade, r.confidence,
                        r.suggested_price if r.suggested_price is not None else "",
                        r.created_at])
    # 文件名：指定批次时带上批次号（ASCII 安全 + UTF-8 扩展名双写）
    fname = "grade_history.csv"
    if batch:
        safe = re.sub(r"[^\w\-]", "", batch.removeprefix("b:").removeprefix("t:")) or "batch"
        fname = f"grade_history_{safe}.csv"
    return Response(
        content="\ufeff" + out.getvalue(),  # BOM 让 Excel 正确识别 UTF-8
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=\"{fname}\"",
            "Content-Disposition-Fallback": fname,
        },
    )

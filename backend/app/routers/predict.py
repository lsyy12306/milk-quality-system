# -*- coding: utf-8 -*-
"""预测接口：单条 /predict 与 CSV 批量 /predict/csv。

企业落地增强：
- 支持关联来源档案（source_id）与批次号（batch_no）
- 返回收购定价建议（优质优价，系数在 config.PRICE_FACTORS 可配置）
"""
import io
from datetime import datetime
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from .. import schemas
from ..ml_model import predict_single
from ..auth import get_current_user_optional
from ..database import get_db
from .. import models_db
from ..config import BASE_PRICE, PRICE_FACTORS, PRICE_ADVICE

router = APIRouter(prefix="/api", tags=["predict"])

# 输入列名兼容（原始数据集把 Temperature 拼成 Temprature）
_RENAME = {"temprature": "temperature"}
_REQUIRED = ["pH", "Temperature", "Taste", "Odor", "Fat", "Turbidity", "Colour"]


def _pricing(grade: str) -> dict:
    """按等级生成收购定价建议（优质优价）。"""
    factor = PRICE_FACTORS.get(grade, 1.0)
    price = round(BASE_PRICE * factor, 2)
    return {
        "base_price": BASE_PRICE,
        "factor": factor,
        "suggested_price": price,
        "advice": PRICE_ADVICE.get(grade, ""),
    }


@router.post("/predict")
def predict(req: schemas.PredictRequest,
            source_id: int | None = None,
            batch_no: str | None = None,
            current_user=Depends(get_current_user_optional),
            db: Session = Depends(get_db)):
    grade, confidence, probs = predict_single(
        req.ph, req.temperature, req.taste, req.odor, req.fat, req.turbidity, req.colour
    )
    pricing = _pricing(grade)
    # 登录用户自动落库历史；未填批次号时自动生成（便于按批次追溯/导出）
    if current_user is not None:
        if not batch_no:
            batch_no = datetime.now().strftime("B%Y%m%d-%H%M%S")
        db.add(models_db.GradeRecord(
            user_id=current_user.id, ph=req.ph, temperature=req.temperature,
            taste=req.taste, odor=req.odor, fat=req.fat, turbidity=req.turbidity,
            colour=req.colour, predicted_grade=grade, confidence=confidence,
            source_id=source_id, batch_no=batch_no,
            suggested_price=pricing["suggested_price"],
        ))
        db.commit()
    return {
        "grade": grade,
        "confidence": confidence,
        "probabilities": probs,
        "pricing": pricing,
    }


@router.post("/predict/csv")
async def predict_csv(file: UploadFile = File(...),
                      source_id: int | None = None,
                      current_user=Depends(get_current_user_optional),
                      db: Session = Depends(get_db)):
    content = await file.read()
    try:
        df = pd.read_csv(io.StringIO(content.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV 解析失败：{e}")

    # 列名清洗 + 兼容拼写（统一转小写再匹配）
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns={k: v for k, v in _RENAME.items() if k in df.columns})

    missing = [c for c in _REQUIRED if c not in df.columns and c.lower() not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"缺少必需列：{missing}")

    # 若 CSV 带 Source 列，按名称匹配来源档案（按行关联）
    source_map = {}
    src_col = next((c for c in ("Source", "source", "来源", "奶站", "牧场") if c in df.columns), None)
    if src_col:
        for s in db.query(models_db.Source).all():
            source_map[s.name] = s.id

    results, errors = [], []
    # 本次导入的自动批次号（CSV 内无批次列的行统一归入该批次）
    auto_batch = datetime.now().strftime("B%Y%m%d-%H%M%S")
    for i, row in df.iterrows():
        try:
            get = lambda k: row[k] if k in df.columns else row[k.lower()]
            grade, conf, probs = predict_single(
                float(get("pH")), float(get("Temperature")),
                int(get("Taste")), int(get("Odor")), int(get("Fat")),
                int(get("Turbidity")), int(get("Colour")),
            )
            pricing = _pricing(grade)
            batch_no = None
            for k in ("Batch", "batch", "批次", "批次号", "batch_no"):
                if k in df.columns and pd.notna(row[k]):
                    batch_no = str(row[k])
                    break
            if not batch_no:
                batch_no = auto_batch
            # 来源：优先 CSV 行内 Source 列，其次接口参数
            row_source_id = source_id
            if src_col and pd.notna(row[src_col]) and str(row[src_col]) in source_map:
                row_source_id = source_map[str(row[src_col])]
            results.append({
                "row": int(i) + 2,  # +2 = 去掉表头并从 1 开始
                "grade": grade, "confidence": conf, "probabilities": probs,
                "pricing": pricing,
                "batch_no": batch_no,
                "input": {k: (int(get(k)) if k in ("Taste", "Odor", "Fat", "Turbidity", "Colour") else float(get(k))) for k in _REQUIRED},
            })
            if current_user is not None:
                db.add(models_db.GradeRecord(
                    user_id=current_user.id, ph=float(get("pH")),
                    temperature=float(get("Temperature")), taste=int(get("Taste")),
                    odor=int(get("Odor")), fat=int(get("Fat")),
                    turbidity=int(get("Turbidity")), colour=int(get("Colour")),
                    predicted_grade=grade, confidence=conf,
                    source_id=row_source_id, batch_no=batch_no,
                    suggested_price=pricing["suggested_price"],
                ))
        except Exception as e:
            errors.append({"row": int(i) + 2, "error": str(e)})

    if current_user is not None:
        db.commit()
    return {"count": len(results), "results": results, "errors": errors}

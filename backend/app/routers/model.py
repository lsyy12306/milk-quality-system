# -*- coding: utf-8 -*-
"""模型信息接口：指标 / 性能 / 特征重要性（供前端可视化）。"""
import json
from pathlib import Path
from fastapi import APIRouter
from ..config import PROJECT_ROOT

router = APIRouter(prefix="/api/model", tags=["model"])


@router.get("/info")
def model_info():
    meta_path = PROJECT_ROOT / "models" / "model_metadata.json"
    meta = json.load(open(meta_path, encoding="utf-8"))
    return {
        "model_type": meta.get("model_type"),
        "n_samples": meta.get("n_samples"),
        "features": meta.get("features"),
        "class_order": meta.get("class_order"),
        "test_accuracy": meta.get("test_accuracy"),
        "test_macro_f1": meta.get("test_macro_f1"),
        "test_f1_per_class": meta.get("test_f1_per_class"),
        "feature_importance": meta.get("feature_importance"),
        "best_params": meta.get("best_params"),
        "correlation": meta.get("correlation"),
        "baseline_comparison": meta.get("baseline_comparison"),
    }

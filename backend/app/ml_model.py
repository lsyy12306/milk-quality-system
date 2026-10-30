# -*- coding: utf-8 -*-
"""加载已训练模型并提供单条预测。"""
import json
import joblib
from pathlib import Path
from .config import MODEL_PATH

_pipeline = None
_meta = None


def load_model():
    global _pipeline, _meta
    if _pipeline is None:
        _pipeline = joblib.load(MODEL_PATH)
        meta_path = MODEL_PATH.parent / "model_metadata.json"
        _meta = json.load(open(meta_path, encoding="utf-8"))
    return _pipeline, _meta


def predict_single(ph, temperature, taste, odor, fat, turbidity, colour):
    """输入 7 项指标，返回 (等级, 置信度, 各等级概率)。"""
    import pandas as pd
    pipe, meta = load_model()
    X = pd.DataFrame([{
        "pH": ph, "Temperature": temperature, "Taste": taste,
        "Odor": odor, "Fat": fat, "Turbidity": turbidity, "Colour": colour,
    }])
    pred_idx = int(pipe.predict(X)[0])
    proba = pipe.predict_proba(X)[0]
    grade = meta["class_order"][pred_idx]
    confidence = float(proba[pred_idx])
    probabilities = {meta["class_order"][i]: float(proba[i]) for i in range(len(meta["class_order"]))}
    return grade, confidence, probabilities

# -*- coding: utf-8 -*-
"""计算指标相关性矩阵 + 基线模型对比，写入 model_metadata.json"""
import json
import pandas as pd
from pathlib import Path

ROOT = Path(r"C:/Users/lishi/WorkBuddy/2026-10-15-10-05-25/milk-quality-system")
df = pd.read_csv(ROOT / "data/milk_quality.csv")
df.columns = [c.strip() for c in df.columns]
df = df.rename(columns={"Temprature": "Temperature"})

FEATURES = ["pH", "Temperature", "Taste", "Odor", "Fat", "Turbidity", "Colour"]

# 1) 相关性矩阵（含目标 Grade 数值化）
grade_map = {"low": 0, "medium": 1, "high": 2}
d = df[FEATURES].copy()
d["Grade"] = df["Grade"].map(grade_map)
corr = d.corr(method="pearson").round(4)
corr_dict = {
    "features": FEATURES + ["Grade"],
    "matrix": corr.values.tolist(),
}

# 2) 基线模型对比（与 01_explore_and_baseline.py 相同的流程复跑）
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score

X = df[FEATURES].copy()
y = df["Grade"].map(grade_map).values

X_tr, X_tmp, y_tr, y_tmp = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
X_va, X_te, y_va, y_te = train_test_split(X_tmp, y_tmp, test_size=0.5, stratify=y_tmp, random_state=42)

scaler = StandardScaler().fit(X_tr[["pH", "Temperature", "Colour"]])
def scale(frame):
    f = frame.copy()
    f[["pH", "Temperature", "Colour"]] = scaler.transform(f[["pH", "Temperature", "Colour"]])
    return f

results = []
dt = DecisionTreeClassifier(random_state=42, max_depth=6).fit(scale(X_tr), y_tr)
p = dt.predict(scale(X_te))
results.append({"model": "决策树 (DecisionTree)", "accuracy": round(accuracy_score(y_te, p), 4),
                "macro_f1": round(f1_score(y_te, p, average="macro"), 4)})

rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1).fit(scale(X_tr), y_tr)
p = rf.predict(scale(X_te))
results.append({"model": "随机森林 (RandomForest)", "accuracy": round(accuracy_score(y_te, p), 4),
                "macro_f1": round(f1_score(y_te, p, average="macro"), 4)})

xgb = XGBClassifier(max_depth=3, learning_rate=0.2, n_estimators=300,
                    subsample=0.8, colsample_bytree=0.8, random_state=42,
                    objective="multi:softprob", eval_metric="mlogloss").fit(scale(X_tr), y_tr)
p = xgb.predict(scale(X_te))
results.append({"model": "XGBoost（本系统）", "accuracy": round(accuracy_score(y_te, p), 4),
                "macro_f1": round(f1_score(y_te, p, average="macro"), 4)})

meta_path = ROOT / "models/model_metadata.json"
meta = json.load(open(meta_path, encoding="utf-8"))
meta["correlation"] = corr_dict
meta["baseline_comparison"] = {
    "note": "同一测试集（10%，stratified split, random_state=42）上的对比",
    "results": results,
}
json.dump(meta, open(meta_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("correlation (Grade row):", [round(v, 3) for v in corr.loc["Grade"].tolist()])
print("baseline comparison:")
for r in results:
    print(f"  {r['model']}: acc={r['accuracy']}, macroF1={r['macro_f1']}")
print("metadata updated:", meta_path)

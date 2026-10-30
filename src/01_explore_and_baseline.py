# -*- coding: utf-8 -*-
"""
步骤 1：探索性数据分析（EDA）+ XGBoost 基线可行性验证
========================================================
对应任务书：任务 2（数据清洗与特征工程）、任务 3（模型开发与训练）的第一步。

本脚本做四件事：
  1) 读取 milk_quality.csv，修正列名（原始数据有拼写/空格问题）
  2) 基础探查：形状、缺失值、类别分布、各特征分布
  3) 按 8:1:1 分层抽样划分 训练/验证/测试 集
  4) 训练 XGBoost 基线（含类别加权），并与决策树、随机森林对比，
     输出 总体准确率 + 各类别 F1 + 混淆矩阵，验证 85% 目标是否可达。

运行：
  .venvcn/Scripts/python src/01_explore_and_baseline.py
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # 无界面环境也能画图
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

import xgboost as xgb

# ---------- 路径 ----------
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA_PATH = os.path.join(ROOT, "data", "milk_quality.csv")
REPORT_DIR = os.path.join(ROOT, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

RANDOM_STATE = 42
TARGET = "Grade"
CLASS_ORDER = ["low", "medium", "high"]  # 固定编码顺序，保证前后一致

# 连续型特征（需要标准化）；其余为 0/1 二值质量标志或数值型颜色
CONTINUOUS = ["pH", "Temperature", "Colour"]


def load_and_clean(path):
    """读取并清洗数据：修正列名、去空格、统一类型。"""
    df = pd.read_csv(path)
    # 原始表头有问题：Temprature 拼写、'Fat ' 带尾随空格
    df.columns = [c.strip().replace("Temprature", "Temperature") for c in df.columns]
    df["Grade"] = df["Grade"].str.strip().str.lower()
    print(f"[读取] 形状={df.shape}")
    print(f"[列名] {list(df.columns)}")
    return df


def basic_eda(df):
    """打印基础探查结果。"""
    print("\n===== 1. 基础探查 =====")
    print("缺失值:\n", df.isnull().sum().to_string())
    print("\n各特征数据类型:\n", df.dtypes.to_string())

    print("\n类别分布 (Grade):")
    counts = df[TARGET].value_counts()
    for k in CLASS_ORDER:
        n = int(counts.get(k, 0))
        print(f"  {k:>6}: {n:>4}  ({n/len(df)*100:.1f}%)")

    print("\n各特征统计描述:")
    print(df.describe().round(3).to_string())

    # 二值特征的取值确认（任务书易踩坑点：Taste/Odor/Fat/Turbidity 是 0/1 标志）
    binary_cols = ["Taste", "Odor", "Fat", "Turbidity"]
    print("\n二值特征唯一取值 (应为 {0,1}):")
    for c in binary_cols:
        print(f"  {c}: {sorted(df[c].unique().tolist())}")


def make_splits(df):
    """8:1:1 分层抽样，返回 (X_train, X_val, X_test, y_train, y_val, y_test)。"""
    X = df.drop(columns=[TARGET]).copy()
    y = df[TARGET].copy()

    # 先拆出测试集（10%）
    X_tmp, X_test, y_tmp, y_test = train_test_split(
        X, y, test_size=0.1, stratify=y, random_state=RANDOM_STATE
    )
    # 剩余 90% 中再拆 验证集（占整体的 1/9 ≈ 11.1%，即 90%里的 ~12.5%）
    X_train, X_val, y_train, y_val = train_test_split(
        X_tmp, y_tmp, test_size=1 / 9, stratify=y_tmp, random_state=RANDOM_STATE
    )
    print("\n===== 2. 数据集划分 (8:1:1 分层抽样) =====")
    print(f"  训练集={len(X_train)}  验证集={len(X_val)}  测试集={len(X_test)}")
    return X_train, X_val, X_test, y_train, y_val, y_test


def prepare_features(X, fit_scaler=None):
    """对连续特征标准化；二值/颜色特征保持不变。返回 (X_proc, scaler)。"""
    Xp = X.copy()
    if fit_scaler is not None:
        scaler = fit_scaler
        Xp[CONTINUOUS] = scaler.transform(Xp[CONTINUOUS])
    else:
        scaler = StandardScaler()
        Xp[CONTINUOUS] = scaler.fit_transform(Xp[CONTINUOUS])
    return Xp, scaler


def evaluate(name, model, Xv, yv, yt, yp):
    """打印单个模型的验证/测试结果。yv/yp 为整数编码(0/1/2)。"""
    acc = accuracy_score(yv, yp)
    f1 = f1_score(yv, yp, labels=list(range(len(CLASS_ORDER))), average=None)
    print(f"\n--- {name} ---")
    print(f"  验证集准确率={acc:.4f}")
    print("  各类别 F1 (low/medium/high):", [round(x, 3) for x in f1])
    print("  混淆矩阵 (行=真实, 列=预测, 顺序 low/medium/high):")
    print(confusion_matrix(yv, yp, labels=list(range(len(CLASS_ORDER)))))
    return acc, f1


def main():
    df = load_and_clean(DATA_PATH)
    basic_eda(df)

    X_train, X_val, X_test, y_train, y_val, y_test = make_splits(df)

    # 只在训练集上拟合标准化器，避免数据泄漏
    Xtr, scaler = prepare_features(X_train)
    Xva, _ = prepare_features(X_val, scaler)
    Xte, _ = prepare_features(X_test, scaler)

    y_train_idx = y_train.map({k: i for i, k in enumerate(CLASS_ORDER)})
    y_val_idx = y_val.map({k: i for i, k in enumerate(CLASS_ORDER)})
    y_test_idx = y_test.map({k: i for i, k in enumerate(CLASS_ORDER)})

    print("\n===== 3. 模型训练与对比 =====")

    # --- 基线1：决策树 ---
    dt = DecisionTreeClassifier(random_state=RANDOM_STATE, max_depth=6)
    dt.fit(Xtr, y_train_idx)
    evaluate("决策树 (DecisionTree)", dt, Xva, y_val_idx, None, dt.predict(Xva))

    # --- 基线2：随机森林 ---
    rf = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE, n_jobs=-1)
    rf.fit(Xtr, y_train_idx)
    evaluate("随机森林 (RandomForest)", rf, Xva, y_val_idx, None, rf.predict(Xva))

    # --- 主模型：XGBoost（类别加权，应对样本不均衡）---
    counts = y_train_idx.value_counts().sort_index()
    total = len(y_train_idx)
    n_classes = len(CLASS_ORDER)
    weight_per_class = {i: total / (n_classes * counts[i]) for i in range(n_classes)}
    sample_weight = y_train_idx.map(weight_per_class).values

    clf = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="multi:softprob",  # 多分类概率输出；num_class 由数据自动推断
        eval_metric="mlogloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    clf.fit(Xtr, y_train_idx, sample_weight=sample_weight)
    val_pred = clf.predict(Xva)
    acc, f1 = evaluate("XGBoost (主模型)", clf, Xva, y_val_idx, None, val_pred)

    # --- 在测试集上给出最终报告 ---
    test_pred = clf.predict(Xte)
    print("\n===== 4. 测试集最终报告 (XGBoost) =====")
    print(classification_report(y_test_idx, test_pred, target_names=CLASS_ORDER, digits=3))
    test_acc = accuracy_score(y_test_idx, test_pred)
    test_f1_macro = f1_score(y_test_idx, test_pred, average="macro")
    print(f"测试集总体准确率={test_acc:.4f}  宏平均F1={test_f1_macro:.4f}")

    # 目标校验
    f1_arr = f1_score(y_test_idx, test_pred, labels=list(range(n_classes)), average=None)
    min_f1 = f1_arr.min()
    print(f"\n[目标校验] 总体准确率≥85%? {'达标' if test_acc >= 0.85 else '未达标'} ({test_acc*100:.1f}%)")
    print(f"[目标校验] 各类别F1≥0.80? {'达标' if min_f1 >= 0.80 else '未达标'} (最低={min_f1:.3f})")

    # 特征重要性
    imp = pd.Series(clf.feature_importances_, index=Xtr.columns).sort_values(ascending=False)
    print("\n特征重要性 (XGBoost):")
    print(imp.round(4).to_string())

    # 保存混淆矩阵图
    cm = confusion_matrix(y_test_idx, test_pred, labels=list(range(n_classes)))
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(n_classes)); ax.set_yticks(range(n_classes))
    ax.set_xticklabels(CLASS_ORDER); ax.set_yticklabels(CLASS_ORDER)
    ax.set_xlabel("预测"); ax.set_ylabel("真实")
    for i in range(n_classes):
        for j in range(n_classes):
            ax.text(j, i, cm[i, j], ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig_path = os.path.join(REPORT_DIR, "baseline_confusion_matrix.png")
    fig.savefig(fig_path, dpi=120)
    print(f"\n[保存] 混淆矩阵图 -> {fig_path}")

    print("\n===== 结论 =====")
    if test_acc >= 0.85 and min_f1 >= 0.80:
        print("✅ 可行性验证通过：XGBoost 在真实分布上轻松达到任务书指标，项目地基稳固。")
    else:
        print("⚠️ 未完全达标，需回到特征工程/调参环节（见任务 4）。")


if __name__ == "__main__":
    main()

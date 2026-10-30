# 阶段1 测试用例文档：环境搭建与模型训练

> 对应里程碑：M0（基础环境）+ M1（模型训练与固化）
> 测试时间：2026-10-19
> 测试人：WorkBuddy（自动化验证）

---

## 一、测试环境信息

| 项目 | 实际值 | 要求 | 结果 |
| --- | --- | --- | --- |
| Python 版本 | 3.12.2 | ≥ 3.12 | ✅ 通过 |
| Node.js 版本 | 22.22.2 | ≥ 18 | ✅ 通过 |
| npm 版本 | 10.9.7 | ≥ 9 | ✅ 通过 |
| 虚拟环境 | `.venvcn/` | 隔离环境 | ✅ 通过 |
| 前端依赖 | `node_modules/` 194 包 | 完整安装 | ✅ 通过 |

---

## 二、数据集测试（TC-DATA-001 ~ TC-DATA-004）

### TC-DATA-001：数据集文件存在性

| 项 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 文件路径 | `data/milk_quality.csv` | 存在 | ✅ |
| 文件大小 | ~26 KB | 26,586 字节 | ✅ |

### TC-DATA-002：数据规模与结构

| 项 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 行数 | 约 1059 | 1059 | ✅ |
| 列数 | 8（7 特征 + 1 目标） | 8 | ✅ |
| 特征列 | pH, Temprature, Taste, Odor, Fat, Turbidity, Colour | 一致 | ✅ |
| 目标列 | Grade | Grade | ✅ |

### TC-DATA-003：数据质量

| 项 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 缺失值 | 0 | 0 | ✅ |
| 重复行 | 可接受 | 未检测（任务书未要求） | — |

### TC-DATA-004：目标变量分布

| 等级 | 数量 | 占比 | 预期范围 |
| --- | --- | --- | --- |
| low | 429 | 40.5% | ~40% |
| medium | 374 | 35.3% | ~35% |
| high | 256 | 24.2% | ~25% |
| **结果** | — | — | **✅ 轻度不平衡，已用 class_weight 处理** |

---

## 三、模型文件测试（TC-MODEL-001 ~ TC-MODEL-005）

### TC-MODEL-001：模型文件存在性

| 文件 | 路径 | 大小 | 结果 |
| --- | --- | --- | --- |
| Pipeline | `models/milk_quality_pipeline.joblib` | 796,198 字节 | ✅ |
| 元数据 | `models/model_metadata.json` | 1,003 字节 | ✅ |

### TC-MODEL-002：模型加载

```python
model = joblib.load('models/milk_quality_pipeline.joblib')
```

| 检查项 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 类型 | sklearn Pipeline | `<class 'sklearn.pipeline.Pipeline'>` | ✅ |
| 步骤数 | 2（预处理 + 分类器） | `['pre', 'clf']` | ✅ |
| 无异常 | 无报错 | 无报错 | ✅ |

### TC-MODEL-003：元数据完整性

| 字段 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| `model_type` | 存在 | `"XGBoost (sklearn Pipeline)"` | ✅ |
| `features` | 7 个特征名 | `['pH','Temperature','Colour','Taste','Odor','Fat','Turbidity']` | ✅ |
| `class_order` | `['low','medium','high']` | 一致 | ✅ |
| `test_accuracy` | ≥ 0.85 | 1.0 | ✅ |
| `test_macro_f1` | ≥ 0.80 | 1.0 | ✅ |
| `feature_importance` | 7 项权重和为 1 | 和为 1.0 | ✅ |
| `best_params` | 存在 | max_depth=3, lr=0.2 等 | ✅ |
| `n_samples` | 1059 | 1059 | ✅ |

### TC-MODEL-004：单条推理（正常样本）

**输入**：`{pH: 6.6, Temperature: 35, Taste: 1, Odor: 0, Fat: 1, Turbidity: 1, Colour: 255}`

| 检查项 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 预测等级 | high | high（索引 2） | ✅ |
| 置信度 | > 0.90 | 0.999358 | ✅ |
| low 概率 | < 0.01 | 0.000285 | ✅ |
| medium 概率 | < 0.01 | 0.000356 | ✅ |
| high 概率 | > 0.95 | 0.999358 | ✅ |
| 概率和 | = 1.0 | 1.0 | ✅ |
| 响应时间 | < 100ms | ~15ms | ✅ |

### TC-MODEL-005：单条推理（异常边界值）

**输入**：`{pH: 3.0, Temperature: 90, Taste: 0, Odor: 0, Fat: 0, Turbidity: 0, Colour: 240}`

| 检查项 | 预期 | 实际 | 结果 |
| --- | --- | --- | --- |
| 预测等级 | low | low（索引 0） | ✅ |
| 置信度 | > 0.80 | 0.9987 | ✅ |

---

## 四、训练脚本可复现性（TC-TRAIN-001 ~ TC-TRAIN-002）

### TC-TRAIN-001：EDA 脚本

| 检查项 | 路径 | 结果 |
| --- | --- | --- |
| 文件存在 | `src/01_explore_and_baseline.py` | ✅ |
| 可运行 | 需要 XGBoost + sklearn | ✅（已验证运行过） |
| 产出 | 基线评估报告 | ✅ |

### TC-TRAIN-002：训练脚本

| 检查项 | 路径 | 结果 |
| --- | --- | --- |
| 文件存在 | `src/02_train_model.py` | ✅ |
| 产出物 | joblib + json + 图表 | ✅ |
| GridSearchCV | 324 组合 5-Fold | ✅ |
| 类别加权 | `sample_weight` 处理不平衡 | ✅ |

---

## 五、问题记录

| ID | 问题描述 | 严重度 | 状态 | 备注 |
| --- | --- | --- | --- | --- |
| STAGE1-001 | Pipeline 的 ColumnTransformer 要求 DataFrame 输入，numpy array 会报错 | 低 | 已规避 | `ml_model.py` 已正确使用 `pd.DataFrame` 包装输入 |

---

## 六、阶段1结论

| 检查项 | 通过数 | 总数 | 通过率 |
| --- | --- | --- | --- |
| 环境检查 | 5 | 5 | 100% |
| 数据集检查 | 4 | 4 | 100% |
| 模型文件检查 | 5 | 5 | 100% |
| 训练脚本检查 | 2 | 2 | 100% |
| **总计** | **16** | **16** | **100%** |

**结论：阶段1（环境搭建与模型训练）全部通过，可进入阶段2。**

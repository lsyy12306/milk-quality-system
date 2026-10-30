# API 接口文档（v2.1）

基础地址（开发期）：`http://127.0.0.1:8000`
完整交互式文档：`http://127.0.0.1:8000/docs`（Swagger UI）

通用约定：
- 请求/响应均为 `application/json`（文件上传除外）。
- 鉴权：除匿名预测外，需在 Header 携带 `Authorization: Bearer <token>`。
- 前端开发期由 Vite 代理把 `/api` 转发到后端，无需处理跨域。
- 接口总数：**23 个** `/api/*` 端点（v1.0 基础 8 个 + v2.0 Agent 7 个 + v2.1 企业与个人 8 个；另有 `GET /` 托管前端页面）。

## 接口总览

| # | 方法 | 路径 | 功能 | 鉴权 |
| --- | --- | --- | --- | --- |
| 1 | GET | `/` | 前端页面托管（构建后返回 SPA；无构建时返回 API 信息） | 否 |
| 2 | GET | `/api/indicators` | 7 项指标字典 | 否 |
| 3 | POST | `/api/predict` | 单条预测（含来源/批次/定价） | 可选 |
| 4 | POST | `/api/predict/csv` | CSV 批量预测（Source 列按行匹配） | 可选 |
| 5 | POST | `/api/auth/register` | 用户注册 | 否 |
| 6 | POST | `/api/auth/login` | 用户登录（返回 JWT） | 否 |
| 7 | GET | `/api/auth/me` | 查看个人资料 | 是 |
| 8 | PUT | `/api/auth/me` | 修改个人资料 | 是 |
| 9 | PUT | `/api/auth/password` | 修改密码 | 是 |
| 10 | GET | `/api/history` | 分级历史（含来源/批次/建议价） | 是 |
| 11 | GET | `/api/history/export` | 导出历史 CSV | 是 |
| 12 | GET | `/api/model/info` | 模型元数据 + 特征重要性 + 相关性矩阵 + 基线对比 | 否 |
| 13 | GET | `/api/sources` | 来源档案列表 | 否 |
| 14 | POST | `/api/sources` | 新建来源档案 | 是 |
| 15 | PUT | `/api/sources/{id}` | 修改来源档案 | 是 |
| 16 | DELETE | `/api/sources/{id}` | 删除来源档案 | 是 |
| 17 | POST | `/api/agent/analyze` | Agent 完整智能分析 | 可选 |
| 18 | POST | `/api/agent/chat` | 智能助手对话 | 可选 |
| 19 | POST | `/api/agent/daily-report` | 企业质量日报（默认最近有数据日期） | 是 |
| 20 | GET | `/api/agent/tools` | Agent 工具列表 | 否 |
| 21 | POST | `/api/agent/trends` | 品质趋势分析（近 N 天） | 是 |
| 22 | POST | `/api/agent/report` | 生成品质分析报告（Markdown） | 可选 |
| 23 | POST | `/api/agent/analyze/batch` | 批量智能分析（≤50 条） | 可选 |
| 24 | GET | `/api/agent/chat/history` | 会话历史消息 | 是 |

---

## 1. GET `/`
前端页面托管入口。
- 已构建前端（存在 `frontend/dist/`）时：返回 SPA `index.html`，`/assets/*` 托管静态资源，未知路径回退 `index.html`（支持前端路由）。
- 未构建时：返回 API 信息 `{"name": "牛奶品质分级系统 API", "version": "2.0.0", "docs": "/docs"}`。
- 交互式接口文档：`GET /docs`（Swagger UI）。

## 2. GET `/api/indicators`
获取 7 项指标字典（无需鉴权）。
- 响应 200：数组，元素含 `key/name/unit/min_value/max_value/description`。

## 3. POST `/api/predict`
单条预测（**匿名可用**；登录后自动写历史）。企业落地增强：支持关联来源、批次号，返回收购定价建议。
- 请求体：
```json
{
  "ph": 6.6,
  "temperature": 35,
  "taste": 1,
  "odor": 0,
  "fat": 1,
  "turbidity": 1,
  "colour": 255
}
```
- 查询参数（可选）：`source_id`（来源档案 ID）、`batch_no`（批次号）。
- 字段约束：`ph` 0–14；`temperature` 0–100；`taste/odor/fat/turbidity` 0/1；`colour` 0–255。
- 响应 200：
```json
{
  "grade": "high",
  "confidence": 0.999,
  "probabilities": { "low": 0.0003, "medium": 0.0004, "high": 0.999 },
  "pricing": {
    "base_price": 4.0,
    "factor": 1.15,
    "suggested_price": 4.6,
    "advice": "优质奶源，建议按优质优价机制优先收购"
  }
}
```
- 响应 422：字段缺失 / 越界（Pydantic 校验）。

## 4. POST `/api/predict/csv`
CSV 批量预测（**匿名可用**；登录后可写历史）。
- 请求：`multipart/form-data`，字段 `file` 为 CSV 文件；查询参数 `source_id`（可选，统一关联本批来源）。
- CSV 表头需含：`pH, Temperature, Taste, Odor, Fat, Turbidity, Colour`（列名大小写/拼写容错：`temprature`/`Temprature` 自动纠正）。
- 可选列：`Source`（来源名称，按行匹配档案）、`Batch`（批次号）。
- 响应 200：
```json
{
  "count": 3,
  "results": [
    {
      "row": 2, "grade": "high", "confidence": 0.998,
      "probabilities": { "low": 0.0001, "medium": 0.0002, "high": 0.9997 },
      "pricing": { "base_price": 4.0, "factor": 1.15, "suggested_price": 4.6, "advice": "优质奶源，建议按优质优价机制优先收购" },
      "batch_no": "B1021-A01"
    }
  ],
  "errors": [ { "row": 5, "error": "缺少必需列: Taste" } ]
}
```
- `row` 为文件中的实际行号（含表头，从 2 起计），便于定位问题。

## 5. POST `/api/auth/register`
用户注册。
- 请求体：`{"username": "alice", "password": "secret123", "email": "a@b.c", "full_name": "Alice"}`（email/full_name 选填）。
- 约束：username 3–50 字符；password ≥ 6 字符。
- 响应 200：`UserOut`（id/username/email/full_name/created_at）。
- 响应 400：用户名已存在。

## 6. POST `/api/auth/login`
用户登录，获取 JWT。
- 请求体：`{"username": "alice", "password": "secret123"}`
- 响应 200：`{"access_token": "<jwt>", "token_type": "bearer"}`
- 响应 401：用户名或密码错误。

## 7. GET `/api/auth/me`
查看当前登录用户资料（任务书 2.2.6 个人信息管理）。
- 响应 200：`UserOut`（id/username/email/full_name/created_at）。
- 响应 401：未登录 / token 无效。

## 8. PUT `/api/auth/me`
修改个人资料。
- 请求体：`{"full_name": "张三", "email": "zs@example.com"}`（均为选填，只更新传入字段）。
- 响应 200：更新后的 `UserOut`。

## 9. PUT `/api/auth/password`
修改密码。
- 请求体：`{"old_password": "secret123", "new_password": "newpass456"}`
- 约束：新密码 ≥ 6 位。
- 响应 200：`{"ok": true}`；响应 400：原密码错误 / 新密码过短。

## 10. GET `/api/history`
获取当前用户的分级历史（**需鉴权**），企业落地增强字段。
- 查询参数：`limit=100`（默认）、`offset=0`。
- 响应 200：数组，元素含 7 项指标 + `predicted_grade` + `confidence` + `source_name`（来源名称）+ `batch_no`（批次号）+ `suggested_price`（建议价）+ `created_at`。

## 11. GET `/api/history/export`
导出当前用户历史为 CSV（**需鉴权**）。
- 响应：带 UTF-8 BOM 的 `text/csv`，列含 `id/ph/temperature/taste/odor/fat/turbidity/colour/source/batch_no/predicted_grade/confidence/suggested_price/created_at`。

## 12. GET `/api/model/info`
模型元信息与性能（无需鉴权），供前端可视化。
- 响应 200：
```json
{
  "model_type": "XGBoost (sklearn Pipeline: StandardScaler + XGBClassifier)",
  "n_samples": 1059,
  "features": ["pH","Temperature","Colour","Taste","Odor","Fat","Turbidity"],
  "class_order": ["low","medium","high"],
  "test_accuracy": 1.0,
  "test_macro_f1": 1.0,
  "test_f1_per_class": {"low":1.0,"medium":1.0,"high":1.0},
  "feature_importance": {"Turbidity":0.274,"pH":0.200,"Fat":0.177,"Temperature":0.149,"Odor":0.084,"Taste":0.073,"Colour":0.044},
  "best_params": {"max_depth":3,"learning_rate":0.2,"n_estimators":300,"subsample":0.8,"colsample_bytree":0.8},
  "correlation": { "features": ["pH","Temperature","Taste","Odor","Fat","Turbidity","Colour","Grade"], "matrix": "8×8 Pearson 相关系数矩阵" },
  "baseline_comparison": {
    "note": "同一测试集（10%，stratified split, random_state=42）上的对比",
    "results": [
      {"model":"决策树 (DecisionTree)","accuracy":0.9434,"macro_f1":0.938},
      {"model":"随机森林 (RandomForest)","accuracy":0.9906,"macro_f1":0.9895},
      {"model":"XGBoost（本系统）","accuracy":1.0,"macro_f1":1.0}
    ]
  }
}
```

## 13. GET `/api/sources`
来源档案列表（录入表单下拉用，无需鉴权）。
- 响应 200：数组，元素含 `id/name/source_type/contact/region/note/created_at`。
- 种子数据：第一奶站、第二奶站、绿源牧场、康达合作社、润发牧场。

## 14. POST `/api/sources`
新建来源档案（**需鉴权**）。
- 请求体：`{"name": "第三奶站", "source_type": "奶站", "contact": "张站长 138****0006", "region": "城北区", "note": "新合作"}`（source_type：奶站/牧场/合作社，其余选填）。
- 响应 200：创建的来源对象；响应 400：名称已存在。

## 15. PUT `/api/sources/{id}`
修改来源档案（**需鉴权**）。请求体同 14；响应 404：来源不存在。

## 16. DELETE `/api/sources/{id}`
删除来源档案（**需鉴权**）。响应 200：`{"ok": true}`；响应 404：来源不存在。

## 17. POST `/api/agent/analyze`
对单条样品执行完整 Agent 分析：预测 → 根因分析 → 异常检测 → 改进建议 → 报告生成。
- 请求体同 `/api/predict`（7 项指标）。
- 响应 200：含 `prediction / root_cause / anomaly / suggestions / report / thinking_chain`（推理链 Step 1–5）。

## 18. POST `/api/agent/chat`
与智能助手对话。支持意图：`greeting / knowledge / trend / daily_report / analyze_request`。
- 请求体：`{"message": "生成今天的日报", "session_id": "sess_xxx"}`（session_id 选填，不传自动生成）。
- 响应 200：`{"reply": "...", "intent": "daily_report", "session_id": "sess_xxx"}`。
- 知识库覆盖 14 主题（pH/温度/口感/气味/脂肪/浑浊度/颜色/储存/乳腺炎/分级/提高品质/生产工艺/食品安全/污染掺假），无匹配时返回友好引导。

## 19. POST `/api/agent/daily-report`
生成企业质量日报（**需鉴权**）。
- 请求体：`{"date": "2026-10-23"}`（选填，格式 YYYY-MM-DD；**不传时默认取最近有收购记录的日期**，避免隔日打开无数据）。
- 响应 200：
```json
{
  "date": "2026-10-23",
  "records_count": 30,
  "grade_distribution": {"high": 19, "medium": 0, "low": 11},
  "suggested_total_price": 120.40,
  "anomaly_count": 11,
  "source_ranking": [
    {"source": "绿源牧场", "count": 5, "high_ratio": 100.0, "low_count": 0, "avg_price": 4.6}
  ],
  "content": "# 牛奶收购质量日报 · 2026-10-23\n...（完整 Markdown）",
  "summary": "2026-10-23 收购 30 条，优 19/中 0/差 11，建议总额 ¥120.40"
}
```

## 20. GET `/api/agent/tools`
列出 Agent 支持的所有工具（无需鉴权）。
- 响应 200：`{"tools": [{"name": "root_cause_analysis", "description": "..."}, ...]}`，共 7 个工具（含 `enterprise_daily_report`）。

## 21. POST `/api/agent/trends`
品质趋势分析（**需鉴权**），返回当前用户近 N 天的检测趋势。
- 请求体：`{"days": 30}`（`days` 选填，默认 30）。
- 响应 200：`{"records_count": ..., "trend": "稳定", "grade_distribution": {...}, "avg_confidence": ...}`。

## 22. POST `/api/agent/report`
生成完整品质分析报告（Markdown，**匿名可用**）。
- 请求体同 `/api/predict`（7 项指标）。
- 响应 200：`{"title": ..., "grade": "high", "alert_level": ..., "summary": ..., "content": "# 完整 Markdown"}`。

## 23. POST `/api/agent/analyze/batch`
对多条记录执行批量智能分析（**匿名可用**，上限 50 条，超出返回 400）。
- 请求体：7 项指标对象的数组，如 `[{"ph":6.7,"temperature":4,"taste":1,"odor":1,"fat":1,"turbidity":1,"colour":200}]`。
- 响应 200：逐条分析结果数组。

## 24. GET `/api/agent/chat/history`
获取指定会话的历史消息（**需鉴权**）。
- 查询参数：`session_id`（会话标识）。
- 响应 200：`{"session_id": "...", "messages": [...]}`。

---

## 错误码汇总

| 状态码 | 含义 |
| --- | --- |
| 200 | 成功 |
| 400 | 业务错误（如用户名已存在、原密码错误、CSV 缺列） |
| 401 | 未认证 / 用户名密码错误 |
| 404 | 资源不存在（如来源 ID 无效） |
| 422 | 请求字段校验失败（缺字段 / 越界） |
| 500 | 服务内部错误 |

---

*文档版本：V2.1.0 | 接口以 `/docs` Swagger 实时文档为准*

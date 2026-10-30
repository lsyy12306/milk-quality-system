# -*- coding: utf-8 -*-
"""
构建「牛奶品质分级系统」RAG 语料库。

输出：
  docs/rag_corpus.jsonl   每行一个 JSON 知识块，字段：
                          id, category, title, content, keywords, source, type
  docs/rag_corpus_readme.md  语料库说明与接入示例

用法：
  python src/build_rag_corpus.py
"""

import json
import os
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_JSONL = os.path.join(ROOT, "docs", "rag_corpus.jsonl")
OUT_README = os.path.join(ROOT, "docs", "rag_corpus_readme.md")

# type: "qa" 表示问答对，检索后可直接作为答案；"doc" 表示事实性知识块
CORPUS = [
    # ---------------- 项目概述 ----------------
    {
        "category": "项目概述",
        "title": "系统是什么",
        "type": "doc",
        "content": "牛奶品质分级系统是一套轻量级机器学习 Web 应用，基于公开的牛奶理化指标数据集，输入 7 项理化指标，自动输出牛奶品质等级（低/中/高，即 low/medium/high）及置信度，并提供历史记录与 CSV 批量处理能力。系统用于奶源收购与生产环节的品质初筛，不替代实验室食品安全检测。",
        "keywords": ["牛奶品质分级", "机器学习", "Web应用", "初筛", "品质等级"],
        "source": "02-PRD与项目说明.md",
    },
    {
        "category": "项目概述",
        "title": "项目背景与目标",
        "type": "doc",
        "content": "乳制品行业中，奶源品质的初步分级直接关系到收购定价与生产调度。传统分级依赖人工经验，效率低且标准不统一。本项目目标：用机器学习模型对牛奶品质做三级自动分级，准确率 ≥ 85%，各类别 F1 ≥ 0.80。实测测试集准确率 100%、各类别 F1 均为 1.00，远超任务书底线。",
        "keywords": ["背景", "目标", "准确率", "F1", "85%", "任务书"],
        "source": "02-PRD与项目说明.md",
    },
    {
        "category": "项目概述",
        "title": "技术栈总览",
        "type": "doc",
        "content": "本项目技术栈：算法/模型用 Python 3.12 + scikit-learn Pipeline + XGBoost；后端用 FastAPI + Uvicorn + SQLAlchemy 2.0 + Pydantic v2 + PyJWT + bcrypt；前端用 React 18 + Vite 5 + Ant Design 5 + react-router-dom 6 + recharts + axios；数据库用 SQLite 3（通过 SQLAlchemy）。前后端分离，模型以 joblib 打包。",
        "keywords": ["技术栈", "FastAPI", "React", "Ant Design", "XGBoost", "SQLite", "Vite"],
        "source": "03-系统架构与数据库设计.md",
    },
    {
        "category": "项目概述",
        "title": "目录结构",
        "type": "doc",
        "content": "milk-quality-system/ 目录：data/（数据集 milk_quality.csv、测试批次 test_batch.csv）；src/（训练/EDA 脚本 01_*、02_train_model.py、build_rag_corpus.py）；models/（milk_quality_pipeline.joblib + model_metadata.json）；reports/（评估报表、混淆矩阵、特征重要性图）；backend/（FastAPI 应用，含 milk_quality.db）；frontend/（React 应用）；docs/（项目交付文档）。",
        "keywords": ["目录结构", "data", "src", "models", "backend", "frontend", "docs"],
        "source": "03-系统架构与数据库设计.md",
    },
    {
        "category": "项目概述",
        "title": "核心功能列表",
        "type": "doc",
        "content": "系统核心功能：F1 单条预测（7 项指标→等级+置信度+三分类概率）；F2 CSV 批量预测（两步预览确认，Source 列按行匹配来源）；F3 用户鉴权（注册/登录，Bearer Token，匿名也可预测）；F4 历史记录（含来源、批次号、建议价）；F5 历史导出（带 UTF-8 BOM 的 CSV）；F6 指标字典；F7 模型信息（含特征重要性、相关性矩阵、基线对比）；F8 Agent 智能体（根因分析/改进建议/趋势/异常检测/报告/知识问答/企业日报）；F9 奶源来源档案（奶站/牧场管理）；F10 优质优价定价建议；F11 企业质量日报；F12 个人中心（资料编辑+修改密码）。",
        "keywords": ["功能", "单条预测", "CSV批量", "历史记录", "指标字典", "模型信息", "Agent", "来源档案", "定价", "企业日报", "个人中心"],
        "source": "02-PRD与项目说明.md / 14-企业落地增强说明.md",
    },
    {
        "category": "项目概述",
        "title": "目标用户",
        "type": "doc",
        "content": "目标用户：奶站/收奶点的品质初筛员；乳制品企业的品控与调度人员；课程作业/原型演示场景下的学习者。非范围（明确不做）：食品安全实验室检测（掺假/抗生素/微生物）、物联网实时采集、多租户与企业级权限。",
        "keywords": ["目标用户", "品控", "初筛员", "学习", "非范围"],
        "source": "02-PRD与项目说明.md",
    },

    # ---------------- 数据 ----------------
    {
        "category": "数据",
        "title": "数据来源与溯源",
        "type": "doc",
        "content": "数据集名称 Milk Quality Prediction，来源平台 Kaggle，发布者 cpluzshrijayan，地址 https://www.kaggle.com/datasets/cpluzshrijayan/milkquality，数据文件 milknew.csv（约 26.59 kB），8 列（7 自变量+1 目标），样本量 1059 行。本项目 data/milk_quality.csv 即从该 Kaggle 数据集的 milknew.csv 经 GitHub 镜像下载获取，字段数、样本量、目标分布完全一致。",
        "keywords": ["数据来源", "Kaggle", "cpluzshrijayan", "milknew.csv", "1059", "溯源"],
        "source": "01-数据来源与数据字典.md",
    },
    {
        "category": "数据",
        "title": "数据授权声明",
        "type": "qa",
        "question": "这个数据集可以商用吗？授权协议是什么？",
        "content": "数据集授权协议为 Unknown（未知）。本项目将其用于学习/课程作业/原型演示目的；若用于商业发布或对外分发，须自行向数据发布者确认授权，或替换为自有/已授权数据。这是本项目明确标注的合规风险点，商用前必须处理。",
        "answer": "Kaggle 页面标注 License = Unknown（未知）。可用于学习/作业/演示；商用或分发前须向发布者确认授权，或换用自有/已授权数据。",
        "keywords": ["授权", "License", "Unknown", "商用", "合规", "Kaggle"],
        "source": "01-数据来源与数据字典.md",
    },
    {
        "category": "数据",
        "title": "字段说明与取值域",
        "type": "doc",
        "content": "7 个自变量与 1 个目标：pH 连续，3.0–9.5（实际多 6.25–6.90），标准化参与建模；Temperature 连续，34–90°C（实际多 34–45.20），标准化；Taste 二值 0=差/1=好，直通；Odor 二值 0=差/1=好，直通；Fat 二值 0=低/1=高，直通；Turbidity 二值 0=低/1=高，直通；Colour 连续整数 240–255，标准化；Grade 类别目标 low(差)/medium(一般)/high(优)。",
        "keywords": ["字段", "pH", "Temperature", "Taste", "Odor", "Fat", "Turbidity", "Colour", "Grade", "取值域"],
        "source": "01-数据来源与数据字典.md",
    },
    {
        "category": "数据",
        "title": "温度列拼写笔误与容错",
        "type": "qa",
        "question": "为什么温度列有时叫 Temprature？上传 CSV 报缺少列怎么办？",
        "content": "原始数据中温度列拼写为 Temprature（少一个 e），属数据本身笔误。本项目在数据清洗阶段统一修正为 Temperature，并在 CSV 批量预测接口做容错：自动把 temprature / Temprature 等变体清洗为标准名 Temperature，避免用户上传原始文件时报「缺少列」。后端接口与前端表单统一使用小写 temperature。",
        "answer": "原始数据拼写就是 Temprature（少 e），是笔误。系统已自动容错：清洗和 CSV 接口都会把 Temprature/temprature 纠正为 Temperature，上传原始文件不会报错。",
        "keywords": ["Temprature", "Temperature", "拼写", "笔误", "容错", "CSV列名"],
        "source": "01-数据来源与数据字典.md",
    },
    {
        "category": "数据",
        "title": "目标变量取值分布",
        "type": "doc",
        "content": "目标变量 Grade 取值 low/medium/high，分布约为 low 40.5%、medium 35.3%、high 24.2%（约 256 条）。存在轻度类别不平衡（low:medium:high ≈ 41:35:24），已由模型端 class_weight 处理。",
        "keywords": ["Grade", "分布", "low", "medium", "high", "类别不平衡"],
        "source": "01-数据来源与数据字典.md",
    },
    {
        "category": "数据",
        "title": "数据质量与业务语义",
        "type": "doc",
        "content": "数据质量：无缺失值（Kaggle 声明 + 本项目 EDA 双重确认）；轻度类别不平衡已用类别加权缓解。业务语义：当 Taste、Odor、Fat、Turbidity 均满足最优条件（取值为 1）时，牛奶更可能被评 high；任一为 0 会拉低等级。pH 与 Temperature 为实际测量连续值，其余四项为合格/不合格式质量标志。数据用途边界：仅用于品质初筛模型训练与演示，不覆盖食品安全核心检测（掺假、抗生素残留、微生物）。",
        "keywords": ["数据质量", "缺失值", "业务语义", "食品安全", "使用边界"],
        "source": "01-数据来源与数据字典.md",
    },

    # ---------------- 模型 ----------------
    {
        "category": "模型",
        "title": "模型类型与结构",
        "type": "doc",
        "content": "模型为 XGBoost 多分类：使用 scikit-learn Pipeline 包装 StandardScaler + XGBClassifier，objective=multi:softprob，class_order=[low, medium, high]。Pipeline 整体保存为 models/milk_quality_pipeline.joblib，预测时一次载入、一次推理，避免线上线下预处理不一致。StandardScaler 仅作用于连续特征 pH/Temperature/Colour，二值特征直通。",
        "keywords": ["XGBoost", "Pipeline", "StandardScaler", "XGBClassifier", "multi:softprob", "joblib"],
        "source": "03-系统架构与数据库设计.md",
    },
    {
        "category": "模型",
        "title": "训练与调参方法",
        "type": "doc",
        "content": "训练脚本 02_train_model.py：先做 8:1:1 分层切分，再用 GridSearchCV（5 折分层，约 324 组超参组合）搜索最优超参，并用类别加权（class_weight / sample_weight）缓解轻度不平衡。最佳参数：max_depth=3, learning_rate=0.2, n_estimators=300, subsample=0.8, colsample_bytree=0.8。交叉验证宏 F1=0.9976。",
        "keywords": ["GridSearchCV", "分层", "类别加权", "超参", "best_params", "训练"],
        "source": "04-API接口文档.md / 05-系统测试报告.md",
    },
    {
        "category": "模型",
        "title": "模型性能与达标情况",
        "type": "qa",
        "question": "模型准确率是多少？达到任务书要求了吗？",
        "content": "测试集准确率实测 100.0%，宏平均 F1=1.000，各类别（low/medium/high）F1 均为 1.000，交叉验证宏 F1=0.9976。任务书要求准确率 ≥ 85%、各类别 F1 ≥ 0.80，均已大幅达标。该数据集线性可分度很高，工程重点已从「达标」转为「工程完整性与文档交付」。",
        "answer": "测试集准确率 100%、宏 F1 1.0、各类别 F1 均 1.0，远超任务书要求的 85% 准确率与 0.80 F1。",
        "keywords": ["准确率", "F1", "性能", "达标", "测试集", "100%"],
        "source": "02-PRD与项目说明.md / 05-系统测试报告.md",
    },
    {
        "category": "模型",
        "title": "特征重要性排序",
        "type": "doc",
        "content": "XGBoost 特征重要性（增益口径）排序：Turbidity(0.274) > pH(0.200) > Fat(0.177) > Temperature(0.149) > Odor(0.084) > Taste(0.073) > Colour(0.044)。浑浊度与 pH 对分级影响最大，Colour（颜色）影响最小。该排名通过 /api/model/info 暴露，前端「模型与特征」页用水平柱状图可视化。",
        "keywords": ["特征重要性", "Turbidity", "pH", "Fat", "可视化", "feature_importance"],
        "source": "04-API接口文档.md / 01-数据来源与数据字典.md",
    },
    {
        "category": "模型",
        "title": "如何替换/更新模型",
        "type": "qa",
        "question": "怎么更换模型或重新训练？需要改代码吗？",
        "content": "重新训练：运行 src/02_train_model.py 会生成新的 models/milk_quality_pipeline.joblib 与 model_metadata.json。部署更新：仅需替换这两个文件后重启后端 uvicorn 即可，无需改代码。注意 class_order 与 features 顺序必须与 Pipeline 训练时一致，metadata 中的 features 列表顺序即模型期望的输入顺序。",
        "answer": "重新训练运行 02_train_model.py；上线只需替换 models/ 下两个文件并重启后端，无需改代码。",
        "keywords": ["替换模型", "重新训练", "更新", "joblib", "metadata", "重启"],
        "source": "03-系统架构与数据库设计.md / 06-部署手册.md",
    },

    # ---------------- 后端 ----------------
    {
        "category": "后端",
        "title": "后端接口清单",
        "type": "doc",
        "content": "后端 FastAPI 共 20 个接口（v2.1）：GET / 根信息；GET /api/indicators 指标字典；POST /api/predict 单条预测（含 source_id/batch_no 参数与 pricing 返回，匿名可用）；POST /api/predict/csv CSV 批量（Source 列按行匹配来源，匿名可用）；POST /api/auth/register 注册；POST /api/auth/login 登录取 JWT；GET/PUT /api/auth/me 查看/修改个人资料；PUT /api/auth/password 修改密码；GET /api/history 历史（含 source_name/batch_no/suggested_price）；GET /api/history/export 导出 CSV；GET /api/model/info 模型信息（含相关性矩阵、基线对比）；GET /api/sources 来源列表；POST/PUT/DELETE /api/sources 来源 CRUD（需登录）；POST /api/agent/analyze 智能分析；POST /api/agent/chat 对话；POST /api/agent/daily-report 企业日报（需登录）；GET /api/agent/tools 工具列表。完整交互文档见 http://127.0.0.1:8000/docs（Swagger）。",
        "keywords": ["后端", "接口", "FastAPI", "端点", "Swagger", "docs", "20接口", "来源", "日报", "个人中心"],
        "source": "04-API接口文档.md",
    },
    {
        "category": "后端",
        "title": "单条预测接口 /api/predict",
        "type": "doc",
        "content": "POST /api/predict 单条预测，匿名可用，登录后自动写历史。请求体字段（小写蛇形）：ph(0–14 浮点)、temperature(0–100 浮点)、taste(0/1 整数)、odor(0/1 整数)、fat(0/1 整数)、turbidity(0/1 整数)、colour(0–255 整数)。响应 200：{grade, confidence, probabilities:{low,medium,high}}。示例输入 {ph:6.6,temperature:35,taste:1,odor:0,fat:1,turbidity:1,colour:255} → grade:high, confidence:0.999。字段缺失或越界返回 422（Pydantic 校验）。",
        "keywords": ["predict", "单条预测", "请求体", "字段约束", "422", "示例"],
        "source": "04-API接口文档.md",
    },
    {
        "category": "后端",
        "title": "CSV 批量预测接口 /api/predict/csv",
        "type": "doc",
        "content": "POST /api/predict/csv，multipart/form-data，字段 file 为 CSV。CSV 表头需含 pH, Temperature, Taste, Odor, Fat, Turbidity, Colour（列名大小写/拼写容错：temprature/Temprature 自动纠正）。响应 200：{count, results:[{row,grade,confidence}], errors:[{row,error}]}。row 为文件中实际行号（含表头从 2 起计），便于定位问题行。匿名可用，登录后可写历史。",
        "keywords": ["CSV", "批量", "predict/csv", "UploadFile", "row", "errors", "表头"],
        "source": "04-API接口文档.md",
    },
    {
        "category": "后端",
        "title": "鉴权机制 JWT 与匿名预测",
        "type": "doc",
        "content": "鉴权：注册/登录返回 PyJWT 短时 Bearer Token；除匿名预测外，需在 Header 携带 Authorization: Bearer <token>。/api/predict 与 /api/predict/csv 使用 auto_error=False 的可选鉴权：未登录也能分级，登录后自动把记录 user_id 写入历史（匿名则 user_id 为 NULL），兼顾易用与隐私。前端 axios 拦截 401 自动跳登录。",
        "keywords": ["JWT", "Bearer", "匿名预测", "鉴权", "auto_error", "user_id"],
        "source": "03-系统架构与数据库设计.md / 04-API接口文档.md",
    },
    {
        "category": "后端",
        "title": "数据库设计与表结构",
        "type": "doc",
        "content": "数据库 SQLite（backend/milk_quality.db），SQLAlchemy 2.0 声明式。v2.1 共 6 张表：users（id PK、username 唯一、hashed_password bcrypt、email/full_name 选填、created_at）；grade_records（id PK、7 项指标 NOT NULL、predicted_grade、confidence、user_id FK 可空，以及 v2.1 新增 source_id FK→sources.id、batch_no、suggested_price）；indicators（key PK、name、unit、min/max_value、description，seed 写入 7 行）；sources（v2.1 奶源档案：name 唯一、source_type 奶站/牧场/合作社、contact、region、note，种子 5 家）；user_preferences 与 agent_messages（v2.0 Agent 记忆表）。关系：User(1)—<GradeRecord(*)，GradeRecord(*)—>Source(1)。旧库升级由 database.py 的 _migrate_columns() 幂等 ALTER TABLE 自动补列。",
        "keywords": ["数据库", "SQLite", "users", "grade_records", "sources", "indicators", "user_preferences", "agent_messages", "表结构", "迁移"],
        "source": "03-系统架构与数据库设计.md",
    },
    {
        "category": "后端",
        "title": "字段命名约定",
        "type": "doc",
        "content": "后端接口统一使用小写蛇形字段名：ph/temperature/taste/odor/fat/turbidity/colour。数据集原始为大写首字母（含 Temprature 笔误），在清洗与 CSV 接口处统一纠正为标准名。前端单条预测表单与 CSV 批量均按小写传参，与数据集原始命名区分开，避免大小写不匹配导致的 422。",
        "keywords": ["字段命名", "小写", "ph", "temperature", "蛇形", "422"],
        "source": "03-系统架构与数据库设计.md",
    },

    # ---------------- 前端 ----------------
    {
        "category": "前端",
        "title": "前端技术栈与页面",
        "type": "doc",
        "content": "前端 React 18 + Vite 5 + Ant Design 5 + react-router-dom 6 + recharts + axios。v2.1 共 8 个页面：登录/注册；品质分级（单条录入 Tab + CSV 批量 Tab[两步预览] + 模型与特征 Tab[含相关性热力图与基线对比]）；历史记录（Table + 品质波动分析 + 导出 CSV）；分析仪表盘（趋势统计 + 企业日报入口）；智能助手（AgentChat 对话）；来源管理（SourceManager 档案 CRUD）；指标说明；个人中心（Profile 资料+密码）。布局用 Ant Design Layout + Sider 菜单，ConfigProvider 设中文 locale。",
        "keywords": ["前端", "React", "Ant Design", "Vite", "recharts", "页面", "Sider", "来源管理", "仪表盘", "个人中心"],
        "source": "03-系统架构与数据库设计.md",
    },
    {
        "category": "前端",
        "title": "开发端口与 API 代理",
        "type": "doc",
        "content": "前端开发服务器默认端口 5173（npm run dev）。Vite 已配置 server.proxy['/api'] → http://127.0.0.1:8000，开发期前端无需处理跨域；浏览器访问 http://127.0.0.1:5173 即可，所有 /api 请求由 Vite 转发到后端 8000。生产可用 VITE_API_BASE 环境变量指向后端真实地址。",
        "keywords": ["5173", "Vite", "代理", "proxy", "跨域", "VITE_API_BASE"],
        "source": "03-系统架构与数据库设计.md / 06-部署手册.md",
    },

    # ---------------- 部署 ----------------
    {
        "category": "部署",
        "title": "后端启动命令",
        "type": "qa",
        "question": "怎么启动后端服务？",
        "content": "后端启动：cd milk-quality-system/backend，执行 ../.venvcn/Scripts/uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --log-level info（使用项目 .venvcn 虚拟环境）。首次启动会执行 init_db() 建表 + seed.seed() 写入 7 项指标。验证：curl http://127.0.0.1:8000/api/indicators 应返回 7 项。交互文档 http://127.0.0.1:8000/docs。注意：修改 routers 或 main.py 路由后必须重启 uvicorn，否则新接口 404。",
        "answer": "cd backend 后用项目 venv 运行 uvicorn app.main:app --host 127.0.0.1 --port 8000；首次启动自动建表并写入指标。改了路由必须重启。",
        "keywords": ["启动", "uvicorn", "后端", "8000", "venvcn", "init_db"],
        "source": "06-部署手册.md",
    },
    {
        "category": "部署",
        "title": "前端启动与构建",
        "type": "qa",
        "question": "怎么启动前端？怎么打包生产？",
        "content": "前端开发：cd milk-quality-system/frontend，npm install --registry=https://registry.npmmirror.com（仅需一次），再 npm run dev 启动 Vite（默认 5173）。生产构建：npm run build 产物输出到 frontend/dist/，npm run preview 本地预览。vite.config.js 已设 build.emptyOutDir:false 以规避本机安全删除机制对清空 dist 的拦截。国内 npm 请用 npmmirror 镜像，否则极慢。",
        "answer": "开发：npm install（npmmirror 镜像）+ npm run dev；生产：npm run build 生成 dist/，npm run preview 预览。",
        "keywords": ["启动", "前端", "npm", "build", "dist", "npmmirror", "emptyOutDir"],
        "source": "06-部署手册.md",
    },
    {
        "category": "部署",
        "title": "生产部署建议",
        "type": "doc",
        "content": "生产部署建议：用 Nginx 同时托管前端静态文件并把 /api 反向代理到 FastAPI（建议开启 HTTPS）；CORS 生产环境将 allow_origins 改为前端真实域名；为 JWT 设置合理过期时间并引入刷新机制、限流防爆破；数据库当前为单文件 SQLite，适合演示/小规模，高并发可迁移到 PostgreSQL（只需改 database.py 连接串）；模型更新只需替换 joblib 与 metadata 后重启。",
        "keywords": ["生产", "Nginx", "反向代理", "HTTPS", "CORS", "PostgreSQL", "JWT刷新"],
        "source": "06-部署手册.md",
    },
    {
        "category": "部署",
        "title": "国内网络与镜像",
        "type": "doc",
        "content": "本机位于国内网络：pip 用清华镜像 https://pypi.tuna.tsinghua.edu.cn/simple；npm 用 https://registry.npmmirror.com，否则依赖安装极慢甚至卡死。Python 因 3.13 无 xgboost wheel 需用 3.12 虚拟环境。vite build 清空 dist 会被本机安全删除机制拦截，已用 emptyOutDir:false 规避。",
        "keywords": ["国内", "镜像", "清华", "npmmirror", "xgboost", "安全删除", "vite build"],
        "source": "06-部署手册.md / 用户级 MEMORY.md",
    },
    {
        "category": "部署",
        "title": "常见问题排错",
        "type": "doc",
        "content": "常见问题：新接口 404 → 后端未重启，重启 uvicorn；npm install 卡住 → 未用国内镜像，改用 npmmirror；vite build 失败(safe-delete) → 已用 emptyOutDir:false 规避，仍失败则手动删 dist 重试；前端调接口跨域报错 → 确认 Vite 代理已配且后端 CORS 开放，生产改具体域名；预测 422 → 字段名应为小写 ph/temperature/... 且取值在约束内。",
        "keywords": ["排错", "404", "跨域", "422", "safe-delete", "npm卡住"],
        "source": "06-部署手册.md",
    },

    # ---------------- 测试 ----------------
    {
        "category": "测试",
        "title": "测试结论总览",
        "type": "doc",
        "content": "系统测试（v1.0：2026-10-15；v2.1 企业功能补充：2026-10-23；Windows/Python3.12.2/Node22/后端8000/前端5173）：四阶段测试用例 70/70 全部通过（阶段1 数据模型16、阶段2 后端API 17、阶段3 前端集成25、阶段4 Agent 12）；后端接口全量复测 23/23 通过（含 422/400/401 异常路径）；前端 npm run build 0 error；企业功能实测：来源 CRUD、定价建议（优¥4.60/差¥3.00）、CSV 按行匹配来源、企业日报预警触发、个人中心全部通过。",
        "keywords": ["测试", "结论", "70/70", "23/23", "企业功能", "联调", "build"],
        "source": "05-系统测试报告.md / test-report-stage1~4",
    },
    {
        "category": "测试",
        "title": "异常输入测试用例",
        "type": "doc",
        "content": "异常输入用例：字段缺失（不传 ph）→ 422（Pydantic 校验）；数值越界（ph=99）→ 422；CSV 缺列（无 Taste 列）→ 200 + errors 明细；CSV 列名笔误（Temprature）→ 自动纠正并正确预测；二值越界（taste=2）→ 422。说明接口对边界与脏数据有正确防护。",
        "keywords": ["异常", "422", "越界", "缺列", "笔误", "容错", "测试"],
        "source": "05-系统测试报告.md",
    },

    # ---------------- 安全 ----------------
    {
        "category": "安全",
        "title": "安全设计要点",
        "type": "doc",
        "content": "安全：密码以 bcrypt 哈希存储，不落明文；令牌为 PyJWT 短时 Bearer Token，前端拦截 401 自动跳登录；匿名预测不写历史（user_id 为 NULL），兼顾易用与隐私；CORS 开发期 allow_origins=[\"*\"] 且 allow_credentials=False（因用 Bearer 非 Cookie），生产应改为具体域名。遗留建议：为 JWT 设过期与刷新、限流防爆破。",
        "keywords": ["安全", "bcrypt", "JWT", "CORS", "隐私", "匿名", "401"],
        "source": "02-PRD与项目说明.md / 05-系统测试报告.md",
    },

    # ---------------- Agent 智能体（v2.0） ----------------
    {
        "category": "Agent",
        "title": "Agent 架构与四层模型",
        "type": "doc",
        "content": "v2.0 将单一模型预测升级为 Agent 智能体架构：用户输入 → 感知层（XGBoost 预测）→ 推理层（根因分析/异常检测）→ 行动层（改进建议/报告生成）→ 记忆层（用户偏好/会话上下文）。纯规则 + 数据分析实现，零外部 LLM 依赖，单条分析 < 200ms，推理链完整可解释。后端模块：app/agent/engine.py（引擎）、tools.py（工具注册）、memory.py（记忆）；前端：预测结果页智能分析卡片、AgentChat 对话页、Dashboard 仪表盘。",
        "keywords": ["Agent", "智能体", "感知", "推理", "行动", "记忆", "四层", "零LLM"],
        "source": "13-Agent智能体升级说明.md",
    },
    {
        "category": "Agent",
        "title": "Agent 七大工具",
        "type": "doc",
        "content": "Agent 共 7 个工具：①根因分析（对比理想范围，按特征重要性排序问题指标，生成自然语言总结）；②改进建议（按严重/轻微/提示分级，给出操作指南与优先级行动计划）；③趋势分析（品质趋势判断 + 低品质占比超标预警）；④异常检测（临界值+预警值双重阈值，正常/预警/严重三级）；⑤报告生成（完整 Markdown 分析报告）；⑥知识问答（14 主题知识库，覆盖 pH/温度/储存/乳腺炎/分级/工艺/安全/污染等）；⑦企业日报（enterprise_daily_report，按日期汇总收购数据）。",
        "keywords": ["Agent工具", "根因分析", "改进建议", "趋势", "异常检测", "报告", "知识问答", "企业日报"],
        "source": "13-Agent智能体升级说明.md",
    },
    {
        "category": "Agent",
        "title": "智能助手对话能力",
        "type": "qa",
        "question": "智能助手能做什么？怎么用？",
        "content": "智能助手（/agent 页面）支持自然语言对话，意图识别五类：greeting（问候）、knowledge（知识问答，14 主题知识库 + 意图识别 + 友好兜底）、trend（趋势查询，如『最近品质趋势怎么样』）、daily_report（企业日报，如『生成今天的日报』，可带日期 2026-10-23）、analyze_request（引导到预测页做分析）。多轮对话上下文由 agent_messages 表按 session_id 保存。",
        "answer": "打开「智能助手」页面即可对话：问知识（pH 范围、温度控制）、查趋势、说『生成今天的日报』出企业日报；答不了会给出引导方向。",
        "keywords": ["智能助手", "对话", "意图识别", "知识问答", "日报", "session"],
        "source": "13-Agent智能体升级说明.md / 前端 AgentChat",
    },

    # ---------------- 模型增强（v2.1） ----------------
    {
        "category": "模型",
        "title": "基线模型对比",
        "type": "qa",
        "question": "为什么选 XGBoost？和其他模型比怎么样？",
        "content": "同一测试集（10%，stratified split, random_state=42）实测对比：决策树（max_depth=6）准确率 94.34%、宏 F1 0.938；随机森林（200 棵）准确率 99.06%、宏 F1 0.9895；XGBoost（本系统，max_depth=3/lr=0.2/n_estimators=300）准确率 100%、宏 F1 1.000。XGBoost 在三者中最优，且 Pipeline 一体化封装。对比结果通过 /api/model/info 的 baseline_comparison 字段暴露，前端「模型与特征」页展示。",
        "answer": "同测试集实测：决策树 94.34% < 随机森林 99.06% < XGBoost 100%，选 XGBoost。",
        "keywords": ["基线", "决策树", "随机森林", "XGBoost", "对比", "94.34", "99.06", "100%"],
        "source": "05-系统测试报告.md / 04-API接口文档.md",
    },
    {
        "category": "模型",
        "title": "指标相关性分析",
        "type": "doc",
        "content": "指标与 Grade 的 Pearson 相关（1059 条实测，8×8 矩阵经 /api/model/info 返回，前端热力图展示）：Temperature -0.418（最强负相关，温度越高品质越差）；Fat +0.151；Odor +0.150；Turbidity -0.154；pH +0.029（线性相关弱，但 XGBoost 特征重要性第二，属非线性关系）；Taste +0.026；Colour -0.057。相关性与特征重要性互相印证，支撑根因分析的排序依据。",
        "keywords": ["相关性", "Pearson", "热力图", "Temperature", "-0.418", "correlation"],
        "source": "04-API接口文档.md / 01-数据来源与数据字典.md",
    },

    # ---------------- 企业落地（v2.1） ----------------
    {
        "category": "企业落地",
        "title": "奶源来源档案",
        "type": "doc",
        "content": "v2.1 新增 sources 表管理奶站/牧场/合作社档案（name 唯一、source_type、contact、region、note）。启动时 seed 写入 5 家：第一奶站（城东区）、第二奶站（城西区）、绿源牧场（青山县）、康达合作社（6 个自然村）、润发牧场（河口镇）。使用方式：预测页表单选择来源+填批次号，或「来源管理」页面做完整 CRUD；CSV 批量支持 Source 列按行匹配来源名称。历史记录与日报按来源统计。",
        "keywords": ["来源", "奶站", "牧场", "合作社", "档案", "追溯", "批次", "来源管理"],
        "source": "14-企业落地增强说明.md",
    },
    {
        "category": "企业落地",
        "title": "优质优价定价建议",
        "type": "qa",
        "question": "系统怎么给出收购定价建议？",
        "content": "定价策略（config.py 的 PRICE_FACTORS 可配置）：基础价 ¥4.00/kg；high（优）×1.15 = ¥4.60；medium（中）×1.00 = ¥4.00；low（差）×0.75 = ¥3.00。predict 接口响应含 pricing 字段（base_price/factor/suggested_price/advice），历史记录落库 suggested_price，企业日报汇总建议收购总额。落地时按当地生鲜乳收购指导价调整 BASE_PRICE，并保留人工议价通道。",
        "answer": "按等级给建议价：优 ¥4.60（×1.15）/ 中 ¥4.00 / 差 ¥3.00（×0.75），基础价与系数可在 config.py 配置。",
        "keywords": ["定价", "优质优价", "价格系数", "suggested_price", "收购", "4.6", "3.0"],
        "source": "14-企业落地增强说明.md",
    },
    {
        "category": "企业落地",
        "title": "企业质量日报",
        "type": "qa",
        "question": "企业日报是什么？怎么生成？",
        "content": "企业质量日报（POST /api/agent/daily-report，需登录）按日期汇总当日收购数据：①收购概况（记录数、等级分布、建议收购总额）；②来源质量排名（按优质率：收购数/优质率/差奶数/均价）；③异常与预警（差奶占比超 20% 触发警戒线，列出出现差奶的来源）；④管理建议（提高优质来源收购量、差奶处置、冷链提醒）。输出完整 Markdown，前端仪表盘「生成企业日报」可查看、复制、下载 .md。也可对智能助手说『生成今天的日报』。",
        "answer": "仪表盘右上角「生成企业日报」或对智能助手说『生成今天的日报』：汇总当日收购统计、来源排名、差奶预警和建议总额，可复制/下载 Markdown。",
        "keywords": ["企业日报", "日报", "来源排名", "预警", "收购总额", "Markdown", "daily-report"],
        "source": "14-企业落地增强说明.md",
    },
    {
        "category": "企业落地",
        "title": "个人中心",
        "type": "doc",
        "content": "个人中心（/profile 页面，对应任务书 2.2.6 个人信息管理）：GET /api/auth/me 查看当前用户资料（id/username/email/full_name/created_at）；PUT /api/auth/me 修改姓名与邮箱；PUT /api/auth/password 修改密码（校验原密码，新密码 ≥ 6 位）。前端表单含确认密码二次校验。",
        "keywords": ["个人中心", "资料", "修改密码", "profile", "auth/me", "auth/password"],
        "source": "04-API接口文档.md / 14-企业落地增强说明.md",
    },
    {
        "category": "企业落地",
        "title": "CSV 两步预览",
        "type": "doc",
        "content": "v2.1 CSV 批量上传改为两步走（任务书 2.2.1 数据预览）：第一步上传后前端本地解析，展示前 5 行预览表 + 列名校验（缺少必需列时警告并阻止预测）；第二步用户点击「确认无误，执行批量预测」才上传推理。支持可选 Batch 列提取批次号、Source 列按行匹配来源。",
        "keywords": ["CSV预览", "两步走", "数据预览", "列校验", "Batch", "Source"],
        "source": "14-企业落地增强说明.md / 02-PRD与项目说明.md",
    },

    # ---------------- FAQ ----------------
    {
        "category": "FAQ",
        "title": "为什么准确率能到 100%？",
        "type": "qa",
        "question": "为什么测试集准确率能达到 100%？是不是过拟合？",
        "content": "该 Kaggle 牛奶数据集线性可分度很高，目标 Grade 与 7 个指标（尤其 Turbidity、pH、Fat）高度相关，XGBoost 在此类数据上容易达到接近满分的区分度。训练采用 8:1:1 分层切分 + 5 折交叉验证（宏 F1=0.9976），并非单点过拟合。但需注意：数据规模仅 1059 条且来自单一来源，泛化到真实奶源仍需更多样化样本与现场验证。",
        "answer": "数据集本身线性可分度高、特征与目标强相关，所以 XGBoost 接近满分；且经过分层切分与 5 折交叉验证（宏 F1 0.9976），不是单点过拟合。但样本少、来源单一，真实泛化需更多数据。",
        "keywords": ["100%", "过拟合", "线性可分", "泛化", "交叉验证", "样本量"],
        "source": "01-数据来源与数据字典.md / 05-系统测试报告.md",
    },
    {
        "category": "FAQ",
        "title": "支持哪些输入方式？",
        "type": "qa",
        "question": "系统支持哪些方式录入牛奶指标做分级？",
        "content": "两种方式：1) 单条录入——在「品质分级」页填写 7 项指标表单实时预测，返回等级、置信度与三分类概率；2) CSV 批量——上传含表头（pH, Temperature, Taste, Odor, Fat, Turbidity, Colour）的 CSV，系统逐行预测并展示结果表，支持列名大小写/拼写容错与错误行定位。两种方式均支持匿名使用，登录后自动留存历史。",
        "answer": "支持单条表单录入和 CSV 批量上传两种；均可用匿名，登录后自动留历史。",
        "keywords": ["输入方式", "单条", "CSV", "批量", "录入", "表单"],
        "source": "02-PRD与项目说明.md / 04-API接口文档.md",
    },
    {
        "category": "FAQ",
        "title": "预测结果如何解读？",
        "type": "qa",
        "question": "predict 返回的 grade、confidence、probabilities 怎么看？",
        "content": "predict 返回 grade（预测等级 low/medium/high）、confidence（模型对该样本的最高类概率，0–1，越接近 1 越可信）、probabilities（三分类各自概率，三者之和为 1）。例如 grade:high, confidence:0.999 表示模型 99.9% 把握该牛奶为优等级。结果仅供品质初筛参考，需结合实验室检测复核（UI 已内置免责声明）。",
        "answer": "grade 是预测等级；confidence 是最可能类的置信度；probabilities 是三类的各自概率（和为1）。高 confidence 表示可信度高，但仅作初筛参考。",
        "keywords": ["解读", "grade", "confidence", "probabilities", "概率", "免责声明"],
        "source": "04-API接口文档.md / 前端 Indicators 页",
    },
    {
        "category": "FAQ",
        "title": "历史记录怎么看和导出？",
        "type": "qa",
        "question": "登录后怎么查看和导出我的分级历史？",
        "content": "登录后在「历史记录」页可分页查看本人所有分级记录（含 7 项指标、预测等级、置信度、时间）。点击「导出 CSV」调用 GET /api/history/export，下载带 UTF-8 BOM 的 grade_history.csv，可直接用 Excel 打开不乱码。历史仅本人可见（按 user_id 过滤）。",
        "answer": "历史记录页分页查看本人记录；导出按钮下载带 BOM 的 CSV，Excel 直接打开不乱码，且仅本人可见。",
        "keywords": ["历史", "导出", "CSV", "BOM", "分页", "本人"],
        "source": "04-API接口文档.md / 前端 History 页",
    },
]


def main():
    os.makedirs(os.path.dirname(OUT_JSONL), exist_ok=True)
    count = 0
    with open(OUT_JSONL, "w", encoding="utf-8") as f:
        for i, item in enumerate(CORPUS, start=1):
            rec = {
                "id": f"mq-{i:03d}",
                "category": item["category"],
                "title": item["title"],
                "type": item["type"],
                "content": item["content"],
                "keywords": item.get("keywords", []),
                "source": item.get("source", ""),
            }
            if item["type"] == "qa":
                rec["question"] = item.get("question", "")
                rec["answer"] = item.get("answer", "")
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1
    print(f"[ok] wrote {count} chunks -> {OUT_JSONL}")

    # 统计
    cats = {}
    for item in CORPUS:
        cats[item["category"]] = cats.get(item["category"], 0) + 1
    print("[stats] by category:", cats)

    # 写 README
    readme = generate_readme(count, cats)
    with open(OUT_README, "w", encoding="utf-8") as f:
        f.write(readme)
    print(f"[ok] wrote -> {OUT_README}")


def generate_readme(count, cats):
    today = datetime.now().strftime("%Y-%m-%d")
    cat_lines = "\n".join(f"- {k}：{v} 条" for k, v in cats.items())
    return f"""# 牛奶品质分级系统 · RAG 语料库

> 生成时间：{today}　|　知识块总数：**{count}**　|　格式：JSONL（每行一个 JSON）

## 1. 这是什么
本语料库为「牛奶品质分级系统」项目沉淀的可检索知识，覆盖项目概述、数据、模型、后端、前端、部署、测试、安全、Agent 智能体、企业落地、FAQ 十一大类。可用于搭建项目级问答机器人、智能助手或文档检索，让使用者用自然语言问「怎么部署」「数据从哪来」「预测接口怎么调」「企业日报怎么生成」等问题并拿到准确答案。

## 2. 文件
- `rag_corpus.jsonl`：主语料，每行一个 JSON 知识块。
- `build_rag_corpus.py`（位于 `src/`）：可复现的生成脚本，修改后重跑即可重建语料。
- 本文件：使用说明。

## 3. 知识块字段
| 字段 | 含义 |
| --- | --- |
| id | 唯一编号，如 `mq-001` |
| category | 分类（项目概述/数据/模型/后端/前端/部署/测试/安全/Agent/企业落地/FAQ） |
| title | 知识块标题 |
| type | `doc`=事实性知识块；`qa`=问答对（含 question/answer，可直接作答案） |
| content | 正文（自包含、可被检索与引用） |
| keywords | 关键词数组，建议作为检索 boost 或标签 |
| source | 出处文档，便于溯源 |
| question / answer | 仅 `qa` 类型有，问答对原文 |

## 4. 分类统计
{cat_lines}

## 5. 如何接入 RAG 管线（示例）
语料为纯文本 + 元数据，embedding 在摄取（ingest）阶段生成。以下为通用接入示例（Python + sentence-transformers）：

```python
import json
from sentence_transformers import SentenceTransformer

# 1) 读取语料
chunks = [json.loads(l) for l in open("docs/rag_corpus.jsonl", encoding="utf-8")]

# 2) 构造待嵌入文本（qa 优先用 question+answer，doc 用 title+content）
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  # 多语言，支持中文
texts = []
for c in chunks:
    if c["type"] == "qa":
        texts.append(c["question"] + " " + c["answer"])
    else:
        texts.append(c["title"] + " " + c["content"])

embs = model.encode(texts, normalize_embeddings=True)

# 3) 写入向量库（以 sqlite + 简单余弦为例，或换 chroma/pgvector/FAISS）
#    chroma: collection.add(ids=[c['id'] for c in chunks], documents=texts, embeddings=embs, metadatas=chunks)
# 4) 检索时取 top-k，把对应 content 作为上下文喂给 LLM 生成答案
```

接入要点：
- **检索粒度**：以单个知识块为单位，块已拆分为「一事一议」，便于精准命中。
- **中文 embedding**：推荐多语言模型（如 paraphrase-multilingual-MiniLM-L12-v2、bge-m3）以保证中文召回。
- **关键词 boost**：命中 `keywords` 的查询可直接提升该块权重。
- **答案来源**：`qa` 块的 `answer` 字段可直接作为高置信答案；`doc` 块交给 LLM 基于 content 归纳。

## 6. 维护建议
- 项目文档（docs/01~06、README）更新后，重跑 `python src/build_rag_corpus.py` 重建语料。
- 新增 FAQ 直接在 `build_rag_corpus.py` 的 `CORPUS` 列表追加条目即可，脚本自动编号与分流。
"""


if __name__ == "__main__":
    main()

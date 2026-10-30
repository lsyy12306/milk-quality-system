# -*- coding: utf-8 -*-
"""后端配置（路径、密钥、模型位置）。"""
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent          # backend/app
BACKEND_DIR = APP_DIR.parent                       # backend
PROJECT_ROOT = BACKEND_DIR.parent                  # milk-quality-system

# SQLite 数据库文件（放在 backend/ 下）
DB_PATH = BACKEND_DIR / "milk_quality.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# JWT 鉴权（生产环境务必改掉 SECRET_KEY）
SECRET_KEY = "change-me-in-production-milk-quality-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24              # 1 天

# 已训练好的模型（第二步产出）
MODEL_PATH = PROJECT_ROOT / "models" / "milk_quality_pipeline.joblib"

# ------------------------------------------------------------------ #
# 企业落地：收购定价策略（优质优价）
# 基础价为当地生鲜乳收购指导价（元/kg），可按合同调整
# ------------------------------------------------------------------ #
BASE_PRICE = 4.00                    # 基础收购价（元/kg）
PRICE_FACTORS = {                    # 各等级价格系数
    "high": 1.15,                    # 优：加价 15%
    "medium": 1.00,                  # 中：按基础价
    "low": 0.75,                     # 差：降价 25%（建议拒收或折价）
}
PRICE_ADVICE = {
    "high": "优质奶源，建议按优质优价机制优先收购",
    "medium": "品质一般，可按基础价收购并加强监控",
    "low": "品质不达标，建议拒收或折价处理，并追溯来源",
}

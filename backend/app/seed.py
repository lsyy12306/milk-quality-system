# -*- coding: utf-8 -*-
"""初始化数据库并写入指标字典（7 项理化指标）+ 企业来源档案种子。"""
from .database import SessionLocal, engine, Base
from . import models_db

INDICATORS = [
    ("pH", "pH值", "", 3.0, 9.5, "酸碱度，影响奶质与稳定性"),
    ("Temperature", "温度", "°C", 34.0, 90.0, "样品温度"),
    ("Taste", "口感", "", 0.0, 1.0, "口感质量标志：1=合格 / 0=不合格"),
    ("Odor", "气味", "", 0.0, 1.0, "气味质量标志：1=合格 / 0=不合格"),
    ("Fat", "脂肪", "", 0.0, 1.0, "脂肪质量标志：1=合格 / 0=不合格"),
    ("Turbidity", "浑浊度", "", 0.0, 1.0, "浑浊度质量标志：1=合格 / 0=不合格"),
    ("Colour", "颜色", "", 240.0, 255.0, "颜色数值（数据集刻度）"),
]

# 企业来源档案种子（奶站 / 牧场 / 合作社）
SOURCES = [
    ("第一奶站", "奶站", "张站长 138****0001", "城东区", "合作 3 年，质量稳定"),
    ("第二奶站", "奶站", "李站长 138****0002", "城西区", "夏季温度需重点关注"),
    ("绿源牧场", "牧场", "王场长 139****0003", "青山县", "规模化牧场，500 头奶牛"),
    ("康达合作社", "合作社", "赵社长 137****0004", "下辖 6 个自然村", "散奶集中收储"),
    ("润发牧场", "牧场", "陈场长 136****0005", "河口镇", "新合作牧场，考察期"),
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for key, name, unit, mn, mx, desc in INDICATORS:
            if not db.query(models_db.Indicator).filter(models_db.Indicator.key == key).first():
                db.add(models_db.Indicator(
                    key=key, name=name, unit=unit,
                    min_value=mn, max_value=mx, description=desc,
                ))
        for name, stype, contact, region, note in SOURCES:
            if not db.query(models_db.Source).filter(models_db.Source.name == name).first():
                db.add(models_db.Source(
                    name=name, source_type=stype, contact=contact,
                    region=region, note=note,
                ))
        db.commit()
    finally:
        db.close()

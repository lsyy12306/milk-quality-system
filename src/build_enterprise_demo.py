# -*- coding: utf-8 -*-
"""生成企业场景演示数据（v2.0 企业落地版）。

产出：
- data/demo_batch_enterprise.csv  30 条带 Source/Batch/Date 的收购批次数据
- data/demo_enterprise_samples.json  带真实预测+定价建议的演示样本
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# 企业来源档案（与 seed.py 一致）
SOURCES = {
    "第一奶站": "S1",
    "第二奶站": "S2",
    "绿源牧场": "S3",
    "康达合作社": "S4",
    "润发牧场": "S5",
}

# 30 条企业场景样本：(pH, 温度, 口感, 气味, 脂肪, 浑浊度, 颜色, 来源, 批次)
# 覆盖：优质 / 一般 / 劣质 / 边界场景，来源分布体现不同牧场质量差异
SAMPLES = [
    # 优质批次（12 条）
    (6.62, 35.0, 1, 1, 1, 1, 254, "第一奶站", "B1021-A01"),
    (6.60, 36.0, 1, 1, 1, 1, 255, "第一奶站", "B1021-A01"),
    (6.65, 34.5, 1, 1, 1, 1, 253, "第一奶站", "B1021-A02"),
    (6.58, 37.0, 1, 1, 1, 1, 252, "绿源牧场", "B1021-B01"),
    (6.70, 35.5, 1, 1, 1, 1, 255, "绿源牧场", "B1021-B01"),
    (6.55, 36.5, 1, 1, 1, 1, 251, "绿源牧场", "B1021-B02"),
    (6.63, 34.0, 1, 1, 1, 1, 254, "润发牧场", "B1021-C01"),
    (6.68, 35.0, 1, 1, 1, 1, 250, "润发牧场", "B1021-C01"),
    (6.60, 38.0, 1, 1, 1, 1, 252, "康达合作社", "B1021-D01"),
    (6.52, 36.0, 1, 1, 1, 1, 253, "康达合作社", "B1021-D01"),
    (6.66, 34.8, 1, 1, 1, 1, 254, "第一奶站", "B1021-A03"),
    (6.57, 37.2, 1, 1, 1, 1, 252, "绿源牧场", "B1021-B03"),
    # 一般/边缘（8 条，部分指标偏差）
    (6.5, 42.0, 1, 1, 1, 1, 250, "第二奶站", "B1021-E01"),
    (6.75, 40.0, 1, 1, 1, 1, 251, "第二奶站", "B1021-E01"),
    (6.6, 45.0, 1, 1, 1, 1, 252, "第二奶站", "B1021-E02"),
    (6.45, 38.0, 1, 1, 1, 1, 250, "康达合作社", "B1021-D02"),
    (6.8, 39.0, 1, 1, 1, 1, 249, "康达合作社", "B1021-D02"),
    (6.55, 46.0, 1, 1, 1, 1, 251, "第二奶站", "B1021-E03"),
    (6.7, 43.5, 1, 1, 1, 1, 252, "润发牧场", "B1021-C02"),
    (6.4, 41.0, 1, 1, 1, 1, 250, "润发牧场", "B1021-C02"),
    # 劣质/异常（10 条，覆盖不同问题类型）
    (7.2, 65.0, 1, 0, 1, 0, 245, "第二奶站", "B1021-E04"),   # 高温+气味差+浑浊
    (5.5, 40.0, 1, 1, 0, 1, 248, "康达合作社", "B1021-D03"),  # pH低+脂肪差
    (3.0, 90.0, 0, 0, 0, 0, 240, "第二奶站", "B1021-E05"),   # 全项劣质
    (6.0, 45.0, 0, 1, 1, 0, 245, "康达合作社", "B1021-D04"),  # 口感差+浑浊
    (6.6, 99.0, 1, 1, 1, 1, 255, "润发牧场", "B1021-C03"),   # 边界：极端高温
    (0.5, 35.0, 1, 1, 1, 1, 255, "润发牧场", "B1021-C04"),   # 边界：极端pH
    (6.6, 35.0, 1, 1, 1, 1, 1, "绿源牧场", "B1021-B04"),     # 边界：极端颜色
    (6.8, 52.0, 1, 0, 1, 1, 246, "第二奶站", "B1021-E06"),   # 温度偏高+气味差
    (4.0, 70.0, 0, 0, 0, 0, 242, "第二奶站", "B1021-E07"),   # 劣质边缘
    (3.5, 60.0, 0, 1, 0, 0, 241, "康达合作社", "B1021-D05"),  # 劣质酸败
]


def main():
    DATA.mkdir(exist_ok=True)

    # 1) 企业演示 CSV（含 Source / Batch 列）
    csv_path = DATA / "demo_batch_enterprise.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pH", "Temperature", "Taste", "Odor", "Fat", "Turbidity", "Colour", "Source", "Batch"])
        for ph, temp, taste, odor, fat, turb, colour, src, batch in SAMPLES:
            w.writerow([ph, temp, taste, odor, fat, turb, colour, src, batch])
    print(f"written: {csv_path} ({len(SAMPLES)} rows)")

    # 2) 演示样本 JSON（用真实模型推理 + 定价）
    import sys
    sys.path.insert(0, str(ROOT / "backend"))
    from app.ml_model import predict_single

    from app.config import BASE_PRICE, PRICE_FACTORS, PRICE_ADVICE

    samples = []
    for i, (ph, temp, taste, odor, fat, turb, colour, src, batch) in enumerate(SAMPLES, 1):
        grade, conf, probs = predict_single(ph, temp, taste, odor, fat, turb, colour)
        factor = PRICE_FACTORS[grade]
        samples.append({
            "id": i,
            "scenario": "优质" if grade == "high" else ("劣质/异常" if grade == "low" else "边缘"),
            "source": src,
            "batch": batch,
            "input": {"ph": ph, "temperature": temp, "taste": taste, "odor": odor,
                      "fat": fat, "turbidity": turb, "colour": colour},
            "result": {"grade": grade, "confidence": round(conf, 4), "probabilities": probs},
            "pricing": {
                "base_price": BASE_PRICE,
                "factor": factor,
                "suggested_price": round(BASE_PRICE * factor, 2),
                "advice": PRICE_ADVICE[grade],
            },
        })

    json_path = DATA / "demo_enterprise_samples.json"
    json.dump({
        "description": "企业场景演示样本（含来源档案、批次号、定价建议），预测由真实模型推理得出",
        "sources": {k: v for k, v in SOURCES.items()},
        "pricing_policy": {"base_price": BASE_PRICE, "factors": PRICE_FACTORS},
        "samples": samples,
    }, open(json_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"written: {json_path} ({len(samples)} samples)")

    # 统计
    from collections import Counter
    c = Counter(s["result"]["grade"] for s in samples)
    print(f"grade distribution: high={c['high']}, medium={c['medium']}, low={c['low']}")
    total_price = sum(s["pricing"]["suggested_price"] for s in samples)
    print(f"total suggested price: ¥{total_price:.2f} (base ¥{BASE_PRICE}/kg x {len(samples)})")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Agent 工具集：根因分析、改进建议、趋势预测、报告生成、预警检测、企业日报。"""
from datetime import datetime, timedelta, timezone
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from .. import models_db
from ..ml_model import load_model


class ToolRegistry:
    """工具注册中心：所有 Agent 可调用的能力。"""

    def __init__(self, db: Session | None = None):
        self.db = db
        self._tools = {
            "root_cause_analysis": self.root_cause_analysis,
            "improvement_suggestions": self.improvement_suggestions,
            "trend_analysis": self.trend_analysis,
            "anomaly_detection": self.anomaly_detection,
            "generate_report": self.generate_report,
            "knowledge_qa": self.knowledge_qa,
            "enterprise_daily_report": self.enterprise_daily_report,
        }

    def list_tools(self) -> list[dict]:
        return [
            {"name": k, "description": v.__doc__.strip().split("\n")[0] if v.__doc__ else ""}
            for k, v in self._tools.items()
        ]

    def call(self, tool_name: str, **kwargs) -> dict:
        if tool_name not in self._tools:
            return {"error": f"未知工具：{tool_name}"}
        return self._tools[tool_name](**kwargs)

    # ------------------------------------------------------------------ #
    # 工具 1：根因分析
    # ------------------------------------------------------------------ #
    def root_cause_analysis(self, ph, temperature, taste, odor, fat, turbidity, colour,
                            grade, confidence, probabilities) -> dict:
        """根据指标值和模型特征重要性，分析品质等级的根因。"""
        _, meta = load_model()
        importance = meta.get("feature_importance", {})

        # 标准化特征重要性排序
        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)

        # 指标理想范围（基于训练数据统计）
        IDEAL = {
            "pH": (6.5, 6.8),
            "Temperature": (35.0, 45.0),
            "Taste": (1, 1),
            "Odor": (1, 1),
            "Fat": (1, 1),
            "Turbidity": (1, 1),
            "Colour": (250, 255),
        }

        inputs = {
            "pH": ph, "Temperature": temperature, "Taste": taste,
            "Odor": odor, "Fat": fat, "Turbidity": turbidity, "Colour": colour,
        }

        issues = []
        healthy = []

        for feat, (low, high) in IDEAL.items():
            val = inputs[feat]
            if low <= val <= high:
                healthy.append(feat)
            else:
                deviation = 0
                if val < low:
                    deviation = (low - val) / (low if low > 0 else 1)
                else:
                    deviation = (val - high) / (high if high > 0 else 1)
                severity = "严重" if deviation > 0.5 else "轻微"
                issues.append({
                    "feature": feat,
                    "value": val,
                    "ideal_range": f"{low}~{high}",
                    "deviation": round(deviation, 3),
                    "severity": severity,
                    "importance": round(importance.get(feat, 0), 4),
                })

        # 按特征重要性排序问题
        issues.sort(key=lambda x: x["importance"], reverse=True)

        # 根因总结
        if not issues:
            summary = "所有指标均在理想范围内，品质优良。"
        elif grade == "low":
            top = issues[0]
            summary = f"品质等级为【差】，主要由 {top['feature']} 异常导致（偏离理想范围 {top['severity']}），该指标对模型决策贡献度为 {top['importance']*100:.1f}%。"
        elif grade == "medium":
            summary = f"品质等级为【一般】，存在 {len(issues)} 项指标偏离理想范围，建议关注 {'、'.join([i['feature'] for i in issues[:2]])}。"
        else:
            summary = "品质等级为【优】，虽然个别指标略有波动，但整体品质良好。"

        return {
            "grade": grade,
            "confidence": confidence,
            "issues": issues,
            "healthy_count": len(healthy),
            "issue_count": len(issues),
            "summary": summary,
            "top_risk_factors": [i["feature"] for i in issues[:3]],
        }

    # ------------------------------------------------------------------ #
    # 工具 2：改进建议
    # ------------------------------------------------------------------ #
    def improvement_suggestions(self, ph, temperature, taste, odor, fat, turbidity, colour,
                                 grade, **kwargs) -> dict:
        """根据问题指标生成具体可操作的改进建议。"""

        SUGGESTIONS = {
            "pH": {
                "high": [
                    "pH 偏高：可能由于乳腺感染或保存不当导致碱性物质增加。建议立即检测奶牛乳腺健康状况。",
                    "检查储奶罐清洁度，避免碱性清洗剂残留。",
                    "缩短从挤奶到冷却的时间间隔，抑制微生物产碱。",
                ],
                "low": [
                    "pH 偏低：可能由于乳酸发酵过度或初乳混入。建议检测是否混入变质奶。",
                    "检查冷链温度，确保 4°C 以下保存。",
                    "评估挤奶设备卫生状况，避免微生物污染。",
                ],
            },
            "Temperature": {
                "high": [
                    "温度过高：严重警示！高温会加速细菌繁殖。建议立即启动紧急冷却程序。",
                    "检查制冷设备运行状态，确保冷却水循环正常。",
                    "评估挤奶到入库的时间，目标控制在 2 小时以内。",
                ],
                "low": [
                    "温度偏低：虽然不利于细菌繁殖，但可能影响后续加工工艺。",
                    "检查温度传感器是否准确，排除测量误差。",
                ],
            },
            "Taste": {
                "bad": [
                    "口感不合格：可能由于饲料霉变、奶牛疾病或储存污染。建议更换饲料批次并检测。",
                    "检查挤奶设备是否有异味残留。",
                    "评估是否混入不同批次或不同来源的牛奶。",
                ],
            },
            "Odor": {
                "bad": [
                    "气味异常：可能由于奶牛酮病、乳腺炎或环境污染。建议兽医检查。",
                    "检查牛舍通风和卫生状况。",
                    "评估挤奶后是否及时密封保存。",
                ],
            },
            "Fat": {
                "bad": [
                    "脂肪指标异常：可能由于奶牛营养不良或泌乳期变化。建议调整饲料配方。",
                    "检查是否混入脱脂奶或乳清。",
                    "评估挤奶方式是否影响脂肪球结构。",
                ],
            },
            "Turbidity": {
                "bad": [
                    "浑浊度异常：提示可能存在絮凝物、杂质或微生物污染。建议过滤检测。",
                    "检查储奶罐和管道的清洁状况。",
                    "评估是否发生蛋白质变性。",
                ],
            },
            "Colour": {
                "high": [
                    "颜色值偏高：可能由于血乳混入或氧化反应。建议检测体细胞数。",
                ],
                "low": [
                    "颜色值偏低：可能由于掺水或脂肪含量过低。建议检测掺假指标。",
                ],
            },
        }

        IDEAL = {
            "pH": (6.5, 6.8),
            "Temperature": (35.0, 45.0),
            "Taste": (1, 1),
            "Odor": (1, 1),
            "Fat": (1, 1),
            "Turbidity": (1, 1),
            "Colour": (250, 255),
        }

        inputs = {
            "pH": ph, "Temperature": temperature, "Taste": taste,
            "Odor": odor, "Fat": fat, "Turbidity": turbidity, "Colour": colour,
        }

        suggestions = []
        priority = {"严重": [], "轻微": [], "提示": []}

        for feat, (low, high) in IDEAL.items():
            val = inputs[feat]
            if low <= val <= high:
                continue

            severity = "严重" if (val < low and feat in ("pH", "Temperature", "Turbidity")) or \
                                 (val > high and feat == "Temperature") else "轻微"

            key = "high" if val > high else "low" if val < low else "bad"

            if feat in SUGGESTIONS and key in SUGGESTIONS[feat]:
                for sug in SUGGESTIONS[feat][key]:
                    item = {"feature": feat, "severity": severity, "suggestion": sug}
                    suggestions.append(item)
                    priority[severity].append(item)

        # 通用建议
        if grade == "low":
            priority["提示"].append({
                "feature": "通用",
                "severity": "提示",
                "suggestion": "【紧急】该样品品质为差，建议立即隔离处理，不得进入流通环节。",
            })
        elif grade == "medium":
            priority["提示"].append({
                "feature": "通用",
                "severity": "提示",
                "suggestion": "该样品品质一般，建议加强监控并追溯上游环节，避免品质进一步下降。",
            })

        return {
            "grade": grade,
            "total_suggestions": len(suggestions),
            "suggestions": suggestions,
            "priority": priority,
            "action_plan": self._build_action_plan(priority),
        }

    def _build_action_plan(self, priority: dict) -> list[dict]:
        """构建行动计划（按紧急程度排序）。"""
        plan = []
        for sev in ["严重", "轻微", "提示"]:
            for item in priority.get(sev, []):
                plan.append({
                    "priority": sev,
                    "feature": item["feature"],
                    "action": item["suggestion"],
                })
        return plan

    # ------------------------------------------------------------------ #
    # 工具 3：趋势分析
    # ------------------------------------------------------------------ #
    def trend_analysis(self, user_id: int | None = None, days: int = 30, **kwargs) -> dict:
        """基于历史数据，分析品质变化趋势。"""
        if not self.db:
            return {"error": "趋势分析需要数据库连接"}

        since = datetime.now() - timedelta(days=days)
        query = self.db.query(models_db.GradeRecord).filter(
            models_db.GradeRecord.created_at >= since
        )
        if user_id:
            query = query.filter(models_db.GradeRecord.user_id == user_id)

        records = query.order_by(models_db.GradeRecord.created_at).all()
        if not records:
            return {"error": f"近 {days} 天内无历史记录", "records_count": 0}

        # 等级统计
        grade_counts = {"high": 0, "medium": 0, "low": 0}
        confidence_sum = 0
        daily_stats = {}

        for r in records:
            grade_counts[r.predicted_grade] = grade_counts.get(r.predicted_grade, 0) + 1
            confidence_sum += r.confidence

            day = r.created_at.strftime("%Y-%m-%d")
            if day not in daily_stats:
                daily_stats[day] = {"count": 0, "grades": [], "avg_confidence": 0}
            daily_stats[day]["count"] += 1
            daily_stats[day]["grades"].append(r.predicted_grade)

        total = len(records)
        avg_confidence = confidence_sum / total if total > 0 else 0

        # 趋势判断
        grade_score = {"high": 3, "medium": 2, "low": 1}
        if len(records) >= 5:
            first_half = records[: len(records) // 2]
            second_half = records[len(records) // 2 :]
            first_score = sum(grade_score[r.predicted_grade] for r in first_half) / len(first_half)
            second_score = sum(grade_score[r.predicted_grade] for r in second_half) / len(second_half)
            diff = second_score - first_score
            if diff > 0.3:
                trend = "上升（品质改善）"
                trend_direction = "up"
            elif diff < -0.3:
                trend = "下降（品质恶化）"
                trend_direction = "down"
            else:
                trend = "稳定"
                trend_direction = "stable"
        else:
            trend = "数据不足，无法判断趋势"
            trend_direction = "unknown"

        # 预警
        low_ratio = grade_counts.get("low", 0) / total if total > 0 else 0
        alerts = []
        if low_ratio > 0.2:
            alerts.append(f"低品质样品占比 {low_ratio*100:.1f}%，超过 20% 警戒线，建议排查生产环节。")
        if avg_confidence < 0.8:
            alerts.append(f"平均置信度仅 {avg_confidence*100:.1f}%，模型对近期样品判断不够确定，建议检查数据质量。")

        return {
            "period_days": days,
            "records_count": total,
            "grade_distribution": grade_counts,
            "grade_distribution_pct": {
                k: round(v / total * 100, 1) if total else 0
                for k, v in grade_counts.items()
            },
            "avg_confidence": round(avg_confidence, 4),
            "trend": trend,
            "trend_direction": trend_direction,
            "daily_breakdown": daily_stats,
            "alerts": alerts,
        }

    # ------------------------------------------------------------------ #
    # 工具 4：异常检测
    # ------------------------------------------------------------------ #
    def anomaly_detection(self, ph, temperature, taste, odor, fat, turbidity, colour,
                          grade, confidence, **kwargs) -> dict:
        """检测异常指标并触发预警。"""
        THRESHOLDS = {
            "pH": {"critical_low": 6.0, "critical_high": 7.5, "warning_low": 6.4, "warning_high": 7.0},
            "Temperature": {"critical_high": 55, "warning_high": 50},
            "Colour": {"critical_high": 260, "critical_low": 240, "warning_high": 255, "warning_low": 245},
        }

        BINARY_MUST = ["Taste", "Odor", "Fat", "Turbidity"]
        inputs = {
            "pH": ph, "Temperature": temperature, "Taste": taste,
            "Odor": odor, "Fat": fat, "Turbidity": turbidity, "Colour": colour,
        }

        warnings = []
        criticals = []

        # 连续指标检测
        for feat, bounds in THRESHOLDS.items():
            val = inputs[feat]
            if "critical_low" in bounds and val < bounds["critical_low"]:
                criticals.append({"feature": feat, "value": val, "reason": f"低于临界值 {bounds['critical_low']}"})
            elif "critical_high" in bounds and val > bounds["critical_high"]:
                criticals.append({"feature": feat, "value": val, "reason": f"高于临界值 {bounds['critical_high']}"})
            elif "warning_low" in bounds and val < bounds["warning_low"]:
                warnings.append({"feature": feat, "value": val, "reason": f"低于预警值 {bounds['warning_low']}"})
            elif "warning_high" in bounds and val > bounds["warning_high"]:
                warnings.append({"feature": feat, "value": val, "reason": f"高于预警值 {bounds['warning_high']}"})

        # 二元指标检测
        for feat in BINARY_MUST:
            if inputs[feat] == 0:
                criticals.append({"feature": feat, "value": 0, "reason": "不合格（应为 1）"})

        # 置信度异常
        if confidence < 0.6:
            warnings.append({"feature": "confidence", "value": confidence, "reason": "模型置信度偏低，判断不够确定"})

        alert_level = "normal"
        if criticals:
            alert_level = "critical"
        elif warnings:
            alert_level = "warning"

        return {
            "alert_level": alert_level,
            "alert_level_text": {"normal": "正常", "warning": "预警", "critical": "严重"}.get(alert_level),
            "critical_count": len(criticals),
            "warning_count": len(warnings),
            "criticals": criticals,
            "warnings": warnings,
            "recommendation": "立即处理" if alert_level == "critical" else (
                "关注并跟进" if alert_level == "warning" else "继续保持"
            ),
        }

    # ------------------------------------------------------------------ #
    # 工具 5：报告生成
    # ------------------------------------------------------------------ #
    def generate_report(self, ph, temperature, taste, odor, fat, turbidity, colour,
                        grade, confidence, probabilities, user_id=None, **kwargs) -> dict:
        """生成完整的品质分析报告（Markdown 格式）。"""

        # 先调用其他工具获取分析内容
        root_cause = self.root_cause_analysis(
            ph, temperature, taste, odor, fat, turbidity, colour,
            grade, confidence, probabilities
        )
        suggestions = self.improvement_suggestions(
            ph, temperature, taste, odor, fat, turbidity, colour, grade
        )
        anomaly = self.anomaly_detection(
            ph, temperature, taste, odor, fat, turbidity, colour, grade, confidence
        )

        grade_cn = {"high": "高（优）", "medium": "中（一般）", "low": "低（差）"}.get(grade, grade)

        report_md = f"""# 牛奶品质分析报告

> 生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 一、样品信息

| 指标 | 数值 | 理想范围 | 状态 |
|------|------|----------|------|
| pH | {ph} | 6.5 ~ 6.8 | {"正常" if 6.5 <= ph <= 6.8 else "异常"} |
| 温度 | {temperature} °C | 35 ~ 45 | {"正常" if 35 <= temperature <= 45 else "异常"} |
| 口感 | {taste} | 1 | {"正常" if taste == 1 else "异常"} |
| 气味 | {odor} | 1 | {"正常" if odor == 1 else "异常"} |
| 脂肪 | {fat} | 1 | {"正常" if fat == 1 else "异常"} |
| 浑浊度 | {turbidity} | 1 | {"正常" if turbidity == 1 else "异常"} |
| 颜色 | {colour} | 250 ~ 255 | {"正常" if 250 <= colour <= 255 else "异常"} |

## 二、分级结果

- **品质等级**：{grade_cn}
- **置信度**：{confidence*100:.2f}%
- **概率分布**：
  - 优 (high)：{probabilities.get('high', 0)*100:.2f}%
  - 中 (medium)：{probabilities.get('medium', 0)*100:.2f}%
  - 差 (low)：{probabilities.get('low', 0)*100:.2f}%

## 三、根因分析

{root_cause['summary']}

### 异常指标详情

"""
        if root_cause["issues"]:
            for issue in root_cause["issues"]:
                report_md += f"- **{issue['feature']}**：当前值 {issue['value']}，理想范围 {issue['ideal_range']}，偏离程度 {issue['severity']}\n"
        else:
            report_md += "所有指标均在理想范围内，无异常项。\n"

        report_md += f"""
## 四、改进建议

共 {suggestions['total_suggestions']} 条建议：

"""
        for i, item in enumerate(suggestions["action_plan"][:10], 1):
            report_md += f"{i}. 【{item['priority']}】{item['action']}\n"

        report_md += f"""
## 五、异常预警

- **预警级别**：{anomaly['alert_level_text']}
- **严重异常**：{anomaly['critical_count']} 项
- **一般预警**：{anomaly['warning_count']} 项

"""
        if anomaly["criticals"]:
            report_md += "### 严重异常\n\n"
            for c in anomaly["criticals"]:
                report_md += f"- {c['feature']}：{c['reason']}（值：{c['value']}）\n"
        if anomaly["warnings"]:
            report_md += "\n### 一般预警\n\n"
            for w in anomaly["warnings"]:
                report_md += f"- {w['feature']}：{w['reason']}（值：{w['value']}）\n"

        report_md += f"""
## 六、结论

{anomaly['recommendation']}。

---
*本报告由牛奶品质分级系统自动生成，仅供参考。*
"""

        return {
            "title": f"品质分析报告 - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "grade": grade,
            "alert_level": anomaly["alert_level"],
            "content": report_md,
            "summary": f"品质等级：{grade_cn}，{anomaly['recommendation']}。",
        }

    # ------------------------------------------------------------------ #
    # 工具 6：知识问答
    # ------------------------------------------------------------------ #
    def knowledge_qa(self, question: str, **kwargs) -> dict:
        """基于规则的牛奶品质知识问答。"""

        KB = {
            "ph": {
                "keywords": ["ph", "酸碱度", "酸碱", "ph值", "酸度", "碱性"],
                "answer": "牛奶的正常 pH 范围为 6.5~6.8。pH 偏低可能由于乳酸发酵或初乳混入；pH 偏高可能由于乳腺感染或碱性清洗剂残留。",
            },
            "temperature": {
                "keywords": ["温度", "冷链", "保存", "冷藏", "冷却", "高温", "低温", "升温", "降温", "热", "冷"],
                "answer": "挤奶后应在 2 小时内冷却至 4°C 以下。储存温度应保持在 0~4°C。温度过高会加速细菌繁殖，严重影响品质。",
            },
            "taste": {
                "keywords": ["口感", "味道", "味觉", "异味", "好吃", "难吃", "甜", "苦", "酸"],
                "answer": "正常牛奶口感微甜、醇厚。出现苦味、酸味或异味可能由于饲料问题、奶牛疾病或储存污染。",
            },
            "odor": {
                "keywords": ["气味", "臭味", "异味", "香味", "腥", "臭", "香"],
                "answer": "正常牛奶有淡淡乳香。出现腥臭、酸臭或饲料味可能由于奶牛酮病、乳腺炎或环境污染。",
            },
            "fat": {
                "keywords": ["脂肪", "脱脂", "全脂", "乳脂", "油脂", "油"],
                "answer": "牛奶脂肪含量一般为 3.0%~4.0%。脂肪过低可能由于营养不良或掺假；脂肪过高可能由于浓缩处理。",
            },
            "turbidity": {
                "keywords": ["浑浊", "浑浊度", "沉淀", "絮凝", "杂质", "澄清", "透明", "分层", "凝结"],
                "answer": "正常牛奶呈均匀乳浊液。出现沉淀、絮凝或分层可能由于蛋白质变性、微生物污染或储存不当。",
            },
            "colour": {
                "keywords": ["颜色", "色泽", "发黄", "发红", "白色", "血色", "乳白", "黄"],
                "answer": "正常牛奶呈乳白色或微黄色。颜色过深可能由于血乳混入或氧化；颜色过浅可能由于掺水或脂肪过低。",
            },
            "storage": {
                "keywords": ["储存", "保存", "保质期", "保鲜", "存放", "放置", "贮藏"],
                "answer": "生鲜牛奶在 0~4°C 条件下可保存 2~3 天。巴氏杀菌奶可保存 7~15 天。应避免光照和异味污染。",
            },
            "mastitis": {
                "keywords": ["乳腺炎", "乳腺", "感染", "体细胞", "炎症", "发炎"],
                "answer": "乳腺炎会导致牛奶中体细胞数增加、pH 升高、出现絮状物。应定期检测体细胞数（SCC），控制在 40 万/mL 以下。",
            },
            "grade": {
                "keywords": ["分级", "等级", "分类", "品质等级", "怎么分", "分几级", "级别"],
                "answer": "系统采用 XGBoost 机器学习模型，基于 7 项理化指标将牛奶分为三级：高（优）、中（一般）、低（差）。模型准确率超过 99%。",
            },
            "improvement": {
                "keywords": ["提高", "提升", "改善", "优化", "做好", "方法", "建议", "措施", "控制", "管理", "品质管理", "质量管理", "改进", "增强"],
                "answer": "提高牛奶品质可从以下方面入手：\n1. 源头把控：保证奶牛健康，定期体检，科学配饲；\n2. 挤奶卫生：挤奶前清洗消毒，避免环境污染；\n3. 冷链控制：挤奶后 2 小时内冷却至 4°C 以下；\n4. 设备清洁：定期清洗储奶罐和管道，防止微生物滋生；\n5. 质量检测：定期检测 pH、体细胞数、微生物指标；\n6. 及时隔离：发现问题奶立即隔离，避免交叉污染。",
            },
            "process": {
                "keywords": ["工艺", "流程", "生产", "加工", "挤奶", "杀菌", "巴氏", "均质", "灭菌", "工序"],
                "answer": "牛奶主要生产流程：挤奶 → 过滤 → 冷却 → 储存 → 运输 → 加工（均质、巴氏杀菌/超高温灭菌）→ 灌装 → 冷链配送。每个环节的温度控制和卫生管理都直接影响最终品质。",
            },
            "safety": {
                "keywords": ["安全", "标准", "国标", "检测", "指标", "合格", "不合格", "卫生", "菌落", "微生物", "大肠"],
                "answer": "牛奶安全关键指标包括：菌落总数（≤10 万 CFU/mL）、大肠杆菌（不得检出）、体细胞数（≤40 万/mL）、抗生素残留（不得检出）。应符合《GB 19301-2010 生乳》国家标准。",
            },
            "contamination": {
                "keywords": ["污染", "掺假", "掺水", "假奶", "变质", "坏掉", "酸败", "腐败", "不合格品"],
                "answer": "牛奶污染常见类型：微生物污染（细菌超标）、化学污染（抗生素/清洗剂残留）、物理污染（杂质/异物）、掺假（掺水/掺豆浆/掺尿素）。发现异常应立即隔离并追溯源头。",
            },
        }

        q = question.lower()
        for topic, data in KB.items():
            for kw in data["keywords"]:
                if kw in q:
                    return {"matched_topic": topic, "answer": data["answer"]}

        return {
            "matched_topic": None,
            "answer": "抱歉，我暂时无法回答这个问题。您可以询问关于 pH、温度、口感、气味、脂肪、浑浊度、颜色、储存或乳腺炎的相关知识。",
        }

    # ------------------------------------------------------------------ #
    # 工具 7：企业质量日报（按日期汇总收购数据，供管理层决策）
    # ------------------------------------------------------------------ #
    def enterprise_daily_report(self, date: str | None = None, user_id: int | None = None,
                                **kwargs) -> dict:
        """生成企业质量日报：收购统计、等级分布、来源排名、定价汇总、异常预警。"""
        if not self.db:
            return {"error": "企业日报需要数据库连接"}

        # 目标日期：未指定时默认取「最近有收购记录的日期」，避免演示/隔日打开时
        # "今天无数据" 导致空日报（生产语义上"今天"仍可通过传入 date 精确获取）。
        if date:
            try:
                target = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                return {"error": f"日期格式错误：{date}，应为 YYYY-MM-DD"}
        else:
            latest_q = self.db.query(models_db.GradeRecord.created_at)
            if user_id:
                latest_q = latest_q.filter(models_db.GradeRecord.user_id == user_id)
            latest = latest_q.order_by(models_db.GradeRecord.created_at.desc()).first()
            target = latest[0].date() if latest else datetime.now().date()

        # SQLite 存储 UTC，取当天 UTC 全天（本地时区 +8 会有偏移，演示可接受）
        day_start = datetime.combine(target, datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        query = self.db.query(models_db.GradeRecord).filter(
            models_db.GradeRecord.created_at >= day_start,
            models_db.GradeRecord.created_at < day_end,
        )
        if user_id:
            query = query.filter(models_db.GradeRecord.user_id == user_id)
        records = query.order_by(models_db.GradeRecord.created_at).all()
        if not records:
            return {"error": f"{target} 无收购记录", "date": str(target), "records_count": 0}

        grade_counts = {"high": 0, "medium": 0, "low": 0}
        price_sum = 0.0
        source_stats: dict[str, dict] = {}
        anomaly_count = 0

        for r in records:
            grade_counts[r.predicted_grade] = grade_counts.get(r.predicted_grade, 0) + 1
            if r.suggested_price:
                price_sum += r.suggested_price
            if r.confidence < 0.6 or r.predicted_grade == "low":
                anomaly_count += 1
            # 来源统计
            src = self.db.query(models_db.Source).filter(
                models_db.Source.id == r.source_id).first() if r.source_id else None
            src_name = src.name if src else "未标注来源"
            st = source_stats.setdefault(src_name, {"count": 0, "high": 0, "medium": 0, "low": 0, "price_sum": 0.0})
            st["count"] += 1
            st[r.predicted_grade] = st.get(r.predicted_grade, 0) + 1
            if r.suggested_price:
                st["price_sum"] += r.suggested_price

        total = len(records)
        # 来源质量排名（按 high 占比）
        ranking = sorted(
            [
                {
                    "source": name,
                    "count": st["count"],
                    "high_ratio": round(st["high"] / st["count"] * 100, 1),
                    "low_count": st["low"],
                    "avg_price": round(st["price_sum"] / st["count"], 2),
                }
                for name, st in source_stats.items()
            ],
            key=lambda x: x["high_ratio"], reverse=True,
        )

        grade_cn = {"high": "优", "medium": "中", "low": "差"}
        report_md = f"""# 牛奶收购质量日报 · {target}

> 由牛奶品质分级系统 Agent 自动生成

## 一、收购概况
- 收购记录：**{total} 条**
- 等级分布：优 {grade_counts['high']}（{grade_counts['high']/total*100:.1f}%）/ 中 {grade_counts['medium']}（{grade_counts['medium']/total*100:.1f}%）/ 差 {grade_counts['low']}（{grade_counts['low']/total*100:.1f}%）
- 建议收购总额：**¥{price_sum:.2f}**（基础价 ¥4.00/kg，优 ×1.15 / 中 ×1.00 / 差 ×0.75）

## 二、来源质量排名（按优质率）
| 排名 | 来源 | 收购数 | 优质率 | 差奶数 | 均价(元/kg) |
| --- | --- | --- | --- | --- | --- |
"""
        for i, s in enumerate(ranking, 1):
            report_md += f"| {i} | {s['source']} | {s['count']} | {s['high_ratio']}% | {s['low_count']} | {s['avg_price']} |\n"

        report_md += f"""
## 三、异常与预警
- 需关注记录：**{anomaly_count} 条**（低品质或低置信度）
"""
        if grade_counts["low"] / total > 0.2:
            report_md += f"- ⚠️ 当日差奶占比 {grade_counts['low']/total*100:.1f}%，超过 20% 警戒线，建议排查储运环节\n"
        worst = [s for s in ranking if s["low_count"] > 0]
        if worst:
            names = "、".join(s["source"] for s in worst)
            report_md += f"- ⚠️ 出现差奶的来源：{names}，建议追溯并现场检查\n"

        report_md += """
## 四、管理建议
"""
        best = ranking[0] if ranking else None
        if best:
            report_md += f"1. 优质率最高来源：**{best['source']}**（{best['high_ratio']}%），可提高收购量\n"
        if grade_counts["low"] > 0:
            report_md += f"2. 当日 {grade_counts['low']} 条差奶建议拒收或折价，并留存样品复检\n"
        report_md += "3. 持续监控温度敏感来源，挤奶后 2 小时内冷却至 4°C 以下\n"

        report_md += f"""
---
*本日报由 Agent 基于 {total} 条真实分级记录自动生成，定价系数可在系统配置中调整。*
"""

        return {
            "date": str(target),
            "records_count": total,
            "grade_distribution": grade_counts,
            "suggested_total_price": round(price_sum, 2),
            "anomaly_count": anomaly_count,
            "source_ranking": ranking,
            "content": report_md,
            "summary": f"{target} 收购 {total} 条，优 {grade_counts['high']}/中 {grade_counts['medium']}/差 {grade_counts['low']}，建议总额 ¥{price_sum:.2f}",
        }

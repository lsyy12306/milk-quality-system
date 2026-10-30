# -*- coding: utf-8 -*-
"""Agent 推理引擎：编排工具调用、管理多步推理流程。"""
from datetime import datetime
from typing import Any
from .tools import ToolRegistry
from .memory import AgentMemory


class AgentEngine:
    """
    牛奶品质分级智能体引擎。

    核心能力：
    1. 感知 → 调用 XGBoost 模型获取分级结果
    2. 推理 → 根因分析、异常检测
    3. 行动 → 改进建议、报告生成、趋势预测
    4. 记忆 → 用户偏好、会话上下文
    """

    def __init__(self, db=None):
        self.tools = ToolRegistry(db=db)
        self.memory = AgentMemory(db=db)
        self.db = db

    # ------------------------------------------------------------------ #
    # 核心入口：完整智能分析
    # ------------------------------------------------------------------ #
    def analyze(self, ph, temperature, taste, odor, fat, turbidity, colour,
                user_id=None) -> dict:
        """
        对单条样品执行完整的 Agent 分析流程：
        预测 → 根因分析 → 异常检测 → 改进建议 → 生成报告摘要。
        """
        from ..ml_model import predict_single

        # Step 1: 感知（模型预测）
        grade, confidence, probabilities = predict_single(
            ph, temperature, taste, odor, fat, turbidity, colour
        )

        # Step 2: 推理（根因 + 异常）
        root_cause = self.tools.call(
            "root_cause_analysis",
            ph=ph, temperature=temperature, taste=taste, odor=odor,
            fat=fat, turbidity=turbidity, colour=colour,
            grade=grade, confidence=confidence, probabilities=probabilities,
        )

        anomaly = self.tools.call(
            "anomaly_detection",
            ph=ph, temperature=temperature, taste=taste, odor=odor,
            fat=fat, turbidity=turbidity, colour=colour,
            grade=grade, confidence=confidence,
        )

        # Step 3: 行动（建议 + 报告）
        suggestions = self.tools.call(
            "improvement_suggestions",
            ph=ph, temperature=temperature, taste=taste, odor=odor,
            fat=fat, turbidity=turbidity, colour=colour, grade=grade,
        )

        report = self.tools.call(
            "generate_report",
            ph=ph, temperature=temperature, taste=taste, odor=odor,
            fat=fat, turbidity=turbidity, colour=colour,
            grade=grade, confidence=confidence, probabilities=probabilities,
            user_id=user_id,
        )

        # Step 4: 记忆（个性化洞察）
        insights = {}
        if user_id:
            insights = self.memory.get_user_insights(user_id)

        return {
            "analysis_id": f"anal_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "prediction": {
                "grade": grade,
                "confidence": confidence,
                "probabilities": probabilities,
            },
            "root_cause": root_cause,
            "anomaly": anomaly,
            "suggestions": suggestions,
            "report": {
                "title": report["title"],
                "summary": report["summary"],
                "alert_level": report["alert_level"],
                "full_report": report["content"],
            },
            "personalized": insights,
            "thinking_chain": [
                {"step": 1, "action": "模型预测", "result": f"等级={grade}, 置信度={confidence:.2%}"},
                {"step": 2, "action": "根因分析", "result": f"发现问题 {root_cause['issue_count']} 项"},
                {"step": 3, "action": "异常检测", "result": f"预警级别={anomaly['alert_level_text']}"},
                {"step": 4, "action": "改进建议", "result": f"生成建议 {suggestions['total_suggestions']} 条"},
                {"step": 5, "action": "报告生成", "result": "完成"},
            ],
        }

    # ------------------------------------------------------------------ #
    # 对话式交互
    # ------------------------------------------------------------------ #
    def chat(self, message: str, session_id: str, user_id=None) -> dict:
        """
        处理用户自然语言消息，返回 Agent 回复。
        支持：知识问答、趋势查询、分析请求。
        """
        msg_lower = message.lower().strip()

        # 保留会话上下文
        self.memory.add_message(session_id, "user", message)

        # 意图识别（简单关键词匹配）
        intent = self._detect_intent(msg_lower)

        if intent == "knowledge":
            # 知识问答
            resp = self.tools.call("knowledge_qa", question=message)
            if resp.get("matched_topic"):
                reply = resp["answer"]
            else:
                # 无精确匹配时返回友好引导
                reply = (
                    "这个问题涉及面比较广，我可以从以下几个方向帮你：\n"
                    "1. **品质指标**：pH、温度、口感、气味、脂肪、浑浊度、颜色的正常范围和异常原因\n"
                    "2. **品质提升**：如何提高牛奶品质、生产工艺优化、质量控制措施\n"
                    "3. **储存运输**：冷链管理、保质期、储存条件\n"
                    "4. **疾病防控**：乳腺炎预防、体细胞数控制\n"
                    "5. **安全标准**：国标要求、微生物检测、掺假识别\n\n"
                    "你可以具体说说想了解哪个方面，比如『pH 偏高怎么办』或『温度控制有什么要求』？"
                )

        elif intent == "trend":
            # 趋势查询
            if not user_id:
                reply = "请先登录后查看个人趋势分析。"
            else:
                days = self._extract_days(msg_lower) or 30
                trend = self.tools.call("trend_analysis", user_id=user_id, days=days)
                if "error" in trend:
                    reply = trend["error"]
                else:
                    reply = (
                        f"近 {trend['period_days']} 天共检测 {trend['records_count']} 条记录。\n"
                        f"品质趋势：{trend['trend']}\n"
                        f"等级分布：优 {trend['grade_distribution_pct'].get('high', 0)}%，"
                        f"中 {trend['grade_distribution_pct'].get('medium', 0)}%，"
                        f"差 {trend['grade_distribution_pct'].get('low', 0)}%\n"
                        f"平均置信度：{trend['avg_confidence']*100:.1f}%"
                    )
                    if trend["alerts"]:
                        reply += "\n\n⚠️ 预警：" + "\n".join(trend["alerts"])

        elif intent == "daily_report":
            # 企业日报
            if not user_id:
                reply = "请先登录后生成企业质量日报。"
            else:
                import re
                m = re.search(r"(\d{4}-\d{2}-\d{2})", msg_lower)
                report = self.tools.call(
                    "enterprise_daily_report",
                    date=m.group(1) if m else None,
                    user_id=user_id,
                )
                if "error" in report:
                    reply = report["error"]
                else:
                    reply = (
                        f"📋 {report['date']} 企业质量日报已生成：\n"
                        f"收购 {report['records_count']} 条，"
                        f"优 {report['grade_distribution']['high']} / "
                        f"中 {report['grade_distribution']['medium']} / "
                        f"差 {report['grade_distribution']['low']}\n"
                        f"建议收购总额：¥{report['suggested_total_price']:.2f}\n"
                        f"需关注记录：{report['anomaly_count']} 条\n\n"
                        f"完整日报可在「分析仪表盘 → 企业日报」中查看和导出。"
                    )

        elif intent == "greeting":
            reply = "你好！我是牛奶品质分级智能助手。我可以帮你：\n1. 分析样品品质\n2. 查询品质知识\n3. 查看历史趋势\n4. 生成分析报告与企业日报\n\n请告诉我你想了解什么？"

        elif intent == "analyze_request":
            reply = "请在「品质分级」页面输入 7 项理化指标，然后点击「智能分析」按钮，我将为你生成完整的分析报告。"

        else:
            # 默认知识问答兜底
            resp = self.tools.call("knowledge_qa", question=message)
            if resp.get("matched_topic"):
                reply = resp["answer"]
            else:
                reply = (
                    "这个问题涉及面比较广，我可以从以下几个方向帮你：\n"
                    "1. **品质指标**：pH、温度、口感、气味、脂肪、浑浊度、颜色的正常范围和异常原因\n"
                    "2. **品质提升**：如何提高牛奶品质、生产工艺优化、质量控制措施\n"
                    "3. **储存运输**：冷链管理、保质期、储存条件\n"
                    "4. **疾病防控**：乳腺炎预防、体细胞数控制\n"
                    "5. **安全标准**：国标要求、微生物检测、掺假识别\n\n"
                    "你可以具体说说想了解哪个方面，比如『pH 偏高怎么办』或『温度控制有什么要求』？"
                )

        self.memory.add_message(session_id, "assistant", reply)

        return {
            "reply": reply,
            "intent": intent,
            "session_id": session_id,
        }

    def _detect_intent(self, msg: str) -> str:
        """简单意图识别。"""
        greetings = ["你好", "您好", "hi", "hello", "在吗", "在嘛", "嗨"]
        if any(g in msg for g in greetings):
            return "greeting"

        # 企业日报意图（优先于 trend/knowledge）
        daily_keywords = ["日报", "今日报告", "每日报告", "今日收购", "当天收购", "汇总报告", "今日汇总"]
        if any(k in msg for k in daily_keywords):
            return "daily_report"

        trend_keywords = ["趋势", "走势", "变化", "历史", "统计", "最近", "近期", "过去"]
        if any(k in msg for k in trend_keywords):
            return "trend"

        knowledge_keywords = ["什么是", "为什么", "怎么", "如何", "多少", "ph", "温度", "储存",
                              "脂肪", "浑浊", "颜色", "气味", "口感", "乳腺炎", "分级", "等级",
                              "提高", "提升", "改善", "优化", "建议", "方法", "措施", "控制",
                              "管理", "工艺", "流程", "生产", "加工", "安全", "标准", "检测",
                              "污染", "掺假", "变质", "菌落", "卫生", "挤奶", "杀菌", "巴氏"]
        if any(k in msg for k in knowledge_keywords):
            return "knowledge"

        analyze_keywords = ["分析", "报告", "诊断", "检测", "评估", "帮我看"]
        if any(k in msg for k in analyze_keywords):
            return "analyze_request"

        return "unknown"

    def _extract_days(self, msg: str) -> int | None:
        """从消息中提取天数。"""
        import re
        # 匹配 "7天"、"30 天"、"最近一周" 等
        if "周" in msg or "星期" in msg:
            return 7
        if "月" in msg:
            return 30
        m = re.search(r'(\d+)\s*天', msg)
        if m:
            return int(m.group(1))
        return None

    # ------------------------------------------------------------------ #
    # 趋势分析快捷入口
    # ------------------------------------------------------------------ #
    def get_trends(self, user_id: int | None = None, days: int = 30) -> dict:
        """获取趋势分析结果。"""
        return self.tools.call("trend_analysis", user_id=user_id, days=days)

    # ------------------------------------------------------------------ #
    # 批量分析
    # ------------------------------------------------------------------ #
    def analyze_batch(self, records: list[dict], user_id=None) -> dict:
        """对多条记录执行批量智能分析。"""
        results = []
        for rec in records:
            analysis = self.analyze(
                ph=rec.get("ph", rec.get("pH")),
                temperature=rec.get("temperature", rec.get("Temperature")),
                taste=rec.get("taste", rec.get("Taste")),
                odor=rec.get("odor", rec.get("Odor")),
                fat=rec.get("fat", rec.get("Fat")),
                turbidity=rec.get("turbidity", rec.get("Turbidity")),
                colour=rec.get("colour", rec.get("Colour")),
                user_id=user_id,
            )
            results.append({
                "input": rec,
                "grade": analysis["prediction"]["grade"],
                "alert_level": analysis["anomaly"]["alert_level"],
                "summary": analysis["report"]["summary"],
            })

        # 汇总统计
        grade_counts = {"high": 0, "medium": 0, "low": 0}
        alert_counts = {"normal": 0, "warning": 0, "critical": 0}
        for r in results:
            grade_counts[r["grade"]] = grade_counts.get(r["grade"], 0) + 1
            alert_counts[r["alert_level"]] = alert_counts.get(r["alert_level"], 0) + 1

        return {
            "batch_size": len(records),
            "results": results,
            "summary": {
                "grade_distribution": grade_counts,
                "alert_distribution": alert_counts,
                "critical_samples": [r for r in results if r["alert_level"] == "critical"],
            },
        }

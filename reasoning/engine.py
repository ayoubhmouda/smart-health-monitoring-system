# reasoning/engine.py
from datetime import timedelta
from django.utils import timezone
from reasoning.predictors.base import BasePredictor
from reasoning.predictors.threshold_predictor import ThresholdPredictor
from context.models import ContextHistory
from reasoning.models import Insight


class ReasoningEngine:
    """
    محرك استدلال هجين وذكي:
    يجمع العلامات ويفحص القواعد والـ ML، مع تحديث طابع الوقت للإنذار النشط الحالي 
    في آخر 10 دقائق بدلاً من كتابة سجلات مكررة ومزعجة في الداتابيز.
    """

    def __init__(self, ml_predictor: BasePredictor):
        self.ml_predictor = ml_predictor
        self.threshold_predictor = ThresholdPredictor()

    def reason(self, monitored_element):
        latest_history = ContextHistory.objects.filter(
            monitored_element=monitored_element
        ).order_by('-recorded_at').first()

        if not latest_history:
            return []

        all_insights = []

        # 1. شبكة الأمان (قواعد الحدود السريرية الصارمة)
        threshold_insights = self.threshold_predictor.predict(latest_history)
        all_insights.extend(threshold_insights)

        # 2. الذكاء السياقي (التنبؤ المبكر بنموذج MIMIC-IV)
        ml_insights = self.ml_predictor.predict(latest_history)
        all_insights.extend(ml_insights)

        # 3. التقييم الفوري والمباشر للقواعد والبروتوكولات (العامة والمخصصة) للمريض من السياق مباشرة
        try:
            from rules.engine import evaluate_direct_rules
            rule_insights = evaluate_direct_rules(monitored_element, latest_history)
            all_insights.extend(rule_insights)
        except Exception as e:
            print("🚨 [ReasoningEngine] خطأ أثناء تقييم القواعد المباشرة:", str(e))

        # 🟢 4. تحديث السجل النشط الحالي أو إنشاء سجل جديد عند الاقتضاء (منع تكرار الكروت)
        saved_insights = []
        ten_minutes_ago = timezone.now() - timedelta(minutes=10)

        for insight in all_insights:
            # البحث عن استبصار نشط مشابه في آخر 10 دقائق لتحديثه
            existing_insight = Insight.objects.filter(
                monitored_element=insight.monitored_element,
                insight_type=insight.insight_type,
                source=insight.source,
                detected_at__gte=ten_minutes_ago
            ).order_by('-detected_at').first()

            if existing_insight:
                # تحديث طابع الوقت للإنذار الحالي في الداتابيز ليبقى وحيداً ومحدثاً
                existing_insight.detected_at = timezone.now()
                existing_insight.severity = insight.severity
                existing_insight.confidence = insight.confidence
                existing_insight.save()
                saved_insights.append(existing_insight)
            else:
                # إنشاء سجل خطر جديد تماماً لبدء دورة خطر جديدة
                insight.save()
                saved_insights.append(insight)

        return saved_insights
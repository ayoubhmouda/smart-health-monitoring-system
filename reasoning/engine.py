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
    يجمع العلامات ويفحص العتبات، والـ ML، والقواعد المباشرة معاً،
    مع الحفاظ المطلق على تاريخ بداية الرصد الأول (detected_at) ثابتاً دون مساس.
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
        try:
            threshold_insights = self.threshold_predictor.predict(latest_history)
            all_insights.extend(threshold_insights)
        except Exception as e:
            print("🚨 [ReasoningEngine] خطأ في توقعات العتبات (Thresholds):", str(e))

        # 2. الذكاء السياقي (التنبؤ المبكر بنموذج MIMIC-IV)
        try:
            ml_insights = self.ml_predictor.predict(latest_history)
            all_insights.extend(ml_insights)
        except Exception as e:
            print("🚨 [ReasoningEngine] خطأ في توقعات نموذج الـ ML:", str(e))

        # 3. التقييم الفوري والمباشر للقواعد والبروتوكولات السريرية
        try:
            from rules.engine import evaluate_direct_rules
            rule_insights = evaluate_direct_rules(monitored_element, latest_history)
            all_insights.extend(rule_insights)
        except Exception as e:
            print("🚨 [ReasoningEngine] خطأ أثناء تقييم القواعد المباشرة:", str(e))

        # 🟢 4. تحديث السجل النشط الحالي أو إنشاء سجل جديد عند الاقتضاء
        saved_insights = []
        ten_minutes_ago = timezone.now() - timedelta(minutes=10)

        for insight in all_insights:
            # التأكد من ربط الـ Insight بالسجل السياقي الأحدث (إلزامي وفقاً للموديل الجديد)
            if not getattr(insight, 'context_history_id', None):
                insight.context_history = latest_history

            # البحث عن استبصار نشط مشابه في آخر 10 دقائق
            existing_insight = Insight.objects.filter(
                monitored_element=insight.monitored_element,
                insight_type=insight.insight_type,
                source=insight.source,
                detected_at__gte=ten_minutes_ago
            ).order_by('-detected_at').first()

            if existing_insight:
                # 🟢 الحفاظ التام على وقت البداية الأول (detected_at) دون مساس!
                # نكتفي بتحديث الشدة ونسبة الثقة وأحدث سياق فقط
                existing_insight.severity = insight.severity
                existing_insight.confidence = insight.confidence
                existing_insight.context_history = latest_history
                
                # تم استبعاد detected_at لكي لا يُعاد كتابته أو تعديله في الداتابيز
                existing_insight.save(update_fields=['severity', 'confidence', 'context_history'])
                saved_insights.append(existing_insight)
            else:
                # إذا لم يكن محفوظاً بالفعل في قاعدة البيانات، نقوم بحفظه وسيسجل detected_at تلقائياً لأول مرة
                if not insight.id:
                    insight.save()
                saved_insights.append(insight)

        return saved_insights
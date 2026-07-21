from reasoning.predictors.base import BasePredictor
from reasoning.predictors.threshold_predictor import ThresholdPredictor
from context.models import ContextHistory


class ReasoningEngine:
    """
    محرك استدلال هجين: يجمع بين شبكة الأمان (ThresholdPredictor)
    والذكاء الاصطناعي الشامل (MLPredictor) لإصدار إنذارات وتنبؤات مبكرة.
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

        # 3. حفظ نتائج التنسيق والـ Insights في قاعدة البيانات
        for insight in all_insights:
            insight.save()

        return all_insights
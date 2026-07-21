from datetime import timedelta
from django.utils import timezone
from context.models import ContextHistory
from reasoning.models import Insight
from .base import BasePredictor


class ThresholdPredictor(BasePredictor):
    """
    شبكة أمان ذكية: تعتمد العتبات على مستوى النشاط.
    - في الراحة (Activity 0): عتبات ضيقة للإنذار المبكر.
    - في النشاط (Activity 2-3): توسيع عتبات (النبض، التنفس، الضغط الانقباضي) فقط.
    - لا تكرر نفس الإنذار خلال 5 دقائق.
    """

    # العتبات الأساسية (للراحة)
    BASE_THRESHOLDS = {
        'heart_rate': {'min': 50, 'max': 100, 'dynamic': True},
        'blood_pressure_systolic': {'min': 90, 'max': 140, 'dynamic': True},
        'blood_pressure_diastolic': {'min': 60, 'max': 90, 'dynamic': False},
        'oxygen_saturation': {'min': 92, 'max': 100, 'dynamic': False},  # لا تتأثر بالنشاط
        'body_temperature': {'min': 36.0, 'max': 37.8, 'dynamic': False}, # لا تتأثر بالنشاط
        'respiratory_rate': {'min': 12, 'max': 20, 'dynamic': True},
    }

    def predict(self, context_history: ContextHistory) -> list[Insight]:
        context = context_history.context
        phys_data = context.physiological_data or {}
        act_data = context.activity_data or {}
        activity_level = act_data.get('activity_level', 0)

        # 🛑 منع تكرار الإنذار خلال 5 دقائق
        five_min_ago = timezone.now() - timedelta(minutes=5)
        recent_alert = Insight.objects.filter(
            monitored_element=context_history.monitored_element,
            source=Insight.Source.THRESHOLD,
            detected_at__gte=five_min_ago
        ).exists()

        if recent_alert:
            return []

        # تحديد مُضاعِف التسامح بناءً على النشاط
        if activity_level >= 2:
            tolerance = 1.3
        elif activity_level == 1:
            tolerance = 1.1
        else:
            tolerance = 1.0

        for sensor_name, config in self.BASE_THRESHOLDS.items():
            value = phys_data.get(sensor_name)
            if value is not None:
                # تطبيق التسامح فقط على الميزات المقبولة ديناميكياً (كالنبض والتنفس)
                curr_tolerance = tolerance if config['dynamic'] else 1.0
                
                min_val = config['min'] / curr_tolerance
                max_val = config['max'] * curr_tolerance

                if value < min_val or value > max_val:
                    return [Insight(
                        monitored_element=context_history.monitored_element,
                        context_history=context_history,
                        insight_type=Insight.InsightType.CURRENT_ABNORMALITY,
                        severity=Insight.Severity.HIGH,
                        confidence=0.99,
                        source=Insight.Source.THRESHOLD,
                    )]
        return []
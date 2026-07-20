from .base import BasePredictor
from context.models import ContextHistory
from reasoning.models import Insight

class ThresholdPredictor(BasePredictor):
    """
    شبكة أمان ذكية: تعتمد العتبات على مستوى النشاط.
    - في الراحة (Activity 0): عتبات ضيقة للإنذار المبكر.
    - في النشاط (Activity 2-3): عتبات أوسع لتجنب الإنذارات الكاذبة.
    """

    # العتبات الأساسية (للراحة)
    BASE_THRESHOLDS = {
        'heart_rate': {'min': 50, 'max': 100},
        'blood_pressure_systolic': {'min': 90, 'max': 140},
        'blood_pressure_diastolic': {'min': 60, 'max': 90},
        'oxygen_saturation': {'min': 92, 'max': 101},
        'body_temperature': {'min': 36.0, 'max': 37.8},
        'respiratory_rate': {'min': 12, 'max': 20},
    }

    def predict(self, context_history: ContextHistory) -> list[Insight]:
        context = context_history.context
        phys_data = context.physiological_data or {}
        act_data = context.activity_data or {}
        activity_level = act_data.get('activity_level', 0)

        # تحديد مُضاعِف التسامح بناءً على النشاط
        if activity_level >= 2:
            tolerance = 1.3  # سماح أكبر
        elif activity_level == 1:
            tolerance = 1.1
        else:
            tolerance = 1.0  # لا تسامح في الراحة

        insights = []
        for sensor_name, base_thresholds in self.BASE_THRESHOLDS.items():
            value = phys_data.get(sensor_name)
            if value is not None:
                # تطبيق التسامح
                min_val = base_thresholds['min'] / tolerance
                max_val = base_thresholds['max'] * tolerance

                if value < min_val or value > max_val:
                    insights.append(Insight(
                        monitored_element=context_history.monitored_element,
                        context_history=context_history,
                        insight_type=Insight.InsightType.CURRENT_ABNORMALITY,
                        severity=Insight.Severity.HIGH,
                        confidence=0.99,
                        source=Insight.Source.THRESHOLD,
                    ))
                    break
        return insights
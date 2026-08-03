# threshold_predictor.py (النسخة الفسيولوجية الصامتة والخالصة)
from datetime import timedelta
from django.utils import timezone
from context.models import ContextHistory
from reasoning.models import Insight
from .base import BasePredictor


class ThresholdPredictor(BasePredictor):
    """
    شبكة أمان فسيولوجية خالصة: تفحص العلامات الحيوية الصارمة فقط 
    وتطلق إنذاراً فورياً إذا تم تجاوز الحدود الطبية الثابتة.
    """

    # العتبات السريرية الصارمة والمنفردة
    BASE_THRESHOLDS = {
        'heart_rate': {'min': 50, 'max': 100},
        'blood_pressure_systolic': {'min': 90, 'max': 140},
        'blood_pressure_diastolic': {'min': 60, 'max': 90},
        'oxygen_saturation': {'min': 92, 'max': 100},
        'body_temperature': {'min': 36.0, 'max': 37.8},
        'respiratory_rate': {'min': 12, 'max': 20},
    }

    def predict(self, context_history: ContextHistory) -> list[Insight]:
        context = context_history.context
        phys_data = context.physiological_data or {}

        # 🛑 1. منع تكرار الإنذار خلال 5 دقائق
        five_min_ago = timezone.now() - timedelta(minutes=5)
        recent_alert = Insight.objects.filter(
            monitored_element=context_history.monitored_element,
            source=Insight.Source.THRESHOLD,
            detected_at__gte=five_min_ago
        ).exists()

        if recent_alert:
            return []

        # 2. فحص تجاوز الحدود الجافة الثابتة فقط (دون إدخال النشاط أو حرارة الغرفة)
        for sensor_name, config in self.BASE_THRESHOLDS.items():
            value = phys_data.get(sensor_name)
            if value is not None:
                min_val = config['min']
                max_val = config['max']

                if value < min_val or value > max_val:
                    return [Insight(
                        monitored_element=context_history.monitored_element,
                        context_history=context_history,
                        insight_type=Insight.InsightType.CURRENT_ABNORMALITY,
                        severity=Insight.Severity.CRITICAL if value > (max_val * 1.1) else Insight.Severity.HIGH,
                        confidence=0.99,
                        source=Insight.Source.THRESHOLD,
                    )]
        return []
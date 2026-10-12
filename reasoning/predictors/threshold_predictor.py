from django.utils import timezone
from context.models import ContextHistory
from reasoning.models import Insight
from sensors.models import SensorType
from .base import BasePredictor


class ThresholdPredictor(BasePredictor):
    """
    شبكة أمان فسيولوجية موحدة واعية بالسياق الحركي للمريض مع فلتر استدامة:
    - ينشئ التنبيه فقط بعد استمرار الشذوذ لـ 60 ثانية (3 قراءات متتالية / دورتين كاملتين).
    - يمنع تكرار إنشاء Insights جديدة لنفس الأزمة القائمة.
    """

    def predict(self, context_history: ContextHistory) -> list[Insight]:
        phys_data = context_history.physiological_data or {}
        activity_data = context_history.activity_data or {}
        element = context_history.monitored_element

        ref_time = context_history.recorded_at or timezone.now()

        # 1. جلب آخر سجلين سابقين بدلاً من سجل واحد للتحقق من استمرار الخطر لـ 60 ثانية (3 قراءات)
        previous_histories = list(ContextHistory.objects.filter(
            monitored_element=element,
            recorded_at__lt=ref_time
        ).order_by('-recorded_at')[:2])

        # إذا لم توجد قراءتان سابقتان على الأقل، لا يمكن الجزم بمرور 60 ثانية
        if len(previous_histories) < 2:
            return []

        prev1_phys_data = previous_histories[0].physiological_data or {}  # قراءة 30 ثانية
        prev2_phys_data = previous_histories[1].physiological_data or {}  # قراءة 0 ثانية

        field_to_db_name = {
            'oxygen_saturation': 'Oxygen Saturation',
            'respiratory_rate': 'Respiratory Rate',
        }

        activity_level = int(activity_data.get('activity_level', 0))

        for field_name, db_name in field_to_db_name.items():
            value = phys_data.get(field_name)
            prev1_value = prev1_phys_data.get(field_name)
            prev2_value = prev2_phys_data.get(field_name)
            
            if value is None or prev1_value is None or prev2_value is None:
                continue

            sensor_type = SensorType.objects.filter(name=db_name).first()
            if not sensor_type:
                continue

            min_val = sensor_type.normal_min
            max_val = sensor_type.normal_max

            if field_name == 'respiratory_rate':
                if activity_level == 3:
                    max_val = 35.0
                    min_val = 14.0
                elif activity_level == 2:
                    max_val = 26.0
                    min_val = 12.0

            # أ. فحص القراءة الحالية (عند 60 ثانية)
            is_below = min_val is not None and value < min_val
            is_above = max_val is not None and value > max_val

            if is_below or is_above:
                # ب. فحص القراءة السابقة الأولى (عند 30 ثانية)
                prev1_is_bad = (min_val and prev1_value < min_val) or (max_val and prev1_value > max_val)
                # ج. فحص القراءة السابقة الثانية (عند 0 ثانية)
                prev2_is_bad = (min_val and prev2_value < min_val) or (max_val and prev2_value > max_val)

                # الشرط: يجب أن تكون القراءات الثلاث متتالية في الشذوذ (0ث -> 30ث -> 60ث)
                if not (prev1_is_bad and prev2_is_bad):
                    continue

                # 🟢 د. منع التكرار: إذا كان هناك Insight نشط ومفتوح لنفس المريض والمصدر، لا تنشئ سجلاً جديداً
                has_active_insight = Insight.objects.filter(
                    monitored_element=element,
                    source=Insight.Source.THRESHOLD,
                    status=Insight.Status.ACTIVE
                ).exists()

                if has_active_insight:
                    return []

                # هـ. تحديد الخطورة وإنشاء Insight واحد فقط عند اكتمال الـ 60 ثانية بالتمام
                severity_level = Insight.Severity.HIGH

                if field_name == 'oxygen_saturation' and is_below:
                    severity_level = Insight.Severity.CRITICAL
                elif field_name == 'respiratory_rate':
                    if (min_val and value <= min_val * 0.85) or (max_val and value >= max_val * 1.15) or value < 10:
                        severity_level = Insight.Severity.CRITICAL

                return [Insight(
                    monitored_element=element,
                    context_history=context_history,
                    insight_type=Insight.InsightType.CURRENT_ABNORMALITY,
                    severity=severity_level,
                    confidence=0.99,
                    source=Insight.Source.THRESHOLD,
                )]

        return []
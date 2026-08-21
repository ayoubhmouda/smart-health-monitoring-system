# reasoning/predictors/threshold_predictor.py
from context.models import ContextHistory
from reasoning.models import Insight
from sensors.models import SensorType
from .base import BasePredictor


class ThresholdPredictor(BasePredictor):
    """
    شبكة أمان فسيولوجية موحدة مع تفعيل "فلتر الاستدامة السريري":
    يمنع الإنذارات الكاذبة الناتجة عن حركة المريض أو الشوائب العابرة، 
    حيث يشترط بقاء القراءة شاذة لـ دورتين متتاليتين (30-60 ثانية) قبل تفجير الإنذار.
    """

    def predict(self, context_history: ContextHistory) -> list[Insight]:
        context = context_history.context
        phys_data = context.physiological_data or {}
        element = context_history.monitored_element

        # 🟢 1. جلب القراءة السابقة للمريض مباشرة للتحقق من استدامة الخطر (Persistence Validation)
        previous_history = ContextHistory.objects.filter(
            monitored_element=element,
            recorded_at__lt=context_history.recorded_at
        ).order_by('-recorded_at').first()

        prev_phys_data = {}
        if previous_history and previous_history.context:
            prev_phys_data = previous_history.context.physiological_data or {}

        field_to_db_name = {
            'oxygen_saturation': 'Oxygen Saturation',
            'respiratory_rate': 'Respiratory Rate',
        }

        for field_name, db_name in field_to_db_name.items():
            value = phys_data.get(field_name)
            prev_value = prev_phys_data.get(field_name)  # القراءة السابقة لفلترة الضوضاء
            
            if value is None:
                continue

            sensor_type = SensorType.objects.filter(name=db_name).first()
            if not sensor_type:
                continue

            min_val = sensor_type.normal_min
            max_val = sensor_type.normal_max

            # أ. فحص انحراف القراءة الحالية
            is_below_min = min_val is not None and value < min_val
            is_above_max = max_val is not None and value > max_val

            if is_below_min or is_above_max:
                
                # 🟢 ب. تطبيق فلتر الاستدامة السريري:
                # إذا كانت القراءة السابقة طبيعية، نعتبر الشذوذ الحالي ضوضاء مؤقتة ولا نرسل إنذاراً
                if prev_value is not None:
                    prev_is_below = min_val is not None and prev_value < min_val
                    prev_is_above = max_val is not None and prev_value > max_val
                    
                    if not (prev_is_below or prev_is_above):
                        # القراءة السابقة كانت طبيعية والحالية شاذة -> نكتم التنبيه وننتظر الدورة التالية للتأكيد!
                        continue

                # تفعيل الإنذار بعد التأكد من استدامته لـ دورتين متتاليتين
                severity_level = Insight.Severity.HIGH

                if field_name == 'oxygen_saturation' and is_below_min:
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
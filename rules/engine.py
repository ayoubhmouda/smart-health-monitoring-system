import logging
# pyrefly: ignore [missing-import]
from django.utils import timezone
from rules.models import Rule, CorrectiveAction

logger = logging.getLogger(__name__)


class RuleEngine:
    """
    محرك القواعد الذكي والواعٍ بالسياق:
    - يطابق الإنذارات (Insights) الخام وقيم الحساسات الفورية (Context) عبر الخرائط الفسيولوجية.
    - يتخذ القرار الطبي وينشئ الإجراءات التصحيحية (CorrectiveActions).
    """

    # 🟢 قاموس خرائط الميزات لربط الحقل بمساره في كائن السياق (Context)
    FIELD_MAP = {
        'heart_rate': ('physiological_data', 'heart_rate'),
        'oxygen_saturation': ('physiological_data', 'oxygen_saturation'),
        'body_temperature': ('physiological_data', 'body_temperature'),
        'blood_pressure_systolic': ('physiological_data', 'blood_pressure_systolic'),
        'blood_pressure_diastolic': ('physiological_data', 'blood_pressure_diastolic'),
        'respiratory_rate': ('physiological_data', 'respiratory_rate'),
        'activity_level': ('activity_data', 'activity_level'),
        'room_temperature': ('environmental_data', 'room_temperature'),
    }

    def _evaluate_condition(self, condition: dict, insight, context) -> bool:
        """يُقيم شرطاً فردياً واحداً من شروط بروتوكول العلاج ويطابقه سياقياً بالملي ثانية"""
        field = condition.get('field')
        op = condition.get('op')
        target_val = condition.get('value')

        current_val = None

        # 🟢 الاستخراج الذكي والموحد للقيمة الحيوية بناءً على الخرائط الفسيولوجية (FIELD_MAP)
        if field in self.FIELD_MAP:
            category, sub_key = self.FIELD_MAP[field]
            category_data = getattr(context, category, {}) or {}
            current_val = category_data.get(sub_key)
        elif field in ['insight_type', 'severity', 'source']:
            current_val = getattr(insight, field, None)

        if current_val is None:
            return False

        # مطابقة المعاملات المنطقية والرياضية بدقة كاملة
        try:
            if op == '==':
                return str(current_val).lower() == str(target_val).lower()
            elif op == '!=':
                return str(current_val).lower() != str(target_val).lower()
            elif op == '>':
                return float(current_val) > float(target_val)
            elif op == '<':
                return float(current_val) < float(target_val)
            elif op == '>=':
                return float(current_val) >= float(target_val)
            elif op == '<=':
                return float(current_val) <= float(target_val)
        except (ValueError, TypeError):
            return False

        return False

    def process(self, insight) -> list[CorrectiveAction]:
        """المصفي والمايسترو الرئيسي للقرار السريري"""
        active_rules = Rule.objects.filter(is_active=True)
        context_history = insight.context_history
        context = context_history.context
        
        created_actions = []

        for rule in active_rules:
            rule_data = rule.condition or {}
            conditions = rule_data.get('conditions', [])
            operator = rule_data.get('operator', 'AND')

            if not conditions:
                continue

            # تقييم جميع الشروط الفردية للقاعدة الحالية
            results = [self._evaluate_condition(cond, insight, context) for cond in conditions]

            # تصفية المنطق الكلي للقاعدة (AND لجميع الشروط، أو OR لأي شرط)
            is_triggered = False
            if operator == 'AND':
                is_triggered = all(results) if results else False
            elif operator == 'OR':
                is_triggered = any(results) if results else False

            # إذا انطبقت الشروط السريرية، ننشئ الإجراء التصحيحي (البطاقة التنبيهية)
            if is_triggered:
                action_template = rule.action_template or "notify_doctor_immediately"
                
                # كتابة صياغة طبية محترفة لوصف المشكلة للـ UI والأطباء
                desc = f"🚨 تنبيه من محرك القواعد لـ: [{rule.name}] للمريض [{insight.monitored_element.full_name}]. " \
                       f"الحالة المكتشفة: {insight.get_insight_type_display()} بدرجة خطورة ({insight.get_severity_display()}). " \
                       f"يتطلب الإجراء الفوري: {action_template}."

                # الحفظ الآمن لمنع تكرار نفس الإجراء لنفس الإنذار في قاعدة البيانات
                action, created = CorrectiveAction.objects.get_or_create(
                    insight=insight,
                    rule=rule,
                    defaults={
                        'description': desc,
                        'status': CorrectiveAction.Status.PENDING
                    }
                )
                
                if created:
                    created_actions.append(action)
                    logger.info(f"🚨 [RuleEngine] تم تفعيل الإجراء التصحيحي بنجاح: {desc}")

        return created_actions
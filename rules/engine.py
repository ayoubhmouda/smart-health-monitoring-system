# rules/engine.py
import logging
from datetime import timedelta
from django.utils import timezone
from rules.models import Rule, CorrectiveAction
from reasoning.models import Insight
from context.models import ContextHistory

logger = logging.getLogger(__name__)


def evaluate_direct_rules(monitored_element, context_history) -> list:
    """
    تقييم القواعد المخصصة والعامة مباشرة من السياق وتوليد كائنات Insight لها إذا تطابقت الشروط
    مع دمج صمام الاستدامة الزمنية الثنائي (المخصص للحساس أو الافتراضي للقاعدة).
    """
    active_rules = Rule.objects.filter(is_active=True)
    triggered_insights = []

    engine = RuleEngine()

    for rule in active_rules:
        # صمام أمان لمرضى العنبر
        if rule.monitored_element and rule.monitored_element_id != monitored_element.id:
            continue

        # تقييم القاعدة بالاستعانة بفلتر الاستدامة السريري الزمني المطور
        is_triggered = engine.evaluate_rule_temporally(rule, monitored_element, context_history)

        if is_triggered:
            existing = Insight.objects.filter(
                monitored_element=monitored_element,
                context_history=context_history,
                source='rules'
            ).exists()

            if not existing:
                insight = Insight(
                    monitored_element=monitored_element,
                    context_history=context_history,
                    insight_type=Insight.InsightType.CURRENT_ABNORMALITY,
                    severity=rule.severity,
                    confidence=1.0,
                    source='rules'
                )
                triggered_insights.append(insight)

    return triggered_insights


class RuleEngine:
    """
    Smart Clinical Rule Engine:
    - Evaluates patient context history and live vital readings against clinical rules.
    - Generates CorrectiveActions and saves them upon matching conditions.
    """

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

    def evaluate_rule_temporally(self, rule, monitored_element, latest_history) -> bool:
        """
        تقيم شروط القاعدة بالكامل مع دعم التخصيص الثنائي:
        تفحص مهلة الاستدامة المخصصة لكل حساس على حدة، وإذا لم توجد تعود للمهلة الافتراضية للقاعدة.
        """
        rule_data = rule.condition or {}
        conditions = rule_data.get('conditions', [])
        if not conditions:
            return False

        # جلب مهلة الاستدامة الافتراضية للقاعدة ككل كمرجع احتياطي
        global_duration = getattr(rule, 'duration_seconds', None) or rule_data.get('duration_seconds', 0)

        # تقييم الشرط الأول زمنياً
        is_triggered = self._evaluate_single_condition_temporally(
            conditions[0], monitored_element, latest_history, global_duration
        )

        # تقييم بقية الشروط التراكمية (AND / OR) مع احترام التخصيص الزمني لكل حساس
        for i in range(1, len(conditions)):
            cond = conditions[i]
            connector = cond.get('connector', 'AND')
            res = self._evaluate_single_condition_temporally(
                cond, monitored_element, latest_history, global_duration
            )

            if connector == 'OR':
                is_triggered = is_triggered or res
            else:  # AND
                is_triggered = is_triggered and res
                
        return is_triggered

    def _evaluate_single_condition_temporally(self, cond, monitored_element, latest_history, global_duration) -> bool:
        """تقييم شرط فردي واحد على نافذة زمنية مخصصة له تحديداً لاستبعاد الشوائب"""
        cond_duration = cond.get('duration_seconds')
        if cond_duration is None:
            cond_duration = global_duration

        if not cond_duration or int(cond_duration) <= 0:
            # تقييم فوري مباشر
            return self._evaluate_condition(cond, None, latest_history.context)

        # سحب النافذة الزمنية المخصصة لهذا الحساس تحديداً تحويلاً إلى قائمة
        start_time = latest_history.recorded_at - timedelta(seconds=int(cond_duration))
        
        historical_records = list(ContextHistory.objects.filter(
            monitored_element=monitored_element,
            recorded_at__gte=start_time,
            recorded_at__lte=latest_history.recorded_at
        ).order_by('recorded_at'))

        if not historical_records:
            return False

        # 🟢 صمام الأمان الرياضي لحل مشكلة الـ Cold Start:
        # نحسب الفارق الزمني الفعلي المتوفر بين أقدم وأحدث سجل في الكويري
        oldest_record_time = historical_records[0].recorded_at
        newest_record_time = historical_records[-1].recorded_at
        actual_span_seconds = (newest_record_time - oldest_record_time).total_seconds()

        # إذا كانت المدة الزمنية المتوفرة في الداتابيز أقل من المدة المطلوبة للشرط (مع سماح مرونة 5 ثوانٍ)، نكتم التنبيه فوراً!
        if actual_span_seconds < (int(cond_duration) - 5):
            print(f"⏱️ [RuleEngine] كتم التنبيه لـ Patient #{monitored_element.id} مؤقتاً: المتوفر {actual_span_seconds}ث، والمطلوب {cond_duration}ث.")
            return False

        # يجب أن يتحقق هذا الشرط الفردي في كل السجلات داخل نافذته الزمنية المخصصة بعد اكتمالها
        for hist_h in historical_records:
            if not hist_h.context:
                return False
            if not self._evaluate_condition(cond, None, hist_h.context):
                return False
                
        return True

    def _evaluate_condition(self, condition: dict, insight, context) -> bool:
        """Evaluates a single rule condition against the current patient context."""
        field = condition.get('field')
        op = condition.get('op')
        target_val = condition.get('value')

        current_val = None
        formatted_field = str(field).lower().replace(' ', '_') if field else ''

        if formatted_field in self.FIELD_MAP:
            category, sub_key = self.FIELD_MAP[formatted_field]
            category_data = getattr(context, category, {}) or {}
            current_val = category_data.get(sub_key)
        elif formatted_field in ['insight_type', 'severity', 'source']:
            current_val = getattr(insight, formatted_field, None)

        if current_val is None:
            return False

        try:
            res = False
            if op == '==':
                try:
                    res = float(current_val) == float(target_val)
                except (ValueError, TypeError):
                    res = str(current_val).lower() == str(target_val).lower()
            elif op == '!=':
                try:
                    res = float(current_val) != float(target_val)
                except (ValueError, TypeError):
                    res = str(current_val).lower() != str(target_val).lower()
            elif op == '>':
                res = float(current_val) > float(target_val)
            elif op == '<':
                res = float(current_val) < float(target_val)
            elif op == '>=':
                res = float(current_val) >= float(target_val)
            elif op == '<=':
                res = float(current_val) <= float(target_val)
                
            return res
            
        except (ValueError, TypeError) as err:
            return False

    def process(self, insight) -> list[CorrectiveAction]:
        """Evaluates all active clinical rules against a triggered insight."""
        active_rules = Rule.objects.filter(is_active=True)
        context_history = insight.context_history
        
        created_actions = []

        for rule in active_rules:
            if rule.monitored_element and rule.monitored_element_id != insight.monitored_element_id:
                continue

            is_triggered = self.evaluate_rule_temporally(rule, insight.monitored_element, context_history)

            if is_triggered:
                action_template = rule.action_template or "notify_doctor_immediately"
                
                desc = f"🚨 تنبيه من محرك القواعد لـ: [{rule.name}] للمريض [{insight.monitored_element.full_name}]. " \
                       f"الحالة المكتشفة: {insight.get_insight_type_display()} بدرجة خطورة ({insight.get_severity_display()}). " \
                       f"يتطلب الإجراء الفوري: {action_template}."

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
                    logger.info(f"🚨 [RuleEngine] CorrectiveAction successfully created: {desc}")

        return created_actions
# rules/engine.py (V14 Final - Production Ready)
import logging
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from rules.models import Rule, CorrectiveAction
from reasoning.models import Insight
from context.models import ContextHistory
from sensors.models import SensorType

logger = logging.getLogger(__name__)


def evaluate_direct_rules(monitored_element, context_history) -> list:
    """
    تقييم القواعد والعتبات وإدارة دورة الحياة السريرية للتنبيه (Alarm Lifecycle).
    - تنشئ أزمة واحدة فقط عند بداية الخطر (status=ACTIVE).
    - تمنع تكرار السجلات طالما الخطر مستمر.
    - تحدّث السجل نفسه إلى (status=RESOLVED) فور تعافي المريض وتغلق الإنذار تلقائياً.
    """
    if not context_history:
        return []

    engine = RuleEngine()
    progressions = engine.calculate_rules_progression(
        monitored_element, context_history, update_state=True
    )

    triggered_insights = []

    active_rules_map = {
        r.id: r for r in Rule.objects.filter(is_active=True).select_related('monitored_element')
    }

    for prog in progressions:
        rule_id = prog['rule_id']
        is_threshold = str(rule_id).startswith('threshold_')
        rule_ref_id = str(rule_id) if is_threshold else f"rule_{rule_id}"

        overall_prog = prog.get('overall_progress', 0)
        episode_key = f"active_episode_{monitored_element.id}_{rule_ref_id}"
        active_insight_id = cache.get(episode_key)

        # 🚨 الحالة 1: الخطر قائم ومكتمل (100%)
        if overall_prog >= 100:
            if active_insight_id:
                # الأزمة ما زالت مستمرة -> جلب السجل الحي الحالي
                try:
                    existing_insight = Insight.objects.get(id=active_insight_id)
                    triggered_insights.append(existing_insight)
                except Insight.DoesNotExist:
                    cache.delete(episode_key)
            else:
                # بداية أزمة سريرية جديدة -> إنشاء سجل واحد وحفظ المعرف في Redis
                if is_threshold:
                    rule_source = Insight.Source.THRESHOLD
                    severity = prog.get('severity_enum', Insight.Severity.HIGH)
                else:
                    rule = active_rules_map.get(rule_id)
                    if not rule:
                        continue

                    rule_source = (
                        Insight.Source.PATIENT_RULE
                        if prog.get('is_patient_specific')
                        else Insight.Source.GLOBAL_RULE
                    )
                    severity = rule.severity

                insight = Insight.objects.create(
                    monitored_element=monitored_element,
                    context_history=context_history,
                    insight_type=Insight.InsightType.CURRENT_ABNORMALITY,
                    severity=severity,
                    confidence=0.99 if is_threshold else 1.0,
                    source=rule_source,
                    status=Insight.Status.ACTIVE
                )

                # حفظ الأزمة في Redis لتظل نشطة حتى التعافي
                cache.set(episode_key, insight.id, timeout=None)
                triggered_insights.append(insight)

        # 🟢 الحالة 2: الخطر زال (أقل من 100%) مع وجود أزمة كانت نشطة
        else:
            if active_insight_id:
                try:
                    insight = Insight.objects.get(id=active_insight_id)
                    if insight.status != Insight.Status.RESOLVED:
                        insight.status = Insight.Status.RESOLVED
                        insight.resolved_at = timezone.now()
                        # إطلاق إشارة post_save ذاتياً لتحديث التنبيه عبر السوكيت
                        insight.save(update_fields=['status', 'resolved_at'])

                        logger.info(f"🟢 [Auto-Resolution] تعافي المريض {monitored_element.id} من القاعدة {rule_ref_id}")
                except Insight.DoesNotExist:
                    pass
                finally:
                    cache.delete(episode_key)

    return triggered_insights


class RuleEngine:
    """
    محرك القواعد السريرية V14 Final المعتمد:
    - إدارة دورة الحياة السريرية للتنبيهات (Alarm Lifecycle).
    - دعم الإغلاق والتعافي التلقائي الحقيقي عند زوال الخطر.
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

    @classmethod
    def _get_sensor_threshold(cls, sensor_type_name: str, default_min: float) -> float:
        cache_key = f"sensor_thresh_min_{sensor_type_name.lower().replace(' ', '_')}"
        cached_val = cache.get(cache_key)
        if cached_val is not None:
            return cached_val

        sensor_type = SensorType.objects.filter(name__iexact=sensor_type_name).first()
        min_val = sensor_type.normal_min if (sensor_type and sensor_type.normal_min is not None) else default_min
        cache.set(cache_key, min_val, timeout=3600)
        return min_val

    def _get_condition_temporal_state(
        self, cond, monitored_element, latest_history, rule_id, cond_idx, global_duration, insight=None, update_state=True
    ):
        field = cond.get('field')
        formatted_field = str(field).lower().replace(' ', '_') if field else ''

        if formatted_field in ['insight_type', 'severity', 'source']:
            matches = self._evaluate_condition(cond, insight, latest_history)
            return matches, 0, 0, matches

        cond_duration = cond.get('duration_seconds')
        if cond_duration is None:
            cond_duration = global_duration
        cond_dur = int(cond_duration or 0)

        is_matching = self._evaluate_condition(cond, insight, latest_history)
        cache_key = f"rule_state_{monitored_element.id}_{rule_id}_{cond_idx}"

        if not is_matching:
            if update_state:
                cache.delete(cache_key)
            return False, 0, cond_dur, False

        if cond_dur <= 0:
            return True, 0, 0, True

        now_ts = (
            latest_history.recorded_at.timestamp()
            if (latest_history and hasattr(latest_history, 'recorded_at') and latest_history.recorded_at)
            else timezone.now().timestamp()
        )
        timeout = max(cond_dur * 3, 300)

        state = cache.get(cache_key)

        if not state:
            if update_state:
                state = {
                    'first_triggered_at': now_ts,
                    'last_seen_at': now_ts,
                    'consecutive_cycles': 1
                }
                cache.set(cache_key, state, timeout=timeout)
            elapsed_seconds = 0.0
        else:
            last_seen = state.get('last_seen_at', now_ts)
            gap = now_ts - last_seen

            if gap > max(cond_dur + 30, 90):
                if update_state:
                    state = {
                        'first_triggered_at': now_ts,
                        'last_seen_at': now_ts,
                        'consecutive_cycles': 1
                    }
                    cache.set(cache_key, state, timeout=timeout)
                elapsed_seconds = 0.0
            else:
                if update_state and gap >= 1.0:
                    state['last_seen_at'] = now_ts
                    state['consecutive_cycles'] = state.get('consecutive_cycles', 1) + 1
                    cache.set(cache_key, state, timeout=timeout)

                elapsed_seconds = max(0.0, now_ts - state.get('first_triggered_at', now_ts))

        is_fulfilled = round(elapsed_seconds) >= cond_dur
        return True, elapsed_seconds, cond_dur, is_fulfilled

    def _check_system_thresholds_progression(self, monitored_element, latest_history, update_state=True) -> list:
        threshold_items = []
        phys_data = getattr(latest_history, 'physiological_data', {}) or {}
        act_data = getattr(latest_history, 'activity_data', {}) or {}
        activity_level = int(act_data.get('activity_level', 0))

        # 1. فحص تشبع الأكسجين
        o2_val = phys_data.get('oxygen_saturation')
        if o2_val is not None:
            min_o2 = self._get_sensor_threshold('Oxygen Saturation', 95.0)
            is_o2_abnormal = float(o2_val) < min_o2

            cache_key_o2 = f"threshold_state_{monitored_element.id}_o2"
            episode_key_o2 = f"active_episode_{monitored_element.id}_threshold_o2"
            is_active_o2_episode = bool(cache.get(episode_key_o2))

            now_ts = latest_history.recorded_at.timestamp() if hasattr(latest_history, 'recorded_at') and latest_history.recorded_at else timezone.now().timestamp()
            target_dur = 60

            if not is_o2_abnormal:
                if update_state:
                    cache.delete(cache_key_o2)
                if is_active_o2_episode:
                    threshold_items.append({
                        'rule_id': 'threshold_o2',
                        'rule_name': 'شبكة الأمان: هبوط تشبع الأكسجين',
                        'severity': 'critical',
                        'severity_display': 'حرج حاد',
                        'severity_enum': Insight.Severity.CRITICAL,
                        'is_patient_specific': False,
                        'duration_mode': 'global',
                        'overall_progress': 0,
                        'recipient': 'doctor_and_caregiver',
                        'conditions': []
                    })
            else:
                state = cache.get(cache_key_o2)
                if not state:
                    if update_state:
                        cache.set(cache_key_o2, {'first_triggered_at': now_ts, 'last_seen_at': now_ts}, timeout=180)
                    elapsed_o2 = 0.0
                else:
                    if update_state and (now_ts - state.get('last_seen_at', now_ts)) >= 1.0:
                        state['last_seen_at'] = now_ts
                        cache.set(cache_key_o2, state, timeout=180)
                    elapsed_o2 = max(0.0, now_ts - state.get('first_triggered_at', now_ts))

                sustained_sec = min(target_dur, round(elapsed_o2))
                prog_pct = min(100, round((sustained_sec / target_dur) * 100))

                threshold_items.append({
                    'rule_id': 'threshold_o2',
                    'rule_name': 'شبكة الأمان: هبوط تشبع الأكسجين',
                    'severity': 'critical',
                    'severity_display': 'حرج حاد',
                    'severity_enum': Insight.Severity.CRITICAL,
                    'is_patient_specific': False,
                    'duration_mode': 'global',
                    'overall_progress': prog_pct,
                    'recipient': 'doctor_and_caregiver',
                    'conditions': [{
                        'field': 'oxygen_saturation',
                        'field_label': 'تشبع الأكسجين',
                        'current_value': o2_val,
                        'op': '<',
                        'target_value': min_o2,
                        'is_matching': True,
                        'target_duration': target_dur,
                        'sustained_seconds': sustained_sec,
                        'remaining_seconds': max(0, target_dur - sustained_sec),
                        'progress': prog_pct
                    }]
                })

        # 2. فحص معدل التنفس
        rr_val = phys_data.get('respiratory_rate')
        if rr_val is not None:
            min_rr, max_rr = 12.0, 20.0
            if activity_level == 3:
                max_rr, min_rr = 35.0, 14.0
            elif activity_level == 2:
                max_rr, min_rr = 26.0, 12.0

            is_rr_abnormal = float(rr_val) < min_rr or float(rr_val) > max_rr
            cache_key_rr = f"threshold_state_{monitored_element.id}_rr"
            episode_key_rr = f"active_episode_{monitored_element.id}_threshold_rr"
            is_active_rr_episode = bool(cache.get(episode_key_rr))

            now_ts = latest_history.recorded_at.timestamp() if hasattr(latest_history, 'recorded_at') and latest_history.recorded_at else timezone.now().timestamp()
            target_dur = 60

            if not is_rr_abnormal:
                if update_state:
                    cache.delete(cache_key_rr)
                if is_active_rr_episode:
                    threshold_items.append({
                        'rule_id': 'threshold_rr',
                        'rule_name': 'شبكة الأمان: اضطراب معدل التنفس',
                        'severity': 'high',
                        'severity_display': 'خطورة عالية',
                        'severity_enum': Insight.Severity.HIGH,
                        'is_patient_specific': False,
                        'duration_mode': 'global',
                        'overall_progress': 0,
                        'recipient': 'doctor_and_caregiver',
                        'conditions': []
                    })
            else:
                state = cache.get(cache_key_rr)
                if not state:
                    if update_state:
                        cache.set(cache_key_rr, {'first_triggered_at': now_ts, 'last_seen_at': now_ts}, timeout=180)
                    elapsed_rr = 0.0
                else:
                    if update_state and (now_ts - state.get('last_seen_at', now_ts)) >= 1.0:
                        state['last_seen_at'] = now_ts
                        cache.set(cache_key_rr, state, timeout=180)
                    elapsed_rr = max(0.0, now_ts - state.get('first_triggered_at', now_ts))

                sustained_sec = min(target_dur, round(elapsed_rr))
                prog_pct = min(100, round((sustained_sec / target_dur) * 100))

                threshold_items.append({
                    'rule_id': 'threshold_rr',
                    'rule_name': 'شبكة الأمان: اضطراب معدل التنفس',
                    'severity': 'high',
                    'severity_display': 'خطورة عالية',
                    'severity_enum': Insight.Severity.HIGH,
                    'is_patient_specific': False,
                    'duration_mode': 'global',
                    'overall_progress': prog_pct,
                    'recipient': 'doctor_and_caregiver',
                    'conditions': [{
                        'field': 'respiratory_rate',
                        'field_label': 'معدل التنفس (سياقي)',
                        'current_value': rr_val,
                        'op': '><',
                        'target_value': f"{min_rr}-{max_rr}",
                        'is_matching': True,
                        'target_duration': target_dur,
                        'sustained_seconds': sustained_sec,
                        'remaining_seconds': max(0, target_dur - sustained_sec),
                        'progress': prog_pct
                    }]
                })

        return threshold_items

    def evaluate_rule_temporally(self, rule, monitored_element, latest_history, insight=None, update_state=False) -> bool:
        if not latest_history:
            return False

        progressions = self.calculate_rules_progression(
            monitored_element, latest_history, insight=insight, update_state=update_state
        )
        for prog in progressions:
            if prog['rule_id'] == rule.id:
                return prog.get('overall_progress', 0) >= 100

        return False

    def _calculate_overall_progress(self, cond_progress_items, conditions) -> int:
        if not cond_progress_items:
            return 0

        overall_progress = cond_progress_items[0]['progress']

        for i in range(1, len(cond_progress_items)):
            connector = (
                conditions[i].get('connector') or 
                conditions[i].get('logical_operator') or 
                'AND'
            ).upper()

            curr_prog = cond_progress_items[i]['progress']

            if connector == 'OR':
                overall_progress = max(overall_progress, curr_prog)
            else:  # AND
                overall_progress = min(overall_progress, curr_prog)

        return overall_progress

    def calculate_rules_progression(self, monitored_element, latest_history, insight=None, update_state=True) -> list:
        if not latest_history:
            return []

        patient_rules = Rule.objects.filter(
            monitored_element_id=monitored_element.id, is_active=True
        ).prefetch_related('overridden_rules')

        overridden_ids = set()
        for r in patient_rules:
            overridden_ids.update(r.overridden_rules.values_list('id', flat=True))

        global_rules = Rule.objects.filter(
            monitored_element__isnull=True, is_active=True
        ).exclude(id__in=overridden_ids)

        active_rules = list(patient_rules) + list(global_rules)
        progression_list = []

        for rule in active_rules:
            rule_data = rule.condition or {}
            conditions = rule_data.get('conditions', [])
            if not conditions:
                continue

            global_duration = getattr(rule, 'duration_seconds', None) or rule_data.get('duration_seconds', 0)
            has_custom_durations = any(c.get('duration_seconds') is not None for c in conditions)
            duration_mode = 'custom' if has_custom_durations else 'global'

            cond_progress_items = []

            for i, cond in enumerate(conditions):
                field = cond.get('field')
                formatted_field = str(field).lower().replace(' ', '_') if field else ''

                if formatted_field in ['insight_type', 'severity', 'source']:
                    continue

                is_matching, elapsed_sec, cond_dur, is_fulfilled = self._get_condition_temporal_state(
                    cond, monitored_element, latest_history, rule.id, i, global_duration, insight=insight, update_state=update_state
                )

                current_val = None
                if formatted_field in self.FIELD_MAP:
                    cat, sub_k = self.FIELD_MAP[formatted_field]
                    cat_data = getattr(latest_history, cat, {}) or {}
                    current_val = cat_data.get(sub_k)

                if not is_matching:
                    sustained_seconds = 0
                    progress_pct = 0
                elif cond_dur <= 0:
                    sustained_seconds = 0
                    progress_pct = 100
                else:
                    sustained_seconds = min(cond_dur, round(elapsed_sec))
                    progress_pct = min(100, round((sustained_seconds / cond_dur) * 100))

                remaining_sec = max(0, cond_dur - sustained_seconds) if cond_dur > 0 else 0

                cond_progress_items.append({
                    'field': formatted_field,
                    'field_label': self._get_field_arabic_label(formatted_field),
                    'current_value': current_val,
                    'op': cond.get('op'),
                    'target_value': cond.get('value'),
                    'is_matching': is_matching,
                    'target_duration': cond_dur,
                    'sustained_seconds': sustained_seconds,
                    'remaining_seconds': remaining_sec,
                    'progress': progress_pct
                })

            if not cond_progress_items:
                continue

            has_started = any(c['is_matching'] or c['sustained_seconds'] > 0 for c in cond_progress_items)

            episode_key = f"active_episode_{monitored_element.id}_rule_{rule.id}"
            is_active_episode = bool(cache.get(episode_key))

            if not has_started and not is_active_episode:
                continue

            overall_progress = self._calculate_overall_progress(cond_progress_items, conditions)

            progression_list.append({
                'rule_id': rule.id,
                'rule_name': rule.name,
                'severity': rule.severity,
                'severity_display': rule.get_severity_display(),
                'is_patient_specific': rule.monitored_element is not None,
                'duration_mode': duration_mode,
                'overall_progress': overall_progress,
                'recipient': rule_data.get('recipient', 'doctor_and_caregiver'),
                'conditions': cond_progress_items
            })

        threshold_progressions = self._check_system_thresholds_progression(
            monitored_element, latest_history, update_state=update_state
        )
        progression_list.extend(threshold_progressions)

        return progression_list

    def _get_field_arabic_label(self, field_name: str) -> str:
        labels = {
            'heart_rate': 'نبض القلب',
            'oxygen_saturation': 'تشبع الأكسجين',
            'body_temperature': 'حرارة الجسم',
            'blood_pressure_systolic': 'الضغط الانقباضي',
            'blood_pressure_diastolic': 'الضغط الانبساطي',
            'respiratory_rate': 'معدل التنفس',
            'activity_level': 'النشاط الحركي',
            'room_temperature': 'حرارة الغرفة'
        }
        return labels.get(field_name, field_name)

    def _evaluate_condition(self, condition: dict, insight, context_record) -> bool:
        field = condition.get('field')
        op = condition.get('op')
        target_val = condition.get('value')

        current_val = None
        formatted_field = str(field).lower().replace(' ', '_') if field else ''

        if formatted_field in self.FIELD_MAP:
            category, sub_key = self.FIELD_MAP[formatted_field]
            category_data = getattr(context_record, category, {}) or {}
            current_val = category_data.get(sub_key)
        elif formatted_field in ['insight_type', 'severity', 'source']:
            current_val = getattr(insight, formatted_field, None) if insight else None

        if current_val is None:
            return False

        try:
            if op == '==':
                try:
                    return float(current_val) == float(target_val)
                except (ValueError, TypeError):
                    return str(current_val).lower() == str(target_val).lower()
            elif op == '!=':
                try:
                    return float(current_val) != float(target_val)
                except (ValueError, TypeError):
                    return str(current_val).lower() != str(target_val).lower()
            elif op == '>':
                return float(current_val) > float(target_val)
            elif op == '<':
                return float(current_val) < float(target_val)
            elif op == '>=':
                return float(current_val) >= float(target_val)
            elif op == '<=':
                return float(current_val) <= float(target_val)

            return False
        except (ValueError, TypeError):
            return False

    def process(self, insight) -> list[CorrectiveAction]:
        active_rules = Rule.objects.filter(is_active=True).select_related('monitored_element')
        context_history = insight.context_history
        created_actions = []

        for rule in active_rules:
            if rule.monitored_element and rule.monitored_element_id != insight.monitored_element_id:
                continue

            is_triggered = self.evaluate_rule_temporally(
                rule, insight.monitored_element, context_history, insight=insight, update_state=False
            )

            if is_triggered:
                # 🟢 نص الطبيب كما هو، مع fallback آمن
                action_text = rule.action_template or "مراجعة المريض سريرياً فوراً"

                action, created = CorrectiveAction.objects.get_or_create(
                    insight=insight,
                    rule=rule,
                    defaults={
                        'description': action_text,
                        'status': CorrectiveAction.Status.PENDING
                    }
                )

                if created:
                    created_actions.append(action)
                    logger.info(f"🚨 [RuleEngine] CorrectiveAction created: {action_text}")

        return created_actions 
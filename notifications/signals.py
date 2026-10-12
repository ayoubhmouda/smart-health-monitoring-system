# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from rules.models import CorrectiveAction
from reasoning.models import Insight
from .models import InterestRegistration, Notification
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@receiver(post_save, sender=CorrectiveAction)
def create_notifications(sender, instance, created, **kwargs):
    if created:
        insight = instance.insight
        if not insight:
            return

        if insight.severity in [Insight.Severity.HIGH, Insight.Severity.CRITICAL]:
            monitored_element = insight.monitored_element

            registrations = InterestRegistration.objects.filter(
                monitored_element=monitored_element
            ).select_related('interested_party')

            for reg in registrations:
                Notification.objects.create(
                    corrective_action=instance,
                    insight=insight,
                    recipient=reg.interested_party,
                    message=f"{insight.get_insight_type_display()} ({insight.get_severity_display()}): {instance.description}"
                )

            # 🟢 حماية من خطأ NoneType إذا كان الإجراء ناتجاً عن شبكة الأمان (instance.rule is None)
            rule_condition = (instance.rule.condition or {}) if instance.rule else {}
            recipient = rule_condition.get('recipient', 'doctor_and_caregiver')

            # تحديد هوية البروتوكول العام بأمان
            is_global = (instance.rule.monitored_element is None) if instance.rule else False

            # استخلاص الاسم والتوصية بدقة للقواعد ولشبكة الأمان
            r_name = instance.rule.name if instance.rule else "شبكة الأمان السريرية (Threshold)"
            act_template = (instance.rule.action_template if (instance.rule and instance.rule.action_template) else instance.description)

            channel_layer = get_channel_layer()
            group_name = f"patient_alerts_group_{monitored_element.id}"
            
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_alert",
                    "monitored_element": monitored_element.id,
                    "message": instance.description,
                    "severity": insight.severity,
                    "source": insight.source,
                    "is_global_rule": is_global,
                    "rule_name": r_name,
                    "action_template": act_template,
                    "recipient": recipient,
                    "detected_at": insight.detected_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if insight.detected_at else timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                }
            )


@receiver(post_save, sender=Insight)
def broadcast_insight_notification(sender, instance, created, **kwargs):
    rule_name = None
    action_template = None
    is_global_rule = (instance.source == Insight.Source.GLOBAL_RULE)
    recipient = "doctor_and_caregiver"
    
    try:
        from rules.engine import RuleEngine
        from rules.models import CorrectiveAction

        # 1. للقواعد العادية: تشغيل محرك تقييم القواعد لتوليد الإجراء التصحيحي
        if created:
            RuleEngine().process(instance)
        
        # 🟢 2. لشبكة الأمان (Thresholds): إنشاء CorrectiveAction رسمي مثلها مثل القواعد تماماً
        if created and instance.source == Insight.Source.THRESHOLD and instance.severity in [Insight.Severity.HIGH, Insight.Severity.CRITICAL]:
            action_desc = (
                "تزويد المريض بالأكسجين الطبي فوراً وتفقد مجرى التنفس ومؤشرات الصدمة"
                if 'o2' in str(instance.insight_type).lower() or instance.severity == Insight.Severity.CRITICAL
                else "معاينة المريض وضبط وضعية الجلوس ومراقبة انتظام التنفس"
            )
            desc = f"🚨 إنذار شبكة الأمان السريرية ({instance.get_severity_display()}): {action_desc} لـ [{instance.monitored_element.full_name}]."
            
            # إنشاء الإجراء التصحيحي الرسمي (وهو بدوره سيطلق إشارة إنشاء Notification تلقائياً)
            CorrectiveAction.objects.create(
                insight=instance,
                rule=None,  # شبكة أمان فسيولوجية لا ترتبط بجدول Rule
                description=desc,
                status=CorrectiveAction.Status.PENDING
            )

        # 3. جلب أحدث إجراء تصحيحي مرتبط بالاستبصار (سواء كان ناتجاً عن قاعدة أو شبكة الأمان)
        action = CorrectiveAction.objects.filter(insight=instance).order_by('-id').first()
        
        if action:
            if action.rule:
                # بيانات قادمة من بروتوكول/قاعدة
                rule_name = action.rule.name
                action_template = action.rule.action_template or action.description
                is_global_rule = (action.rule.monitored_element is None)
                rule_condition = action.rule.condition or {}
                recipient = rule_condition.get('recipient', 'doctor_and_caregiver')
            else:
                # بيانات قادمة من شبكة الأمان (Threshold)
                rule_name = "شبكة الأمان السريرية (Threshold)"
                action_template = action.description
                is_global_rule = False
                recipient = "doctor_and_caregiver"

    except Exception as e:
        print("🚨 [Rule Engine / Signals] خطأ أثناء معالجة الإجراءات التصحيحية:", str(e))

    is_threshold = instance.source == Insight.Source.THRESHOLD
    is_ml_model = instance.source == Insight.Source.ML_MODEL
    is_rule = instance.source in [Insight.Source.GLOBAL_RULE, Insight.Source.PATIENT_RULE]
    is_severe = instance.severity in [Insight.Severity.HIGH, Insight.Severity.CRITICAL]

    if is_threshold or is_severe or is_ml_model or is_rule or rule_name:
        channel_layer = get_channel_layer()
        group_name = f"patient_alerts_group_{instance.monitored_element_id}"
        
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_insight_update",
                "insight": {
                    "id": instance.id,
                    "monitored_element": instance.monitored_element_id,
                    "insight_type": instance.insight_type,
                    "severity": instance.severity,
                    "confidence": float(instance.confidence) if instance.confidence else 1.0,
                    "source": instance.source,
                    "status": getattr(instance, 'status', 'active'),
                    "resolved_at": instance.resolved_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if getattr(instance, 'resolved_at', None) else None,
                    "rule_name": rule_name,
                    "action_template": action_template,
                    "is_global_rule": is_global_rule,
                    "recipient": recipient,
                    "detected_at": instance.detected_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if instance.detected_at else timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                },
                "timestamp": timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            }
        )
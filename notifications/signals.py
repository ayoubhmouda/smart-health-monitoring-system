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

            channel_layer = get_channel_layer()
            group_name = f"patient_alerts_group_{monitored_element.id}"
            
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_alert",
                    "monitored_element": monitored_element.id,
                    "message": instance.description,
                    "severity": insight.severity,
                    "action_template": instance.rule.action_template if instance.rule else "",
                    "detected_at": insight.detected_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if insight.detected_at else timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                }
            )

# notifications/signals.py

@receiver(post_save, sender=Insight)
def broadcast_insight_notification(sender, instance, created, **kwargs):
    # البث الفوري عبر السوكيت في الحالتين (الإنشاء والتعديل) لإبقاء شاشة المراقبة الطبية حية طوال الخطر
    rule_name = None
    action_template = None
    is_global_rule = False
    try:
        from rules.engine import RuleEngine
        # تفعيل محرك تقييم الإجراءات العلاجية فقط عند الإنشاء الأول لتجنب تكرار كتابة الإنذارات
        if created:
            RuleEngine().process(instance)
        
        from rules.models import CorrectiveAction
        # 🟢 تصفية ذكية بالباك إند: جلب أحدث إجراء تصحيحي مرتبط بقانون نشط حالياً فقط!
        action = CorrectiveAction.objects.filter(
            insight=instance,
            rule__is_active=True  # 👈 صمام الأمان: استبعاد القوانين المعطلة
        ).order_by('-id').first()  # 👈 جلب الأحدث دائماً
        
        if action and action.rule:
            rule_name = action.rule.name
            action_template = action.rule.action_template
            is_global_rule = (action.rule.monitored_element is None)
    except Exception as e:
        print("🚨 [Rule Engine] خطأ أثناء معالجة قوانين المريض:", str(e))

    is_threshold = instance.source == Insight.Source.THRESHOLD
    is_severe = instance.severity in [Insight.Severity.HIGH, Insight.Severity.CRITICAL]
    is_ml_model = instance.source == Insight.Source.ML_MODEL

    if is_threshold or is_severe or is_ml_model or rule_name:
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
                    "rule_name": rule_name,
                    "action_template": action_template,
                    "is_global_rule": is_global_rule,
                    "detected_at": instance.detected_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if instance.detected_at else timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                },
                "timestamp": timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            }
        )


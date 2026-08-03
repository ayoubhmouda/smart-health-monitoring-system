# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from rules.models import CorrectiveAction
from reasoning.models import Insight
from .models import InterestRegistration, Notification
# 🟢 استيراد مكتبة قنوات دجانغو للبث الفوري المشترك
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@receiver(post_save, sender=CorrectiveAction)
def create_notifications(sender, instance, created, **kwargs):
    if created:
        insight = instance.insight
        # لا نرسل تنبيهاً فورياً إلا إذا كانت الخطورة عالية أو حرجة
        if insight.severity in [Insight.Severity.HIGH, Insight.Severity.CRITICAL]:
            monitored_element = insight.monitored_element

            # أرشفة وحفظ الإشعارات صامتاً في قاعدة البيانات أولاً لتطبيق نمط المراقب
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

            # 🟢 5. تفعيل سحر الـ WebSockets: بث الإنذار فوراً عبر قنوات دجانغو لقنوات الاتصال المفتوحة
            channel_layer = get_channel_layer()
            group_name = f"patient_alerts_group_{monitored_element.id}"
            
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_alert",
                    "message": instance.description,
                    "severity": insight.severity,
                    "action_template": instance.rule.action_template,
                    "detected_at": insight.detected_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                }
            )
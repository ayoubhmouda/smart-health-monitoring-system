from django.db.models.signals import post_save
from django.dispatch import receiver
from rules.models import CorrectiveAction
from reasoning.models import Insight  # تأكد من هذا الاستيراد
from .models import InterestRegistration, Notification

@receiver(post_save, sender=CorrectiveAction)
def create_notifications(sender, instance, created, **kwargs):
    if created:
        insight = instance.insight
        # لا نرسل إشعارًا فوريًا إلا إذا كانت الخطورة عالية أو حرجة
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
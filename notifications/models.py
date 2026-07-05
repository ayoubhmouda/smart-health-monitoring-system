from django.db import models
from django.conf import settings
from core.models import MonitoredElement
from rules.models import CorrectiveAction
from reasoning.models import Insight

class InterestedParty(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class CareGiver(InterestedParty):
    pass


class MedicalPersonnel(InterestedParty):
    specialty = models.CharField(max_length=100, blank=True)


class InterestRegistration(models.Model):
    interested_party = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    monitored_element = models.ForeignKey(MonitoredElement, on_delete=models.CASCADE)
    notify_via = models.CharField(max_length=50, default='websocket')

    class Meta:
        unique_together = ('interested_party', 'monitored_element')

    def __str__(self):
        return f"{self.interested_party} interested in {self.monitored_element}"


class Notification(models.Model):
    corrective_action = models.ForeignKey(CorrectiveAction, on_delete=models.CASCADE, null=True, blank=True)
    insight = models.ForeignKey(Insight, on_delete=models.CASCADE, null=True, blank=True)
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient}: {self.message[:50]}"
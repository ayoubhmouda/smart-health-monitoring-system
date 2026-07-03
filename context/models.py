from django.db import models
from core.models import Patient, Elderly, Disabled

class Context(models.Model):
    monitored_element = models.ForeignKey(
        'core.MonitoredElement',
        on_delete=models.CASCADE,
        related_name='contexts'
    )
    physiological_data = models.JSONField(default=dict)
    activity_data = models.JSONField(default=dict)
    environmental_data = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Context for {self.monitored_element} at {self.timestamp}"

class ContextHistory(models.Model):
    monitored_element = models.ForeignKey(
        'core.MonitoredElement',
        on_delete=models.CASCADE,
        related_name='context_history'
    )
    context = models.OneToOneField(Context, on_delete=models.CASCADE)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['monitored_element', 'recorded_at']),
        ]

    def __str__(self):
        return f"History for {self.monitored_element} at {self.recorded_at}"
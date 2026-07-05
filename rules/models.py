from django.db import models
from reasoning.models import Insight

class Rule(models.Model):
    name = models.CharField(max_length=100)
    condition = models.JSONField(help_text="مثال: {'conditions': ['heart_rate > 130'], 'operator': 'AND'}")
    action_template = models.CharField(max_length=255, help_text="الإجراء المقترح، مثل: 'Notify doctor immediately'")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CorrectiveAction(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        ACKNOWLEDGED = 'acknowledged', 'Acknowledged'

    insight = models.ForeignKey(Insight, on_delete=models.CASCADE, related_name='corrective_actions')
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name='corrective_actions')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Action for {self.insight} via {self.rule.name}"
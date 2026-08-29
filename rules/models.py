# rules/models.py
from django.db import models
from reasoning.models import Insight


class Rule(models.Model):
    """
    نموذج القواعد السريرية والنظامية الواعية بالسياق:
    يحدد الشروط والتوصية ودرجة خطورة القاعدة من قبل الإدارة الطبية.
    """
    class Severity(models.TextChoices):
        MEDIUM = 'medium', 'متوسط'
        HIGH = 'high', 'عالي'
        CRITICAL = 'critical', 'حرج حاد'

    name = models.CharField(max_length=100)
    condition = models.JSONField(
        help_text="مثال: {'conditions': [{'field': 'heart_rate', 'op': '>', 'value': 120}], 'operator': 'AND'}"
    )
    action_template = models.CharField(
        max_length=255, 
        help_text="الإجراء أو التوصية المقترحة، مثل: 'Notify doctor immediately'"
    )
    severity = models.CharField(
        max_length=15, 
        choices=Severity.choices, 
        default=Severity.MEDIUM,
        help_text="درجة خطورة القاعدة المحددة من الإدارة الطبية"
    )
    monitored_element = models.ForeignKey(
        'core.MonitoredElement',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='custom_rules'
    )
    is_active = models.BooleanField(default=True)

    # 🟢 علاقة ManyToMany ذاتية الربط وصريحة لتجاوز وإلغاء القوانين العامة المحددة
    overridden_rules = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='overriding_rules',
        help_text="البروتوكولات السريرية العامة التي يتم إلغاؤها واستبدالها بهذه القاعدة المخصصة للمريض"
    )

    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"


class CorrectiveAction(models.Model):
    """
    نموذج الإجراء التصحيحي / التوصية السريرية الناتجة عن محرك القواعد
    """
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
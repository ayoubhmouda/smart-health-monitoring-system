# rules/models.py
from django.db import models


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

    # علاقة ManyToMany ذاتية الربط لتجاوز وإلغاء القوانين العامة المحددة للمريض
    overridden_rules = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='overriding_rules',
        help_text="البروتوكولات السريرية العامة التي يتم إلغاؤها واستبدالها بهذه القاعدة المخصصة للمريض"
    )

    class Meta:
        verbose_name = "Rule"
        verbose_name_plural = "Rules"

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

    insight = models.ForeignKey(
        'reasoning.Insight', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='corrective_actions'
    )
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE,null='True',blank='True',related_name='corrective_actions')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Corrective Action"
        verbose_name_plural = "Corrective Actions"
        ordering = ['-created_at']

    def __str__(self):
        # 🟢 قراءة اسم القاعدة بأمان أو وضع اسم شبكة الأمان إذا كانت rule فارغة
        rule_name = self.rule.name if self.rule else "شبكة الأمان السريرية (Threshold)"
        return f"Action for {rule_name} (Status: {self.get_status_display()})"


class RuleExecutionLog(models.Model):
    """
    سجل تنفيذ وتفعيل القواعد (MAPE Loop Execution Logs)
    """
    class Status(models.TextChoices):
        SUCCESS = 'success', 'تم بنجاح'
        FAILED = 'failed', 'فشل'

    rule = models.ForeignKey(
        Rule, 
        on_delete=models.CASCADE, 
        null='True', 
        blank='True', 
        related_name='execution_logs',
        help_text="القاعدة الطبية التي تم تفعيلها وتطبيقها"
    )
    monitored_element = models.ForeignKey(
        'core.MonitoredElement', 
        on_delete=models.CASCADE, 
        related_name='rule_execution_logs',
        help_text="المريض الذي انطلقت من أجله القاعدة"
    )
    triggered_at = models.DateTimeField(
        auto_now_add=True, 
        db_index=True,
        help_text="توقيت تفعيل وتنفيذ الإجراء"
    )
    context_snapshot = models.JSONField(
        default=dict, 
        blank=True, 
        help_text="لقطة حية لقيم الحساسات والنشاط والسياق البيئي للمريض عند لحظة تفعيل التنبيه"
    )
    action_executed = models.CharField(
        max_length=255, 
        help_text="قناة الإجراء المنفذ بالفعل (مثل: تنبيه فوري بالواجهة / بث SMS)"
    )
    status = models.CharField(
        max_length=15, 
        choices=Status.choices, 
        default=Status.SUCCESS,
        help_text="حالة تنفيذ الإجراء"
    )

    class Meta:
        verbose_name = "Rule Execution Log"
        verbose_name_plural = "Rule Execution Logs"
        ordering = ['-triggered_at']
        indexes = [
            models.Index(fields=['monitored_element', '-triggered_at']),
        ]

    
    def __str__(self):
        # 🟢 قراءة اسم القاعدة بأمان أو وضع اسم شبكة الأمان إذا كانت rule فارغة
        rule_name = self.rule.name if self.rule else "شبكة الأمان السريرية (Threshold)"
        patient_name = self.monitored_element.full_name if self.monitored_element else "مريض غير معروف"
        return f"Execution of {rule_name} for {patient_name} at {self.triggered_at}"
 # reasoning/models.py
from django.db import models
from core.models import MonitoredElement
from context.models import ContextHistory


class Insight(models.Model):
    class InsightType(models.TextChoices):
        CURRENT_ABNORMALITY = 'current_abnormality', 'Current Abnormality'
        PREDICTED_RISK = 'predicted_risk', 'Predicted Risk'

    class Severity(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'

    # 🟢 التقسيم السريري الصريح والرباعي للمصادر
    class Source(models.TextChoices):
        THRESHOLD = 'threshold', 'شبكة الأمان السريرية (Threshold)'
        ML_MODEL = 'ml_model', 'تنبؤ الذكاء الاصطناعي (ML Model)'
        GLOBAL_RULE = 'global_rule', 'بروتوكول عام للمستشفى'
        PATIENT_RULE = 'patient_rule', 'قاعدة سريرية خاصة بالمريض'

    # 🟢 دورة الحياة السريرية للتنبيه (Clinical Alarm Lifecycle)
    class Status(models.TextChoices):
        ACTIVE = 'active', 'نشط ومستمر (Active)'
        RESOLVED = 'resolved', 'تم التعافي وزوال الخطر (Resolved)'

    monitored_element = models.ForeignKey(MonitoredElement, on_delete=models.CASCADE, related_name='insights')
    context_history = models.ForeignKey(ContextHistory, on_delete=models.CASCADE)
    insight_type = models.CharField(max_length=25, choices=InsightType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices)
    confidence = models.FloatField(default=1.0)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.THRESHOLD)
    
    # 🟢 الحقول الجديدة لتتبع الأزمة الحية وانتهائها
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="طابع وقت زوال الخطر وتعافي المريض")

    def __str__(self):
        return f"{self.insight_type} - {self.severity} - {self.get_status_display()} ({self.monitored_element})"


class RiskPrediction(models.Model):
    class PredictionWindow(models.TextChoices):
        ONE_HOUR = '1h', '1 Hour'
        SIX_HOURS = '6h', '6 Hours'
        TWENTY_FOUR_HOURS = '24h', '24 Hours'

    insight = models.OneToOneField(Insight, on_delete=models.CASCADE)
    predicted_condition = models.CharField(max_length=100)
    probability = models.FloatField()
    prediction_window = models.CharField(max_length=5, choices=PredictionWindow.choices)
    contributing_features = models.JSONField(default=dict)
    model_version = models.ForeignKey('MLModelVersion', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class MLModelVersion(models.Model):
    version_name = models.CharField(max_length=50)
    trained_at = models.DateTimeField(auto_now_add=True)
    algorithm = models.CharField(max_length=30)
    training_data_size = models.IntegerField()
    accuracy = models.FloatField(null=True)
    precision = models.FloatField(null=True)
    recall = models.FloatField(null=True)
    f1_score = models.FloatField(null=True)
    feature_list = models.JSONField(default=list)
    model_file_path = models.CharField(max_length=200)
    is_active = models.BooleanField(default=False) 
 
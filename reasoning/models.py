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

    class Source(models.TextChoices):
        THRESHOLD = 'threshold', 'Threshold'
        ML_MODEL = 'ml_model', 'ML Model'

    monitored_element = models.ForeignKey(MonitoredElement, on_delete=models.CASCADE, related_name='insights')
    context_history = models.ForeignKey(ContextHistory, on_delete=models.CASCADE)
    insight_type = models.CharField(max_length=25, choices=InsightType.choices)
    severity = models.CharField(max_length=10, choices=Severity.choices)
    confidence = models.FloatField(default=1.0)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.THRESHOLD)
    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.insight_type} - {self.severity} ({self.monitored_element})"

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
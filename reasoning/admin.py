from django.contrib import admin
from .models import Insight, RiskPrediction, MLModelVersion

@admin.register(Insight)
class InsightAdmin(admin.ModelAdmin):
    list_display = ('monitored_element', 'insight_type', 'severity', 'source', 'confidence', 'detected_at')
    list_filter = ('insight_type', 'severity', 'source')
    search_fields = ('monitored_element__full_name',)

@admin.register(RiskPrediction)
class RiskPredictionAdmin(admin.ModelAdmin):
    list_display = ('insight', 'predicted_condition', 'probability', 'prediction_window', 'created_at')

@admin.register(MLModelVersion)
class MLModelVersionAdmin(admin.ModelAdmin):
    list_display = ('version_name', 'algorithm', 'accuracy', 'precision', 'recall', 'f1_score', 'is_active')
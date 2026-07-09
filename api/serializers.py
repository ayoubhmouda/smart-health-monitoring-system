# api/serializers.py
from rest_framework import serializers
from core.models import MonitoredElement, Patient, Elderly, Disabled, MedicalHistory
from sensors.models import Sensor, SensorType, DataSourceConfig, SensorReading
from context.models import Context, ContextHistory
from reasoning.models import Insight, RiskPrediction, MLModelVersion
from rules.models import Rule, CorrectiveAction
from notifications.models import Notification

# --- Core ---
class MonitoredElementSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField() # لعرض العمر المحسوب
    class Meta:
        model = MonitoredElement
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    element = MonitoredElementSerializer()
    class Meta:
        model = Patient
        fields = '__all__'

class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = '__all__'  

# --- Sensors ---
class SensorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorType
        fields = '__all__'

class SensorSerializer(serializers.ModelSerializer):
    sensor_type = SensorTypeSerializer()
    class Meta:
        model = Sensor
        fields = '__all__'

class DataSourceConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSourceConfig
        fields = '__all__'

class SensorReadingSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer()
    class Meta:
        model = SensorReading
        fields = '__all__'

# --- Context ---
class ContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Context
        fields = '__all__'

class ContextHistorySerializer(serializers.ModelSerializer):
    context = ContextSerializer()
    class Meta:
        model = ContextHistory
        fields = '__all__'

# --- Reasoning ---
class InsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insight
        fields = '__all__'

# --- Rules ---
class CorrectiveActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrectiveAction
        fields = '__all__'

# --- Notifications ---
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
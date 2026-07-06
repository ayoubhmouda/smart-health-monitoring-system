# api/views.py
from rest_framework import viewsets
from core.models import MonitoredElement, Patient, MedicalHistory
from sensors.models import Sensor, SensorType, DataSourceConfig, SensorReading
from context.models import Context, ContextHistory
from reasoning.models import Insight
from rules.models import CorrectiveAction
from notifications.models import Notification
from .serializers import (
    MonitoredElementSerializer, PatientSerializer, MedicalHistorySerializer,
    SensorTypeSerializer, SensorSerializer, DataSourceConfigSerializer, SensorReadingSerializer,
    ContextSerializer, ContextHistorySerializer,
    InsightSerializer, CorrectiveActionSerializer, NotificationSerializer
)

class MonitoredElementViewSet(viewsets.ModelViewSet):
    queryset = MonitoredElement.objects.all()
    serializer_class = MonitoredElementSerializer

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

class MedicalHistoryViewSet(viewsets.ModelViewSet):
    queryset = MedicalHistory.objects.all()
    serializer_class = MedicalHistorySerializer

class SensorTypeViewSet(viewsets.ModelViewSet):
    queryset = SensorType.objects.all()
    serializer_class = SensorTypeSerializer

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

class DataSourceConfigViewSet(viewsets.ModelViewSet):
    queryset = DataSourceConfig.objects.all()
    serializer_class = DataSourceConfigSerializer

class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all().order_by('-recorded_at')
    serializer_class = SensorReadingSerializer

class ContextViewSet(viewsets.ModelViewSet):
    queryset = Context.objects.all()
    serializer_class = ContextSerializer

class ContextHistoryViewSet(viewsets.ModelViewSet):
    queryset = ContextHistory.objects.all()
    serializer_class = ContextHistorySerializer

class InsightViewSet(viewsets.ModelViewSet):
    queryset = Insight.objects.all().order_by('-detected_at')
    serializer_class = InsightSerializer

class CorrectiveActionViewSet(viewsets.ModelViewSet):
    queryset = CorrectiveAction.objects.all()
    serializer_class = CorrectiveActionSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
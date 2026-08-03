# api/views.py

from rest_framework import viewsets, status
import django_filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from core.models import MonitoredElement, Patient, MedicalHistory
from sensors.models import Sensor, SensorType, DataSourceConfig, SensorReading
from context.models import Context, ContextHistory
from reasoning.models import Insight
from rules.models import CorrectiveAction
from notifications.models import Notification
from accounts.models import User

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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['monitored_element']

class SensorTypeViewSet(viewsets.ModelViewSet):
    queryset = SensorType.objects.all()
    serializer_class = SensorTypeSerializer

class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all().select_related('sensor_type')
    serializer_class = SensorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['monitored_element']

class DataSourceConfigViewSet(viewsets.ModelViewSet):
    queryset = DataSourceConfig.objects.all()
    serializer_class = DataSourceConfigSerializer

# 2. 🟢 تعريف كلاس فلترة مخصص لدعم العلاقات المتداخلة (__ Lookup) بضمان 100%
class SensorReadingFilter(django_filters.FilterSet):
    class Meta:
        model = SensorReading
        fields = {
            'sensor': ['exact'],
            'sensor__monitored_element': ['exact'], # دعم فلترة القراءات بمعرف المريض العكسي
        }

# 3. الـ ViewSet المحدث والمربوط بكلاس الفلترة الجديد
class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all().order_by('-recorded_at')
    serializer_class = SensorReadingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    
    filterset_class = SensorReadingFilter
    

class ContextViewSet(viewsets.ModelViewSet):
    queryset = Context.objects.all()
    serializer_class = ContextSerializer

class ContextHistoryViewSet(viewsets.ModelViewSet):
    queryset = ContextHistory.objects.all()
    serializer_class = ContextHistorySerializer

class InsightViewSet(viewsets.ModelViewSet):
    queryset = Insight.objects.all().order_by('-detected_at')
    serializer_class = InsightSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['monitored_element']

class CorrectiveActionViewSet(viewsets.ModelViewSet):
    queryset = CorrectiveAction.objects.all()
    serializer_class = CorrectiveActionSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


# =========================================================
# API Endpoints مخصصة لعمليات المصادقة
# =========================================================
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    role = request.data.get('role', User.Role.CAREGIVER)

    if not username or not password:
        return Response({'error': 'اسم المستخدم وكلمة المرور مطلوبان'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'اسم المستخدم موجود مسبقاً'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        role=role
    )
    return Response({'message': 'تم إنشاء الحساب بنجاح', 'user_id': user.id}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'full_name': user.get_full_name() or user.username
    })
# api/views.py
from datetime import datetime
from django.db import transaction
from django.db.models import Q
import django_filters
from rest_framework.decorators import action
from rules.models import Rule, CorrectiveAction, RuleExecutionLog
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination

# تم التكييف: استيراد الموديلات المعتمدة فقط دون الكيانات الملغاة (Patient, Context)
from accounts.models import User
from core.models import MonitoredElement, MedicalHistory
from sensors.models import Sensor, SensorType, DataSourceConfig, SensorReading
from context.models import ContextHistory
from reasoning.models import Insight
from rules.models import Rule, CorrectiveAction
from notifications.models import Notification, InterestRegistration

from .serializers import (
    MonitoredElementSerializer, MedicalHistorySerializer,
    SensorTypeSerializer, SensorSerializer, DataSourceConfigSerializer, SensorReadingSerializer,
    ContextHistorySerializer,
    InsightSerializer, CorrectiveActionSerializer, NotificationSerializer,
    DoctorSerializer, RuleSerializer
)


# ==============================================================================
# 🛡️ 1. صمامات الأمان والتحقق من الصلاحيات (Security Permissions)
# ==============================================================================
class IsDoctorOrReadOnly(BasePermission):
    """
    صمام أمان للسجل الطبي وبيانات المرضى:
    - القراءة متاحة للجميع (أطباء، مقدمي رعاية، مشرفين).
    - التعديل والكتابة (PUT, PATCH, DELETE):
      * محصورة بالطبيب المعالج المشرف على المريض فقط.
      * أو إذا كان المريض جديداً وغير مسند لطبيب بعد (obj.doctor is None).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_superuser or getattr(request.user, 'role', '') in ['admin', 'doctor']

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if isinstance(obj, MonitoredElement):
            return obj.doctor is None or obj.doctor == request.user

        if isinstance(obj, MedicalHistory):
            return obj.monitored_element.doctor is None or obj.monitored_element.doctor == request.user

        return False


class IsAdminOrPatientRulePermission(BasePermission):
    """
    صلاحية حماية القواعد والبروتوكولات (RuleViewSet):
    - القراءة متاحة لجميع المستخدمين الموثقين.
    - القواعد العامة للمستشفى (monitored_element is None): تعديلها للأدمن فقط.
    - القواعد الخاصة بمريض معين: تعديلها وإنشاؤها وحذفها محصور بالطبيب المشرف على المريض.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method == 'POST':
            patient_id = request.data.get('monitored_element')
            if patient_id:
                patient = MonitoredElement.objects.filter(id=patient_id).first()
                return patient and (patient.doctor is None or patient.doctor == request.user)
            else:
                return request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'

        return request.user.is_superuser or getattr(request.user, 'role', '') in ['admin', 'doctor']

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        if obj.monitored_element:
            return obj.monitored_element.doctor is None or obj.monitored_element.doctor == request.user

        return request.user.is_superuser or getattr(request.user, 'role', '') == 'admin'


class IsAdminOrSelf(BasePermission):
    """صلاحية لحسابات الأطباء: الطبيب يعدل حسابه فقط، والإدارة الشاملة للأدمن."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        if request.method in ['POST', 'DELETE']:
            return request.user and (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin')
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or getattr(request.user, 'role', '') == 'admin':
            return True
        return obj.id == request.user.id


# ==============================================================================
# 📄 2. أدوات الفلترة والترقيم (Pagination & Filtering)
# ==============================================================================

class StandardResultsSetPagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 1000

class AlertsPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200

class SensorReadingFilter(django_filters.FilterSet):
    class Meta:
        model = SensorReading
        fields = {
            'sensor': ['exact'],
            'sensor__monitored_element': ['exact'],
        }


# ==============================================================================
# 🏥 3. الواجهات والمجموعات البرمجية (ViewSets)
# ==============================================================================

class MonitoredElementViewSet(viewsets.ModelViewSet):
    queryset = MonitoredElement.objects.all()
    serializer_class = MonitoredElementSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user, 'role', '') == 'admin':
            return MonitoredElement.objects.all()
        elif getattr(user, 'role', '') == 'doctor':
            return MonitoredElement.objects.filter(Q(doctor=user) | Q(doctor__isnull=True))
        elif getattr(user, 'role', '') == 'caregiver':
            return MonitoredElement.objects.filter(caregivers=user)
        return MonitoredElement.objects.none()

    def create(self, request, *args, **kwargs):
        data = request.data
        full_name = data.get('full_name')
        date_of_birth = data.get('date_of_birth')
        gender = data.get('gender')
        element_type = data.get('element_type', MonitoredElement.ElementType.PATIENT)
        chronic_conditions = data.get('chronic_conditions', [])
        
        diagnosis = data.get('diagnosis')
        admission_date = data.get('admission_date') or None
        mobility_level = data.get('mobility_level')
        disability_type = data.get('disability_type')

        caregiver_option = data.get('caregiver_option', 'none')
        caregiver_id = data.get('existing_caregiver_id')
        new_caregiver_username = data.get('caregiver_username')
        new_caregiver_name = data.get('caregiver_full_name')
        new_caregiver_password = data.get('caregiver_password')
        new_caregiver_phone = data.get('caregiver_phone_number', '')

        if not full_name or not date_of_birth or not gender:
            return Response({'error': 'جميع بيانات العنصر المراقب الأساسية مطلوبة'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                assigned_caregiver = None
                if caregiver_option == 'new' and new_caregiver_username and new_caregiver_password:
                    if User.objects.filter(username=new_caregiver_username).exists():
                        return Response({'error': 'اسم مستخدم مقدم الرعاية موجود مسبقاً'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    name_parts = new_caregiver_name.strip().split(' ', 1) if new_caregiver_name else []
                    first_name = name_parts[0] if name_parts else ''
                    last_name = name_parts[1] if len(name_parts) > 1 else ''

                    assigned_caregiver = User.objects.create_user(
                        username=new_caregiver_username,
                        password=new_caregiver_password,
                        phone_number=new_caregiver_phone,
                        first_name=first_name,
                        last_name=last_name,
                        role='caregiver'
                    )
                elif caregiver_option == 'existing' and caregiver_id:
                    assigned_caregiver = User.objects.filter(id=caregiver_id, role='caregiver').first()

                monitored_element = MonitoredElement.objects.create(
                    full_name=full_name,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    element_type=element_type,
                    doctor=request.user,
                    diagnosis=diagnosis,
                    admission_date=admission_date,
                    mobility_level=mobility_level,
                    disability_type=disability_type
                )
                
                if assigned_caregiver:
                    monitored_element.caregivers.add(assigned_caregiver)

                MedicalHistory.objects.create(
                    monitored_element=monitored_element,
                    chronic_conditions=chronic_conditions
                )

                InterestRegistration.objects.get_or_create(
                    monitored_element=monitored_element,
                    interested_party=request.user
                )
                if assigned_caregiver:
                    InterestRegistration.objects.get_or_create(
                        monitored_element=monitored_element,
                        interested_party=assigned_caregiver
                    )

                default_sensor_types = [
                    ('Heart Rate', SensorType.Category.PHYSIOLOGICAL, 'bpm'),
                    ('Oxygen Saturation', SensorType.Category.PHYSIOLOGICAL, '%'),
                    ('Body Temperature', SensorType.Category.PHYSIOLOGICAL, '°C'),
                    ('Blood Pressure Systolic', SensorType.Category.PHYSIOLOGICAL, 'mmHg'),
                    ('Blood Pressure Diastolic', SensorType.Category.PHYSIOLOGICAL, 'mmHg'),
                    ('Respiratory Rate', SensorType.Category.PHYSIOLOGICAL, 'rpm'),
                    ('Activity Level', SensorType.Category.ACTIVITY, ''),
                    ('Room Temperature', SensorType.Category.ENVIRONMENTAL, '°C'),
                ]

                for name, category, unit in default_sensor_types:
                    sensor_type, _ = SensorType.objects.get_or_create(
                        name=name,
                        defaults={'category': category, 'unit': unit}
                    )

                    device_id = f"SN-{monitored_element.id}-{sensor_type.id}"
                    sensor = Sensor.objects.create(
                        sensor_type=sensor_type,
                        monitored_element=monitored_element,
                        device_identifier=device_id,
                        mode=Sensor.Mode.TIME_BASED,
                        is_active=True
                    )

                    DataSourceConfig.objects.create(
                        sensor=sensor,
                        source=DataSourceConfig.Source.SIMULATED,
                        simulation_profile=DataSourceConfig.SimulationProfile.NORMAL
                    )

            serializer = self.get_serializer(monitored_element)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f'فشل إنشاء العنصر وتأسيس الحساسات: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def readings(self, request, pk=None):
        """🟢 نقطة نهاية موحدة لجلب بيانات المريض وقراءاته معاً لمنع التداخل (Race Conditions)"""
        patient = self.get_object()
        
        readings_qs = SensorReading.objects.filter(
            sensor__monitored_element=patient
        ).select_related('sensor', 'sensor__sensor_type').order_by('-recorded_at')[:50]
        
        patient_serializer = self.get_serializer(patient)
        readings_serializer = SensorReadingSerializer(readings_qs, many=True)
        
        return Response({
            'patient': patient_serializer.data,
            'readings': readings_serializer.data
        })

        
# 🟢 تم التكييف: توجيه مسار المرضى لاستعلام عناصر Patient من جدول MonitoredElement الموحد
class PatientViewSet(viewsets.ModelViewSet):
    queryset = MonitoredElement.objects.filter(element_type=MonitoredElement.ElementType.PATIENT)
    serializer_class = MonitoredElementSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrReadOnly]


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    queryset = MedicalHistory.objects.all()
    serializer_class = MedicalHistorySerializer
    permission_classes = [IsAuthenticated, IsDoctorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['monitored_element']


class SensorTypeViewSet(viewsets.ModelViewSet):
    queryset = SensorType.objects.all()
    serializer_class = SensorTypeSerializer
    permission_classes = [IsAuthenticated]


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all().select_related('sensor_type')
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['monitored_element']


class DataSourceConfigViewSet(viewsets.ModelViewSet):
    queryset = DataSourceConfig.objects.all()
    serializer_class = DataSourceConfigSerializer
    permission_classes = [IsAuthenticated]


class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all().order_by('-recorded_at')
    serializer_class = SensorReadingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = SensorReadingFilter
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = SensorReading.objects.all().select_related('sensor', 'sensor__sensor_type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date and end_date:
            queryset = queryset.filter(recorded_at__range=[start_date, end_date])
        elif start_date:
            queryset = queryset.filter(recorded_at__gte=start_date)
        elif end_date:
            queryset = queryset.filter(recorded_at__lte=end_date)
            
        return queryset.order_by('-recorded_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        limit = request.query_params.get('limit')
        if limit and int(limit) <= 100:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset[:int(limit)], many=True)
            return Response(serializer.data)

        count = queryset.count()
        target_points = 120
        
        if count > target_points:
            step = count // target_points
            readings_list = list(queryset)[::step]
            serializer = self.get_serializer(readings_list, many=True)
            return Response(serializer.data)
            
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# 🟢 تم التكييف: توجيه مسار Context لقراءة سجلات ContextHistory المعتمدة
class ContextViewSet(viewsets.ModelViewSet):
    queryset = ContextHistory.objects.all()
    serializer_class = ContextHistorySerializer
    permission_classes = [IsAuthenticated]


class ContextHistoryViewSet(viewsets.ModelViewSet):
    queryset = ContextHistory.objects.all()
    serializer_class = ContextHistorySerializer
    permission_classes = [IsAuthenticated]


class InsightViewSet(viewsets.ModelViewSet):
    """
    سجل الاستبصارات السريرية الطبية (Medical Insights API):
    - يوثق الحالات الفسيولوجية والتنبؤات الطبية (MIMIC-IV / Rules / Thresholds).
    """
    queryset = Insight.objects.all()
    serializer_class = InsightSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AlertsPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get_queryset(self):
        queryset = Insight.objects.all().select_related('monitored_element', 'context_history')
        patient_id = self.request.query_params.get('monitored_element')
        if patient_id:
            queryset = queryset.filter(monitored_element_id=patient_id)
        return queryset.order_by('-detected_at')



         
class CorrectiveActionViewSet(viewsets.ModelViewSet):
    queryset = CorrectiveAction.objects.all()
    serializer_class = CorrectiveActionSerializer
    permission_classes = [IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    """
    مركز إدارة إشعارات وتنبيهات الطبيب والمرافق (Caregiver Alert Hub API):
    - يعرض فقط الإشعارات المعلقة الخاصة بالمستخدم الحالي.
    - يحتوي على مسار unread-count لحساب العداد الحقيقي للنافبار.
    - دالة الحل توثق التدخل في RuleExecutionLog وتغلق الإشعار.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = AlertsPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get_queryset(self):
        user = self.request.user
        queryset = Notification.objects.filter(recipient=user).select_related(
            'insight', 'insight__monitored_element', 'corrective_action', 'corrective_action__rule'
        )

        # 🟢 افتراضياً: لا نعرض في القائمة إلا الإشعارات المعلقة (غير المقروءة) لتبقى الشاشة نظيفة
        is_read_param = self.request.query_params.get('is_read')
        if is_read_param is not None:
            queryset = queryset.filter(is_read=is_read_param.lower() == 'true')
        else:
            # الافتراضي عند فتح الصفحة: المعلقة فقط!
            queryset = queryset.filter(is_read=False)

        # فلترة المريض
        patient_id = self.request.query_params.get('monitored_element')
        if patient_id:
            queryset = queryset.filter(insight__monitored_element_id=patient_id)

        # فلترة الخطورة
        severity_param = self.request.query_params.get('severity')
        if severity_param:
            severities = [s.strip().upper() for s in severity_param.split(',')]
            if 'HIGH' in severities and 'WARNING' not in severities:
                severities.append('WARNING')
            queryset = queryset.filter(insight__severity__in=severities)

        # فلترة نوع الإنذار
        alert_type = self.request.query_params.get('alert_type')
        if alert_type:
            if alert_type == 'threshold':
                queryset = queryset.filter(insight__source=Insight.Source.THRESHOLD)
            elif alert_type in ['global', 'global_rule']:
                queryset = queryset.filter(
                    Q(insight__source=Insight.Source.GLOBAL_RULE) |
                    Q(corrective_action__rule__monitored_element__isnull=True)
                ).distinct()
            elif alert_type in ['patient_rule', 'patient']:
                queryset = queryset.filter(
                    Q(insight__source=Insight.Source.PATIENT_RULE) |
                    Q(corrective_action__rule__monitored_element__isnull=False)
                ).distinct()

        return queryset.order_by('-sent_at')

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """🟢 عداد الإشعارات المعلقة الحقيقي الخاص بالمستخدم المسجل حالياً"""
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'unread_count': count, 'count': count})

    def destroy(self, request, *args, **kwargs):
        """🟢 دعم نقرة 'تم الحل والمعاينة' عبر DELETE"""
        return self._resolve_notification(request)

    @action(detail=True, methods=['post'], url_path='resolve')
    def resolve(self, request, pk=None):
        """🟢 دعم نقرة 'تم الحل والمعاينة' عبر POST"""
        return self._resolve_notification(request)

    def _resolve_notification(self, request):
        notification = self.get_object()
        doctor_name = request.user.get_full_name() or request.user.username

        # 1. تحويل الإشعار إلى مقروء ومحلول
        notification.is_read = True
        notification.save(update_fields=['is_read'])

        # 2. تحديث الإجراء السريري إلى ACKNOWLEDGED وتوثيقه في RuleExecutionLog
        if notification.corrective_action:
            ca = notification.corrective_action
            ca.status = CorrectiveAction.Status.ACKNOWLEDGED
            ca.save(update_fields=['status'])

            action_desc = ca.description or (ca.rule.action_template if ca.rule else "معاينة واعتماد الإجراء")
            RuleExecutionLog.objects.create(
                rule=ca.rule,
                monitored_element=notification.insight.monitored_element if notification.insight else None,
                context_snapshot=getattr(notification.insight.context_history, 'physiological_data', {}) if (notification.insight and notification.insight.context_history) else {},
                action_executed=f"تم تطبيق الإجراء [{action_desc}] بواسطة الطبيب: {doctor_name}",
                status=RuleExecutionLog.Status.SUCCESS
            )
        elif notification.insight:
            # توثيق حل عتبات شبكة الأمان
            RuleExecutionLog.objects.create(
                rule=None,
                monitored_element=notification.insight.monitored_element,
                context_snapshot=getattr(notification.insight.context_history, 'physiological_data', {}) if notification.insight.context_history else {},
                action_executed=f"تم معاينة وحل إنذار شبكة الأمان السريرية بواسطة الطبيب: {doctor_name}",
                status=RuleExecutionLog.Status.SUCCESS
            )

        return Response({'status': 'resolved', 'message': 'تم حل التنبيه ومعاينته بنجاح'}, status=status.HTTP_200_OK)

class DoctorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrSelf]
    serializer_class = DoctorSerializer

    def get_queryset(self):
        if hasattr(User, 'Role'):
            return User.objects.filter(role__in=[User.Role.DOCTOR, User.Role.ADMIN]) | User.objects.filter(is_superuser=True)
        return User.objects.all()

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        full_name = request.data.get('full_name', '')
        phone_number = request.data.get('phone_number', '')

        if not username or not password:
            return Response({'error': 'اسم المستخدم وكلمة المرور مطلوبان'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'اسم المستخدم موجود مسبقاً'}, status=status.HTTP_400_BAD_REQUEST)

        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        role = getattr(User.Role, 'DOCTOR', 'doctor') if hasattr(User, 'Role') else 'doctor'

        user = User.objects.create_user(
            username=username,
            password=password,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        full_name = request.data.get('full_name')
        if full_name is not None:
            name_parts = full_name.strip().split(' ', 1)
            instance.first_name = name_parts[0] if name_parts else ''
            instance.last_name = name_parts[1] if len(name_parts) > 1 else ''

        password = request.data.get('password')
        if password:
            instance.set_password(password)

        role = request.data.get('role')
        if role:
            instance.role = role

        phone_number = request.data.get('phone_number')
        if phone_number is not None:
            instance.phone_number = phone_number

        instance.save()
        return super().partial_update(request, *args, **kwargs)


class RuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrPatientRulePermission]
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer

    def get_queryset(self):
        queryset = Rule.objects.all()
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy'] or 'pk' in self.kwargs:
            return queryset
            
        patient_id = self.request.query_params.get('monitored_element')
        if patient_id:
            return queryset.filter(monitored_element_id=patient_id)
        else:
            return queryset.filter(monitored_element__isnull=True)


class CaregiverViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsDoctorOrReadOnly]
    serializer_class = DoctorSerializer

    def get_queryset(self):
        queryset = User.objects.filter(role='caregiver')
        patient_id = self.request.query_params.get('monitored_element')
        if patient_id:
            return queryset.filter(cared_patients__id=patient_id).distinct()
        return queryset

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        full_name = request.data.get('full_name', '')
        phone_number = request.data.get('phone_number', '')
        patient_id = request.data.get('monitored_element')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'اسم المستخدم موجود مسبقاً'}, status=status.HTTP_400_BAD_REQUEST)

        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                password=password,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                role='caregiver'
            )

            if patient_id:
                patient = MonitoredElement.objects.filter(id=patient_id).first()
                if patient:
                    patient.caregivers.add(user)
                
                InterestRegistration.objects.get_or_create(
                    monitored_element_id=patient_id,
                    interested_party=user
                )

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# ==============================================================================
# 👤 4. مسارات المصادقة والمستخدم الحالي (Auth Endpoints)
# ==============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    phone_number = request.data.get('phone_number', '')
    role = request.data.get('role', User.Role.CAREGIVER if hasattr(User, 'Role') else 'caregiver')

    if not username or not password:
        return Response({'error': 'اسم المستخدم وكلمة المرور مطلوبان'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'اسم المستخدم موجود مسبقاً'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(
        username=username,
        password=password,
        phone_number=phone_number,
        role=role
    )
    return Response({'message': 'تم إنشاء الحساب بنجاح', 'user_id': user.id}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    # إذا كان المستخدم سوبر أدمن، دوره دائماً admin بدون أي لبس
    if user.is_superuser:
        role = 'admin'
    else:
        role = getattr(user, 'role', 'doctor') or 'doctor'
    
    assigned_patients = []
    registrations = InterestRegistration.objects.filter(
        interested_party=user
    ).select_related('monitored_element')
    
    for reg in registrations:
        elem = reg.monitored_element
        if elem:
            assigned_patients.append({
                'id': elem.id,
                'full_name': elem.full_name,
                'element_type': elem.element_type,
                'age': getattr(elem, 'age', 30)
            })

    return Response({
        'id': user.id,
        'username': user.username,
        'phone_number': getattr(user, 'phone_number', ''),
        'role': role,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_superuser': user.is_superuser,
        'full_name': user.get_full_name() or user.username,
        'assigned_patients': assigned_patients,
        'assigned_patients_count': len(assigned_patients)
    })
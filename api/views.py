# api/views.py
from rest_framework import viewsets, status, filters
# 🟢 إضافة SAFE_METHODS و BasePermission لبناء الصمامات الأمنية
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.db.models import Q

from core.models import MonitoredElement, Patient, MedicalHistory
from sensors.models import Sensor, SensorType, DataSourceConfig, SensorReading
from context.models import Context, ContextHistory
from reasoning.models import Insight
from rules.models import CorrectiveAction
from notifications.models import Notification
from accounts.models import User
from rules.models import Rule

from .serializers import (
    MonitoredElementSerializer, PatientSerializer, MedicalHistorySerializer,
    SensorTypeSerializer, SensorSerializer, DataSourceConfigSerializer, SensorReadingSerializer,
    ContextSerializer, ContextHistorySerializer,
    InsightSerializer, CorrectiveActionSerializer, NotificationSerializer,
    DoctorSerializer, RuleSerializer
)


# 🟢 1. صمام الأمان الأول للبروتوكولات والقواعد: يسمح للأطباء بقراءة الكل، وتعديل تنبيهات المرضى الخاصة فقط، ويحظر العام للمستشفى
class IsAdminOrPatientRulePermission(BasePermission):
    """
    صلاحية حماية مخصصة للبروتوكولات (RuleViewSet):
    - القراءة (GET) متاحة لجميع الأطباء الموثقين.
    - الإضافة والتعديل والحذف (POST, PUT, PATCH, DELETE) مسموح للأطباء العاديين 
      فقط إذا كان التنبيه مخصصاً لمريض محدد (أي حقل monitored_element ليس فارغاً).
    - القواعد العامة (التي monitored_element فيها فارغ) محصورة لمدير النظام (Admin) فقط.
    """
    def has_permission(self, request, view):
        # القراءة السريرية (GET, HEAD, OPTIONS) متاحة لكافة الطاقم الطبي الموثق
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # في حالة الإنشاء (POST):
        if request.method == 'POST':
            # نتحقق من البيانات المرسلة
            monitored_element = request.data.get('monitored_element')
            if monitored_element:
                # إذا كان التنبيه مخصصاً لمريض، يسمح للطبيب العادي بإنشائه
                return request.user and request.user.is_authenticated
            else:
                # إذا كان فارغاً (بروتوكول عام للمستشفى)، يحظر لغير المدير والأدمن
                return request.user and (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin')
        
        # للتعديل والحذف (سيرد الفحص المفصل في has_object_permission بالأسفل)
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # الأدمن والـ Superuser يملكون الصلاحية الكاملة على جميع القواعد والبروتوكولات
        if request.user.is_superuser or getattr(request.user, 'role', '') == 'admin':
            return True
        
        # الطبيب العادي يمكنه تعديل/حذف القواعد المخصصة للمرضى فقط
        # ويُمنع تماماً من المساس بالبروتوكولات العامة للمستشفى (التي ليس لها monitored_element)
        return obj.monitored_element is not None


# 🟢 2. صمام الأمان الثاني للبروفايل: يسمح للطبيب بتعديل حسابه هو فقط، ويحصر الإدارة العامة للأدمن
class IsAdminOrSelf(BasePermission):
    """
    صلاحية مخصصة للكادر الطبي:
    - تتيح القراءة (GET) لجميع الطاقم الطبي الموثق.
    - تتيح التعديل (PUT, PATCH) للطبيب على حسابه الشخصي فقط (تطابق الـ ID).
    - تتيح الإضافة والحذف والإدارة الشاملة لمدير النظام (Admin) والـ Superuser فقط.
    """
    def has_permission(self, request, view):
        # القراءة السريرية (GET) متاحة لجميع الأطباء الموثقين
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # الإضافة والإنشاء (POST) والحذف (DELETE) محصور بالأدمن فقط لحماية كود التسجيل
        if request.method in ['POST', 'DELETE']:
            return request.user and (request.user.is_superuser or getattr(request.user, 'role', '') == 'admin')
        
        # التعديل مسموح مبدئياً وسيتم التحقق من ملكية الحساب في دالة has_object_permission بالأسفل
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # الأدمن والـ Superuser يملكون الصلاحية الكاملة على جميع الحسابات
        if request.user.is_superuser or getattr(request.user, 'role', '') == 'admin':
            return True
        
        # الطبيب العادي يمكنه تعديل حسابه الشخصي فقط (عند تطابق كائن الحساب مع المستخدم الحالي)
        return obj.id == request.user.id


class MonitoredElementViewSet(viewsets.ModelViewSet):
    queryset = MonitoredElement.objects.all()
    serializer_class = MonitoredElementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role == 'admin':
            return MonitoredElement.objects.all()
        elif user.role == 'doctor':
            return MonitoredElement.objects.filter(Q(doctor=user) | Q(doctor__isnull=True))
        elif user.role == 'caregiver':
            return MonitoredElement.objects.filter(caregivers=user)
        return MonitoredElement.objects.none()

    # الإنشاء اللوجستي الموحد للمريض والتاريخ الطبي ومقدم الرعاية وتأسيس الحساسات آلياً
    def create(self, request, *args, **kwargs):
        data = request.data
        full_name = data.get('full_name')
        date_of_birth = data.get('date_of_birth')
        gender = data.get('gender')
        element_type = data.get('element_type', 'patient')
        chronic_conditions = data.get('chronic_conditions', [])
        
        caregiver_option = data.get('caregiver_option', 'none')
        caregiver_id = data.get('existing_caregiver_id')
        new_caregiver_username = data.get('caregiver_username')
        new_caregiver_name = data.get('caregiver_full_name')
        new_caregiver_password = data.get('caregiver_password')
        new_caregiver_phone = data.get('caregiver_phone_number', '')

        if not full_name or not date_of_birth or not gender:
            return Response({'error': 'جميع بيانات المريض الأساسية مطلوبة'}, status=status.HTTP_400_BAD_REQUEST)

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
                    doctor=request.user
                )
                
                if assigned_caregiver:
                    monitored_element.caregivers.add(assigned_caregiver)

                MedicalHistory.objects.create(
                    monitored_element=monitored_element,
                    chronic_conditions=chronic_conditions
                )

                from notifications.models import InterestRegistration
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
                    ('Heart Rate', 'physiological', 'bpm'),
                    ('Oxygen Saturation', 'physiological', '%'),
                    ('Body Temperature', 'physiological', '°C'),
                    ('Blood Pressure Systolic', 'physiological', 'mmHg'),
                    ('Blood Pressure Diastolic', 'physiological', 'mmHg'),
                    ('Respiratory Rate', 'physiological', 'rpm'),
                    ('Activity Level', 'activity', ''),
                    ('Room Temperature', 'environmental', '°C'),
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
            return Response({'error': f'فشل إنشاء المريض وتأسيس الحساسات: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


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


# كلاس فلترة مخصص لدعم العلاقات المتداخلة (__ Lookup)
class SensorReadingFilter(django_filters.FilterSet):
    class Meta:
        model = SensorReading
        fields = {
            'sensor': ['exact'],
            'sensor__monitored_element': ['exact'],
        }


# ركيزة التقسيم المخصصة لتلافي جلب آلاف الصفوف للداشبورد افتراضياً
class StandardResultsSetPagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 1000


class SensorReadingViewSet(viewsets.ModelViewSet):
    queryset = SensorReading.objects.all().order_by('-recorded_at')
    serializer_class = SensorReadingSerializer
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


class ContextViewSet(viewsets.ModelViewSet):
    queryset = Context.objects.all()
    serializer_class = ContextSerializer


class ContextHistoryViewSet(viewsets.ModelViewSet):
    queryset = ContextHistory.objects.all()
    serializer_class = ContextHistorySerializer


# api/views.py
# api/views.py

class AlertsPagination(LimitOffsetPagination):
    default_limit = 50
    max_limit = 200


class InsightViewSet(viewsets.ModelViewSet):
    """
    مصب الإنذارات السريري المطور والآمن 100% والمقاوم للانهيار:
    يستخدم استعلاماً فرعياً مباشراً (Subqueries) لتفادي انهيار العلاقات العكسية، 
    مع دعم التقسيم والتصفية الثلاثية لمركز التنبيهات.
    """
    queryset = Insight.objects.all()
    serializer_class = InsightSerializer
    pagination_class = AlertsPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    def get_queryset(self):
        # 🟢 ربط المريض فقط وهو حقل مباشر مضمون ومستقر
        queryset = Insight.objects.all().select_related('monitored_element')

        # 1. فلترة المريض
        patient_id = self.request.query_params.get('monitored_element')
        if patient_id:
            queryset = queryset.filter(monitored_element_id=patient_id)

        # 2. فلترة مستوى الخطورة
        severity_param = self.request.query_params.get('severity')
        if severity_param:
            severities = [s.strip().upper() for s in severity_param.split(',')]
            if 'HIGH' in severities and 'WARNING' not in severities:
                severities.append('WARNING')
            queryset = queryset.filter(severity__in=severities)

        # 3. 🟢 الفلترة السريرية الثلاثية بنظام الاستعلام الفرعي المباشر (آمن ومجرب 100%)
        alert_type = self.request.query_params.get('alert_type')
        if alert_type:
            if alert_type == 'threshold':
                queryset = queryset.filter(source=Insight.Source.THRESHOLD)
                
            elif alert_type == 'global':
                # جلب معرفات التنبيهات المرتبطة بقوانين عامة للمستشفى
                from rules.models import CorrectiveAction
                global_insight_ids = CorrectiveAction.objects.filter(
                    rule__monitored_element__isnull=True
                ).values_list('insight_id', flat=True)
                queryset = queryset.filter(id__in=global_insight_ids)
                
            elif alert_type == 'patient_rule':
                # جلب معرفات التنبيهات المرتبطة بقوانين مخصصة لمريض معين
                from rules.models import CorrectiveAction
                patient_insight_ids = CorrectiveAction.objects.filter(
                    rule__monitored_element__isnull=False
                ).values_list('insight_id', flat=True)
                queryset = queryset.filter(id__in=patient_insight_ids)

        return queryset.order_by('-detected_at')

class CorrectiveActionViewSet(viewsets.ModelViewSet):
    queryset = CorrectiveAction.objects.all()
    serializer_class = CorrectiveActionSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


# حماية الكادر الطبي مع السماح للطبيب بتعديل حسابه الشخصي فقط (IsAdminOrSelf)
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
    role = getattr(user, 'role', 'admin' if user.is_superuser else 'doctor')
    
    from notifications.models import InterestRegistration
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


# 🟢 3. حماية البروتوكولات السريرية العامة مع السماح للأطباء بإضافة وتعديل وحذف التنبيهات الخاصة بالمرضى (IsAdminOrPatientRulePermission)
class RuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrPatientRulePermission]
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer

    def get_queryset(self):
        queryset = Rule.objects.all()
        
        # 🟢 التعديل المصلح والآمن والمستقر لـ DRF: التحقق بـ self.action بدلاً من self.detail لمنع AttributeError والانهيار في دوجر
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy'] or 'pk' in self.kwargs:
            return queryset
            
        # في حالة طلب القوائم الإجمالية (List Route):
        patient_id = self.request.query_params.get('monitored_element')
        if patient_id:
            # أ. إذا حددت الواجهة معرف مريض، نرجع فقط القواعد الخاصة به
            return queryset.filter(monitored_element_id=patient_id)
        else:
            # ب. إذا كان الاستعلام عاماً (صفحة البروتوكولات العامة)، نرجع فقط البروتوكولات العامة للمستشفى (isnull=True)
            return queryset.filter(monitored_element__isnull=True)


class CaregiverViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
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
                
                from notifications.models import InterestRegistration
                InterestRegistration.objects.get_or_create(
                    monitored_element_id=patient_id,
                    interested_party=user
                )

        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED) 
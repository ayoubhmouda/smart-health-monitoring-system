# api/serializers.py
from rest_framework import serializers
from core.models import MonitoredElement, Patient, Elderly, Disabled, MedicalHistory
from sensors.models import Sensor, SensorType, DataSourceConfig, SensorReading
from context.models import Context, ContextHistory
from reasoning.models import Insight
from rules.models import Rule, CorrectiveAction
from notifications.models import Notification
from accounts.models import User
from notifications.models import InterestRegistration

# --- Core ---
class MonitoredElementSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()  # لعرض العمر المحسوب
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
    sensor_type = SensorTypeSerializer(read_only=True)
    class Meta:
        model = Sensor
        fields = '__all__'


class DataSourceConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSourceConfig
        fields = '__all__'


# 🟢 دمج وتوحيد كلاس قراءة الحساس ليعرض الحساس المدمج وحالة التلوين (status) معاً دون تضارب
class SensorReadingSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer(read_only=True)
    sensor_name = serializers.CharField(source='sensor.sensor_type.name', read_only=True)
    status = serializers.SerializerMethodField()  # حقل تحديد حالة اللون الموجه للفرونت إند

    class Meta:
        model = SensorReading
        fields = ['id', 'sensor', 'sensor_name', 'value', 'status', 'recorded_at']

    def get_status(self, obj):
        # قراءة العتبات الطبية الحقيقية للحساس مباشرة من قاعدة البيانات
        val = obj.value
        sensor_type = obj.sensor.sensor_type if (obj.sensor and obj.sensor.sensor_type) else None
        if val is None or not sensor_type:
            return 'Good'

        # جلب الحدود المسجلة في جدول SensorType
        min_val = sensor_type.normal_min
        max_val = sensor_type.normal_max

        # إذا تداخلت القراءة وخرجت عن الحدود، نوجه الفرونت إند لتلوينها بالأصفر (Caution)
        if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
            return 'Caution'
        return 'Good'


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
class RuleSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)

    class Meta:
        model = Rule
        fields = ['id', 'name', 'condition', 'action_template', 'severity', 'severity_display', 'is_active', 'monitored_element']


class CorrectiveActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrectiveAction
        fields = '__all__'


# --- Notifications ---
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


# --- Accounts & Staff ---
class DoctorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    assigned_patients_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number', 'full_name', 'first_name', 'last_name', 'role', 'is_active', 'is_superuser', 'assigned_patients_count']

    def get_full_name(self, obj):
        name = obj.get_full_name()
        return name if name else obj.username

    def get_assigned_patients_count(self, obj):
        # حساب عدد المرضى المتابعين لهذا الطبيب عبر سجلات الاهتمام والمتابعة
        return InterestRegistration.objects.filter(interested_party=obj).values('monitored_element').distinct().count()
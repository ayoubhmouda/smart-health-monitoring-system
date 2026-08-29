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
    age = serializers.ReadOnlyField()  
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


class SensorReadingSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer(read_only=True)
    sensor_name = serializers.CharField(source='sensor.sensor_type.name', read_only=True)
    status = serializers.SerializerMethodField()  
    min_val = serializers.FloatField(source='sensor.sensor_type.normal_min', read_only=True)
    max_val = serializers.FloatField(source='sensor.sensor_type.normal_max', read_only=True)

    class Meta:
        model = SensorReading
        fields = ['id', 'sensor', 'sensor_name', 'value', 'status', 'recorded_at', 'min_val','max_val']

    def get_status(self, obj):
        val = obj.value
        sensor_type = obj.sensor.sensor_type if (obj.sensor and obj.sensor.sensor_type) else None
        if val is None or not sensor_type:
            return 'Good'

        min_val = sensor_type.normal_min
        max_val = sensor_type.normal_max

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
    # 🟢 حقن البيانات الفوقية للقاعدة المرتبطة بالتنبؤ تلقائياً في السيرفر لضمان دقة الهوية بالفرونت إند
    is_global_rule = serializers.SerializerMethodField()
    rule_name = serializers.SerializerMethodField()
    action_template = serializers.SerializerMethodField()

    class Meta:
        model = Insight
        fields = '__all__'

    def get_is_global_rule(self, obj):
        # التحقق من ارتباط الاستبصار بإجراء تصحيحي نشط لقانون عام للمستشفى (monitored_element is null)
        action = obj.corrective_actions.filter(rule__is_active=True).order_by('-id').first()
        if action and action.rule:
            return action.rule.monitored_element is None
        return False

    def get_rule_name(self, obj):
        action = obj.corrective_actions.filter(rule__is_active=True).order_by('-id').first()
        if action and action.rule:
            return action.rule.name
        return None

    def get_action_template(self, obj):
        action = obj.corrective_actions.filter(rule__is_active=True).order_by('-id').first()
        if action and action.rule:
            return action.rule.action_template
        return None


# --- Rules ---
class RuleSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)

    class Meta:
        model = Rule
        # 🟢 إضافة حقل overridden_rules لتمكين الواجهة من قراءة وحفظ التجاوز الصريح
        fields = [
            'id', 'name', 'condition', 'action_template', 'severity', 
            'severity_display', 'is_active', 'monitored_element', 'overridden_rules'
        ]


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
        return InterestRegistration.objects.filter(interested_party=obj).values('monitored_element').distinct().count()
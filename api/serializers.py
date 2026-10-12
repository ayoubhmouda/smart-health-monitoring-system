# api/serializers.py
from rest_framework import serializers
from core.models import MonitoredElement, MedicalHistory
from sensors.models import Sensor, SensorType, DataSourceConfig, SensorReading
from context.models import ContextHistory  # تم التكييف: إزالة Context الملغى
from reasoning.models import Insight
from rules.models import Rule, CorrectiveAction
from notifications.models import Notification, InterestRegistration
from accounts.models import User

# --- Core ---
class MonitoredElementSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    doctor_name = serializers.SerializerMethodField()
    doctor_phone = serializers.SerializerMethodField()

    class Meta:
        model = MonitoredElement
        fields = '__all__'

    def get_doctor_name(self, obj):
        if obj.doctor:
            return obj.doctor.get_full_name() or obj.doctor.username
        return None

    def get_doctor_phone(self, obj):
        if obj.doctor:
            return getattr(obj.doctor, 'phone_number', '') or None
        return None


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
        fields = ['id', 'sensor', 'sensor_name', 'value', 'status', 'recorded_at', 'min_val', 'max_val']

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
class ContextHistorySerializer(serializers.ModelSerializer):
    """
    سيريالايزر السجل السياقي الموحد:
    يدعم الحقول المباشرة للنموذج الجديد، مع توفير حقل context ديناميكي
    لحماية توافق شاشات الفرونت إند القديمة من أي كسر.
    """
    context = serializers.SerializerMethodField()

    class Meta:
        model = ContextHistory
        fields = [
            'id', 
            'monitored_element', 
            'physiological_data', 
            'activity_data', 
            'environmental_data', 
            'recorded_at', 
            'context'
        ]

    def get_context(self, obj):
        # توافق خلفي كامل مع أي شاشة فرونت تقرأ من كائن context الداخلي
        return {
            'physiological_data': obj.physiological_data,
            'activity_data': obj.activity_data,
            'environmental_data': obj.environmental_data,
            'timestamp': obj.recorded_at.isoformat() if obj.recorded_at else None
        }


# سيريالايزر وهمي خفيف إذا كان مستدعياً في أي ملف خارجي لمنع أخطاء الـ Import
class ContextSerializer(ContextHistorySerializer):
    pass


# --- Reasoning ---
# في api/serializers.py
class InsightSerializer(serializers.ModelSerializer):
    # 🟢 حقن بيانات المريض مباشرة من الداتابيز لمنع ظهور "غير معروف"
    patient_name = serializers.CharField(source='monitored_element.full_name', read_only=True)
    patient_age = serializers.ReadOnlyField(source='monitored_element.age')
    patient_gender = serializers.CharField(source='monitored_element.get_gender_display', read_only=True)
    monitored_element_id = serializers.IntegerField(source='monitored_element.id', read_only=True)

    is_global_rule = serializers.SerializerMethodField()
    rule_name = serializers.SerializerMethodField()
    action_template = serializers.SerializerMethodField()

    class Meta:
        model = Insight
        fields = '__all__'

    def get_is_global_rule(self, obj):
        if obj.source == Insight.Source.GLOBAL_RULE:
            return True
        if obj.source == Insight.Source.PATIENT_RULE:
            return False
        action = obj.corrective_actions.filter(rule__is_active=True).order_by('-id').first()
        if action and action.rule:
            return action.rule.monitored_element is None
        return False

    def get_rule_name(self, obj):
        action = obj.corrective_actions.filter(rule__is_active=True).order_by('-id').first()
        if action and action.rule:
            return action.rule.name
        if obj.source == Insight.Source.THRESHOLD:
            return "شبكة الأمان السريرية (Threshold)"
        return None

    def get_action_template(self, obj):
        action = obj.corrective_actions.filter(rule__is_active=True).order_by('-id').first()
        if action and action.rule:
            return action.rule.action_template or ""
        if action:
            return action.description or ""
        return ""

# --- Rules ---
class RuleSerializer(serializers.ModelSerializer):
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)

    class Meta:
        model = Rule
        fields = [
            'id', 'name', 'condition', 'action_template', 'severity', 
            'severity_display', 'is_active', 'monitored_element', 'overridden_rules'
        ]


class CorrectiveActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrectiveAction
        fields = '__all__'


# --- Notifications ---
# في api/serializers.py

class NotificationSerializer(serializers.ModelSerializer):
    """
    سيريالايزر مخصص لإشعارات الطبيب:
    يجلب البيانات السريرية المرتبطة بالاستبصار والإجراء لتغذية بطاقة التنبيه بالواجهة مباشرة.
    """
    patient_name = serializers.CharField(source='insight.monitored_element.full_name', default='مريض غير معروف', read_only=True)
    patient_id = serializers.IntegerField(source='insight.monitored_element.id', default=None, read_only=True)
    patient_age = serializers.ReadOnlyField(source='insight.monitored_element.age')
    patient_gender = serializers.CharField(source='insight.monitored_element.get_gender_display', default='غير محدد', read_only=True)
    monitored_element_id = serializers.IntegerField(source='insight.monitored_element.id', default=None, read_only=True)

    severity = serializers.CharField(source='insight.severity', default='HIGH', read_only=True)
    source = serializers.CharField(source='insight.source', default='rules', read_only=True)
    detected_at = serializers.DateTimeField(source='sent_at', read_only=True)

    rule_name = serializers.SerializerMethodField()
    action_template = serializers.SerializerMethodField()
    is_global_rule = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'message', 'is_read', 'sent_at', 'detected_at',
            'patient_name', 'patient_id', 'patient_age', 'patient_gender', 'monitored_element_id',
            'severity', 'source', 'rule_name', 'action_template', 'is_global_rule'
        ]

    def get_rule_name(self, obj):
        if obj.corrective_action and obj.corrective_action.rule:
            return obj.corrective_action.rule.name
        if obj.insight and obj.insight.source == Insight.Source.THRESHOLD:
            return "شبكة الأمان السريرية (Threshold)"
        return "تنبيه سريري"

    def get_action_template(self, obj):
        # إرجاع محتوى action_template الفعلي للقاعدة فقط، دون أي جمل جاهزة
        if obj.corrective_action and obj.corrective_action.rule:
            return obj.corrective_action.rule.action_template or ""
        if obj.corrective_action:
            return obj.corrective_action.description or ""
        return ""

    def get_is_global_rule(self, obj):
        if obj.corrective_action and obj.corrective_action.rule:
            return obj.corrective_action.rule.monitored_element is None
        if obj.insight:
            return obj.insight.source == Insight.Source.GLOBAL_RULE
        return False


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
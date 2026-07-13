from sensors.models import DataSourceConfig
from sensors.services.simulator import HealthSimulator

class SourceRouter:
    """يقرر مصدر البيانات لكل حساس بناءً على DataSourceConfig مع ضمان العزل الكامل بين المرضى."""

    def __init__(self):
        # لم نعد ننشئ كائناً ثابتاً هنا منعاً لتداخل البيانات بين المرضى
        pass

    def get_reading(self, sensor, profile_override=None):
        """يُرجع قيمة قراءة لحساس معين مع عزل تام لكل مريض وسيناريوهاته."""
        
        # استخراج معرف المريض (Monitored Element ID) لضمان الفصل
        patient_id = sensor.monitored_element_id

        try:
            config = sensor.data_source_config
        except DataSourceConfig.DoesNotExist:
            # إذا لم يوجد إعداد، ننشئ له محاكي افتراضي معزول بهوية هذا المريض
            simulator = HealthSimulator(patient_id=patient_id)
            return simulator.generate_reading(sensor.sensor_type.name.lower())

        if config.source == DataSourceConfig.Source.SIMULATED:
            profile = profile_override or config.simulation_profile
            
            # 🧠 إنشاء نسخة محاكي مخصصة ومستمرة في الكاش لهذا المريض تحديداً بناءً على معرفه
            simulator = HealthSimulator(profile=profile, patient_id=patient_id)
            simulator.set_profile(profile)
            
            # تحويل اسم الحساس لمفتاح متوافق (مثل heart_rate)
            sensor_key = sensor.sensor_type.name.lower().replace(' ', '_')
            return simulator.generate_reading(sensor_key)
        else:
            # المصدر الحقيقي (Physical Sensor) - سيتم تنفيذه لاحقاً
            return None
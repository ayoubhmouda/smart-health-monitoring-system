# sensors/services/source_router.py
from typing import Optional
from sensors.models import DataSourceConfig
from sensors.services.simulator import HealthSimulator


class SourceRouter:
    """يقرر مصدر البيانات لكل حساس بناءً على DataSourceConfig مع ضمان العزل الكامل بين المرضى."""

    def __init__(self):
        pass

    def get_reading(self, sensor, profile_override: Optional[str] = None, start_time: Optional[float] = None) -> Optional[float]:
        """يُرجع قيمة قراءة لحساس معين مع عزل تام لكل مريض وسيناريوهاته."""
        
        # استخراج معرف المريض (Monitored Element ID) لضمان الفصل
        patient_id = sensor.monitored_element_id

        # تحويل اسم نوع الحساس دائماً إلى المفتاح القياسي (مثل heart_rate)
        sensor_key = sensor.sensor_type.name.lower().replace(' ', '_')

        try:
            config = sensor.data_source_config
        except (DataSourceConfig.DoesNotExist, AttributeError):
            # إذا لم يوجد إعداد، ننشئ له محاكياً افتراضياً معزولاً بهوية المريض
            simulator = HealthSimulator(patient_id=patient_id, start_time=start_time)
            return simulator.generate_reading(sensor_key)

        # التأكد من أن الـ config ليس None
        if not config:
            simulator = HealthSimulator(patient_id=patient_id, start_time=start_time)
            return simulator.generate_reading(sensor_key)

        if config.source == DataSourceConfig.Source.SIMULATED:
            profile = profile_override or config.simulation_profile
            
            # إنشاء نسخة محاكي مخصصة ومستمرة مع الحفاظ على وقت البداية
            simulator = HealthSimulator(profile=profile, patient_id=patient_id, start_time=start_time)
            
            if simulator.profile != profile:
                simulator.set_profile(profile, start_time=start_time)
            
            return simulator.generate_reading(sensor_key)
        else:
            # المصدر الحقيقي (Physical Sensor) - للتعامل مع الحساسات الفيزيائية
            return None
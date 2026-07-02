from sensors.models import DataSourceConfig
from sensors.services.simulator import HealthSimulator

class SourceRouter:
    """يقرر مصدر البيانات لكل حساس بناءً على DataSourceConfig."""

    def __init__(self):
        self.simulator = HealthSimulator()

    def get_reading(self, sensor, profile_override=None):
        """
        يُرجع قيمة قراءة لحساس معين.
        profile_override: يمكن تجاوز الملف الشخصي للمحاكي (لأغراض الاختبار).
        """
        try:
            config = sensor.data_source_config
        except DataSourceConfig.DoesNotExist:
            # إذا لم يوجد إعداد، نعتبره محاكي افتراضي
            return self.simulator.generate_reading(sensor.sensor_type.name.lower())

        if config.source == DataSourceConfig.Source.SIMULATED:
            # استخدم الملف الشخصي المحدد
            profile = profile_override or config.simulation_profile
            self.simulator.set_profile(profile)
            # مفتاح الحساس (مثلاً heart_rate) يجب أن يطابق أسماء المفاتيح في المحاكي
            sensor_key = sensor.sensor_type.name.lower().replace(' ', '_')
            return self.simulator.generate_reading(sensor_key)
        else:
            # Physical: سننفذه لاحقاً في physical_reader.py
            # حالياً نرجع None
            return None
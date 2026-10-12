# context/services.py
from django.utils import timezone
from sensors.models import SensorReading, SensorType, Sensor
from .models import ContextHistory


class ContextAggregator:
    """
    يجمع أحدث قراءات الحساسات للمريض ويبني سجلاً سياقياً واحداً
    مباشرة في ContextHistory دون الحاجة لجدول وسيط.
    """

    def aggregate_for(self, monitored_element):
        # لا تبني سياقاً لمريض ليس لديه حساسات نشطة
        if not Sensor.objects.filter(monitored_element=monitored_element, is_active=True).exists():
            return None

        all_types = SensorType.objects.all()
        phys_data = {}
        act_data = {}
        env_data = {}

        for stype in all_types:
            latest = SensorReading.objects.filter(
                sensor__sensor_type=stype,
                sensor__monitored_element=monitored_element
            ).order_by('-recorded_at').first()

            if latest:
                key = stype.name.lower().replace(' ', '_')
                if stype.category == SensorType.Category.PHYSIOLOGICAL:
                    phys_data[key] = latest.value
                elif stype.category == SensorType.Category.ACTIVITY:
                    act_data[key] = latest.value
                elif stype.category == SensorType.Category.ENVIRONMENTAL:
                    env_data[key] = latest.value

        # إذا لم يتم العثور على أي قراءات على الإطلاق، نتجنب حفظ سجل فارغ
        if not (phys_data or act_data or env_data):
            return None

        # الحفظ المباشر في السجل الزمني التراكمي الموحد (ContextHistory)
        history = ContextHistory.objects.create(
            monitored_element=monitored_element,
            physiological_data=phys_data,
            activity_data=act_data,
            environmental_data=env_data
        )
        return history
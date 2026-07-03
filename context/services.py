from datetime import datetime
from sensors.models import SensorReading, SensorType
from .models import Context, ContextHistory

class ContextAggregator:
    """يجمع أحدث قراءات الحساسات لكل أنواع القياس ويبني سياقًا واحدًا."""

    def aggregate_for(self, monitored_element):
        all_types = SensorType.objects.all()
        phys_data = {}
        act_data = {}
        env_data = {}

        for stype in all_types:
            latest = SensorReading.objects.filter(
                sensor__sensor_type=stype
            ).order_by('-recorded_at').first()

            if latest:
                key = stype.name.lower().replace(' ', '_')
                if stype.category == SensorType.Category.PHYSIOLOGICAL:
                    phys_data[key] = latest.value
                elif stype.category == SensorType.Category.ACTIVITY:
                    act_data[key] = latest.value
                elif stype.category == SensorType.Category.ENVIRONMENTAL:
                    env_data[key] = latest.value

        ctx = Context.objects.create(
            monitored_element=monitored_element,
            physiological_data=phys_data,
            activity_data=act_data,
            environmental_data=env_data,
            timestamp=datetime.utcnow()
        )

        ContextHistory.objects.create(
            monitored_element=monitored_element,
            context=ctx,
            recorded_at=datetime.utcnow()
        )
        return ctx
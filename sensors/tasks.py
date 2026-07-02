# sensors/tasks.py
from celery import shared_task
from sensors.models import Sensor, SensorReading
from sensors.services.source_router import SourceRouter
from datetime import datetime

router = SourceRouter()

@shared_task
def read_all_active_sensors():
    """مهمة دورية: تجلب قراءة من كل حساس نشط وتحفظها."""
    sensors = Sensor.objects.filter(is_active=True).select_related('sensor_type')
    count = 0
    for sensor in sensors:
        reading_value = router.get_reading(sensor)
        if reading_value is not None:
            SensorReading.objects.create(
                sensor=sensor,
                value=reading_value,
                source='SIMULATED',
                recorded_at=datetime.utcnow()
            )
            count += 1
    return f"Readings created for {count} sensors"
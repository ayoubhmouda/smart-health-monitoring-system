from celery import shared_task
from django.db import transaction
from sensors.models import Sensor, SensorReading
from sensors.services.source_router import SourceRouter
from django.utils import timezone # أفضل من datetime.utcnow لدعم التوقيت المحلي والإعدادات

@shared_task
def read_all_active_sensors():
    """مهمة دورية: تجلب القراءات مجمعة ومفرزة حسب المريض لضمان التناسق الطبي ومنع التداخل."""
    
    # تحسين الاستعلام باستخدام select_related لتجنب مشكلة الـ N+1 في قاعدة البيانات
    # وفرز الحساسات حسب المريض لضمان معالجة متتالية وناجحة للـ Batch الفسيولوجي
    sensors = Sensor.objects.filter(is_active=True).select_related(
        'sensor_type', 
        'monitored_element', 
        'data_source_config'
    ).order_by('monitored_element_id')
    
    router = SourceRouter()
    count = 0
    
    # توحيد الطابع الزمني الحالي للدورة بالكامل
    current_time = timezone.now()
    
    # استخدام transaction.atomic لضمان سرعة وموثوقية الحفظ في قاعدة البيانات ككتلة واحدة
    with transaction.atomic():
        for sensor in sensors:
            reading_value = router.get_reading(sensor)
            
            if reading_value is not None:
                SensorReading.objects.create(
                    sensor=sensor,
                    value=reading_value,
                    source='SIMULATED',
                    recorded_at=current_time # جميع قراءات نفس الدورة تأخذ نفس اللحظة الزمنية تماماً
                )
                count += 1
                
    return f"Readings created for {count} sensors safely and coherently."
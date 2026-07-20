# sensors/tasks.py
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from collections import defaultdict
from sensors.models import Sensor, SensorReading
from sensors.services.source_router import SourceRouter

@shared_task
def read_all_active_sensors():
    """
    مهمة دورية: تجلب القراءات مجمعة ومفرزة حسب المريض لضمان التناسق الطبي والأداء العالي.
    """
    
    # 1. جلب الحساسات النشطة دفعة واحدة مع تحسين الاستعلام (Eager Loading)
    sensors = Sensor.objects.filter(is_active=True).select_related(
        'monitored_element', 
        'sensor_type', 
        'data_source_config'
    )
    
    # 2. تجميع الحساسات حسب المريض (أو None للحساسات العامة)
    patient_sensors = defaultdict(list)
    for sensor in sensors:
        patient_id = sensor.monitored_element_id if sensor.monitored_element else None
        patient_sensors[patient_id].append(sensor)
    
    router = SourceRouter()
    readings_to_create = []
    
    # توحيد الطابع الزمني لجميع مستشعرات هذه الدورة بدقة ثانية واحدة
    current_time = timezone.now() 
    
    # 3. توليد القيم في الذاكرة (خارج الترانزاكشن لتقليل وقت قفل الجداول في قاعدة البيانات)
    for patient_id, sensor_list in patient_sensors.items():
        # بما أن المستشعرات مجمعة ومترابطة للمريض الواحد، 
        # فإن استدعاء الـ router لها بالتوالي السريع على نفس الـ Worker 
        # سيضمن استخدام كاش Redis المشترك بكفاءة 100% دون تداخل من مرضى آخرين.
        for sensor in sensor_list:
            
            # 🟢 التعديل الجديد: استخراج وقت تحديث الإعدادات كطابع زمني (Timestamp) 
            # لحل مشكلة تجمد قراءات التدهور التدريجي وتمريره للموجه (Router)
            config_start_time = None
            if sensor.data_source_config and hasattr(sensor.data_source_config, 'updated_at'):
                config_start_time = sensor.data_source_config.updated_at.timestamp()
            
            # تمرير الـ config_start_time إلى الـ router ليقوم بدوره بتمريره للمحاكي
            reading_value = router.get_reading(sensor, start_time=config_start_time)
            
            if reading_value is not None:
                # نجهز كائنات القراءة في الذاكرة أولاً ولا نحفظها فوراً
                readings_to_create.append(
                    SensorReading(
                        sensor=sensor,
                        value=reading_value,
                        source='SIMULATED',
                        recorded_at=current_time
                    )
                )
                
    # 4. الحفظ الجماعي الصاروخي في قاعدة البيانات (Bulk Insert)
    if readings_to_create:
        with transaction.atomic():
            # نقوم بحفظ مئات القراءات في استعلام SQL واحد فقط!
            SensorReading.objects.bulk_create(readings_to_create)
            
    return f"Readings created for {len(readings_to_create)} sensors safely and coherently."
# sensors/tasks.py
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from collections import defaultdict
from sensors.models import Sensor, SensorReading
from sensors.services.source_router import SourceRouter

# استيراد مكتبات قنوات دجانغو للبث الفوري وإشارات دجانغو
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# 🟢 دالة مساعدة سريعة لتقييم حالة الحساس حركياً من عتبات الداتابيز لتغذية السوكيت الحي
def get_reading_status(reading):
    val = reading.value
    sensor_type = reading.sensor.sensor_type if (reading.sensor and reading.sensor.sensor_type) else None
    if val is None or not sensor_type:
        return 'Good'

    min_val = sensor_type.normal_min
    max_val = sensor_type.normal_max

    if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
        return 'Caution'
    return 'Good'


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
    
    # 3. توليد القيم في الذاكرة
    for patient_id, sensor_list in patient_sensors.items():
        for sensor in sensor_list:
            
            config_start_time = None
            if sensor.data_source_config and hasattr(sensor.data_source_config, 'updated_at'):
                config_start_time = sensor.data_source_config.updated_at.timestamp()
            
            reading_value = router.get_reading(sensor, start_time=config_start_time)
            
            if reading_value is not None:
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
            SensorReading.objects.bulk_create(readings_to_create)
            
        # 5. إطلاق إشارة الـ post_save يدوياً لكل قراءة تم حفظها بالـ bulk_create لتفعيل محرك القواعد
        try:
            for reading in readings_to_create:
                post_save.send(
                    sender=SensorReading,
                    instance=reading,
                    created=True
                )
        except Exception as e:
            pass
            
        # 6. بث تحديث فوري عبر الـ WebSocket لكافة المرضى مع تمرير حقل الحالة (status) السريري
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                updated_patient_ids = {
                    r.sensor.monitored_element_id 
                    for r in readings_to_create 
                    if r.sensor and r.sensor.monitored_element_id
                }
                
                for p_id in updated_patient_ids:
                    patient_readings = [
                        {
                            "sensor_id": r.sensor_id,
                            "sensor_name": r.sensor.sensor_type.name if r.sensor and r.sensor.sensor_type else "Unknown",
                            "value": r.value,
                            "min_val": r.sensor.sensor_type.normal_min if r.sensor and r.sensor.sensor_type else None,
                            "max_val": r.sensor.sensor_type.normal_max if r.sensor and r.sensor.sensor_type else None,
                            # 🟢 تمرير حالة الحساس الحقيقية من قاعدة البيانات بالملي ثانية لمزامنة التلوين وتطهير شارة الانتباه فوراً
                            "status": get_reading_status(r),
                            "recorded_at": r.recorded_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                        }
                        for r in readings_to_create 
                        if r.sensor and r.sensor.monitored_element_id == p_id
                    ]

                    async_to_sync(channel_layer.group_send)(
                        f"patient_alerts_group_{p_id}",
                        {
                            "type": "send_sensor_update",
                            "readings": patient_readings,
                            "message": "New sensor readings recorded",
                            "timestamp": current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                        }
                    )
        except Exception as e:
            pass
            
    return f"Readings created for {len(readings_to_create)} sensors safely, coherently, and evaluated against clinical rules."
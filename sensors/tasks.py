# sensors/tasks.py
from collections import defaultdict
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from sensors.models import Sensor, SensorReading
from sensors.services.source_router import SourceRouter

# استيراد مكتبات قنوات دجانغو للبث الفوري وإشارات دجانغو
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def get_reading_status(reading):
    """دالة مساعدة سريعة لتقييم حالة الحساس حركياً من عتبات الداتابيز لتغذية السوكيت الحي"""
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
    مهمة دورية مركزية:
    1. تجلب القراءات مجمعة ومفرزة حسب المريض لضمان التناسق الطبي.
    2. تحفظ القراءات وتبثها عبر الـ WebSocket للرسم البياني فوراً.
    3. تستدعي فوراً وبشكل متزامن مهمة تجميع السياق وتقييم القواعد لتوحيد الدورة الزمنية.
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
        # معالجة حساس النشاط الحركي أولاً لبناء الحزمة المتناسقة قبل باقي الحساسات
        sorted_sensors = sorted(
            sensor_list,
            key=lambda s: 0 if (s.sensor_type and s.sensor_type.name == 'Activity Level') else 1
        )

        for sensor in sorted_sensors:
            
            config_start_time = None
            if hasattr(sensor, 'data_source_config') and sensor.data_source_config and hasattr(sensor.data_source_config, 'updated_at'):
                config_start_time = sensor.data_source_config.updated_at.timestamp()
            
            reading_value = router.get_reading(sensor, start_time=config_start_time)
            
            if reading_value is not None:
                source_type = (
                    sensor.data_source_config.source 
                    if hasattr(sensor, 'data_source_config') and sensor.data_source_config 
                    else SensorReading.Source.SIMULATED
                )
                
                readings_to_create.append(
                    SensorReading(
                        sensor=sensor,
                        value=reading_value,
                        source=source_type,
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
            print(f"⚠️ [خطأ في إشارة post_save للقراءات]: {str(e)}")
            
        # 6. بث تحديث فوري عبر الـ WebSocket لكافة المرضى
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
                            "sensor_name": str(r.sensor.sensor_type.name) if (r.sensor and r.sensor.sensor_type) else "Unknown",
                            "value": float(r.value),
                            "min_val": float(r.sensor.sensor_type.normal_min) if (r.sensor and r.sensor.sensor_type and r.sensor.sensor_type.normal_min is not None) else None,
                            "max_val": float(r.sensor.sensor_type.normal_max) if (r.sensor and r.sensor.sensor_type and r.sensor.sensor_type.normal_max is not None) else None,
                            "status": get_reading_status(r),
                            "recorded_at": r.recorded_at.isoformat()
                        }
                        for r in readings_to_create 
                        if r.sensor and r.sensor.monitored_element_id == p_id
                    ]

                    # إرسال الحزمة للمجموعة المعزولة الخاصة بالمريض
                    async_to_sync(channel_layer.group_send)(
                        f"patient_alerts_group_{p_id}",
                        {
                            "type": "send_sensor_update",
                            "readings": patient_readings,
                            "message": "New sensor readings recorded",
                            "timestamp": current_time.isoformat()
                        }
                    )
                    print(f"📡 [WebSocket Broadcast]: تم بث {len(patient_readings)} قراءة للمريض رقم #{p_id}")
        except Exception as e:
            print(f"🚨 [خطأ خطير في بث السوكيت الحساسات]: {str(e)}")

        # 🟢 7. الخطوة الجوهرية لتوحيد خط الإنتاج (Atomic Pipeline):
        # استدعاء تجميع السياق وحساب القواعد فوراً في نفس اللحظة لمنع أي تباعد زمني
        try:
            from context.tasks import aggregate_all_contexts
            aggregate_all_contexts()
        except Exception as e:
            print(f"⚠️ [خطأ في تجميع السياق aggregate_all_contexts]: {str(e)}")
            
    return f"Readings created for {len(readings_to_create)} sensors safely, coherently, and evaluated against clinical rules."
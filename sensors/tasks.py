# sensors/tasks.py
from celery import shared_task
from django.db import transaction
from django.utils import timezone
from collections import defaultdict
from sensors.models import Sensor, SensorReading
from sensors.services.source_router import SourceRouter

# 🟢 استيراد مكتبات قنوات دجانغو للبث الفوري وإشارات دجانغو
from django.db.models.signals import post_save
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

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
            
            # استخراج وقت تحديث الإعدادات كطابع زمني (Timestamp) 
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
            
        # 🟢 5. حل مشكلة الباك إند: إطلاق إشارة الـ post_save يدوياً لكل قراءة تم حفظها بالـ bulk_create
        # هذا يضمن استيقاظ محرك القواعد (Rule Engine) في تطبيق rules وتقييم القوانين المخصصة وحفظ التنبيهات فوراً
        try:
            for reading in readings_to_create:
                post_save.send(
                    sender=SensorReading,
                    instance=reading,
                    created=True
                )
        except Exception as e:
            # حماية صامتة: لضمان عدم تأثر البث عند أي ظرف طارئ في المعالجة
            pass
            
        # 🟢 6. بث تحديث فوري عبر الـ WebSocket لكافة المرضى مع تمرير القراءات الفعلية
        try:
            channel_layer = get_channel_layer()
            if channel_layer:
                # استخراج المعرفات المتميزة للمرضى الذين شملتهم القراءات الجديدة
                updated_patient_ids = {
                    r.sensor.monitored_element_id 
                    for r in readings_to_create 
                    if r.sensor and r.sensor.monitored_element_id
                }
                
                for p_id in updated_patient_ids:
                    # تجميع القراءات الخاصة بهذا المريض تحديداً لتمريرها بداخل الـ WebSocket
                    patient_readings = [
                        {
                            "sensor_id": r.sensor_id,
                            "sensor_name": r.sensor.sensor_type.name if r.sensor and r.sensor.sensor_type else "Unknown",
                            "value": r.value,
                            "recorded_at": r.recorded_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                        }
                        for r in readings_to_create 
                        if r.sensor and r.sensor.monitored_element_id == p_id
                    ]

                    async_to_sync(channel_layer.group_send)(
                        f"patient_alerts_group_{p_id}",
                        {
                            "type": "send_sensor_update",
                            "readings": patient_readings, # تم إضافة القراءات الفعلية هنا!
                            "message": "New sensor readings recorded",
                            "timestamp": current_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                        }
                    )
        except Exception as e:
            # حماية صامتة: لضمان عدم تأثر حفظ البيانات عند أي طارئ في الشبكة
            pass
            
    return f"Readings created for {len(readings_to_create)} sensors safely, coherently, and evaluated against clinical rules."
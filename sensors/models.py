# sensors/models.py
from django.db import models
from django.utils import timezone


class SensorType(models.Model):
    class Category(models.TextChoices):
        PHYSIOLOGICAL = 'physiological', 'Physiological'
        ACTIVITY = 'activity', 'Activity'
        ENVIRONMENTAL = 'environmental', 'Environmental'

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=Category.choices)
    unit = models.CharField(max_length=50, blank=True)
    normal_min = models.FloatField(null=True, blank=True)
    normal_max = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Sensor Type"
        verbose_name_plural = "Sensor Types"

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Sensor(models.Model):
    class Mode(models.TextChoices):
        TIME_BASED = 'time_based', 'Time-Based'
        EVENT_BASED = 'event_based', 'Event-Based'

    sensor_type = models.ForeignKey(SensorType, on_delete=models.CASCADE)
    device_identifier = models.CharField(max_length=100, unique=True)
    mode = models.CharField(max_length=20, choices=Mode.choices, default=Mode.TIME_BASED)
    is_active = models.BooleanField(default=True)

    monitored_element = models.ForeignKey(
        'core.MonitoredElement',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='sensors'
    )

    class Meta:
        verbose_name = "Sensor"
        verbose_name_plural = "Sensors"

    def __str__(self):
        return f"{self.sensor_type.name} ({self.device_identifier})"


class DataSourceConfig(models.Model):
    class Source(models.TextChoices):
        SIMULATED = 'SIMULATED', 'Simulated'
        PHYSICAL = 'PHYSICAL', 'Physical'

    class SimulationProfile(models.TextChoices):
        NORMAL = 'normal', 'Normal'
        GRADUAL_DETERIORATION = 'gradual_deterioration', 'Gradual Deterioration'
        GRADUAL_RECOVERY = 'gradual_recovery', 'Gradual Recovery'
        SUDDEN_HIGH = 'sudden_high', 'Sudden High'
        SUDDEN_LOW = 'sudden_low', 'Sudden Low'

        ACTIVITY_RESTING = 'activity_resting', 'Activity Resting'
        ACTIVITY_SITTING = 'activity_sitting', 'Activity Sitting'
        ACTIVITY_WALKING = 'activity_walking', 'Activity Walking'
        ACTIVITY_RUNNING = 'activity_running', 'Activity Running'

        RANDOM = 'random', 'Random'
        CUSTOM = 'custom', 'Custom'
        EMERGENCY_SPIKE = 'emergency_spike', 'Emergency Spike'
        ABNORMAL = 'abnormal', 'Abnormal'

    sensor = models.OneToOneField(Sensor, on_delete=models.CASCADE, related_name='data_source_config')
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.SIMULATED)
    simulation_profile = models.CharField(max_length=35, choices=SimulationProfile.choices, default=SimulationProfile.NORMAL)
    physical_connection_info = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Data Source Config"
        verbose_name_plural = "Data Source Configs"

    def __str__(self):
        return f"{self.sensor} – {self.source}"


class SensorReading(models.Model):
    class Source(models.TextChoices):
        SIMULATED = 'SIMULATED', 'Simulated'
        PHYSICAL = 'PHYSICAL', 'Physical'

    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='readings')
    value = models.FloatField()
    source = models.CharField(max_length=10, choices=Source.choices)
    recorded_at = models.DateTimeField(default=timezone.now, db_index=True)
    raw_payload = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        verbose_name = "Sensor Reading"
        verbose_name_plural = "Sensor Readings"
        ordering = ['-recorded_at']
        indexes = [
            # 🟢 فهرس مركّب لسحب القراءات الأخيرة لكل حساس في السلسلة الزمنية بسرعة
            models.Index(fields=['sensor', '-recorded_at']),
        ]

    def __str__(self):
        return f"{self.sensor} → {self.value} at {self.recorded_at}"


class DeviceHeartbeat(models.Model):
    class Status(models.TextChoices):
        ONLINE = 'online', 'متصل'
        OFFLINE = 'offline', 'منقطع'
        UNSTABLE = 'unstable', 'غير مستقر'

    sensor = models.ForeignKey(
        Sensor, 
        on_delete=models.CASCADE, 
        related_name='heartbeats', 
        null=True, 
        blank=True,
        help_text="المستشعر المرتبط بالنبضة (إن وجد)"
    )
    device_identifier = models.CharField(
        max_length=100, 
        help_text="المعرّف الفيزيائي لجهاز البث أو الجوال الناقل للإشارة"
    )
    last_seen = models.DateTimeField(default=timezone.now, help_text="توقيت آخر إشارة تم رصدها")
    status = models.CharField(
        max_length=15, 
        choices=Status.choices, 
        default=Status.ONLINE, 
        help_text="حالة اتصال الجهاز اللحظية"
    )
    battery_level = models.IntegerField(
        null=True, 
        blank=True, 
        help_text="مستوى بطارية الجهاز المئوي لمنع الإيقاف المفاجئ"
    )
    network_latency_ms = models.IntegerField(
        null=True, 
        blank=True, 
        help_text="زمن استجابة اتصال الشبكة بالملي ثانية (QoS)"
    )

    class Meta:
        verbose_name = "Device Heartbeat"
        verbose_name_plural = "Device Heartbeats"
        ordering = ['-last_seen']
        indexes = [
            # 🟢 فهرس مركّب للتحقق المباشر والسريع من آخر نبضة لكل جهاز
            models.Index(fields=['device_identifier', '-last_seen']),
        ]

    def __str__(self):
        return f"Heartbeat for {self.device_identifier} ({self.get_status_display()}) at {self.last_seen}"
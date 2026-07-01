from django.db import models
from core.models import Patient, Elderly, Disabled

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

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Sensor(models.Model):
    class Mode(models.TextChoices):
        TIME_BASED = 'time_based', 'Time-Based'
        EVENT_BASED = 'event_based', 'Event-Based'

    sensor_type = models.ForeignKey(SensorType, on_delete=models.CASCADE)
    #monitored_element = models.ForeignKey(
    #    'core.MonitoredElement',
    #    on_delete=models.CASCADE,
    #    null=True, blank=True  # سنستخدم نموذج وسيط لاحقًا
    #)
    device_identifier = models.CharField(max_length=100, unique=True)
    mode = models.CharField(max_length=20, choices=Mode.choices, default=Mode.TIME_BASED)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.sensor_type.name} ({self.device_identifier})"


class DataSourceConfig(models.Model):
    class Source(models.TextChoices):
        SIMULATED = 'SIMULATED', 'Simulated'
        PHYSICAL = 'PHYSICAL', 'Physical'

    class SimulationProfile(models.TextChoices):
        NORMAL = 'normal', 'Normal'
        ABNORMAL = 'abnormal', 'Abnormal'
        RANDOM = 'random', 'Random'
        CUSTOM = 'custom', 'Custom'

    sensor = models.OneToOneField(Sensor, on_delete=models.CASCADE, related_name='data_source_config')
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.SIMULATED)
    simulation_profile = models.CharField(max_length=20, choices=SimulationProfile.choices, default=SimulationProfile.NORMAL)
    physical_connection_info = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sensor} – {self.source}"


class SensorReading(models.Model):
    class Source(models.TextChoices):
        SIMULATED = 'SIMULATED', 'Simulated'
        PHYSICAL = 'PHYSICAL', 'Physical'

    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='readings')
    value = models.FloatField()
    source = models.CharField(max_length=10, choices=Source.choices)
    recorded_at = models.DateTimeField(auto_now_add=True)
    raw_payload = models.JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"{self.sensor} → {self.value} at {self.recorded_at}"
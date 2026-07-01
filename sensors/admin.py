from django.contrib import admin
from .models import SensorType, Sensor, DataSourceConfig, SensorReading

@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit', 'normal_min', 'normal_max')

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('sensor_type', 'device_identifier', 'mode', 'is_active')

@admin.register(DataSourceConfig)
class DataSourceConfigAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'source', 'simulation_profile', 'updated_at')

@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'value', 'source', 'recorded_at')
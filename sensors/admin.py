# sensors/admin.py
from django.contrib import admin
from .models import SensorType, Sensor, DataSourceConfig, SensorReading, DeviceHeartbeat


@admin.register(SensorType)
class SensorTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'unit', 'normal_min', 'normal_max')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('sensor_type', 'device_identifier', 'mode', 'monitored_element', 'is_active')
    list_filter = ('mode', 'is_active', 'sensor_type__category')
    search_fields = ('device_identifier', 'monitored_element__full_name')


@admin.register(DataSourceConfig)
class DataSourceConfigAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'source', 'simulation_profile', 'updated_at')
    list_filter = ('source', 'simulation_profile')


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('sensor', 'value', 'source', 'recorded_at')
    list_filter = ('source',)
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sensor__sensor_type')


@admin.register(DeviceHeartbeat)
class DeviceHeartbeatAdmin(admin.ModelAdmin):
    list_display = ('device_identifier', 'sensor', 'status', 'battery_level', 'network_latency_ms', 'last_seen')
    list_filter = ('status',)
    search_fields = ('device_identifier',)
    list_per_page = 25
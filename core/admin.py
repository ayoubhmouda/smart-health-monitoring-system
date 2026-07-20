from django.contrib import admin
from .models import MonitoredElement, Patient, Elderly, Disabled, MedicalHistory

@admin.register(MonitoredElement)
class MonitoredElementAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'date_of_birth', 'age', 'gender', 'element_type', 'created_at')
    search_fields = ('full_name',)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('element', 'diagnosis', 'admission_date')
    search_fields = ('element__full_name',)

@admin.register(Elderly)
class ElderlyAdmin(admin.ModelAdmin):
    list_display = ('element', 'mobility_level')
    search_fields = ('element__full_name',)

@admin.register(Disabled)
class DisabledAdmin(admin.ModelAdmin):
    list_display = ('element', 'disability_type')
    search_fields = ('element__full_name',)

@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('monitored_element', 'updated_at')
    fields = ('monitored_element', 'chronic_conditions', 'lifestyle')
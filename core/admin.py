from django.contrib import admin
from .models import Patient, Elderly, Disabled, MedicalHistory

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'date_of_birth', 'gender', 'admission_date')
    search_fields = ('full_name',)

@admin.register(Elderly)
class ElderlyAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'date_of_birth', 'mobility_level')

@admin.register(Disabled)
class DisabledAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'date_of_birth', 'disability_type')

@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('monitored_element', 'updated_at')
# core/admin.py
from django.contrib import admin
from .models import MonitoredElement, MedicalHistory


@admin.register(MonitoredElement)
class MonitoredElementAdmin(admin.ModelAdmin):
    # عرض الحقول السريرية الجديدة مباشرة في واجهة المشرف
    list_display = (
        'full_name', 'date_of_birth', 'age', 'gender', 'element_type', 
        'diagnosis', 'mobility_level', 'created_at'
    )
    search_fields = ('full_name', 'diagnosis')
    list_filter = ('element_type', 'gender')
    
    # تنظيم الحقول المتاحة للتحرير والإضافة بشكل منسق في لوحة التحكم
    fields = (
        'full_name', 'date_of_birth', 'gender', 'element_type', 
        'doctor', 'caregivers', 'diagnosis', 'admission_date', 
        'mobility_level', 'disability_type'
    )


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ('monitored_element', 'updated_at')
    fields = ('monitored_element', 'chronic_conditions')
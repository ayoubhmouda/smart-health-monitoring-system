# context/admin.py
from django.contrib import admin
from .models import ContextHistory


@admin.register(ContextHistory)
class ContextHistoryAdmin(admin.ModelAdmin):
    list_display = ('monitored_element', 'recorded_at')
    search_fields = ('monitored_element__full_name',)
    list_filter = ('recorded_at',)
    
    # تمكين المشرف من معاينة البيانات الفسيولوجية والبيئية والحركية في صفحة التفاصيل
    fields = ('monitored_element', 'physiological_data', 'activity_data', 'environmental_data')
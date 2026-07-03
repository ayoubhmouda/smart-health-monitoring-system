from django.contrib import admin
from .models import Context, ContextHistory

@admin.register(Context)
class ContextAdmin(admin.ModelAdmin):
    list_display = ('monitored_element', 'timestamp')

@admin.register(ContextHistory)
class ContextHistoryAdmin(admin.ModelAdmin):
    list_display = ('monitored_element', 'recorded_at')
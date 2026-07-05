from django.contrib import admin
from .models import Rule, CorrectiveAction

@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'action_template', 'is_active')

@admin.register(CorrectiveAction)
class CorrectiveActionAdmin(admin.ModelAdmin):
    list_display = ('insight', 'rule', 'status', 'created_at')
# rules/admin.py
from django.contrib import admin
from .models import Rule, CorrectiveAction, RuleExecutionLog


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'severity', 'action_template', 'monitored_element', 'is_active')
    list_filter = ('severity', 'is_active')
    search_fields = ('name', 'action_template')


@admin.register(CorrectiveAction)
class CorrectiveActionAdmin(admin.ModelAdmin):
    list_display = ('rule','get_clean_action','insight', 'status', 'created_at')
    list_filter = ('status',)
    def get_clean_action(self, obj):
        # 🟢 عرض النص الطبي الصافي من القاعدة مباشرة
        if obj.rule and obj.rule.action_template:
            return obj.rule.action_template
        return obj.description  # fallback في حال عدم وجود قاعدة
        
    get_clean_action.short_description = "الإجراء المقترح"

@admin.register(RuleExecutionLog)
class RuleExecutionLogAdmin(admin.ModelAdmin):
    list_display = ('rule', 'monitored_element', 'action_executed', 'status', 'triggered_at')
    list_filter = ('status', 'triggered_at')
    search_fields = ('rule__name', 'monitored_element__full_name', 'action_executed')
    list_per_page = 25
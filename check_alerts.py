# check_alerts.py
import os
import django

# 🟢 تهيئة وإعداد بيئة عمل دنجو تلقائياً لقراءة الداتابيز بداخل الحاوية
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reasoning.models import Insight
from rules.models import CorrectiveAction

print('\n=== 🩺 1. استبصارات القواعد السريرية بجدول الـ Insights ===')
insights = Insight.objects.filter(source__iexact='rules')
print(f'الإجمالي: {insights.count()} سجل في الداتابيز')
for i in insights:
    detected_time = i.detected_at.strftime('%Y-%m-%d %H:%M:%S') if i.detected_at else 'غير محدد'
    print(f'- [{detected_time}] مريض ID #{i.monitored_element_id}: خطورة ({i.severity})')

print('\n=== 🚨 2. الإجراءات التصحيحية والإنذارات المفعّلة (Corrective Actions) ===')
actions = CorrectiveAction.objects.select_related('rule', 'insight', 'insight__monitored_element').all()
print(f'الإجمالي: {actions.count()} إجراء نشط حالياً')
for a in actions:
    print(f'- [القاعدة: {a.rule.name}] للمريض: [{a.insight.monitored_element.full_name}] ⬅️ التوصية السريرية: ({a.rule.action_template})')
print()
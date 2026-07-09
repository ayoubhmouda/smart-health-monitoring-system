import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from context.tasks import aggregate_all_contexts
from reasoning.models import Insight
from core.models import MonitoredElement

# شغّل دورة تجميع وتحليل يدوية
result = aggregate_all_contexts()
print(result)

# تحقق من أحدث Insight لأحمد
ahmed = MonitoredElement.objects.get(full_name='احمد محمد')
latest = Insight.objects.filter(monitored_element=ahmed).order_by('-detected_at').first()
if latest:
    print(f"أحدث Insight: {latest.insight_type}, severity={latest.severity}, confidence={latest.confidence:.2f}, detected_at={latest.detected_at}")
else:
    print("لا توجد Insights لأحمد")
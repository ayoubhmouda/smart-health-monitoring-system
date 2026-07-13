docker-compose exec web python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from context.tasks import aggregate_all_contexts
from reasoning.models import Insight
from core.models import MonitoredElement

print(aggregate_all_contexts())

for elem in MonitoredElement.objects.all():
    latest = Insight.objects.filter(monitored_element=elem).order_by('-detected_at').first()
    if latest:
        print(f'{elem.full_name}: {latest.insight_type}, {latest.severity}, {latest.confidence:.2f}, {latest.detected_at}')
    else:
        print(f'{elem.full_name}: لا توجد Insights')
"
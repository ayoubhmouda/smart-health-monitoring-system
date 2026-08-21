# notifications/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # 🟢 رابط اتصال فوري معزول بالـ ID الخاص بكل مريض
    re_path(r'ws/notifications/(?P<patient_id>\d+)/$', consumers.NotificationConsumer.as_asgi()),
]
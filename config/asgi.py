"""
ASGI config for config project.

Exposes the ASGI callable as a module-level variable named ``application``.
Supports both HTTP requests and WebSocket connections via Django Channels.
"""

import os
import django

# 1. ضبط متغير البيئة لإعدادات دجانجو
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 2. تهيئة تطبيق ASGI الأساسي لطلب التطبيقات المسبقة
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

# 3. استيراد مكونات Channels بعد تهيئة Django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import notifications.routing

# 4. توجيه البروتوكولات (HTTP و WebSocket)
application = ProtocolTypeRouter({
    # طلبات الـ HTTP التقليدية (REST API / Admin)
    "http": django_asgi_app,
    
    # اتصالات الـ WebSocket التفاعلية في الوقت الفعلي
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notifications.routing.websocket_urlpatterns
        )
    ),
})
# notifications/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 🟢 استخراج معرف المريض النشط من رابط اتصال الـ WebSocket بالفرونت إند
        self.patient_id = self.scope['url_route']['kwargs']['patient_id']
        # تصميم قناة بث مستقلة ومعزولة للمريض لمنع تداخل التنبيهات بين المرضى الآخرين
        self.group_name = f"patient_alerts_group_{self.patient_id}"

        # الانضمام لقناة البث المشتركة لـ الـ WebSockets
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # مغادرة القناة بأمان عند إغلاق الصفحة أو تبديل المريض
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # 🟢 هذه الدالة تستقبل التنبيه المرسل من السينيال (Signals) وتقوم ببثه فوراً لمتصفح الطبيب (Vue 3)
    async def send_alert(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'severity': event['severity'],
            'action_template': event['action_template'],
            'detected_at': event['detected_at']
        }))
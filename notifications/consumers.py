import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 🟢 استخراج معرف المريض من الرابط
        self.patient_id = self.scope['url_route']['kwargs']['patient_id']
        # تصميم قناة بث معزولة وخاصة بالمريض
        self.group_name = f"patient_alerts_group_{self.patient_id}"

        # الانضمام للقناة
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # مغادرة القناة عند إغلاق الاتصال
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # 1️⃣ معالجة إرسال التنبيهات والإجراءات التصحيحية الحرجة
    async def send_alert(self, event):
        await self.send(text_data=json.dumps({
            'type': 'alert',  # 👈 لتمييز نوع الرسالة في Vue 3
            'message': event.get('message'),
            'severity': event.get('severity'),
            'action_template': event.get('action_template'),
            'detected_at': event.get('detected_at')
        }))

    # 2️⃣ معالجة إرسال قراءات الحساسات المباشرة (Live Sensors Stream)
    async def send_sensor_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'sensor_update',
            'readings': event.get('readings', {}),
            'timestamp': event.get('timestamp')
        }))

    # 3️⃣ معالجة إرسال التنبؤات واستبصارات الذكاء الاصطناعي (ML & Threshold Insights)
    async def send_insight_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'insight_update',
            'insight': event.get('insight', {}),
            'timestamp': event.get('timestamp')
        }))
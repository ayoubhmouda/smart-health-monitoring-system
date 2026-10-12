import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.patient_id = self.scope['url_route']['kwargs']['patient_id']
        self.group_name = f"patient_alerts_group_{self.patient_id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        # 🟢 رسالة اختبار فورية للتأكد من وصول البث للموبايل فور الاتصال
        await self.send(text_data=json.dumps({
            'type': 'test_connection',
            'message': '✅ اتصال الـ WebSocket مع الهاتف ناجح 100%!'
        }))

    async def disconnect(self, close_code):
        # مغادرة القناة عند إغلاق الاتصال
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # 1️⃣ معالجة إرسال التنبيهات والإجراءات التصحيحية الحرجة
    async def send_alert(self, event):
        await self.send(text_data=json.dumps({
            'type': 'alert',
            'message': event.get('message'),
            'severity': event.get('severity'),
            'source': event.get('source'),                  # 🟢 تمرير المصدر الحقيقي
            'is_global_rule': event.get('is_global_rule'),  # 🟢 تمرير هوية البروتوكول العام
            'rule_name': event.get('rule_name'),            # 🟢 تمرير اسم القاعدة
            'action_template': event.get('action_template'),
            'recipient': event.get('recipient'),
            'monitored_element': event.get('monitored_element'),
            'detected_at': event.get('detected_at')
        }))

    # 2️⃣ معالجة إرسال قراءات الحساسات المباشرة (Live Sensors Stream)
    async def send_sensor_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'sensor_update',
            'readings': event.get('readings', {}),
            'timestamp': event.get('timestamp')
        }))

    # 4️⃣ معالجة إرسال مؤشرات التقدم الاستباقية للقواعد (Proactive Rule Progression)
    async def send_rule_progression(self, event):
        await self.send(text_data=json.dumps({
            'type': 'rule_progression_update',
            'progressions': event.get('progressions', []),
            'timestamp': event.get('timestamp')
        }))

    # 3️⃣ معالجة إرسال التنبؤات واستبصارات الذكاء الاصطناعي (ML & Threshold Insights)
    async def send_insight_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'insight_update',
            'insight': event.get('insight', {}),
            'timestamp': event.get('timestamp')
        }))
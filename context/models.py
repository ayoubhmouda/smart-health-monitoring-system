# context/models.py
from django.db import models


class ContextHistory(models.Model):
    """
    الجدول الزمني التراكمي الموحد (Unified Time-Series Context Ledger):
    يخزن كافة قراءات العلامات الفسيولوجية، البيئية، والنشاط الحركي للمريض معاً
    لكل لحظة زمنية، مما يمنع الازدواجية ويلغي تماماً عبء عمليات الكتابة المزدوجة.
    """
    monitored_element = models.ForeignKey(
        'core.MonitoredElement',
        on_delete=models.CASCADE,
        related_name='context_histories'
    )
    
    # حقول المجالات الثلاثة وفقاً للورقة الأكاديمية
    physiological_data = models.JSONField(default=dict, blank=True)
    activity_data = models.JSONField(default=dict, blank=True)
    environmental_data = models.JSONField(default=dict, blank=True)
    
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Context History"
        verbose_name_plural = "Context Histories"
        ordering = ['-recorded_at']  # جلب القراءات الأحدث تلقائياً في كافة الاستعلامات
        indexes = [
            # 🟢 فهرس مركّب مرتب تنازلياً لجلب النافذة الزمنية الأحدث في 1 ملي ثانية
            models.Index(fields=['monitored_element', '-recorded_at']),
        ]

    def __str__(self):
        return f"Context for {self.monitored_element} at {self.recorded_at}"
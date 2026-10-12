# context/tasks.py
from django.utils import timezone
from celery import shared_task
from core.models import MonitoredElement
from .models import ContextHistory
from .services import ContextAggregator
from reasoning.engine import ReasoningEngine
from reasoning.predictors.ml_predictor import MLPredictor
from rules.engine import RuleEngine, evaluate_direct_rules


@shared_task
def aggregate_all_contexts():
    """
    مهمة دورية مركزية:
    1. تجمع قراءات المريض الفورية وتحفظها كـ ContextHistory.
    2. تقيم القواعد السريرية المباشرة (Direct Clinical Rules) وتطلق الإنذارات فوراً.
    3. تمرر السياق لنموذج الذكاء الاصطناعي لإنتاج استبصارات الـ ML.
    4. تحسب وتبث مؤشرات التقدم الاستباقي عبر قنوات الـ WebSocket الحية.
    """
    elements = MonitoredElement.objects.all()
    aggregator = ContextAggregator()
    reasoning_engine = ReasoningEngine(MLPredictor())  
    rule_engine = RuleEngine()                         
    count = 0
    
    for elem in elements:
        # 1. تجميع القراءات الفورية والحصول مباشرة على كائن ContextHistory الجديد
        latest_history = aggregator.aggregate_for(elem)
        
        # إذا لم ينتج سياق جديد في هذه الدورة، نأخذ آخر سياق مسجل في النظام للمريض
        if not latest_history:
            latest_history = ContextHistory.objects.filter(monitored_element=elem).first()
        
        if latest_history:
            # 2. تقييم القواعد السريرية المباشرة وحفظ التنبيهات فوراً عند اكتمال مهلتها
            direct_insights = evaluate_direct_rules(elem, latest_history)
            for ins in direct_insights:
                # التأكد من ربط الـ Insight بالسجل السياقي قبل الحفظ إذا لم يكن مربوطاً
                if not getattr(ins, 'context_history_id', None):
                    ins.context_history = latest_history
                ins.save()

            # 3. تشغيل الذكاء الاصطناعي لتنبؤات الـ ML
            try:
                insights = reasoning_engine.reason(elem)       
                for insight in insights:
                    rule_engine.process(insight)
            except Exception:
                pass

            # 4. حساب وبث مؤشرات التقدم الاستباقية للقواعد عبر الـ WebSocket
            try:
                progressions = rule_engine.calculate_rules_progression(elem, latest_history)
                if progressions:
                    from asgiref.sync import async_to_sync
                    from channels.layers import get_channel_layer
                    channel_layer = get_channel_layer()
                    
                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            f"patient_alerts_group_{elem.id}",
                            {
                                "type": "send_rule_progression",
                                "progressions": progressions,
                                "timestamp": timezone.now().isoformat()
                            }
                        )
            except Exception:
                pass

        count += 1
        
    return f"Aggregated, direct rules evaluated, and progressions broadcasted for {count} elements."
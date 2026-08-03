# context/tasks.py
from celery import shared_task
from core.models import MonitoredElement
from .services import ContextAggregator
from reasoning.engine import ReasoningEngine
from reasoning.predictors.ml_predictor import MLPredictor
from rules.engine import RuleEngine

@shared_task
def aggregate_all_contexts():
    """
    مهمة دورية مركزية:
    1. تجمع قراءات المريض الفورية وتحفظها كـ ContextHistory.
    2. تمرر السياق لمحرك الاستدلال (الذي يستخدم نموذج الذكاء الاصطناعي حالياً).
    3. تمرر النتائج (Insights) لمحرك القواعد لإنشاء الإجراءات التصحيحية اللحظية.
    """
    elements = MonitoredElement.objects.all()
    aggregator = ContextAggregator()
    
    # 🟢 تنظيف وتفعيل نمط الاستراتيجية (Strategy Pattern)
    # نقوم بحقن Predictor محدد (هنا MLPredictor كخيار رئيسي، ويمكن استبداله بـ ThresholdPredictor بكل سهولة)
    reasoning_engine = ReasoningEngine(MLPredictor())  
    rule_engine = RuleEngine()                         
    count = 0
    
    for elem in elements:
        # 1. تجميع القراءات الفورية وتحديث السياق وتخزينه
        aggregator.aggregate_for(elem)
        
        # 2. تشغيل محرك الاستدلال لإنتاج الـ Insights
        insights = reasoning_engine.reason(elem)       
        
        # 3. تمرير الـ Insights الناتجة إلى محرك القواعد لاتخاذ القرارات
        for insight in insights:
            rule_engine.process(insight)               
        count += 1
        
    return f"Aggregated, reasoned and processed rules for {count} elements safely."
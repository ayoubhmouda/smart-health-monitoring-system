from celery import shared_task
from core.models import MonitoredElement
from .services import ContextAggregator
from reasoning.engine import ReasoningEngine
from reasoning.predictors.ml_predictor import MLPredictor
from rules.engine import RuleEngine

@shared_task
def aggregate_all_contexts():
    elements = MonitoredElement.objects.all()
    aggregator = ContextAggregator()
    reasoning_engine = ReasoningEngine(MLPredictor())  # يحتوي على المُعزِّز الشخصي
    rule_engine = RuleEngine()                         # دوره فقط إنشاء الإجراءات
    count = 0
    for elem in elements:
        aggregator.aggregate_for(elem)
        insights = reasoning_engine.reason(elem)       # 1. ينتج Insight مع ثقة مُعزَّزة
        for insight in insights:
            rule_engine.process(insight)               # 2. يحول Insight إلى CorrectiveAction
        count += 1
    return f"Aggregated, reasoned and processed rules for {count} elements"
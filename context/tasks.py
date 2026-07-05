from celery import shared_task
from core.models import MonitoredElement
from .services import ContextAggregator
from reasoning.engine import ReasoningEngine
from reasoning.predictors.ml_predictor import MLPredictor
from rules.engine import RuleEngine  # جديد

@shared_task
def aggregate_all_contexts():
    elements = MonitoredElement.objects.all()
    aggregator = ContextAggregator()
    reasoning_engine = ReasoningEngine(MLPredictor())
    rule_engine = RuleEngine()  # جديد
    count = 0
    for elem in elements:
        aggregator.aggregate_for(elem)
        insights = reasoning_engine.reason(elem)
        for insight in insights:
            rule_engine.process(insight)  # جديد
        count += 1
    return f"Aggregated, reasoned and processed rules for {count} elements"
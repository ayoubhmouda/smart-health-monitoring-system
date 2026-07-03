from celery import shared_task
from core.models import MonitoredElement
from .services import ContextAggregator
from reasoning.engine import ReasoningEngine
from reasoning.predictors.threshold_predictor import ThresholdPredictor

@shared_task
def aggregate_all_contexts():
    elements = MonitoredElement.objects.all()
    aggregator = ContextAggregator()
    engine = ReasoningEngine(ThresholdPredictor())  # تجهيز المحرك
    count = 0
    for elem in elements:
        aggregator.aggregate_for(elem)
        engine.reason(elem)  # تحليل السياق فوراً بعد تجميعه
        count += 1
    return f"Aggregated context and reasoned for {count} elements"
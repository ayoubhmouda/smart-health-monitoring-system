from reasoning.predictors.base import BasePredictor
from context.models import ContextHistory

class ReasoningEngine:
    def __init__(self, predictor: BasePredictor):
        self._predictor = predictor

    def reason(self, monitored_element):
        latest_history = ContextHistory.objects.filter(
            monitored_element=monitored_element
        ).order_by('-recorded_at').first()

        if not latest_history:
            return []

        insights = self._predictor.predict(latest_history)
        for insight in insights:
            insight.save()
        return insights
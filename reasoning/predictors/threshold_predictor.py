from .base import BasePredictor
from context.models import ContextHistory
from reasoning.models import Insight
from sensors.models import SensorType

class ThresholdPredictor(BasePredictor):
    def predict(self, context_history: ContextHistory) -> list[Insight]:
        context = context_history.context
        insights = []

        for key, value in context.physiological_data.items():
            try:
                stype = SensorType.objects.get(name__iexact=key.replace('_', ' '))
                if stype.normal_min is not None and stype.normal_max is not None:
                    if value < stype.normal_min or value > stype.normal_max:
                        severity = Insight.Severity.LOW
                        if value < stype.normal_min * 0.8 or value > stype.normal_max * 1.2:
                            severity = Insight.Severity.HIGH
                        insights.append(Insight(
                            monitored_element=context_history.monitored_element,
                            context_history=context_history,
                            insight_type=Insight.InsightType.CURRENT_ABNORMALITY,
                            severity=severity,
                            confidence=0.9,
                            source=Insight.Source.THRESHOLD
                        ))
            except SensorType.DoesNotExist:
                continue
        return insights
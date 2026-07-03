from abc import ABC, abstractmethod
from context.models import ContextHistory
from reasoning.models import Insight

class BasePredictor(ABC):
    @abstractmethod
    def predict(self, context_history: ContextHistory) -> list[Insight]:
        pass
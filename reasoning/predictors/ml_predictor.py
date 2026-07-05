import pickle
import os
from .base import BasePredictor
from context.models import ContextHistory
from reasoning.models import Insight
from reasoning.ml.feature_engineering import extract_features_from_window

class MLPredictor(BasePredictor):
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), '..', 'ml', 'models', 'random_forest.pkl')
        with open(model_path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.feature_names = data['feature_names']

    def predict(self, context_history: ContextHistory) -> list[Insight]:
        # نجلب آخر 6 سياقات (نافذة زمنية)
        recent = ContextHistory.objects.filter(
            monitored_element=context_history.monitored_element
        ).order_by('-recorded_at')[:6]

        if len(recent) < 6:
            return []  # لا توجد بيانات كافية

        # تجهيز النافذة بشكل عكسي (الأقدم فالأحدث)
        window_data = []
        for ctx_h in reversed(recent):
            ctx = ctx_h.context
            window_data.append({
                'heart_rate': ctx.physiological_data.get('heart_rate', 0),
                'blood_pressure_systolic': ctx.physiological_data.get('blood_pressure_systolic', 0),
                'blood_pressure_diastolic': ctx.physiological_data.get('blood_pressure_diastolic', 0),
                'oxygen_saturation': ctx.physiological_data.get('oxygen_saturation', 0),
                'activity_level': ctx.activity_data.get('activity_level', 0),
                'room_temperature': ctx.environmental_data.get('room_temperature', 0),
            })

        # استخراج الميزات
        import pandas as pd
        feats = extract_features_from_window(window_data)
        if feats is None:
            return []

        X = pd.DataFrame([feats], columns=self.feature_names)
        proba = self.model.predict_proba(X)[0]
        risk_prob = proba[1] if len(proba) > 1 else 0

        if risk_prob > 0.7:  # عتبة التنبيه
            insight = Insight(
                monitored_element=context_history.monitored_element,
                context_history=context_history,
                insight_type=Insight.InsightType.PREDICTED_RISK,
                severity=Insight.Severity.HIGH if risk_prob > 0.9 else Insight.Severity.MEDIUM,
                confidence=risk_prob,
                source=Insight.Source.ML_MODEL
            )
            return [insight]
        return []
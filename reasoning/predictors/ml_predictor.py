import os
import pickle
import pandas as pd
import numpy as np
from context.models import ContextHistory
from core.models import MedicalHistory
from reasoning.models import Insight
from .base import BasePredictor
# 🟢 استيراد دالة هندسة الميزات الموحدة
from reasoning.ml.feature_engineering import extract_features_from_window


class MLPredictor(BasePredictor):
    """
    مُتنبئ الذكاء الاصطناعي المعتمد على MIMIC-IV (22 ميزة).
    يستخدم دالة هندسة الميزات الموحدة لضمان تطابق مدخلات التنبؤ الفوري مع مدخلات التدريب.
    """

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(__file__), "..", "ml", "models", "random_forest.pkl"
            )

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"لم يتم العثور على نموذج MIMIC في: {model_path}")

        with open(model_path, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.feature_names = data["feature_names"]
            self.best_threshold = data.get("best_threshold", 0.55)

    def _extract_medical_history_features(self, element) -> dict:
        """استخراج تاريخ المريض الطبي الحقيقي من قاعدة البيانات وتجهيز ميزاته"""
        has_heart_disease = 0
        has_chronic_condition = 0

        try:
            med_hist = element.medical_history
            conditions = med_hist.chronic_conditions or []

            cond_names = []
            for item in conditions:
                if isinstance(item, str):
                    cond_names.append(item.lower())
                elif isinstance(item, dict):
                    cond_names.append(str(item.get('name', '')).lower())

            if any(c in cond_names for c in ['heart_disease', 'heart_failure', 'cardiac', '410', '428', 'i50', 'i21']):
                has_heart_disease = 1

            if any(c in cond_names for c in ['diabetes', 'hypertension', 'copd', '401', '250', 'e11', 'i10']):
                has_chronic_condition = 1

        except (MedicalHistory.DoesNotExist, AttributeError):
            pass

        return {
            'has_heart_disease': has_heart_disease,
            'has_chronic_condition': has_chronic_condition,
            'anchor_age': float(getattr(element, 'age', 30) or 30),
            'is_female': 1 if str(getattr(element, 'gender', 'M')).upper() in ['F', 'FEMALE'] else 0
        }

    def predict(self, context_history: ContextHistory) -> list[Insight]:
        element = context_history.monitored_element

        # سحب أحدث 6 قراءات زمنية مسجلة للمريض
        recent = list(
            ContextHistory.objects.filter(monitored_element=element)
            .order_by("-recorded_at")[:6]
        )

        if not recent:
            return []

        # تحويل بيانات الحساسات المختلفة إلى قائمة من القواميس المسطحة (Flat Dicts)
        flat_contexts = []
        for ctx_h in recent:
            ctx = ctx_h.context
            merged = {}
            merged.update(ctx.physiological_data or {})
            merged.update(ctx.activity_data or {})
            merged.update(ctx.environmental_data or {})
            flat_contexts.append(merged)

        # التأكد من توفر علامات حيوية رئيسية واحدة على الأقل في النافذة الزمنية
        if not flat_contexts or not any(c.get("heart_rate") or c.get("oxygen_saturation") or c.get("blood_pressure_systolic") for c in flat_contexts):
            return []

        # استخراج الميزات الطبية الثابتة للمريض
        med_features = self._extract_medical_history_features(element)

        # 🟢 استدعاء دالة هندسة الميزات الموحدة
        features_dict = extract_features_from_window(flat_contexts, med_features)

        # تنظيم الميزات كـ DataFrame متوافق مع مدخلات النموذج الرياضي
        df_input = pd.DataFrame([features_dict])
        X = df_input[self.feature_names]

        # التنبؤ الفوري بنسبة الخطر بواسطة نموذج الـ Random Forest
        proba = self.model.predict_proba(X)[0]
        risk_prob = proba[1] if len(proba) > 1 else proba[0]

        if risk_prob >= self.best_threshold:
            insight = Insight(
                monitored_element=element,
                context_history=context_history,
                insight_type=Insight.InsightType.PREDICTED_RISK,
                severity=Insight.Severity.HIGH if risk_prob > 0.8 else Insight.Severity.MEDIUM,
                confidence=round(float(risk_prob), 2),
                source=Insight.Source.ML_MODEL,
            )
            return [insight]

        return []
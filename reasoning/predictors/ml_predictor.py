import os
import pickle
import pandas as pd
from context.models import ContextHistory
from core.models import MedicalHistory
from reasoning.ml.feature_engineering import extract_features_from_window
from reasoning.models import Insight
from .base import BasePredictor


class MLPredictor(BasePredictor):

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "ml",
                "models",
                "random_forest.pkl",
            )
        with open(model_path, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.feature_names = data["feature_names"]

    def _extract_condition_names(self, conditions):
        if not conditions:
            return []
        names = []
        for item in conditions:
            if isinstance(item, str):
                names.append(item.lower().strip())
            elif isinstance(item, dict):
                name = (
                    item.get("name")
                    or item.get("condition")
                    or item.get("disease")
                    or ""
                )
                if name:
                    names.append(name.lower().strip())
        return names

    def _get_smoking_status(self, lifestyle):
        smoking = lifestyle.get("smoking", "never")
        if isinstance(smoking, str):
            smoking = smoking.lower().strip()
        if smoking == "current":
            return 2
        elif smoking == "former":
            return 1
        return 0

    def predict(self, context_history: ContextHistory) -> list[Insight]:

        # 1. جلب آخر 6 سياقات (النافذة الزمنية) مرتبة من الأحدث للأقدم
        recent = ContextHistory.objects.filter(
            monitored_element=context_history.monitored_element
        ).order_by("-recorded_at")[:6]

        if len(recent) < 6:
            return []

        # 2. الحصول على بيانات المريض الحقيقية من قاعدة البيانات
        element = context_history.monitored_element
        age = element.age
        gender_code = 1 if element.gender == "M" else 0

        lifestyle = {}
        raw_conditions = []

        try:
            med_hist = element.medical_history
            raw_conditions = med_hist.chronic_conditions or []
            lifestyle = med_hist.lifestyle or {}
        except MedicalHistory.DoesNotExist:
            pass

        conditions = self._extract_condition_names(raw_conditions)

        # 3. تجهيز النافذة بشكل عكسي (الأقدم فالأحدث مصفوفة زمنياً)
        window_data = []
        for ctx_h in reversed(recent):
            ctx = ctx_h.context
            point = {
                "heart_rate": ctx.physiological_data.get("heart_rate", 0),
                "blood_pressure_systolic": ctx.physiological_data.get(
                    "blood_pressure_systolic", 0
                ),
                "blood_pressure_diastolic": ctx.physiological_data.get(
                    "blood_pressure_diastolic", 0
                ),
                "oxygen_saturation": ctx.physiological_data.get(
                    "oxygen_saturation", 0
                ),
                "body_temperature": ctx.physiological_data.get(
                    "body_temperature", 37.0
                ),
                "activity_level": ctx.activity_data.get("activity_level", 0),
                "room_temperature": ctx.environmental_data.get(
                    "room_temperature", 0
                ),
                "age": age,
                "gender": gender_code,
                "has_hypertension": 1 if "hypertension" in conditions else 0,
                "has_diabetes": 1 if "diabetes" in conditions else 0,
                "has_heart_disease": 1 if "heart_disease" in conditions else 0,
                "smoking_status": self._get_smoking_status(lifestyle),
                "bmi": lifestyle.get("bmi", 25),
            }
            window_data.append(point)

        # 4. استخراج الميزات (باستخدام الكود المطور الذي يحسب القيم الحالية والـ Interaction)
        feats = extract_features_from_window(window_data)
        if feats is None:
            return []

        # 5. ترتيب الأعمدة وتحويلها لـ DataFrame متوافق مع النموذج تماماً
        X = pd.DataFrame([feats], columns=self.feature_names)
        for col in self.feature_names:
            if col not in X.columns:
                X[col] = 0
        X = X[self.feature_names]

        # 6. التنبؤ الخالص (اعتماد كامل على ذكاء الـ ML المستخلص من التدريب الشامل)
        proba = self.model.predict_proba(X)[0]
        risk_prob = proba[1] if len(proba) > 1 else 0

        # تم حذف التعديل اليدوي (Boost) لترك النموذج يتصرف طبياً بناءً على التدريب المتوازن

        # 7. اتخاذ القرار بناءً على عتبة الخطورة
        if risk_prob > 0.45:
            insight = Insight(
                monitored_element=context_history.monitored_element,
                context_history=context_history,
                insight_type=Insight.InsightType.PREDICTED_RISK,
                severity=(
                    Insight.Severity.HIGH
                    if risk_prob > 0.80
                    else Insight.Severity.MEDIUM
                ),
                confidence=round(float(risk_prob), 2),  # تحسين لعرض النسبة
                source=Insight.Source.ML_MODEL,
            )
            return [insight]

        return []
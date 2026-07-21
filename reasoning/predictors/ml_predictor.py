import os
import pickle
import pandas as pd
import numpy as np
from context.models import ContextHistory
from core.models import MedicalHistory
from reasoning.models import Insight
from .base import BasePredictor


class MLPredictor(BasePredictor):
    """
    مُتنبئ الذكاء الاصطناعي المعتمد على MIMIC-IV (22 ميزة).
    يعمل بمرونة: يعتمد على الحساسات المتوفرة، ويستكمل الحساسات المفقودة
    بقيم فيزيولوجية طبيعية آمنة حتى لا يتوقف النظام عن حماية المريض.
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
            self.best_threshold = data.get("best_threshold", 0.70)

    def _extract_medical_history_features(self, element) -> dict:
        """استخراج تاريخ المريض الطبي الحقيقي من قاعدة البيانات"""
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

        # تجميع العلامات الحيوية من الحساسات
        hr_l, sbp_l, dbp_l, spo2_l, temp_l, resp_l = [], [], [], [], [], []
        act_l, room_l = [], []

        for ctx_h in recent:
            ctx = ctx_h.context
            p = ctx.physiological_data or {}
            a = ctx.activity_data or {}
            e = ctx.environmental_data or {}

            if p.get("heart_rate") is not None: hr_l.append(float(p["heart_rate"]))
            if p.get("blood_pressure_systolic") is not None: sbp_l.append(float(p["blood_pressure_systolic"]))
            if p.get("blood_pressure_diastolic") is not None: dbp_l.append(float(p["blood_pressure_diastolic"]))
            if p.get("oxygen_saturation") is not None: spo2_l.append(float(p["oxygen_saturation"]))
            if p.get("body_temperature") is not None: temp_l.append(float(p["body_temperature"]))
            if p.get("respiratory_rate") is not None: resp_l.append(float(p["respiratory_rate"]))

            if a.get("activity_level") is not None: act_l.append(float(a["activity_level"]))
            if e.get("room_temperature") is not None: room_l.append(float(e["room_temperature"]))

        # 🛑 شرط الأدنى: يجب توفر علامة حيوية رئيسية واحدة على الأقل (مثل النبض أو الأكسجين أو الضغط)
        if not any([hr_l, spo2_l, sbp_l]):
            return []

        # حساب القراءات مع استخدام المبادئ الطبيعية (Baselines) للحساسات غير المربوطة
        # المبادئ الطبية الطبيعية: HR:75, SBP:120, DBP:80, SpO2:98%, Temp:37.0, Resp:16
        hr_mean = np.mean(hr_l) if hr_l else 75.0
        spo2_mean = np.mean(spo2_l) if spo2_l else 98.0
        sbp_mean = np.mean(sbp_l) if sbp_l else 120.0
        dbp_mean = np.mean(dbp_l) if dbp_l else 80.0
        temp_mean = np.mean(temp_l) if temp_l else 37.0
        resp_mean = np.mean(resp_l) if resp_l else 16.0

        med = self._extract_medical_history_features(element)

        features_dict = {
            'heart_rate_mean': hr_mean,
            'heart_rate_std': np.std(hr_l) if len(hr_l) > 1 else 0.0,
            'heart_rate_max': np.max(hr_l) if hr_l else hr_mean,
            'heart_rate_min': np.min(hr_l) if hr_l else hr_mean,

            'blood_pressure_systolic_mean': sbp_mean,
            'blood_pressure_systolic_std': np.std(sbp_l) if len(sbp_l) > 1 else 0.0,
            'blood_pressure_systolic_max': np.max(sbp_l) if sbp_l else sbp_mean,

            'blood_pressure_diastolic_mean': dbp_mean,
            'blood_pressure_diastolic_std': np.std(dbp_l) if len(dbp_l) > 1 else 0.0,
            'blood_pressure_diastolic_min': np.min(dbp_l) if dbp_l else dbp_mean,

            'oxygen_saturation_mean': spo2_mean,
            'oxygen_saturation_min': np.min(spo2_l) if spo2_l else spo2_mean,

            'body_temperature_mean': temp_mean,
            'body_temperature_max': np.max(temp_l) if temp_l else temp_mean,

            'respiratory_rate_mean': resp_mean,
            'respiratory_rate_max': np.max(resp_l) if resp_l else resp_mean,

            'activity_level_baseline': np.mean(act_l) if act_l else 1.0,
            'room_temperature_baseline': np.mean(room_l) if room_l else 22.0,

            **med
        }

        df_input = pd.DataFrame([features_dict])
        X = df_input[self.feature_names]

        # التنبؤ بواسطة نموذج MIMIC
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
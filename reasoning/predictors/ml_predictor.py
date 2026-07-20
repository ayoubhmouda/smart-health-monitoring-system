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
    يستخدم نموذج PhysioNet المدرب على ميزات Lag & Delta مباشرة (15 ميزة)،
    مع مُعزِّز شخصي للتاريخ الطبي + النشاط الحركي + البيئة المحيطة.
    تمت معالجة وحماية جميع القيم لمنع انهيار النظام بسبب قيم None أو Null.
    """

    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(__file__), "..", "ml", "models", "sepsis_model.pkl"
            )
        with open(model_path, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.feature_names = data["features"]
            self.best_threshold = data.get("best_threshold", 0.3)

    # ------------------------------------------------------------------
    # المُعزِّز الشخصي الشامل: يدمج (جميع) ميزات السياق والتاريخ الطبي رياضياً
    # يستخدم تحويل Log-Odds (Logit) لضمان دمج سيجمويدي حقيقي وغير خطي
    # ------------------------------------------------------------------
    def _apply_personal_risk_augmenter(self, element, risk_prob, activity_level=1, room_temperature=22):
        """
        تعديل احتمالية الخطر بناءً على مؤشر Charlson Comorbidity Index والبيئة والنشاط.
        تم دمج ميزات BMI و درجة حرارة الغرفة لضمان استخدام جميع ميزات مدخلات السياق الحالية.
        """
        comorbidity_score = 0.0

        try:
            med_hist = element.medical_history
            conditions = self._extract_condition_names(med_hist.chronic_conditions or [])
            lifestyle = med_hist.lifestyle or {}
        except (MedicalHistory.DoesNotExist, AttributeError):
            conditions = []
            lifestyle = {}

        # ============================================
        # 1. حساب أوزان التاريخ الطبي (الميزات الثابتة)
        # ============================================
        if 'heart_disease' in conditions or 'heart_failure' in conditions:
            comorbidity_score += 1.0
        if 'diabetes' in conditions:
            comorbidity_score += 1.0
        if 'hypertension' in conditions:
            comorbidity_score += 0.5

        # نمط الحياة والتدخين مع حماية القيمة الفارغة None
        smoking = 'never'
        if isinstance(lifestyle, dict):
            smoking = lifestyle.get('smoking', 'never')
            if smoking is None:
                smoking = 'never'

        if smoking == 'current':
            comorbidity_score += 0.5
        elif smoking == 'former':
            comorbidity_score += 0.2

        # ميزة مؤشر كتلة الجسم (BMI) - مع حماية كاملة من القيمة الفارغة None أو غير الرقمية
        bmi_val = 22.0
        if isinstance(lifestyle, dict):
            bmi_val = lifestyle.get('bmi', 22.0)
            
        try:
            bmi = float(bmi_val) if bmi_val is not None else 22.0
        except (ValueError, TypeError):
            bmi = 22.0

        if bmi > 35:
            comorbidity_score += 0.6  # سمنة مفرطة
        elif bmi > 30:
            comorbidity_score += 0.4  # سمنة
        elif bmi > 25:
            comorbidity_score += 0.2  # زيادة وزن

        # الدمج السيجمويدي غير الخطي للتاريخ الطبي والأمراض المزمنة
        if comorbidity_score > 0:
            risk_prob = max(min(risk_prob, 0.999), 0.001)
            logit = np.log(risk_prob / (1 - risk_prob))
            logit_adjusted = logit + (comorbidity_score * 0.25)
            adjusted_prob = 1 / (1 + np.exp(-logit_adjusted))
        else:
            adjusted_prob = risk_prob

        # ============================================
        # 2. تعديلات السياق الحي (النشاط والبيئة)
        # ============================================
        # أ: سياق النشاط الحركي مع الحماية
        try:
            act_level = int(activity_level) if activity_level is not None else 1
        except (ValueError, TypeError):
            act_level = 1

        if act_level == 3 and adjusted_prob > 0.4:
            adjusted_prob -= 0.1  # الجهد البدني العنيف يبرر ارتفاع المؤشرات طبيعياً
        elif act_level == 0 and adjusted_prob > 0.5:
            adjusted_prob += 0.1  # السكون التام مع مؤشرات سيئة يعني خطر حرج

        # ب: سياق البيئة المحيطة (درجة حرارة الغرفة) مع الحماية
        try:
            room_temp = float(room_temperature) if room_temperature is not None else 22.0
        except (ValueError, TypeError):
            room_temp = 22.0

        if room_temp > 32 and adjusted_prob > 0.4:
            adjusted_prob -= 0.05  # الجو الحار يبرر ارتفاع حرارة المريض جزئياً
        elif room_temp < 15 and adjusted_prob > 0.4:
            adjusted_prob += 0.05

        return max(min(adjusted_prob, 0.99), 0.01)

    # ------------------------------------------------------------------
    # استخراج أسماء الأمراض من القواميس (إن وجدت)
    # ------------------------------------------------------------------
    def _extract_condition_names(self, conditions):
        if not conditions:
            return []
        names = []
        for item in conditions:
            if isinstance(item, str):
                names.append(item.lower().strip())
            elif isinstance(item, dict):
                name = (
                    item.get('name') or
                    item.get('condition') or
                    item.get('disease') or
                    ''
                )
                if name:
                    names.append(name.lower().strip())
        return names

    # ------------------------------------------------------------------
    # دالة التنبؤ الرئيسية
    # ------------------------------------------------------------------
    def predict(self, context_history: ContextHistory) -> list[Insight]:
        recent = ContextHistory.objects.filter(
            monitored_element=context_history.monitored_element
        ).order_by("-recorded_at")[:6]

        if len(recent) < 6:
            return []

        element = context_history.monitored_element
        age = element.age
        gender_code = 1 if element.gender == "M" else 0

        # دالة مساعدة داخلية لحماية البيانات من الـ None أو القراءات التالفة لضمان استقرار العمليات الحسابية
        def safe_float(val, default):
            try:
                return float(val) if val is not None else default
            except (ValueError, TypeError):
                return default

        # بناء DataFrame من النافذة الزمنية
        rows = []
        for ctx_h in reversed(recent):
            ctx = ctx_h.context
            
            p_data = ctx.physiological_data or {}
            a_data = ctx.activity_data or {}
            e_data = ctx.environmental_data or {}

            hr = safe_float(p_data.get("heart_rate"), 80.0)
            o2 = safe_float(p_data.get("oxygen_saturation"), 98.0)
            temp = safe_float(p_data.get("body_temperature"), 37.0)
            sbp = safe_float(p_data.get("blood_pressure_systolic"), 120.0)
            dbp = safe_float(p_data.get("blood_pressure_diastolic"), 80.0)
            resp = safe_float(p_data.get("respiratory_rate"), 16.0)
            
            activity = safe_float(a_data.get("activity_level"), 1.0)
            room_temp = safe_float(e_data.get("room_temperature"), 22.0)

            rows.append({
                "HR": hr,
                "O2Sat": o2,
                "Temp": temp,
                "SBP": sbp,
                "MAP": dbp + (sbp - dbp) / 3,  # الآن آمنة تماماً من الـ TypeError
                "DBP": dbp,
                "Resp": resp,
                "Age": age,
                "Gender": gender_code,
                "Activity": activity,
                "RoomTemp": room_temp,
            })

        df = pd.DataFrame(rows)

        # بناء ميزات الذاكرة الزمنية (Lag & Delta) لنموذج الـ ML
        df['HR_past_hour'] = df['HR'].shift(1).fillna(df['HR'])
        df['HR_change'] = df['HR'] - df['HR_past_hour']
        df['O2Sat_past_hour'] = df['O2Sat'].shift(1).fillna(df['O2Sat'])
        df['O2Sat_change'] = df['O2Sat'] - df['O2Sat_past_hour']
        df['Temp_past_hour'] = df['Temp'].shift(1).fillna(df['Temp'])
        df['Temp_change'] = df['Temp'] - df['Temp_past_hour']

        # فلترة واستخلاص الـ 15 ميزة المحددة والمطلوبة للموديل فقط
        last_row = df.iloc[-1:][self.feature_names].fillna(0)

        # تنبؤ النموذج الأساسي (الـ ML)
        proba = self.model.predict_proba(last_row)[0]
        risk_prob = proba[1] if len(proba) > 1 else 0

        # استخراج قيم النشاط والحرارة البيئية لتمريرها للمعزز الشخصي فقط وليس للموديل
        latest_activity = df.iloc[-1].get("Activity", 1)
        latest_room_temp = df.iloc[-1].get("RoomTemp", 22)

        # تطبيق المُعزِّز الشخصي
        risk_prob = self._apply_personal_risk_augmenter(
            element, risk_prob, latest_activity, latest_room_temp
        )

        # تطبيق العتبة لإنتاج فكرة الخطر (Insight)
        if risk_prob > self.best_threshold:
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

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reasoning.predictors.ml_predictor import MLPredictor
from context.models import ContextHistory
from reasoning.ml.feature_engineering import extract_features_from_window
from core.models import MonitoredElement
import pandas as pd

ahmed = MonitoredElement.objects.get(full_name='احمد محمد')
predictor = MLPredictor()

recent = ContextHistory.objects.filter(monitored_element=ahmed).order_by('-recorded_at')[:6]
print('عدد السياقات في النافذة:', len(recent))

if len(recent) >= 6:
    window_data = []
    for ctx_h in reversed(recent):
        ctx = ctx_h.context
        point = {
            'heart_rate': ctx.physiological_data.get('heart_rate', 0),
            'blood_pressure_systolic': ctx.physiological_data.get('blood_pressure_systolic', 0),
            'blood_pressure_diastolic': ctx.physiological_data.get('blood_pressure_diastolic', 0),
            'oxygen_saturation': ctx.physiological_data.get('oxygen_saturation', 0),
            'body_temperature': ctx.physiological_data.get('body_temperature', 0),
            'activity_level': ctx.activity_data.get('activity_level', 0),
            'room_temperature': ctx.environmental_data.get('room_temperature', 0),
            'age': ahmed.age,
            'gender': 1 if ahmed.gender == 'M' else 0,
            'has_hypertension': 1,
            'has_diabetes': 1,
            'has_heart_disease': 0,
            'smoking_status': 2,
            'bmi': 32,
        }
        window_data.append(point)

    feats = extract_features_from_window(window_data)
    print('الميزات المستخرجة:', feats)

    if feats:
        X = pd.DataFrame([feats], columns=predictor.feature_names)
        for col in predictor.feature_names:
            if col not in X.columns:
                X[col] = 0
        X = X[predictor.feature_names]
        proba = predictor.model.predict_proba(X)[0]
        print('الاحتمالات:', proba)
        risk_prob = proba[1] if len(proba) > 1 else 0
        print('احتمالية الخطر:', risk_prob)
    else:
        print('فشل استخراج الميزات!')
else:
    print('لا توجد سياقات كافية (تحتاج 6)')
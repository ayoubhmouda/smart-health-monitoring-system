import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# ---------- اختبار دالة _calculate_risk_score ----------
from reasoning.ml.data_generator import ClinicalScenarioGenerator
gen = ClinicalScenarioGenerator()

# قيم حيوية معتدلة (في المنطقة الرمادية)
test_ctx = {
    'heart_rate': 105,
    'blood_pressure_systolic': 145,
    'blood_pressure_diastolic': 90,
    'oxygen_saturation': 93,
    'body_temperature': 37.8,
    'activity_level': 1,
    'age': 56,
}

# احسب لأحمد (56 سنة، ضغط وسكري، مدخن، بدين)
score_ahmed, threshold_ahmed = gen._calculate_risk_score(
    test_ctx, ['hypertension','diabetes'], {'smoking':'current','bmi':32}
)

# عدل العمر لـ 20 وأزل الأمراض والتدخين لخالد
test_ctx['age'] = 20
score_khaled, threshold_khaled = gen._calculate_risk_score(
    test_ctx, [], {'smoking':'never','bmi':22}
)

print("----- اختبار دالة _calculate_risk_score -----")
print(f"Ahmed risk_score: {score_ahmed:.3f} (threshold: {threshold_ahmed:.2f}) → label: {1 if score_ahmed > threshold_ahmed else 0}")
print(f"Khaled risk_score: {score_khaled:.3f} (threshold: {threshold_khaled:.2f}) → label: {1 if score_khaled > threshold_khaled else 0}")
print("(توقع: أحمد خطر، خالد آمن)\n")

# ---------- اختبار MLPredictor (آخر 6 سياقات لأحمد) ----------
from reasoning.predictors.ml_predictor import MLPredictor
from context.models import ContextHistory
from reasoning.ml.feature_engineering import extract_features_from_window
from core.models import MonitoredElement
import pandas as pd

ahmed = MonitoredElement.objects.get(full_name='احمد محمد')
predictor = MLPredictor()
recent = ContextHistory.objects.filter(monitored_element=ahmed).order_by('-recorded_at')[:6]

print("----- اختبار MLPredictor (أحمد محمد) -----")
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
    if feats:
        X = pd.DataFrame([feats], columns=predictor.feature_names)
        for col in predictor.feature_names:
            if col not in X.columns:
                X[col] = 0
        X = X[predictor.feature_names]
        proba = predictor.model.predict_proba(X)[0]
        risk_prob = proba[1] if len(proba) > 1 else 0
        print(f'احتمالية الخطر: {risk_prob:.3f}')
        print("(توقع: > 0.70 بعد التدريب الجيد)")
    else:
        print('فشل استخراج الميزات!')
else:
    print('لا توجد سياقات كافية (تحتاج 6)')
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import pickle, pandas as pd
from reasoning.ml.feature_engineering import extract_features_from_window

with open('reasoning/ml/models/random_forest.pkl', 'rb') as f:
    data = pickle.load(f)
model = data['model']
feature_names = data['feature_names']

def test_patient(label, age, has_h, has_d, smoking, bmi, hr, bp, o2):
    window = [{
        'heart_rate': hr + i*0.5,
        'blood_pressure_systolic': bp + i*0.5,
        'blood_pressure_diastolic': 88,
        'oxygen_saturation': o2 - i*0.1,
        'body_temperature': 37.8,
        'activity_level': 1,
        'room_temperature': 23,
        'age': age, 'gender': 1,
        'has_hypertension': has_h,
        'has_diabetes': has_d,
        'has_heart_disease': 0,
        'smoking_status': smoking,
        'bmi': bmi,
    } for i in range(6)]
    feats = extract_features_from_window(window)
    X = pd.DataFrame([feats], columns=feature_names)
    for col in feature_names:
        if col not in X.columns: X[col] = 0
    X = X[feature_names]
    prob = model.predict_proba(X)[0][1]
    print(f'{label}: {prob:.3f}')

print('=== Vitals معتدلة (HR~105, BP~145, O2~93) ===')
test_patient('أحمد (56، ضغط+سكري، مدخن، BMI32)', 56, 1, 1, 2, 32, 105, 145, 93)
test_patient('خالد (20، صحيح، BMI22)',             20, 0, 0, 0, 22, 105, 145, 93)
print()
print('=== Vitals شديدة (HR~125, BP~170, O2~88) ===')
test_patient('أحمد (56، ضغط+سكري، مدخن، BMI32)', 56, 1, 1, 2, 32, 125, 170, 88)
test_patient('خالد (20، صحيح، BMI22)',             20, 0, 0, 0, 22, 125, 170, 88)
print()
print('=== Vitals طبيعية (HR~78, BP~120, O2~97) ===')
test_patient('أحمد (56، ضغط+سكري، مدخن، BMI32)', 56, 1, 1, 2, 32, 78, 120, 97)
test_patient('خالد (20، صحيح، BMI22)',             20, 0, 0, 0, 22, 78, 120, 97)
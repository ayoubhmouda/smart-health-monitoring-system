import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "shms.settings")
try:
    django.setup()
except Exception:
    pass

import pandas as pd
from reasoning.predictors.ml_predictor import MLPredictor


def run_feature_test():
    p = MLPredictor()

    # 1. عرض أوزان الميزات
    importances = p.model.feature_importances_
    features_importance = sorted(
        zip(p.feature_names, importances), key=lambda x: x[1], reverse=True
    )

    print("\n" + "=" * 60)
    print("📊 أوزان الميزات (Feature Importances) في نموذج MIMIC-IV:")
    print("=" * 60)
    for name, imp in features_importance:
        print(f"{name:<32} : {imp*100:.2f}%")

    # 2. إعداد مريض سلييييم 100% بكل قيم حدوده الأدنى والأقصى
    base_patient = {
        'heart_rate_mean': 75.0, 'heart_rate_max': 80.0, 'heart_rate_min': 70.0, 'heart_rate_std': 2.0,
        'oxygen_saturation_mean': 98.0, 'oxygen_saturation_min': 96.0,
        'blood_pressure_systolic_mean': 120.0, 'blood_pressure_systolic_max': 125.0, 'blood_pressure_systolic_std': 3.0,
        'blood_pressure_diastolic_mean': 80.0, 'blood_pressure_diastolic_min': 75.0, 'blood_pressure_diastolic_std': 2.0,
        'body_temperature_mean': 37.0, 'body_temperature_max': 37.2,
        'respiratory_rate_mean': 16.0, 'respiratory_rate_max': 18.0,
        'activity_level_baseline': 1.0, 'room_temperature_baseline': 22.0,
        'anchor_age': 35.0, 'is_female': 0,
        'has_heart_disease': 0, 'has_chronic_condition': 0
    }

    def get_risk(data_dict):
        df = pd.DataFrame([data_dict])[p.feature_names]
        return round(p.model.predict_proba(df)[0][1] * 100, 2)

    print("\n" + "=" * 60)
    print("🔬 اختبار حساسية النموذج بعد إعطاء قيم طبيعية صحيحة:")
    print("=" * 60)
    
    # حالة طبيعية
    risk_normal = get_risk(base_patient)
    print(f"1. مريض سليـــم تماماً (بدون أمراض وقراءات سليمة) <- نسبة الخطر: {risk_normal}%")

    # إضافة مرض مزمن (مثل السكري/الضغط)
    case_chronic = base_patient.copy()
    case_chronic['has_chronic_condition'] = 1
    print(f"2. إضافة مرض مزمن (كالسكري/الضغط) في السجل الطبي   <- نسبة الخطر: {get_risk(case_chronic)}%")

    # إضافة مرض قلب
    case_heart = base_patient.copy()
    case_heart['has_heart_disease'] = 1
    print(f"3. إضافة مرض قلب في السجل الطبي                  <- نسبة الخطر: {get_risk(case_heart)}%")

    # انخفاض ضغط الدم الانبساطي الأدنى
    case_bp = base_patient.copy()
    case_bp['blood_pressure_diastolic_min'] = 45.0
    case_bp['blood_pressure_diastolic_mean'] = 55.0
    print(f"4. انخفاض ضغط الدم الانبساطي إلى 45 mmHg           <- نسبة الخطر: {get_risk(case_bp)}%")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_feature_test()
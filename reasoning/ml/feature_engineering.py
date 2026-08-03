# feature_engineering.py
import numpy as np
import pandas as pd

def extract_features_from_window(contexts, medical_features: dict) -> dict:
    """
    تستخرج الـ 22 ميزة المتوافقة تماماً مع نموذج MIMIC-IV والـ MLPredictor.
    تستقبل قائمة بالـ contexts للمريض، وقاموساً يحتوي على ميزات التاريخ الطبي المجهز.
    """
    if not contexts:
        return None

    # استخراج السلاسل الزمنية
    hr = [c.get("heart_rate") for c in contexts if c.get("heart_rate") is not None]
    sbp = [c.get("blood_pressure_systolic") for c in contexts if c.get("blood_pressure_systolic") is not None]
    dbp = [c.get("blood_pressure_diastolic") for c in contexts if c.get("blood_pressure_diastolic") is not None]
    o2 = [c.get("oxygen_saturation") for c in contexts if c.get("oxygen_saturation") is not None]
    temp = [c.get("body_temperature") for c in contexts if c.get("body_temperature") is not None]
    resp = [c.get("respiratory_rate") for c in contexts if c.get("respiratory_rate") is not None]
    act = [c.get("activity_level") for c in contexts if c.get("activity_level") is not None]
    room = [c.get("room_temperature") for c in contexts if c.get("room_temperature") is not None]

    #Baselines الطبية في حال غياب بعض الحساسات مؤقتاً
    hr_mean = np.mean(hr) if hr else 75.0
    sbp_mean = np.mean(sbp) if sbp else 120.0
    dbp_mean = np.mean(dbp) if dbp else 80.0
    o2_mean = np.mean(o2) if o2 else 98.0
    temp_mean = np.mean(temp) if temp else 37.0
    resp_mean = np.mean(resp) if resp else 16.0

    features = {
        'heart_rate_mean': hr_mean,
        'heart_rate_std': np.std(hr) if len(hr) > 1 else 0.0,
        'heart_rate_max': np.max(hr) if hr else hr_mean,
        'heart_rate_min': np.min(hr) if hr else hr_mean,

        'blood_pressure_systolic_mean': sbp_mean,
        'blood__pressure_systolic_mean': sbp_mean,
        'blood_pressure_systolic_std': np.std(sbp) if len(sbp) > 1 else 0.0,
        'blood_pressure_systolic_max': np.max(sbp) if sbp else sbp_mean,

        'blood_pressure_diastolic_mean': dbp_mean,
        'blood_pressure_diastolic_std': np.std(dbp) if len(dbp) > 1 else 0.0,
        'blood_pressure_diastolic_min': np.min(dbp) if dbp else dbp_mean,

        'oxygen_saturation_mean': o2_mean,
        'oxygen_saturation_min': np.min(o2) if o2 else o2_mean,

        'body_temperature_mean': temp_mean,
        'body_temperature_max': np.max(temp) if temp else temp_mean,

        'respiratory_rate_mean': resp_mean,
        'respiratory_rate_max': np.max(resp) if resp else resp_mean,

        'activity_level_baseline': np.mean(act) if act else 1.0,
        'room_temperature_baseline': np.mean(room) if room else 22.0,

        # دمج التاريخ الطبي
        'has_heart_disease': medical_features.get('has_heart_disease', 0),
        'has_chronic_condition': medical_features.get('has_chronic_condition', 0),
        'anchor_age': float(medical_features.get('anchor_age', 30.0)),
        'is_female': medical_features.get('is_female', 0)
    }

    return features
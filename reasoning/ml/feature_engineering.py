import numpy as np
import pandas as pd


def extract_features_from_window(contexts):
    """تحول قائمة من القواميس (contexts) مرتبة زمنياً إلى متجه ميزات مطور."""
    if not contexts:
        return None

    # استخراج السلاسل الزمنية للمؤشرات الحيوية
    hr = [c.get("heart_rate", 0) for c in contexts]
    bp_sys = [c.get("blood_pressure_systolic", 0) for c in contexts]
    bp_dia = [c.get("blood_pressure_diastolic", 0) for c in contexts]
    o2 = [c.get("oxygen_saturation", 0) for c in contexts]
    body_temp = [c.get("body_temperature", 0) for c in contexts]
    act = [c.get("activity_level", 0) for c in contexts]
    room_temp = [c.get("room_temperature", 0) for c in contexts]
    blood_glucose = [c.get("blood_glucose", 0) for c in contexts]
    respiratory_rate = [c.get("respiratory_rate", 0) for c in contexts]

    # حساب MAP (Mean Arterial Pressure) من SBP و DBP
    map_vals = [dbp + (sbp - dbp) / 3 for sbp, dbp in zip(bp_sys, bp_dia)]

    features = {}

    # --- 1. الميزات الفورية الحالية ---
    features["current_hr"] = hr[-1]
    features["current_bp_sys"] = bp_sys[-1]
    features["current_bp_dia"] = bp_dia[-1]
    features["current_o2"] = o2[-1]
    features["current_body_temp"] = body_temp[-1]
    features["current_blood_glucose"] = blood_glucose[-1]
    features["current_respiratory_rate"] = respiratory_rate[-1]
    features["current_map"] = map_vals[-1]

    # أعلام الخطورة المطلقة
    features["is_hr_critically_high"] = 1 if hr[-1] > 100 else 0
    features["is_o2_critically_low"] = 1 if o2[-1] < 92 else 0
    features["is_bp_sys_critically_high"] = 1 if bp_sys[-1] > 140 else 0

    # --- 2. ميزات الذاكرة الزمنية (Lag & Delta) – متوافقة مع PhysioNet ---
    # Heart Rate
    features["hr_past_hour"] = hr[-2] if len(hr) >= 2 else hr[-1]
    features["hr_change"] = hr[-1] - hr[-2] if len(hr) >= 2 else 0

    # Oxygen Saturation
    features["o2sat_past_hour"] = o2[-2] if len(o2) >= 2 else o2[-1]
    features["o2_change"] = o2[-1] - o2[-2] if len(o2) >= 2 else 0

    # Body Temperature
    features["temp_past_hour"] = body_temp[-2] if len(body_temp) >= 2 else body_temp[-1]
    features["temp_change"] = body_temp[-1] - body_temp[-2] if len(body_temp) >= 2 else 0

    # --- 3. إحصائيات النافذة الزمنية العامة ---
    features["hr_mean"] = np.mean(hr)
    features["hr_std"] = np.std(hr)
    features["hr_trend"] = hr[-1] - hr[0] if len(hr) > 1 else 0

    features["bp_sys_mean"] = np.mean(bp_sys)
    features["bp_sys_std"] = np.std(bp_sys)

    features["bp_dia_mean"] = np.mean(bp_dia)
    features["bp_dia_std"] = np.std(bp_dia)

    features["o2_mean"] = np.mean(o2)
    features["o2_std"] = np.std(o2)

    features["body_temp_mean"] = np.mean(body_temp)
    features["body_temp_std"] = np.std(body_temp)

    # ميزات MAP
    features["map_mean"] = np.mean(map_vals)
    features["map_std"] = np.std(map_vals)
    features["map_trend"] = map_vals[-1] - map_vals[0] if len(map_vals) > 1 else 0

    # ميزات المستشعرين الجديدين
    features["bg_mean"] = np.mean(blood_glucose)
    features["bg_std"] = np.std(blood_glucose)
    features["bg_trend"] = blood_glucose[-1] - blood_glucose[0] if len(blood_glucose) > 1 else 0

    features["rr_mean"] = np.mean(respiratory_rate)
    features["rr_std"] = np.std(respiratory_rate)
    features["rr_trend"] = respiratory_rate[-1] - respiratory_rate[0] if len(respiratory_rate) > 1 else 0

    features["last_activity"] = act[-1]
    features["last_room_temp"] = room_temp[-1]
    features["window_size"] = len(contexts)

    # --- 4. الميزات الشخصية والطبية الثابتة ---
    last_ctx = contexts[-1]
    features["age"] = last_ctx.get("age", 50)
    features["gender"] = last_ctx.get("gender", 0)
    features["has_hypertension"] = last_ctx.get("has_hypertension", 0)
    features["has_diabetes"] = last_ctx.get("has_diabetes", 0)
    features["has_heart_disease"] = last_ctx.get("has_heart_disease", 0)
    features["smoking_status"] = last_ctx.get("smoking_status", 0)
    features["bmi"] = last_ctx.get("bmi", 25)

    # ميزات التاريخ العائلي
    features["family_heart_disease"] = last_ctx.get("family_heart_disease", 0)
    features["family_diabetes"] = last_ctx.get("family_diabetes", 0)

    # --- 5. ميزات التفاعل المركبة ---
    features["hr_x_hypertension"] = (
        features["current_hr"] * features["has_hypertension"]
    )
    features["bp_sys_x_hypertension"] = (
        features["current_bp_sys"] * features["has_hypertension"]
    )

    features["crit_hr_x_heart_disease"] = (
        features["is_hr_critically_high"] * features.get("has_heart_disease", 0)
    )
    features["crit_bp_x_hypertension"] = (
        features["is_bp_sys_critically_high"] * features.get("has_hypertension", 0)
    )

    return features


def prepare_training_data(scenarios):
    """تحول السيناريوهات إلى X (DataFrame) و y (Series) جاهزة للتدريب."""
    X = []
    y = []
    window_size = 6

    for scenario in scenarios:
        for i in range(window_size, len(scenario) + 1):
            window = [ctx for ctx, _ in scenario[i - window_size : i]]
            label = scenario[i - 1][1]

            feats = extract_features_from_window(window)
            if feats:
                X.append(feats)
                y.append(label)

    return pd.DataFrame(X), pd.Series(y)
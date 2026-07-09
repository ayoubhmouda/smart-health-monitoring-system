import numpy as np
import pandas as pd  # استيراد باندا أساسي لتحويل الميزات


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

    features = {}

    # --- 1. الميزات الفورية الحالية ---
    features["current_hr"] = hr[-1]
    features["current_bp_sys"] = bp_sys[-1]
    features["current_bp_dia"] = bp_dia[-1]
    features["current_o2"] = o2[-1]
    features["current_body_temp"] = body_temp[-1]

    # [إضافة حاسمة]: أعلام الخطورة المطلقة (لحماية النموذج من عتبات الاستقرار الكاذب)
    features["is_hr_critically_high"] = 1 if hr[-1] > 100 else 0
    features["is_o2_critically_low"] = 1 if o2[-1] < 92 else 0
    features["is_bp_sys_critically_high"] = 1 if bp_sys[-1] > 140 else 0

    # --- 2. Tالتغير اللحظي الفوري ---
    features["hr_immediate_change"] = hr[-1] - hr[-2] if len(hr) > 1 else 0
    features["bp_sys_immediate_change"] = (
        bp_sys[-1] - bp_sys[-2] if len(bp_sys) > 1 else 0
    )
    features["o2_immediate_change"] = o2[-1] - o2[-2] if len(o2) > 1 else 0

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

    # --- 5. ميزات التفاعل المركبة (Interaction Features) ---
    features["hr_x_hypertension"] = (
        features["current_hr"] * features["has_hypertension"]
    )
    features["bp_sys_x_hypertension"] = (
        features["current_bp_sys"] * features["has_hypertension"]
    )

    # [إضافة حاسمة]: دمج أعلام الخطورة المطلقة بالتاريخ الطبي للمريض
    features["crit_hr_x_heart_disease"] = (
        features["is_hr_critically_high"] * last_ctx.get("has_heart_disease", 0)
    )
    features["crit_bp_x_hypertension"] = (
        features["is_bp_sys_critically_high"]
        * last_ctx.get("has_hypertension", 0)
    )

    return features


def prepare_training_data(scenarios):
    """تحول السيناريوهات إلى X (DataFrame) و y (Series) جاهزة تماماً لتدريب الـ

    Random Forest دون أي أخطاء توافقية.
    """
    X = []
    y = []
    window_size = 6

    for scenario in scenarios:
        # إصلاح الثغرة الأولى: إضافة +1 لضمان شمول النقطة الأخيرة وعدم تجاهل السيناريوهات ذات الـ 6 نقاط
        for i in range(window_size, len(scenario) + 1):
            window = [ctx for ctx, _ in scenario[i - window_size : i]]
            label = scenario[i - 1][1]  # جلب الـ label الخاص بآخر عنصر في النافذة

            feats = extract_features_from_window(window)
            if feats:
                X.append(feats)
                y.append(label)

    # إصلاح الثغرة الثانية: التحويل لـ DataFrame و Series لتغذية مكتبة sklearn مباشرة
    return pd.DataFrame(X), pd.Series(y)
import numpy as np

def extract_features_from_window(contexts):
    """
    يحول قائمة من القواميس (contexts) مرتبة زمنياً إلى متجه ميزات.
    الميزات تشمل:
    - المتوسط والانحراف المعياري لكل متغير فسيولوجي خلال النافذة.
    - الميل (trend) لتقدير التغير.
    - آخر قيمة للنشاط والحرارة.
    """
    if not contexts:
        return None

    # استخراج السلاسل الزمنية
    hr = [c['heart_rate'] for c in contexts]
    bp_sys = [c['blood_pressure_systolic'] for c in contexts]
    bp_dia = [c['blood_pressure_diastolic'] for c in contexts]
    o2 = [c['oxygen_saturation'] for c in contexts]
    act = [c['activity_level'] for c in contexts]
    temp = [c['room_temperature'] for c in contexts]

    features = {}

    # Heart Rate
    features['hr_mean'] = np.mean(hr)
    features['hr_std'] = np.std(hr)
    features['hr_trend'] = hr[-1] - hr[0] if len(hr) > 1 else 0

    # BP Sys
    features['bp_sys_mean'] = np.mean(bp_sys)
    features['bp_sys_std'] = np.std(bp_sys)
    features['bp_sys_trend'] = bp_sys[-1] - bp_sys[0] if len(bp_sys) > 1 else 0

    # BP Dia
    features['bp_dia_mean'] = np.mean(bp_dia)
    features['bp_dia_std'] = np.std(bp_dia)
    features['bp_dia_trend'] = bp_dia[-1] - bp_dia[0] if len(bp_dia) > 1 else 0

    # Oxygen
    features['o2_mean'] = np.mean(o2)
    features['o2_std'] = np.std(o2)
    features['o2_trend'] = o2[-1] - o2[0] if len(o2) > 1 else 0

    # آخر قيم للنشاط والحرارة
    features['last_activity'] = act[-1]
    features['last_temp'] = temp[-1]

    # عدد القراءات (حجم النافذة)
    features['window_size'] = len(contexts)

    return features

def prepare_training_data(scenarios):
    """
    يحول السيناريوهات (قائمة من سيناريوهات، كل سيناريو هو قائمة من (context_dict, label)) إلى X و y.
    """
    X = []
    y = []
    window_size = 6
    for scenario in scenarios:  # الآن كل سيناريو هو قائمة من النقاط
        for i in range(window_size, len(scenario)):
            window = [ctx for ctx, _ in scenario[i-window_size:i]]
            label = scenario[i][1]
            feats = extract_features_from_window(window)
            if feats:
                X.append(feats)
                y.append(label)
    return X, y
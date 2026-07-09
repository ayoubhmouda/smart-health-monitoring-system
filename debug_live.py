import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from context.models import ContextHistory
from core.models import MonitoredElement, MedicalHistory
from reasoning.ml.feature_engineering import extract_features_from_window

for el in MonitoredElement.objects.all():
    if 'احمد' in str(el):
        print(f'=== {el} ===')
        
        recent = ContextHistory.objects.filter(
            monitored_element=el
        ).order_by('-recorded_at')[:6]
        print(f'عدد السياقات: {len(recent)}')
        
        for i, ctx_h in enumerate(reversed(recent)):
            ctx = ctx_h.context
            print(f'  سياق {i+1}: HR={ctx.physiological_data.get("heart_rate","?"):.1f}, BP={ctx.physiological_data.get("blood_pressure_systolic","?"):.1f}, O2={ctx.physiological_data.get("oxygen_saturation","?"):.1f}')
        
        try:
            mh = el.medical_history
            print(f'chronic_conditions: {mh.chronic_conditions}')
            print(f'lifestyle: {mh.lifestyle}')
        except:
            print('لا يوجد تاريخ طبي')
        
        window_data = []
        for ctx_h in reversed(recent):
            ctx = ctx_h.context
            window_data.append({
                'heart_rate': ctx.physiological_data.get('heart_rate', 0),
                'blood_pressure_systolic': ctx.physiological_data.get('blood_pressure_systolic', 0),
                'blood_pressure_diastolic': ctx.physiological_data.get('blood_pressure_diastolic', 0),
                'oxygen_saturation': ctx.physiological_data.get('oxygen_saturation', 0),
                'body_temperature': ctx.physiological_data.get('body_temperature', 37.0),
                'activity_level': ctx.activity_data.get('activity_level', 0),
                'room_temperature': ctx.environmental_data.get('room_temperature', 0),
                'age': el.age,
                'has_hypertension': 1,
                'has_diabetes': 1,
                'smoking_status': 2,
                'bmi': 32,
                'gender': 1,
                'has_heart_disease': 0,
            })
        
        feats = extract_features_from_window(window_data)
        print(f'hr_mean: {feats["hr_mean"]:.1f}')
        print(f'bp_sys_mean: {feats["bp_sys_mean"]:.1f}')
        print(f'o2_mean: {feats["o2_mean"]:.1f}')
        print(f'has_hypertension: {feats["has_hypertension"]}')
        print(f'has_diabetes: {feats["has_diabetes"]}')
        print(f'smoking_status: {feats["smoking_status"]}')
        print(f'bmi: {feats["bmi"]}')
        break
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import MonitoredElement
from context.models import ContextHistory
from reasoning.predictors.threshold_predictor import ThresholdPredictor
from reasoning.predictors.ml_predictor import MLPredictor

def test_patient(patient_name):
    try:
        patient = MonitoredElement.objects.get(full_name=patient_name)
    except MonitoredElement.DoesNotExist:
        print(f"❌ المريض '{patient_name}' غير موجود.")
        return

    latest_ctx = ContextHistory.objects.filter(
        monitored_element=patient
    ).order_by('-recorded_at').first()

    if not latest_ctx:
        print(f"⚠️ لا يوجد سياق مسجل للمريض '{patient_name}'.")
        return

    ctx = latest_ctx.context

    # 1. عرض القيم الحالية
    print(f"\n📋 أحدث قراءات للمريض: {patient.full_name}")
    print("-" * 50)
    phys = ctx.physiological_data or {}
    for k, v in phys.items():
        print(f"  • {k}: {v}")
    print(f"  • activity_level: {ctx.activity_data.get('activity_level', 'غير متوفر')}")
    print(f"  • room_temperature: {ctx.environmental_data.get('room_temperature', 'غير متوفر')}")

    # 2. تشغيل ThresholdPredictor
    print("\n🔴 تشغيل ThresholdPredictor (شبكة الأمان)...")
    threshold = ThresholdPredictor()
    insights_t = threshold.predict(latest_ctx)
    if insights_t:
        for ins in insights_t:
            print(f"  ⚠️  إنذار: {ins.get_insight_type_display()} | خطورة: {ins.get_severity_display()} | ثقة: {ins.confidence}")
    else:
        print("  ✅ لا يوجد إنذار (جميع القيم طبيعية).")

    # 3. تشغيل MLPredictor
    print("\n🟢 تشغيل MLPredictor (نموذج MIMIC)...")
    ml = MLPredictor()
    insights_ml = ml.predict(latest_ctx)
    if insights_ml:
        for ins in insights_ml:
            print(f"  🤖 تنبؤ: {ins.get_insight_type_display()} | خطورة: {ins.get_severity_display()} | ثقة: {ins.confidence}")
    else:
        print("  ✅ لا يوجد تنبؤ (احتمالية الخطر أقل من العتبة).")

if __name__ == "__main__":
    import sys
    # يمكنك تمرير اسم المريض كوسيط، مثال: python test_predictors.py "فتحي محمد"
    if len(sys.argv) > 1:
        patient_name = sys.argv[1]
    else:
        patient_name = "فتحي محمد"  # الاسم الافتراضي للتجربة

    test_patient(patient_name)
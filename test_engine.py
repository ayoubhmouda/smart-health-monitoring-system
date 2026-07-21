import os
import django

django.setup()

from reasoning.engine import ReasoningEngine
from reasoning.predictors.ml_predictor import MLPredictor
from core.models import MonitoredElement

def run_test():
    print("🔍 بدء اختبار Reasoning Engine لجميع المرضى...\n")
    
    elements = MonitoredElement.objects.all()
    if not elements.exists():
        print("❌ لا يوجد عناصر مراقَبة في قاعدة البيانات!")
        return

    # 1. تهيئة الـ Predictor والمحرك
    ml_predictor = MLPredictor()
    engine = ReasoningEngine(ml_predictor)

    for element in elements:
        print(f"👤 فحص العنصر: {element.full_name} ({element.get_element_type_display()})")
        
        # 2. استدعاء الدالة الصحيحة reason()
        insights = engine.reason(element)
        
        print(f"   📊 عدد التنبيهات الناتجة: {len(insights)}")
        for idx, insight in enumerate(insights, 1):
            print(f"      {idx}. [Insight] المصدر: {insight.source} | النوع: {insight.insight_type} | الخطورة: {insight.severity} | درجة الثقة: {insight.confidence}")
        print("-" * 60)

    print("\n✅ تم تشغيل المحرك بنجاح لجميع المرضى!")

if __name__ == "__main__":
    run_test()
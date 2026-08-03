# test_all.py
from core.models import MonitoredElement
from sensors.models import Sensor, SensorReading, DataSourceConfig
from context.models import Context, ContextHistory
from reasoning.models import Insight
from sensors.tasks import read_all_active_sensors
from context.tasks import aggregate_all_contexts

def run_test():
    print("=" * 60)
    print("🚀 بدء الاختبار الشامل والمتتابع للنظام الذكي")
    print("=" * 60)

    patients = MonitoredElement.objects.all()
    active_sensors = Sensor.objects.filter(is_active=True)
    print(f"🔹 المرضى المتاحون: {patients.count()}")
    print(f"🔹 الحساسات النشطة: {active_sensors.count()}")

    if not active_sensors.exists():
        print("❌ خطأ: لا توجد حساسات نشطة لتشغيل الاختبار!")
        return

    # -------------------------------------------------------------
    # الجزء الأول: اختبار الحالة الطبيعية (Normal Profile)
    # -------------------------------------------------------------
    print("\n--- [الخطوة 1: اختبار الحالة الطبيعية] ---")
    print("🔄 ضبط ملفات المحاكاة لجميع الحساسات النشطة إلى 'normal'...")
    DataSourceConfig.objects.filter(sensor__is_active=True).update(simulation_profile='normal')

    print("⚙️ تشغيل قراءة الحساسات...")
    read_all_active_sensors()
    
    print("⚙️ تجميع السياق وتشغيل محركات الاستدلال...")
    aggregate_all_contexts()

    print("🔍 فحص الـ Insights المتولدة في الحالة الطبيعية:")
    # جلب أحدث 3 تنبيهات للتأكد من خلو الحالة الطبيعية منها
    normal_insights = Insight.objects.all().order_by('-detected_at')[:3]
    if normal_insights.exists() and any(i.insight_type == Insight.InsightType.CURRENT_ABNORMALITY for i in normal_insights):
        for ins in normal_insights:
            print(f"  - [مريض: {ins.monitored_element}] | النوع: {ins.insight_type} | المصدر: {ins.source}")
    else:
        print("  ✅ لم تظهر أي إنذارات كاذبة (المريض مستقر تماماً وهذا هو السلوك المتوقع).")

    # -------------------------------------------------------------
    # الجزء الثاني: اختبار حالة الطوارئ (Emergency Profile)
    # -------------------------------------------------------------
    print("\n--- [الخطوة 2: اختبار حالة الطوارئ] ---")
    print("🔄 تحويل ملفات المحاكاة لجميع الحساسات النشطة إلى 'emergency_spike'...")
    # تحديث قاعدة البيانات للمحاكاة دفعة واحدة
    DataSourceConfig.objects.filter(sensor__is_active=True).update(simulation_profile='emergency_spike')

    print("⚙️ تشغيل قراءة الحساسات في حالة الطوارئ...")
    read_all_active_sensors()
    
    print("⚙️ تجميع السياق وتشغيل محركات الاستدلال لحالة الطوارئ...")
    aggregate_all_contexts()

    print("🔍 فحص الـ Insights المتولدة في حالة الطوارئ:")
    emergency_insights = Insight.objects.all().order_by('-detected_at')[:5]
    if emergency_insights.exists():
        for ins in emergency_insights:
            print(f"  - 🚨 [مريض: {ins.monitored_element}] | النوع: {ins.insight_type} | الخطورة: {ins.severity} | المصدر: {ins.source} | الثقة: {ins.confidence}")
    else:
        print("  ❌ خطأ: لم يتم إصدار أي إنذار رغم وجود حالة طوارئ!")

    # -------------------------------------------------------------
    # تنظيف وتصفير الإعدادات للوضع الافتراضي
    # -------------------------------------------------------------
    print("\n--- [الخطوة 3: تصفير الإعدادات للعودة للوضع المستقر] ---")
    print("🔄 إعادة ملفات المحاكاة إلى الوضع الافتراضي 'normal'...")
    DataSourceConfig.objects.filter(sensor__is_active=True).update(simulation_profile='normal')
    print("=" * 60)
    print("✅ انتهى الاختبار الشامل بنجاح!")
    print("=" * 60)

# تشغيل الفحص تلقائياً عند الاستيراد
run_test()
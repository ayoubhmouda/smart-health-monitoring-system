import random
import math
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class HealthSimulator:
    """يولد قراءات واقعية للحساسات الفسيولوجية والنشاط والبيئة بناءً على ملفات شخصية (profiles)."""

    PROFILES = {
    'normal': {
        'heart_rate': (70, 80),
        'blood_pressure_systolic': (110, 130),    # بدلاً من blood_pressure_sys
        'blood_pressure_diastolic': (70, 85),     # بدلاً من blood_pressure_dia
        'oxygen_saturation': (95, 100),
        'activity_level': (1, 3),
        'room_temperature': (20, 24),
        'description': 'Patient stable'
    },
    # ... وطبق نفس التعديل على باقي الملفات الشخصية
    'gradual_deterioration': {
        'heart_rate': (70, 115),
        'blood_pressure_systolic': (110, 160),
        'blood_pressure_diastolic': (70, 100),
        'oxygen_saturation': (98, 88),
        'activity_level': (3, 1),
        'room_temperature': (21, 26),
        'description': 'Patient gradually worsening'
    },
    'abnormal': {
        'heart_rate': (45, 55),
        'blood_pressure_systolic': (80, 100),
        'blood_pressure_diastolic': (50, 65),
        'oxygen_saturation': (88, 92),
        'activity_level': (0, 1),
        'room_temperature': (20, 25),
        'description': 'Concerning low vitals'
    },
    'emergency_spike': {
        'heart_rate': (130, 150),
        'blood_pressure_systolic': (170, 200),
        'blood_pressure_diastolic': (100, 120),
        'oxygen_saturation': (80, 85),
        'activity_level': (0, 0),
        'room_temperature': (22, 26),
        'description': 'Dangerous spike'
    },
    'recovery': {
        'heart_rate': (90, 70),
        'blood_pressure_systolic': (150, 120),
        'blood_pressure_diastolic': (95, 78),
        'oxygen_saturation': (88, 96),
        'activity_level': (0, 2),
        'room_temperature': (22, 22),
        'description': 'Recovering'
    },
    'custom': {
        'heart_rate': (70, 70),
        'blood_pressure_systolic': (120, 120),
        'blood_pressure_diastolic': (80, 80),
        'oxygen_saturation': (98, 98),
        'activity_level': (1, 1),
        'room_temperature': (22, 22),
        'description': 'Manual override'
    }
}

    def __init__(self, profile: str = 'normal'):
        self.profile = profile
        self.iteration = 0
        self.start_time = time.time()
        # للتدهور التدريجي نحتاج تتبع التقدم
        self.deterioration_progress = 0.0  # من 0 إلى 1 خلال ساعتين مثلاً

    def set_profile(self, profile: str):
        if profile in self.PROFILES:
            self.profile = profile
            self.iteration = 0
            self.start_time = time.time()
            self.deterioration_progress = 0.0
        else:
            raise ValueError(f"Unknown profile: {profile}")

    def set_custom_values(self, overrides: Dict[str, float]):
        """يضبط القيم اليدوية لملف custom."""
        # سنحفظ القيم المستخدمة في self.custom_overrides
        self.custom_overrides = overrides

    def _interpolate(self, low, high, progress):
        """استيفاء خطي بين قيمتين بناءً على progress من 0 إلى 1."""
        return low + (high - low) * progress

    def generate_reading(self, sensor_type: str) -> float:
        """يولد قراءة واحدة لنوع حساس معين بناءً على الملف الشخصي الحالي."""
        profile_config = self.PROFILES[self.profile]
        
        # إذا كان الملف custom، نأخذ القيم من التجاوزات اليدوية إن وجدت
        if self.profile == 'custom' and hasattr(self, 'custom_overrides'):
            # نبحث عن القيمة المطلوبة في overrides
            value = self.custom_overrides.get(sensor_type)
            if value is not None:
                # نضيف قليل من الضوضاء العشوائية لمحاكاة الواقع
                return value + random.uniform(-0.5, 0.5)
            # إذا لم نجد، نرجع قيمة افتراضية
            return 0.0

        # باقي الملفات الشخصية تعتمد على النطاقات
        low, high = profile_config.get(sensor_type, (0, 0))
        
        # التدهور التدريجي: نزيد التقدم مع الزمن
        if self.profile == 'gradual_deterioration':
            elapsed_seconds = time.time() - self.start_time
            # نصل إلى 100% بعد ساعتين (7200 ثانية)
            progress = min(1.0, elapsed_seconds / 7200.0)
            self.deterioration_progress = progress
            # عكس الاتجاه للأكسجين والنشاط (مرتفع -> منخفض)
            if sensor_type in ('oxygen_saturation', 'activity_level'):
                # نعكس: high -> low
                value = self._interpolate(high, low, progress)
            else:
                value = self._interpolate(low, high, progress)
            # إضافة ضوضاء عشوائية طفيفة
            noise = random.uniform(-1.5, 1.5) if sensor_type != 'activity_level' else 0
            return round(value + noise, 1)

        # للملفات الأخرى: قيمة عشوائية ضمن النطاق
        if sensor_type == 'activity_level':
            # النشاط نعطيه قيماً صحيحة (0,1,2,3) بناءً على النطاق
            return float(random.randint(int(low), int(high)))
        
        # مع تقلب عشوائي بسيط
        base = random.uniform(low, high)
        noise = random.uniform(-1.0, 1.0)
        return round(base + noise, 1)

# للتجربة السريعة
if __name__ == "__main__":
    sim = HealthSimulator(profile='normal')
    print("Normal HR:", sim.generate_reading('heart_rate'))
    sim.set_profile('gradual_deterioration')
    for i in range(5):
        print(f"Deterioration step {i+1}: HR={sim.generate_reading('heart_rate')}, O2={sim.generate_reading('oxygen_saturation')}")
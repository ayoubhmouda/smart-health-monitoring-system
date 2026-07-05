import random
import math
from datetime import datetime, timedelta

class ClinicalScenarioGenerator:
    """يولد سيناريوهات سريرية تركيبية مع تسميات (خطر/طبيعي)."""

    def __init__(self):
        self.base_time = datetime(2026, 1, 1, 12, 0, 0)

    def _generate_normal_context(self, timestamp):
        """قراءات طبيعية تماماً."""
        return {
            'timestamp': timestamp,
            'heart_rate': random.uniform(70, 80),
            'blood_pressure_systolic': random.uniform(110, 130),
            'blood_pressure_diastolic': random.uniform(70, 85),
            'oxygen_saturation': random.uniform(95, 100),
            'activity_level': random.randint(1, 3),
            'room_temperature': random.uniform(20, 24)
        }

    def generate_stable_scenario(self, hours=6, interval_minutes=5):
        """مريض مستقر لمدة ساعات. التسمية = 0 (لا خطر)."""
        data = []
        current_time = self.base_time
        for _ in range(int(hours * 60 / interval_minutes)):
            ctx = self._generate_normal_context(current_time)
            data.append((ctx, 0))  # 0 يعني طبيعي
            current_time += timedelta(minutes=interval_minutes)
        return data

    def generate_deterioration_scenario(self, hours=6, interval_minutes=5):
        """مريض يتدهور تدريجياً (معدل القلب يرتفع، الأكسجين ينخفض). التسمية = 1 (خطر) في النهاية."""
        data = []
        current_time = self.base_time
        total_steps = int(hours * 60 / interval_minutes)

        for step in range(total_steps):
            progress = step / total_steps  # من 0 إلى 1

            heart_rate = 75 + 40 * progress + random.uniform(-2, 2)
            bp_sys = 120 + 40 * progress + random.uniform(-3, 3)
            bp_dia = 80 + 20 * progress + random.uniform(-2, 2)
            oxygen = 98 - 10 * progress + random.uniform(-1, 1)
            activity = max(0, int(2 - 2 * progress + random.uniform(-0.5, 0.5)))
            temp = 22 + 2 * progress + random.uniform(-0.5, 0.5)

            ctx = {
                'timestamp': current_time,
                'heart_rate': heart_rate,
                'blood_pressure_systolic': bp_sys,
                'blood_pressure_diastolic': bp_dia,
                'oxygen_saturation': oxygen,
                'activity_level': activity,
                'room_temperature': temp
            }

            # نعتبر آخر 20% من السيناريو "خطر" (1)
            label = 1 if progress > 0.8 else 0
            data.append((ctx, label))
            current_time += timedelta(minutes=interval_minutes)

        return data

    def generate_emergency_spike_scenario(self, hours=2, interval_minutes=5):
        """مريض مستقر تماماً، ثم فجأة يحدث ارتفاع خطير في النصف الثاني. التسمية = 1 بعد الحدث."""
        data = []
        current_time = self.base_time
        total_steps = int(hours * 60 / interval_minutes)
        spike_start = int(total_steps * 0.6)  # يبدأ الخطر بعد 60% من الوقت

        for step in range(total_steps):
            if step < spike_start:
                # مستقر
                ctx = self._generate_normal_context(current_time)
                label = 0
            else:
                # حالة طارئة
                ctx = {
                    'timestamp': current_time,
                    'heart_rate': random.uniform(130, 150),
                    'blood_pressure_systolic': random.uniform(170, 200),
                    'blood_pressure_diastolic': random.uniform(100, 120),
                    'oxygen_saturation': random.uniform(80, 85),
                    'activity_level': 0,
                    'room_temperature': random.uniform(22, 26)
                }
                label = 1

            data.append((ctx, label))
            current_time += timedelta(minutes=interval_minutes)

        return data

    def generate_mixed_scenarios(self, num_each=50):
        """يولد قائمة من السيناريوهات للتدريب."""
        scenarios = []
        for _ in range(num_each):
            scenarios.append(self.generate_stable_scenario(hours=1, interval_minutes=5))
            scenarios.append(self.generate_deterioration_scenario(hours=2, interval_minutes=5))
            scenarios.append(self.generate_emergency_spike_scenario(hours=1, interval_minutes=5))
        return scenarios
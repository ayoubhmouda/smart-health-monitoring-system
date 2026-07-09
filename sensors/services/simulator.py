import random
import math
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class HealthSimulator:
    """يولد قراءات واقعية للحساسات الفسيولوجية والنشاط والبيئة بناءً على ملفات شخصية متناسقة طبياً."""

    PROFILES = {
        'normal': {
            'heart_rate': (60, 100),
            'blood_pressure_systolic': (110, 130),
            'blood_pressure_diastolic': (70, 85),
            'oxygen_saturation': (95, 100),
            'body_temperature': (36.1, 37.2),
            'activity_level': (0, 3),
            'room_temperature': (20, 24),
            'description': 'Patient stable'
        },
        'gradual_deterioration': {
            'heart_rate': (70, 115),
            'blood_pressure_systolic': (110, 160),
            'blood_pressure_diastolic': (70, 100),
            'oxygen_saturation': (98, 88),
            'body_temperature': (37.0, 39.5),
            'activity_level': (3, 0),
            'room_temperature': (21, 26),
            'description': 'Patient gradually worsening'
        },
        'abnormal': {
            'heart_rate': (45, 55),
            'blood_pressure_systolic': (80, 100),
            'blood_pressure_diastolic': (50, 65),
            'oxygen_saturation': (88, 92),
            'body_temperature': (35.0, 36.0),
            'activity_level': (0, 1),
            'room_temperature': (20, 25),
            'description': 'Concerning low vitals'
        },
        'emergency_spike': {
            'heart_rate': (130, 150),
            'blood_pressure_systolic': (170, 200),
            'blood_pressure_diastolic': (100, 120),
            'oxygen_saturation': (80, 85),
            'body_temperature': (39.0, 41.0),
            'activity_level': (0, 0),
            'room_temperature': (22, 26),
            'description': 'Dangerous spike'
        },
        'recovery': {
            'heart_rate': (90, 70),
            'blood_pressure_systolic': (150, 120),
            'blood_pressure_diastolic': (95, 78),
            'oxygen_saturation': (88, 96),
            'body_temperature': (38.5, 37.0),
            'activity_level': (0, 2),
            'room_temperature': (22, 22),
            'description': 'Recovering'
        },
        'custom': {
            'heart_rate': (70, 70),
            'blood_pressure_systolic': (120, 120),
            'blood_pressure_diastolic': (80, 80),
            'oxygen_saturation': (98, 98),
            'body_temperature': (37.0, 37.0),
            'activity_level': (1, 1),
            'room_temperature': (22, 22),
            'description': 'Manual override'
        }
    }

    def __init__(self, profile: str = 'normal'):
        self.profile = profile
        self.iteration = 0
        self.start_time = time.time()
        self.deterioration_progress = 0.0
        self._cached_batch = {}
        self._unfetched_sensors = set()

    def set_profile(self, profile: str):
        if profile in self.PROFILES:
            self.profile = profile
            self.iteration = 0
            self.start_time = time.time()
            self.deterioration_progress = 0.0
            self._cached_batch = {}
            self._unfetched_sensors = set()
        else:
            raise ValueError(f"Unknown profile: {profile}")

    def set_custom_values(self, overrides: Dict[str, float]):
        self.custom_overrides = overrides
        self._cached_batch = {}

    def _interpolate(self, low, high, progress):
        return low + (high - low) * progress

    def _generate_coherent_batch(self) -> Dict[str, float]:
        """تولد حزمة قراءات متناسقة فسيولوجياً للحظة الحالية كاملة."""
        profile_config = self.PROFILES[self.profile]
        base_vals = {}

        # 1. معالجة الملف الشخصي اليدوي (Custom)
        if self.profile == 'custom' and hasattr(self, 'custom_overrides'):
            for s_type in profile_config.keys():
                if s_type == 'description':
                    continue
                val = self.custom_overrides.get(s_type, 0.0)
                base_vals[s_type] = val + random.uniform(-0.5, 0.5)
            base_vals['activity_level'] = float(int(self.custom_overrides.get('activity_level', 1.0)))
            return base_vals

        # 2. حساب التقدم للتدهور التدريجي
        progress = 0.0
        if self.profile == 'gradual_deterioration':
            elapsed_seconds = time.time() - self.start_time
            progress = min(1.0, elapsed_seconds / 7200.0)
            self.deterioration_progress = progress

        # 3. توليد القيم الأساسية (مع تخطي 'description' لتجنب ValueError)
        for s_type, val in profile_config.items():
            if s_type == 'description':
                continue
            low, high = val

            if self.profile == 'gradual_deterioration':
                if s_type in ('oxygen_saturation', 'activity_level'):
                    base_vals[s_type] = self._interpolate(high, low, progress)
                else:
                    base_vals[s_type] = self._interpolate(low, high, progress)
            else:
                if s_type == 'activity_level':
                    base_vals[s_type] = float(random.randint(int(low), int(high)))
                else:
                    base_vals[s_type] = random.uniform(low, high)

        # 4. محرك القوانين الفسيولوجية (ربط النشاط بالعلامات الحيوية في الحالة الطبيعية)
        if self.profile == 'normal':
            activity = float(int(base_vals['activity_level']))

            if activity == 3.0:      # جري
                base_vals['heart_rate'] = random.uniform(135.0, 155.0)
                base_vals['blood_pressure_systolic'] = random.uniform(140.0, 155.0)
                base_vals['blood_pressure_diastolic'] = random.uniform(85.0, 95.0)
            elif activity == 2.0:    # مشي سريع
                base_vals['heart_rate'] = random.uniform(95.0, 120.0)
                base_vals['blood_pressure_systolic'] = random.uniform(122.0, 132.0)
                base_vals['blood_pressure_diastolic'] = random.uniform(80.0, 84.0)
            elif activity == 1.0:    # حركة خفيفة
                base_vals['heart_rate'] = random.uniform(75.0, 90.0)
                base_vals['blood_pressure_systolic'] = random.uniform(115.0, 121.0)
                base_vals['blood_pressure_diastolic'] = random.uniform(75.0, 79.0)
            else:                    # راحة تامة
                base_vals['heart_rate'] = random.uniform(60.0, 73.0)
                base_vals['blood_pressure_systolic'] = random.uniform(110.0, 114.0)
                base_vals['blood_pressure_diastolic'] = random.uniform(70.0, 74.0)

        # 5. الضوضاء والتقريب
        final_batch = {}
        for s_type, val in base_vals.items():
            if s_type == 'activity_level':
                final_batch[s_type] = float(int(val))
            else:
                noise = random.uniform(-1.0, 1.0) if self.profile != 'gradual_deterioration' else random.uniform(-1.5, 1.5)
                if s_type == 'room_temperature':
                    noise = 0
                res = round(val + noise, 1)
                if s_type == 'oxygen_saturation':
                    res = min(100.0, res)
                final_batch[s_type] = res

        return final_batch

    def generate_reading(self, sensor_type: str) -> float:
        if sensor_type not in self._unfetched_sensors or not self._cached_batch:
            self._cached_batch = self._generate_coherent_batch()
            self._unfetched_sensors = set(self._cached_batch.keys())
            self.iteration += 1

        self._unfetched_sensors.discard(sensor_type)
        return self._cached_batch.get(sensor_type, 0.0)
import random
import math
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class HealthSimulator:
    """يولد قراءات واقعية متناسقة طبياً تعتمد على السير العشوائي المتدرج (Random Walk) مع كاش لحفظ الحالة."""

    MAX_STEPS = {
        'heart_rate': 1.5,
        'blood_pressure_systolic': 2.0,
        'blood_pressure_diastolic': 1.0,
        'oxygen_saturation': 0.3,
        'body_temperature': 0.05,
        'room_temperature': 0.1,
        'blood_glucose': 2.0,
        'respiratory_rate': 0.5
    }

    PROFILES = {
        'normal': {
            'heart_rate': (60, 100),
            'blood_pressure_systolic': (110, 130),
            'blood_pressure_diastolic': (70, 85),
            'oxygen_saturation': (95, 100),
            'body_temperature': (36.1, 37.2),
            'activity_level': (0, 3),
            'room_temperature': (20, 24),
            'blood_glucose': (80, 120),
            'respiratory_rate': (14, 18),
            'description': 'Patient stable'
        },
        'gradual_deterioration': {
            'heart_rate': (70, 115),
            'blood_pressure_systolic': (110, 160),
            'blood_pressure_diastolic': (70, 100),
            'oxygen_saturation': (88, 98),
            'body_temperature': (37.0, 39.5),
            'activity_level': (0, 3),
            'room_temperature': (21, 26),
            'blood_glucose': (90, 200),
            'respiratory_rate': (16, 28),
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
            'blood_glucose': (50, 65),
            'respiratory_rate': (8, 11),
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
            'blood_glucose': (250, 400),
            'respiratory_rate': (30, 45),
            'description': 'Dangerous spike'
        },
        'recovery': {
            'heart_rate': (70, 90),
            'blood_pressure_systolic': (120, 150),
            'blood_pressure_diastolic': (78, 95),
            'oxygen_saturation': (88, 96),
            'body_temperature': (37.0, 38.5),
            'activity_level': (0, 2),
            'room_temperature': (22, 22),
            'blood_glucose': (95, 180),
            'respiratory_rate': (16, 26),
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
            'blood_glucose': (100, 100),
            'respiratory_rate': (16, 16),
            'description': 'Manual override'
        }
    }

    def __init__(self, profile: str = 'normal', patient_id: Optional[int] = None, start_time: Optional[float] = None):
        self.patient_id = patient_id
        self.cache_key = f"sim_state_patient_{patient_id}" if patient_id else None
        
        cached_state = None
        if self.cache_key:
            try:
                from django.core.cache import cache
                cached_state = cache.get(self.cache_key)
            except Exception:
                pass

        if cached_state:
            self.profile = cached_state.get('profile', profile)
            self.iteration = cached_state.get('iteration', 0)
            self.start_time = start_time if start_time is not None else cached_state.get('start_time', time.time())
            self.deterioration_progress = cached_state.get('deterioration_progress', 0.0)
            self._cached_batch = cached_state.get('cached_batch', {})
            self._unfetched_sensors = set(cached_state.get('unfetched_sensors', []))
            self.last_readings = cached_state.get('last_readings', {})
        else:
            self.profile = profile
            self.iteration = 0
            self.start_time = start_time if start_time is not None else time.time()
            self.deterioration_progress = 0.0
            self._cached_batch = {}
            self._unfetched_sensors = set()
            self.last_readings = {}

    def _save_state_to_cache(self):
        if not self.cache_key:
            return
        try:
            from django.core.cache import cache
            state = {
                'profile': self.profile,
                'iteration': self.iteration,
                'start_time': self.start_time,
                'deterioration_progress': self.deterioration_progress,
                'cached_batch': self._cached_batch,
                'unfetched_sensors': list(self._unfetched_sensors),
                'last_readings': self.last_readings
            }
            cache.set(self.cache_key, state, timeout=7200)
        except Exception:
            pass

    def set_profile(self, profile: str, start_time: Optional[float] = None):
        if profile not in self.PROFILES:
            raise ValueError(f"Unknown profile: {profile}")

        if self.profile == profile and self._cached_batch:
            return
            
        self.profile = profile
        self.iteration = 0
        # 🟢 تثبيت وقت البداية القادم من قاعدة البيانات لمنع تصفير التدهور التدريجي عند الانتقال بين الحساسات
        self.start_time = start_time if start_time is not None else time.time()
        self.deterioration_progress = 0.0
        self._cached_batch = {}
        self._unfetched_sensors = set()
        self.last_readings = {}
        self._save_state_to_cache()

    def _interpolate(self, low, high, progress):
        return low + (high - low) * progress

    def _generate_coherent_batch(self) -> Dict[str, float]:
        profile_config = self.PROFILES[self.profile]
        base_vals = {}

        if self.profile == 'custom' and hasattr(self, 'custom_overrides'):
            for s_type in profile_config.keys():
                if s_type == 'description': continue
                val = self.custom_overrides.get(s_type, 0.0)
                base_vals[s_type] = val + random.uniform(-0.5, 0.5)
            base_vals['activity_level'] = float(int(self.custom_overrides.get('activity_level', 1.0)))
            self.last_readings = base_vals.copy()
            return base_vals

        progress = 0.0
        if self.profile == 'gradual_deterioration':
            elapsed_seconds = time.time() - self.start_time
            progress = min(1.0, elapsed_seconds / 300.0)
            self.deterioration_progress = progress

        current_bounds = {}
        for s_type, val in profile_config.items():
            if s_type == 'description': continue
            low, high = val

            if self.profile == 'gradual_deterioration':
                if s_type in ('oxygen_saturation', 'activity_level'):
                    current_bounds[s_type] = (high, low)
                else:
                    current_bounds[s_type] = (low, high)
            else:
                current_bounds[s_type] = (low, high)

        for s_type, bounds in current_bounds.items():
            if s_type == 'activity_level':
                low, high = bounds
                if self.profile == 'gradual_deterioration':
                    base_vals[s_type] = float(round(self._interpolate(low, high, progress)))
                else:
                    base_vals[s_type] = float(random.randint(int(low), int(high)))
                continue

            low, high = bounds
            if self.profile == 'gradual_deterioration':
                target_val = self._interpolate(low, high, progress)
            else:
                target_val = (low + high) / 2.0

            if s_type in self.last_readings:
                prev_val = self.last_readings[s_type]
                step_limit = self.MAX_STEPS[s_type]
                step = random.uniform(-step_limit, step_limit)
                
                drift = 0.05 * (target_val - prev_val)
                new_val = prev_val + step + drift
            else:
                # 🟢 الحساب المباشر والدقيق بناءً على الوقت المنقضي في حال فقدان الكاش المؤقت
                new_val = target_val if self.profile == 'gradual_deterioration' else random.uniform(low, high)

            min_val, max_val = min(low, high), max(low, high)
            base_vals[s_type] = max(min_val, min(max_val, new_val))

        if self.profile == 'normal':
            activity = float(int(base_vals['activity_level']))
            if activity == 3.0:
                # تكسير الجدار الثابت للنبض والضغط والتنفس عند أعلى مستوى نشاط لجعل القيم فريدة لكل مريض
                hr_floor = 135.0 + random.uniform(-2.0, 2.0)
                base_vals['heart_rate'] = max(hr_floor, min(155.0, base_vals['heart_rate'] + random.uniform(2, 5)))
                
                bps_floor = 140.0 + random.uniform(-3.0, 3.0)
                base_vals['blood_pressure_systolic'] = max(bps_floor, min(155.0, base_vals['blood_pressure_systolic'] + random.uniform(3, 6)))
                
                rr_floor = 22.0 + random.uniform(-0.8, 0.8)
                base_vals['respiratory_rate'] = max(rr_floor, min(28.0, base_vals['respiratory_rate'] + random.uniform(1.5, 3.0)))
            elif activity == 0.0:
                # تكسير السقف الثابت للمؤشرات عند الراحة التامة لنفس السبب الواقعي
                hr_ceil = 73.0 + random.uniform(-1.5, 1.5)
                base_vals['heart_rate'] = max(60.0, min(hr_ceil, base_vals['heart_rate'] - random.uniform(1, 3)))
                
                bps_ceil = 114.0 + random.uniform(-2.0, 2.0)
                base_vals['blood_pressure_systolic'] = max(110.0, min(bps_ceil, base_vals['blood_pressure_systolic'] - random.uniform(1, 3)))
                
                rr_ceil = 14.0 + random.uniform(-0.5, 0.5)
                base_vals['respiratory_rate'] = max(12.0, min(rr_ceil, base_vals['respiratory_rate'] - random.uniform(0.5, 1.5)))

        final_batch = {}
        for s_type, val in base_vals.items():
            if s_type == 'activity_level':
                final_batch[s_type] = float(int(val))
            else:
                res = round(val, 1)
                if s_type == 'oxygen_saturation': 
                    res = min(100.0, res)
                final_batch[s_type] = res

        self.last_readings = final_batch.copy()
        return final_batch

    def generate_reading(self, sensor_type: str) -> float:
        if sensor_type not in self._unfetched_sensors or not self._cached_batch:
            self._cached_batch = self._generate_coherent_batch()
            self._unfetched_sensors = set(self._cached_batch.keys())
            self.iteration += 1

        self._unfetched_sensors.discard(sensor_type)
        val = self._cached_batch.get(sensor_type, 0.0)
        
        self._save_state_to_cache()
        return val
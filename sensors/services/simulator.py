# sensors/services/simulator.py
import random
import math
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from django.utils import timezone
from django.core.cache import cache


class HealthSimulator:
    """
    يولد قراءات واقعية متناسقة طبياً تعتمد على السير العشوائي المتدرج (Random Walk).
    - يدعم الترابط الفسيولوجي الذكي الواعي بالسياق الحركي للحساسات في الوضع الطبيعي فقط.
    - السيناريوهات المخصصة تظل مستقلة تماماً ولا تتأثر بالنشاط الحركي.
    - تحديث فوري ومتزامن لكافة الحساسات عند تغيير النشاط دون أي تأخير.
    """

    MAX_STEPS = {
        'heart_rate': 4.0,
        'blood_pressure_systolic': 5.0,
        'blood_pressure_diastolic': 3.0,
        'oxygen_saturation': 1.0,
        'body_temperature': 0.25,
        'room_temperature': 0.1,
        'blood_glucose': 5.0,
        'respiratory_rate': 1.5
    }

    PROFILES = {
        # 1. السيناريوهات الطبية السريرية المخصصة
        'normal': {
            'heart_rate': (60, 100),
            'blood_pressure_systolic': (110, 130),
            'blood_pressure_diastolic': (70, 85),
            'oxygen_saturation': (95, 100),
            'body_temperature': (36.1, 37.2),
            'activity_level': (0, 1),
            'room_temperature': (20, 24),
            'blood_glucose': (80, 120),
            'respiratory_rate': (14, 18),
            'description': 'Patient stable'
        },
        'gradual_deterioration': {
            'heart_rate': (80, 135),
            'blood_pressure_systolic': (120, 175),
            'blood_pressure_diastolic': (80, 105),
            'oxygen_saturation': (98, 86),
            'body_temperature': (36.5, 39.5),
            'activity_level': (1, 0),
            'room_temperature': (22, 22),
            'blood_glucose': (90, 250),
            'respiratory_rate': (16, 32),
            'description': 'Patient gradually worsening over 10 minutes'
        },
        'gradual_recovery': {
            'heart_rate': (135, 75),
            'blood_pressure_systolic': (175, 120),
            'blood_pressure_diastolic': (105, 80),
            'oxygen_saturation': (86, 97),
            'body_temperature': (39.5, 36.8),
            'activity_level': (0, 1),
            'room_temperature': (22, 22),
            'blood_glucose': (250, 100),
            'respiratory_rate': (32, 16),
            'description': 'Patient gradually recovering over 10 minutes'
        },
        'sudden_high': {
            'heart_rate': (130, 150),
            'blood_pressure_systolic': (170, 200),
            'blood_pressure_diastolic': (100, 120),
            'oxygen_saturation': (80, 85),
            'body_temperature': (39.0, 41.0),
            'activity_level': (0, 0),
            'room_temperature': (22, 26),
            'blood_glucose': (250, 400),
            'respiratory_rate': (30, 45),
            'description': 'Sudden acute high vitals'
        },
        'sudden_low': {
            'heart_rate': (45, 55),
            'blood_pressure_systolic': (80, 100),
            'blood_pressure_diastolic': (50, 65),
            'oxygen_saturation': (88, 92),
            'body_temperature': (35.0, 36.0),
            'activity_level': (0, 1),
            'room_temperature': (20, 25),
            'blood_glucose': (50, 65),
            'respiratory_rate': (8, 11),
            'description': 'Sudden acute low vitals'
        },

        # 2. سيناريوهات مستويات النشاط الحركي
        'activity_resting': {
            'heart_rate': (58, 68),
            'blood_pressure_systolic': (105, 115),
            'blood_pressure_diastolic': (65, 75),
            'oxygen_saturation': (97, 100),
            'body_temperature': (36.2, 36.8),
            'activity_level': (0, 0),
            'room_temperature': (21, 23),
            'blood_glucose': (80, 100),
            'respiratory_rate': (12, 15),
            'description': 'Activity Level 0: Resting / Sleeping'
        },
        'activity_sitting': {
            'heart_rate': (68, 82),
            'blood_pressure_systolic': (112, 124),
            'blood_pressure_diastolic': (72, 82),
            'oxygen_saturation': (96, 99),
            'body_temperature': (36.5, 37.0),
            'activity_level': (1, 1),
            'room_temperature': (21, 23),
            'blood_glucose': (85, 110),
            'respiratory_rate': (14, 17),
            'description': 'Activity Level 1: Sitting / Deskwork'
        },
        'activity_walking': {
            'heart_rate': (88, 108),
            'blood_pressure_systolic': (122, 138),
            'blood_pressure_diastolic': (78, 88),
            'oxygen_saturation': (95, 98),
            'body_temperature': (36.8, 37.4),
            'activity_level': (2, 2),
            'room_temperature': (21, 23),
            'blood_glucose': (90, 120),
            'respiratory_rate': (18, 23),
            'description': 'Activity Level 2: Walking'
        },
        'activity_running': {
            'heart_rate': (125, 155),
            'blood_pressure_systolic': (142, 165),
            'blood_pressure_diastolic': (82, 92),
            'oxygen_saturation': (94, 97),
            'body_temperature': (37.2, 38.1),
            'activity_level': (3, 3),
            'room_temperature': (21, 23),
            'blood_glucose': (95, 135),
            'respiratory_rate': (24, 32),
            'description': 'Activity Level 3: Running'
        }
    }

    def __init__(self, profile: str = 'normal', patient_id: Optional[int] = None, start_time: Optional[float] = None):
        if profile not in self.PROFILES:
            profile = 'normal'

        self.patient_id = patient_id
        self.cache_key = f"sim_state_patient_{patient_id}_{profile}" if patient_id else None
        
        # استخراج النشاط الحركي الحالي للمريض
        current_activity = self._get_current_activity_profile() if profile == 'normal' else None

        cached_state = None
        if self.cache_key:
            try:
                cached_state = cache.get(self.cache_key)
            except Exception:
                pass

        # 🟢 التحقق من تطابق البروفايل وكذلك تطابق النشاط الحركي لمنع استخدام كاش قديم عند تغيير النشاط
        is_same_activity = (profile != 'normal') or (cached_state and cached_state.get('active_activity') == current_activity)

        if cached_state and cached_state.get('profile') == profile and is_same_activity:
            self.profile = cached_state.get('profile', profile)
            self.active_activity = current_activity
            self.iteration = cached_state.get('iteration', 0)
            self.start_time = start_time if start_time is not None else cached_state.get('start_time', timezone.now().timestamp())
            self.deterioration_progress = cached_state.get('deterioration_progress', 0.0)
            self._cached_batch = cached_state.get('cached_batch', {})
            self._unfetched_sensors = set(cached_state.get('unfetched_sensors', []))
            self.last_readings = cached_state.get('last_readings', {})
        else:
            # إعادة تعيين الكاش وبناء حزمة جديدة فوراً إذا تغير النشاط أو البروفايل
            self.profile = profile
            self.active_activity = current_activity
            self.iteration = 0
            self.start_time = start_time if start_time is not None else timezone.now().timestamp()
            self.deterioration_progress = 0.0
            self._cached_batch = {}
            self._unfetched_sensors = set()
            self.last_readings = cached_state.get('last_readings', {}) if cached_state else {}
            self._save_state_to_cache()

    def _save_state_to_cache(self):
        if not self.cache_key:
            return
        try:
            state = {
                'profile': self.profile,
                'active_activity': getattr(self, 'active_activity', None),
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
            profile = 'normal'

        if self.profile == profile and self._cached_batch:
            return
            
        self.profile = profile
        self.active_activity = self._get_current_activity_profile() if profile == 'normal' else None
        self.iteration = 0
        self.start_time = start_time if start_time is not None else timezone.now().timestamp()
        self.deterioration_progress = 0.0
        self._cached_batch = {}
        self._unfetched_sensors = set()
        self.last_readings = {}
        self._save_state_to_cache()

    def _interpolate(self, low, high, progress):
        return low + (high - low) * progress

    def _get_current_activity_profile(self) -> str:
        if not self.patient_id:
            return 'normal'
        try:
            from sensors.models import DataSourceConfig
            cfg = DataSourceConfig.objects.filter(
                sensor__monitored_element_id=self.patient_id,
                sensor__sensor_type__name='Activity Level'
            ).first()
            if cfg:
                return cfg.simulation_profile
        except Exception:
            pass
        return 'normal'

    def _generate_coherent_batch(self) -> Dict[str, float]:
        current_profile = self.profile

        # 🟢 النشاط يتحكم بالحساسات فقط وفقط عندما يكون الحساس في الوضع الطبيعي
        if current_profile == 'normal':
            activity_profile = self._get_current_activity_profile()
            if activity_profile in ['activity_resting', 'activity_sitting', 'activity_walking', 'activity_running']:
                current_profile = activity_profile

        profile_config = self.PROFILES[current_profile]
        base_vals = {}

        progress = 0.0
        if current_profile in ['gradual_deterioration', 'gradual_recovery']:
            elapsed_seconds = timezone.now().timestamp() - self.start_time
            progress = min(1.0, elapsed_seconds / 600.0)
            self.deterioration_progress = progress

        current_bounds = {}
        for s_type, val in profile_config.items():
            if s_type == 'description': 
                continue
            low, high = val
            current_bounds[s_type] = (low, high)

        # حماية الأكسجين عند تغيير النشاط في الوضع الطبيعي
        if self.profile == 'normal' and current_profile.startswith('activity_'):
            current_bounds['oxygen_saturation'] = self.PROFILES['normal']['oxygen_saturation']

        for s_type, bounds in current_bounds.items():
            low, high = bounds
            
            # معالجة المستوى الحركي للنشاط
            if s_type == 'activity_level':
                if current_profile in ['gradual_deterioration', 'gradual_recovery']:
                    base_vals[s_type] = float(round(self._interpolate(low, high, progress)))
                else:
                    base_vals[s_type] = float(random.randint(int(min(low, high)), int(max(low, high))))
                continue

            # معالجة الحساسات الفسيولوجية
            if current_profile in ['gradual_deterioration', 'gradual_recovery']:
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
                new_val = target_val if current_profile in ['gradual_deterioration', 'gradual_recovery'] else random.uniform(low, high)

            min_val, max_val = min(low, high), max(low, high)
            base_vals[s_type] = max(min_val, min(max_val, new_val))

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
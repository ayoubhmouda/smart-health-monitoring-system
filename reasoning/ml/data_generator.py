import random
from datetime import datetime, timedelta


class ClinicalScenarioGenerator:
    """يولد سيناريوهات سريرية تركيبية مع تسميات (خطر/طبيعي) ومعلومات طبية شاملة."""

    def __init__(self):
        self.base_time = datetime(2026, 1, 1, 12, 0, 0)

    # ------------------------------------------------------------------
    # حساب نقاط الخطر — القلب الجوهري للتمييز بين المرضى
    # ------------------------------------------------------------------
    def _calculate_risk_score(self, ctx, chronic_conditions=None, lifestyle=None):
        """
        يحسب نقاط الخطر بضرب شدة الـ vitals في معامل الخطورة الشخصي.
        هذا يضمن أن نفس الـ vitals المعتدلة تُصنَّف خطراً للمريض عالي الخطورة
        لكن آمنة للشخص الصحيح.
        """
        if chronic_conditions is None:
            chronic_conditions = []
        if lifestyle is None:
            lifestyle = {}

        # --- نقاط الـ vitals ---
        vitals_score = 0.0

        hr = ctx.get('heart_rate', 75)
        if hr > 120:
            vitals_score += 0.35
        elif hr > 100:
            vitals_score += 0.15

        bp = ctx.get('blood_pressure_systolic', 120)
        if bp > 170:
            vitals_score += 0.35
        elif bp > 140:
            vitals_score += 0.15

        o2 = ctx.get('oxygen_saturation', 98)
        if o2 < 90:
            vitals_score += 0.35
        elif o2 < 94:
            vitals_score += 0.15

        temp = ctx.get('body_temperature', 37.0)
        if temp > 39.0:
            vitals_score += 0.20
        elif temp > 38.0:
            vitals_score += 0.10

        activity = ctx.get('activity_level', 2)
        if activity == 0:
            vitals_score += 0.10

        # --- معامل الخطر الشخصي ---
        personal_multiplier = 1.0

        age = ctx.get('age', 50)
        if age > 70:
            personal_multiplier += 0.5
        elif age > 55:
            personal_multiplier += 0.3
        elif age > 40:
            personal_multiplier += 0.1

        if 'hypertension' in chronic_conditions:
            personal_multiplier += 0.4
        if 'diabetes' in chronic_conditions:
            personal_multiplier += 0.3
        if 'heart_disease' in chronic_conditions:
            personal_multiplier += 0.5

        smoking = lifestyle.get('smoking', 'never')
        if isinstance(smoking, str):
            smoking = smoking.lower()
        if smoking == 'current':
            personal_multiplier += 0.3
        elif smoking == 'former':
            personal_multiplier += 0.1

        bmi = lifestyle.get('bmi', 22)
        if bmi > 35:
            personal_multiplier += 0.3
        elif bmi > 30:
            personal_multiplier += 0.2
        elif bmi > 25:
            personal_multiplier += 0.1

        return vitals_score * personal_multiplier

    # ------------------------------------------------------------------
    # بناء سياق بقراءات طبيعية
    # ------------------------------------------------------------------
    def _generate_normal_context(self, timestamp, age=50, gender='M',
                                 chronic_conditions=None, lifestyle=None):
        if chronic_conditions is None:
            chronic_conditions = []
        if lifestyle is None:
            lifestyle = {}

        return {
            'timestamp': timestamp,
            'heart_rate': random.uniform(70, 80),
            'blood_pressure_systolic': random.uniform(110, 130),
            'blood_pressure_diastolic': random.uniform(70, 85),
            'oxygen_saturation': random.uniform(95, 100),
            'body_temperature': random.uniform(36.1, 37.2),
            'activity_level': random.randint(1, 3),
            'room_temperature': random.uniform(20, 24),
            'age': age,
            'gender': 1 if gender == 'M' else 0,
            'has_hypertension': 1 if 'hypertension' in chronic_conditions else 0,
            'has_diabetes':     1 if 'diabetes' in chronic_conditions else 0,
            'has_heart_disease':1 if 'heart_disease' in chronic_conditions else 0,
            'smoking_status': self._smoking_code(lifestyle),
            'bmi': lifestyle.get('bmi', 25),
        }

    def _smoking_code(self, lifestyle):
        s = lifestyle.get('smoking', 'never')
        if isinstance(s, str):
            s = s.lower()
        if s == 'current':
            return 2
        if s == 'former':
            return 1
        return 0

    def _make_ctx(self, timestamp, vitals, age, gender, chronic_conditions, lifestyle):
        """بناء سياق من قيم vitals مباشرة + بيانات المريض."""
        return {
            'timestamp': timestamp,
            **vitals,
            'age': age,
            'gender': 1 if gender == 'M' else 0,
            'has_hypertension': 1 if 'hypertension' in chronic_conditions else 0,
            'has_diabetes':     1 if 'diabetes' in chronic_conditions else 0,
            'has_heart_disease':1 if 'heart_disease' in chronic_conditions else 0,
            'smoking_status': self._smoking_code(lifestyle),
            'bmi': lifestyle.get('bmi', 25),
        }

    # ------------------------------------------------------------------
    # سيناريو 1: مريض مستقر
    # ------------------------------------------------------------------
    def generate_stable_scenario(self, hours=6, interval_minutes=5,
                                 age=50, gender='M', chronic_conditions=None,
                                 lifestyle=None, medications=None, family_history=None):
        if chronic_conditions is None:
            chronic_conditions = []
        if lifestyle is None:
            lifestyle = {}

        data = []
        current_time = self.base_time
        for _ in range(int(hours * 60 / interval_minutes)):
            ctx = self._generate_normal_context(
                current_time, age, gender, chronic_conditions, lifestyle)
            risk_score = self._calculate_risk_score(ctx, chronic_conditions, lifestyle)
            label = 1 if risk_score >= 0.45 else 0
            data.append((ctx, label))
            current_time += timedelta(minutes=interval_minutes)
        return data

    # ------------------------------------------------------------------
    # سيناريو 2: تدهور تدريجي
    # ------------------------------------------------------------------
    def generate_deterioration_scenario(self, hours=6, interval_minutes=5,
                                        age=50, gender='M', chronic_conditions=None,
                                        lifestyle=None, medications=None,
                                        family_history=None, high_risk=False):
        if chronic_conditions is None:
            chronic_conditions = []
        if lifestyle is None:
            lifestyle = {}

        data = []
        current_time = self.base_time
        total_steps = int(hours * 60 / interval_minutes)

        for step in range(total_steps):
            progress = step / total_steps

            if high_risk:
                vitals = {
                    'heart_rate':               75 + 50 * progress + random.uniform(-2, 2),
                    'blood_pressure_systolic':  120 + 50 * progress + random.uniform(-3, 3),
                    'blood_pressure_diastolic': 80  + 25 * progress + random.uniform(-2, 2),
                    'oxygen_saturation':        98  - 12 * progress + random.uniform(-1, 1),
                    'body_temperature':         37.0 + 3.0 * progress + random.uniform(-0.3, 0.3),
                    'activity_level':           max(0, int(2 - 2.5 * progress + random.uniform(-0.5, 0.5))),
                    'room_temperature':         22  + 2  * progress + random.uniform(-0.5, 0.5),
                }
            else:
                vitals = {
                    'heart_rate':               75 + 40 * progress + random.uniform(-2, 2),
                    'blood_pressure_systolic':  120 + 40 * progress + random.uniform(-3, 3),
                    'blood_pressure_diastolic': 80  + 20 * progress + random.uniform(-2, 2),
                    'oxygen_saturation':        98  - 10 * progress + random.uniform(-1, 1),
                    'body_temperature':         37.0 + 2.5 * progress + random.uniform(-0.3, 0.3),
                    'activity_level':           max(0, int(2 - 2 * progress + random.uniform(-0.5, 0.5))),
                    'room_temperature':         22  + 2  * progress + random.uniform(-0.5, 0.5),
                }

            ctx = self._make_ctx(current_time, vitals, age, gender, chronic_conditions, lifestyle)
            risk_score = self._calculate_risk_score(ctx, chronic_conditions, lifestyle)
            label = 1 if risk_score >= 0.45 else 0
            data.append((ctx, label))
            current_time += timedelta(minutes=interval_minutes)

        return data

    # ------------------------------------------------------------------
    # سيناريو 3: ارتفاع مفاجئ (طارئ)
    # ------------------------------------------------------------------
    def generate_emergency_spike_scenario(self, hours=2, interval_minutes=5,
                                          age=50, gender='M', chronic_conditions=None,
                                          lifestyle=None, medications=None, family_history=None):
        if chronic_conditions is None:
            chronic_conditions = []
        if lifestyle is None:
            lifestyle = {}

        data = []
        current_time = self.base_time
        total_steps = int(hours * 60 / interval_minutes)
        spike_start = int(total_steps * 0.6)

        for step in range(total_steps):
            if step < spike_start:
                ctx = self._generate_normal_context(
                    current_time, age, gender, chronic_conditions, lifestyle)
            else:
                vitals = {
                    'heart_rate':               random.uniform(130, 150),
                    'blood_pressure_systolic':  random.uniform(170, 200),
                    'blood_pressure_diastolic': random.uniform(100, 120),
                    'oxygen_saturation':        random.uniform(80, 85),
                    'body_temperature':         random.uniform(39.0, 41.0),
                    'activity_level':           0,
                    'room_temperature':         random.uniform(22, 26),
                }
                ctx = self._make_ctx(current_time, vitals, age, gender, chronic_conditions, lifestyle)

            risk_score = self._calculate_risk_score(ctx, chronic_conditions, lifestyle)
            label = 1 if risk_score >= 0.45 else 0
            data.append((ctx, label))
            current_time += timedelta(minutes=interval_minutes)

        return data

    # ------------------------------------------------------------------
    # *** السيناريو الرابع الجديد ***
    # مريض عالي الخطورة + vitals معتدلة = خطر
    # هذا هو المفتاح لتعليم النموذج الفرق بين أحمد وخالد
    # ------------------------------------------------------------------
    def generate_high_risk_moderate_vitals_scenario(
            self, hours=3, interval_minutes=5,
            age=60, gender='M', chronic_conditions=None, lifestyle=None):
        """
        السيناريو الحاسم:
        يولد مريضاً عالي الخطورة بقيم حيوية معتدلة (ليست طارئة).
        النموذج يجب أن يتعلم أن هذه القيم خطيرة على هذا المريض
        بينما هي آمنة على شخص صحيح.
        """
        if chronic_conditions is None:
            chronic_conditions = ['hypertension', 'diabetes']
        if lifestyle is None:
            lifestyle = {'smoking': 'current', 'bmi': 32}

        data = []
        current_time = self.base_time
        total_steps = int(hours * 60 / interval_minutes)

        for step in range(total_steps):
            # vitals معتدلة — ليست طارئة لكن فوق الطبيعي قليلاً
            vitals = {
                'heart_rate':               random.uniform(95, 115),   # مرتفع قليلاً
                'blood_pressure_systolic':  random.uniform(135, 155),  # مرتفع قليلاً
                'blood_pressure_diastolic': random.uniform(85, 100),
                'oxygen_saturation':        random.uniform(91, 95),    # منخفض قليلاً
                'body_temperature':         random.uniform(37.5, 38.5),
                'activity_level':           random.randint(0, 1),
                'room_temperature':         random.uniform(22, 26),
            }
            ctx = self._make_ctx(current_time, vitals, age, gender, chronic_conditions, lifestyle)
            risk_score = self._calculate_risk_score(ctx, chronic_conditions, lifestyle)
            label = 1 if risk_score >= 0.45 else 0
            data.append((ctx, label))
            current_time += timedelta(minutes=interval_minutes)

        return data

    def generate_low_risk_moderate_vitals_scenario(
            self, hours=3, interval_minutes=5,
            age=25, gender='M', chronic_conditions=None, lifestyle=None):
        """
        المقابل: شخص صحيح بنفس الـ vitals المعتدلة = آمن.
        يُعلّم النموذج الفرق بوضوح.
        """
        if chronic_conditions is None:
            chronic_conditions = []
        if lifestyle is None:
            lifestyle = {'smoking': 'never', 'bmi': 22}

        data = []
        current_time = self.base_time
        total_steps = int(hours * 60 / interval_minutes)

        for step in range(total_steps):
            vitals = {
                'heart_rate':               random.uniform(95, 115),
                'blood_pressure_systolic':  random.uniform(135, 155),
                'blood_pressure_diastolic': random.uniform(85, 100),
                'oxygen_saturation':        random.uniform(91, 95),
                'body_temperature':         random.uniform(37.5, 38.5),
                'activity_level':           random.randint(0, 1),
                'room_temperature':         random.uniform(22, 26),
            }
            ctx = self._make_ctx(current_time, vitals, age, gender, chronic_conditions, lifestyle)
            risk_score = self._calculate_risk_score(ctx, chronic_conditions, lifestyle)
            label = 1 if risk_score >= 0.45 else 0
            data.append((ctx, label))
            current_time += timedelta(minutes=interval_minutes)

        return data

    # ------------------------------------------------------------------
    # توليد مجموعة تدريب متنوعة — تشمل السيناريو الرابع
    # ------------------------------------------------------------------
    def generate_mixed_scenarios(self, num_each=50):
        """
        يولد خليطاً من السيناريوهات الأربعة مع تنوع حقيقي في الخلفيات الطبية.
        السيناريو الرابع هو المفتاح لتعليم النموذج الفرق بين أحمد وخالد
        عند نفس مستوى الـ vitals المعتدلة.
        """
        scenarios = []

        for _ in range(num_each):
            age = random.randint(20, 85)
            gender = random.choice(['M', 'F'])
            chronic = random.choice([
                [],
                ['hypertension'],
                ['diabetes'],
                ['hypertension', 'diabetes'],
                ['heart_disease'],
                ['hypertension', 'heart_disease'],
            ])
            lifestyle = random.choice([
                {'smoking': 'never',   'bmi': 22},
                {'smoking': 'never',   'bmi': 26},
                {'smoking': 'former',  'bmi': 27},
                {'smoking': 'current', 'bmi': 30},
                {'smoking': 'current', 'bmi': 35},
            ])
            medications   = random.choice([[], ['Metformin'], ['Aspirin'], ['Amlodipine']])
            family_history = random.choice([[], ['Diabetes'], ['Heart Disease']])

            high_risk = (
                age > 60 or
                'hypertension' in chronic or
                'diabetes' in chronic or
                'heart_disease' in chronic or
                lifestyle.get('smoking') == 'current'
            )

            # السيناريوهات الثلاثة الأصلية
            scenarios.append(self.generate_stable_scenario(
                hours=1, interval_minutes=5,
                age=age, gender=gender,
                chronic_conditions=chronic, lifestyle=lifestyle,
                medications=medications, family_history=family_history,
            ))
            scenarios.append(self.generate_deterioration_scenario(
                hours=2, interval_minutes=5,
                age=age, gender=gender,
                chronic_conditions=chronic, lifestyle=lifestyle,
                medications=medications, family_history=family_history,
                high_risk=high_risk,
            ))
            scenarios.append(self.generate_emergency_spike_scenario(
                hours=1, interval_minutes=5,
                age=age, gender=gender,
                chronic_conditions=chronic, lifestyle=lifestyle,
                medications=medications, family_history=family_history,
            ))

        # *** السيناريو الرابع: حالات متعددة بـ vitals معتدلة ***
        # مرضى عاليو الخطورة بأعمار وأمراض مختلفة
        high_risk_profiles = [
            {'age': 58, 'gender': 'M', 'chronic': ['hypertension', 'diabetes'],
             'lifestyle': {'smoking': 'current', 'bmi': 33}},
            {'age': 65, 'gender': 'F', 'chronic': ['hypertension'],
             'lifestyle': {'smoking': 'former', 'bmi': 30}},
            {'age': 72, 'gender': 'M', 'chronic': ['heart_disease'],
             'lifestyle': {'smoking': 'never', 'bmi': 28}},
            {'age': 55, 'gender': 'M', 'chronic': ['hypertension', 'diabetes', 'heart_disease'],
             'lifestyle': {'smoking': 'current', 'bmi': 36}},
            {'age': 60, 'gender': 'F', 'chronic': ['diabetes'],
             'lifestyle': {'smoking': 'current', 'bmi': 32}},
        ]
        for profile in high_risk_profiles:
            for _ in range(4):  # 4 تكرارات لكل profile
                scenarios.append(self.generate_high_risk_moderate_vitals_scenario(
                    hours=3, interval_minutes=5,
                    age=profile['age'], gender=profile['gender'],
                    chronic_conditions=profile['chronic'],
                    lifestyle=profile['lifestyle'],
                ))

        # مقابلهم: شباب أصحاء بنفس الـ vitals = آمنون
        low_risk_profiles = [
            {'age': 22, 'chronic': [], 'lifestyle': {'smoking': 'never', 'bmi': 21}},
            {'age': 28, 'chronic': [], 'lifestyle': {'smoking': 'never', 'bmi': 23}},
            {'age': 35, 'chronic': [], 'lifestyle': {'smoking': 'former', 'bmi': 25}},
        ]
        for profile in low_risk_profiles:
            for _ in range(4):
                scenarios.append(self.generate_low_risk_moderate_vitals_scenario(
                    hours=3, interval_minutes=5,
                    age=profile['age'],
                    chronic_conditions=profile['chronic'],
                    lifestyle=profile['lifestyle'],
                ))

        return scenarios
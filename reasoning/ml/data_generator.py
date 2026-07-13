import random
from datetime import datetime, timedelta


class ClinicalScenarioGenerator:
    """يولد سيناريوهات سريرية تركيبية مع تسميات (خطر/طبيعي) ومعلومات طبية شاملة."""

    def __init__(self):
        self.base_time = datetime(2026, 1, 1, 12, 0, 0)

    # ------------------------------------------------------------------
    # الدالة الجوهرية: تحسب نقاط الخطر وتُعيد درجة الخطورة والعتبة المناسبة
    # هذه الدالة تُستخدم فقط لتوليد تسميات التدريب (Labels)
    # وهي ليست جزءًا من "ذكاء" النموذج، بل هي "المعلم" الذي يصنع الأمثلة
    # ------------------------------------------------------------------
    def _calculate_risk_score(self, ctx, chronic_conditions=None, lifestyle=None):
        if chronic_conditions is None:
            chronic_conditions = []
        if lifestyle is None:
            lifestyle = {}

        # --- نقاط الـ vitals (تعكس شدة التدهور الحالي) ---
        vitals_score = 0.0

        hr = ctx.get('heart_rate', 75)
        if hr > 120:
            vitals_score += 0.35
        elif hr > 100:
            vitals_score += 0.20
        elif hr < 50:
            vitals_score += 0.25

        bp = ctx.get('blood_pressure_systolic', 120)
        if bp > 170:
            vitals_score += 0.35
        elif bp > 140:
            vitals_score += 0.20

        o2 = ctx.get('oxygen_saturation', 98)
        if o2 < 90:
            vitals_score += 0.30
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

        # --- معامل الخطر الشخصي (يُضخّم تأثير الـ vitals على المرضى الأكثر هشاشة) ---
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

        risk_score = vitals_score * personal_multiplier

        # --- تحديد العتبة بناءً على خطورة المريض ---
        if personal_multiplier > 1.5:
            threshold = 0.35
        else:
            threshold = 0.55

        return risk_score, threshold

    # ------------------------------------------------------------------
    # بناء سياق واحد بقراءات طبيعية
    # ------------------------------------------------------------------
    def _generate_normal_context(self, timestamp, age=50, gender='M',
                                 chronic_conditions=None, lifestyle=None,
                                 family_history=None):
        """قراءات طبيعية تماماً مع معلومات المريض."""
        if chronic_conditions is None:
            chronic_conditions = []
        if lifestyle is None:
            lifestyle = {}
        if family_history is None:
            family_history = []

        # استخراج التاريخ العائلي لأمراض القلب والسكري
        family_lower = [f.lower().strip() if isinstance(f, str) else str(f.get('condition', f.get('name', ''))).lower().strip() for f in family_history]
        has_family_heart = 1 if any('heart' in f or 'قلب' in f for f in family_lower) else 0
        has_family_diabetes = 1 if any('diabetes' in f or 'سكري' in f for f in family_lower) else 0

        # توليد القيم الأساسية
        hr_val = random.uniform(70, 80)
        bp_sys_val = random.uniform(110, 130)
        bp_dia_val = random.uniform(70, 85)

        ctx = {
            'timestamp': timestamp,
            'heart_rate': hr_val,
            'blood_pressure_systolic': bp_sys_val,
            'blood_pressure_diastolic': bp_dia_val,
            # ✅ MAP محسوبة من ضغط الدم
            'map': bp_dia_val + (bp_sys_val - bp_dia_val) / 3,
            'oxygen_saturation': random.uniform(95, 100),
            'body_temperature': random.uniform(36.1, 37.2),
            'activity_level': random.randint(1, 3),
            'room_temperature': random.uniform(20, 24),
            # المستشعرات الجديدة
            'blood_glucose': random.uniform(80, 120),
            'respiratory_rate': random.uniform(14, 18),
            # الميزات الشخصية
            'age': age,
            'gender': 1 if gender == 'M' else 0,
            'has_hypertension': 1 if 'hypertension' in chronic_conditions else 0,
            'has_diabetes': 1 if 'diabetes' in chronic_conditions else 0,
            'has_heart_disease': 1 if 'heart_disease' in chronic_conditions else 0,
            'smoking_status': (
                0 if not lifestyle else
                0 if lifestyle.get('smoking') == 'never' else
                1 if lifestyle.get('smoking') == 'former' else
                2
            ),
            'bmi': lifestyle.get('bmi', 25) if lifestyle else 25,
            # التاريخ العائلي
            'family_heart_disease': has_family_heart,
            'family_diabetes': has_family_diabetes,
        }
        return ctx

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
        if family_history is None:
            family_history = []

        data = []
        current_time = self.base_time

        for _ in range(int(hours * 60 / interval_minutes)):
            ctx = self._generate_normal_context(
                current_time, age, gender, chronic_conditions, lifestyle, family_history
            )
            risk_score, threshold = self._calculate_risk_score(ctx, chronic_conditions, lifestyle)
            label = 1 if risk_score > threshold else 0
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
        if family_history is None:
            family_history = []

        # استخراج التاريخ العائلي
        family_lower = [f.lower().strip() if isinstance(f, str) else str(f.get('condition', f.get('name', ''))).lower().strip() for f in family_history]
        has_family_heart = 1 if any('heart' in f or 'قلب' in f for f in family_lower) else 0
        has_family_diabetes = 1 if any('diabetes' in f or 'سكري' in f for f in family_lower) else 0

        data = []
        current_time = self.base_time
        total_steps = int(hours * 60 / interval_minutes)

        for step in range(total_steps):
            progress = step / total_steps

            if high_risk:
                heart_rate = 75 + 50 * progress + random.uniform(-2, 2)
                bp_sys = 120 + 50 * progress + random.uniform(-3, 3)
                bp_dia = 80 + 25 * progress + random.uniform(-2, 2)
                oxygen = 98 - 12 * progress + random.uniform(-1, 1)
                body_temp = 37.0 + 3.0 * progress + random.uniform(-0.3, 0.3)
                activity = max(0, int(2 - 2.5 * progress + random.uniform(-0.5, 0.5)))
                room_temp = 22 + 2 * progress + random.uniform(-0.5, 0.5)
                blood_glucose = random.uniform(90, 200) * (1 + progress)
                respiratory_rate = random.uniform(16, 28) * (1 + progress * 0.5)
            else:
                heart_rate = 75 + 40 * progress + random.uniform(-2, 2)
                bp_sys = 120 + 40 * progress + random.uniform(-3, 3)
                bp_dia = 80 + 20 * progress + random.uniform(-2, 2)
                oxygen = 98 - 10 * progress + random.uniform(-1, 1)
                body_temp = 37.0 + 2.5 * progress + random.uniform(-0.3, 0.3)
                activity = max(0, int(2 - 2 * progress + random.uniform(-0.5, 0.5)))
                room_temp = 22 + 2 * progress + random.uniform(-0.5, 0.5)
                blood_glucose = random.uniform(80, 120) * (1 + progress * 0.2)
                respiratory_rate = random.uniform(14, 20) * (1 + progress * 0.2)

            ctx = {
                'timestamp': current_time,
                'heart_rate': heart_rate,
                'blood_pressure_systolic': bp_sys,
                'blood_pressure_diastolic': bp_dia,
                # ✅ MAP محسوبة
                'map': bp_dia + (bp_sys - bp_dia) / 3,
                'oxygen_saturation': oxygen,
                'body_temperature': body_temp,
                'activity_level': activity,
                'room_temperature': room_temp,
                # المستشعرات الجديدة
                'blood_glucose': blood_glucose,
                'respiratory_rate': respiratory_rate,
                # الميزات الشخصية
                'age': age,
                'gender': 1 if gender == 'M' else 0,
                'has_hypertension': 1 if 'hypertension' in chronic_conditions else 0,
                'has_diabetes': 1 if 'diabetes' in chronic_conditions else 0,
                'has_heart_disease': 1 if 'heart_disease' in chronic_conditions else 0,
                'smoking_status': (
                    0 if not lifestyle else
                    0 if lifestyle.get('smoking') == 'never' else
                    1 if lifestyle.get('smoking') == 'former' else
                    2
                ),
                'bmi': lifestyle.get('bmi', 25) if lifestyle else 25,
                # التاريخ العائلي
                'family_heart_disease': has_family_heart,
                'family_diabetes': has_family_diabetes,
            }

            risk_score, threshold = self._calculate_risk_score(ctx, chronic_conditions, lifestyle)
            label = 1 if risk_score > threshold else 0

            data.append((ctx, label))
            current_time += timedelta(minutes=interval_minutes)

        return data

    # ------------------------------------------------------------------
    # سيناريو 3: ارتفاع مفاجئ (طارئ)
    # ------------------------------------------------------------------
    def generate_emergency_spike_scenario(self, hours=2, interval_minutes=5,
                                          age=50, gender='M', chronic_conditions=None,
                                          lifestyle=None, medications=None,
                                          family_history=None):
        if chronic_conditions is None:
            chronic_conditions = []
        if lifestyle is None:
            lifestyle = {}
        if family_history is None:
            family_history = []

        family_lower = [f.lower().strip() if isinstance(f, str) else str(f.get('condition', f.get('name', ''))).lower().strip() for f in family_history]
        has_family_heart = 1 if any('heart' in f or 'قلب' in f for f in family_lower) else 0
        has_family_diabetes = 1 if any('diabetes' in f or 'سكري' in f for f in family_lower) else 0

        data = []
        current_time = self.base_time
        total_steps = int(hours * 60 / interval_minutes)
        spike_start = int(total_steps * 0.6)

        for step in range(total_steps):
            if step < spike_start:
                ctx = self._generate_normal_context(
                    current_time, age, gender, chronic_conditions, lifestyle, family_history
                )
            else:
                bp_sys_val = random.uniform(170, 200)
                bp_dia_val = random.uniform(100, 120)
                ctx = {
                    'timestamp': current_time,
                    'heart_rate': random.uniform(130, 150),
                    'blood_pressure_systolic': bp_sys_val,
                    'blood_pressure_diastolic': bp_dia_val,
                    # ✅ MAP محسوبة
                    'map': bp_dia_val + (bp_sys_val - bp_dia_val) / 3,
                    'oxygen_saturation': random.uniform(80, 85),
                    'body_temperature': random.uniform(39.0, 41.0),
                    'activity_level': 0,
                    'room_temperature': random.uniform(22, 26),
                    'blood_glucose': random.uniform(250, 400),
                    'respiratory_rate': random.uniform(30, 45),
                    'age': age,
                    'gender': 1 if gender == 'M' else 0,
                    'has_hypertension': 1 if 'hypertension' in chronic_conditions else 0,
                    'has_diabetes': 1 if 'diabetes' in chronic_conditions else 0,
                    'has_heart_disease': 1 if 'heart_disease' in chronic_conditions else 0,
                    'smoking_status': (
                        0 if not lifestyle else
                        0 if lifestyle.get('smoking') == 'never' else
                        1 if lifestyle.get('smoking') == 'former' else
                        2
                    ),
                    'bmi': lifestyle.get('bmi', 25) if lifestyle else 25,
                    'family_heart_disease': has_family_heart,
                    'family_diabetes': has_family_diabetes,
                }

            risk_score, threshold = self._calculate_risk_score(ctx, chronic_conditions, lifestyle)
            label = 1 if risk_score > threshold else 0

            data.append((ctx, label))
            current_time += timedelta(minutes=interval_minutes)

        return data

    # ------------------------------------------------------------------
    # سيناريو 4: خطر منعزل (مؤشر واحد فقط في حالة طوارئ)
    # ------------------------------------------------------------------
    def generate_isolated_danger_scenarios(self, num_each=30):
        scenarios = []
        danger_values = {
            'heart_rate': 145,
            'blood_pressure_systolic': 185,
            'oxygen_saturation': 82,
            'body_temperature': 40.5,
            'blood_glucose': 350,
            'respiratory_rate': 40,
        }

        for key, danger_val in danger_values.items():
            for _ in range(num_each):
                scenario = []
                for i in range(6):
                    ctx = self._generate_normal_context(self.base_time)
                    if i >= 3:
                        ctx[key] = danger_val + random.uniform(-2, 2)
                    scenario.append((ctx.copy(), 1 if i >= 3 else 0))
                scenarios.append(scenario)
        return scenarios

    # ------------------------------------------------------------------
    # سيناريو 5: بيانات ناقصة (مريض لديه حساسات محدودة فقط)
    # ------------------------------------------------------------------
    def generate_partial_sensor_scenarios(self, num_each=20):
        """يُعلّم النموذج أن الخطر يُستنتج حتى مع نقص بعض الحساسات."""
        scenarios = []
        for _ in range(num_each):
            scenario = []
            for i in range(6):
                ctx = self._generate_normal_context(self.base_time)
                if i >= 3:
                    ctx['heart_rate'] = random.uniform(130, 150)
                    ctx['oxygen_saturation'] = random.uniform(80, 85)
                scenario.append((ctx.copy(), 1 if i >= 3 else 0))
            scenarios.append(scenario)
        return scenarios

    # ------------------------------------------------------------------
    # توليد مجموعة تدريب متنوعة
    # ------------------------------------------------------------------
    def generate_mixed_scenarios(self, num_each=50):
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
            medications = random.choice([
                [],
                ['Metformin'],
                ['Aspirin'],
                ['Amlodipine'],
            ])
            family_history = random.choice([
                [],
                ['Diabetes'],
                ['Heart Disease'],
                ['Heart Disease', 'Diabetes'],
            ])

            high_risk = (
                age > 60 or
                'hypertension' in chronic or
                'diabetes' in chronic or
                'heart_disease' in chronic or
                lifestyle.get('smoking') == 'current'
            )

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

        # إضافة سيناريوهات الخطر المنعزل والبيانات الناقصة
        scenarios.extend(self.generate_isolated_danger_scenarios(num_each=30))
        scenarios.extend(self.generate_partial_sensor_scenarios(num_each=20))

        return scenarios
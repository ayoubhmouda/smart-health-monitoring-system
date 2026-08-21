# core/models.py
from datetime import date
from django.db import models
from django.conf import settings


class MonitoredElement(models.Model):
    class ElementType(models.TextChoices):
        PATIENT = 'patient', 'Patient'
        ELDERLY = 'elderly', 'Elderly'
        DISABLED = 'disabled', 'Disabled'

    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    element_type = models.CharField(max_length=20, choices=ElementType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    # ربط المريض بالطبيب المعالج (مريض واحد يتابعه طبيب واحد كحد أقصى)
    doctor = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='monitored_patients',
        limit_choices_to={'role': 'doctor'},  # حصر الاختيار للأطباء فقط
        help_text="الطبيب المعالج المسؤول عن المريض"
    )

    # تعيين مقدم رعاية واحد أو أكثر في نفس الوقت عبر علاقة ManyToMany
    caregivers = models.ManyToManyField(
        'accounts.User',
        related_name='cared_patients',
        blank=True,
        limit_choices_to={'role': 'caregiver'},  # حصر الاختيار لمقدمي الرعاية فقط
        help_text="مقدمو الرعاية المسؤولون عن متابعة المريض"
    )

    @property
    def age(self) -> int:
        """يحسب العمر الحالي بناءً على تاريخ الميلاد بدقة."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def __str__(self):
        return f"{self.full_name} ({self.get_element_type_display()})"


class Patient(models.Model):
    element = models.OneToOneField(MonitoredElement, on_delete=models.CASCADE, related_name='patient_profile')
    diagnosis = models.CharField(max_length=255, blank=True)
    admission_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Patient: {self.element.full_name}"


class Elderly(models.Model):
    element = models.OneToOneField(MonitoredElement, on_delete=models.CASCADE, related_name='elderly_profile')
    mobility_level = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Elderly: {self.element.full_name}"


class Disabled(models.Model):
    element = models.OneToOneField(MonitoredElement, on_delete=models.CASCADE, related_name='disabled_profile')
    disability_type = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Disabled: {self.element.full_name}"


class MedicalHistory(models.Model):
    monitored_element = models.OneToOneField(
        'MonitoredElement', on_delete=models.CASCADE, related_name='medical_history'
    )
    chronic_conditions = models.JSONField(
        default=list, 
        blank=True, 
        null=True,
        help_text=(
            'قائمة الأمراض المزمنة المعالجة بنموذج MIMIC.\n'
            '- أمراض القلب: "heart_disease", "heart_failure"\n'
            '- أمراض مزمنة: "hypertension", "diabetes", "copd"\n'
            'مثال: [{"name": "heart_disease"}, {"name": "diabetes"}]'
        )
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Medical History of {self.monitored_element.full_name}'
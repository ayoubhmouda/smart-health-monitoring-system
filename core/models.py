
# pyrefly: ignore [missing-import]
from django.db import models
from datetime import date


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
    @property
    def age(self) -> int:
        """يحسب العمر الحالي بناءً على تاريخ الميلاد."""
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def __str__(self):
        return f"{self.full_name} ({self.get_element_type_display()})"


class Patient(models.Model):
    element = models.OneToOneField(MonitoredElement, on_delete=models.CASCADE, related_name='patient_profile')
    diagnosis = models.TextField(blank=True)
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
        help_text='الميزات المدعومة: "hypertension", "diabetes", "heart_disease". مثال: [{"name": "Hypertension"}, {"name": "Diabetes"}]'
    )
    lifestyle = models.JSONField(
        default=dict, 
        blank=True, 
        null=True,
        help_text='الميزات المدعومة: "smoking" (current/former), "bmi" (رقم). مثال: {"smoking": "current", "bmi": 32}'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Medical History of {self.monitored_element.full_name}'
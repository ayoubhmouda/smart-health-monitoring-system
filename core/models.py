from django.db import models

class MonitoredElement(models.Model):
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.full_name


class Patient(MonitoredElement):
    diagnosis = models.TextField(blank=True)
    admission_date = models.DateField(null=True, blank=True)


class Elderly(MonitoredElement):
    mobility_level = models.CharField(max_length=50, blank=True)


class Disabled(MonitoredElement):
    disability_type = models.CharField(max_length=100, blank=True)


class MedicalHistory(models.Model):
    monitored_element = models.OneToOneField(
        'Patient',
        on_delete=models.CASCADE,
        related_name='medical_history'
    )
    chronic_conditions = models.JSONField(default=list, blank=True)
    allergies = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Medical History of {self.monitored_element.full_name}"
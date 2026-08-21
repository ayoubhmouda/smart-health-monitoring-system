# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        DOCTOR = 'doctor', 'Doctor'
        CAREGIVER = 'caregiver', 'Caregiver'

    # تحديد دور وصلاحية المستخدم في المنظومة الطبية
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CAREGIVER,
    )

    # 🟢 رقم هاتف الاتصال المباشر المربوط بنظام الإشعارات الفورية والـ SMS للطبيب ومقدم الرعاية
    # تم تصحيح المحاذاة والمسافات البادئة ليكون جزءاً أساسياً داخل كلاس User
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        help_text="رقم هاتف الاتصال للطبيب أو مقدم الرعاية"
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
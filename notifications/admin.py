from django.contrib import admin
from .models import CareGiver, MedicalPersonnel, InterestRegistration, Notification

@admin.register(CareGiver)
class CareGiverAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number')

@admin.register(MedicalPersonnel)
class MedicalPersonnelAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'phone_number')

@admin.register(InterestRegistration)
class InterestRegistrationAdmin(admin.ModelAdmin):
    list_display = ('interested_party', 'monitored_element', 'notify_via')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'sent_at')
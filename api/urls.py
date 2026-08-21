# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = DefaultRouter()
router.register(r'monitored-elements', views.MonitoredElementViewSet)
router.register(r'patients', views.PatientViewSet)
router.register(r'medical-histories', views.MedicalHistoryViewSet)
router.register(r'sensor-types', views.SensorTypeViewSet)
router.register(r'sensors', views.SensorViewSet)
router.register(r'data-source-configs', views.DataSourceConfigViewSet)
router.register(r'sensor-readings', views.SensorReadingViewSet)
router.register(r'contexts', views.ContextViewSet)
router.register(r'context-histories', views.ContextHistoryViewSet)
router.register(r'insights', views.InsightViewSet)
router.register(r'corrective-actions', views.CorrectiveActionViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'doctors', views.DoctorViewSet, basename='doctors')
router.register(r'rules', views.RuleViewSet, basename='rules')
router.register(r'caregivers', views.CaregiverViewSet, basename='caregivers')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.register_user, name='register'),
    path('login/', obtain_auth_token, name='login'),  
    path('user/profile/', views.current_user, name='current-user'),
]


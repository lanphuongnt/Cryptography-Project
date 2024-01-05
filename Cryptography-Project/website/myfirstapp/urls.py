from django.urls import path
from . import views

app_name = 'myfirstapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    path('reception/', views.reception, name='reception'),
    path('patient_profile/', views.patient_profile, name='patient_profile'),
    path('get_patient_info/', views.get_patient_info, name='get_patient_info'),
    path('get_health_record/', views.GetHealthRecordOfPatient, name='get_health_record'),
    path('doctor/', views.doctor, name='doctor'),
    path('doctor/filter/', views.GetListOfPatientsWithFilter, name='filter'),
    path('doctor/patient_ehr', views.PatientHealthRecord, name='patient_ehr')
]

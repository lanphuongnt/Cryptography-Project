from django.urls import path
from . import views

app_name = 'myfirstapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('logout/', views.logout, name='logout'),
    path('staff_profile/', views.staff_profile, name='staff_profile'),
    path('reception/', views.reception, name='reception'),
    path('patient_profile/', views.patient_profile, name='patient_profile'),
    path('staff_profile/reference/patient_view/', views.ehr_view, name='patient_view'),
    path('get_patient_info/', views.get_patient_info, name='get_patient_info'),
    # path('staff_profile/reference/', views.reference_by_specialty, name='reference'),
    path('lanphuong/', views.Doctor, name='lanphuong'),
    # path('lanphuongresult/', views.result, name='result'),
]

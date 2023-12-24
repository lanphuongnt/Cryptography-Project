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
    # path('staff_profile/patients/', views.reference_by_specialty, name='patient_view'),
    # path('staff_profile/patients/', views.get_medical_history, name='patient_get_ehr'),
    path('patient_profile/', views.patient_profile, name='patient_profile'),
    # path('patient_view/', views.ehr_view, name='patient_ehr'),
    path('staff_profile/reference/', views.reference_by_specialty, name='reference')
]

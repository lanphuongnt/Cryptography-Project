from django.urls import path
from . import views
# from .views import signup, index, login_view, staff_profile, patient_profile, logout

app_name = 'myfirstapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('logout/', views.logout, name='logout'),
    path('staff_profile/', views.staff_profile, name='staff_profile'),
    path('patient_profile/', views.patient_profile, name='patient_profile'),
]

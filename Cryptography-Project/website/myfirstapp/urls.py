from django.urls import path
from . import views
from .views import signup, home, login_view, staff_profile, patient_profile

urlpatterns = [
    path('home/', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('staff_profile/', staff_profile, name='staff_profile'),
    path('patient_profile/', patient_profile, name='patient_profile'),
]

from django.urls import path
from . import views
from .views import signup, index, login_view, staff_profile, patient_profile, logout

app_name = 'myfirstapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout, name='logout'),
    path('staff_profile/', staff_profile, name='staff_profile'),
    path('patient_profile/', patient_profile, name='patient_profile'),
]

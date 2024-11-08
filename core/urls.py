from django.contrib.auth.views import LoginView
from django.urls import path

from core import views

urlpatterns = [
    path('', views.home, name='home'),
    path('Signup/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', LoginView.as_view(template_name='core/login.html'), name='login'),

]

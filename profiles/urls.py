from django.urls import path

from profiles import views

urlpatterns = [
    path('<int:user_id>/', views.profile, name='profile'),
    path('edit/<int:user_id>/', views.profile_edit, name='profile_edit'),
]
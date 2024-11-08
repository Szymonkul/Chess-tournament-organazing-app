from django.urls import path

from tournaments import views

urlpatterns = [path('add/', views.add_tournament, name='add_tournament'),
               path('', views.list_of_tournaments, name='tournaments'),
               path('<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),
               path('edit/<int:tournament_id>/', views.edit_tournament, name='tournament_edit'),
               path('<int:tournament_id>/join/', views.join_tournament, name='join_tournament'),
               path('<int:tournament_id>/round/<int:round_id>/', views.round_detail, name='round_detail'),
               path('<int:tournament_id>/round/<int:round_id>/edit/', views.enter_round_results, name='enter_round_results'),
               path('<int:tournament_id>/start/', views.start_tournament,
                    name='start_tournament'),
               path('my/history/', views.tournament_history,
                    name='tournament_history'),
               ]

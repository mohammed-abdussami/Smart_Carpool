from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('add-schedule/', views.add_schedule, name='add_schedule'),
    path('matches/', views.matches_view, name='matches'),
    path('matches/<int:match_id>/<str:status>/', views.update_match_status, name='update_match_status'),
    path('forms/', views.forms_view, name='forms'),
]
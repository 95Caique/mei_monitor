from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    path('', views.index, name='index'),
    path('users/', views.users_list, name='users_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/toggle/', views.user_toggle_active, name='user_toggle'),
    path('logs/', views.logs_list, name='logs_list'),
]

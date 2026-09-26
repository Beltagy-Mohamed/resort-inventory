from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_home, name='chat_home'),
    path('room/<int:room_id>/', views.room_view, name='chat_room'),
    path('start/<int:user_id>/', views.start_private, name='chat_start_private'),
    path('api/room/<int:room_id>/messages/', views.api_messages, name='chat_api_messages'),
    path('api/unread/', views.api_unread_count, name='chat_api_unread'),
    path('api/users/', views.get_users_list, name='chat_api_users'),
    path('api/rooms/', views.api_rooms_list, name='chat_api_rooms'),
    path('set-name/', views.set_display_name, name='chat_set_name'),
]

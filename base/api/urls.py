from django.urls import path
from . import views


urlpatterns =[
    path('', views.getRoute),
    path('api/rooms/', views.getRooms, name='get-rooms')
]
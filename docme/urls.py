from django.urls import path
from . import views

urlpatterns = [
    path('auto_tour', views.auto_tour_index),
    path('start_tour', views.start_tour),
    path('get_steps', views.get_steps),
]

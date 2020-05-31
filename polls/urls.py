from django.urls import path
from polls import views

urlpatterns = [
    path('', views.mapp, name='mapp'),
    path('get_value', views.get_value, name='get_value'),
    path('reset', views.reset, name='reset'),
    path('intoDb', views.reset, name='intoDb')
]

from django.urls import path
from polls import views

urlpatterns = [
    path('', views.reset, name='reset'),
    path('get_value', views.get_value, name='get_value'),
    path('reset', views.reset, name='reset'),
    path('intoDb', views.intoDb, name='intoDb'),
    path('run',views.run, name='run')
]

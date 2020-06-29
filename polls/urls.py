from django.urls import path
from polls import views

urlpatterns = [
    path('', views.reset, name='reset'),
    path('getValue', views.getValue, name='getValue'),
    path('reset', views.reset, name='reset'),
    path('intoDb', views.intoDb, name='intoDb'),
    path('run', views.run, name='run'),
    path('export', views.export, name='export')
]

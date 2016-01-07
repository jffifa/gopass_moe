from django.conf.urls import url

from kotoridb import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^on_air$', views.on_air, name='on_air'),
]

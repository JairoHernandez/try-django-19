from django.conf.urls import url
from django.contrib import admin
from . import views # Doing it this way is not vulnerable to the views.py conflict in trydjango19/urls.py.
from .views import (post_list, post_create, post_detail, post_update, post_delete) # Doing it this ways is correct and also prepares it for Django 1.10.
					  

urlpatterns = [
    url(r'^$', post_list, name='list'),
    url(r'^create/$', post_create), # In general using the full path is best for function views.
    url(r'^(?P<slug>[\w-]+)/$', post_detail, name='detail'), # Instead of <id> one can also use <pk>.
    url(r'^(?P<slug>[\w-]+)/edit/$', post_update),
    url(r'^(?P<slug>[\w-]+)/delete/$', post_delete),
]

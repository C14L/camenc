from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.urls import path

import main.views

urlpatterns = [
    path('login/', login, name='user_login'),
    path('logout/', logout, name='user_logout'),
    path('admin/', admin.site.urls, name='admin'),
    path('', main.views.home),
    path('add', main.views.add),
]

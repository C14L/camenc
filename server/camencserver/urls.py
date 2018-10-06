from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.urls import path

import main.views

urlpatterns = [
    path('camenc/login/', login, name='user_login'),
    path('camenc/logout/', logout, name='user_logout'),
    path('camenc/admin/', admin.site.urls, name='admin'),
    path('camenc/', main.views.home),
    path('camenc/add', main.views.add),
]

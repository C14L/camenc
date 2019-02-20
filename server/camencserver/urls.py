from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.urls import path

import main.views

urlpatterns = [
    path('camenc/login/', LoginView.as_view(), name='user_login'),
    path('camenc/logout/', LogoutView.as_view(), name='user_logout'),
    path('camenc/admin/', admin.site.urls, name='admin'),
    path('camenc/doorman/add', main.views.doorman_add),
    path('camenc/add', main.views.add),
    path('camenc/', main.views.home),
]

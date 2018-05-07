from django.urls import path

import main.views

urlpatterns = [
    path('', main.views.home),
    path('add', main.views.add),
]

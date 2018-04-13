from django.urls import path
import main.views

urlpatterns = [
    path('', main.views.hello),
    path('add', main.views.add, name='add'),
]

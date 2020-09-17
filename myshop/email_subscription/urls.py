from django.urls import path
from . import views

app_name = 'email_subscription'

urlpatterns = [
    path('', views.email_subscribe, name='email_subscribe'),
]
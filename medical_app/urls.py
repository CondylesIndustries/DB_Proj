
from django.contrib import admin
from django.urls import path, include

import medical_app.views

urlpatterns = [
    path('', medical_app.views.home_view, name='home'),
    path('custom-query/', medical_app.views.custom_query_view, name='custom-query'),
    path('<str:portal_type>-portal/login', medical_app.views.login_view, name='login'),
    path('register/', medical_app.views.register_view, name='register'),
    path('signout/', medical_app.views.signout, name='signout'),
]
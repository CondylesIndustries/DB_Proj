
from django.contrib import admin
from django.urls import path, include

import medical_app.views

urlpatterns = [
    path('', medical_app.views.home_view, name='home'),
    path('custom-query', medical_app.views.custom_query_view, name='custom-query'),
]
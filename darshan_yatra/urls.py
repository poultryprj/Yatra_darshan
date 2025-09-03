from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [

    # path('hello/', views.hello, name='hello'),

    path('', views.login, name='login'),

    path('Registrationpage', views.Registrationpage, name='Registrationpage'),
    path("registration_api/", views.registration_api, name="registration_api"),
    # path("route_yatra_api/", views.route_yatra_api, name="route_yatra_api"),
    path("logout/", views.logout, name="logout"),

        
]
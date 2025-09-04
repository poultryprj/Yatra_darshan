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

    path('route_master/', views.route_master, name='route_master'),
    path('route_master_api/', views.route_master_api, name='route_master_api'),

    path('area_master/', views.area_master, name='area_master'),
    path('area_master_api/', views.area_master_api, name='area_master_api'),


    path('yatra_master/', views.yatra_master, name='yatra_master'),
    path('yatra_master_api/', views.yatra_master_api, name='yatra_master_api'),

        
]
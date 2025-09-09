from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [

    # path('hello/', views.hello, name='hello'),

    path('', views.login, name='login'),

    path('Registrationpage', views.Registrationpage, name='Registrationpage'),
    path("registration_api/", views.registration_api, name="registration_api"),
    
    path('Registrationpage1', views.Registrationpage1, name='Registrationpage1'),
    path("registration_api1/", views.registration_api1, name="registration_api1"),
    

    path('route_master/', views.route_master, name='route_master'),
    path('route_master_api/', views.route_master_api, name='route_master_api'),

    path('area_master/', views.area_master, name='area_master'),
    path('area_master_api/', views.area_master_api, name='area_master_api'),


    path('yatra_master/', views.yatra_master, name='yatra_master'),
    path('yatra_master_api/', views.yatra_master_api, name='yatra_master_api'),

    path("logout/", views.logout, name="logout"),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard_api/', views.dashboard_api, name='dashboard_api'),

    path('detailed_report_api/', views.detailed_report_api, name='detailed_report_api'),

    path('user_master/', views.user_master, name='user_master'),
    path('user_master_api/', views.user_master_api, name='user_master_api'),
    
    path('get_pilgrim_card_api/', views.get_pilgrim_card_api, name='get_pilgrim_card_api'),

    path('daily_report/', views.daily_report, name='daily_report'),
    path('daily_report_api/', views.daily_report_api, name='daily_report_api'),

    path('print_report/', views.print_report_page, name='print_report_page'),
    path('print_passenger_list/<int:route_id>/', views.print_passenger_list, name='print_passenger_list'),

        
]
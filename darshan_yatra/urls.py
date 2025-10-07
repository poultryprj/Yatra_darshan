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


    path('passenger_documents/', views.passenger_documents, name='passenger_documents'),
    path('passenger_documents_api/', views.passenger_documents_api, name='passenger_documents_api'),

    path('area_report/', views.area_report, name='area_report'),
    path('area_report_api/', views.area_report_api, name='area_report_api'),

    path('area_report_pdf/<int:route_id>/<str:area_name>/', views.area_report_pdf, name='area_report_pdf'),


    # path('bus_master/', views.bus_master, name='bus_master'),
    # path('bus_master_api/', views.bus_master_api, name='bus_master_api'),


    path('send_whatsapp_api/', views.send_whatsapp_api, name='send_whatsapp_api'),
    path('whatsapp_messaging/', views.whatsapp_messaging_page, name='whatsapp_messaging_page'),

    path('get_whatsapp_templates_api/', views.get_whatsapp_templates_api, name='get_whatsapp_templates_api'),

# #########  Diwali Yatra ##################

    path('home/', views.home, name='home'),
    path('diwali_yatra/', views.diwali_yatra_page, name='diwali_yatra_page'),

    path("diwali_registration/", views.diwali_registration, name="diwali_registration"),


    path("diwali_all_registrations/",views.diwali_all_registrations,name='diwali_all_registrations'),

    path('rationcardscan/' , views.rationcardscan , name='rationcardscan'),   
]
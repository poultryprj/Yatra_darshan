from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [

    # path('hello/', views.hello, name='hello'),

    path('', views.login, name='login'),

    # path('TicketBooking', views.TicketBooking, name='TicketBooking'),
    # path('TicketBookingApi', views.TicketBookingApi, name='TicketBookingApi'),
    
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


    path('yatra_bus_master/', views.yatra_bus_master, name='yatra_bus_master'),
    path('yatra_bus_master_api/', views.yatra_bus_master_api, name='yatra_bus_master_api'),


    path('send_whatsapp_api/', views.send_whatsapp_api, name='send_whatsapp_api'),
    path('whatsapp_messaging/', views.whatsapp_messaging_page, name='whatsapp_messaging_page'),

    path('get_whatsapp_templates_api/', views.get_whatsapp_templates_api, name='get_whatsapp_templates_api'),


    # #########  Diwali Yatra ##################

    path('home/', views.home, name='home'),
    
    path('diwali_yatra/', views.diwali_yatra_page, name='diwali_yatra_page'),

    path("diwali_registration/", views.diwali_registration, name="diwali_registration"),


    path("diwali_all_registrations/",views.diwali_all_registrations,name='diwali_all_registrations'),

    path('rationcardscan/' , views.rationcardscan , name='rationcardscan'),  


    path("change_diwali_token/", views.change_diwali_token, name="change_diwali_token"), 

    path('diwali_report/', views.diwali_report_page, name='diwali_report_page'),

    path("manage_family/<str:ration_card_no>/", views.manage_family_members, name='manage_family_members'),

    path("delete_diwali_member/<int:reg_id>/", views.delete_diwali_member, name='delete_diwali_member'),


    path('darshan_yatra/', views.darshan_yatra_management, name='darshan_yatra_management'),


    # Event Manag,emt ########


    path('events/', views.event_list_page, name='event_list_page'),
    path('events_add/', views.add_edit_event_page, name='add_event_page'),
    path('events_edit/<int:event_id>/', views.add_edit_event_page, name='edit_event_page'),
    path('events_delete/<int:event_id>/', views.delete_event_page, name='delete_event_page'),


    path('event/<int:event_id>/configure/', views.configure_event_fields_page, name='configure_event_fields_page'),

    path('event/<int:event_id>/registrations/', views.view_registrations_page, name='view_registrations_page'),

    path('register/<int:event_id>/', views.public_registration_page, name='public_registration_page'),
        
]
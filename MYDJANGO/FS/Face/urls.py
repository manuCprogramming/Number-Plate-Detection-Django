from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('validate_plate/', views.validate_plate, name='validate_plate'),
    path('open_webcam/', views.open_webcam, name='open_webcam'),
    path('add_plate_info/', views.add_plate_info, name='add_plate_info'),
    path('license_info/', views.LicenseInfoView.as_view(), name='license_info'),
    path('save_plate_info/', views.save_plate_info, name='save_plate_info'),
   


    path('time/plus/<int:offset>/', views.hours_ahead),  # Dynamic URL pattern


  
]

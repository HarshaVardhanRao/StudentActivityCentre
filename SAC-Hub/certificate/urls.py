from django.urls import path
from . import views

app_name = 'certificate'

urlpatterns = [
    path('', views.home, name='home'),
    path('generate/', views.generate_certificates, name='generate_certificates'),
    path('sample/', views.generate_certificate, name='generate_certificate'),
    path('download/<int:event_id>/', views.download_event_certificate, name='download_event_certificate'),
]

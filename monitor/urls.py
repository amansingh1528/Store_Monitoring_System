from django.urls import path
from .views import trigger_report, get_report

urlpatterns = [
    path('trigger_report', trigger_report),
    path('get_report', get_report),
]

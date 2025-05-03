from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify/', views.verify_otp, name='verify_otp'),
    path('resend/', views.resend_otp, name='resend_otp'),
]

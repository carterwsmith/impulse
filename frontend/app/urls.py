from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import base_view, logout_view, register, domain_onboarding

urlpatterns = [
    path('', login_required(base_view), name='example'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('onboard/', domain_onboarding, name='onboard')
]
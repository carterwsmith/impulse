from django.contrib.auth.decorators import login_required
from django.urls import path

from .views import base_view, logout_view, register, domain_onboarding, manage_promotions, delete_promotion, add_promotion, edit_promotion

urlpatterns = [
    path('', login_required(base_view), name='example'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('onboard/', domain_onboarding, name='onboard'),
    
    path('promotions/', manage_promotions, name='promotions'),
    path('promotions/add/', add_promotion, name='add_promotion'),
    path('promotions/edit/<int:promotion_id>/', edit_promotion, name='edit_promotion'),
    # this is definitely not secure and should be updated later
    path('delete_promotion/<int:promotion_id>/', delete_promotion, name='delete_promotion'),
]
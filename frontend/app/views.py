from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Promotions
from .forms import DomainOnboardingForm, PromotionForm
from .services import ImpulseUserService, PromotionsService

#
# DECORATORS
#
def redirect_if_not_logged_in(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def forbidden_if_not_logged_in(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# 
# VIEWS
#
def base_view(request):
    user = ImpulseUserService.impulse_user_from_request(request)
    if not ImpulseUserService.does_user_have_domain(user):
        return redirect('onboard')
    else:
        return render(request, 'example.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

@redirect_if_not_logged_in
def domain_onboarding(request):
    if request.method == 'POST':
        form = DomainOnboardingForm(request.POST)
        if form.is_valid():
            user = ImpulseUserService.impulse_user_from_request(request)
            ImpulseUserService.completed_valid_onboarding_form(user, form)
            return redirect('/')
    else:
        form = DomainOnboardingForm()
    return render(request, 'onboarding.html', {'form': form})

@redirect_if_not_logged_in
def add_promotion(request):
    if request.method == 'POST':
        form = PromotionForm(request.POST)
        if form.is_valid():
            promotion = form.save(commit=False)
            impulse_user = ImpulseUserService.impulse_user_from_request(request)
            promotion.django_user = impulse_user.user
            promotion.save()
            return redirect('promotions')  # Redirect to the manage promotion page to show the updated list
    else:
        form = PromotionForm()
    
    return render(request, 'add_promotion.html', {'form': form})


@redirect_if_not_logged_in
def edit_promotion(request, promotion_id):
    promotion = get_object_or_404(Promotions, pk=promotion_id)
    if not PromotionsService.is_promotion_owned_by_user(request.user.id, promotion_id):
        return HttpResponseForbidden("Forbidden")
    elif request.method == 'POST':
        form = PromotionForm(request.POST, instance=promotion)
        if form.is_valid():
            form.save()
            return redirect('promotions')  # Redirect to the manage promotion page to show the updated list
    else:
        form = PromotionForm(instance=promotion)
    
    return render(request, 'edit_promotion.html', {'form': form})

@redirect_if_not_logged_in
def manage_promotions(request):
    user = ImpulseUserService.impulse_user_from_request(request)
    promotions = PromotionsService.all_promotions_for_user(user)
    return render(request, 'promotions.html', {'promotions': promotions})

@forbidden_if_not_logged_in
@require_POST
def delete_promotion(request, promotion_id):
    if not PromotionsService.is_promotion_owned_by_user(request.user.id, promotion_id):
        return HttpResponseForbidden("Forbidden")
    else:
        PromotionsService.delete_promotion_from_id(promotion_id)
        return redirect('promotions')
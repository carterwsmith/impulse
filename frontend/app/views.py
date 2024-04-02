from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import DomainOnboardingForm, PromotionForm
from .services import ImpulseUserService, PromotionsService

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

def manage_promotions(request):
    if request.method == 'POST':
        form = PromotionForm(request.POST)
        if form.is_valid():
            promotion = form.save(commit=False)
            impulse_user = ImpulseUserService.impulse_user_from_request(request)
            promotion.django_user = impulse_user.user
            promotion.save()
            return redirect('promotions')  # Redirect to the same page to show the updated list and a clean form
    else:
        form = PromotionForm()
    
    user = ImpulseUserService.impulse_user_from_request(request)
    promotions = PromotionsService.all_promotions_for_user(user)
    return render(request, 'promotions.html', {'form': form, 'promotions': promotions})

@require_POST
def delete_promotion(request, promotion_id):
    PromotionsService.delete_promotion_from_id(promotion_id)
    return redirect('promotions')
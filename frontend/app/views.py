from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from .forms import DomainOnboardingForm
from .services import ImpulseUserService

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
from .models import ImpulseUser

class ImpulseUserService():
    def impulse_user_from_request(request):
        user_id = request.user.id
        impulse_user = ImpulseUser.objects.get(user_id=user_id)
        return impulse_user

    def does_user_have_domain(impulse_user):
        return impulse_user.root_domain

    def completed_valid_onboarding_form(impulse_user, form):
        impulse_user.root_domain = form.cleaned_data['root_domain']
        impulse_user.is_domain_configured = True
        impulse_user.save()
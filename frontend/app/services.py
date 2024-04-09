from .models import ImpulseUser, Promotions

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

class PromotionsService():
    def all_promotions_for_user(impulse_user):
        return Promotions.objects.filter(django_user_id=impulse_user.user_id)

    def get_promotion_from_id(promotion_id):
        return Promotions.objects.get(id=promotion_id)

    def delete_promotion_from_id(promotion_id):
        promotion = PromotionsService.get_promotion_from_id(promotion_id)
        promotion.delete()
        return True

    def is_promotion_owned_by_user(django_user_id, promotion_id):
        promotion = PromotionsService.get_promotion_from_id(promotion_id)
        return int(promotion.django_user.id) == int(django_user_id)
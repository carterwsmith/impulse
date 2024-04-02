from django import forms

from .models import ImpulseUser, Promotions

class DomainOnboardingForm(forms.ModelForm):
    class Meta:
        model = ImpulseUser  # Specify the model here
        fields = ['root_domain']  # Specify the fields you want to include in the form

    def clean(self):
        cleaned_data = super().clean()
        root_domain = cleaned_data.get('root_domain')

        # Add custom validation logic here (ping domain to see if js is added)
        #if not is_valid_domain(root_domain):
        #    raise forms.ValidationError('Invalid domain')

        return cleaned_data

class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotions
        fields = ['promotion_name', 'display_title', 'display_description', 'is_discount', 'discount_percent', 'discount_dollars']
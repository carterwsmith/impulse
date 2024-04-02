from django import forms

from .models import ImpulseUser

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
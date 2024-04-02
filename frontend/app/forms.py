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
        fields = ['is_ai_generated', 'promotion_name', 'display_title', 'display_description', 'discount_percent', 'discount_dollars',
                  'ai_description', 'ai_discount_percent_min', 'ai_discount_percent_max', 'ai_discount_dollars_min', 'ai_discount_dollars_max']
        widgets = {
            'is_ai_generated': forms.CheckboxInput(attrs={'id': 'is_ai_generated'}),
            'promotion_name': forms.TextInput(attrs={'id': 'promotion_name'}),
            'display_title': forms.TextInput(attrs={'id': 'display_title'}),
            'display_description': forms.Textarea(attrs={'id': 'display_description'}),
            'discount_percent': forms.NumberInput(attrs={'id': 'discount_percent'}),
            'discount_dollars': forms.NumberInput(attrs={'id': 'discount_dollars'}),
            
            'ai_description': forms.Textarea(attrs={'id': 'ai_description', 'display': 'none'}),
            'ai_discount_percent_min': forms.NumberInput(attrs={'id': 'ai_discount_percent_min', 'display': 'none'}),
            'ai_discount_percent_max': forms.NumberInput(attrs={'id': 'ai_discount_percent_max', 'display': 'none'}),
            'ai_discount_dollars_min': forms.NumberInput(attrs={'id': 'ai_discount_dollars_min', 'display': 'none'}),
            'ai_discount_dollars_max': forms.NumberInput(attrs={'id': 'ai_discount_dollars_max', 'display': 'none'}),
        }


from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError

class Sessions(models.Model):
    id = models.TextField(primary_key=True)
    django_user = models.ForeignKey(User, on_delete=models.CASCADE)

class PageVisits(models.Model):
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    pagevisit_token = models.TextField(unique=True, primary_key=True)
    page_path = models.TextField()
    start_time = models.TextField()
    end_time = models.TextField(null=True)

class MouseMovements(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    pagevisit_token = models.ForeignKey(PageVisits, to_field='pagevisit_token', on_delete=models.CASCADE)
    position_x = models.IntegerField()
    position_y = models.IntegerField()
    text_or_tag_hovered = models.TextField()
    recorded_at = models.TextField()

class LLMResponses(models.Model):
    id = models.AutoField(primary_key=True)
    session = models.ForeignKey(Sessions, on_delete=models.CASCADE)
    response = models.TextField()
    recorded_at = models.TextField()
    is_emitted = models.BooleanField(default=False)
    response_html = models.TextField(null=True)

class Promotions(models.Model):
    django_user = models.ForeignKey(User, on_delete=models.CASCADE)

    is_ai_generated = models.BooleanField(default=False)
    ai_description = models.TextField(null=True, blank=True)
    ai_discount_percent_min = models.FloatField(null=True, blank=True)
    ai_discount_percent_max = models.FloatField(null=True, blank=True)
    ai_discount_dollars_min = models.FloatField(null=True, blank=True)
    ai_discount_dollars_max = models.FloatField(null=True, blank=True)

    promotion_name = models.CharField(max_length=100)
    image_url = models.CharField(max_length=150, null=True, blank=True)

    display_title = models.CharField(max_length=100, null=True, blank=True)
    display_description = models.TextField(null=True, blank=True)
    discount_percent = models.FloatField(null=True, blank=True)
    discount_dollars = models.FloatField(null=True, blank=True)
    discount_code = models.CharField(max_length=50, null=True)

    def clean(self):
        ai_fields = [self.ai_description, self.ai_discount_percent_min, self.ai_discount_percent_max,
                         self.ai_discount_dollars_min, self.ai_discount_dollars_max]

        # Case 1: Promotion is NOT AI generated
        if not self.is_ai_generated:
            if any(field not in (None, '') for field in ai_fields):
                raise ValidationError("AI fields must be blank for non-AI generated promotions.")
            required_fields = [self.promotion_name, self.display_title, self.display_description]
            if any(field is None for field in required_fields):
                raise ValidationError("Promotion name and all non-AI fields must be filled out for non-AI generated promotions.")
            if (self.discount_percent is None and self.discount_dollars is None) or (self.discount_percent is not None and self.discount_dollars is not None):
                raise ValidationError("Only one of discount_percent or discount_dollars must be filled out for non-AI generated promotions.")

        # Case 2: Promotion IS AI generated
        else:
            pct_none_count = sum([self.ai_discount_percent_min is None, self.ai_discount_percent_max is None])
            dollars_none_count = sum([self.ai_discount_dollars_min is None, self.ai_discount_dollars_max is None])
            has_no_minmax = (pct_none_count == 2 and dollars_none_count == 2) or pct_none_count == 1 or dollars_none_count == 1 or (pct_none_count == 0 and dollars_none_count == 0)
            if any(field in (None, '') for field in [self.ai_description, self.promotion_name]) or has_no_minmax:
                raise ValidationError("Promotion name, AI fields, and only one discount type must be filled out for AI generated promotions.")
            non_ai_fields = [self.display_title, self.display_description, self.discount_percent, self.discount_dollars]
            if any(field not in (None, '') for field in non_ai_fields):
                raise ValidationError("Non-AI fields must be left blank for AI generated promotions (except for promotion_name).")

    def save(self, *args, **kwargs):
        self.clean()
        super(Promotions, self).save(*args, **kwargs)

class ImpulseUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    root_domain = models.CharField(max_length=255, null=True, blank=True)
    is_domain_configured = models.BooleanField(default=False)
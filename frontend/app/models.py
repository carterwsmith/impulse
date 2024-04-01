from django.db import models
from django.core.exceptions import ValidationError

class Sessions(models.Model):
    id = models.TextField(primary_key=True)

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

class Promotions(models.Model):
    promotion_name = models.CharField(max_length=100)
    display_title = models.CharField(max_length=100)
    display_description = models.TextField()

    is_discount = models.BooleanField(default=False)
    discount_percent = models.FloatField(null=True, blank=True)
    discount_dollars = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.is_discount and (self.discount_percent is None and self.discount_dollars is None):
            raise ValidationError("Either discount_percent or discount_dollars must be not null if is_discount is True")
        super(Promotions, self).save(*args, **kwargs)
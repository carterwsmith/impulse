# Generated by Django 5.0.3 on 2024-04-01 21:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_rename_impulse_user_promotions_django_user_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='promotions',
            old_name='django_user_id',
            new_name='django_user',
        ),
        migrations.RenameField(
            model_name='sessions',
            old_name='django_user_id',
            new_name='django_user',
        ),
    ]

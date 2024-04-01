# 4/1

import django.db.models.deletion
from django.db import migrations, models

def set_impulse_user_to_1(apps, schema_editor):
    Session = apps.get_model('app', 'Sessions')
    Promotion = apps.get_model('app', 'Promotions')

    Session.objects.update(impulse_user=1)
    Promotion.objects.update(impulse_user=1)

def reverse_set_impulse_user_to_1(apps, schema_editor):
    #  Not reversible
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_promotions'),
    ]

    operations = [
        # Create impulse_user fields as NULLABLE because they will be empty at first
        migrations.AddField(
            model_name='sessions',
            name='impulse_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.User', null=True),
        ),
        migrations.AddField(
            model_name='promotions',
            name='impulse_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.User', null=True),
        ),

        # Set all impulse_user fields to 1 (admin)
        migrations.RunPython(set_impulse_user_to_1, reverse_code=reverse_set_impulse_user_to_1),
        
        # Make all impulse_user fields NOT NULLABLE
        migrations.AlterField(
            model_name='sessions',
            name='impulse_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.User'),
        ),
        migrations.AlterField(
            model_name='promotions',
            name='impulse_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.User'),
        ),
    ]
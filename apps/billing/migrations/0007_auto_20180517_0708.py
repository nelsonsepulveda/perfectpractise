# Generated by Django 2.0 on 2018-05-17 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0006_billinginfo_subscription_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='billinginfo',
            old_name='subscription_date',
            new_name='created',
        ),
        migrations.AddField(
            model_name='billinginfo',
            name='current_period_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='billinginfo',
            name='current_period_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
# Generated by Django 2.0 on 2018-05-29 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20180528_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deltashotreport',
            name='club',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
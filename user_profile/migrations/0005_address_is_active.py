# Generated by Django 4.2.3 on 2023-08-21 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0004_rename_street_address_address_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]

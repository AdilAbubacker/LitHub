# Generated by Django 4.2.3 on 2023-08-21 06:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0005_address_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='country',
        ),
    ]

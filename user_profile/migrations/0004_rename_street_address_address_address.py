# Generated by Django 4.2.2 on 2023-07-25 07:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0003_rename_address_address_street_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='street_address',
            new_name='address',
        ),
    ]

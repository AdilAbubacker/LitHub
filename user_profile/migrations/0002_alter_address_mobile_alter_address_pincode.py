# Generated by Django 4.2.2 on 2023-07-25 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='mobile',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='address',
            name='pincode',
            field=models.CharField(max_length=10),
        ),
    ]

# Generated by Django 4.2.3 on 2023-08-03 13:48

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0002_alter_coupon_discount_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='activation_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

# Generated by Django 4.2.3 on 2023-08-27 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_bookvariant_offer_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookvariant',
            name='offer_percentage',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

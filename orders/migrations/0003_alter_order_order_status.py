# Generated by Django 4.2.3 on 2023-07-27 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(choices=[('CANCELLED', 'Cancelled'), ('DELIVERED', 'Delivered'), ('OUT FOR DELIVERY', 'Out for Delivery'), ('SHIPPED', 'Shipped'), ('RETURNED', 'Returned'), ('PROCESSING', 'Processing')], max_length=20),
        ),
    ]

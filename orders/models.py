from django.contrib.auth.models import User
from django.db import models
from store.models import BookVariant
from user_profile.models import Address


class Order(models.Model):
    PAYMENT_STATUS_CHOICE = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('REFUND', 'refund'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery')
    ]
    PAYMENT_METHOD_CHOICE = [
        ('PREPAID', 'Prepaid'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery')
    ]
    ORDERED_STATUS_CHOICE = [
        ('CANCELLED', 'Cancelled'),
        ('DELIVERED', 'Delivered'),
        ('OUT FOR DELIVERY', 'Out for Delivery'),
        ('SHIPPED', 'Shipped'),
        ('RETURNED', 'Returned'),
        ('PROCESSING', 'Processing')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICE, default='PENDING')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICE)
    order_status = models.CharField(max_length=20, choices=ORDERED_STATUS_CHOICE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    razor_pay_payment_id = models.CharField(max_length=100)
    razor_pay_payment_signature = models.CharField(max_length=200)
    razor_pay_order_id = models.CharField(max_length=100)

    def __str__(self):
        return f"Order #{self.pk} by {self.user.username}"

    def update_total_price(self):
        total_price = sum(item.price for item in self.orderitem_set.all())
        self.price = total_price
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    variant = models.ForeignKey(BookVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.variant} - Quantity: {self.quantity} - Price: {self.price}"

    def save(self, *args, **kwargs):
        self.price = self.variant.price * self.quantity
        super(OrderItem, self).save(*args, **kwargs)
        # After saving the OrderItem, update the total price of the associated Order
        self.order.update_total_price()

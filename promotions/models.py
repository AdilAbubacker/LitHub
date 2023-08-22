from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=10, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed')],
                                     default='percentage')
    discount_value = models.DecimalField(max_digits=5, decimal_places=0)
    min_or_max_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    activation_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField(default=timezone.now)
    is_onetime_usable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class UsedCoupon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    used_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'coupon')

    def __str__(self):
        return f"{self.user.username} used {self.coupon.code} on {self.used_date}"
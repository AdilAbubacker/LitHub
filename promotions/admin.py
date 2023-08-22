from django.contrib import admin
from promotions.models import Coupon, UsedCoupon

# Register your models here.
admin.site.register(Coupon)
admin.site.register(UsedCoupon)

